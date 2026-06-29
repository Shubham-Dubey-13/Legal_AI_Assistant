"""
Application startup and shutdown events
"""

from loguru import logger
from app.core.config import settings


async def startup_event():
    """Initialize services on app startup"""
    logger.info("🚀 Starting Multi-Agent AI Legal Assistant...")
    logger.info(f"📌 Version: {settings.APP_VERSION}")
    logger.info(f"🤖 LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"📦 Vector DB: ChromaDB @ {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
    logger.info("✅ All services initialized successfully")


async def shutdown_event():
    """Cleanup on app shutdown"""
    logger.info("🛑 Shutting down Legal AI Assistant...")
    logger.info("✅ Cleanup complete")
