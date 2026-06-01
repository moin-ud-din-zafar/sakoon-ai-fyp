"""Chat route: send message, full AI pipeline (HuggingFace + OpenRouter)."""

import logging
import random
import re

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_classifier, get_current_user, require_session_access, require_user_id
from app.services.classifier_service import MentalHealthClassifier
from app.services.risk_detector_service import RiskDetector
from app.services.llm_service import (
    generate_response,
    format_conversation_memory,
    generate_personalized_exercise,
    generate_journal_reflection,
)
from app.services.emotion_service import detect_emotion
from app.services.sentiment_service import detect_sentiment
from app.utils.translator import normalize_input
from app.utils.language_detector import detect_language
from app.services.personalization_service import (
    choose_library_exercise,
    compute_trend,
    exercise_to_api_payload,
    merge_llm_exercise,
)
from app.services.db_service import (
    create_chat_log,
    add_emotion_history,
    get_user,
    get_recent_session_turns,
    get_mood_summary,
    get_recent_assignment_types,
    get_recent_assignment_titles,
    save_exercise_assignment,
)
from app.core.constants import HELPLINE_NUMBERS

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    userId: int
    sessionId: int
    message: str


class JournalReflectRequest(BaseModel):
    """Optional reflection on coping journal text — same OpenRouter stack."""

    text: str
    language: str = "en"


# Roman Urdu / Urdu fragments — Latin script Pakistani chat
_URDU_INDICATORS = (
    "meri", "mera", "meray", "tum", "tumhari", "aap", "aapko", "hai", "hain", "ho", "hon",
    "kya", "kyun", "kab", "kahan", "kisi", "karun", "karo", "karna", "tabiyat",
    "dil", "dill", "bahut", "bohat", "thora", "thori", "theek", "tik", "nahi", "na",
    "mein", "main", "mai", "ab", "aaj", "aj", "kal", "phir", "par", "pe", "ko", "se",
    "kharab", "achha", "acha", "zyada", "zada", "munaasib", "khair", "sun", "suno",
    "dard", "beta", "yar", "yaar", "bhai", "jan", "jumlon", "alfaz", "izzat", "dost",
    "matlab", "sab", "kaam", "kaun", "kaisi", "kaise", "kis", "jab", "jo", "wo", "waisa",
    "bilkul", "shukriya", "mashallah", "insha", "allah", "dua", "bas", "sirf", "bhi",
    "mujhe", "mujhko", "hum", "hamari", "unka", "usi", "yahan", "wahan", "acha laga",
)

# Short English-only phrases — do not force Urdu reply for these
_ENGLISH_ONLY_PHRASES = (
    "how are you",
    "how's it going",
    "how is it going",
    "what's up",
    "whats up",
    "thank you",
    "thanks",
    "hello",
    "hi there",
    "hey there",
    "good morning",
    "good night",
    "good afternoon",
    "see you",
    "bye",
    "okay",
    "ok ",
    "yes",
    "no",
)


def _urdu_token_hit(text: str, word: str) -> bool:
    """Avoid English false positives (e.g. 'ho' in 'how', 'par' in 'prepare')."""
    t = text.lower()
    w = word.lower()
    if len(w) <= 3:
        return re.search(rf"(?<![a-z0-9]){re.escape(w)}(?![a-z0-9])", t) is not None
    return w in t


def _detect_language_from_message(msg: str) -> str | None:
    """If message looks like Roman Urdu, return 'ur'. Else None."""
    t = (msg or "").lower().strip()
    if len(t) < 2:
        return None
    hits = sum(1 for w in _URDU_INDICATORS if _urdu_token_hit(t, w))
    plain_en = any(p in t for p in _ENGLISH_ONLY_PHRASES) and hits == 0
    if plain_en and len(t) < 80:
        return None
    if hits >= 2:
        return "ur"
    if hits >= 1 and len(t) >= 3:
        return "ur"
    return None


def _normalize_reply_language(lang_pref: str) -> str:
    p = (lang_pref or "en").lower().strip()[:2]
    return p if p in ("ur", "hi", "ps", "sd", "sk") else "en"


def _detect_emotion(text: str, mh_class: str) -> str:
    """Simple emotion refinement from text + MH class."""
    t = text.lower()
    if "sad" in t or "hopeless" in t or mh_class == "Depression":
        return "sad"
    if "anxious" in t or "worried" in t or "nervous" in t or mh_class == "Anxiety":
        return "anxious"
    if "angry" in t or "angry" in t or "frustrated" in t:
        return "angry"
    if "stress" in t or "overwhelmed" in t or mh_class == "Stress":
        return "stressed"
    if mh_class == "Suicidal":
        return "distressed"
    return mh_class.lower()


