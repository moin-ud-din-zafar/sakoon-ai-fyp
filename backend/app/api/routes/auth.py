"""Auth routes: register, login, change password, forgot/reset password, JWT session."""

from datetime import datetime, timedelta, timezone
from typing import Literal
from urllib.parse import quote_plus
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.config import RESET_PASSWORD_BASE_URL, RESET_TOKEN_EXPIRE_MINUTES
from app.api.deps import get_current_user
from app.services.auth_service import (
    create_access_token,
    hash_password,
    user_to_public,
    verify_password,
)
from app.services.db_service import (
    create_user_account,
    create_password_reset_token,
    email_exists,
    get_valid_password_reset,
    get_or_create_session,
    get_user,
    get_user_by_email,
    mark_password_reset_used,
    update_user_password,
)
from app.services.email_service import send_password_reset_email

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


class ChangePasswordRequest(BaseModel):
    currentPassword: str = Field(..., min_length=1, max_length=128)
    newPassword: str = Field(..., min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=16, max_length=512)
    newPassword: str = Field(..., min_length=8, max_length=128)


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


@router.patch("/change-password")
def change_password(req: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    """Change account password for authenticated user."""
    user = get_user(current_user["id"])
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(req.currentPassword, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if req.currentPassword == req.newPassword:
        raise HTTPException(status_code=400, detail="New password must be different")
    update_user_password(current_user["id"], hash_password(req.newPassword))
    return {"ok": True, "message": "Password updated successfully"}


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    """
    Create password reset token and email a link.
    Always returns success message to avoid user enumeration.
    """
    user = get_user_by_email(str(req.email))
    if user:
        raw_token = secrets.token_urlsafe(48)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
        create_password_reset_token(user["id"], raw_token, expires_at)
        reset_link = f"{RESET_PASSWORD_BASE_URL}?token={quote_plus(raw_token)}"
        send_password_reset_email(str(req.email), reset_link)
    return {"ok": True, "message": "If this email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    """Reset password using one-time token from forgot-password flow."""
    row = get_valid_password_reset(req.token)
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user = get_user(row["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_user_password(user["id"], hash_password(req.newPassword))
    mark_password_reset_used(row["id"])
    return {"ok": True, "message": "Password has been reset successfully"}
