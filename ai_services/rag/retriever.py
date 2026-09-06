"""
HYBRID RETRIEVER — Unified retrieval interface used by search endpoints.
Wraps RetrievalAgent to provide a clean interface for search.py and chat.py.
"""

from typing import List, Dict, Optional
from ai_services.agents.retrieval_agent import RetrievalAgent


class HybridRetriever:
    """Dense + BM25 hybrid retriever used by all search endpoints."""

    def __init__(self):
        self._agent = RetrievalAgent()

    async def retrieve(
        self,
        query: str,
        document_ids: List[str] = None,
        category: str = "general",
        top_k: int = 5,
    ) -> List[Dict]:
        return await self._agent.retrieve(query=query, document_ids=document_ids,
                                          category=category, top_k=top_k)

    async def search_case_law(
        self,
        query: str,
        court: str = None,
        year_from: int = None,
        year_to: int = None,
        top_k: int = 10,
        search_type: str = "hybrid",
    ) -> List[Dict]:
        results = await self._agent.search_case_law(
            query=query, court=court, year_from=year_from,
            year_to=year_to, top_k=top_k, search_type=search_type,
        )
        if court:
            filtered = [r for r in results if court.lower() in r.get("court", "").lower()]
            results = filtered or results
        if year_from:
            filtered = [r for r in results if int(r.get("year", 0)) >= year_from]
            results = filtered or results
        if year_to:
            filtered = [r for r in results if int(r.get("year", 9999)) <= year_to]
            results = filtered or results
        return results[:top_k]

    async def find_similar(self, case_description: str, top_k: int = 5) -> List[Dict]:
        return await self._agent.find_similar(case_description, top_k=top_k)
