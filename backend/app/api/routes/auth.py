"""Auth routes: register, session."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from app.services.db_service import create_user, get_user, get_user_by_name, get_or_create_session

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    languagePreference: Literal["en", "ur", "hi", "ps", "sd", "sk"] = "en"


class RegisterResponse(BaseModel):
    user: dict


class LoginRequest(BaseModel):
    name: str


@router.post("/login", response_model=RegisterResponse)
def login(req: LoginRequest):
    """Login for returning users — find by name."""
    user = get_user_by_name(req.name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")
    return RegisterResponse(user={
        "id": user["id"],
        "name": user["name"],
        "languagePreference": user.get("language_preference", "en"),
        "totalSessions": user.get("total_sessions", 0),
        "createdAt": str(user.get("created_at", "")),
    })


@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest):
    """Create new user."""
    uid = create_user(req.name, req.languagePreference)
    user = get_user(uid)
    return RegisterResponse(user={
        "id": user["id"],
        "name": user["name"],
        "languagePreference": user["language_preference"],
        "totalSessions": user.get("total_sessions", 0),
        "createdAt": str(user.get("created_at", "")),
    })


@router.get("/session/{user_id}")
def get_session(user_id: int):
    """Get or create current session for user."""
    session, total, is_limit = get_or_create_session(user_id)
    if not session and is_limit:
        return {
            "session": None,
            "totalSessions": total,
            "isLimitReached": True,
        }
    if not session:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "session": {
            "id": session["id"],
            "userId": session["user_id"],
            "sessionNo": session["session_no"],
            "status": session["status"],
            "stressLevel": session.get("stress_level", 0),
            "createdAt": str(session.get("created_at", "")),
        },
        "totalSessions": total,
        "isLimitReached": is_limit,
    }
