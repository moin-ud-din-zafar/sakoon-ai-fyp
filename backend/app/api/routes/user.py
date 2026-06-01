"""User routes: mood summary, recommendations."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user, require_user_id
from app.services.db_service import (
    get_mood_summary,
    get_assignments,
    record_exercise_feedback,
    verify_assignment_owner,
)
from app.services.personalization_service import compute_trend

router = APIRouter(prefix="/user", tags=["user"])


class ExerciseFeedbackBody(BaseModel):
    assignmentId: Optional[int] = None
    sessionId: Optional[int] = None
    helped: Optional[bool] = None


@router.get("/{user_id}/mood-summary")
def mood_summary(user_id: int, current_user: dict = Depends(get_current_user)):
    """Get mood summary per session for user."""
    require_user_id(current_user, user_id)
    summary = get_mood_summary(user_id)
    trend = compute_trend(summary)
    return {"summary": summary, "trend": trend}


@router.get("/{user_id}/recommendations")
def recommendations(user_id: int, current_user: dict = Depends(get_current_user)):
    """Get coping exercise recommendations for user."""
    require_user_id(current_user, user_id)
    recs = get_assignments(user_id)
    return {"recommendations": recs}


@router.post("/{user_id}/exercise-feedback")
def exercise_feedback(
    user_id: int,
    body: ExerciseFeedbackBody,
    current_user: dict = Depends(get_current_user),
):
    """Store whether a completed exercise felt helpful; soft session stress nudge."""
    require_user_id(current_user, user_id)
    if body.assignmentId is not None and not verify_assignment_owner(
        body.assignmentId, user_id
    ):
        raise HTTPException(status_code=404, detail="Assignment not found")
    record_exercise_feedback(
        user_id,
        body.assignmentId,
        body.sessionId,
        body.helped,
    )
    return {"ok": True}
