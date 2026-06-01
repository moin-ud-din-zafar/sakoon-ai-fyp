"""
Therapy Response Generator — HuggingFace InferenceClient (PRIMARY)
Model: mistralai/Mistral-7B-Instruct-v0.3 (falls back to zephyr-7b-beta)
Keeps the deeply-crafted Sakoon therapeutic persona from llm_service.py.
"""

import logging
from typing import Optional

from huggingface_hub import InferenceClient
from app.config import HF_TOKEN, HF_CHAT_MODEL
from app.core.constants import HELPLINE_NUMBERS

logger = logging.getLogger(__name__)

_FALLBACK_MODEL = "HuggingFaceH4/zephyr-7b-beta"

# ── Tone guidance per detected emotion ──────────────────────────────────────

_EMOTION_TONE: dict = {
    "sad":       "Tone: comforting. Soft landing — no forced cheer. Small warm reflection.",
    "angry":     "Tone: calming. Anger often protects something tender. Stay grounded, lower verbal temperature.",
    "anxious":   "Tone: reassuring. Slow down. Don't flood with options. Stay with one worry or just stay present.",
    "fear":      "Tone: reassuring and grounding. One concrete anchor, then soft presence.",
    "happy":     "Tone: encouraging. Meet their energy warmly — genuine, not over-the-top.",
    "surprised": "Tone: curious warmth. Make space for what they are processing.",
    "disgust":   "Tone: steady and non-judgmental. Acknowledge without moralising.",
    "distressed": "Tone: SAFETY. Very short (2–4 lines). Grounding first. Warm, plain, human.",
    "neutral":   "Tone: curious warmth — gently explore what they bring.",
}

_SENTIMENT_CONTEXT: dict = {
    "negative": "Their overall mood is negative — prioritise validation and presence over advice.",
    "positive": "Their overall mood is positive — match warmth; brief encouragement fits.",
    "neutral":  "Neutral mood — open, exploratory tone.",
}

# ── System prompt (Sakoon persona — kept identical to llm_service.py core) ───

_SYSTEM_EN = """You are Sakoon — a deeply present, emotionally intelligent human therapist in spirit (not a chatbot).
You sense what lies beneath the user's words — without claiming to know them better than they do.
Your job is not to "reply" — it is to sit with the person and, when it fits, softly deepen.
Never sound like software. Never mention AI, bots, or "I'm here to help."

HOW TO RESPOND:
- Acknowledge the emotional tone lightly.
- Reflect ONE possible deeper layer using uncertainty ("maybe…", "it feels like…", "I wonder if…").
- Choose ONE closing move: a single soft question OR a gentle suggestion OR pure presence — never two questions.
- Hard ceiling: 2–5 short lines. At most one "?" in the whole reply.
- FORBIDDEN: "you are not alone", "I understand your feelings", bullet lists, clinical labels, instant fixes.
- Final test: does this read like a calm human beside them — or a system? If system, rewrite."""

_SYSTEM_UR = """Aap Sakoon hain — deeply present, samajhdaar (chatbot nahi).
Sirf alfaaz nahi — narmi se un ke neeche kya ho sakta hai, bina yeh keh ke ke tum 100% jaante ho.
Jawab machine jaisa nahi. "AI", "madad ke liye hun" — nahi.
Saath, phir gehraai jab munasib ho. Roman Urdu bol-chaal.

KAISA JAWAB DENA HAI:
- Halka acknowledge karein.
- EK gehra layer shayad/lagta hai/dil mein aata hai se.
- EK closing: ek narm sawal YA suggestion YA sirf mauzoodgi — do sawal ek jawab mein nahi.
- 2–5 chhote jumle. Zyada se zyada ek "?".
- MANA: "tum akayle nahi", "main samajhti hun tumhara dard", list, label, foran solution."""


def _build_prompt(
    user_message: str,
    emotion: str,
    sentiment: str,
    mh_classification: str = "",
    is_crisis: bool = False,
    conversation_memory: str = "",
    language: str = "en",
) -> tuple[str, str]:
    """Build (system_prompt, user_prompt) for the HF chat model."""
    lang = (language or "en").lower().strip()
    system = _SYSTEM_UR if lang in ("ur", "urdu") else _SYSTEM_EN

    tone = _EMOTION_TONE.get(emotion, _EMOTION_TONE["neutral"])
    sent_ctx = _SENTIMENT_CONTEXT.get(sentiment, _SENTIMENT_CONTEXT["neutral"])

    if is_crisis:
        helplines = ", ".join(f"{h['name']}: {h['number']}" for h in HELPLINE_NUMBERS)
        crisis_note = (
            f"\n[SAFETY MODE: User may be in acute distress. "
            f"Grounding first (breath, feet, cold water). 2–4 lines max. "
            f"Weave in these helplines naturally: {helplines}. "
            f"No toxic positivity. No banned phrases.]"
        )
        system += crisis_note

    mem_block = ""
    if conversation_memory and not is_crisis:
        mem_block = (
            f"\n[Thread — last ~5 turns. Sense returning feelings and momentum. "
            f"Weave continuity without citing the past directly.]\n"
            f"{conversation_memory}\n"
        )

    lang_remind = (
        "Reply in natural conversational Roman Urdu (Pakistani bol-chaal)."
        if lang in ("ur", "urdu")
        else "Match user language: Roman Urdu if they wrote it, English otherwise."
    )

    user_prompt = f"""[Internal context — do NOT expose to user]
Detected emotion: {emotion}
Overall sentiment: {sentiment}
Mental health category: {mh_classification or "not classified"}
{tone}
{sent_ctx}
{mem_block}
Language: {lang_remind}

[User's message]
{user_message}

[Your reply — follow the system instructions. Acknowledge → one uncertain deeper layer → ONE closing move. 2–5 short lines. At most one "?". Calm human presence, not a system.]"""

    return system, user_prompt


