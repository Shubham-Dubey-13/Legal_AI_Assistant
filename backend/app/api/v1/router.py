"""
API Router — aggregates all v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, chat, documents, search, drafts, agents, analytics, ws

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat & Q&A"])
api_router.include_router(documents.router, prefix="/documents", tags=["Legal Documents"])
api_router.include_router(search.router, prefix="/search", tags=["Case Law Search"])
api_router.include_router(drafts.router, prefix="/drafts", tags=["Legal Drafts"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agent Control"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ws.router, prefix="/ws", tags=["WebSocket"])
