"""TTS route: text-to-speech via Edge-TTS."""

from fastapi import APIRouter
from fastapi.responses import Response
from typing import Optional

from pydantic import BaseModel, Field

from app.services.tts_service import generate_tts_audio_async

router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = Field(
        default=None,
        description="Short code: en, ur, hi — selects Edge-TTS voice",
    )
    voice: Optional[str] = Field(
        default=None,
        description="Override Edge voice id (e.g. en-US-GuyNeural)",
    )


@router.post("/speak")
async def speak(req: TTSRequest):
    """Convert text to speech, return audio/mpeg."""
    audio_bytes = await generate_tts_audio_async(
        req.text, voice=req.voice, language=req.language
    )
    if not audio_bytes:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"detail": "TTS unavailable. Install edge-tts and ensure it works."},
        )
    return Response(content=audio_bytes, media_type="audio/mpeg")
