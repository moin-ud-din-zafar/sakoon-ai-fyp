"""
Language detection utility.
Detects Urdu (Arabic script + Roman Urdu), English, and other languages.
Uses langdetect for Latin-script detection + Unicode range check for Nastaliq script.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Arabic/Urdu Unicode block (U+0600–U+06FF)
_ARABIC_BLOCK = re.compile(r"[\u0600-\u06FF]")

# Roman Urdu indicator words (word-boundary safe matching)
_ROMAN_URDU_WORDS = (
    "meri", "mera", "meray", "tum", "tumhari", "aap", "aapko",
    "hai", "hain", "ho", "hon", "kya", "kyun", "kab", "kahan",
    "kisi", "karun", "karo", "karna", "tabiyat", "dil", "dill",
    "bahut", "bohat", "thora", "thori", "theek", "tik", "nahi",
    "mein", "main", "mai", "ab", "aaj", "aj", "kal", "phir",
    "par", "pe", "ko", "se", "kharab", "achha", "acha", "zyada",
    "zada", "sun", "suno", "dard", "yar", "yaar", "bhai", "jan",
    "matlab", "sab", "kaam", "kaun", "kaisi", "kaise", "jab",
    "jo", "wo", "bilkul", "shukriya", "mashallah", "bas", "sirf",
    "bhi", "mujhe", "mujhko", "hum", "hamari", "unka", "usi",
    "yahan", "wahan", "gussa", "bechaini", "udas", "tang", "zindagi",
    "mushkil", "problem", "pareshan", "khush", "dukhi", "rone",
    "rota", "roti", "thaka", "thaki", "nind", "neend",
)

_ENGLISH_ONLY_PHRASES = (
    "how are you", "how's it going", "how is it going",
    "what's up", "whats up", "thank you", "thanks",
    "hello", "hi there", "hey there", "good morning",
    "good night", "good afternoon", "see you", "bye",
)


def _word_hit(text: str, word: str) -> bool:
    """Avoid false positives: 'ho' in 'how', 'par' in 'prepare'."""
    w = word.lower()
    if len(w) <= 3:
        return re.search(rf"(?<![a-z0-9]){re.escape(w)}(?![a-z0-9])", text) is not None
    return w in text


def detect_language(text: str) -> str:
    """
    Detect language of text.

    Returns:
        "ur"  - Urdu (Nastaliq or Roman)
        "en"  - English
        "xx"  - Other / unknown
    """
    text = (text or "").strip()
    if not text:
        return "en"

    # 1. Nastaliq Arabic-script Urdu
    if _ARABIC_BLOCK.search(text):
        return "ur"

    lower = text.lower()

    # 2. Short plain English greetings — skip Urdu scan
    if any(p in lower for p in _ENGLISH_ONLY_PHRASES) and len(lower) < 80:
        # still check urdu hits
        pass

    # 3. Roman Urdu token counting
    hits = sum(1 for w in _ROMAN_URDU_WORDS if _word_hit(lower, w))
    if hits >= 2:
        return "ur"
    if hits >= 1 and len(lower) >= 4:
        return "ur"

    # 4. Fallback: langdetect
    try:
        from langdetect import detect as _ld_detect
        detected = _ld_detect(text)
        if detected in ("ur", "ar", "fa"):
            return "ur"
        if detected.startswith("en"):
            return "en"
        return detected[:2]
    except Exception:
        return "en"


def is_urdu(text: str) -> bool:
    return detect_language(text) == "ur"


def is_english(text: str) -> bool:
    return detect_language(text) == "en"
