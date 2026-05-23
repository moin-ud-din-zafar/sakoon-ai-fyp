"""FastAPI dependencies."""

from functools import lru_cache
from typing import Optional

from fastapi import Header, HTTPException

from app.config import ADMIN_KEY
from app.services.classifier_service import MentalHealthClassifier


@lru_cache()
def get_classifier() -> MentalHealthClassifier:
    """Singleton classifier instance (loaded once at startup)."""
    return MentalHealthClassifier()


def verify_admin(x_admin_key: Optional[str] = Header(None)) -> None:
    """Verify admin API key."""
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")
