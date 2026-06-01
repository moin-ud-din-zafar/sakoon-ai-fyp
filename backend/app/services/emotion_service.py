"""
Emotion Detection Service — direct PyTorch inference (no TF dependency).
Model: j-hartmann/emotion-english-distilroberta-base
Output: { "emotion": "sadness", "confidence": 0.92 }
Classes: anger, disgust, fear, joy, neutral, sadness, surprise
"""

from app.utils.env_patch import patch_protobuf  # noqa: F401 — side-effect import
import os
import logging
import hashlib
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

_EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

_LABEL_MAP: Dict[str, str] = {
    "anger":    "angry",
    "disgust":  "disgust",
    "fear":     "anxious",
    "joy":      "happy",
    "neutral":  "neutral",
    "sadness":  "sad",
    "surprise": "surprised",
}

_FALLBACK = {"emotion": "neutral", "confidence": 0.0}

_cache: Dict[str, Dict] = {}
_CACHE_MAX = 128

_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        _tokenizer = AutoTokenizer.from_pretrained(_EMOTION_MODEL)
        _model = AutoModelForSequenceClassification.from_pretrained(_EMOTION_MODEL)
        _model.eval()
        logger.info("emotion_service: model loaded (%s)", _EMOTION_MODEL)
    return _tokenizer, _model


def _cache_key(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode(), usedforsecurity=False).hexdigest()


def detect_emotion(text: str) -> Dict[str, object]:
    """
    Detect the top emotion from user text.

    Args:
        text: English user input (translate first if Urdu).

    Returns:
        {"emotion": str, "confidence": float}
    """
    text = (text or "").strip()
    if not text:
        return dict(_FALLBACK)

    key = _cache_key(text)
    if key in _cache:
        return dict(_cache[key])

    try:
        import torch
        import torch.nn.functional as F

        tokenizer, model = _load_model()

        inputs = tokenizer(
            text[:512],
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        with torch.no_grad():
            logits = model(**inputs).logits

        probs = F.softmax(logits, dim=-1).squeeze()
        top_idx = int(torch.argmax(probs).item())
        top_score = float(probs[top_idx].item())

        # model.config.id2label: {0: "anger", 1: "disgust", ...}
        raw_label: str = model.config.id2label[top_idx].lower()
        emotion = _LABEL_MAP.get(raw_label, raw_label)
        result = {"emotion": emotion, "confidence": round(top_score, 4)}

        if len(_cache) >= _CACHE_MAX:
            _cache.pop(next(iter(_cache)))
        _cache[key] = result
        return dict(result)

    except Exception as exc:
        logger.warning("emotion_service.detect_emotion failed: %s", exc)
        return dict(_FALLBACK)


def detect_emotion_full(text: str):
    """Return ALL emotion scores sorted desc (for analytics)."""
    text = (text or "").strip()
    if not text:
        return []
    try:
        import torch
        import torch.nn.functional as F

        tokenizer, model = _load_model()
        inputs = tokenizer(text[:512], return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1).squeeze()

        results = []
        for idx, prob in enumerate(probs.tolist()):
            raw = model.config.id2label[idx].lower()
            results.append({
                "emotion": _LABEL_MAP.get(raw, raw),
                "raw_label": raw,
                "confidence": round(float(prob), 4),
            })
        return sorted(results, key=lambda x: x["confidence"], reverse=True)
    except Exception as exc:
        logger.warning("detect_emotion_full failed: %s", exc)
        return []
