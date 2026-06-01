"""Assessment routes — Sakoon AI Phase 2.

Endpoints:
  POST /assessment/profile           — Save patient intake profile
  GET  /assessment/profile/{user_id} — Get patient profile
  GET  /assessment/status/{user_id}  — Which sessions are done / next to start
  POST /assessment/start             — Start or resume a session (1, 2, or 3)
  GET  /assessment/next/{id}         — Get next question for an assessment
  POST /assessment/answer            — Submit an answer
  POST /assessment/scores/{user_id}  — Calculate + return final scores
  GET  /assessment/result/{user_id}  — Get previously stored result
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, require_assessment_access, require_user_id
from app.services.assessment_service import (
    calculate_scores,
    get_assessment_status,
    get_next_question,
    start_assessment,
    submit_answer,
)
from app.services.db_service import (
    get_assessment_result,
    get_patient_profile,
    upsert_patient_profile,
    get_user,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assessment", tags=["assessment"])


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────

class PatientProfileIn(BaseModel):
    user_id: int
    age: Optional[int] = Field(None, ge=5, le=120)
    gender: Optional[str] = None
    sleep_pattern: Optional[str] = None
    stress_triggers: Optional[str] = None
    past_therapy: Optional[bool] = False
    medications: Optional[str] = None


class StartAssessmentIn(BaseModel):
    user_id: int
    session_number: int = Field(..., ge=1, le=3)


class AnswerIn(BaseModel):
    assessment_id: int
    question_key: str
    answer_value: Optional[int] = None
    answer_text: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Patient Profile
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/profile", summary="Save patient intake profile")
def save_profile(
    body: PatientProfileIn,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    require_user_id(current_user, body.user_id)
    upsert_patient_profile(body.user_id, body.model_dump(exclude={"user_id"}))
    return {"ok": True, "message": "Profile saved."}


@router.get("/profile/{user_id}", summary="Get patient profile")
def get_profile(
    user_id: int,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    require_user_id(current_user, user_id)
    profile = get_patient_profile(user_id)
    return {"profile": profile}


# ─────────────────────────────────────────────────────────────────────────────
# Assessment Status
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/status/{user_id}", summary="Get assessment completion status")
def assessment_status(
    user_id: int,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    require_user_id(current_user, user_id)
    return get_assessment_status(user_id)


# ─────────────────────────────────────────────────────────────────────────────
# Session Flow
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/start", summary="Start or resume an assessment session")
def start(
    body: StartAssessmentIn,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    require_user_id(current_user, body.user_id)
    try:
        result = start_assessment(body.user_id, body.session_number)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result


@router.get("/next/{assessment_id}", summary="Get next question for an assessment")
def next_question(
    assessment_id: int,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    require_assessment_access(assessment_id, current_user["id"])
    try:
        return get_next_question(assessment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/answer", summary="Submit an answer")
def answer(
    body: AnswerIn,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    require_assessment_access(body.assessment_id, current_user["id"])
    if body.answer_value is None and not body.answer_text:
        raise HTTPException(
            status_code=422,
            detail="Provide at least answer_value or answer_text.",
        )
    try:
        return submit_answer(
            body.assessment_id,
            body.question_key,
            body.answer_value,
            body.answer_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Scores & Result
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/scores/{user_id}", summary="Calculate and store assessment scores")
def scores(
    user_id: int,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    require_user_id(current_user, user_id)
    status = get_assessment_status(user_id)
    if not status["allComplete"]:
        incomplete = [s for s in (1, 2, 3) if s not in status["completedSessions"]]
        raise HTTPException(
            status_code=400,
            detail=f"Sessions {incomplete} are not yet complete. Finish all 3 sessions first.",
        )
    try:
        return calculate_scores(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/result/{user_id}", summary="Get stored assessment result")
def result(
    user_id: int,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    require_user_id(current_user, user_id)
    row = get_assessment_result(user_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail="No result found. Complete all 3 assessment sessions first.",
        )
    return {
        "depressionScore": row.get("depression_score"),
        "anxietyScore": row.get("anxiety_score"),
        "riskLevel": row.get("risk_level"),
        "depressionSeverity": row.get("depression_severity"),
        "anxietySeverity": row.get("anxiety_severity"),
        "summary": row.get("summary"),
        "recommendations": row.get("recommendations"),
        "completedAt": str(row.get("completed_at") or ""),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _assert_user_exists(user_id: int) -> None:
    if not get_user(user_id):
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
