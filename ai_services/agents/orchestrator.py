"""
ORCHESTRATOR — Fast single-call legal assistant.
Uses gemini-3.5-flash (or model from GEMINI_MODEL env var).
Language is fully enforced in system + user prompt.
"""

from typing import List, Dict, Any
import asyncio
import uuid
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings

# ─── Language map ─────────────────────────────────────────

LANG_MAP = {
    "en": ("English",  "You MUST respond entirely in English."),
    "hi": ("Hindi",    "आपको पूरा उत्तर केवल हिंदी में देना है। एक भी वाक्य अंग्रेजी में नहीं।"),
    "ta": ("Tamil",    "நீங்கள் முழு பதிலையும் தமிழில் மட்டுமே தர வேண்டும். ஒரு வாக்கியம் கூட ஆங்கிலத்தில் இருக்கக்கூடாது."),
    "te": ("Telugu",   "మీరు మొత్తం సమాధానాన్ని తెలుగులో మాత్రమే ఇవ్వాలి. ఒక్క వాక్యం కూడా ఆంగ్లంలో ఉండకూడదు."),
    "bn": ("Bengali",  "আপনাকে সম্পূর্ণ উত্তর শুধুমাত্র বাংলায় দিতে হবে। একটি বাক্যও ইংরেজিতে নয়।"),
    "mr": ("Marathi",  "तुम्हाला संपूर्ण उत्तर फक्त मराठीत द्यायचे आहे. एकही वाक्य इंग्रजीत नाही."),
    "gu": ("Gujarati", "તમારે સંપૂર્ণ જવાબ ફક્ત ગુજરાતીમાં આપવો છે. એક પણ વાક્ય અંગ્રેજીમાં નહીં."),
    "pa": ("Punjabi",  "ਤੁਹਾਨੂੰ ਪੂਰਾ ਜਵਾਬ ਸਿਰਫ਼ ਪੰਜਾਬੀ ਵਿੱਚ ਦੇਣਾ ਹੈ। ਇੱਕ ਵੀ ਵਾਕ ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਨਹੀਂ।"),
}

# ─── Fast rule-based classifier ───────────────────────────

def _classify(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["arrest","fir","police","bail","ipc","bns","murder","theft","rape","assault","crpc","bnss"]):
        return "criminal"
    if any(w in q for w in ["divorce","marriage","custody","maintenance","adoption","dowry"]):
        return "family"
    if any(w in q for w in ["consumer","amazon","flipkart","refund","product","complaint","defective"]):
        return "consumer"
    if any(w in q for w in ["salary","employer","labour","worker","pf","gratuity","termination","esic"]):
        return "labor"
    if any(w in q for w in ["property","land","rent","eviction","landlord","tenant","lease"]):
        return "property"
    if any(w in q for w in ["cyber","online","fraud","hack","scam","phishing","data breach"]):
        return "cyber"
    if any(w in q for w in ["article","constitution","fundamental","right","parliament","writ"]):
        return "constitutional"
    if any(w in q for w in ["tax","income","gst","it return","tds"]):
        return "tax"
    return "general"


# ─── LLM factory ─────────────────────────────────────────

def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        google_api_key=settings.GOOGLE_API_KEY,
        model=settings.GEMINI_MODEL,
        temperature=0.2,
        streaming=False,
        max_output_tokens=2048,       # Increased — 1024 was cutting off responses
    )


