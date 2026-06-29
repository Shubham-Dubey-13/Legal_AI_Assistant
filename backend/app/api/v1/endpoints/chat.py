"""
Chat Endpoint — routes user queries through the multi-agent orchestrator
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.schemas import ChatRequest, ChatResponse
from app.core.security import get_current_user
import asyncio
import json
import time
import uuid

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    payload: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Main chat endpoint — orchestrates all agents to answer legal queries.
    
    Flow:
    1. Orchestrator receives query
    2. Routes to Research + Retrieval agents (parallel)
    3. Verification agent checks facts
    4. Memory agent adds context
    5. Response synthesized with citations
    """
    start_time = time.time()

    # Import here to avoid circular imports
    from ai_services.agents.orchestrator import LegalOrchestrator

    orchestrator = LegalOrchestrator()

    try:
        result = await orchestrator.process_query(
            query=payload.message,
            user_id=current_user["user_id"],
            conversation_id=payload.conversation_id,
            language=payload.language,
            document_ids=payload.document_ids or [],
            agent_mode=payload.agent_mode,
        )

        processing_time = int((time.time() - start_time) * 1000)

        return ChatResponse(
            message_id=str(uuid.uuid4()),
            conversation_id=result.get("conversation_id", str(uuid.uuid4())),
            response=result.get("response", ""),
            agent_pipeline=result.get("agent_pipeline", []),
            citations=result.get("citations", []),
            ipc_sections=result.get("ipc_sections", []),
            bns_sections=result.get("bns_sections", []),
            confidence_score=result.get("confidence_score", 0.85),
            processing_time_ms=processing_time,
            language=payload.language,
            tokens_used=result.get("tokens_used", 0),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Streaming chat endpoint — returns SSE stream of agent thoughts + final response
    """
    async def event_generator():
        # Import orchestrator
        from ai_services.agents.orchestrator import LegalOrchestrator
        orchestrator = LegalOrchestrator()

        async for chunk in orchestrator.stream_query(
            query=payload.message,
            user_id=current_user["user_id"],
            language=payload.language,
        ):
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.01)

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get full message history for a conversation"""
    # Return mock data for demonstration
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "total": 0,
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    return {"message": "Conversation deleted", "conversation_id": conversation_id}
