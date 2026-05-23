# Sakoon AI — Supervisor Q&A Preparation

**30 anticipated questions with technical answers (4–6 lines each).**  
Read aloud before your FYP meeting.

---

## ARCHITECTURE (5)

**Q1: Why did you choose FastAPI over Django or Flask?**  
FastAPI gives us automatic OpenAPI docs (`/docs`), native async support for TTS/avatar routes, and Pydantic validation on every request body. For an API-only mental health backend with ML and external LLM calls, we do not need Django’s admin UI or ORM — our data layer is a focused `db_service` module. FastAPI’s performance and type hints also match our Python 3.11 stack and keep route code readable for viva and maintenance.

**Q2: Why support both SQLite and MySQL?**  
`USE_SQLITE=true` in `.env` creates `backend/data/sakoon.db` automatically — ideal for development, demos, and Docker without installing MySQL. Production uses MySQL via `mysql-connector-python` and `database/init_sakoon.sql`. The same SQL patterns are abstracted in `db_service.py` with `?` vs `%s` placeholders, so one codebase serves both environments.

**Q3: Why is there no JWT for users but an API key for admin?**  
End users are identified by a display **name** at register/login — a prototype choice for low-friction access in a research/FYP setting, not for real PHI. The frontend stores `userId` and `sessionId`. Admin routes protect sensitive aggregates (all sessions, crisis logs) with `POST /admin/login` returning `adminKey`, sent as header **`X-Admin-Key`** on subsequent calls — verified in `app/api/deps.py` via `verify_admin`.

**Q4: How does the mental health (MH) classifier work?**  
We train a **TF-IDF vectorizer + Logistic Regression** on `Dataset/Combined Data.csv` (`scripts/train_model.py`). At runtime, `MentalHealthClassifier` in `classifier_service.py` preprocesses text, vectorizes it, and outputs one of seven labels (Normal, Stress, Anxiety, Depression, Suicidal, Bipolar, Personality disorder) with a confidence score. That label feeds risk detection, personalization, and the LLM context — it is not a diagnosis, only a signal.

**Q5: How is CORS configured and why?**  
In `app/main.py`, `CORSMiddleware` allows all origins (`allow_origins=["*"]`) so our React frontend on a different port (e.g. `localhost:5173`) can call the API during development. In production we would restrict origins to the deployed frontend domain and enable HTTPS. CORS is a browser security feature; our pytest tests call the API directly and do not depend on CORS.

**Q6: What is the session limit of 3 and why?**  
`MAX_SESSIONS_PER_USER = 3` in `app/core/constants.py` caps how many therapy **sessions** a user can open (`get_or_create_session` in `db_service.py`). This models a bounded trial or study protocol and prevents unlimited DB growth in demos. When the limit is reached, `/auth/session/{user_id}` returns `session: null` and `isLimitReached: true`.

---

## TESTING (10)

**Q7: What is the difference between happy path and sad path testing?**  
Happy path uses **valid** input and expects success (e.g. register with name → 200). Sad path uses **invalid** input and expects controlled errors (e.g. login unknown user → 404, mood_score 6 → 422). Both are in `test_complete.py` so we verify the API fails safely, not silently or with 500 errors.

**Q8: How did you test crisis detection?**  
`test_12_chat_crisis_keyword` sends text from `CRISIS_KEYWORD_SAMPLE` in `qa_helpers.py`, which includes phrases like “suicide” and “end my life” from `CRISIS_KEYWORDS` in `constants.py`. We assert `isCrisis: true`, `riskLevel` high/medium, and non-empty `helplineNumbers` (Umang, PMHW, Sehat Tahaffuz). Admin `crisis-alerts` is tested in `test_52`.

**Q9: What is the purpose of `conftest.py`?**  
It defines **session-scoped** pytest fixtures: `client` (httpx with base URL), `state` (`SakoonTestState` for userId/sessionId/adminKey), and `admin_credentials`. It checks `/health` before tests run and sorts tests by `test_XX_` number so register runs before chat. This avoids duplicating setup in 52 test functions.

