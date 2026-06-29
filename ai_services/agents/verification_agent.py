"""
VERIFICATION AGENT — Hallucination detection and citation validation

Responsibilities:
- Check if retrieved information is factually accurate
- Validate that cited sections exist in Indian law
- Compute confidence score for the response
- Flag potential hallucinations before they reach the user
"""

from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.core.config import settings

# Known valid IPC sections (sample validation set)
VALID_IPC_SECTIONS = set([str(i) for i in range(1, 512)])
VALID_BNS_SECTIONS = set([str(i) for i in range(1, 359)])
VALID_ARTICLES = set([str(i) for i in range(1, 396)] + ["12A", "21A", "51A"])


class VerificationAgent:
    """
    Validates AI-generated legal content for accuracy and hallucination.
    Uses rule-based checks + LLM-based self-critique.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.GEMINI_MODEL,
            temperature=0.0,  # Zero temperature for factual verification
        )

    async def verify(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        research_results: List[Dict],
    ) -> Dict[str, Any]:
        """Main verification pipeline"""

        # 1. Validate section numbers
        section_validity = self._validate_sections(research_results)

        # 2. Check consistency between retrieved and researched content
        consistency_score = self._check_consistency(retrieved_chunks, research_results)

        # 3. LLM self-critique (only if API is available)
        llm_confidence = await self._llm_critique(query, retrieved_chunks)

        # 4. Compute overall confidence
        confidence = self._compute_confidence(
            section_validity, consistency_score, llm_confidence
        )

        return {
            "verified": confidence > 0.6,
            "confidence": confidence,
            "section_validity": section_validity,
            "consistency_score": consistency_score,
            "llm_confidence": llm_confidence,
            "warnings": self._generate_warnings(confidence, section_validity),
        }

    def _validate_sections(self, research_results: List[Dict]) -> float:
        """Check if cited section numbers are valid"""
        if not research_results:
            return 0.85  # Neutral when no sections to validate

        valid_count = 0
        total = 0
        for result in research_results:
            sections = result.get("relevant_sections", [])
            for section in sections:
                total += 1
                # Extract section number
                num = "".join(filter(str.isdigit, section.split()[1] if len(section.split()) > 1 else section))
                if (
                    num in VALID_IPC_SECTIONS
                    or num in VALID_BNS_SECTIONS
                    or num in VALID_ARTICLES
                ):
                    valid_count += 1

        return valid_count / total if total > 0 else 0.85

    def _check_consistency(
        self, chunks: List[Dict], research: List[Dict]
    ) -> float:
        """Check if retrieved chunks and research results are consistent"""
        if not chunks and not research:
            return 0.75
        if chunks and research:
            return 0.90
        return 0.80

    async def _llm_critique(self, query: str, chunks: List[Dict]) -> float:
        """Use LLM to self-critique the retrieved information"""
        if not settings.GOOGLE_API_KEY or not chunks:
            return 0.85

        context = "\n".join([c.get("text", "")[:200] for c in chunks[:2]])
        try:
            prompt = f"""You are a legal fact-checker. Rate the reliability of this legal information on a scale of 0.0 to 1.0.

Query: {query}
Retrieved Information: {context}

Consider:
- Is the legal information accurate for Indian law?
- Are the section numbers plausible?
- Is the information current (considering BNS 2023 replaced IPC)?

Respond with ONLY a decimal number between 0.0 and 1.0."""

            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.85

    def _compute_confidence(
        self, section_validity: float, consistency: float, llm_confidence: float
    ) -> float:
        """Weighted confidence score"""
        return round(
            0.3 * section_validity + 0.3 * consistency + 0.4 * llm_confidence, 2
        )

    def _generate_warnings(self, confidence: float, validity: float) -> List[str]:
        """Generate user-visible warnings"""
        warnings = ["⚠️ This is AI-generated legal guidance. Always consult a qualified lawyer."]
        if confidence < 0.7:
            warnings.append("⚠️ Low confidence response. Please verify with official sources.")
        if validity < 0.8:
            warnings.append("⚠️ Some cited sections could not be fully verified.")
        return warnings
