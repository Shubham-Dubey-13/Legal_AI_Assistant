"""
SUMMARIZATION AGENT — Legal document and response summarization

Responsibilities:
- Summarize uploaded legal PDFs (case facts, issues, holding)
- Compress retrieved chunks before sending to LLM
- Generate structured legal summaries with source mapping
"""

from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.core.config import settings


class SummarizationAgent:
    """
    Extracts and condenses legal information from documents and retrieved chunks.
    Uses extractive + abstractive summarization with source mapping.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.GEMINI_MODEL,
            temperature=0.1,
            max_output_tokens=512,
        )

    async def summarize_document(self, text: str, filename: str = "") -> Dict[str, Any]:
        """
        Generate a structured summary of a legal document.
        Returns: facts, issues, holding, parties, key_sections
        """
        prompt = f"""Analyze this Indian legal document and provide a structured summary.

Document: {filename}
Text (first 4000 chars):
{text[:4000]}

Provide a JSON-structured response with:
- case_type: (Criminal/Civil/Constitutional/Consumer/Family/General)
- facts: 2-3 sentence summary of key facts
- legal_issues: list of 2-3 main legal issues
- applicable_laws: list of IPC/BNS/Act sections mentioned
- parties: {{petitioner, respondent}}
- outcome: outcome if mentioned, else "Pending/Not mentioned"
- key_points: list of 3-5 important points

Respond ONLY with valid JSON."""

        try:
            resp = await self.llm.ainvoke([
                SystemMessage(content="You are a legal document analyst specializing in Indian law. Extract key information accurately."),
                HumanMessage(content=prompt),
            ])
            import json, re
            # Extract JSON from response
            content = resp.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            pass

        return {
            "case_type": "General",
            "facts": "Document processed. AI summary requires valid API key.",
            "legal_issues": [],
            "applicable_laws": [],
            "parties": {"petitioner": "Not identified", "respondent": "Not identified"},
            "outcome": "Not mentioned",
            "key_points": [],
        }

    async def summarize_chunks(self, chunks: List[Dict], query: str) -> str:
        """
        Compress retrieved chunks into a concise context string for the LLM.
        Removes redundant information and preserves most relevant passages.
        """
        if not chunks:
            return ""

        combined = "\n\n---\n\n".join([
            f"[Source: {c.get('metadata', {}).get('source', 'Legal DB')}]\n{c.get('text', '')[:500]}"
            for c in chunks[:5]
        ])

        if len(combined) < 1500:
            return combined  # Short enough — return as-is

        try:
            resp = await self.llm.ainvoke([
                SystemMessage(content="You are a legal research assistant. Compress the following retrieved legal passages into a focused summary relevant to the query. Preserve section numbers and case names."),
                HumanMessage(content=f"Query: {query}\n\nRetrieved Passages:\n{combined[:3000]}\n\nCompress to 300-400 words, preserving key legal facts and section numbers."),
            ])
            return resp.content
        except:
            return combined[:1500]

    async def extract_key_sections(self, text: str) -> Dict[str, List[str]]:
        """Extract IPC/BNS section numbers from document text."""
        import re
        ipc = list(set(re.findall(r'(?:IPC|Section)\s+(\d+[A-Z]?)', text, re.IGNORECASE)))
        bns = list(set(re.findall(r'BNS\s+(\d+[A-Z]?)', text, re.IGNORECASE)))
        bnss = list(set(re.findall(r'BNSS\s+(\d+[A-Z]?)', text, re.IGNORECASE)))
        articles = list(set(re.findall(r'Article\s+(\d+[A-Z]?)', text, re.IGNORECASE)))
        return {
            "ipc": [f"IPC {s}" for s in ipc[:10]],
            "bns": [f"BNS {s}" for s in bns[:10]],
            "bnss": [f"BNSS {s}" for s in bnss[:5]],
            "articles": [f"Article {a}" for a in articles[:10]],
        }
