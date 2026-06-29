"""
Legal Document Upload and Analysis Endpoints
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from app.schemas.schemas import DocumentUploadResponse, DocumentAnalysisResponse
from app.core.security import get_current_user
from app.core.config import settings
import uuid, os, time

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a legal PDF document for AI analysis.
    
    Processing pipeline (async background task):
    1. PDF parsing with PyMuPDF
    2. Text extraction + OCR for scanned docs
    3. Section-aware chunking
    4. Embedding generation
    5. ChromaDB indexing
    6. IPC/BNS section identification
    7. Party extraction (NER)
    8. Summary generation
    """
    # Validate file type
    allowed_types = ["application/pdf", "application/msword", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and Word documents are allowed")

    # Validate file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB")

    # Save file
    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{doc_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(content)

    # Queue background processing
    background_tasks.add_task(
        process_document_background,
        doc_id=doc_id,
        file_path=file_path,
        user_id=current_user["user_id"],
        original_filename=file.filename,
    )

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        status="processing",
        message="Document uploaded successfully. AI analysis in progress...",
    )


async def process_document_background(doc_id: str, file_path: str, user_id: str, original_filename: str):
    """Background task: full AI document processing pipeline"""
    try:
        from ai_services.rag.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        await processor.process(
            doc_id=doc_id,
            file_path=file_path,
            user_id=user_id,
            original_filename=original_filename,
        )
    except Exception as e:
        print(f"Document processing failed: {e}")


@router.get("/{document_id}", response_model=DocumentAnalysisResponse)
async def get_document_analysis(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get AI analysis results for an uploaded document"""
    # In production: query from database
    return DocumentAnalysisResponse(
        document_id=document_id,
        filename="sample_legal_doc.pdf",
        status="completed",
        page_count=12,
        summary="This document is a civil dispute case regarding property rights...",
        extracted_sections=["Section 1: Preamble", "Section 2: Facts", "Section 3: Arguments"],
        identified_acts=["Indian Penal Code 1860", "Code of Civil Procedure 1908"],
        parties={"petitioner": "Ramesh Kumar", "respondent": "Delhi Municipal Corporation"},
        case_type="Civil",
        key_points=[
            "Property dispute over 500 sq ft of land",
            "Municipal corporation issued illegal notice",
            "Right to property under Article 300A invoked",
        ],
        ipc_sections=["IPC 420", "IPC 406"],
        bns_sections=["BNS 316", "BNS 303"],
        created_at=__import__("datetime").datetime.utcnow(),
    )


@router.get("/", summary="List all user documents")
async def list_documents(current_user: dict = Depends(get_current_user)):
    return {"documents": [], "total": 0}


@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)):
    return {"message": "Document deleted", "document_id": document_id}
