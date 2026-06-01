"""Session routes: chat history."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_session_access
from app.services.db_service import get_chat_history

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/{session_id}/history")
def get_history(
    session_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get chat history for session (JWT required)."""
    require_session_access(session_id, current_user["id"])
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
