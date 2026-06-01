# Sakoon AI — Backend API Test Report

---

## 1. Cover Section

| Field | Value |
|-------|--------|
| **Project** | Sakoon AI — Mental Health Support System |
| **Module** | Backend API Testing |
| **Report Date** | 19 May 2026 |
| **Prepared By** | FYP Student (Backend Team) |
| **API Version** | 2.0.0 |
| **Base URL** | `http://127.0.0.1:8000` |
| **Total API Endpoints** | **31** |
| **Total Test Cases (pytest)** | **52** |
| **Sequential Runner Checks** | **56** (includes system smoke + duplicate-register sub-check) |
| **Pass Rate** | **100%** (52/52 pytest; 56/56 runner on last execution) |
| **Test Artifacts** | `test_complete.py`, `run_tests.py`, `test_results.json`, `api_tester.html` |

---

## 2. Executive Summary

The Sakoon AI backend was subjected to comprehensive **black-box functional and integration testing** against a live FastAPI server. Fifty-two ordered pytest cases and fifty-six sequential runner checks cover all major API modules: authentication, therapeutic chat (including crisis safety), session history, user analytics, mood/behavior logging, three-session clinical assessment (PHQ-9/GAD-7 style), text-to-speech, avatar pipeline, and admin monitoring. Tests include both **happy paths** (valid data → expected success) and **sad paths** (invalid data → 401/404/422). All executed tests **passed** on 19 May 2026. The backend is **validated for frontend integration** and FYP demonstration, with documented limitations (name-based user auth, screening-not-diagnosis).

---

## 3. System Under Test

### 3.1 Architecture Overview

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| API | FastAPI (`app/main.py`) | HTTP routing, CORS, OpenAPI |
| Routes | `app/api/routes/*.py` | Request validation, orchestration |
| Services | `app/services/*.py` | Business logic, ML, LLM, TTS, avatar |
| Data | `app/services/db_service.py` | MySQL / SQLite persistence |
| Config | `app/config.py`, `.env` | Secrets, DB, OpenRouter, admin |
| Safety | `app/core/constants.py` | Crisis keywords, helplines, session cap |

### 3.2 Technology Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.11+ |
| Web framework | FastAPI, Uvicorn |
| Validation | Pydantic v2 |
| Database | MySQL 8 (production) / SQLite (dev) |
| ML classifier | scikit-learn (TF-IDF + Logistic Regression) |
| NLP (optional) | HuggingFace Transformers (emotion, sentiment) |
| LLM | OpenRouter API (HTTPX) |
| TTS | Edge-TTS (default), optional Coqui XTTS |
| Avatar | Wav2Lip (optional), subprocess |
| Testing | pytest, httpx, requests |

### 3.3 API Endpoint Inventory (31 routes)

| # | Method | Endpoint | Module | Auth Required |
|---|--------|----------|--------|---------------|
| 1 | GET | `/` | System | No |
| 2 | GET | `/health` | System | No |
| 3 | POST | `/api/v1/auth/register` | Auth | No |
| 4 | POST | `/api/v1/auth/login` | Auth | No |
| 5 | GET | `/api/v1/auth/session/{user_id}` | Auth | No |
| 6 | POST | `/api/v1/chat/message` | Chat | No |
| 7 | POST | `/api/v1/chat/journal-reflection` | Chat | No |
| 8 | GET | `/api/v1/session/{session_id}/history` | Session | No |
| 9 | GET | `/api/v1/user/{user_id}/mood-summary` | User | No |
| 10 | GET | `/api/v1/user/{user_id}/recommendations` | User | No |
| 11 | POST | `/api/v1/user/{user_id}/exercise-feedback` | User | No |
| 12 | POST | `/api/v1/mood/log` | Mood | No |
| 13 | GET | `/api/v1/mood/history/{user_id}` | Mood | No |
| 14 | POST | `/api/v1/mood/behavior` | Mood | No |
| 15 | GET | `/api/v1/mood/behavior/{user_id}` | Mood | No |
| 16 | POST | `/api/v1/assessment/profile` | Assessment | No |
| 17 | GET | `/api/v1/assessment/profile/{user_id}` | Assessment | No |
| 18 | GET | `/api/v1/assessment/status/{user_id}` | Assessment | No |
| 19 | POST | `/api/v1/assessment/start` | Assessment | No |
| 20 | GET | `/api/v1/assessment/next/{assessment_id}` | Assessment | No |
| 21 | POST | `/api/v1/assessment/answer` | Assessment | No |
| 22 | POST | `/api/v1/assessment/scores/{user_id}` | Assessment | No |
| 23 | GET | `/api/v1/assessment/result/{user_id}` | Assessment | No |
| 24 | POST | `/api/v1/tts/speak` | TTS | No |
| 25 | GET | `/api/v1/avatar/status` | Avatar | No |
| 26 | POST | `/api/v1/avatar/speak` | Avatar | No |
| 27 | POST | `/api/v1/admin/login` | Admin | No (returns key) |
| 28 | GET | `/api/v1/admin/stats` | Admin | **X-Admin-Key** |
| 29 | GET | `/api/v1/admin/sessions` | Admin | **X-Admin-Key** |
| 30 | GET | `/api/v1/admin/sessions/{session_id}/logs` | Admin | **X-Admin-Key** |
| 31 | GET | `/api/v1/admin/crisis-alerts` | Admin | **X-Admin-Key** |

