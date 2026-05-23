"""Text preprocessing for mental health classification."""

import re
from typing import Optional


def preprocess_text(text: str, normalize_roman_urdu: bool = False) -> str:
    """
    Clean and normalize text for MH classification.

    Args:
        text: Raw input text (can be empty or None)
        normalize_roman_urdu: If True, apply basic Roman Urdu normalization

    Returns:
        Cleaned text, lowercase, trimmed
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to string and strip
    cleaned = str(text).strip()

    # Lowercase for consistency
    cleaned = cleaned.lower()

    # Remove URLs
    cleaned = re.sub(r"https?://\S+|www\.\S+", "", cleaned)

    # Remove @mentions (social media)
    cleaned = re.sub(r"@\w+", "", cleaned)

    # Remove hashtags but keep the word (optional: remove entirely)
    cleaned = re.sub(r"#(\w+)", r"\1", cleaned)

    # Remove extra whitespace and newlines
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Remove common noise (repeated punctuation)
    cleaned = re.sub(r"([.!?]){2,}", r"\1", cleaned)

    # Trim
    cleaned = cleaned.strip()

    if normalize_roman_urdu:
        cleaned = _normalize_roman_urdu(cleaned)

    return cleaned


def _normalize_roman_urdu(text: str) -> str:
    """
    Basic Roman Urdu normalization (common transliterations).
    Expands common contractions and standardizes spellings.
    """
    # Common Roman Urdu variations → standard form
    replacements = {
        r"\bko\b": "ko",
        r"\bmain\b": "main",
        r"\bhai\b": "hai",
        r"\bho\b": "ho",
        r"\bhain\b": "hain",
        r"\bka\b": "ka",
        r"\bki\b": "ki",
        r"\bke\b": "ke",
    }
    result = text
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result
