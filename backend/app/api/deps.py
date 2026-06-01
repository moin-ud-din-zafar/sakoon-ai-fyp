"""FastAPI dependencies."""

from functools import lru_cache
from typing import Any, Dict, Optional

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import ADMIN_KEY
from app.services.auth_service import decode_access_token, user_to_public
from app.services.classifier_service import MentalHealthClassifier
from app.services.db_service import get_user

_bearer = HTTPBearer(auto_error=True)
_bearer_optional = HTTPBearer(auto_error=False)


@lru_cache()
def get_classifier() -> MentalHealthClassifier:
    """Singleton classifier instance (loaded once at startup)."""
    return MentalHealthClassifier()


def verify_admin(
    x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> None:
    """Verify admin API key (header X-Admin-Key)."""
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")


def _load_user_from_token(token: str) -> Dict[str, Any]:
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token subject")
    row = get_user(user_id)
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    if not row.get("password_hash"):
        raise HTTPException(
            status_code=401,
            detail="Account not configured for secure login. Please register again.",
        )
    return user_to_public(row)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Dict[str, Any]:
    """Require valid JWT Bearer token; return public user dict."""
    return _load_user_from_token(credentials.credentials)


def require_user_id(current_user: Dict[str, Any], user_id: int) -> None:
    """Ensure path/body user_id matches authenticated user."""
    if int(current_user["id"]) != int(user_id):
        raise HTTPException(status_code=403, detail="Forbidden: user id does not match token")


def require_session_access(session_id: int, user_id: int) -> None:
    from app.services.db_service import session_belongs_to_user

    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(status_code=403, detail="Forbidden: invalid session for this user")


def require_assessment_access(assessment_id: int, user_id: int) -> None:
    from app.services.db_service import assessment_belongs_to_user

    if not assessment_belongs_to_user(assessment_id, user_id):
        raise HTTPException(status_code=403, detail="Forbidden: invalid assessment for this user")
