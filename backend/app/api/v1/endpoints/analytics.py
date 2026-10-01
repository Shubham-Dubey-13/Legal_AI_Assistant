"""
Analytics Dashboard Endpoints — Real DB queries
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.models import Message, LegalDocument, LegalDraft, Conversation

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")

    # ── total_queries: assistant messages for this user ──────────────────────
    q_queries = (
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.user_id == user_id,
            Message.role == "assistant",
        )
    )
    total_queries = (await db.execute(q_queries)).scalar_one() or 0

    # ── total_documents ───────────────────────────────────────────────────────
    q_docs = select(func.count(LegalDocument.id)).where(
        LegalDocument.user_id == user_id
    )
    total_documents = (await db.execute(q_docs)).scalar_one() or 0

    # ── total_drafts ──────────────────────────────────────────────────────────
    q_drafts = select(func.count(LegalDraft.id)).where(
        LegalDraft.user_id == user_id
    )
    total_drafts = (await db.execute(q_drafts)).scalar_one() or 0

    # ── query_trends: last 7 days — count of assistant messages per day ───────
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=6)

    q_trends = (
        select(
            func.date(Message.created_at).label("day"),
            func.count(Message.id).label("cnt"),
        )
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.user_id == user_id,
            Message.role == "assistant",
            func.date(Message.created_at) >= seven_days_ago,
        )
        .group_by(func.date(Message.created_at))
        .order_by(func.date(Message.created_at))
    )
    trends_rows = (await db.execute(q_trends)).all()
    trends_map = {str(row.day): row.cnt for row in trends_rows}

    query_trends = []
    for i in range(7):
        day = today - timedelta(days=6 - i)
        day_str = str(day)
        query_trends.append({"date": day_str, "count": trends_map.get(day_str, 0)})

    # ── static / telemetry-dependent data ────────────────────────────────────
    agent_performance = {
        "orchestrator":  {"avg_ms": 120,  "success_rate": 0.98},
        "retrieval":     {"avg_ms": 340,  "success_rate": 0.97},
        "research":      {"avg_ms": 890,  "success_rate": 0.95},
        "verification":  {"avg_ms": 210,  "success_rate": 0.99},
        "summarization": {"avg_ms": 560,  "success_rate": 0.96},
        "drafting":      {"avg_ms": 1200, "success_rate": 0.94},
        "citation":      {"avg_ms": 90,   "success_rate": 0.98},
        "memory":        {"avg_ms": 45,   "success_rate": 0.99},
    }

    top_case_types = [
        {"type": "Criminal",       "count": 423, "percentage": 33.9},
        {"type": "Civil",          "count": 312, "percentage": 25.0},
        {"type": "Consumer",       "count": 198, "percentage": 15.9},
        {"type": "Constitutional", "count": 156, "percentage": 12.5},
        {"type": "Family",         "count": 158, "percentage": 12.7},
    ]

    language_distribution = [
        {"language": "English", "count": 789, "percentage": 63.3},
        {"language": "Hindi",   "count": 287, "percentage": 23.0},
        {"language": "Bengali", "count": 89,  "percentage": 7.1},
        {"language": "Tamil",   "count": 56,  "percentage": 4.5},
        {"language": "Telugu",  "count": 26,  "percentage": 2.1},
    ]

    return {
        "total_queries": total_queries,
        "total_documents": total_documents,
        "total_drafts": total_drafts,
        "agent_performance": agent_performance,
        "top_case_types": top_case_types,
        "query_trends": query_trends,
        "language_distribution": language_distribution,
    }


@router.get("/agent-metrics")
async def get_agent_metrics(current_user: dict = Depends(get_current_user)):
    return {"metrics": "Agent performance metrics"}


@router.get("/usage-stats")
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    return {"stats": "Usage statistics"}
