"""
Main FastAPI Application Entry Point
Multi-Agent AI Legal Assistant for Indian Law
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse as StarletteJSONResponse
from datetime import datetime
import asyncio
import os
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.core.events import startup_event, shutdown_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifecycle manager"""
    await startup_event()
    yield
    await shutdown_event()



class TimeoutMiddleware(BaseHTTPMiddleware):
    """Abort requests that exceed 120 seconds to avoid worker starvation."""

    async def dispatch(self, request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=120.0)
        except asyncio.TimeoutError:
            return StarletteJSONResponse(
                {"detail": "Request timed out. Please try again."},
                status_code=504,
            )


def create_application() -> FastAPI:
    """Application factory pattern"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="""
        ## ⚖️ Multi-Agent AI Legal Assistant for Indian Law
        
        A production-grade Multi-Agent system built with:
        - **Agentic AI**: LangGraph multi-agent orchestration
        - **RAG Pipeline**: ChromaDB vector database with hybrid search
        - **GenAI**: GPT-4o / Gemini Pro for legal reasoning
        - **Legal NLP**: IPC/BNS classification, NER, summarization
        - **ML Models**: Judgment prediction, case similarity
        
        ### Agents
        - 🔍 Research Agent
        - 📚 Retrieval Agent  
        - ✅ Verification Agent
        - 📝 Summarization Agent
        - ✍️ Drafting Agent
        - 📎 Citation Agent
        - 🧠 Memory Agent
        - 🎯 Orchestrator Agent
        """,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TimeoutMiddleware)

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    # Static files for uploads
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    return app


app = create_application()


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": "⚖️ Multi-Agent AI Legal Assistant for Indian Law - API Server",
        "version": settings.APP_VERSION,
        "agents": [
            "Orchestrator Agent",
            "Research Agent",
            "Retrieval Agent",
            "Verification Agent",
            "Summarization Agent",
            "Drafting Agent",
            "Citation Agent",
            "Memory Agent",
        ],
        "docs": "/api/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """System health check — no auth required."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "model": os.environ.get("GEMINI_MODEL", "gemini-3.5-flash"),
        "components": {
            "api": "online",
            "database": "online",
            "agents": "online",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    from loguru import logger
    logger.error(
        f"Unhandled error on {request.method} {request.url}: {exc}\n{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again.",
            "error_type": type(exc).__name__,
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
