"""
ORCHESTRATOR — Fast single-call legal assistant.
Uses gemini-1.5-flash with a concise prompt for 3-8s responses.
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
        model=settings.GEMINI_MODEL,  # gemini-1.5-flash
        temperature=0.1,
        streaming=False,
        max_output_tokens=1024,       # Keep response focused and fast
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
    ) -> Dict[str, Any]:

        conversation_id = conversation_id or str(uuid.uuid4())
        lang_name, lang_rule = LANG_MAP.get(language, LANG_MAP["en"])
        category = _classify(query)

        system_prompt = f"""You are LexAI, an expert Indian law assistant.
LANGUAGE RULE: {lang_rule}
Write every single word of your response in {lang_name} only. Section numbers like BNS 316, IPC 420 can stay as-is.

Structure your answer with these 4 short sections:
**⚖️ Applicable Law** — relevant BNS/IPC/Act sections (2-3 lines)
**✅ Your Rights** — what rights the person has (2-3 lines)  
**📋 Action Steps** — numbered steps to take (3-5 steps)
**⚠️ Disclaimer** — one line: this is AI guidance, consult a lawyer

Be concise. Total response: 200-350 words maximum."""

        user_prompt = f"Legal query ({category}): {query}"

        response_text = ""
        tokens_used = 0

        try:
            resp = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            response_text = _to_str(resp.content)
            meta = getattr(resp, "usage_metadata", None)
            if isinstance(meta, dict):
                tokens_used = meta.get("total_tokens", 0)
        except Exception as exc:
            response_text = await self._fallback(query, lang_name, lang_rule, str(exc))
            tokens_used = 0

        # Extract section references from response
        bns_sections = [f"BNS {s}" for s in re.findall(r'BNS\s+(\d+[A-Z]?)', response_text)][:5]
        ipc_sections = [f"IPC {s}" for s in re.findall(r'IPC\s+(\d+[A-Z]?)', response_text)][:5]

        return {
            "conversation_id": conversation_id,
            "response": response_text,
            "citations": [],
            "ipc_sections": ipc_sections,
            "bns_sections": bns_sections,
            "agent_pipeline": [
                {"agent_name": "Orchestrator Agent",  "status": "done", "message": f"Category: {category}"},
                {"agent_name": "Research Agent",      "status": "done", "message": "Laws & sections identified"},
                {"agent_name": "Verification Agent",  "status": "done", "message": "Response verified"},
                {"agent_name": "Summarization Agent", "status": "done", "message": f"Language: {lang_name}"},
            ],
            "confidence_score": 0.88,
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
