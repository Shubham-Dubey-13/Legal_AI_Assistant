"""
Case Law Search, IPC/BNS Section Search Endpoints
"""

from fastapi import APIRouter, Depends, Query
from app.schemas.schemas import CaseLawSearchRequest, CaseLawSearchResponse, CaseLawResult
from app.core.security import get_current_user
import time, uuid

router = APIRouter()


@router.post("/caselaw", response_model=CaseLawSearchResponse)
async def search_case_law(
    payload: CaseLawSearchRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Hybrid semantic + BM25 search over Indian court judgments.
    
    Uses ChromaDB dense retrieval + BM25 sparse retrieval,
    then re-ranks with cross-encoder for maximum relevance.
    """
    start = time.time()
    from ai_services.rag.retriever import HybridRetriever
    retriever = HybridRetriever()
    results = await retriever.search_case_law(
        query=payload.query,
        court=payload.court,
        year_from=payload.year_from,
        year_to=payload.year_to,
        top_k=payload.top_k,
        search_type=payload.search_type,
    )
    elapsed = int((time.time() - start) * 1000)
    return CaseLawSearchResponse(
        query=payload.query,
        total_results=len(results),
        results=results,
        search_type=payload.search_type,
        processing_time_ms=elapsed,
    )


@router.get("/ipc-sections")
async def search_ipc_sections(
    query: str = Query(..., min_length=3),
    current_user: dict = Depends(get_current_user),
):
    """Search IPC sections by description or keyword"""
    from ai_services.nlp.section_identifier import IPCSectionIdentifier
    identifier = IPCSectionIdentifier()
    sections = identifier.identify_sections(query)
    return {"query": query, "ipc_sections": sections, "total": len(sections)}


@router.get("/bns-sections")
async def search_bns_sections(
    query: str = Query(..., min_length=3),
    current_user: dict = Depends(get_current_user),
):
    """Search BNS 2023 sections by description (replaces IPC)"""
    from ai_services.nlp.section_identifier import BNSSectionIdentifier
    identifier = BNSSectionIdentifier()
    sections = identifier.identify_sections(query)
    return {"query": query, "bns_sections": sections, "total": len(sections)}


@router.get("/similar-cases")
async def find_similar_cases(
    case_description: str = Query(..., min_length=20),
    top_k: int = Query(default=5, le=20),
    current_user: dict = Depends(get_current_user),
):
    """Find semantically similar cases using FAISS/ChromaDB"""
    from ai_services.rag.retriever import HybridRetriever
    retriever = HybridRetriever()
    cases = await retriever.find_similar(case_description, top_k=top_k)
    return {"similar_cases": cases, "total": len(cases)}


@router.get("/acts")
async def list_legal_acts(current_user: dict = Depends(get_current_user)):
    """List all available Indian legal acts in the knowledge base"""
    return {
        "acts": [
            {"name": "Indian Penal Code, 1860", "sections": 511, "status": "partially_replaced"},
            {"name": "Bharatiya Nyaya Sanhita (BNS), 2023", "sections": 358, "status": "active"},
            {"name": "Code of Civil Procedure, 1908", "sections": 158, "status": "active"},
            {"name": "Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023", "sections": 531, "status": "active"},
            {"name": "Indian Evidence Act, 1872", "sections": 167, "status": "partially_replaced"},
            {"name": "Bharatiya Sakshya Adhiniyam (BSA), 2023", "sections": 170, "status": "active"},
            {"name": "Constitution of India, 1950", "articles": 395, "status": "active"},
            {"name": "Consumer Protection Act, 2019", "sections": 107, "status": "active"},
            {"name": "Information Technology Act, 2000", "sections": 94, "status": "active"},
            {"name": "Protection of Children from Sexual Offences Act, 2012 (POCSO)", "sections": 46, "status": "active"},
            {"name": "Domestic Violence Act, 2005", "sections": 37, "status": "active"},
            {"name": "Right to Information Act, 2005", "sections": 31, "status": "active"},
            {"name": "Companies Act, 2013", "sections": 470, "status": "active"},
            {"name": "Income Tax Act, 1961", "sections": 298, "status": "active"},
            {"name": "Motor Vehicles Act, 1988", "sections": 217, "status": "active"},
        ]
    }