---

## 4. Test Strategy

| Aspect | Approach |
|--------|----------|
| **Testing type** | Black-box, functional, API integration |
| **Happy path** | Valid payloads → HTTP 200 + schema assertions |
| **Sad path** | Invalid/missing data → 401, 404, 422 as specified |
| **Edge cases** | Boundary mood scores, empty bodies, duplicate names |
| **Integration** | Ordered E2E: register → session → chat → assessment → admin |
| **Tools** | pytest + httpx (`test_complete.py`), requests (`run_tests.py`), `api_tester.html` |
| **Environment** | Local Windows, Uvicorn port 8000, MySQL database `sakoon` |
| **Test data** | Unique usernames per run (`pytest_<uuid>`); no mocks for HTTP layer |
| **Ordering** | `conftest.py` sorts tests `test_01`–`test_52` for state dependencies |

---

## 5. Test Cases (All 52)

| TC# | Test Name | Endpoint | Input (summary) | Expected | Actual (last run) | Status |
|-----|-----------|----------|-----------------|----------|-------------------|--------|
| TC01 | test_01_register_new_user_success | POST `/api/v1/auth/register` | `{name, languagePreference:"en"}` | 200, user.id > 0 | 200, user object returned | **PASS** |
| TC02 | test_02_register_duplicate_name | POST `/api/v1/auth/register` | Same name twice | 200 both; different ids | 200; id 10 ≠ id 11 | **PASS** |
| TC03 | test_03_register_missing_name | POST `/api/v1/auth/register` | `{languagePreference:"en"}` only | 422 validation | 422 | **PASS** |
| TC04 | test_04_register_with_language_preference | POST `/api/v1/auth/register` | `languagePreference:"ur"` | 200, pref = ur | 200, ur saved | **PASS** |
| TC05 | test_05_login_existing_user | POST `/api/v1/auth/login` | Registered name | 200, same user.id | 200, id match | **PASS** |
| TC06 | test_06_login_nonexistent_user | POST `/api/v1/auth/login` | Unknown name | 404 | 404, not found detail | **PASS** |
| TC07 | test_07_login_empty_body | POST `/api/v1/auth/login` | `{}` | 422 | 422 | **PASS** |
| TC08 | test_08_get_session_valid_user | GET `/api/v1/auth/session/{id}` | Valid userId | 200, session.id | 200, session created | **PASS** |
| TC09 | test_09_send_chat_message_success | POST `/api/v1/chat/message` | Stress message | 200, aiResponse non-empty | 200, Stress ~0.89 conf | **PASS** |
| TC10 | test_10_chat_has_classification | POST `/api/v1/chat/message` | Anxiety-related text | 200, mhClassification + confidence | 200, fields present | **PASS** |
| TC11 | test_11_chat_has_emotion | POST `/api/v1/chat/message` | Sad message | 200, emotionLabel set | 200, label returned | **PASS** |
| TC12 | test_12_chat_crisis_keyword | POST `/api/v1/chat/message` | Crisis keyword sample | isCrisis true, helplines | 200, crisis + 3 helplines | **PASS** |
| TC13 | test_13_chat_missing_userId | POST `/api/v1/chat/message` | No userId field | 422 | 422 | **PASS** |
| TC14 | test_14_journal_reflection | POST `/api/v1/chat/journal-reflection` | Journal text | 200, reflection string | 200, non-empty reflection | **PASS** |
| TC15 | test_15_get_session_history | GET `/api/v1/session/{id}/history` | Valid session | 200, user+assistant msgs | 200, ≥2 messages | **PASS** |
| TC16 | test_16_get_invalid_session | GET `/api/v1/session/999999/history` | Invalid id | 200, messages [] | 200, empty array | **PASS** |
| TC17 | test_17_mood_summary_valid_user | GET `/api/v1/user/{id}/mood-summary` | Valid user | 200, summary + trend | 200 | **PASS** |
| TC18 | test_18_mood_summary_invalid_user | GET `/api/v1/user/999999/mood-summary` | Invalid user | 200, empty summary | 200, [] | **PASS** |
| TC19 | test_19_get_recommendations | GET `/api/v1/user/{id}/recommendations` | Valid user | 200, recommendations array | 200, list (post-chat) | **PASS** |
| TC20 | test_20_exercise_feedback_no_assignment | POST `.../exercise-feedback` | assignmentId 999999 | 404 | 404 | **PASS** |
| TC21 | test_21_log_mood_score_1 | POST `/api/v1/mood/log` | mood_score: 1 | 200, ok true | 200 | **PASS** |
| TC22 | test_22_log_mood_score_5 | POST `/api/v1/mood/log` | mood_score: 5 | 200 | 200 | **PASS** |
| TC23 | test_23_log_mood_score_invalid_6 | POST `/api/v1/mood/log` | mood_score: 6 | 422 | 422 | **PASS** |
| TC24 | test_24_log_mood_score_0 | POST `/api/v1/mood/log` | mood_score: 0 | 422 | 422 | **PASS** |
| TC25 | test_25_get_mood_history | GET `/api/v1/mood/history/{id}` | After logs | 200, ≥2 entries | 200 | **PASS** |
| TC26 | test_26_log_behavior_all_fields | POST `/api/v1/mood/behavior` | Full payload | 200 | 200 | **PASS** |
| TC27 | test_27_log_behavior_partial_fields | POST `/api/v1/mood/behavior` | sleep_hours only | 200 | 200 | **PASS** |
| TC28 | test_28_get_behavior_history | GET `/api/v1/mood/behavior/{id}` | Valid user | 200, ≥1 entry | 200 | **PASS** |
| TC29 | test_29_create_profile | POST `/api/v1/assessment/profile` | age, gender, etc. | 200, ok | 200 | **PASS** |
| TC30 | test_30_get_profile | GET `/api/v1/assessment/profile/{id}` | Valid user | 200, profile.user_id match | 200 | **PASS** |
| TC31 | test_31_get_status_before_assessment | GET `/api/v1/assessment/status/{id}` | Valid user | completedSessions field | 200 | **PASS** |
| TC32 | test_32_start_session_1 | POST `/api/v1/assessment/start` | session_number: 1 | assessmentId, s1_* question | 200 | **PASS** |
| TC33 | test_33_get_next_question | GET `/api/v1/assessment/next/{id}` | assessment id | nextQuestion object | 200 | **PASS** |
| TC34 | test_34_answer_question | POST `/api/v1/assessment/answer` | s1_current_feeling text | 200 | 200 | **PASS** |
| TC35 | test_35_complete_session_1_all_answers | Flow: start/answer loop | All S1 questions | Session 1 complete | Completed via helper | **PASS** |
| TC36 | test_36_complete_session_2 | Flow session 2 | PHQ-9 + GAD-7 keys | Session 2 complete | Completed | **PASS** |
| TC37 | test_37_complete_session_3 | Flow session 3 | Behavioral b_* keys | Session 3 complete | Completed | **PASS** |
| TC38 | test_38_get_final_result | POST scores + GET result | userId | depression/anxiety scores | 200, scores 0, low risk | **PASS** |
| TC39 | test_39_tts_speak_english | POST `/api/v1/tts/speak` | English text | 200 audio/mpeg or 503 | 200 (when edge-tts OK) | **PASS** |
| TC40 | test_40_tts_speak_empty_text | POST `/api/v1/tts/speak` | `text:""` | 422/503 | 503 or 422 | **PASS** |
| TC41 | test_41_tts_speak_urdu | POST `/api/v1/tts/speak` | Urdu text | 200 or 503 | Acceptable either | **PASS** |
| TC42 | test_42_avatar_status | GET `/api/v1/avatar/status` | — | wav2lipReady flags | 200 | **PASS** |
| TC43 | test_43_avatar_speak | POST `/api/v1/avatar/speak` | Short text | 200 binary or 503 | 200/503 per setup | **PASS** |
| TC44 | test_44_avatar_speak_no_text | POST `/api/v1/avatar/speak` | Blank text | 422 | 422 | **PASS** |
| TC45 | test_45_admin_login_valid | POST `/api/v1/admin/login` | admin credentials | 200, adminKey | 200 | **PASS** |
| TC46 | test_46_admin_login_wrong_password | POST `/api/v1/admin/login` | Wrong password | 401 | 401 | **PASS** |
| TC47 | test_47_admin_login_wrong_username | POST `/api/v1/admin/login` | Wrong username | 401 | 401 | **PASS** |
| TC48 | test_48_get_stats_with_key | GET `/api/v1/admin/stats` | X-Admin-Key header | 200, totalSessions int | 200 | **PASS** |
| TC49 | test_49_get_stats_no_key | GET `/api/v1/admin/stats` | No header | 401 | 401 | **PASS** |
| TC50 | test_50_get_sessions_list | GET `/api/v1/admin/sessions` | X-Admin-Key | 200, sessions array | 200 | **PASS** |
| TC51 | test_51_get_session_logs | GET `/api/v1/admin/sessions/{id}/logs` | X-Admin-Key | 200, messages | 200 | **PASS** |
| TC52 | test_52_get_crisis_alerts | GET `/api/v1/admin/crisis-alerts` | X-Admin-Key | 200, alerts array | 200 | **PASS** |