@router.post("/message")
def send_message(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user),
    classifier: MentalHealthClassifier = Depends(get_classifier),
):
    """
    Process user message: classify, risk check, LLM response, store.
  Requires Authorization: Bearer <JWT>. userId in body must match token.
    """
    require_user_id(current_user, req.userId)
    require_session_access(req.sessionId, current_user["id"])
    user_id = int(current_user["id"])

    if not req.message or not req.message.strip():
        u0 = get_user(user_id)
        lp = (u0.get("language_preference") or "en") if u0 else "en"
        if str(lp).lower().strip()[:2] == "ur":
            empty_reply = (
                "…jab dil kare, apni marzi se likhna. Yahan jaldi nahi."
            )
            empty_lang = "ur"
        else:
            empty_reply = "No rush… when a thought's ready, you can share it."
            empty_lang = "en"
        return {
            "aiResponse": empty_reply,
            "replyLanguage": empty_lang,
            "mhClassification": "Normal",
            "mhConfidence": 0.0,
            "emotionLabel": "neutral",
            "riskLevel": "low",
            "isCrisis": False,
            "helplineNumbers": [],
            "recommendations": [],
            "suggestedExercise": None,
            "chatLogId": None,
        }

    detector = RiskDetector()
    mh_class, confidence = classifier.predict(req.message)
    risk_result = detector.check(req.message, mh_class, confidence)
    is_crisis = risk_result["is_crisis"]
    risk_level = risk_result["risk_level"]

    user = get_user(user_id)
    lang_pref = (user.get("language_preference") or "en") if user else "en"
    language = _normalize_reply_language(lang_pref)
    if _normalize_reply_language(lang_pref) == "en":
        detected = _detect_language_from_message(req.message)
        if detected:
            language = detected

    # ── HuggingFace Pipeline ─────────────────────────────────────────────
    # Normalise to English for HF models (translate if Urdu)
    try:
        normalized_text = normalize_input(req.message)
    except Exception:
        normalized_text = req.message

    hf_emotion_result = {"emotion": "neutral", "confidence": 0.0}
    hf_sentiment_result = {"sentiment": "neutral", "confidence": 0.0}
    try:
        hf_emotion_result = detect_emotion(normalized_text)
    except Exception as e:
        logger.warning("HF emotion detection failed: %s", e)
    try:
        hf_sentiment_result = detect_sentiment(normalized_text)
    except Exception as e:
        logger.warning("HF sentiment detection failed: %s", e)

    # Merge HF emotion with local MH classifier for richer emotion label
    emotion = hf_emotion_result.get("emotion") or _detect_emotion(req.message, mh_class)

    recent_turns = get_recent_session_turns(req.sessionId, limit=5)  # noqa: session verified
    memory_text = format_conversation_memory(recent_turns)

    ai_response = generate_response(
        user_message=req.message,
        mh_classification=mh_class,
        emotion_label=emotion,
        risk_level=risk_level,
        is_crisis=is_crisis,
        language=language,
        conversation_memory=memory_text or None,
        hf_emotion=hf_emotion_result.get("emotion"),
        hf_sentiment=hf_sentiment_result.get("sentiment"),
    )

    suggested_exercise = None
    recs_compact: list = []

    if not is_crisis:
        mood_summary = get_mood_summary(user_id)
        trend = compute_trend(mood_summary)
        recent_types = get_recent_assignment_types(user_id, limit=8)
        recent_titles = get_recent_assignment_titles(user_id, limit=6)

        use_llm = (
            mh_class not in ("Normal", "Suicidal")
            and len(req.message.strip()) > 8
            and random.random() < 0.42
        )
        internal = None
        source = "library"
        if use_llm:
            raw_ex = generate_personalized_exercise(
                user_message=req.message,
                mh_classification=mh_class,
                emotion_label=emotion,
                memory_snippet=memory_text or "",
                language=language,
            )
            if raw_ex:
                try:
                    internal = merge_llm_exercise(raw_ex)
                    internal["source"] = "llm"
                    source = "llm"
                except Exception:
                    internal = None
        if internal is None:
            internal = choose_library_exercise(
                mh_class,
                recent_types=recent_types,
                recent_titles=recent_titles,
                mood_trend=trend,
            )
            internal["source"] = "library"

        aid = save_exercise_assignment(user_id, internal)
        prefer_urdu = language in ("ur", "urdu")
        suggested_exercise = exercise_to_api_payload(
            internal, source, assignment_id=aid, prefer_urdu=prefer_urdu
        )
        recs_compact = [
            {
                "type": suggested_exercise.get("type"),
                "title": suggested_exercise.get("title"),
                "content": suggested_exercise.get("description") or "",
            }
        ]

    chat_log_id = create_chat_log(
        session_id=req.sessionId,
        user_message=req.message,
        ai_response=ai_response,
        mh_classification=mh_class,
        mh_confidence=confidence,
        emotion_label=emotion,
        risk_level=risk_level,
        is_crisis=1 if is_crisis else 0,
    )
    add_emotion_history(req.sessionId, mh_class, confidence)

    return {
        "aiResponse": ai_response,
        "replyLanguage": language,
        "mhClassification": mh_class,
        "mhConfidence": confidence,
        # HuggingFace pipeline results
        "emotionLabel": emotion,
        "emotionConfidence": hf_emotion_result.get("confidence", 0.0),
        "sentiment": hf_sentiment_result.get("sentiment", "neutral"),
        "sentimentConfidence": hf_sentiment_result.get("confidence", 0.0),
        # Risk
        "riskLevel": risk_level,
        "isCrisis": is_crisis,
        "helplineNumbers": HELPLINE_NUMBERS if is_crisis else [],
        "recommendations": recs_compact,
        "suggestedExercise": suggested_exercise,
        "chatLogId": chat_log_id,
    }


@router.post("/journal-reflection")
def journal_reflection(
    req: JournalReflectRequest,
    current_user: dict = Depends(get_current_user),
):
    """Gentle 2–3 line reflection on coping journal entry (Roman Urdu / English)."""
    text = (req.text or "").strip()
    if not text:
        return {"reflection": ""}
    ref = generate_journal_reflection(text, language=req.language or "en")
    return {"reflection": ref}
