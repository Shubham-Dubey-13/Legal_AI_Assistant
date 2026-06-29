"""
Pydantic Schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ─── Auth Schemas ────────────────────────────────────────

from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    preferred_language: str = "en"

    @validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 capital letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least 1 symbol")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    preferred_language: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Chat Schemas ─────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
    language: str = "en"
    include_citations: bool = True
    agent_mode: str = "auto"  # auto | research | retrieval | draft
    document_ids: Optional[List[str]] = []


class AgentStatus(BaseModel):
    agent_name: str
    status: str  # thinking | working | done
    message: Optional[str] = None


class CitationItem(BaseModel):
    case_name: str
    citation: str
    court: str
    year: int
    relevance: float
    url: Optional[str] = None


class ChatResponse(BaseModel):
    message_id: str
    conversation_id: str
    response: str
    agent_pipeline: List[AgentStatus]
    citations: List[CitationItem]
    ipc_sections: List[str]
    bns_sections: List[str]
    confidence_score: float
    processing_time_ms: int
    language: str
    tokens_used: int


# ─── Document Schemas ─────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


class DocumentAnalysisResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    page_count: int
    summary: Optional[str]
    extracted_sections: List[str]
    identified_acts: List[str]
    parties: Dict[str, Any]
    case_type: Optional[str]
    key_points: List[str]
    ipc_sections: List[str]
    bns_sections: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Draft Schemas ────────────────────────────────────────

class DraftType(str, Enum):
    FIR = "fir"
    LEGAL_NOTICE = "legal_notice"
    PETITION = "petition"
    AFFIDAVIT = "affidavit"
    BAIL_APPLICATION = "bail_application"
    COMPLAINT = "complaint"
    CONTRACT = "contract"
    WILL = "will"


class DraftRequest(BaseModel):
    draft_type: DraftType
    description: str = Field(..., min_length=20)
    parties: Dict[str, str] = {}
    facts: str = ""
    relief_sought: str = ""
    language: str = "en"
    jurisdiction: str = "India"


class DraftResponse(BaseModel):
    draft_id: str
    draft_type: str
    title: str
    content: str
    word_count: int
    sections_used: List[str]
    language: str
    created_at: datetime


# ─── Search Schemas ───────────────────────────────────────

class CaseLawSearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    court: Optional[str] = None  # supreme | high | district | all
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    top_k: int = Field(default=10, le=50)
    search_type: str = "hybrid"  # semantic | bm25 | hybrid


class CaseLawResult(BaseModel):
    case_name: str
    citation: str
    court: str
    year: int
    summary: str
    relevant_sections: List[str]
    similarity_score: float
    url: Optional[str] = None
    judge: Optional[str] = None


class CaseLawSearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[CaseLawResult]
    search_type: str
    processing_time_ms: int


# ─── Judgment Prediction Schemas ─────────────────────────

class JudgmentPredictionRequest(BaseModel):
    case_description: str = Field(..., min_length=50)
    case_type: str
    jurisdiction: str = "India"
    additional_context: Optional[str] = None


class JudgmentPredictionResponse(BaseModel):
    prediction_id: str
    predicted_outcome: str
    confidence_score: float
    outcome_probabilities: Dict[str, float]
    relevant_sections: List[str]
    similar_cases: List[CaseLawResult]
    reasoning: str
    disclaimer: str


# ─── Analytics Schemas ────────────────────────────────────

class AnalyticsDashboard(BaseModel):
    total_queries: int
    total_documents: int
    total_drafts: int
    total_predictions: int
    most_searched_sections: List[Dict[str, Any]]
    query_trends: List[Dict[str, Any]]
    agent_performance: Dict[str, Any]
    avg_response_time_ms: float
    top_case_types: List[Dict[str, Any]]