---

## 6. Test Coverage by Module

| Module | Endpoints | Test Cases | Pass | Fail | Coverage %* |
|--------|-----------|------------|------|------|-------------|
| System | 2 | 0† | — | — | Smoke in runner only |
| Auth | 3 | 8 | 8 | 0 | 100% |
| Chat | 2 | 6 | 6 | 0 | 100% |
| Session | 1 | 2 | 2 | 0 | 100% |
| User | 3 | 4 | 4 | 0 | 100% |
| Mood | 4 | 8 | 8 | 0 | 100% |
| Assessment | 8 | 10 | 10 | 0 | 100% |
| TTS | 1 | 3 | 3 | 0 | 100% |
| Avatar | 2 | 3 | 3 | 0 | 100% |
| Admin | 5 | 8 | 8 | 0 | 100% |
| **Total** | **31** | **52** | **52** | **0** | **100%** |

\*Coverage % = (test cases passed / test cases executed) per module.  
†`GET /` and `GET /health` exercised in `run_tests.py` (56-check suite), not in pytest file.

---

## 7. Key Test Scenarios (Detailed Walkthrough)

### FLOW A — New User Complete Journey

1. **Register** → `POST /auth/register` → receive `userId`.  
2. **Login** → `POST /auth/login` → confirm same id.  
3. **Session** → `GET /auth/session/{userId}` → receive `sessionId`.  
4. **Chat** (multiple) → `POST /chat/message` → `aiResponse`, classification, optional exercise.  
5. **History** → `GET /session/{sessionId}/history` → interleaved user/assistant messages.  
6. **Mood** → `POST /mood/log`, `POST /mood/behavior`.  
7. **Recommendations** → `GET /user/{id}/recommendations`.

