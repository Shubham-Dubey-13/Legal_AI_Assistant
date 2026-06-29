"""
Analytics Dashboard Endpoints
"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "total_queries": 1247,
        "total_documents": 89,
        "total_drafts": 34,
        "total_predictions": 56,
        "avg_response_time_ms": 1420,
        "most_searched_sections": [
            {"section": "BNS 316 (Cheating)", "count": 142},
            {"section": "BNS 74 (Assault)", "count": 98},
            {"section": "Article 21 (Right to Life)", "count": 87},
            {"section": "Consumer Protection Act S.35", "count": 76},
            {"section": "IT Act S.66A", "count": 65},
        ],
        "query_trends": [
            {"date": "2026-05-12", "count": 89},
            {"date": "2026-05-13", "count": 102},
            {"date": "2026-05-14", "count": 134},
            {"date": "2026-05-15", "count": 178},
            {"date": "2026-05-16", "count": 156},
            {"date": "2026-05-17", "count": 201},
            {"date": "2026-05-18", "count": 187},
        ],
        "agent_performance": {
            "orchestrator": {"avg_ms": 120, "success_rate": 0.98},
            "retrieval": {"avg_ms": 340, "success_rate": 0.97},
            "research": {"avg_ms": 890, "success_rate": 0.95},
            "verification": {"avg_ms": 210, "success_rate": 0.99},
            "summarization": {"avg_ms": 560, "success_rate": 0.96},
            "drafting": {"avg_ms": 1200, "success_rate": 0.94},
            "citation": {"avg_ms": 90, "success_rate": 0.98},
            "memory": {"avg_ms": 45, "success_rate": 0.99},
        },
        "top_case_types": [
            {"type": "Criminal", "count": 423, "percentage": 33.9},
            {"type": "Civil", "count": 312, "percentage": 25.0},
            {"type": "Consumer", "count": 198, "percentage": 15.9},
            {"type": "Constitutional", "count": 156, "percentage": 12.5},
            {"type": "Family", "count": 158, "percentage": 12.7},
        ],
        "language_distribution": [
            {"language": "English", "count": 789, "percentage": 63.3},
            {"language": "Hindi", "count": 287, "percentage": 23.0},
            {"language": "Bengali", "count": 89, "percentage": 7.1},
            {"language": "Tamil", "count": 56, "percentage": 4.5},
            {"language": "Telugu", "count": 26, "percentage": 2.1},
        ],
    }


@router.get("/agent-metrics")
async def get_agent_metrics(current_user: dict = Depends(get_current_user)):
    return {"metrics": "Agent performance metrics"}


@router.get("/usage-stats")
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    return {"stats": "Usage statistics"}
