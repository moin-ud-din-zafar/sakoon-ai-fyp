"""Crisis and risk detection using rules + ML classifier score."""

from typing import Dict, Any

from app.core.constants import CRISIS_KEYWORDS, CRISIS_THRESHOLD, HELPLINE_NUMBERS


class RiskDetector:
    """Detects crisis/high-risk indicators in user messages."""

    def check(self, text: str, classification: str, confidence: float) -> Dict[str, Any]:
        """Check for crisis. Returns dict with is_crisis, risk_level."""
        return check_risk(text, classification, confidence)


def check_risk(text: str, classification: str, confidence: float) -> Dict[str, Any]:
    """
    Determine if message indicates crisis/high risk.

    Uses:
        1. Rule-based: keyword matching
        2. ML-based: Suicidal classification with high confidence

    Returns:
        Dict with is_crisis (bool), risk_level (low|medium|high), helpline_numbers
    """
    text_lower = text.lower() if text else ""
    is_crisis = False
    risk_level = "low"

    # Rule-based: crisis keywords
    for kw in CRISIS_KEYWORDS:
        if kw.lower() in text_lower:
            is_crisis = True
            risk_level = "high"
            break

    # ML-based: Suicidal with high confidence
    if classification == "Suicidal" and confidence >= CRISIS_THRESHOLD:
        is_crisis = True
        risk_level = "high"

    # Medium risk: Suicidal class but below threshold
    if not is_crisis and classification == "Suicidal" and confidence > 0.3:
        risk_level = "medium"

    helplines = HELPLINE_NUMBERS if is_crisis else []

    return {
        "is_crisis": is_crisis,
        "risk_level": risk_level,
        "helpline_numbers": helplines,
    }
