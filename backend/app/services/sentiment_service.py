"""
Sentiment Analysis Service — direct PyTorch inference (no TF dependency).
Model: cardiffnlp/twitter-roberta-base-sentiment-latest
Output: { "sentiment": "negative", "confidence": 0.88 }
Labels: positive, negative, neutral
"""

from app.utils.env_patch import patch_protobuf  # noqa: F401
import logging
import hashlib
from typing import Dict

logger = logging.getLogger(__name__)

_SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Model card labels (vary by model version)
_LABEL_MAP: Dict[str, str] = {
    "label_0":  "negative",
    "label_1":  "neutral",
    "label_2":  "positive",
    "negative": "negative",
    "neutral":  "neutral",
    "positive": "positive",
}

_FALLBACK = {"sentiment": "neutral", "confidence": 0.0}

_cache: Dict[str, Dict] = {}
_CACHE_MAX = 128

_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        _tokenizer = AutoTokenizer.from_pretrained(_SENTIMENT_MODEL)
        _model = AutoModelForSequenceClassification.from_pretrained(_SENTIMENT_MODEL)
        _model.eval()
        logger.info("sentiment_service: model loaded (%s)", _SENTIMENT_MODEL)
    return _tokenizer, _model


def _cache_key(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode(), usedforsecurity=False).hexdigest()


def detect_sentiment(text: str) -> Dict[str, object]:
    """
    Detect overall sentiment from user text.

    Args:
        text: English user input.

    Returns:
        {"sentiment": str, "confidence": float}
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

        raw_label: str = model.config.id2label[top_idx].lower()
        sentiment = _LABEL_MAP.get(raw_label, "neutral")
        result = {"sentiment": sentiment, "confidence": round(top_score, 4)}

        if len(_cache) >= _CACHE_MAX:
            _cache.pop(next(iter(_cache)))
        _cache[key] = result
        return dict(result)

    except Exception as exc:
        logger.warning("sentiment_service.detect_sentiment failed: %s", exc)
        return dict(_FALLBACK)