**Q10: Why pytest instead of unittest?**  
Pytest gives simpler assertions, fixture injection, markers (`@pytest.mark.critical`), and readable failure output. Our suite is **integration-heavy** (real HTTP), where pytest + httpx is a common industry pattern. `run_tests.py` exists for supervisors who prefer a single `python run_tests.py` without installing pytest.

**Q11: How did you ensure test isolation?**  
Each pytest session creates a **unique username** (`pytest_<uuid>`) so DB rows do not clash. Tests are ordered 01→52 so state builds logically. We do not delete users after tests (no delete API), but unique names isolate runs. Sad-path tests use non-existent IDs (999999) where needed.

**Q12: What does HTTP 422 mean in FastAPI?**  
**422 Unprocessable Entity** — request JSON failed **Pydantic validation** (missing `name`, `mood_score` out of range 1–5, invalid `languagePreference`). FastAPI returns a structured `detail` array describing each field error. We assert 422 in tests 03, 07, 13, 23, 24, 40, 44.

**Q13: How are test cases ordered and why does order matter?**  
`conftest.py` sorts collected tests by numeric prefix `test_01` … `test_52`. Register (01) must run before chat (09) because chat needs `userId` and `sessionId` in shared `state`. Assessment tests 35–37 complete sessions sequentially. Wrong order would cause false failures from missing state.

**Q14: What is an integration test vs a unit test?**  
**Unit tests** would mock DB and LLM and test one function in isolation. Our **`test_complete.py` tests are integration tests**: they start the real server and call real endpoints, DB, classifier, and (if configured) OpenRouter. They prove the **system works together**, which is what the supervisor cares about for API acceptance.

**Q15: How did you test the 3-session assessment flow?**  
Tests 29–38: save profile, start session 1, answer questions via `complete_assessment_session()` in `qa_helpers.py` (loops `GET /next` + `POST /answer`), repeat for sessions 2 (PHQ-9/GAD-7) and 3 (behavioral), then `POST /scores/{userId}` and `GET /result/{userId}`. We assert depression/anxiety scores and severity fields are present.

**Q16: What would you add with more testing time?**  
`pytest-cov` for code coverage, **Locust** load tests, contract tests against OpenAPI schema, mocked LLM unit tests for speed, GitHub Actions CI, and security tests (SQL injection, rate limits). We would also add automated teardown or a test database reset script.

---

## API DESIGN (5)

**Q17: Why are users identified by name, not username + password?**  
The FYP scope prioritizes **accessibility** and quick onboarding for a support chatbot prototype. Name-based login reduces friction for demos. We document that this is **not production-ready** for confidential health data — a real deployment would need passwords, JWT, and encryption.

**Q18: How does the chat pipeline work end to end?**  
`POST /chat/message` → MH classifier → `RiskDetector` (keywords + Suicidal class) → optional Urdu normalization/translation → HF emotion/sentiment → load last turns from DB → `generate_response()` (OpenRouter + therapeutic prompts) → optional coping exercise assignment → `create_chat_log` + `emotion_history`. Response includes `aiResponse`, labels, risk, helplines if crisis.

**Q19: What happens when a crisis keyword is detected?**  
`risk_detector_service.py` matches `CRISIS_KEYWORDS` or high-confidence Suicidal class. `is_crisis` becomes true, `helplineNumbers` lists Pakistan numbers from `constants.py`, and `llm_service` switches to **crisis mode** prompts (short, grounding-first, helplines woven in). Exercise assignment is skipped when `is_crisis` is true.

**Q20: How is admin protected differently from users?**  
Users have no secret token — only `userId`. Admin must `POST /admin/login` with `ADMIN_USERNAME` / `ADMIN_PASSWORD` from `.env`, receive `adminKey`, and send **`X-Admin-Key`** on `/admin/stats`, `/sessions`, `/crisis-alerts`. Missing/wrong key → **401** (`test_49`). This separates public chat from operational monitoring.

