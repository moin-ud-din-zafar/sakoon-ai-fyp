"""Session routes: chat history."""

from fastapi import APIRouter

from app.services.db_service import get_chat_history

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/{session_id}/history")
def get_history(session_id: int):
    """Get chat history for session."""
    rows = get_chat_history(session_id)
    return {
        "messages": [
            {
                "id": r["id"],
                "role": r["role"],
                "content": r["content"],
                "mhClassification": r.get("mhClassification"),
                "timestamp": str(r.get("timestamp", "")),
            }
            for r in rows
        ]
    }