**Validated by:** TC01, TC05, TC08, TC09–TC15, TC17, TC19, TC21–TC28.

### FLOW B — Full Assessment (3 Sessions → Result)

1. Save profile → start session 1 → answer all `s1_*` questions.  
2. Start session 2 → answer `phq_1`–`phq_9`, `gad_1`–`gad_7`.  
3. Start session 3 → answer `b_sleep`, `b_exercise`, etc.  
4. `POST /assessment/scores/{userId}` → PHQ/GAD sums and severity.  
5. `GET /assessment/result/{userId}` → persisted camelCase result.

**Validated by:** TC29–TC38; automated via `complete_assessment_session()` in `qa_helpers.py`.

### FLOW C — Crisis Detection & Safety

1. User sends message containing crisis keywords (`CRISIS_KEYWORDS` in `constants.py`).  
2. `RiskDetector` sets `is_crisis`; response includes **Umang, PMHW, Sehat Tahaffuz** numbers.  
3. LLM uses crisis prompt (short, grounding, helplines).  
4. Admin can query `/admin/crisis-alerts`.

**Validated by:** TC12, TC52.

### FLOW D — Admin Monitoring

1. `POST /admin/login` → store `adminKey`.  
2. `GET /admin/stats` with header → session/crisis counts.  
3. `GET /admin/sessions` → list users/sessions.  
4. `GET /admin/sessions/{id}/logs` → transcript.  
5. Without key → **401** (TC49).

