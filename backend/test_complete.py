"""
Sakoon AI — complete pytest integration suite (52 tests).

Run:
  cd backend
  pip install pytest pytest-order httpx python-dotenv
  python -m uvicorn app.main:app --reload --port 8000
  pytest test_complete.py -v --tb=short

Markers:
  pytest -m smoke
  pytest -m critical
"""

from __future__ import annotations

import pytest

from qa_helpers import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    CRISIS_KEYWORD_SAMPLE,
    DEFAULT_TEST_PASSWORD,
    SakoonTestState,
    apply_auth_from_response,
    complete_assessment_session,
    register_payload,
)

pytestmark = [pytest.mark.regression]


# ---------------------------------------------------------------------------
# TestAuth (01-08)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.critical
class TestAuth:
  """User registration, login (email + password), JWT, and session bootstrap."""

  def test_01_register_new_user_success(self, client, state: SakoonTestState):
    """POST /auth/register returns JWT and user with id."""
    r = client.post(
      "/api/v1/auth/register",
      json=register_payload(state.user_name, state.email, state.password),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("accessToken")
    assert body.get("tokenType") == "bearer"
    assert "user" in body
    assert body["user"]["id"] > 0
    assert body["user"]["name"] == state.user_name
    assert body["user"].get("email") == state.email
    apply_auth_from_response(state, body)

  def test_02_register_duplicate_email(self, client, state: SakoonTestState):
    """Duplicate email returns 409."""
    dup_name = f"dup_user_{state_suffix()}"
    payload = register_payload(dup_name, state.duplicate_email, state.password)
    r1 = client.post("/api/v1/auth/register", json=payload)
    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 409
    assert "email" in r2.json().get("detail", "").lower()

  def test_03_register_missing_fields(self, client):
    """Missing email/password returns 422."""
    r = client.post(
      "/api/v1/auth/register",
      json={"name": "only_name", "languagePreference": "en"},
    )
    assert r.status_code == 422
    assert r.json().get("detail") is not None

  def test_04_register_with_language_preference(self, client):
    """languagePreference ur is persisted on the user record."""
    suffix = state_suffix()
    r = client.post(
      "/api/v1/auth/register",
      json=register_payload(
        f"ur_user_{suffix}",
        f"ur_{suffix}@example.com",
        DEFAULT_TEST_PASSWORD,
        "ur",
      ),
    )
    assert r.status_code == 200
    assert r.json()["user"]["languagePreference"] == "ur"

  def test_05_login_existing_user(self, client, state: SakoonTestState):
    """POST /auth/login returns same user id and a new JWT."""
    assert state.user_id is not None
    r = client.post(
      "/api/v1/auth/login",
      json={"email": state.email, "password": state.password},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["id"] == state.user_id
    assert body.get("accessToken")
    apply_auth_from_response(state, body)

  def test_06_login_invalid_credentials(self, client):
    """Wrong email/password returns 401."""
    r = client.post(
      "/api/v1/auth/login",
      json={"email": "nobody@example.com", "password": "WrongPass99!"},
    )
    assert r.status_code == 401
    assert "invalid" in r.json().get("detail", "").lower()

  def test_07_login_empty_body(self, client):
    """Login without email/password returns 422."""
    r = client.post("/api/v1/auth/login", json={})
    assert r.status_code == 422

  def test_08_get_session_valid_user(self, client, state: SakoonTestState):
    """GET /auth/session (JWT) returns active session and ids."""
    assert state.user_id is not None
    assert state.access_token
    r = client.get("/api/v1/auth/session")
    assert r.status_code == 200
    data = r.json()
    assert data.get("session") is not None
    assert data["session"]["userId"] == state.user_id
    assert data["session"]["id"] > 0
    state.session_id = data["session"]["id"]


def state_suffix() -> str:
    import uuid
    return uuid.uuid4().hex[:8]


# ---------------------------------------------------------------------------
# TestChat (09-14)
# ---------------------------------------------------------------------------


@pytest.mark.critical
class TestChat:
  """Chat pipeline, classification, crisis detection, journal."""

  def test_09_send_chat_message_success(self, client, state: SakoonTestState):
    """POST /chat/message returns aiResponse string."""
    assert state.user_id and state.session_id
    r = client.post(
      "/api/v1/chat/message",
      json={
        "userId": state.user_id,
        "sessionId": state.session_id,
        "message": "I feel stressed about my exams.",
      },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body.get("aiResponse"), str)
    assert len(body["aiResponse"].strip()) > 0

  def test_10_chat_has_classification(self, client, state: SakoonTestState):
    """Response includes mhClassification and numeric mhConfidence."""
    r = client.post(
      "/api/v1/chat/message",
      json={
        "userId": state.user_id,
        "sessionId": state.session_id,
        "message": "I cannot sleep and feel anxious.",
      },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("mhClassification") is not None
    assert isinstance(body.get("mhConfidence"), (int, float))

  def test_11_chat_has_emotion(self, client, state: SakoonTestState):
    """Response includes emotionLabel from HF/heuristic pipeline."""
    r = client.post(
      "/api/v1/chat/message",
      json={
        "userId": state.user_id,
        "sessionId": state.session_id,
        "message": "I am sad and hopeless today.",
      },
    )
    assert r.status_code == 200
    assert r.json().get("emotionLabel") is not None

  def test_12_chat_crisis_keyword(self, client, state: SakoonTestState):
    """Crisis keywords set isCrisis=true and return helplineNumbers."""
    r = client.post(
      "/api/v1/chat/message",
      json={
        "userId": state.user_id,
        "sessionId": state.session_id,
        "message": CRISIS_KEYWORD_SAMPLE,
      },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("isCrisis") is True
    assert body.get("riskLevel") in ("high", "medium")
    helplines = body.get("helplineNumbers") or []
    assert len(helplines) >= 1
    assert "number" in helplines[0]

  def test_13_chat_missing_userId(self, client, state: SakoonTestState):
    """Omitting userId returns 422 validation error."""
    r = client.post(
      "/api/v1/chat/message",
      json={"sessionId": state.session_id, "message": "hello"},
    )
    assert r.status_code == 422

  def test_14_journal_reflection(self, client):
    """POST /chat/journal-reflection returns non-empty reflection."""
    r = client.post(
      "/api/v1/chat/journal-reflection",
      json={"text": "Today I took a short walk after class.", "language": "en"},
    )
    assert r.status_code == 200
    ref = r.json().get("reflection", "")
    assert isinstance(ref, str)
    assert len(ref.strip()) > 0


# ---------------------------------------------------------------------------
# TestSession (15-16)
# ---------------------------------------------------------------------------


class TestSession:
  """Session chat history."""

  def test_15_get_session_history(self, client, state: SakoonTestState):
    """GET /session/{id}/history returns messages array with user/assistant roles."""
    assert state.session_id
    r = client.get(f"/api/v1/session/{state.session_id}/history")
    assert r.status_code == 200
    msgs = r.json().get("messages", [])
    assert isinstance(msgs, list)
    assert len(msgs) >= 2
    roles = {m["role"] for m in msgs}
    assert "user" in roles and "assistant" in roles

  def test_16_get_invalid_session(self, client, state: SakoonTestState):
    """Unknown session id returns 403 (not owned by user)."""
    assert state.access_token
    r = client.get("/api/v1/session/999999/history")
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# TestUser (17-20)
# ---------------------------------------------------------------------------


class TestUser:
  """User mood summary, recommendations, feedback."""

  def test_17_mood_summary_valid_user(self, client, state: SakoonTestState):
    """GET mood-summary returns summary list and trend string."""
    r = client.get(f"/api/v1/user/{state.user_id}/mood-summary")
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    assert "trend" in data
    assert isinstance(data["summary"], list)

  def test_18_mood_summary_wrong_user(self, client, state: SakoonTestState):
    """Another user's id returns 403."""
    assert state.access_token
    r = client.get("/api/v1/user/999999/mood-summary")
    assert r.status_code == 403

  def test_19_get_recommendations(self, client, state: SakoonTestState):
    """GET recommendations returns array (may include exercises from chat)."""
    r = client.get(f"/api/v1/user/{state.user_id}/recommendations")
    assert r.status_code == 200
    recs = r.json().get("recommendations", [])
    assert isinstance(recs, list)
    if recs:
      state.assignment_id = recs[0].get("assignmentId")

  def test_20_exercise_feedback_no_assignment(self, client, state: SakoonTestState):
    """Invalid assignmentId returns 404."""
    r = client.post(
      f"/api/v1/user/{state.user_id}/exercise-feedback",
      json={"assignmentId": 999999, "helped": True},
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# TestMood (21-28)
# ---------------------------------------------------------------------------


class TestMood:
  """Mood and behavior logging."""

  def test_21_log_mood_score_1(self, client, state: SakoonTestState):
    """mood_score=1 is accepted."""
    r = client.post(
      "/api/v1/mood/log",
      json={"user_id": state.user_id, "mood_score": 1, "note": "Very low"},
    )
    assert r.status_code == 200
    assert r.json().get("ok") is True
    assert r.json().get("id", 0) > 0

  def test_22_log_mood_score_5(self, client, state: SakoonTestState):
    """mood_score=5 is accepted."""
    r = client.post(
      "/api/v1/mood/log",
      json={"user_id": state.user_id, "mood_score": 5},
    )
    assert r.status_code == 200

  def test_23_log_mood_score_invalid_6(self, client, state: SakoonTestState):
    """mood_score=6 returns 422."""
    r = client.post(
      "/api/v1/mood/log",
      json={"user_id": state.user_id, "mood_score": 6},
    )
    assert r.status_code == 422

  def test_24_log_mood_score_0(self, client, state: SakoonTestState):
    """mood_score=0 returns 422."""
    r = client.post(
      "/api/v1/mood/log",
      json={"user_id": state.user_id, "mood_score": 0},
    )
    assert r.status_code == 422

  def test_25_get_mood_history(self, client, state: SakoonTestState):
    """GET mood history returns entries with moodScore."""
    r = client.get(f"/api/v1/mood/history/{state.user_id}")
    assert r.status_code == 200
    entries = r.json().get("entries", [])
    assert len(entries) >= 2
    assert "moodScore" in entries[0]

  def test_26_log_behavior_all_fields(self, client, state: SakoonTestState):
    """Full behavior payload is accepted."""
    r = client.post(
      "/api/v1/mood/behavior",
      json={
        "user_id": state.user_id,
        "sleep_hours": 7.0,
        "physical_activity": "moderate",
        "social_interaction": "active",
        "notes": "Good day",
      },
    )
    assert r.status_code == 200
    assert r.json().get("ok") is True

  def test_27_log_behavior_partial_fields(self, client, state: SakoonTestState):
    """Only user_id is required; optional fields may be omitted."""
    r = client.post(
      "/api/v1/mood/behavior",
      json={"user_id": state.user_id, "sleep_hours": 6.5},
    )
    assert r.status_code == 200

  def test_28_get_behavior_history(self, client, state: SakoonTestState):
    """GET behavior history returns entries array."""
    r = client.get(f"/api/v1/mood/behavior/{state.user_id}")
    assert r.status_code == 200
    assert isinstance(r.json().get("entries"), list)
    assert len(r.json()["entries"]) >= 1


# ---------------------------------------------------------------------------
# TestAssessment (29-38)
# ---------------------------------------------------------------------------


@pytest.mark.critical
class TestAssessment:
  """Three-session clinical assessment flow."""

  def test_29_create_profile(self, client, state: SakoonTestState):
    """POST assessment/profile saves intake data."""
    r = client.post(
      "/api/v1/assessment/profile",
      json={
        "user_id": state.user_id,
        "age": 21,
        "gender": "other",
        "sleep_pattern": "irregular",
        "past_therapy": False,
      },
    )
    assert r.status_code == 200
    assert r.json().get("ok") is True

  def test_30_get_profile(self, client, state: SakoonTestState):
    """GET profile returns saved fields."""
    r = client.get(f"/api/v1/assessment/profile/{state.user_id}")
    assert r.status_code == 200
    profile = r.json().get("profile")
    assert profile is not None
    assert profile.get("user_id") == state.user_id
    assert profile.get("age") == 21

  def test_31_get_status_before_assessment(self, client, state: SakoonTestState):
    """Fresh user may have empty completedSessions before tests 35-37."""
    r = client.get(f"/api/v1/assessment/status/{state.user_id}")
    assert r.status_code == 200
    data = r.json()
    assert "completedSessions" in data
    assert "allComplete" in data

  def test_32_start_session_1(self, client, state: SakoonTestState):
    """POST start session 1 returns assessmentId and first question."""
    r = client.post(
      "/api/v1/assessment/start",
      json={"user_id": state.user_id, "session_number": 1},
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("assessmentId", 0) > 0
    assert data.get("nextQuestion") is not None
    assert data["nextQuestion"].get("key", "").startswith("s1_")
    state.assessment_id = data["assessmentId"]

  def test_33_get_next_question(self, client, state: SakoonTestState):
    """GET next returns question with key and text."""
    assert state.assessment_id
    r = client.get(f"/api/v1/assessment/next/{state.assessment_id}")
    assert r.status_code == 200
    assert r.json().get("nextQuestion") is not None

  def test_34_answer_question(self, client, state: SakoonTestState):
    """POST answer accepts answer_text for s1_current_feeling."""
    assert state.assessment_id
    r = client.post(
      "/api/v1/assessment/answer",
      json={
        "assessment_id": state.assessment_id,
        "question_key": "s1_current_feeling",
        "answer_text": "Tired and worried.",
      },
    )
    assert r.status_code == 200

  def test_35_complete_session_1_all_answers(self, client, state: SakoonTestState):
    """Finish all session 1 questions until completed."""
    from qa_helpers import auth_headers

    aid, ok = complete_assessment_session(
      client, state.user_id, 1, headers=auth_headers(state)
    )
    assert ok, "Session 1 did not complete"
    state.assessment_id = aid

  def test_36_complete_session_2(self, client, state: SakoonTestState):
    """Complete PHQ-9 + GAD-7 session."""
    from qa_helpers import auth_headers

    aid, ok = complete_assessment_session(
      client, state.user_id, 2, headers=auth_headers(state)
    )
    assert ok, "Session 2 did not complete"
    state.assessment_id = aid

  def test_37_complete_session_3(self, client, state: SakoonTestState):
    """Complete behavioral session."""
    from qa_helpers import auth_headers

    aid, ok = complete_assessment_session(
      client, state.user_id, 3, headers=auth_headers(state)
    )
    assert ok, "Session 3 did not complete"
    state.assessment_id = aid

  def test_38_get_final_result(self, client, state: SakoonTestState):
    """POST scores then GET result with depression/anxiety scores."""
    calc = client.post(f"/api/v1/assessment/scores/{state.user_id}")
    assert calc.status_code == 200
    calc_body = calc.json()
    assert "depression_score" in calc_body or "depressionScore" in calc_body

    r = client.get(f"/api/v1/assessment/result/{state.user_id}")
    assert r.status_code == 200
    result = r.json()
    assert result.get("depressionScore") is not None
    assert result.get("anxietyScore") is not None
    assert result.get("riskLevel") is not None
    assert result.get("depressionSeverity")
    assert result.get("summary")


# ---------------------------------------------------------------------------
# TestTTS (39-41)
# ---------------------------------------------------------------------------


class TestTTS:
  """Text-to-speech endpoints."""

  def test_39_tts_speak_english(self, client):
    """POST /tts/speak returns audio/mpeg when Edge-TTS is available."""
    r = client.post(
      "/api/v1/tts/speak",
      json={"text": "Hello from Sakoon automated test.", "language": "en"},
    )
    assert r.status_code in (200, 503)
    if r.status_code == 200:
      assert "audio" in r.headers.get("content-type", "")
      assert len(r.content) > 100

  def test_40_tts_speak_empty_text(self, client):
    """Empty text yields 503 JSON (no audio generated)."""
    r = client.post("/api/v1/tts/speak", json={"text": ""})
    assert r.status_code in (422, 400, 503)

  def test_41_tts_speak_urdu(self, client):
    """Urdu TTS may succeed or 503 if voice/network unavailable."""
    r = client.post(
      "/api/v1/tts/speak",
      json={"text": "Assalam o alaikum, main theek hun.", "language": "ur"},
    )
    assert r.status_code in (200, 503)


# ---------------------------------------------------------------------------
# TestAvatar (42-44)
# ---------------------------------------------------------------------------


class TestAvatar:
  """Avatar pipeline status and speak."""

  def test_42_avatar_status(self, client):
    """GET /avatar/status returns wav2lip readiness flags."""
    r = client.get("/api/v1/avatar/status")
    assert r.status_code == 200
    data = r.json()
    assert "wav2lipReady" in data
    assert "faceImageExists" in data

  def test_43_avatar_speak(self, client):
    """POST /avatar/speak returns video or audio bytes."""
    r = client.post(
      "/api/v1/avatar/speak",
      json={"text": "Hello.", "language": "en"},
    )
    assert r.status_code in (200, 503)
    if r.status_code == 200:
      assert r.headers.get("x-avatar-mode") in ("video", "audio", None)
      assert len(r.content) > 0

  def test_44_avatar_speak_no_text(self, client):
    """Blank text returns 422."""
    r = client.post("/api/v1/avatar/speak", json={"text": "   "})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# TestAdmin (45-52)
# ---------------------------------------------------------------------------


@pytest.mark.critical
class TestAdmin:
  """Admin authentication and protected routes."""

  def test_45_admin_login_valid(self, client, state: SakoonTestState):
    """Valid admin credentials return adminKey."""
    r = client.post(
      "/api/v1/admin/login",
      json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert r.status_code == 200
    assert r.json().get("adminKey")
    state.admin_key = r.json()["adminKey"]

  def test_46_admin_login_wrong_password(self, client):
    """Wrong password returns 401."""
    r = client.post(
      "/api/v1/admin/login",
      json={"username": ADMIN_USERNAME, "password": "wrong-password-xyz"},
    )
    assert r.status_code == 401

  def test_47_admin_login_wrong_username(self, client):
    """Wrong username returns 401."""
    r = client.post(
      "/api/v1/admin/login",
      json={"username": "not_admin", "password": ADMIN_PASSWORD},
    )
    assert r.status_code == 401

  def test_48_get_stats_with_key(self, client, state: SakoonTestState):
    """GET /admin/stats with X-Admin-Key returns counts."""
    assert state.admin_key
    r = client.get(
      "/api/v1/admin/stats",
      headers={"X-Admin-Key": state.admin_key},
    )
    assert r.status_code == 200
    data = r.json()
    assert "totalSessions" in data
    assert "crisisCount" in data
    assert isinstance(data["totalSessions"], int)

  def test_49_get_stats_no_key(self, client):
    """Missing admin key returns 401."""
    r = client.get("/api/v1/admin/stats")
    assert r.status_code == 401

  def test_50_get_sessions_list(self, client, state: SakoonTestState):
    """GET /admin/sessions returns sessions array."""
    r = client.get(
      "/api/v1/admin/sessions",
      headers={"X-Admin-Key": state.admin_key},
    )
    assert r.status_code == 200
    assert isinstance(r.json().get("sessions"), list)

  def test_51_get_session_logs(self, client, state: SakoonTestState):
    """GET session logs for the test session."""
    assert state.session_id
    r = client.get(
      f"/api/v1/admin/sessions/{state.session_id}/logs",
      headers={"X-Admin-Key": state.admin_key},
    )
    assert r.status_code == 200
    assert isinstance(r.json().get("messages"), list)

  def test_52_get_crisis_alerts(self, client, state: SakoonTestState):
    """GET crisis-alerts returns alerts list (may include crisis from test_12)."""
    r = client.get(
      "/api/v1/admin/crisis-alerts",
      headers={"X-Admin-Key": state.admin_key},
    )
    assert r.status_code == 200
    assert isinstance(r.json().get("alerts"), list)
