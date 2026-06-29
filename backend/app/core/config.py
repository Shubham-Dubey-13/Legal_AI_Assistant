"""
Application Configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Multi-Agent AI Legal Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/legal_ai_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Google Gemini
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "indian_legal_corpus"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Indian Kanoon API
    INDIAN_KANOON_API_KEY: str = ""
    INDIAN_KANOON_BASE_URL: str = "https://api.indiankanoon.org"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # LLM Provider: "openai" or "gemini"
    LLM_PROVIDER: str = "gemini"

    class Config:
        # Resolve the .env file relative to this config file so it works
        # regardless of where `uvicorn` is launched.
        from pathlib import Path
        env_file = Path(__file__).resolve().parents[2] / ".env"
        case_sensitive = True

    # Validate that required API keys are present based on provider
    @classmethod
    def validate_keys(cls, values):
        provider = values.get('LLM_PROVIDER', 'gemini')
        if provider == 'openai' and not values.get('OPENAI_API_KEY'):
            raise ValueError('OPENAI_API_KEY is required when LLM_PROVIDER is set to openai')
        if provider == 'gemini' and not values.get('GOOGLE_API_KEY'):
            raise ValueError('GOOGLE_API_KEY is required when LLM_PROVIDER is set to gemini')
        return values

    # Pydantic post-init validation hook
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_keys


settings = Settings()


# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