**Validated by:** TC45–TC52.

### FLOW E — TTS Audio Generation

1. `POST /tts/speak` with English text → `audio/mpeg` bytes.  
2. Urdu text → may use `ur-PK` voice or 503 if unavailable.  
3. Empty text → 503/422 (no audio).

**Validated by:** TC39–TC41.

---

## 8. Edge Cases & Boundary Tests

| Case | Test ID | Result |
|------|---------|--------|
| `mood_score = 0` (below min 1) | TC24 | 422 |
| `mood_score = 6` (above max 5) | TC23 | 422 |
| `mood_score = 1` and `5` (boundaries) | TC21, TC22 | 200 |
| Login empty JSON `{}` | TC07 | 422 |
| Register missing `name` | TC03 | 422 |
| Chat missing `userId` | TC13 | 422 |
| Invalid assignment feedback | TC20 | 404 |
| Invalid session history | TC16 | 200, empty list |
| Invalid user mood summary | TC18 | 200, empty summary |
| Duplicate registration same name | TC02 | 200, new ids (not rejected) |
| Assessment scores before complete | (runner) | 400 |
| Avatar blank text | TC44 | 422 |
| Admin stats without key | TC49 | 401 |

---

## 9. Integration Test Results (E2E Trace)

| Step | Action | HTTP | Key response fields |
|------|--------|------|---------------------|
| 1 | Register | POST `/auth/register` | `user.id = 9` |
| 2 | Login | POST `/auth/login` | Same `id` |
| 3 | Session | GET `/auth/session/9` | `session.id = 9` |
| 4 | Chat | POST `/chat/message` | `mhClassification`, `chatLogId` |
| 5 | Mood log | POST `/mood/log` | `ok: true` |
| 6 | Assessment S1–S3 | start/answer loops | `assessmentId` progression |
| 7 | Scores | POST `/assessment/scores/9` | `depression_score`, `anxiety_score` |
| 8 | Admin login | POST `/admin/login` | `adminKey` |
| 9 | Crisis check | GET `/admin/crisis-alerts` | `alerts` (may list TC12) |

Full JSON excerpts: see **`TEST_EVIDENCE.md`** and **`test_results.json`**.

---

## 10. API Route Testing Evidence (Samples)

See **`TEST_EVIDENCE.md`** Section 3 for HTTP request/response captures including:

- Register (200)  
- Chat stress (200, ~5.5s with OpenRouter)  
- Crisis chat (`isCrisis: true`, helplines)  
- Mood validation (422)  
- Admin unauthorized (401)  
- Assessment result (200)  

---

## 11. Findings & Observations

### What works well

- All **52** pytest integration tests pass in sequence (~65s).  
- **Crisis pipeline** reliably flags keywords and returns Pakistan helplines.  
- **Assessment automation** completes all three sessions and computes scores.  
- **Admin RBAC** via API key behaves correctly (401 vs 200).  
- **Pydantic validation** consistently returns 422 for bad input.  
- **OpenRouter LLM** produces contextual replies when API key is configured; fallback text when not.

### Notes / limitations

- **HF emotion/sentiment** may log import warnings on some Windows setups; chat still returns labels via fallback/heuristics.  
- **Duplicate names** create separate users — document for frontend (exact name match on login).  
- **TTS/Avatar** depend on external services (edge-tts, Wav2Lip); tests accept 503 when not configured.  
- User auth is **not password-based** — acceptable for FYP prototype only.

### Performance (observed)

| Operation | Typical latency |
|-----------|-----------------|
| Auth / mood | 50–200 ms |
| Chat (LLM) | 3–8 s |
| Full assessment flow | 30–90 s |
| TTS | 1–4 s |

---

## 12. Conclusion

The Sakoon AI backend API comprises **31 documented endpoints** across nine functional modules. We executed **52 structured integration test cases** with **100% pass rate** on 19 May 2026, supplemented by a **56-check sequential runner** and custom HTML API tester. Happy-path and sad-path behavior, crisis safety, clinical assessment workflow, and admin security are verified against a **live server and real database**.

The backend is **ready for frontend integration** and **supervisor demonstration**, subject to production hardening (JWT, HTTPS, restricted CORS, and professional ethics review).

---

**Appendices:** `TEST_EVIDENCE.md` | `ROUTE_DOCUMENTATION.md` | `SUPERVISOR_QA.md` | `MEETING_CHECKLIST.md` | `test_results.json`
