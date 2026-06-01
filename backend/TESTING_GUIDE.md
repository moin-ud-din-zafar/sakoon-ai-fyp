# Sakoon AI Backend — Testing Guide

Complete manual and automated testing for the FastAPI backend (`http://127.0.0.1:8000`).

> **Full API test document (routes, headers, request/response JSON):** see **[API_COMPLETE_TEST_DOCUMENTATION.md](./API_COMPLETE_TEST_DOCUMENTATION.md)** — use this for viva/FYP submission.

## Files in this folder

| File | Purpose |
|------|---------|
| `API_COMPLETE_TEST_DOCUMENTATION.md` | **All routes, headers, JSON bodies, test flows** |
| `ROUTE_DOCUMENTATION.md` | Shorter API reference |
| `test_complete.py` | 52 pytest integration tests |
| `conftest.py` | Pytest fixtures + test ordering |
| `qa_helpers.py` | Shared state and assessment completion helpers |
| `run_tests.py` | Sequential runner (no pytest): `python run_tests.py` |
| `api_tester.html` | Browser Postman-style UI |
| `test_all_routes.py` | Legacy broad smoke script (optional) |

---

## 1. Setup checklist

Before testing, confirm:

- [ ] Python 3.11+ and virtualenv activated
- [ ] `pip install -r requirements.txt`
- [ ] Extra test deps: `pip install pytest httpx requests python-dotenv`
- [ ] `.env` exists (copy from `.env.example`)
- [ ] **Database**
  - **SQLite (easiest):** `USE_SQLITE=true` in `.env` — tables auto-created
  - **MySQL:** `USE_SQLITE=false`, run `python scripts/setup_mysql.py` or `mysql < ../database/init_sakoon.sql`
- [ ] **MH classifier models:** `python scripts/train_model.py` → creates `backend/models/*.joblib`
- [ ] **OpenRouter:** `OPENROUTER_API_KEY` set for real LLM replies (fallback text works without it)
- [ ] **Server running:**
  ```powershell
  cd backend
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ```
- [ ] Health check: `GET http://127.0.0.1:8000/health` → `{"status":"ok"}`
- [ ] Optional TTS: `pip install edge-tts` (network required)
- [ ] Optional avatar: Wav2Lip setup via `scripts/setup_wav2lip.py`

---

## 2. Automated test commands

### Simple runner (recommended first)

```powershell
cd backend
python run_tests.py
python run_tests.py --verbose
python run_tests.py --base-url http://127.0.0.1:8000
```

Output: colored PASS/FAIL, summary table, `test_results.json`.

### Pytest (52 named tests)

```powershell
cd backend
pytest test_complete.py -v --tb=short
pytest test_complete.py -m smoke -v
pytest test_complete.py -m critical -v
```

Tests run in order `test_01` … `test_52` (see `conftest.py`).

### HTML tester

```powershell
cd backend
python -m http.server 5500
```

Open: http://127.0.0.1:5500/api_tester.html

Use **Quick flow** / **Run All Tests** or pick endpoints from the sidebar.

---

## 3. Manual test — all endpoints in terminal

**Two terminals required:**

**Terminal 1 — server (keep running):**
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — run every endpoint one by one with JSON output:**
```powershell
cd backend
powershell -ExecutionPolicy Bypass -File .\test_endpoints_manual.ps1
```

| Flag | Effect |
|------|--------|
| `-Pause` | Press Enter after each step (slow walkthrough) |
| `-SkipSlow` | Skip chat LLM, journal, TTS, avatar speak (fast smoke) |

Example slow demo for viva:
```powershell
.\test_endpoints_manual.ps1 -Pause
```

---

## 4. Manual test flows

### FLOW A — New user complete journey

| Step | Request | Expected |
|------|---------|----------|
| 1 | `POST /api/v1/auth/register` `{"name":"ali_test","languagePreference":"en"}` | 200, `user.id` present |
| 2 | `POST /api/v1/auth/login` `{"name":"ali_test"}` | 200, same `user.id` |
| 3 | `GET /api/v1/auth/session/{userId}` | 200, `session.id`, `isLimitReached: false` |
| 4 | `POST /api/v1/chat/message` × 3–5 messages | 200, `aiResponse`, `mhClassification`, `chatLogId` |
| 5 | `GET /api/v1/session/{sessionId}/history` | 200, `messages` with `user` + `assistant` roles |
| 6 | `POST /api/v1/mood/log` `mood_score: 3` | 200, `ok: true` |
| 7 | `POST /api/v1/mood/behavior` sleep/activity fields | 200 |
| 8 | `GET /api/v1/user/{userId}/recommendations` | 200, array (exercises from chat) |

### FLOW B — Assessment complete (3 sessions)

| Step | Request | Expected |
|------|---------|----------|
| 1 | Register + get session | userId, sessionId |
| 2 | `POST /api/v1/assessment/profile` | 200 |
| 3 | `POST /api/v1/assessment/start` `session_number: 1` | `assessmentId`, `nextQuestion.key` like `s1_*` |
| 4 | Loop: `GET /next/{id}` → `POST /answer` until completed | Session 1 done |
| 5 | Repeat for `session_number: 2` (PHQ-9 + GAD-7 keys `phq_*`, `gad_*`) | Session 2 done |
| 6 | Repeat for `session_number: 3` (behavior keys `b_*`) | Session 3 done |
| 7 | `POST /api/v1/assessment/scores/{userId}` | `depression_score`, `anxiety_score`, `risk_level` |
| 8 | `GET /api/v1/assessment/result/{userId}` | `depressionScore`, `anxietyScore`, `summary` |

