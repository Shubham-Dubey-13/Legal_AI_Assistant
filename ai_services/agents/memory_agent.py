"""
MEMORY AGENT — Long-term conversation memory and user legal profile

Uses:
- ChromaDB for semantic memory retrieval
- PostgreSQL for structured conversation history
- User legal profile building over sessions
"""

from typing import Dict, List, Any, Optional
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.core.config import settings

# In-memory store for demo (replace with Redis/ChromaDB in production)
_memory_store: Dict[str, List[Dict]] = {}


class MemoryAgent:
    """
    Manages conversation context and user legal profile.
    Supports multi-turn legal consultations with full context.
    """

    def __init__(self):
        self.max_history = 10  # Max messages to include in context
        self.max_context_tokens = 2000

    async def get_context(
        self, user_id: str, conversation_id: str
    ) -> str:
        """Retrieve relevant conversation history as context string"""
        key = f"{user_id}:{conversation_id}"
        history = _memory_store.get(key, [])

        if not history:
            return ""

        # Build context string from recent messages
        context_parts = []
        for msg in history[-self.max_history:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")[:300]
            context_parts.append(f"{role.upper()}: {content}")

        return "\n".join(context_parts)

    async def save_message(
        self,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Dict = None,
    ):
        """Save a message to conversation memory"""
        key = f"{user_id}:{conversation_id}"
        if key not in _memory_store:
            _memory_store[key] = []

        _memory_store[key].append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
        })

        # Keep only last 50 messages per conversation
        if len(_memory_store[key]) > 50:
            _memory_store[key] = _memory_store[key][-50:]

    async def get_user_profile(self, user_id: str) -> Dict:
        """Build user's legal profile from history"""
        all_topics = []
        for key, messages in _memory_store.items():
            if key.startswith(f"{user_id}:"):
                for msg in messages:
                    if msg.get("role") == "user":
                        all_topics.append(msg.get("content", "")[:100])

        return {
            "user_id": user_id,
            "total_queries": len(all_topics),
            "recent_topics": all_topics[-5:] if all_topics else [],
            "profile_built": len(all_topics) > 0,
        }

    async def clear_conversation(self, user_id: str, conversation_id: str):
        """Clear conversation memory"""
        key = f"{user_id}:{conversation_id}"
        _memory_store.pop(key, None)

    async def semantic_memory_search(
        self, user_id: str, query: str, top_k: int = 3
    ) -> List[Dict]:
        """Search across all user's conversations for relevant context"""
        all_messages = []
        for key, messages in _memory_store.items():
            if key.startswith(f"{user_id}:"):
                all_messages.extend(messages)

        # Simple keyword matching (replace with ChromaDB semantic search in production)
        query_words = set(query.lower().split())
        scored = []
        for msg in all_messages:
            content_words = set(msg.get("content", "").lower().split())
            overlap = len(query_words & content_words) / max(len(query_words), 1)
            if overlap > 0.2:
                scored.append({"message": msg, "score": overlap})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return [s["message"] for s in scored[:top_k]]
