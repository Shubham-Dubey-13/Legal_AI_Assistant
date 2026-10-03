"""
Legal Document Upload and Analysis Endpoints
All endpoints read/write from the real database.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query
from app.schemas.schemas import DocumentUploadResponse, DocumentAnalysisResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.models import LegalDocument, DocumentStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid, os, datetime

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a legal PDF document for AI analysis.
    Pipeline (background): PDF parse → OCR fallback → chunk → embed → ChromaDB index → NER → summary
    """
    allowed_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and Word documents are allowed")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB")

    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "doc.pdf")[1] or ".pdf"
    safe_filename = f"{doc_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(content)

    # Persist document record to DB
    doc = LegalDocument(
        id=doc_id,
        user_id=current_user["user_id"],
        filename=safe_filename,
        original_filename=file.filename or "document.pdf",
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        status=DocumentStatus.PROCESSING,
    )
    db.add(doc)
    await db.flush()

    background_tasks.add_task(
        process_document_background,
        doc_id=doc_id,
        file_path=file_path,
        user_id=current_user["user_id"],
        original_filename=file.filename or "document.pdf",
    )

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        status="processing",
        message="Document uploaded. AI analysis in progress...",
    )


async def process_document_background(
    doc_id: str, file_path: str, user_id: str, original_filename: str
):
    """Background: full AI pipeline, then update DB record."""
    from app.core.database import AsyncSessionLocal
    from ai_services.rag.document_processor import DocumentProcessor

    async with AsyncSessionLocal() as db:
        try:
            processor = DocumentProcessor()
            result = await processor.process(
                doc_id=doc_id,
                file_path=file_path,
                user_id=user_id,
                original_filename=original_filename,
            )
            # Update DB with results
            res = await db.execute(select(LegalDocument).where(LegalDocument.id == doc_id))
            doc = res.scalar_one_or_none()
            if doc:
                doc.status = DocumentStatus.COMPLETED
                doc.page_count = result.get("page_count", 0)
                doc.summary = result.get("summary", "")
                doc.extracted_sections = result.get("ipc_sections", []) + result.get("bns_sections", [])
                doc.parties = result.get("parties", {})
                doc.case_type = result.get("case_type", "General")
                doc.identified_acts = result.get("ipc_sections", []) + result.get("bns_sections", [])
                await db.flush()
        except Exception as e:
            print(f"Document processing failed for {doc_id}: {e}")
            res = await db.execute(select(LegalDocument).where(LegalDocument.id == doc_id))
            doc = res.scalar_one_or_none()
            if doc:
                doc.status = DocumentStatus.FAILED
                await db.flush()


@router.get("/", summary="List all user documents")
async def list_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all documents uploaded by the current user with pagination."""
    user_id = current_user.get("user_id") or current_user.get("id")
    # Count total
    count_q = await db.execute(
        select(func.count(LegalDocument.id)).where(LegalDocument.user_id == user_id)
    )
    total = count_q.scalar_one()
    # Fetch page
    result = await db.execute(
        select(LegalDocument)
        .where(LegalDocument.user_id == user_id)
        .order_by(LegalDocument.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    docs = result.scalars().all()
    return {
        "documents": [
            {
                "document_id": d.id,
                "filename": d.original_filename,
                "status": d.status.value,
                "page_count": d.page_count,
                "case_type": d.case_type,
                "file_size": d.file_size,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in docs
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
    }


@router.get("/{document_id}", response_model=DocumentAnalysisResponse)
async def get_document_analysis(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI analysis results for an uploaded document."""
    result = await db.execute(
        select(LegalDocument).where(
            LegalDocument.id == document_id,
            LegalDocument.user_id == current_user["user_id"],
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Parse IPC/BNS sections from extracted_sections
    sections = doc.extracted_sections or []
    ipc = [s for s in sections if "IPC" in str(s)]
    bns = [s for s in sections if "BNS" in str(s)]

    return DocumentAnalysisResponse(
        document_id=doc.id,
        filename=doc.original_filename,
        status=doc.status.value,
        page_count=doc.page_count or 0,
        summary=doc.summary or "Processing in progress...",
        extracted_sections=sections,
        identified_acts=doc.identified_acts or [],
        parties=doc.parties or {},
        case_type=doc.case_type or "General",
        key_points=[],
        ipc_sections=ipc,
        bns_sections=bns,
        created_at=doc.created_at or datetime.datetime.utcnow(),
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document and its file from storage."""
    result = await db.execute(
        select(LegalDocument).where(
            LegalDocument.id == document_id,
            LegalDocument.user_id == current_user["user_id"],
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from disk
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    await db.delete(doc)
    return {"message": "Document deleted", "document_id": document_id}