**Session 1 question keys:** `s1_current_feeling`, `s1_main_concern`, `s1_duration`, `s1_support`, `s1_initial_mood`

### FLOW C — Crisis detection

| Step | Request | Expected |
|------|---------|----------|
| 1 | Register + session | userId, sessionId |
| 2 | `POST /chat/message` with text containing **`suicide`** or **`kill myself`** (see `app/core/constants.py` `CRISIS_KEYWORDS`) | `isCrisis: true`, `riskLevel: "high"`, `helplineNumbers` length ≥ 1 |
| 3 | `GET /api/v1/admin/crisis-alerts` with `X-Admin-Key` | alerts list may include this session |

Example message: `"I have been thinking about suicide and want to end my life"`

### FLOW D — Admin flow

| Step | Request | Expected |
|------|---------|----------|
| 1 | `POST /api/v1/admin/login` `{"username":"admin","password":"sakoon123"}` (from `.env`) | 200, `adminKey` |
| 2 | `GET /api/v1/admin/stats` header `X-Admin-Key: <adminKey>` | 200, `totalSessions`, `crisisCount` |
| 3 | `GET /api/v1/admin/sessions` | 200, `sessions` array |
| 4 | `GET /api/v1/admin/sessions/{sessionId}/logs` | 200, `messages` |
| 5 | Without header → `GET /admin/stats` | **401** |

### FLOW E — TTS / Avatar

| Step | Request | Expected |
|------|---------|----------|
| 1 | `POST /api/v1/tts/speak` `{"text":"Hello","language":"en"}` | 200, `Content-Type: audio/mpeg`, body length > 100 bytes **or** 503 if edge-tts unavailable |
| 2 | `GET /api/v1/avatar/status` | `wav2lipReady`, `faceImageExists` booleans |
| 3 | `POST /api/v1/avatar/speak` `{"text":"Hi","language":"en"}` | 200 video/mp4 or audio/wav; header `X-Avatar-Mode` |

---

## 5. Expected response shapes (key fields)

### Chat message (200)

```json
{
  "aiResponse": "string",
  "mhClassification": "Stress | Anxiety | Depression | ...",
  "mhConfidence": 0.0,
  "emotionLabel": "string",
  "riskLevel": "low | medium | high",
  "isCrisis": false,
  "helplineNumbers": [],
  "suggestedExercise": { ... } | null,
  "chatLogId": 123
}
```

### Assessment result (200)

```json
{
  "depressionScore": 0,
  "anxietyScore": 0,
  "riskLevel": "low",
  "depressionSeverity": "minimal",
  "anxietySeverity": "minimal",
  "summary": "string",
  "recommendations": "string"
}
```

---

## 6. Common errors and fixes

| Error | Cause | Fix |
|-------|--------|-----|
| Connection refused | Server not running | Start uvicorn on port 8000 |
| `FileNotFoundError` mh_classifier | Models not trained | `python scripts/train_model.py` |
| MySQL access denied | Wrong `DATABASE_*` in `.env` | Fix credentials or use `USE_SQLITE=true` |
| OpenRouter empty / fallback only | Missing/invalid API key | Set `OPENROUTER_API_KEY` |
| TTS 503 | edge-tts not installed or offline | `pip install edge-tts` |
| Emotion/sentiment warnings in logs | transformers/torch issue | Reinstall `transformers torch`; chat still works |
| Assessment 400 on scores | Sessions 1–3 incomplete | Finish all questions in each session |
| Admin 401 | Wrong/missing `X-Admin-Key` | Login via `/admin/login` first |
| CORS in browser file:// | Opening HTML as file | Serve via `python -m http.server 5500` |

---

## 7. Performance benchmarks (local dev, approximate)

| Endpoint | Typical time |
|----------|----------------|
| `/health` | < 50 ms |
| `/auth/register` | 50–200 ms |
| `/chat/message` (with OpenRouter) | 2–15 s |
| `/chat/message` (fallback only) | 200–800 ms |
| `/mood/log` | < 100 ms |
| Full assessment (3 sessions) | 30–90 s (many round-trips) |
| `/tts/speak` | 1–4 s |
| HF emotion (first call) | +5–30 s model load |

---

## 8. Auth notes (for viva)

- **Users:** No JWT. Identity = `userId` from register/login.
- **Admin:** Shared secret `ADMIN_KEY` returned after password login; sent as **`X-Admin-Key`** header.
- **Not production-ready** for PHI without proper OAuth, HTTPS, and rate limiting.

---

## 9. Environment variables for testing

| Variable | Required | Notes |
|----------|----------|--------|
| `USE_SQLITE` | Yes | `true` for file DB |
| `OPENROUTER_API_KEY` | For LLM | Optional for fallback replies |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin tests | Default `admin` / `sakoon123` |
| `ADMIN_KEY` | Admin API | Must match login response |
| `API_BASE_URL` | Test scripts | Default `http://127.0.0.1:8000` |

---

## 10. Docker testing

```powershell
docker build -t sakoon-api backend
docker run -p 8000:8000 --env-file backend/.env sakoon-api
```

Dockerfile sets `USE_SQLITE=true` internally; override with `-e USE_SQLITE=false` if using external MySQL.
