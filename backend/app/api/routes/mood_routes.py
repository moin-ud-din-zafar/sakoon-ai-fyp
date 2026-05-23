"""Mood & Behavior routes — Sakoon AI Phase 2.

Endpoints:
  POST /mood/log              — Add a manual mood entry (slider 1–5 + optional note)
  GET  /mood/history/{uid}    — Last 30 mood entries for a user
  POST /mood/behavior         — Log daily behavior (sleep, activity, social)
  GET  /mood/behavior/{uid}   — Last 30 behavior entries
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.db_service import (
    add_behavior_log,
    add_mood_log,
    get_behavior_history,
    get_mood_history,
    get_user,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mood", tags=["mood"])


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────

class MoodLogIn(BaseModel):
    user_id: int
    mood_score: int = Field(..., ge=1, le=5, description="1 = very low, 5 = very good")
    note: Optional[str] = Field(None, max_length=500)


class BehaviorLogIn(BaseModel):
    user_id: int
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    physical_activity: Optional[str] = Field(
        None,
        description="one of: none | light | moderate | intense",
    )
    social_interaction: Optional[str] = Field(
        None,
        description="one of: isolated | minimal | moderate | active",
    )
    notes: Optional[str] = Field(None, max_length=500)


# ─────────────────────────────────────────────────────────────────────────────
# Mood Log
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/log", summary="Add a manual mood log entry")
def log_mood(body: MoodLogIn) -> Dict[str, Any]:
    _assert_user_exists(body.user_id)
    entry_id = add_mood_log(body.user_id, body.mood_score, body.note)
    return {
        "ok": True,
        "id": entry_id,
        "message": "Mood logged successfully.",
    }


@router.get("/history/{user_id}", summary="Get mood history for a user")
def mood_history(user_id: int, limit: int = 30) -> Dict[str, Any]:
    _assert_user_exists(user_id)
    rows = get_mood_history(user_id, limit=min(limit, 90))
    return {
        "userId": user_id,
        "entries": [
            {
                "id": r["id"],
                "moodScore": r["mood_score"],
                "note": r.get("note"),
                "loggedAt": str(r.get("logged_at") or ""),
            }
            for r in rows
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Behavior Log
# ─────────────────────────────────────────────────────────────────────────────

_VALID_ACTIVITY = {"none", "light", "moderate", "intense"}
_VALID_SOCIAL = {"isolated", "minimal", "moderate", "active"}


@router.post("/behavior", summary="Log daily behavior data")
def log_behavior(body: BehaviorLogIn) -> Dict[str, Any]:
    _assert_user_exists(body.user_id)

    if body.physical_activity and body.physical_activity not in _VALID_ACTIVITY:
        raise HTTPException(
            status_code=422,
            detail=f"physical_activity must be one of {sorted(_VALID_ACTIVITY)}",
        )
    if body.social_interaction and body.social_interaction not in _VALID_SOCIAL:
        raise HTTPException(
            status_code=422,
            detail=f"social_interaction must be one of {sorted(_VALID_SOCIAL)}",
        )

    entry_id = add_behavior_log(
        body.user_id,
        {
            "sleep_hours": body.sleep_hours,
            "physical_activity": body.physical_activity,
            "social_interaction": body.social_interaction,
            "notes": body.notes,
        },
    )
    return {
        "ok": True,
        "id": entry_id,
        "message": "Behavior log saved.",
    }


@router.get("/behavior/{user_id}", summary="Get behavior history for a user")
def behavior_history(user_id: int, limit: int = 30) -> Dict[str, Any]:
    _assert_user_exists(user_id)
    rows = get_behavior_history(user_id, limit=min(limit, 90))
    return {
        "userId": user_id,
        "entries": [
            {
                "id": r["id"],
                "sleepHours": r.get("sleep_hours"),
                "physicalActivity": r.get("physical_activity"),
                "socialInteraction": r.get("social_interaction"),
                "notes": r.get("notes"),
                "loggedAt": str(r.get("logged_at") or ""),
            }
            for r in rows
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _assert_user_exists(user_id: int) -> None:
    if not get_user(user_id):
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