**Q21: What validation does Pydantic provide?**  
Route models enforce types and constraints: e.g. `mood_score` ge=1 le=5, `session_number` ge=1 le=3, `languagePreference` literal enum, required fields on `ChatRequest` (`userId`, `sessionId`, `message`). Invalid bodies never reach business logic — FastAPI returns 422 with field-level errors.

---

## MENTAL HEALTH DOMAIN (5)

**Q22: What are PHQ-9 and GAD-7?**  
**PHQ-9** (Patient Health Questionnaire-9) screens **depression** severity over two weeks. **GAD-7** screens **generalized anxiety**. Our assessment session 2 uses the same 0–3 frequency scale (“Not at all” to “Nearly every day”) in `assessment_service.py`. Scores are summed and mapped to severity bands in `calculate_scores()` — screening tools, not clinical diagnosis.

**Q23: How does the MH classifier relate to PHQ-9?**  
They serve different purposes: the **classifier** labels free-text chat in real time (7 categories from training data). **PHQ-9/GAD-7** are structured questionnaires in the assessment module with scored items. Together they give conversational signals plus standardized screening — documented separately in the API.

**Q24: What is the 3-session assessment structure?**  
**Session 1:** intake (`s1_*` questions — feelings, concerns, duration). **Session 2:** PHQ-9 (`phq_1`–`phq_9`) + GAD-7 (`gad_1`–`gad_7`). **Session 3:** behavioral (`b_sleep`, `b_exercise`, `b_social`, etc.). Sessions must complete in order. Final `POST /scores` computes depression/anxiety scores and risk.

**Q25: How are Pakistan helplines integrated?**  
`HELPLINE_NUMBERS` in `constants.py` lists Umang (0311-7786264), PMHW (1020), Sehat Tahaffuz (1166). When `is_crisis` is true, chat JSON includes this array and the LLM crisis prompt requires weaving them into the reply. Admin can list crisis-flagged chats via `/admin/crisis-alerts`.

**Q26: What ethical considerations are built in?**  
Disclaimers implied: AI support, not a licensed therapist; classifier/assessment are **screening** only. Crisis path prioritizes safety (helplines, no exercise push). Prompts in `llm_service.py` ban harmful chatbot phrases and avoid clinical labeling in user-facing text. Production would need consent, privacy policy, and professional oversight.

---

## FRONTEND INTEGRATION (5)

**Q27: How would a frontend connect to this backend?**  
Set `VITE_API_BASE_URL=http://localhost:8000/api/v1` (or production URL). Use `fetch` or axios: `POST /auth/register`, store `user.id`, `GET /auth/session/{id}` for `session.id`, then `POST /chat/message` with `{ userId, sessionId, message }`. Other pages call mood, assessment, and TTS routes similarly. Swagger `/docs` lists all contracts.

**Q28: What should the frontend store after login?**  
**`userId`**, **`sessionId`**, optional **`languagePreference`**, and for admin UI **`adminKey`** in memory/sessionStorage (not localStorage for admin in production). No JWT — re-login by name returns the same user if they use the exact name match (`get_user_by_name`).

**Q29: How should the frontend handle crisis responses?**  
When `isCrisis === true`, show **helplineNumbers** prominently (tap-to-call), use calm UI, avoid hiding the message, and optionally link to emergency services. Do not continue gamified exercises. Consider blocking further automated prompts until user acknowledges resources. Log incident only on server (already in `chat_logs.is_crisis`).

**Q30: How does TTS integrate with a UI?**  
`POST /api/v1/tts/speak` with `{ text, language }` returns **audio/mpeg** bytes. Frontend plays via `Audio` object or blob URL. Urdu uses `ur-PK-UzmaNeural` via `EDGE_VOICE_BY_LANG` in `tts_service.py`. Avatar route `/avatar/speak` returns MP4 or WAV with header `X-Avatar-Mode` for lip-sync video when Wav2Lip is configured.

---

*End of Q&A — cross-reference `FYP_TEST_REPORT.md` and `ROUTE_DOCUMENTATION.md` for evidence.*
