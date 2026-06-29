"""
Legal Draft Generation Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import DraftRequest, DraftResponse
from app.core.security import get_current_user
import uuid, time
from datetime import datetime

router = APIRouter()


@router.post("/generate", response_model=DraftResponse, status_code=201)
async def generate_draft(
    payload: DraftRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    AI-powered legal document generation using the Drafting Agent.
    
    Supported draft types:
    - FIR (First Information Report)
    - Legal Notice
    - Petition (Civil / Criminal / Writ)
    - Affidavit
    - Bail Application
    - Complaint
    - Contract
    - Will/Testament
    """
    start = time.time()

    from ai_services.agents.drafting_agent import DraftingAgent
    agent = DraftingAgent()

    try:
        result = await agent.generate_draft(
            draft_type=payload.draft_type.value,
            description=payload.description,
            parties=payload.parties,
            facts=payload.facts,
            relief_sought=payload.relief_sought,
            language=payload.language,
            jurisdiction=payload.jurisdiction,
        )

        return DraftResponse(
            draft_id=str(uuid.uuid4()),
            draft_type=payload.draft_type.value,
            title=result.get("title", f"{payload.draft_type.value.upper()} Draft"),
            content=result.get("content", ""),
            word_count=len(result.get("content", "").split()),
            sections_used=result.get("sections_used", []),
            language=payload.language,
            created_at=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Draft generation failed: {str(e)}")


@router.get("/templates")
async def list_draft_templates(current_user: dict = Depends(get_current_user)):
    """List available legal document templates"""
    return {
        "templates": [
            {
                "type": "fir",
                "name": "FIR (First Information Report)",
                "description": "File a criminal complaint with police",
                "fields": ["complainant_name", "incident_date", "incident_place", "accused_details", "facts"],
                "applicable_sections": ["BNS 173", "BNSS 173"],
            },
            {
                "type": "legal_notice",
                "name": "Legal Notice",
                "description": "Send formal legal notice before filing case",
                "fields": ["sender", "recipient", "subject", "demand", "timeline"],
                "applicable_sections": ["CPC Order 21", "NI Act 138"],
            },
            {
                "type": "petition",
                "name": "Writ Petition",
                "description": "File petition in High Court / Supreme Court",
                "fields": ["petitioner", "respondent", "facts", "grounds", "relief_sought"],
                "applicable_sections": ["Article 226", "Article 32"],
            },
            {
                "type": "affidavit",
                "name": "Affidavit",
                "description": "Sworn statement for court proceedings",
                "fields": ["deponent_name", "statements", "place", "date"],
                "applicable_sections": ["Indian Evidence Act"],
            },
            {
                "type": "bail_application",
                "name": "Bail Application",
                "description": "Apply for bail in criminal case",
                "fields": ["accused_name", "fir_number", "charges", "grounds_for_bail"],
                "applicable_sections": ["BNSS 480", "BNSS 483"],
            },
            {
                "type": "consumer_complaint",
                "name": "Consumer Complaint",
                "description": "File complaint with Consumer Forum",
                "fields": ["complainant", "opposite_party", "product_service", "deficiency", "relief"],
                "applicable_sections": ["Consumer Protection Act 2019 - Section 35"],
            },
        ]
    }


@router.get("/{draft_id}")
async def get_draft(draft_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve a previously generated draft"""
    return {"draft_id": draft_id, "message": "Draft retrieval from DB"}


@router.get("/")
async def list_drafts(current_user: dict = Depends(get_current_user)):
    """List all drafts for the current user"""
    return {"drafts": [], "total": 0}
