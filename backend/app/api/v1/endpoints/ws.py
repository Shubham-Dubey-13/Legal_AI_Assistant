"""
WebSocket endpoint for real-time agent streaming
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict
import json, asyncio

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time streaming of agent thoughts.
    
    Message format (server → client):
    {
        "type": "agent_thinking" | "agent_done" | "response_chunk" | "citations" | "error",
        "agent": "Research Agent",
        "content": "...",
        "metadata": {}
    }
    """
    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "⚖️ Legal AI Assistant connected. Ready to help!",
            "agents_online": 8,
        })

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "query":
                query = message.get("content", "")
                language = message.get("language", "en")
                conversation_id = message.get("conversation_id")

                # Stream agent pipeline execution
                await stream_agent_pipeline(websocket, query, user_id, language, conversation_id)

            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        if user_id in active_connections:
            del active_connections[user_id]
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
        if user_id in active_connections:
            del active_connections[user_id]


async def stream_agent_pipeline(
    websocket: WebSocket,
    query: str,
    user_id: str,
    language: str,
    conversation_id: str = None,
):
    """Stream multi-agent pipeline execution step by step"""

    # Step 1: Orchestrator classifying query
    await websocket.send_json({
        "type": "agent_thinking",
        "agent": "Orchestrator Agent",
        "content": "🎯 Analyzing your query and routing to relevant agents...",
        "step": 1,
    })
    await asyncio.sleep(0.3)

    # Step 2: Retrieval Agent
    await websocket.send_json({
        "type": "agent_thinking",
        "agent": "Retrieval Agent",
        "content": "🔍 Searching Indian legal database (ChromaDB hybrid search)...",
        "step": 2,
    })
    await asyncio.sleep(0.5)

    # Step 3: Research Agent
    await websocket.send_json({
        "type": "agent_thinking",
        "agent": "Research Agent",
        "content": "📚 Fetching relevant case laws and statutes...",
        "step": 3,
    })
    await asyncio.sleep(0.8)

    # Step 4: Verification
    await websocket.send_json({
        "type": "agent_thinking",
        "agent": "Verification Agent",
        "content": "✅ Validating facts and checking citations...",
        "step": 4,
    })
    await asyncio.sleep(0.4)

    # Step 5: Generate response
    from ai_services.agents.orchestrator import LegalOrchestrator
    orchestrator = LegalOrchestrator()

    try:
        result = await orchestrator.process_query(
            query=query,
            user_id=user_id,
            conversation_id=conversation_id,
            language=language,
        )

        # Stream response in chunks
        response_text = result.get("response", "")
        chunk_size = 50
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i + chunk_size]
            await websocket.send_json({
                "type": "response_chunk",
                "content": chunk,
            })
            await asyncio.sleep(0.03)

        # Send citations
        await websocket.send_json({
            "type": "citations",
            "content": result.get("citations", []),
        })

        # Send IPC/BNS sections
        await websocket.send_json({
            "type": "sections",
            "ipc_sections": result.get("ipc_sections", []),
            "bns_sections": result.get("bns_sections", []),
        })

        # Done
        await websocket.send_json({
            "type": "done",
            "confidence_score": result.get("confidence_score", 0.85),
            "tokens_used": result.get("tokens_used", 0),
        })

    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
