"""Auth routes: register, login (email + password), JWT, session."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.api.deps import get_current_user
from app.services.auth_service import (
    create_access_token,
    hash_password,
    user_to_public,
    verify_password,
)
from app.services.db_service import (
    create_user_account,
    email_exists,
    get_or_create_session,
    get_user,
    get_user_by_email,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    languagePreference: Literal["en", "ur", "hi", "ps", "sd", "sk"] = "en"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class AuthTokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: dict


def _session_payload(session, total: int, is_limit: bool) -> dict:
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


@router.post("/register", response_model=AuthTokenResponse)
def register(req: RegisterRequest):
    """Create account with email + password; returns JWT."""
    if email_exists(req.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    password_hash = hash_password(req.password)
    try:
        uid = create_user_account(
            req.name.strip(),
            str(req.email),
            password_hash,
            req.languagePreference,
        )
    except Exception as exc:
        if "unique" in str(exc).lower() or "duplicate" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Email already registered") from exc
        raise

    user = get_user(uid)
    if not user:
        raise HTTPException(status_code=500, detail="Registration failed")

    token = create_access_token(user_id=uid, email=str(req.email))
    return AuthTokenResponse(accessToken=token, user=user_to_public(user))


@router.post("/login", response_model=AuthTokenResponse)
def login(req: LoginRequest):
    """Login with email + password; returns JWT."""
    user = get_user_by_email(str(req.email))
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user_id=user["id"], email=str(req.email))
    return AuthTokenResponse(accessToken=token, user=user_to_public(user))


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    """Current user from JWT."""
    return {"user": current_user}


@router.get("/session")
def get_session(current_user: dict = Depends(get_current_user)):
    """Get or create active session for the authenticated user."""
    session, total, is_limit = get_or_create_session(current_user["id"])
    return _session_payload(session, total, is_limit)


@router.get("/session/{user_id}")
def get_session_by_id(user_id: int, current_user: dict = Depends(get_current_user)):
    """Legacy path — user_id must match JWT subject."""
    if int(current_user["id"]) != int(user_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    session, total, is_limit = get_or_create_session(user_id)
    return _session_payload(session, total, is_limit)
