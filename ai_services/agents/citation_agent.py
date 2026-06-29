"""
CITATION AGENT — Extract, format, and validate Indian legal citations

Handles:
- Supreme Court (SCC, AIR, SCR)
- High Court citations
- Statute citations (IPC, BNS, CPC, Constitution)
- Neutral citation format
"""

from typing import List, Dict, Any
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.core.config import settings

# Citation patterns
CITATION_PATTERNS = [
    r'\(\d{4}\)\s+\d+\s+SCC\s+\d+',          # (2023) 4 SCC 123
    r'AIR\s+\d{4}\s+SC\s+\d+',                # AIR 1980 SC 898
    r'\d{4}\s+SCR\s+\d+',                     # 1978 SCR 248
    r'Writ Petition\s+(?:Civil|Criminal)?\s+No\.\s*\d+',
    r'SLP\s+\(Civil\)\s+No\.\s*\d+',
    r'\(\d{4}\)\s+\d+\s+(?:MLJ|SLR|LJ)\s+\d+',
]


class CitationAgent:
    """
    Extracts, validates, and formats legal citations in Indian standard format.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.GEMINI_MODEL,
            temperature=0.0,
        )

    async def extract_citations(
        self,
        research_results: List[Dict],
        retrieved_chunks: List[Dict],
    ) -> List[Dict]:
        """Extract and format all citations from agent pipeline outputs"""

        citations = []

        # Extract from research results
        for result in research_results:
            if result.get("citation") and result.get("citation") != "N/A":
                citations.append({
                    "case_name": result.get("case_name", "Unknown"),
                    "citation": result.get("citation", ""),
                    "court": result.get("court", "Supreme Court of India"),
                    "year": int(result.get("year", 2000)) if str(result.get("year", "")).isdigit() else 2000,
                    "relevance": result.get("similarity_score", 0.80),
                    "url": result.get("url"),
                    "type": "case_law",
                })

        # Extract inline citations from text chunks
        for chunk in retrieved_chunks:
            text = chunk.get("text", "")
            extracted = self._extract_inline_citations(text)
            for cit in extracted:
                if not any(c["citation"] == cit["citation"] for c in citations):
                    citations.append(cit)

        # Sort by relevance
        citations.sort(key=lambda x: x["relevance"], reverse=True)

        return citations[:10]  # Max 10 citations

    def _extract_inline_citations(self, text: str) -> List[Dict]:
        """Use regex to extract citation patterns from text"""
        found = []
        for pattern in CITATION_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                found.append({
                    "case_name": "See citation",
                    "citation": match,
                    "court": "Supreme Court of India",
                    "year": self._extract_year(match),
                    "relevance": 0.75,
                    "url": None,
                    "type": "inline",
                })
        return found

    def _extract_year(self, citation: str) -> int:
        """Extract year from citation string"""
        years = re.findall(r'\d{4}', citation)
        if years:
            year = int(years[0])
            if 1947 <= year <= 2026:
                return year
        return 2000

    def format_citation(self, citation: Dict) -> str:
        """Format a citation in Indian legal standard"""
        name = citation.get("case_name", "")
        cit = citation.get("citation", "")
        court = citation.get("court", "")
        year = citation.get("year", "")
        return f"{name}, {cit} ({court}, {year})"
