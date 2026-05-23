"""Avatar Service — Sakoon AI.

Pipeline:
  text  ──► TTS (XTTS-v2 or Edge-TTS)  ──► WAV audio
  WAV + face image  ──► Wav2Lip  ──► MP4 video

Degrades gracefully:
  - If Wav2Lip is not set up  → returns audio-only bytes + mode="audio"
  - If XTTS-v2 is not enabled → uses Edge-TTS (MP3 converted to WAV)
  - If face image is missing  → returns audio-only

Environment variables (all optional):
  WAV2LIP_DIR          Path to the cloned Wav2Lip repo
  WAV2LIP_CHECKPOINT   Path to wav2lip_gan.pth / wav2lip.pth
  AVATAR_FACE_IMAGE    Path to the face image (JPG/PNG) used for animation
  WAV2LIP_PYTHON       Python executable inside Wav2Lip's env (default: python)
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

WAV2LIP_DIR: str = os.getenv(
    "WAV2LIP_DIR",
    str(Path(__file__).resolve().parents[3] / "wav2lip"),
)
WAV2LIP_CHECKPOINT: str = os.getenv(
    "WAV2LIP_CHECKPOINT",
    str(Path(WAV2LIP_DIR) / "checkpoints" / "wav2lip_gan.pth"),
)
AVATAR_FACE_IMAGE: str = os.getenv(
    "AVATAR_FACE_IMAGE",
    str(Path(__file__).resolve().parents[3] / "frontend" / "public" / "avatars" / "face.jpg"),
)
WAV2LIP_PYTHON: str = os.getenv("WAV2LIP_PYTHON", "python")

# Wav2Lip output quality settings
_RESIZE_FACTOR = int(os.getenv("WAV2LIP_RESIZE", "1"))   # 1 = full res
_PAD_TOP       = int(os.getenv("WAV2LIP_PAD_TOP", "0"))
_PAD_BOTTOM    = int(os.getenv("WAV2LIP_PAD_BOTTOM", "10"))
_PAD_LEFT      = int(os.getenv("WAV2LIP_PAD_LEFT", "0"))
_PAD_RIGHT     = int(os.getenv("WAV2LIP_PAD_RIGHT", "0"))


# ─────────────────────────────────────────────────────────────────────────────
# Availability checks (cheap — checked at request time)
# ─────────────────────────────────────────────────────────────────────────────

def wav2lip_available() -> bool:
    """True if Wav2Lip repo + checkpoint + face image are all present."""
    inference = Path(WAV2LIP_DIR) / "inference.py"
    checkpoint = Path(WAV2LIP_CHECKPOINT)
    face = Path(AVATAR_FACE_IMAGE)
    ok = inference.exists() and checkpoint.exists() and face.exists()
    if not ok:
        missing = [
            str(p) for p in [inference, checkpoint, face] if not p.exists()
        ]
        logger.debug("avatar_service: Wav2Lip not ready. Missing: %s", missing)
    return ok


def get_avatar_status() -> dict:
    """Return setup status for the /avatar/status endpoint."""
    return {
        "wav2lipReady": wav2lip_available(),
        "wav2lipDir": WAV2LIP_DIR,
        "wav2lipCheckpoint": WAV2LIP_CHECKPOINT,
        "faceImage": AVATAR_FACE_IMAGE,
        "faceImageExists": Path(AVATAR_FACE_IMAGE).exists(),
        "checkpointExists": Path(WAV2LIP_CHECKPOINT).exists(),
        "wav2lipInferenceExists": (Path(WAV2LIP_DIR) / "inference.py").exists(),
        "xttsModeActive": os.getenv("USE_XTTS", "false").lower() in ("1", "true", "yes"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Core pipeline
# ─────────────────────────────────────────────────────────────────────────────

async def generate_talking_avatar(
    text: str,
    language: Optional[str] = "en",
    face_image_path: Optional[str] = None,
) -> Tuple[bytes, str]:
    """Generate a talking avatar video (or audio fallback).

    Returns:
        (content_bytes, mode)
        mode = "video"  → MP4 bytes
        mode = "audio"  → WAV/MP3 bytes (Wav2Lip not available)
        mode = "error"  → empty bytes, something failed completely
    """
    from app.services.tts_service import generate_speech_wav

    # ── 1. Generate speech audio ────────────────────────────────────────────
    audio_bytes = await generate_speech_wav(text, language=language)
    if not audio_bytes:
        logger.error("avatar_service: TTS produced no audio for text[:80]=%r", text[:80])
        return b"", "error"

    # ── 2. Skip Wav2Lip if not configured ───────────────────────────────────
    face = face_image_path or AVATAR_FACE_IMAGE
    if not wav2lip_available() or not Path(face).exists():
        logger.info("avatar_service: Wav2Lip not ready — returning audio only")
        return audio_bytes, "audio"

    # ── 3. Write audio to temp file ─────────────────────────────────────────
    tmp_dir = Path(tempfile.gettempdir()) / "sakoon_avatar"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex[:8]
    audio_path = tmp_dir / f"speech_{run_id}.wav"
    video_path = tmp_dir / f"avatar_{run_id}.mp4"

    try:
        audio_path.write_bytes(audio_bytes)
        logger.info("avatar_service: audio written to %s (%d bytes)", audio_path, len(audio_bytes))

        # ── 4. Run Wav2Lip ───────────────────────────────────────────────────
        video_bytes = await _run_wav2lip(
            face_path=str(face),
            audio_path=str(audio_path),
            out_path=str(video_path),
        )

        if video_bytes:
            logger.info("avatar_service: video generated %d bytes", len(video_bytes))
            return video_bytes, "video"

        # Wav2Lip ran but produced nothing — fall back to audio
        logger.warning("avatar_service: Wav2Lip produced empty output — returning audio")
        return audio_bytes, "audio"

    finally:
        _cleanup(audio_path, video_path)


async def _run_wav2lip(
    face_path: str,
    audio_path: str,
    out_path: str,
) -> Optional[bytes]:
    """Run Wav2Lip inference.py in a subprocess and return video bytes."""
    cmd = [
        WAV2LIP_PYTHON,
        str(Path(WAV2LIP_DIR) / "inference.py"),
        "--checkpoint_path", WAV2LIP_CHECKPOINT,
        "--face",            face_path,
        "--audio",           audio_path,
        "--outfile",         out_path,
        "--resize_factor",   str(_RESIZE_FACTOR),
        "--pads",
            str(_PAD_TOP),
            str(_PAD_BOTTOM),
            str(_PAD_LEFT),
            str(_PAD_RIGHT),
        "--nosmooth",
    ]

    logger.info("avatar_service: running Wav2Lip: %s", " ".join(cmd))

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd,
                cwd=WAV2LIP_DIR,
                capture_output=True,
                text=True,
                timeout=120,   # 2 min max
            ),
        )

        if result.returncode != 0:
            logger.error(
                "avatar_service: Wav2Lip exited %d\nstdout: %s\nstderr: %s",
                result.returncode,
                result.stdout[-800:],
                result.stderr[-800:],
            )
            return None

        out = Path(out_path)
        if out.exists() and out.stat().st_size > 0:
            return out.read_bytes()

        logger.warning("avatar_service: Wav2Lip finished but output file missing/empty")
        return None

    except subprocess.TimeoutExpired:
        logger.error("avatar_service: Wav2Lip timed out after 120 s")
        return None
    except Exception as exc:
        logger.error("avatar_service: Wav2Lip subprocess error: %s", exc)
        return None


def _cleanup(*paths: Path) -> None:
    for p in paths:
        try:
            if Path(p).exists():
                Path(p).unlink()
        except Exception:
            pass
