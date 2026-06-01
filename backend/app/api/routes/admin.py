"""Admin routes: login, sessions, crisis alerts, stats, conversation logs."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import verify_admin
from app.config import ADMIN_KEY, ADMIN_USERNAME, ADMIN_PASSWORD
from app.services.db_service import get_all_sessions, get_crisis_alerts, get_chat_history, get_admin_stats

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminLoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def admin_login(req: AdminLoginRequest):
    """Admin login: username + password. Returns admin key for API calls."""
    if req.username == ADMIN_USERNAME and req.password == ADMIN_PASSWORD:
        return {"adminKey": ADMIN_KEY}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.get("/stats")
def admin_stats(_: None = Depends(verify_admin)):
    """Admin dashboard statistics."""
    return get_admin_stats()


@router.get("/sessions/{session_id}/logs")
def admin_session_logs(session_id: int, _: None = Depends(verify_admin)):
    """Get conversation logs for a session (admin only)."""
    rows = get_chat_history(session_id)
    return {
        "messages": [
            {
                "id": r.get("id"),
                "role": r.get("role"),
                "content": r.get("content"),
                "mhClassification": r.get("mhClassification"),
                "timestamp": str(r.get("timestamp", "")),
            }
            for r in rows
        ]
    }


@router.get("/sessions")
def list_sessions(_: None = Depends(verify_admin)):
    """List all sessions (admin)."""
    rows = get_all_sessions(100)
    return {
        "sessions": [
            {
                "id": r["id"],
                "userId": r["user_id"],
                "userName": r.get("user_name", ""),
                "sessionNo": r["session_no"],
                "status": r["status"],
                "createdAt": str(r.get("created_at", "")),
            }
            for r in rows
        ],
        "total": len(rows),
    }


@router.get("/crisis-alerts")
def crisis_alerts(_: None = Depends(verify_admin)):
    """Get high-risk crisis alerts."""
    alerts = get_crisis_alerts()
    return {"alerts": alerts}
