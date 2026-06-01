"""Password hashing and JWT access tokens for Sakoon AI users."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import JWTError, jwt

from app.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET


def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(*, user_id: int, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email.lower().strip(),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def user_to_public(user: Dict[str, Any]) -> Dict[str, Any]:
    """Safe user dict for API responses (no password_hash)."""
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user.get("email") or "",
        "languagePreference": user.get("language_preference", "en"),
        "totalSessions": user.get("total_sessions", 0),
        "createdAt": str(user.get("created_at", "")),
    }
