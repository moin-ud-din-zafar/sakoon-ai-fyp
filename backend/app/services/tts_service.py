"""Text-to-Speech service.

Providers (tried in order based on config):
  1. XTTS-v2  — Coqui high-quality multilingual TTS  (USE_XTTS=true)
  2. Edge-TTS  — Microsoft neural voices, fast, no local model needed (default)
"""

import io
import logging
import os
import threading
from pathlib import Path
from typing import List, Optional

from app.config import USE_XTTS, XTTS_REFERENCE_WAV, EDGE_TTS_DEFAULT_VOICE

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# XTTS-v2 provider
# ─────────────────────────────────────────────────────────────────────────────

# USE_XTTS and XTTS_REFERENCE_WAV are now sourced from app.config (see config.py)
XTTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

# Language codes recognised by XTTS-v2
_XTTS_LANG_MAP = {
    "en": "en",
    "ur": "hi",   # XTTS-v2 doesn't have Urdu; Hindi is the closest supported
    "hi": "hi",
    "ar": "ar",
    "fr": "fr",
    "de": "de",
    "es": "es",
    "pt": "pt",
    "tr": "tr",
    "ru": "ru",
    "nl": "nl",
    "cs": "cs",
    "pl": "pl",
    "it": "it",
    "zh": "zh-cn",
    "ja": "ja",
    "ko": "ko",
}

_xtts_model = None
_xtts_lock = threading.Lock()


def _load_xtts():
    """Lazy-load XTTS-v2 once and cache globally (thread-safe)."""
    global _xtts_model
    if _xtts_model is not None:
        return _xtts_model
    with _xtts_lock:
        if _xtts_model is not None:
            return _xtts_model
        try:
            from TTS.api import TTS as CoquiTTS  # pip install TTS
            logger.info("tts_service: loading XTTS-v2 model (first run downloads ~1.9 GB)...")
            _xtts_model = CoquiTTS(XTTS_MODEL_NAME)
            logger.info("tts_service: XTTS-v2 ready")
        except Exception as exc:
            logger.error("tts_service: XTTS-v2 load failed: %s", exc)
            _xtts_model = None
    return _xtts_model


def generate_xtts_audio(
    text: str,
    language: Optional[str] = None,
    reference_wav: Optional[str] = None,
) -> Optional[bytes]:
    """Generate WAV audio using XTTS-v2.

    Returns raw WAV bytes, or None on failure.
    WAV (not MP3) is required as input for Wav2Lip.
    """
    if not text.strip():
        return None
    model = _load_xtts()
    if model is None:
        return None

    lang_code = _XTTS_LANG_MAP.get((language or "en")[:2].lower(), "en")
    ref_wav = reference_wav or XTTS_REFERENCE_WAV or None

    try:
        import tempfile, soundfile as sf  # noqa: E401

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        if ref_wav and Path(ref_wav).exists():
            model.tts_to_file(
                text=text[:500],
                speaker_wav=ref_wav,
                language=lang_code,
                file_path=tmp_path,
            )
        else:
            # Use first available speaker when no reference provided
            speakers = getattr(model, "speakers", None) or []
            speaker = speakers[0] if speakers else None
            model.tts_to_file(
                text=text[:500],
                speaker=speaker,
                language=lang_code,
                file_path=tmp_path,
            )

        with open(tmp_path, "rb") as f:
            wav_bytes = f.read()
        os.unlink(tmp_path)
        logger.info("tts_service: XTTS-v2 generated %d bytes (lang=%s)", len(wav_bytes), lang_code)
        return wav_bytes

    except Exception as exc:
        logger.warning("tts_service: XTTS-v2 inference failed: %s", exc)
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        return None

# Edge neural voices by short language code (matches app language_preference prefix)
EDGE_VOICE_BY_LANG = {
    "en": "en-US-JennyNeural",
    "ur": "ur-PK-UzmaNeural",
    "hi": "hi-IN-SwaraNeural",
    "ps": "en-US-JennyNeural",
    "sd": "en-US-JennyNeural",
    "sk": "en-US-JennyNeural",
}

# If primary voice fails (network / invalid voice id), try these in order
FALLBACK_VOICES: List[str] = [
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-GB-SoniaNeural",
]


def get_tts_voice_for_language(lang: Optional[str]) -> str:
    """Map language preference (e.g. en, ur) to Edge-TTS voice name."""
    if not lang:
        return EDGE_TTS_DEFAULT_VOICE
    code = str(lang).lower().strip()[:2]
    return EDGE_VOICE_BY_LANG.get(code, EDGE_TTS_DEFAULT_VOICE)


async def _try_voice(text: str, voice: str) -> Optional[bytes]:
    import edge_tts

    communicate = edge_tts.Communicate(text.strip(), voice)
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks) if chunks else None


async def generate_tts_audio_async(
    text: str,
    voice: Optional[str] = None,
    language: Optional[str] = None,
) -> Optional[bytes]:
    """
    Generate audio from text using Edge-TTS (async — safe inside FastAPI event loop).
    """
    if not (text or "").strip():
        return None

    primary = voice or get_tts_voice_for_language(language)
    to_try = [primary]
    if primary.startswith("ur-"):
        for alt in ("ur-PK-AsadNeural", "ur-IN-GulNeural"):
            if alt not in to_try:
                to_try.append(alt)
    for v in FALLBACK_VOICES:
        if v not in to_try:
            to_try.append(v)

    last_err: Optional[Exception] = None
    for v in to_try:
        try:
            out = await _try_voice(text, v)
            if out:
                if v != primary:
                    logger.info("TTS used fallback voice %s (primary %s failed)", v, primary)
                return out
        except Exception as e:
            last_err = e
            logger.warning("TTS voice %s failed: %s", v, e)

    if last_err:
        logger.error("TTS failed for all voices: %s", last_err)
    return None


def generate_tts_audio(
    text: str,
    voice: Optional[str] = None,
    language: Optional[str] = None,
) -> Optional[bytes]:
    """Sync wrapper for scripts/CLI only."""
    import asyncio

    return asyncio.run(generate_tts_audio_async(text, voice=voice, language=language))


async def generate_speech_wav(
    text: str,
    language: Optional[str] = None,
) -> Optional[bytes]:
    """Return WAV bytes suitable for Wav2Lip input.

    Tries XTTS-v2 first (if USE_XTTS=true), then converts Edge-TTS MP3 to WAV.
    """
    import asyncio

    # 1. XTTS-v2 → already outputs WAV
    if USE_XTTS:
        loop = asyncio.get_event_loop()
        wav = await loop.run_in_executor(
            None, generate_xtts_audio, text, language, None
        )
        if wav:
            return wav

    # 2. Edge-TTS → MP3 → convert to WAV via pydub / ffmpeg
    mp3 = await generate_tts_audio_async(text, language=language)
    if not mp3:
        return None
    try:
        from pydub import AudioSegment
        seg = AudioSegment.from_mp3(io.BytesIO(mp3))
        buf = io.BytesIO()
        seg.export(buf, format="wav")
        return buf.getvalue()
    except Exception:
        # pydub/ffmpeg not available — return MP3 anyway (Wav2Lip requires WAV,
        # avatar_service will handle this case)
        logger.warning("tts_service: pydub unavailable; returning MP3 as fallback")
        return mp3
