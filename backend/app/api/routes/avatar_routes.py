"""Avatar routes — Sakoon AI.

Endpoints:
  GET  /avatar/status          — Check if Wav2Lip + XTTS are configured
  POST /avatar/speak           — Generate talking avatar video (or audio fallback)
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.services.avatar_service import generate_talking_avatar, get_avatar_status

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/avatar", tags=["avatar"])


class AvatarSpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    language: Optional[str] = Field(
        default="en",
        description="Short language code: en, ur, hi ...",
    )
    face_image_path: Optional[str] = Field(
        default=None,
        description="Absolute server-side path to face image. Leave empty to use default.",
    )


@router.get("/status", summary="Avatar system setup status")
def avatar_status():
    """Returns which parts of the avatar pipeline are ready."""
    return get_avatar_status()


@router.post("/speak", summary="Generate talking avatar video or audio")
async def avatar_speak(req: AvatarSpeakRequest):
    """Generate speech from text and animate a face with Wav2Lip.

    Response:
      - video/mp4  when Wav2Lip is configured and inference succeeds
      - audio/wav  when Wav2Lip is not set up (graceful degradation)

    Response header  X-Avatar-Mode: video | audio | error
    """
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text must not be blank")

    content, mode = await generate_talking_avatar(
        text=req.text,
        language=req.language or "en",
        face_image_path=req.face_image_path or None,
    )

    if mode == "error" or not content:
        raise HTTPException(
            status_code=503,
            detail="Avatar generation failed. Check TTS configuration.",
        )

    media_type = "video/mp4" if mode == "video" else "audio/wav"
    logger.info("avatar_routes: returning %s (%d bytes)", mode, len(content))

    return Response(
        content=content,
        media_type=media_type,
        headers={"X-Avatar-Mode": mode},
    )
