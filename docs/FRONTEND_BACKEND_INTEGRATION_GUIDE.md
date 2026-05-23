# Sakoon AI — Frontend ↔ Backend Integration Guide (Developer Handbook)

**Audience:** Frontend developers, full-stack teammates, FYP evaluators  
**Backend repo branch:** `Backend_sakoon_Ai` → https://github.com/moin-ud-din-zafar/sakoon-ai-fyp  
**API version:** `/api/v1`  
**Last updated:** 2026-05-20

---

## Table of contents

1. [Overview](#1-overview)
2. [Project layout](#2-project-layout)
3. [Rules & regulations (must follow)](#3-rules--regulations-must-follow)
4. [Setup — commands step by step](#4-setup--commands-step-by-step)
5. [Environment variables](#5-environment-variables)
6. [How frontend talks to backend](#6-how-frontend-talks-to-backend)
7. [Authentication & session model](#7-authentication--session-model)
8. [Integration flows (step by step)](#8-integration-flows-step-by-step)
9. [API ↔ Frontend file map](#9-api--frontend-file-map)
10. [Endpoint reference for UI developers](#10-endpoint-reference-for-ui-developers)
11. [Adding missing APIs to `api.js`](#11-adding-missing-apis-to-apijs)
12. [Crisis & safety UI rules](#12-crisis--safety-ui-rules)
13. [TTS & avatar integration](#13-tts--avatar-integration)
14. [Error handling standards](#14-error-handling-standards)
15. [CORS & deployment](#15-cors--deployment)
16. [Testing checklist](#16-testing-checklist)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Overview

Sakoon AI is split into:

| Part | Tech | Port (dev) |
|------|------|------------|
| **Backend** | FastAPI + Python | `8000` |
| **Frontend** | React + Vite | `5173` |

The frontend **does not** embed AI logic. It only:

1. Sends HTTP JSON (or blob for audio) to the backend  
2. Stores `userId` / `sessionId` in React state + `localStorage`  
3. Renders responses (chat, exercises, crisis panel, mood charts)

```
┌─────────────┐     HTTP/JSON      ┌──────────────────────┐
│   React UI  │ ◄──────────────► │  FastAPI /api/v1     │
│  (Vite)     │                    │  Services + MySQL    │
└─────────────┘                    └──────────────────────┘
```

**Swagger (live API docs):** `http://127.0.0.1:8000/docs`  
**Detailed API bodies:** `backend/API_COMPLETE_TEST_DOCUMENTATION.md`

---

## 2. Project layout

```
Ai Virtual Assistant/
├── backend/                 # API (pushed to Backend_sakoon_Ai branch)
│   ├── app/main.py          # FastAPI entry
│   ├── app/api/routes/      # HTTP routes
│   ├── app/services/        # Business logic
│   └── .env.example         # Copy to .env (never commit .env)
├── frontend/                # React app (separate folder — clone full repo or add later)
│   ├── src/services/api.js  # ★ Main API client — extend here
│   ├── src/contexts/        # AppContext, ChatContext, TTSContext
│   └── .env.example         # VITE_API_BASE_URL
├── database/init_sakoon.sql # MySQL schema
└── docs/                    # This file
```

**Important:** Git branch `Backend_sakoon_Ai` contains **only** backend-related folders. For integration work you need **both** `frontend/` and `backend/` on your machine (full project clone).

---

## 3. Rules & regulations (must follow)

### Security

| Rule | Detail |
|------|--------|
| **R1** | Never commit `backend/.env` or `frontend/.env` — use `.env.example` only |
| **R2** | Never put `OPENROUTER_API_KEY` or DB passwords in frontend code |
| **R3** | Frontend only uses `VITE_*` env vars (exposed to browser by design) |
| **R4** | Do not store admin `X-Admin-Key` in `localStorage` on shared machines without encryption |

### API usage

| Rule | Detail |
|------|--------|
| **R5** | All user APIs go to `{BASE}/api/v1/...` — no trailing slash required |
| **R6** | Send `Content-Type: application/json` on POST bodies |
| **R7** | Pass **`userId` + `sessionId`** on every chat call — there is **no JWT** yet |
| **R8** | Max **3 sessions** per user — handle `isLimitReached: true` in UI |
| **R9** | On `isCrisis: true`, show helplines and **do not** push exercises as primary CTA |

### UX / product

| Rule | Detail |
|------|--------|
| **R10** | Chat responses can take **2–60 seconds** — always show loading / typing state |
| **R11** | Use `replyLanguage` from chat response for TTS voice selection when available |
| **R12** | Map backend snake_case in session object (`user_id`) to camelCase in UI (`userId`) in one place only (`AppContext`) |

### Code conventions

| Rule | Detail |
|------|--------|
| **R13** | Add new endpoints in **`frontend/src/services/api.js`** — do not scatter `fetch` across components |
| **R14** | Use existing `axios` instance `api` (base URL + headers already set) |
| **R15** | Handle `err.response?.data?.detail` for FastAPI errors (string or array) |

---

## 4. Setup — commands step by step

### 4.1 Backend (Terminal 1)

```cmd
cd /d "E:\Ai Virtual Assistant\backend"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env`:

```env
USE_SQLITE=true
OPENROUTER_API_KEY=your_key_here
```

Train classifier (first time only):

```cmd
python scripts\train_model.py
```

Start API:

```cmd
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify: http://127.0.0.1:8000/health → `{"status":"ok"}`

### 4.2 Frontend (Terminal 2)

```cmd
cd /d "E:\Ai Virtual Assistant\frontend"
npm install
copy .env.example .env
```

Edit `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Start UI:

```cmd
npm run dev
```

Open: http://127.0.0.1:5173/

### 4.3 Both must run together

If frontend shows network errors, backend is usually not running or wrong `VITE_API_BASE_URL`.

---

## 5. Environment variables

### Backend (`backend/.env`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `USE_SQLITE` | Dev: `true` | File DB without MySQL |
| `DATABASE_*` | If MySQL | Host, user, password, name |
| `OPENROUTER_API_KEY` | For real AI replies | LLM; without it fallback text may be used |
| `OPENROUTER_MODEL` | No | Default Llama on OpenRouter |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_KEY` | Admin UI only | |
| `TTS_PROVIDER` | No | `edge` (default) |

### Frontend (`frontend/.env`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `VITE_API_BASE_URL` | **Yes** | e.g. `http://127.0.0.1:8000/api/v1` |
| `VITE_AVATAR_*` | No | Portrait / 3D avatar tuning |

**Vite rule:** Only variables prefixed with `VITE_` are visible in browser code via `import.meta.env`.

---

## 6. How frontend talks to backend

### Central client: `frontend/src/services/api.js`

```javascript
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});
```

All new endpoints should be thin wrappers:

```javascript
export const myNewCall = (userId) =>
  api.get(`/some/path/${userId}`).then((r) => r.data);
```

### Constants: `frontend/src/services/constants.js`

```javascript
export const MAX_SESSIONS = 3; // must match backend MAX_SESSIONS_PER_USER
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "...";
```

---

## 7. Authentication & session model

**There is no Bearer token / JWT for end users.**

| Concept | Where stored | How obtained |
|---------|--------------|--------------|
| User | `localStorage` key `sakoon_user` | `POST /auth/register` or `/auth/login` |
| Session | React `AppContext.currentSession` | `GET /auth/session/{userId}` |

### User object shape (frontend)

After register/login, store:

```javascript
{
  id: number,              // userId — use in all API calls
  name: string,
  languagePreference: "en" | "ur" | ...,
  totalSessions: number,
  currentSession: null,    // filled after refreshSession
}
```

### Session object shape (after `getSession` / `refreshSession`)

Backend returns snake_case; `AppContext` maps to:

```javascript
{
  id: number,              // sessionId — use in chat
  userId: number,
  sessionNo: number,
  status: "active",
  stressLevel: number,
  createdAt: string,
}
```

### Session limit

When `GET /auth/session/{userId}` returns:

```json
{
  "session": null,
  "totalSessions": 3,
  "isLimitReached": true
}
```

Show `SessionLimitBanner` (already in `ChatPage.jsx`) — do not call chat API.

---

## 8. Integration flows (step by step)

### Flow 1 — First-time user (register → chat)

```
RegisterPage
  → registerUser(name, lang)     POST /auth/register
  → setUser(...) + localStorage
  → navigate /home

User opens Chat
  → ChatPage → refreshSession()
  → getSession(user.id)          GET /auth/session/{userId}
  → setCurrentSession(session)

ChatProvider mounts
  → getChatHistory(sessionId)    GET /session/{id}/history

User sends message
  → sendMessage(userId, sessionId, text)   POST /chat/message
  → show typing delay → append assistant message
  → if isCrisis → CrisisSupportPanel
  → if suggestedExercise → show in UI / exercises page
```

### Flow 2 — Returning user

```
LoginPage → loginUser(name)      POST /auth/login
→ same as above
```

### Flow 3 — Mood dashboard

```
MoodDashboardPage
  → getMoodSummary(userId)       GET /user/{id}/mood-summary
  → getRecommendations(userId) GET /user/{id}/recommendations
```

### Flow 4 — Exercise feedback

```
ExerciseRunner
  → submitExerciseFeedback(userId, { assignmentId, sessionId, helped })
     POST /user/{id}/exercise-feedback
  → getJournalReflection({ text, language })  POST /chat/journal-reflection
```

### Flow 5 — Admin (separate route)

```
AdminDashboardPage
  → adminLogin(user, pass)       POST /admin/login  → adminKey
  → getAdminStats(adminKey)      Header: X-Admin-Key
  → getAdminCrisisAlerts(adminKey)
```

### Flow 6 — Assessment (backend ready, frontend NOT wired yet)

Backend supports full 3-session assessment. Frontend must add wrappers (see [Section 11](#11-adding-missing-apis-to-apijs)).

```
POST /assessment/profile
POST /assessment/start
GET  /assessment/next/{id}
POST /assessment/answer  (loop)
POST /assessment/scores/{userId}
GET  /assessment/result/{userId}
```

### Flow 7 — Manual mood/behavior log (backend ready, frontend NOT wired yet)

```
POST /mood/log
GET  /mood/history/{userId}
POST /mood/behavior
GET  /mood/behavior/{userId}
```

---

## 9. API ↔ Frontend file map

| Backend endpoint | Integrated? | Frontend file |
|------------------|-------------|----------------|
| `POST /auth/register` | ✅ | `RegisterPage.jsx` → `api.registerUser` |
| `POST /auth/login` | ✅ | `LoginPage.jsx` → `api.loginUser` |
| `GET /auth/session/{id}` | ✅ | `AppContext.refreshSession` |
| `POST /chat/message` | ✅ | `ChatContext.sendMessage` |
| `GET /session/{id}/history` | ✅ | `ChatContext` useEffect |
| `POST /chat/journal-reflection` | ✅ | `ExerciseRunner.jsx` |
| `GET /user/{id}/mood-summary` | ✅ | `MoodDashboardPage.jsx` |
| `GET /user/{id}/recommendations` | ✅ | `MoodDashboardPage`, `ExercisesPage` |
| `POST /user/{id}/exercise-feedback` | ✅ | `ExerciseRunner.jsx` |
| `POST /tts/speak` | ✅ | `TTSContext.jsx` (fetch blob) |
| Admin routes | ✅ | `AdminDashboardPage.jsx` |
| `POST /mood/log` | ❌ | Add to `api.js` + new UI |
| `GET /mood/history/{id}` | ❌ | Add to `api.js` |
| `POST /mood/behavior` | ❌ | Add to `api.js` |
| Assessment (8 routes) | ❌ | Add to `api.js` + wizard page |
| `GET /avatar/status` | ❌ | Optional avatar page |
| `POST /avatar/speak` | ❌ | Optional (heavy) |

---

## 10. Endpoint reference for UI developers

Base: **`${VITE_API_BASE_URL}`** = `http://127.0.0.1:8000/api/v1`

### 10.1 Register

```http
POST /auth/register
Content-Type: application/json

{
  "name": "Ali",
  "languagePreference": "en"
}
```

Response:

```json
{
  "user": {
    "id": 1,
    "name": "Ali",
    "languagePreference": "en",
    "totalSessions": 0,
    "createdAt": "2026-05-20 12:00:00"
  }
}
```

### 10.2 Login

```http
POST /auth/login
{ "name": "Ali" }
```

Same `user` shape. **404** if not found.

### 10.3 Get session

```http
GET /auth/session/1
```

Response (active):

```json
{
  "session": {
    "id": 5,
    "userId": 1,
    "sessionNo": 1,
    "status": "active",
    "stressLevel": 0,
    "createdAt": "..."
  },
  "totalSessions": 1,
  "isLimitReached": false
}
```

### 10.4 Send chat message (core)

```http
POST /chat/message

{
  "userId": 1,
  "sessionId": 5,
  "message": "I feel stressed"
}
```

Response (use these fields in UI):

| Field | UI use |
|-------|--------|
| `aiResponse` | Assistant bubble text |
| `replyLanguage` | TTS / RTL hints |
| `mhClassification` | Tags, mood chart input |
| `mhConfidence` | Optional display |
| `isCrisis` | Show `CrisisSupportPanel` |
| `helplineNumbers` | Crisis panel list |
| `suggestedExercise` | Exercise card / navigate to `/exercises` |
| `recommendations` | Compact list |
| `chatLogId` | Debugging only |

Example `suggestedExercise`:

```json
{
  "assignmentId": 46,
  "source": "library",
  "type": "breathing",
  "title": "Box Breathing",
  "durationSeconds": 192,
  "steps": [{ "text": "...", "seconds": 4, "phase": "inhale" }]
}
```

### 10.5 Chat history

```http
GET /session/5/history
```

```json
{
  "messages": [
    { "id": 50, "role": "user", "content": "...", "mhClassification": null, "timestamp": "..." },
    { "id": 50, "role": "assistant", "content": "...", "mhClassification": "Stress", "timestamp": "..." }
  ]
}
```

### 10.6 TTS

```http
POST /tts/speak
{ "text": "Hello", "language": "en" }
```

Response: **binary** `audio/mpeg` — not JSON.

Frontend pattern (`TTSContext.jsx`):

```javascript
const res = await fetch(`${API_BASE_URL}/tts/speak`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text, language }),
});
const blob = await res.blob();
const url = URL.createObjectURL(blob);
// play via <audio> or AudioContext
```

### 10.7 Admin header

```http
GET /admin/stats
X-Admin-Key: <adminKey from /admin/login>
```

---

## 11. Adding missing APIs to `api.js`

Copy this block into `frontend/src/services/api.js` when building assessment / mood features:

```javascript
// ── Mood (Phase 2) ─────────────────────────────────────────────
export const logMood = (userId, moodScore, note = null) =>
  api.post("/mood/log", { user_id: userId, mood_score: moodScore, note }).then((r) => r.data);

export const getMoodHistory = (userId, limit = 30) =>
  api.get(`/mood/history/${userId}`, { params: { limit } }).then((r) => r.data);

export const logBehavior = (userId, body) =>
  api.post("/mood/behavior", { user_id: userId, ...body }).then((r) => r.data);

export const getBehaviorHistory = (userId, limit = 30) =>
  api.get(`/mood/behavior/${userId}`, { params: { limit } }).then((r) => r.data);

// ── Assessment (Phase 2) ─────────────────────────────────────
export const saveAssessmentProfile = (body) =>
  api.post("/assessment/profile", body).then((r) => r.data);

export const getAssessmentProfile = (userId) =>
  api.get(`/assessment/profile/${userId}`).then((r) => r.data);

export const getAssessmentStatus = (userId) =>
  api.get(`/assessment/status/${userId}`).then((r) => r.data);

export const startAssessment = (userId, sessionNumber) =>
  api.post("/assessment/start", { user_id: userId, session_number: sessionNumber }).then((r) => r.data);

export const getAssessmentNextQuestion = (assessmentId) =>
  api.get(`/assessment/next/${assessmentId}`).then((r) => r.data);

export const submitAssessmentAnswer = (body) =>
  api.post("/assessment/answer", body).then((r) => r.data);

export const calculateAssessmentScores = (userId) =>
  api.post(`/assessment/scores/${userId}`).then((r) => r.data);

export const getAssessmentResult = (userId) =>
  api.get(`/assessment/result/${userId}`).then((r) => r.data);

// ── Avatar (optional) ────────────────────────────────────────
export const getAvatarStatus = () =>
  api.get("/avatar/status").then((r) => r.data);
```

### Assessment UI loop (pseudo-code)

```javascript
const { assessmentId, nextQuestion } = await startAssessment(userId, 1);

async function answerLoop(assessmentId, question) {
  if (!question) return;
  const body = question.type === "text"
    ? { assessment_id: assessmentId, question_key: question.key, answer_text: userText }
    : { assessment_id: assessmentId, question_key: question.key, answer_value: selectedValue };
  const res = await submitAssessmentAnswer(body);
  if (res.status === "session_complete") return;
  await answerLoop(assessmentId, res.nextQuestion);
}
```

Repeat for `session_number` 2 and 3, then `calculateAssessmentScores(userId)`.

---

## 12. Crisis & safety UI rules

When `POST /chat/message` returns `isCrisis: true`:

1. **Show** `CrisisSupportPanel` with `helplineNumbers` (already wired via `ChatContext.crisisDetected`).
2. **Do not** highlight breathing exercises as the main action.
3. **Do not** dismiss crisis UI without user acknowledgment.
4. Assistant text already includes grounding + helplines from backend — do not replace with generic “How can I help?”.

Backend crisis triggers: keywords + `Suicidal` class confidence ≥ 0.6.

---

## 13. TTS & avatar integration

### Current behavior

| Layer | Implementation |
|-------|----------------|
| Primary TTS | Backend `POST /tts/speak` → MP3 blob |
| Fallback | Browser `speechSynthesis` (`browserTts.js`) |
| Lip sync | `ttsLipSync.js` + avatar components |
| 3D / portrait | `VirtualAvatar.jsx`, env `VITE_AVATAR_*` |

### Passing language to TTS

Use `replyLanguage` from chat response when calling speak:

```javascript
speak(addGentleTtsPauses(aiResponse), { language: replyLanguage || user.languagePreference });
```

### Avatar video (optional, heavy)

Backend: `POST /avatar/speak` returns `video/mp4` or `audio/wav` with header `X-Avatar-Mode`.

Not used in current React app — integrate only if demo machine has Wav2Lip configured (`GET /avatar/status` → `wav2lipReady: true`).

---

## 14. Error handling standards

### Parse FastAPI errors

```javascript
function getApiError(err) {
  const d = err?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x.msg).join(", ");
  return err?.message || "Something went wrong";
}
```

### HTTP codes

| Code | Meaning | UI action |
|------|---------|-----------|
| 400 | Bad request / business rule | Show `detail` toast |
| 401 | Admin key invalid | Re-login admin |
| 404 | User / resource not found | Redirect register or show message |
| 422 | Validation | Fix form fields |
| 503 | TTS/avatar down | Fallback browser TTS |
| Network | Backend off | “Cannot reach server — is API running on :8000?” |

### Chat timeout

Chat can take **60+ seconds**. Set axios timeout if needed:

```javascript
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 min for chat only — or per-request override
});
```

---

## 15. CORS & deployment

### Development

Backend `main.py` allows `allow_origins=["*"]` — frontend on `5173` can call `8000`.

### Production checklist

| Item | Backend | Frontend |
|------|---------|----------|
| URL | Deploy API e.g. `https://api.example.com` | `VITE_API_BASE_URL=https://api.example.com/api/v1` |
| CORS | Restrict to frontend origin only | — |
| HTTPS | Required | Required |
| Secrets | Server env only | No API keys in Vite bundle |

Build frontend:

```cmd
cd frontend
npm run build
```

Output: `frontend/dist/` — serve via Nginx / Vercel / static host.

---

## 16. Testing checklist

### Manual (developer)

- [ ] Backend health: `GET /health`
- [ ] Register new user → `user.id` received
- [ ] `GET /auth/session/{id}` → `session.id`
- [ ] Send chat → `aiResponse` + optional `suggestedExercise`
- [ ] Crisis message → `isCrisis` + helplines
- [ ] Mood page loads summary + recommendations
- [ ] TTS plays (or browser fallback)
- [ ] Admin login + crisis alerts

### Scripts

```cmd
cd backend
powershell -ExecutionPolicy Bypass -File test_endpoints_manual.ps1 -SkipSlow
```

Or:

```cmd
python run_tests.py --verbose
```

---

## 17. Troubleshooting

| Problem | Cause | Fix |
|---------|--------|-----|
| Network Error in browser | Backend not running | Start uvicorn on 8000 |
| CORS error | Wrong origin / blocked | Check backend CORS; use 127.0.0.1 consistently |
| Chat always errors | Missing `mh_classifier.joblib` | `python scripts/train_model.py` |
| Empty AI reply | No `OPENROUTER_API_KEY` | Add key to `backend/.env` |
| `WinError 10013` on port 8000 | Port in use | Kill old process or use `--port 8001` and update `VITE_API_BASE_URL` |
| Session null | User limit 3 sessions | Show session limit banner |
| TTS silent | edge-tts / network | `pip install edge-tts`; use browser fallback |
| History empty | New session, no messages yet | Normal |

---

## Quick reference card (print for desk)

```
BACKEND:  cd backend && python -m uvicorn app.main:app --reload --port 8000
FRONTEND: cd frontend && npm run dev
API BASE: http://127.0.0.1:8000/api/v1
UI:       http://127.0.0.1:5173
DOCS:     http://127.0.0.1:8000/docs

USER FLOW:  register → getSession → chat/message
STORE:      localStorage sakoon_user { id, name, languagePreference }
CHAT NEEDS: userId, sessionId, message
CRISIS:     if (res.isCrisis) show helplines
EXTEND API: frontend/src/services/api.js only
```

---

## Related documents

| File | Purpose |
|------|---------|
| `backend/API_COMPLETE_TEST_DOCUMENTATION.md` | Every route, headers, JSON samples |
| `backend/TESTING_GUIDE.md` | How to run tests |
| `backend/MEETING_PRESENTATION_SCRIPT.md` | Viva talking points |
| `howtorun.txt` | Short run commands |
| `backend/PUSH_BACKEND_BRANCH.md` | Git push to `Backend_sakoon_Ai` |

---

*End of integration guide — share with any developer joining the Sakoon AI frontend team.*