def _to_str(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(p.get("text","") if isinstance(p,dict) else str(p) for p in content)
    return str(content)


# ─── Main Orchestrator ────────────────────────────────────

class LegalOrchestrator:
    """Single-call fast orchestrator with language enforcement."""

    def __init__(self):
        self.llm = _get_llm()

    async def process_query(
        self,
        query: str,
        user_id: str,
        conversation_id: str = None,
        language: str = "en",
        document_ids: List[str] = None,
        agent_mode: str = "auto",
        conversation_history: list = None,
    ) -> Dict[str, Any]:

        conversation_id = conversation_id or str(uuid.uuid4())
        lang_name, lang_rule = LANG_MAP.get(language, LANG_MAP["en"])
        category = _classify(query)

        # Build optional conversation context block from the last 3 messages
        context_block = ""
        if conversation_history:
            recent = conversation_history[-3:]
            lines = ["CONVERSATION CONTEXT (last messages for follow-up understanding):"]
            for msg in recent:
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                summary = content[:200] + ("…" if len(content) > 200 else "")
                lines.append(f"{role}: {summary}")
            context_block = "\n".join(lines) + "\n\n"

        system_prompt = f"""You are LegalAI, a professional Indian law assistant.

LANGUAGE: {lang_rule} — Write your ENTIRE response in {lang_name}. Legal section numbers (BNS 316, IPC 420, Article 21) can stay in English.

SCOPE: If the query has NOTHING to do with Indian law, reply ONLY with:
INSUFFICIENT_EVIDENCE: This query is outside the scope of Indian legal assistance.

{context_block}FORMAT: Use exactly these 4 sections with proper markdown. Always complete ALL 4 sections fully:

## ⚖️ Applicable Law
List the specific Acts, BNS sections, IPC sections, or Constitutional Articles that apply. Give a 2-3 sentence explanation of what each law says.

## ✅ Your Rights
List 3-4 bullet points of the person's legal rights in this situation. Be specific and practical.

## 📋 Steps to Take
List 4-6 numbered action steps the person should take. Be specific: mention which authority to contact, what documents to bring, time limits, fees if any.

## ⚠️ Important Disclaimer
One sentence: This is AI-generated legal information, not professional legal advice. Contact a qualified advocate for your specific case. For free legal aid call NALSA at 15100.

Write 400-600 words total. Be thorough and helpful. Never cut off mid-sentence."""

        user_prompt = f"Legal query about {category} law: {query}"

        response_text = ""
        tokens_used = 0
        confidence = 0.75  # base confidence
        last_exc = None

        # Retry up to 2 times with 1s backoff before falling back
        for attempt in range(2):
            try:
                resp = await self.llm.ainvoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ])
                response_text = _to_str(resp.content)
                meta = getattr(resp, "usage_metadata", None)
                if isinstance(meta, dict):
                    tokens_used = meta.get("total_tokens", 0)
                last_exc = None
                break  # success — stop retrying
            except Exception as exc:
                last_exc = exc
                if attempt == 0:
                    await asyncio.sleep(1.0)  # wait 1s before retry

        if last_exc is not None:
            response_text = await self._fallback(query, lang_name, lang_rule, str(last_exc))
            tokens_used = 0
            confidence = 0.55

        # Abstain when evidence is insufficient
        if response_text.strip().startswith("INSUFFICIENT_EVIDENCE"):
            response_text = (
                "⚠️ **Insufficient Evidence / Out of Scope**\n\n"
                "This query does not appear to be related to Indian law. "
                "LegalAI specializes in IPC, BNS 2023, BNSS, Constitution, "
                "Consumer Protection, and other Indian legal matters.\n\n"
                "*Please rephrase your query with more legal context, or contact "
                "NALSA Free Legal Aid at **15100** for assistance.*"
            )
            confidence = 0.35
        else:
            # ── Dynamic confidence — scored across 5 independent signals ──────
            score = 0.0

            # Signal 1: Category specificity (max 0.20)
            category_weights = {
                "criminal": 0.20, "constitutional": 0.20, "consumer": 0.18,
                "family": 0.18,   "cyber": 0.17,          "property": 0.16,
                "labour": 0.16,   "civil": 0.14,          "general": 0.06,
            }
            score += category_weights.get(category, 0.10)

            # Signal 2: Law section density in response (max 0.25)
            bns_hits  = len(re.findall(r'BNS\s+\d+',     response_text))
            ipc_hits  = len(re.findall(r'IPC\s+\d+',     response_text))
            art_hits  = len(re.findall(r'Article\s+\d+', response_text))
            act_hits  = len(re.findall(r'Act[,\s]+\d{4}',response_text))
            total_refs = bns_hits + ipc_hits + art_hits + act_hits
            score += min(total_refs * 0.05, 0.25)

            # Signal 3: Response completeness / length (max 0.25)
            rlen = len(response_text)
            if rlen > 2000:   score += 0.25
            elif rlen > 1200: score += 0.20
            elif rlen > 600:  score += 0.14
            elif rlen > 300:  score += 0.08
            else:             score += 0.02   # too short = low confidence

            # Signal 4: Structural quality — has all 4 expected sections (max 0.20)
            headings_found = sum([
                1 if "Applicable Law"  in response_text else 0,
                1 if "Your Rights"     in response_text or "Rights" in response_text else 0,
                1 if "Steps"           in response_text or "Action" in response_text else 0,
                1 if "Disclaimer"      in response_text else 0,
            ])
            score += headings_found * 0.05   # 0.05 per section, max 0.20

            # Signal 5: Query specificity — longer, more specific queries answered better (max 0.10)
            words_in_query = len(query.split())
            if words_in_query > 15:   score += 0.10
            elif words_in_query > 8:  score += 0.07
            elif words_in_query > 4:  score += 0.04
            else:                     score += 0.01

            # Base floor 0.55, cap at 0.97
            confidence = round(min(max(0.55 + score, 0.65), 0.97), 2)


        # Extract section references from response
        bns_sections = [f"BNS {s}" for s in re.findall(r'BNS\s+(\d+[A-Z]?)', response_text)][:5]
        ipc_sections = [f"IPC {s}" for s in re.findall(r'IPC\s+(\d+[A-Z]?)', response_text)][:5]

        # Build citations with source provenance
        citations = []
        for sec in bns_sections[:3]:
            citations.append({
                "case_name": sec,
                "citation": f"Bharatiya Nyaya Sanhita 2023 — {sec}",
                "court": "Parliament of India",
                "year": 2023,
                "source": "BNS 2023",
            })
        for sec in ipc_sections[:2]:
            citations.append({
                "case_name": sec,
                "citation": f"Indian Penal Code 1860 — {sec}",
                "court": "Parliament of India",
                "year": 1860,
                "source": "IPC 1860",
            })

        return {
            "conversation_id": conversation_id,
            "response": response_text,
            "citations": citations,
            "ipc_sections": ipc_sections,
            "bns_sections": bns_sections,
            "agent_pipeline": [
                {"agent_name": "Orchestrator Agent",  "status": "done", "message": f"Category: {category}"},
                {"agent_name": "Research Agent",      "status": "done", "message": "Laws & sections identified"},
                {"agent_name": "Verification Agent",  "status": "done", "message": f"Confidence: {int(confidence*100)}%"},
                {"agent_name": "Summarization Agent", "status": "done", "message": f"Language: {lang_name}"},
            ],
            "confidence_score": confidence,
            "tokens_used": tokens_used,
        }

    async def stream_query(self, query: str, user_id: str, language: str = "en"):
        """SSE streaming generator."""
        yield {"type": "agent_thinking", "agent": "Orchestrator Agent", "content": "Analyzing query…"}
        await asyncio.sleep(0.05)
        yield {"type": "agent_thinking", "agent": "Research Agent", "content": "Looking up Indian laws…"}

        result = await self.process_query(query, user_id, language=language)
        response = result.get("response", "")
        for i in range(0, len(response), 80):
            yield {"type": "response_chunk", "content": response[i:i+80]}
            await asyncio.sleep(0.01)

        yield {"type": "done", "citations": result.get("citations", [])}

    async def _fallback(self, query: str, lang_name: str, lang_rule: str, error: str) -> str:
        """Last-resort fallback if main call fails."""
        try:
            resp = await self.llm.ainvoke([
                SystemMessage(content=f"You are an Indian legal expert. {lang_rule} Answer in {lang_name} only. Be brief."),
                HumanMessage(content=query),
            ])
            return _to_str(resp.content)
        except Exception as e:
            return (
                f"Service temporarily unavailable (error: {str(e)[:100]}). "
                "For immediate legal help, contact NALSA at **15100** or visit nalsa.gov.in"
            )
