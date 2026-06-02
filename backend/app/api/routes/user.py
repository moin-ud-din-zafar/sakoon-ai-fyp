"""User routes: mood summary, recommendations, and settings helpers."""

from pathlib import Path
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import MAX_PROFILE_IMAGE_MB, UPLOAD_DIR
from app.api.deps import get_current_user, require_user_id
from app.services.db_service import (
    get_mood_summary,
    get_assignments,
    get_user,
    record_exercise_feedback,
    update_user_profile_image,
    verify_assignment_owner,
)
from app.services.auth_service import user_to_public
from app.services.cloudinary_service import upload_profile_image_bytes
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


@router.post("/{user_id}/profile-image")
async def upload_profile_image(
    user_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload or replace user profile image.
    Supports JPG/PNG/WEBP up to configured size limit.
    """
    require_user_id(current_user, user_id)
    content_type = (file.content_type or "").lower()
    allowed = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    if content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, or WEBP files are allowed")
    data = await file.read()
    max_bytes = MAX_PROFILE_IMAGE_MB * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=400, detail=f"Image must be <= {MAX_PROFILE_IMAGE_MB}MB")

    cloudinary_url = upload_profile_image_bytes(data, user_id=user_id)
    if cloudinary_url:
        image_url = cloudinary_url
    else:
        target_dir = Path(UPLOAD_DIR) / "profile-images"
        target_dir.mkdir(parents=True, exist_ok=True)
        fname = f"user-{user_id}-{uuid.uuid4().hex[:12]}{allowed[content_type]}"
        out_path = target_dir / fname
        out_path.write_bytes(data)
        image_url = f"/uploads/profile-images/{fname}"
    update_user_profile_image(user_id, image_url)
    updated = get_user(user_id)
    return {
        "ok": True,
        "imageUrl": image_url,
        "user": user_to_public(updated or current_user),
    }
