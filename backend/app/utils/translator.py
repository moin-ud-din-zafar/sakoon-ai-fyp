"""
Translation utility — local transformers pipeline (no API token needed).
Translates non-English text to English before feeding HuggingFace models.
Model: Helsinki-NLP/opus-mt-ur-en for Urdu→English.
Falls back to returning original text if translation fails.
"""

from app.utils.env_patch import patch_protobuf  # noqa: F401
import logging
import hashlib
from typing import Dict, Optional

from app.utils.language_detector import detect_language

logger = logging.getLogger(__name__)

_UR_EN_MODEL = "Helsinki-NLP/opus-mt-ur-en"

_cache: Dict[str, str] = {}
_CACHE_MAX = 256

# Lazy-loaded local pipeline
_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        try:
            from transformers import pipeline as hf_pipeline
            _pipeline = hf_pipeline(
                "translation",
                model=_UR_EN_MODEL,
                framework="pt",
            )
            logger.info("translator: pipeline loaded (%s)", _UR_EN_MODEL)
        except Exception as exc:
            logger.error("translator: failed to load pipeline: %s", exc)
            raise
    return _pipeline


def _cache_key(text: str, src: str, tgt: str) -> str:
    raw = f"{src}:{tgt}:{text.strip().lower()}"
    return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()


def translate_to_english(text: str, source_lang: Optional[str] = None) -> str:
    """
    Translate text to English using a local HuggingFace model.
    If already English, returns as-is.

    Args:
        text: Source text.
        source_lang: Override auto-detected language ("ur", "en", …).

    Returns:
        English text, or original on failure.
    """
    text = (text or "").strip()
    if not text:
        return text

    lang = source_lang or detect_language(text)
    if lang == "en":
        return text

    key = _cache_key(text, lang, "en")
    if key in _cache:
        return _cache[key]

    try:
        pipe = _get_pipeline()
        results = pipe(text[:512])
        if not results:
            return text

        translated: str = results[0].get("translation_text", "").strip()
        if not translated:
            return text

        if len(_cache) >= _CACHE_MAX:
            oldest = next(iter(_cache))
            _cache.pop(oldest, None)
        _cache[key] = translated
        return translated

    except Exception as exc:
        logger.warning("translator.translate_to_english failed: %s — using original", exc)
        return text


def normalize_input(text: str) -> str:
    """
    Normalize user input for HuggingFace model consumption.
    - Nastaliq Urdu (Arabic script) → translate to English via Helsinki-NLP model.
    - Roman Urdu (Latin script) → pass as-is (emotion models read Latin).
    - English → pass as-is.
    """
    import re
    text = (text or "").strip()
    if not text:
        return text
    # Only translate if actual Arabic/Urdu script — Roman Urdu passes through
    has_arabic_script = bool(re.search(r"[\u0600-\u06FF]", text))
    if has_arabic_script:
        return translate_to_english(text, source_lang="ur")
    return text
