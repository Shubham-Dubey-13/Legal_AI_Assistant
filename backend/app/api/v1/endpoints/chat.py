"""
Chat Endpoint — routes user queries through the multi-agent orchestrator.
All messages are persisted to the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.schemas import ChatRequest, ChatResponse
from app.core.security import get_current_user
from app.core.database import get_db
from app.models.models import Conversation, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio, json, time, uuid

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    payload: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Main chat endpoint — orchestrates all agents to answer legal queries.
    Persists conversation and messages to database.
    """
    start_time = time.time()

    from ai_services.agents.orchestrator import LegalOrchestrator
    orchestrator = LegalOrchestrator()

    # Resolve or create conversation
    conversation_id = payload.conversation_id
    if conversation_id:
        res = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user["user_id"],
            )
        )
        conv = res.scalar_one_or_none()
        if not conv:
            conversation_id = None  # Reset if not found / not owned

    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        conv = Conversation(
            id=conversation_id,
            user_id=current_user["user_id"],
            title=payload.message[:60] + ("..." if len(payload.message) > 60 else ""),
            language=payload.language or "en",
        )
        db.add(conv)
        await db.flush()

    # Save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="user",
        content=payload.message,
        tokens_used=0,
    )
    db.add(user_msg)

    try:
        result = await orchestrator.process_query(
            query=payload.message,
            user_id=current_user["user_id"],
            conversation_id=conversation_id,
            language=payload.language or "en",
            document_ids=payload.document_ids or [],
            agent_mode=payload.agent_mode or "auto",
        )

        processing_time = int((time.time() - start_time) * 1000)
        message_id = str(uuid.uuid4())

        # Save assistant message
        ai_msg = Message(
            id=message_id,
            conversation_id=conversation_id,
            role="assistant",
            content=result.get("response", ""),
            citations=result.get("citations", []),
            meta_data={
                "ipc_sections": result.get("ipc_sections", []),
                "bns_sections": result.get("bns_sections", []),
                "agent_pipeline": result.get("agent_pipeline", []),
                "confidence_score": result.get("confidence_score", 0.85),
            },
            tokens_used=result.get("tokens_used", 0),
            processing_time_ms=processing_time,
        )
        db.add(ai_msg)
        await db.flush()

        return ChatResponse(
            message_id=message_id,
            conversation_id=conversation_id,
            response=result.get("response", ""),
            agent_pipeline=result.get("agent_pipeline", []),
            citations=result.get("citations", []),
            ipc_sections=result.get("ipc_sections", []),
            bns_sections=result.get("bns_sections", []),
            confidence_score=result.get("confidence_score", 0.85),
            processing_time_ms=processing_time,
            language=payload.language or "en",
            tokens_used=result.get("tokens_used", 0),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Streaming chat endpoint — SSE stream of agent thoughts + final response."""
    async def event_generator():
        from ai_services.agents.orchestrator import LegalOrchestrator
        orchestrator = LegalOrchestrator()
        async for chunk in orchestrator.stream_query(
            query=payload.message,
            user_id=current_user["user_id"],
            language=payload.language or "en",
        ):
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.01)
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/conversations")
async def list_conversations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the current user."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user["user_id"], Conversation.is_active == True)
        .order_by(Conversation.updated_at.desc())
    )
    convs = result.scalars().all()
    return {
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "language": c.language,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in convs
        ],
        "total": len(convs),
    }


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full message history for a conversation."""
    # Verify ownership
    res = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user["user_id"],
        )
    )
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    msgs = result.scalars().all()

    return {
        "conversation_id": conversation_id,
        "title": conv.title,
        "language": conv.language,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "citations": m.citations or [],
                "ipc_sections": (m.meta_data or {}).get("ipc_sections", []),
                "bns_sections": (m.meta_data or {}).get("bns_sections", []),
                "agent_pipeline": (m.meta_data or {}).get("agent_pipeline", []),
                "confidence_score": (m.meta_data or {}).get("confidence_score", 0.85),
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in msgs
        ],
        "total": len(msgs),
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a conversation (sets is_active=False)."""
    res = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user["user_id"],
        )
    )
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.is_active = False
    return {"message": "Conversation deleted", "conversation_id": conversation_id}