def generate_therapy_response(
    text: str,
    emotion: str,
    sentiment: str,
    mh_classification: str = "",
    is_crisis: bool = False,
    conversation_memory: str = "",
    language: str = "en",
) -> str:
    """
    Generate empathetic therapy response using HuggingFace Mistral-7B.

    Args:
        text: Original user message (in their language — reply will match).
        emotion: Top detected emotion (from emotion_service).
        sentiment: Overall sentiment (from sentiment_service).
        mh_classification: Mental health category from classifier.
        is_crisis: Whether crisis safety mode should activate.
        conversation_memory: Recent turns as plain text.
        language: Reply language code ("en" / "ur" / …).

    Returns:
        Therapy response string.
    """
    if not HF_TOKEN:
        logger.warning("therapy_service: HF_TOKEN not set — returning fallback")
        return _fallback_response(emotion, sentiment, is_crisis, language)

    system, user_prompt = _build_prompt(
        user_message=text,
        emotion=emotion,
        sentiment=sentiment,
        mh_classification=mh_classification,
        is_crisis=is_crisis,
        conversation_memory=conversation_memory,
        language=language,
    )

    models_to_try = [HF_CHAT_MODEL, _FALLBACK_MODEL]

    for model in models_to_try:
        try:
            # Use the classic HF Inference API endpoint (no "Inference Providers" permission needed)
            client = InferenceClient(
                token=HF_TOKEN,
                base_url="https://api-inference.huggingface.co",
            )
            completion = client.chat_completion(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user_prompt},
                ],
                model=model,
                max_tokens=200 if is_crisis else 240,
                temperature=0.65 if is_crisis else 0.80,
            )
            content = (
                completion.choices[0].message.content
                if completion.choices
                else None
            )
            if content and content.strip():
                return content.strip()
        except Exception as exc:
            logger.warning("therapy_service: model %s failed: %s", model, exc)
            continue

    return _fallback_response(emotion, sentiment, is_crisis, language)


# ── Structured fallbacks (used when HF is unavailable) ──────────────────────

def _fallback_response(
    emotion: str,
    sentiment: str,
    is_crisis: bool,
    language: str = "en",
) -> str:
    lang = (language or "en").lower().strip()[:2]

    if lang == "ur":
        if is_crisis:
            lines = "\n".join(f"- {h['name']}: {h['number']}" for h in HELPLINE_NUMBERS)
            return (
                "Sun liya… ab waqt sakht lag raha hoga.\n"
                "Pehle ek aahista saans bahar… paon zameen pe.\n"
                f"Koi ek insan ya helpline:\n{lines}"
            )
        _ur = {
            "sad":     "Udaasi mehsoos ho rahi hai… shayad andar se kuch der se bhar raha tha.\nKya thoda sa aur batana chahenge?",
            "angry":   "Gussa ana… aksar neeche kuch aur hota hai.\nWoh baat thori si khul ke kehna chahen ge?",
            "anxious": "Bechaini tang kar rahi hai… shayad cheezein andar se build ho rahi thin.\nEk chhoti saans pe focus karna chahen ge?",
            "fear":    "Darr mehsoos ho raha hai… aur kab ka hai yeh sirf aap jante hain.\nMain yahaan hun.",
        }
        return _ur.get(
            emotion,
            "Jo kaha… woh sun liya.\nDil pe jo hai, thora aur khul ke batana chahen ge?"
        )

    if is_crisis:
        helplines = "\n".join(f"- {h['name']}: {h['number']}" for h in HELPLINE_NUMBERS)
        return (
            "That's a lot to be holding right now…\n"
            "One slow breath out — feet on the floor if you can.\n"
            f"These lines are there when you're ready:\n{helplines}\n"
            "Is there one person you could reach — even a short text?"
        )

    _en = {
        "sad":       "Sounds like something's been weighing on you… maybe more than just today.\nWhat part of it feels heaviest right now?",
        "angry":     "That anger… it usually doesn't come from nowhere.\nWant to say what's underneath it, even a little?",
        "anxious":   "Sounds like your mind's been racing… maybe a lot at once.\nWhat feels loudest right now?",
        "fear":      "Fear can feel so isolating when you're sitting with it alone…\nWhat's bringing it on, if you want to say?",
        "happy":     "Something good today — that matters.\nWhat made it feel that way?",
        "surprised": "Sounds unexpected… in a big way?\nWhat's sitting with you after it?",
    }
    return _en.get(
        emotion,
        "Thanks for putting that into words…\nWhat would feel most helpful — talking it through, or just sitting with it for a moment?"
    )
