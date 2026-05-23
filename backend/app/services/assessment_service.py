"""Assessment Service — Sakoon AI Phase 2.

3-session structured clinical assessment:
  Session 1: Patient intake (basic info + initial emotional state)
  Session 2: PHQ-9 (depression) + GAD-7 (anxiety) clinical questionnaires
  Session 3: Behavioral/lifestyle assessment + risk evaluation

After all 3 sessions:  calculate_scores() computes severity levels and
generates a structured clinical summary with personalised recommendations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.services.db_service import (
    complete_assessment,
    create_assessment,
    get_all_answers_for_user,
    get_all_assessments_for_user,
    get_assessment,
    get_assessment_answers,
    get_latest_assessment_for_user,
    get_patient_profile,
    get_assessment_result,
    save_assessment_answer,
    upsert_assessment_result,
    upsert_patient_profile,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Question Banks
# ─────────────────────────────────────────────────────────────────────────────

# Scale shared by PHQ-9 and GAD-7
_FREQ_SCALE = [
    {"value": 0, "label": "Not at all"},
    {"value": 1, "label": "Several days"},
    {"value": 2, "label": "More than half the days"},
    {"value": 3, "label": "Nearly every day"},
]

# Session 1 — Intake questions (open/select, not scored)
SESSION_1_QUESTIONS: List[Dict[str, Any]] = [
    {
        "key": "s1_current_feeling",
        "text": "In a few words, how would you describe how you've been feeling lately?",
        "type": "text",
        "options": None,
        "scored": False,
    },
    {
        "key": "s1_main_concern",
        "text": "What is the main concern that brought you here today?",
        "type": "text",
        "options": None,
        "scored": False,
    },
    {
        "key": "s1_duration",
        "text": "How long have you been experiencing these feelings?",
        "type": "select",
        "options": [
            {"value": 0, "label": "Less than a week"},
            {"value": 1, "label": "1–4 weeks"},
            {"value": 2, "label": "1–3 months"},
            {"value": 3, "label": "More than 3 months"},
        ],
        "scored": False,
    },
    {
        "key": "s1_support",
        "text": "Do you have people in your life you can talk to for support?",
        "type": "select",
        "options": [
            {"value": 2, "label": "Yes, I have strong support"},
            {"value": 1, "label": "Somewhat — limited support"},
            {"value": 0, "label": "No, I feel isolated"},
        ],
        "scored": False,
    },
    {
        "key": "s1_initial_mood",
        "text": "On a scale of 1 to 10, how would you rate your overall mood right now?",
        "type": "scale",
        "options": [{"value": i, "label": str(i)} for i in range(1, 11)],
        "scored": False,
    },
]

# Session 2 — PHQ-9 then GAD-7
SESSION_2_QUESTIONS: List[Dict[str, Any]] = [
    # ── PHQ-9 ─────────────────────────────────────────────────────────────────
    {
        "key": "phq_1",
        "text": "Over the last 2 weeks — Little interest or pleasure in doing things?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
    },
    {
        "key": "phq_2",
        "text": "Over the last 2 weeks — Feeling down, depressed, or hopeless?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
    },
    {
        "key": "phq_3",
        "text": "Over the last 2 weeks — Trouble falling or staying asleep, or sleeping too much?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
    },
    {
        "key": "phq_4",
        "text": "Over the last 2 weeks — Feeling tired or having little energy?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
    },
    {
        "key": "phq_5",
        "text": "Over the last 2 weeks — Poor appetite or overeating?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
    },
    {
        "key": "phq_6",
        "text": "Over the last 2 weeks — Feeling bad about yourself, or that you're a failure?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
    },
    {
        "key": "phq_7",
        "text": "Over the last 2 weeks — Trouble concentrating on things like reading or watching TV?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
    },
    {
        "key": "phq_8",
        "text": "Over the last 2 weeks — Moving or speaking so slowly that others could notice, or being fidgety/restless?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
    },
    {
        "key": "phq_9",
        "text": "Over the last 2 weeks — Thoughts that you would be better off dead, or thoughts of hurting yourself?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "phq9",
        "crisis_flag": True,
    },
    # ── GAD-7 ─────────────────────────────────────────────────────────────────
    {
        "key": "gad_1",
        "text": "Over the last 2 weeks — Feeling nervous, anxious, or on edge?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "gad7",
    },
    {
        "key": "gad_2",
        "text": "Over the last 2 weeks — Not being able to stop or control worrying?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "gad7",
    },
    {
        "key": "gad_3",
        "text": "Over the last 2 weeks — Worrying too much about different things?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "gad7",
    },
    {
        "key": "gad_4",
        "text": "Over the last 2 weeks — Trouble relaxing?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "gad7",
    },
    {
        "key": "gad_5",
        "text": "Over the last 2 weeks — Being so restless that it's hard to sit still?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "gad7",
    },
    {
        "key": "gad_6",
        "text": "Over the last 2 weeks — Becoming easily annoyed or irritable?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "gad7",
    },
    {
        "key": "gad_7",
        "text": "Over the last 2 weeks — Feeling afraid, as if something awful might happen?",
        "type": "select",
        "options": _FREQ_SCALE,
        "scored": True,
        "scale": "gad7",
    },
]

# Session 3 — Behavioral + lifestyle + risk
SESSION_3_QUESTIONS: List[Dict[str, Any]] = [
    {
        "key": "b_sleep",
        "text": "On average, how many hours of sleep do you get per night?",
        "type": "select",
        "options": [
            {"value": 0, "label": "Less than 5 hours"},
            {"value": 1, "label": "5–6 hours"},
            {"value": 2, "label": "7–8 hours (recommended)"},
            {"value": 1, "label": "More than 9 hours"},
        ],
        "scored": False,
    },
    {
        "key": "b_exercise",
        "text": "How often do you engage in physical activity?",
        "type": "select",
        "options": [
            {"value": 0, "label": "Never"},
            {"value": 1, "label": "1–2 times a week"},
            {"value": 2, "label": "3–4 times a week"},
            {"value": 3, "label": "Daily"},
        ],
        "scored": False,
    },
    {
        "key": "b_social",
        "text": "How would you describe your social interactions recently?",
        "type": "select",
        "options": [
            {"value": 0, "label": "I have been mostly isolating"},
            {"value": 1, "label": "Minimal contact with others"},
            {"value": 2, "label": "Moderate — I talk to a few people"},
            {"value": 3, "label": "Active — regular social contact"},
        ],
        "scored": False,
    },
    {
        "key": "b_substance",
        "text": "Have you increased your use of alcohol or other substances recently?",
        "type": "select",
        "options": [
            {"value": 0, "label": "No"},
            {"value": 1, "label": "Slightly"},
            {"value": 2, "label": "Noticeably more than usual"},
        ],
        "scored": False,
        "risk_flag": True,
    },
    {
        "key": "b_self_care",
        "text": "How well are you managing everyday tasks (cooking, hygiene, work/school)?",
        "type": "select",
        "options": [
            {"value": 0, "label": "Struggling significantly"},
            {"value": 1, "label": "Managing with difficulty"},
            {"value": 2, "label": "Mostly okay"},
            {"value": 3, "label": "Managing well"},
        ],
        "scored": False,
    },
    {
        "key": "b_hope",
        "text": "Do you feel hopeful about the future?",
        "type": "select",
        "options": [
            {"value": 0, "label": "Not at all hopeful"},
            {"value": 1, "label": "Slightly hopeful"},
            {"value": 2, "label": "Moderately hopeful"},
            {"value": 3, "label": "Very hopeful"},
        ],
        "scored": False,
        "risk_flag": True,
    },
    {
        "key": "b_coping",
        "text": "What coping strategies do you currently use? (Select the closest option)",
        "type": "select",
        "options": [
            {"value": 0, "label": "None — I don't know what to do"},
            {"value": 1, "label": "Distraction (TV, social media)"},
            {"value": 2, "label": "Talking to someone"},
            {"value": 3, "label": "Exercise, journaling, or meditation"},
        ],
        "scored": False,
    },
]

# Flat index for fast lookup
_ALL_QUESTIONS_BY_KEY: Dict[str, Dict[str, Any]] = {
    q["key"]: q
    for q in SESSION_1_QUESTIONS + SESSION_2_QUESTIONS + SESSION_3_QUESTIONS
}

_SESSION_QUESTIONS = {
    1: SESSION_1_QUESTIONS,
    2: SESSION_2_QUESTIONS,
    3: SESSION_3_QUESTIONS,
}

_SESSION_TYPES = {
    1: "intake",
    2: "clinical",
    3: "behavioral",
}


# ─────────────────────────────────────────────────────────────────────────────
# Scoring helpers
# ─────────────────────────────────────────────────────────────────────────────

def _phq9_severity(score: int) -> str:
    if score <= 4:
        return "none_minimal"
    if score <= 9:
        return "mild"
    if score <= 14:
        return "moderate"
    if score <= 19:
        return "moderately_severe"
    return "severe"


def _gad7_severity(score: int) -> str:
    if score <= 4:
        return "minimal"
    if score <= 9:
        return "mild"
    if score <= 14:
        return "moderate"
    return "severe"


def _overall_risk(phq: int, gad: int, answers: List[Dict[str, Any]]) -> str:
    # PHQ-9 item 9 (suicidal ideation) — any positive answer escalates risk
    crisis_keys = {"phq_9", "b_substance", "b_hope"}
    for a in answers:
        if a["question_key"] == "phq_9" and (a.get("answer_value") or 0) >= 2:
            return "critical"
        if a["question_key"] == "b_hope" and (a.get("answer_value") or 3) == 0:
            # "Not at all hopeful" + moderate-severe depression
            if phq >= 10:
                return "high"
    if phq >= 20 or gad >= 15:
        return "high"
    if phq >= 10 or gad >= 10:
        return "moderate"
    return "low"


def _build_recommendations(phq: int, gad: int, risk: str, answers: List[Dict]) -> str:
    recs: List[str] = []

    if risk in ("critical", "high"):
        recs.append("Immediate professional support is strongly recommended. Please reach out to a mental health professional or crisis helpline.")

    if phq >= 15:
        recs.append("Consider professional evaluation for Major Depressive Disorder. Behavioral activation and structured routines may help.")
    elif phq >= 10:
        recs.append("Mild-to-moderate depression detected. Journaling, daily walks, and social connection exercises are recommended.")
    elif phq >= 5:
        recs.append("Sub-threshold depressive symptoms. Mood tracking and gratitude journaling may provide relief.")

    if gad >= 15:
        recs.append("Severe anxiety detected. Diaphragmatic breathing, progressive muscle relaxation, and professional support are advised.")
    elif gad >= 10:
        recs.append("Moderate anxiety. Practice grounding techniques (5-4-3-2-1) and limit caffeine/screen time before sleep.")
    elif gad >= 5:
        recs.append("Mild anxiety. Regular mindfulness or box-breathing exercises can help regulate the nervous system.")

    # Exercise check
    for a in answers:
        if a["question_key"] == "b_exercise" and (a.get("answer_value") or 0) == 0:
            recs.append("No physical activity reported. Even a 20-minute daily walk significantly improves mood and anxiety levels.")
        if a["question_key"] == "b_sleep" and (a.get("answer_value") or 2) != 2:
            recs.append("Sleep irregularities detected. A consistent sleep schedule and limiting screens before bed can improve sleep quality.")
        if a["question_key"] == "b_social" and (a.get("answer_value") or 3) <= 1:
            recs.append("Social isolation noted. Scheduled, low-pressure social activities are recommended to rebuild connection.")

    if not recs:
        recs.append("Your scores suggest you are coping well. Continue current healthy habits and check in with your mood regularly.")

    return " | ".join(recs)


def _build_summary(
    phq: int, gad: int,
    phq_sev: str, gad_sev: str,
    risk: str,
) -> str:
    sev_map = {
        "none_minimal": "no significant", "mild": "mild",
        "moderate": "moderate", "moderately_severe": "moderately severe",
        "severe": "severe", "minimal": "minimal",
    }
    d_label = sev_map.get(phq_sev, phq_sev)
    a_label = sev_map.get(gad_sev, gad_sev)
    return (
        f"Assessment complete. PHQ-9 score: {phq} ({d_label} depression). "
        f"GAD-7 score: {gad} ({a_label} anxiety). "
        f"Overall risk level: {risk}."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_assessment_status(user_id: int) -> Dict[str, Any]:
    """Return which sessions are done, in progress, or not started for a user."""
    all_assessments = get_all_assessments_for_user(user_id)
    completed_sessions = {
        a["session_number"]
        for a in all_assessments
        if a.get("status") == "completed"
    }
    next_session = None
    for n in (1, 2, 3):
        if n not in completed_sessions:
            next_session = n
            break

    return {
        "completedSessions": sorted(completed_sessions),
        "nextSession": next_session,
        "allComplete": len(completed_sessions) >= 3,
        "resultReady": get_assessment_result(user_id) is not None,
    }


def start_assessment(user_id: int, session_number: int) -> Dict[str, Any]:
    """Create a new assessment session (or return existing in-progress one)."""
    if session_number not in (1, 2, 3):
        raise ValueError(f"session_number must be 1, 2, or 3 — got {session_number}")

    # Enforce ordering: session 2 requires session 1 to be done
    if session_number > 1:
        prev = get_latest_assessment_for_user(user_id, session_number - 1)
        if not prev or prev.get("status") != "completed":
            raise ValueError(
                f"Session {session_number - 1} must be completed before starting session {session_number}."
            )

    # Return in-progress session if one exists
    existing = get_latest_assessment_for_user(user_id, session_number)
    if existing and existing.get("status") == "in_progress":
        answered_keys = {
            a["question_key"]
            for a in get_assessment_answers(existing["id"])
        }
        questions = _SESSION_QUESTIONS[session_number]
        next_q = next((q for q in questions if q["key"] not in answered_keys), None)
        return {
            "assessmentId": existing["id"],
            "sessionNumber": session_number,
            "status": "in_progress",
            "nextQuestion": _format_question(next_q, questions, answered_keys),
            "totalQuestions": len(questions),
            "answeredCount": len(answered_keys),
        }

    assessment_id = create_assessment(
        user_id,
        _SESSION_TYPES[session_number],
        session_number,
    )
    questions = _SESSION_QUESTIONS[session_number]
    first_q = questions[0] if questions else None
    return {
        "assessmentId": assessment_id,
        "sessionNumber": session_number,
        "status": "started",
        "nextQuestion": _format_question(first_q, questions, set()),
        "totalQuestions": len(questions),
        "answeredCount": 0,
    }


def get_next_question(assessment_id: int) -> Dict[str, Any]:
    """Return the next unanswered question for an assessment."""
    assessment = get_assessment(assessment_id)
    if not assessment:
        raise ValueError(f"Assessment {assessment_id} not found.")
    if assessment.get("status") == "completed":
        return {"status": "completed", "nextQuestion": None}

    session_number = assessment["session_number"]
    questions = _SESSION_QUESTIONS[session_number]
    answered_keys = {a["question_key"] for a in get_assessment_answers(assessment_id)}

    next_q = next((q for q in questions if q["key"] not in answered_keys), None)
    return {
        "assessmentId": assessment_id,
        "sessionNumber": session_number,
        "status": "in_progress" if next_q else "completed",
        "nextQuestion": _format_question(next_q, questions, answered_keys),
        "totalQuestions": len(questions),
        "answeredCount": len(answered_keys),
    }


def submit_answer(
    assessment_id: int,
    question_key: str,
    answer_value: Optional[int],
    answer_text: Optional[str],
) -> Dict[str, Any]:
    """Save an answer and return the next question (or completion status)."""
    assessment = get_assessment(assessment_id)
    if not assessment:
        raise ValueError(f"Assessment {assessment_id} not found.")
    if assessment.get("status") == "completed":
        raise ValueError("This assessment session is already completed.")

    session_number = assessment["session_number"]
    questions = _SESSION_QUESTIONS[session_number]

    question_def = _ALL_QUESTIONS_BY_KEY.get(question_key)
    if not question_def:
        raise ValueError(f"Unknown question key: {question_key}")

    # Validate answer_value against options when provided
    if question_def.get("options") and answer_value is not None:
        valid_values = {opt["value"] for opt in question_def["options"]}
        if answer_value not in valid_values:
            raise ValueError(
                f"answer_value {answer_value} is not valid for question {question_key}"
            )

    save_assessment_answer(
        assessment_id,
        question_key,
        question_def["text"],
        answer_value,
        answer_text,
    )

    answered_keys = {a["question_key"] for a in get_assessment_answers(assessment_id)}
    next_q = next((q for q in questions if q["key"] not in answered_keys), None)

    if next_q is None:
        # All questions answered — mark this session complete
        complete_assessment(assessment_id)
        return {
            "assessmentId": assessment_id,
            "sessionNumber": session_number,
            "status": "session_complete",
            "nextQuestion": None,
            "totalQuestions": len(questions),
            "answeredCount": len(answered_keys),
            "message": _session_complete_message(session_number),
        }

    return {
        "assessmentId": assessment_id,
        "sessionNumber": session_number,
        "status": "in_progress",
        "nextQuestion": _format_question(next_q, questions, answered_keys),
        "totalQuestions": len(questions),
        "answeredCount": len(answered_keys),
    }


def calculate_scores(user_id: int) -> Dict[str, Any]:
    """Compute PHQ-9 and GAD-7 scores from all saved answers and persist result."""
    all_answers = get_all_answers_for_user(user_id)
    if not all_answers:
        raise ValueError("No assessment answers found for this user.")

    phq_keys = {f"phq_{i}" for i in range(1, 10)}
    gad_keys = {f"gad_{i}" for i in range(1, 8)}

    phq_score = sum(
        int(a.get("answer_value") or 0)
        for a in all_answers
        if a["question_key"] in phq_keys
    )
    gad_score = sum(
        int(a.get("answer_value") or 0)
        for a in all_answers
        if a["question_key"] in gad_keys
    )

    phq_sev = _phq9_severity(phq_score)
    gad_sev = _gad7_severity(gad_score)
    risk = _overall_risk(phq_score, gad_score, all_answers)
    summary = _build_summary(phq_score, gad_score, phq_sev, gad_sev, risk)
    recommendations = _build_recommendations(phq_score, gad_score, risk, all_answers)

    result: Dict[str, Any] = {
        "depression_score": phq_score,
        "anxiety_score": gad_score,
        "depression_severity": phq_sev,
        "anxiety_severity": gad_sev,
        "risk_level": risk,
        "summary": summary,
        "recommendations": recommendations,
    }
    upsert_assessment_result(user_id, result)
    logger.info(
        "assessment_service.calculate_scores user=%d phq=%d gad=%d risk=%s",
        user_id, phq_score, gad_score, risk,
    )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _format_question(
    q: Optional[Dict[str, Any]],
    all_questions: List[Dict[str, Any]],
    answered_keys: set,
) -> Optional[Dict[str, Any]]:
    if q is None:
        return None
    idx = next((i for i, x in enumerate(all_questions) if x["key"] == q["key"]), 0)
    return {
        "key": q["key"],
        "text": q["text"],
        "type": q["type"],
        "options": q.get("options"),
        "questionNumber": idx + 1,
        "totalInSession": len(all_questions),
        "isCrisisFlag": q.get("crisis_flag", False),
    }


def _session_complete_message(session_number: int) -> str:
    messages = {
        1: "Thank you for sharing. We'll now move to a brief clinical check-in.",
        2: "Great job — clinical questionnaire complete. One more session to go.",
        3: "Assessment complete. Your personalised summary is ready.",
    }
    return messages.get(session_number, "Session complete.")
