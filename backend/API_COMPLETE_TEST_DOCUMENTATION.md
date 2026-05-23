# Sakoon AI — Complete API Test Documentation

**Project:** Sakoon AI Virtual Mental Health Assistant  
**Backend version:** 2.0.0 (`app/main.py`)  
**Document purpose:** Manual testing, viva demonstration, and FYP evidence — every route with headers, request bodies, response JSON, and error cases.

---

## Table of contents

1. [Base URL and setup](#1-base-url-and-setup)  
2. [Common HTTP headers](#2-common-http-headers)  
3. [Authentication model](#3-authentication-model)  
4. [Endpoint index (31 routes)](#4-endpoint-index-31-routes)  
5. [System routes](#5-system-routes)  
6. [Auth routes](#6-auth-routes)  
7. [Chat routes](#7-chat-routes)  
8. [Session routes](#8-session-routes)  
9. [User routes](#9-user-routes)  
10. [Mood routes](#10-mood-routes)  
11. [Assessment routes](#11-assessment-routes)  
12. [TTS routes](#12-tts-routes)  
13. [Avatar routes](#13-avatar-routes)  
14. [Admin routes](#14-admin-routes)  
15. [Assessment question keys reference](#15-assessment-question-keys-reference)  
16. [MH classification and crisis rules](#16-mh-classification-and-crisis-rules)  
17. [End-to-end test flows](#17-end-to-end-test-flows)  
18. [PowerShell and cURL examples](#18-powershell-and-curl-examples)  

**Related files:** `TESTING_GUIDE.md` (how to run), `ROUTE_DOCUMENTATION.md` (shorter reference), `api_tester.html` (browser UI).

---

## 1. Base URL and setup

| Item | Value |
|------|--------|
| Base URL | `http://127.0.0.1:8000` |
| API prefix | `/api/v1` |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |
| HTML tester | Serve `backend/api_tester.html` via `python -m http.server 5500` |

**Start server:**

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Prerequisites:**

- `pip install -r requirements.txt`
- `python scripts/train_model.py` → `backend/models/*.joblib`
- `.env`: `USE_SQLITE=true` (easy) or MySQL credentials
- Optional: `OPENROUTER_API_KEY` for live LLM replies

---

## 2. Common HTTP headers

| Header | When required | Value |
|--------|----------------|-------|
| `Content-Type` | All `POST` with JSON body | `application/json` |
| `Accept` | Optional | `application/json` (default for JSON endpoints) |
| `X-Admin-Key` | Admin routes **except** `/admin/login` | Value from `POST /admin/login` → `adminKey` (matches `ADMIN_KEY` in `.env`) |

**No JWT / Bearer token** for normal users. The client sends `userId` and `sessionId` in request bodies after register/login.

**Binary responses** (no JSON):

| Endpoint | Success `Content-Type` | Extra response headers |
|----------|------------------------|-------------------------|
| `POST /api/v1/tts/speak` | `audio/mpeg` | — |
| `POST /api/v1/avatar/speak` | `video/mp4` or `audio/wav` | `X-Avatar-Mode: video` \| `audio` |

---

## 3. Authentication model

| Actor | How identified | Protected routes |
|-------|----------------|------------------|
| End user | `user.id` from register/login; `session.id` from `/auth/session/{userId}` | None (trust client IDs — prototype only) |
| Admin | `X-Admin-Key` header after password login | `/admin/stats`, `/admin/sessions`, `/admin/sessions/{id}/logs`, `/admin/crisis-alerts` |

**Default admin credentials** (`.env`): `ADMIN_USERNAME=admin`, `ADMIN_PASSWORD=sakoon123`

---

## 4. Endpoint index (31 routes)

| # | Method | Full path | Auth |
|---|--------|-----------|------|
| 1 | GET | `/` | No |
| 2 | GET | `/health` | No |
| 3 | POST | `/api/v1/auth/register` | No |
| 4 | POST | `/api/v1/auth/login` | No |
| 5 | GET | `/api/v1/auth/session/{user_id}` | No |
| 6 | POST | `/api/v1/chat/message` | No |
| 7 | POST | `/api/v1/chat/journal-reflection` | No |
| 8 | GET | `/api/v1/session/{session_id}/history` | No |
| 9 | GET | `/api/v1/user/{user_id}/mood-summary` | No |
| 10 | GET | `/api/v1/user/{user_id}/recommendations` | No |
| 11 | POST | `/api/v1/user/{user_id}/exercise-feedback` | No |
| 12 | POST | `/api/v1/mood/log` | No |
| 13 | GET | `/api/v1/mood/history/{user_id}` | No |
| 14 | POST | `/api/v1/mood/behavior` | No |
| 15 | GET | `/api/v1/mood/behavior/{user_id}` | No |
| 16 | POST | `/api/v1/assessment/profile` | No |
| 17 | GET | `/api/v1/assessment/profile/{user_id}` | No |
| 18 | GET | `/api/v1/assessment/status/{user_id}` | No |
| 19 | POST | `/api/v1/assessment/start` | No |
| 20 | GET | `/api/v1/assessment/next/{assessment_id}` | No |
| 21 | POST | `/api/v1/assessment/answer` | No |
| 22 | POST | `/api/v1/assessment/scores/{user_id}` | No |
| 23 | GET | `/api/v1/assessment/result/{user_id}` | No |
| 24 | POST | `/api/v1/tts/speak` | No |
| 25 | GET | `/api/v1/avatar/status` | No |
| 26 | POST | `/api/v1/avatar/speak` | No |
| 27 | POST | `/api/v1/admin/login` | No |
| 28 | GET | `/api/v1/admin/stats` | `X-Admin-Key` |
| 29 | GET | `/api/v1/admin/sessions` | `X-Admin-Key` |
| 30 | GET | `/api/v1/admin/sessions/{session_id}/logs` | `X-Admin-Key` |
| 31 | GET | `/api/v1/admin/crisis-alerts` | `X-Admin-Key` |

---

## 5. System routes

### 5.1 GET `/`

| Field | Value |
|-------|--------|
| **Purpose** | API welcome |
| **Headers** | None required |

**Response 200:**

```json
{
  "message": "Sakoon AI API",
  "docs": "/docs"
}
```

---

### 5.2 GET `/health`

| Field | Value |
|-------|--------|
| **Purpose** | Health check (use before all tests) |
| **Headers** | None required |

**Response 200:**

```json
{
  "status": "ok"
}
```

---

## 6. Auth routes

Prefix: `/api/v1/auth`

### 6.1 POST `/api/v1/auth/register`

| Field | Value |
|-------|--------|
| **Purpose** | Create new user |
| **Headers** | `Content-Type: application/json` |

**Request body:**

```json
{
  "name": "Ali Khan",
  "languagePreference": "en"
}
```

| Field | Type | Required | Values |
|-------|------|----------|--------|
| `name` | string | Yes | 1–100 characters |
| `languagePreference` | string | No (default `en`) | `en`, `ur`, `hi`, `ps`, `sd`, `sk` |

**Response 200 (example — verified):**

```json
{
  "user": {
    "id": 17,
    "name": "viva_demo_user",
    "languagePreference": "en",
    "totalSessions": 0,
    "createdAt": "2026-05-20 01:16:00"
  }
}
```

**Errors:**

| Status | Body |
|--------|------|
| 422 | Pydantic validation (missing `name`, invalid language) |

**Notes:** Same display name can register multiple times; each gets a new `id`.

---

### 6.2 POST `/api/v1/auth/login`

| Field | Value |
|-------|--------|
| **Purpose** | Find existing user by name |
| **Headers** | `Content-Type: application/json` |

**Request body:**

```json
{
  "name": "Ali Khan"
}
```

**Response 200:** Same `user` object shape as register.

**Errors:**

| Status | Body |
|--------|------|
| 404 | `{"detail": "User not found. Please register first."}` |
| 422 | Missing `name` |

---

### 6.3 GET `/api/v1/auth/session/{user_id}`

| Field | Value |
|-------|--------|
| **Purpose** | Get active session or create next (max **3** sessions per user — `MAX_SESSIONS_PER_USER`) |
| **Headers** | None |
| **Path** | `user_id` — integer |

**Response 200 — session available (example — verified):**

```json
{
  "session": {
    "id": 11,
    "userId": 17,
    "sessionNo": 1,
    "status": "active",
    "stressLevel": 0,
    "createdAt": "2026-05-20 01:16:12"
  },
  "totalSessions": 1,
  "isLimitReached": false
}
```

**Response 200 — limit reached:**

```json
{
  "session": null,
  "totalSessions": 3,
  "isLimitReached": true
}
```

**Errors:**

| Status | Body |
|--------|------|
| 404 | User not found |

---

## 7. Chat routes

Prefix: `/api/v1/chat`

### 7.1 POST `/api/v1/chat/message`

| Field | Value |
|-------|--------|
| **Purpose** | Full pipeline: MH classify → risk → emotion/sentiment → LLM → exercise → DB log |
| **Headers** | `Content-Type: application/json` |
| **Typical duration** | 2–45 s (OpenRouter + first HF model load) |

**Request body:**

```json
{
  "userId": 17,
  "sessionId": 11,
  "message": "I feel stressed about my exams and cannot sleep"
}
```

| Field | Type | Required |
|-------|------|----------|
| `userId` | integer | Yes |
| `sessionId` | integer | Yes |
| `message` | string | Yes (may be whitespace — see empty case) |

**Response 200 — normal chat (example — verified):**

```json
{
  "aiResponse": "Like everything's demanding something from you at once…\nWhat's the one stress that's loudest today?",
  "replyLanguage": "en",
  "mhClassification": "Stress",
  "mhConfidence": 0.8771557790620038,
  "emotionLabel": "neutral",
  "emotionConfidence": 0.0,
  "sentiment": "neutral",
  "sentimentConfidence": 0.0,
  "riskLevel": "low",
  "isCrisis": false,
  "helplineNumbers": [],
  "recommendations": [
    {
      "type": "breathing",
      "title": "Box Breathing",
      "content": "Even counts in a square — steadying when everything feels loud."
    }
  ],
  "suggestedExercise": {
    "assignmentId": 44,
    "source": "library",
    "id": "stress-box",
    "type": "breathing",
    "title": "Box Breathing",
    "tone": "calm",
    "durationSeconds": 192,
    "description": "Even counts in a square — steadying when everything feels loud.",
    "repeatCount": 4,
    "prompt": null,
    "steps": [
      { "text": "Inhale for 4 counts.", "seconds": 4, "phase": "inhale" },
      { "text": "Hold for 4 counts.", "seconds": 4, "phase": "hold" },
      { "text": "Exhale for 4 counts.", "seconds": 4, "phase": "exhale" },
      { "text": "Hold empty for 4 counts.", "seconds": 4, "phase": "hold" }
    ]
  },
  "chatLogId": 46
}
```

**Response field reference:**

| Field | Description |
|-------|-------------|
| `aiResponse` | Therapeutic reply from OpenRouter (or fallback if no API key) |
| `replyLanguage` | `en`, `ur`, etc. |
| `mhClassification` | One of 7 MH classes (see §16) |
| `mhConfidence` | 0.0–1.0 from TF-IDF + LogisticRegression |
| `emotionLabel` | From HF emotion model or keyword merge |
| `emotionConfidence` | HF confidence (0 if model failed) |
| `sentiment` / `sentimentConfidence` | HF sentiment pipeline |
| `riskLevel` | `low`, `medium`, `high` |
| `isCrisis` | `true` → helplines + no exercise |
| `helplineNumbers` | Array of `{name, number}` when crisis |
| `recommendations` | Compact list for UI cards |
| `suggestedExercise` | Full exercise payload or `null` in crisis |
| `chatLogId` | DB primary key in `chat_logs` |

**Response 200 — crisis (example — verified):**

```json
{
  "aiResponse": "That's a lot to be holding right now…\nOne slow breath out. Feet on the floor if you can.\nWhen you're able, these lines are there:\n\n- Umang Pakistan: 0311-7786264\n- PMHW: 1020\n- Sehat Tahaffuz: 1166",
  "replyLanguage": "en",
  "mhClassification": "Suicidal",
  "mhConfidence": 0.9393291178100853,
  "emotionLabel": "distressed",
  "emotionConfidence": 0.0,
  "sentiment": "neutral",
  "sentimentConfidence": 0.0,
  "riskLevel": "high",
  "isCrisis": true,
  "helplineNumbers": [
    { "name": "Umang Pakistan", "number": "0311-7786264" },
    { "name": "PMHW", "number": "1020" },
    { "name": "Sehat Tahaffuz", "number": "1166" }
  ],
  "recommendations": [],
  "suggestedExercise": null,
  "chatLogId": 47
}
```

**Test message for crisis:** `"I have been thinking about suicide and want to end my life"`

**Response 200 — empty / whitespace message:**

```json
{
  "aiResponse": "No rush… when a thought's ready, you can share it.",
  "replyLanguage": "en",
  "mhClassification": "Normal",
  "mhConfidence": 0.0,
  "emotionLabel": "neutral",
  "riskLevel": "low",
  "isCrisis": false,
  "helplineNumbers": [],
  "recommendations": [],
  "suggestedExercise": null,
  "chatLogId": null
}
```

(Urdu preference users get Roman Urdu empty prompt.)

**Errors:**

| Status | Cause |
|--------|--------|
| 422 | Invalid JSON / missing fields |
| 500 | Missing `mh_classifier.joblib` — run `train_model.py` |

---

### 7.2 POST `/api/v1/chat/journal-reflection`

| Field | Value |
|-------|--------|
| **Purpose** | 2–3 line LLM reflection on journal text |
| **Headers** | `Content-Type: application/json` |

**Request body:**

```json
{
  "text": "Today I tried breathing when I felt overwhelmed.",
  "language": "en"
}
```

| Field | Required | Default |
|-------|----------|---------|
| `text` | Yes | — |
| `language` | No | `en` |

**Response 200:**

```json
{
  "reflection": "string — gentle 2–3 line reflection"
}
```

**Response 200 — empty text:**

```json
{
  "reflection": ""
}
```

---

## 8. Session routes

### 8.1 GET `/api/v1/session/{session_id}/history`

| Field | Value |
|-------|--------|
| **Purpose** | Chat transcript (user + assistant rows) |
| **Headers** | None |

**Response 200 (example — verified):**

```json
{
  "messages": [
    {
      "id": 46,
      "role": "user",
      "content": "I feel stressed about my exams and cannot sleep",
      "mhClassification": null,
      "timestamp": "2026-05-20 01:17:11"
    },
    {
      "id": 46,
      "role": "assistant",
      "content": "Like everything's demanding something from you at once…\nWhat's the one stress that's loudest today?",
      "mhClassification": "Stress",
      "timestamp": "2026-05-20 01:17:11"
    }
  ]
}
```

**Notes:** Unknown `session_id` → **200** with `"messages": []`. User and assistant share the same `id` (chat_log id).

---

## 9. User routes

Prefix: `/api/v1/user`

### 9.1 GET `/api/v1/user/{user_id}/mood-summary`

**Response 200 (example — verified):**

```json
{
  "summary": [
    {
      "sessionNo": 1,
      "dominantEmotion": "Stress",
      "date": "2026-05-20"
    }
  ],
  "trend": "stable"
}
```

`trend` values: `improving`, `worsening`, `stable` (from `personalization_service.compute_trend`).

---

### 9.2 GET `/api/v1/user/{user_id}/recommendations`

**Response 200 (shape):**

```json
{
  "recommendations": [
    {
      "assignmentId": 44,
      "type": "breathing",
      "title": "Box Breathing",
      "content": "Even counts in a square — steadying when everything feels loud.",
      "assignedAt": "2026-05-20T01:17:11",
      "tone": "calm",
      "durationSeconds": 192,
      "source": "library",
      "payload": {
        "id": "stress-box",
        "type": "breathing",
        "title": "Box Breathing",
        "titleUrdu": "Box saans",
        "tone": "calm",
        "durationSeconds": 192,
        "description": "...",
        "descriptionUrdu": "...",
        "repeatCount": 4,
        "steps": [],
        "source": "library"
      }
    }
  ]
}
```

---

### 9.3 POST `/api/v1/user/{user_id}/exercise-feedback`

| Field | Value |
|-------|--------|
| **Headers** | `Content-Type: application/json` |
| **Path** | `user_id` |

**Request body (all body fields optional):**

```json
{
  "assignmentId": 44,
  "sessionId": 11,
  "helped": true
}
```

**Response 200:**

```json
{
  "ok": true
}
```

**Errors:**

| Status | Body |
|--------|------|
| 404 | `{"detail": "Assignment not found"}` — wrong `assignmentId` for user |

---

## 10. Mood routes

Prefix: `/api/v1/mood`

### 10.1 POST `/api/v1/mood/log`

**Headers:** `Content-Type: application/json`

**Request body:**

```json
{
  "user_id": 17,
  "mood_score": 3,
  "note": "okay day"
}
```

| Field | Type | Required | Constraint |
|-------|------|----------|------------|
| `user_id` | int | Yes | Must exist |
| `mood_score` | int | Yes | 1–5 (1 = very low, 5 = very good) |
| `note` | string | No | max 500 chars |

**Response 200 (verified):**

```json
{
  "ok": true,
  "id": 8,
  "message": "Mood logged successfully."
}
```

**Errors:** 404 user not found; 422 invalid `mood_score`

---

### 10.2 GET `/api/v1/mood/history/{user_id}`

**Query parameters:**

| Param | Default | Max |
|-------|---------|-----|
| `limit` | 30 | 90 |

**Response 200:**

```json
{
  "userId": 17,
  "entries": [
    {
      "id": 8,
      "moodScore": 3,
      "note": "okay day",
      "loggedAt": "2026-05-20 01:18:00"
    }
  ]
}
```

---

### 10.3 POST `/api/v1/mood/behavior`

**Request body:**

```json
{
  "user_id": 17,
  "sleep_hours": 6.5,
  "physical_activity": "light",
  "social_interaction": "moderate",
  "notes": "Went for a short walk"
}
```

| Field | Allowed values |
|-------|----------------|
| `physical_activity` | `none`, `light`, `moderate`, `intense` |
| `social_interaction` | `isolated`, `minimal`, `moderate`, `active` |

**Response 200:**

```json
{
  "ok": true,
  "id": 2,
  "message": "Behavior log saved."
}
```

**Errors:** 422 if activity/social value not in allowed set

---

### 10.4 GET `/api/v1/mood/behavior/{user_id}`

**Query:** `limit` (default 30, max 90)

**Response 200:**

```json
{
  "userId": 17,
  "entries": [
    {
      "id": 2,
      "sleepHours": 6.5,
      "physicalActivity": "light",
      "socialInteraction": "moderate",
      "notes": "Went for a short walk",
      "loggedAt": "2026-05-20 01:20:00"
    }
  ]
}
```

---

## 11. Assessment routes

Prefix: `/api/v1/assessment`  
**3 sessions:** 1 = intake, 2 = PHQ-9 + GAD-7, 3 = behavioral/lifestyle

### 11.1 POST `/api/v1/assessment/profile`

**Request body:**

```json
{
  "user_id": 17,
  "age": 22,
  "gender": "male",
  "sleep_pattern": "irregular",
  "stress_triggers": "exams, family",
  "past_therapy": false,
  "medications": "none"
}
```

**Response 200 (verified):**

```json
{
  "ok": true,
  "message": "Profile saved."
}
```

---

### 11.2 GET `/api/v1/assessment/profile/{user_id}`

**Response 200:**

```json
{
  "profile": {
    "id": 1,
    "user_id": 17,
    "age": 22,
    "gender": "male",
    "sleep_pattern": "irregular",
    "stress_triggers": "exams, family",
    "past_therapy": 0,
    "medications": "none",
    "created_at": "2026-05-20 01:18:00",
    "updated_at": "2026-05-20 01:18:00"
  }
}
```

If no profile: `"profile": null`

---

### 11.3 GET `/api/v1/assessment/status/{user_id}`

**Response 200:**

```json
{
  "completedSessions": [1],
  "nextSession": 2,
  "allComplete": false,
  "resultReady": false
}
```

When all 3 done: `"allComplete": true`, `"nextSession": null`

---

### 11.4 POST `/api/v1/assessment/start`

**Request body:**

```json
{
  "user_id": 17,
  "session_number": 1
}
```

`session_number`: **1**, **2**, or **3** (must complete previous session first)

**Response 200 (verified):**

```json
{
  "assessmentId": 14,
  "sessionNumber": 1,
  "status": "started",
  "nextQuestion": {
    "key": "s1_current_feeling",
    "text": "In a few words, how would you describe how you've been feeling lately?",
    "type": "text",
    "options": null,
    "questionNumber": 1,
    "totalInSession": 5,
    "isCrisisFlag": false
  },
  "totalQuestions": 5,
  "answeredCount": 0
}
```

**Errors:** 400 if previous session not complete; 404 user not found

---

### 11.5 GET `/api/v1/assessment/next/{assessment_id}`

**Response 200 — in progress:**

```json
{
  "assessmentId": 14,
  "sessionNumber": 1,
  "status": "in_progress",
  "nextQuestion": {
    "key": "s1_main_concern",
    "text": "What is the main concern that brought you here today?",
    "type": "text",
    "options": null,
    "questionNumber": 2,
    "totalInSession": 5,
    "isCrisisFlag": false
  },
  "totalQuestions": 5,
  "answeredCount": 1
}
```

**Response 200 — session finished:**

```json
{
  "status": "completed",
  "nextQuestion": null
}
```

---

### 11.6 POST `/api/v1/assessment/answer`

**Request body — text question:**

```json
{
  "assessment_id": 14,
  "question_key": "s1_current_feeling",
  "answer_value": null,
  "answer_text": "I have been feeling low and tired"
}
```

**Request body — scored PHQ/GAD (0–3):**

```json
{
  "assessment_id": 14,
  "question_key": "phq_1",
  "answer_value": 2,
  "answer_text": null
}
```

**Frequency scale for PHQ-9 / GAD-7:**

| `answer_value` | Label |
|----------------|--------|
| 0 | Not at all |
| 1 | Several days |
| 2 | More than half the days |
| 3 | Nearly every day |

**Response 200 — more questions remain:**

```json
{
  "assessmentId": 14,
  "sessionNumber": 1,
  "status": "in_progress",
  "nextQuestion": { "key": "s1_main_concern", "text": "...", "type": "text", "options": null, "questionNumber": 2, "totalInSession": 5, "isCrisisFlag": false },
  "totalQuestions": 5,
  "answeredCount": 1
}
```

**Response 200 — session complete:**

```json
{
  "assessmentId": 14,
  "sessionNumber": 1,
  "status": "session_complete",
  "nextQuestion": null,
  "totalQuestions": 5,
  "answeredCount": 5,
  "message": "Thank you for sharing. We'll now move to a brief clinical check-in."
}
```

**Errors:**

| Status | Body |
|--------|------|
| 422 | Neither `answer_value` nor `answer_text` provided |
| 400 | Invalid question key / assessment state |

---

### 11.7 POST `/api/v1/assessment/scores/{user_id}`

**Purpose:** Calculate PHQ-9 + GAD-7 after **all 3 sessions** complete.

**Headers:** None (no body)

**Response 200:**

```json
{
  "depression_score": 8,
  "anxiety_score": 5,
  "depression_severity": "mild",
  "anxiety_severity": "mild",
  "risk_level": "low",
  "summary": "Assessment complete. PHQ-9 score: 8 (mild). GAD-7 score: 5 (mild). ...",
  "recommendations": "Consider regular sleep schedule and ..."
}
```

**Errors:**

| Status | Body |
|--------|------|
| 400 | `Sessions [2, 3] are not yet complete. Finish all 3 sessions first.` |

---

### 11.8 GET `/api/v1/assessment/result/{user_id}`

**Response 200 (camelCase):**

```json
{
  "depressionScore": 8,
  "anxietyScore": 5,
  "riskLevel": "low",
  "depressionSeverity": "mild",
  "anxietySeverity": "mild",
  "summary": "Assessment complete...",
  "recommendations": "Consider regular sleep...",
  "completedAt": "2026-05-20 02:00:00"
}
```

**Errors:** 404 `No result found. Complete all 3 assessment sessions first.`

---

## 12. TTS routes

### 12.1 POST `/api/v1/tts/speak`

**Headers:** `Content-Type: application/json`

**Request body:**

```json
{
  "text": "Hello, I am Sakoon.",
  "language": "en",
  "voice": "en-US-AriaNeural"
}
```

| Field | Required |
|-------|----------|
| `text` | Yes |
| `language` | No — maps to Edge-TTS voice |
| `voice` | No — overrides language default |

**Response 200:** Binary **audio/mpeg** (not JSON). Save response body to `.mp3`.

**Response 503:**

```json
{
  "detail": "TTS unavailable. Install edge-tts and ensure it works."
}
```

---

## 13. Avatar routes

### 13.1 GET `/api/v1/avatar/status`

**Response 200 (example — verified):**

```json
{
  "wav2lipReady": true,
  "wav2lipDir": "E:\\Ai Virtual Assistant\\wav2lip",
  "wav2lipCheckpoint": "E:\\Ai Virtual Assistant\\wav2lip\\checkpoints\\wav2lip_gan.pth",
  "faceImage": "E:\\Ai Virtual Assistant\\frontend\\public\\avatars\\face.jpg",
  "faceImageExists": true,
  "checkpointExists": true,
  "wav2lipInferenceExists": true,
  "xttsModeActive": false
}
```

---

### 13.2 POST `/api/v1/avatar/speak`

**Headers:** `Content-Type: application/json`

**Request body:**

```json
{
  "text": "Hello, I am here with you.",
  "language": "en",
  "face_image_path": null
}
```

| Field | Max length |
|-------|------------|
| `text` | 1000 chars |

**Response 200:** Binary `video/mp4` or `audio/wav`  
**Response header:** `X-Avatar-Mode: video` | `audio`

**Errors:**

| Status | Body |
|--------|------|
| 422 | Blank `text` |
| 503 | Generation failed |

---

## 14. Admin routes

Prefix: `/api/v1/admin`

### 14.1 POST `/api/v1/admin/login`

**Request body:**

```json
{
  "username": "admin",
  "password": "sakoon123"
}
```

**Response 200 (verified):**

```json
{
  "adminKey": "sakoon-admin-secret-change-in-prod"
}
```

**Errors:** 401 `Invalid username or password`

---

### 14.2 GET `/api/v1/admin/stats`

**Headers:**

```
X-Admin-Key: sakoon-admin-secret-change-in-prod
```

**Response 200 (verified):**

```json
{
  "totalSessions": 11,
  "crisisCount": 3
}
```

**Errors:** 401 `Invalid or missing admin key`

---

### 14.3 GET `/api/v1/admin/sessions`

**Headers:** `X-Admin-Key: <adminKey>`

**Response 200:**

```json
{
  "sessions": [
    {
      "id": 11,
      "userId": 17,
      "userName": "viva_demo_user",
      "sessionNo": 1,
      "status": "active",
      "createdAt": "2026-05-20 01:16:12"
    }
  ],
  "total": 1
}
```

---

### 14.4 GET `/api/v1/admin/sessions/{session_id}/logs`

**Headers:** `X-Admin-Key: <adminKey>`

**Response 200:** Same `messages` array as §8.1

---

### 14.5 GET `/api/v1/admin/crisis-alerts`

**Headers:** `X-Admin-Key: <adminKey>`

**Response 200 (verified):**

```json
{
  "alerts": [
    {
      "sessionId": 11,
      "userId": 17,
      "userName": "viva_demo_user",
      "timestamp": "2026-05-20T01:18:25",
      "lastMessage": "I have been thinking about suicide and want to end my life",
      "riskLevel": "high"
    }
  ]
}
```

---

## 15. Assessment question keys reference

### Session 1 — Intake (5 questions)

| Key | Type | Answer |
|-----|------|--------|
| `s1_current_feeling` | text | `answer_text` |
| `s1_main_concern` | text | `answer_text` |
| `s1_duration` | select | `answer_value` 0–3 |
| `s1_support` | select | `answer_value` 0–2 |
| `s1_initial_mood` | scale | `answer_value` 1–10 |

### Session 2 — Clinical (16 questions)

**PHQ-9:** `phq_1` … `phq_9` — each `answer_value` 0–3  
**GAD-7:** `gad_1` … `gad_7` — each `answer_value` 0–3  
**Crisis flag on:** `phq_9` (`isCrisisFlag: true` in question object)

### Session 3 — Behavioral (7 questions)

| Key |
|-----|
| `b_sleep` |
| `b_exercise` |
| `b_social` |
| `b_substance` |
| `b_self_care` |
| `b_hope` |
| `b_coping` |

All use `answer_value` per option labels in `assessment_service.py`.

---

## 16. MH classification and crisis rules

### MH classes (`mhClassification`)

`Normal`, `Stress`, `Anxiety`, `Depression`, `Suicidal`, `Bipolar`, `Personality disorder`

### Crisis triggers

1. **Keywords** in message (`app/core/constants.py`): e.g. `suicide`, `kill myself`, `want to die`, `end my life`, …  
2. **ML:** `Suicidal` class with confidence ≥ **0.6** (`CRISIS_THRESHOLD`)

### Helplines (returned when `isCrisis: true`)

| Name | Number |
|------|--------|
| Umang Pakistan | 0311-7786264 |
| PMHW | 1020 |
| Sehat Tahaffuz | 1166 |

---

## 17. End-to-end test flows

### Flow A — New user journey

| Step | Method | Path | Save |
|------|--------|------|------|
| 1 | POST | `/api/v1/auth/register` | `userId` |
| 2 | GET | `/api/v1/auth/session/{userId}` | `sessionId` |
| 3 | POST | `/api/v1/chat/message` × 3 | `chatLogId` |
| 4 | GET | `/api/v1/session/{sessionId}/history` | — |
| 5 | POST | `/api/v1/mood/log` | — |
| 6 | POST | `/api/v1/mood/behavior` | — |
| 7 | GET | `/api/v1/user/{userId}/recommendations` | — |

### Flow B — Full assessment

| Step | Action |
|------|--------|
| 1 | Register + session |
| 2 | `POST /assessment/profile` |
| 3 | `POST /assessment/start` session 1 → loop `GET /next/{id}` + `POST /answer` until `session_complete` |
| 4 | Repeat for `session_number: 2` and `3` |
| 5 | `POST /assessment/scores/{userId}` |
| 6 | `GET /assessment/result/{userId}` |

### Flow C — Crisis

| Step | Action |
|------|--------|
| 1 | Register + session |
| 2 | `POST /chat/message` with crisis text |
| 3 | Verify `isCrisis`, `helplineNumbers` |
| 4 | `GET /admin/crisis-alerts` with `X-Admin-Key` |

### Flow D — Admin

| Step | Action |
|------|--------|
| 1 | `POST /admin/login` → `adminKey` |
| 2 | `GET /admin/stats` with header |
| 3 | `GET /admin/sessions` |
| 4 | `GET /admin/sessions/{sessionId}/logs` |
| 5 | `GET /admin/stats` **without** header → expect **401** |

### Flow E — TTS / Avatar

| Step | Action |
|------|--------|
| 1 | `GET /avatar/status` |
| 2 | `POST /tts/speak` → save MP3 |
| 3 | `POST /avatar/speak` → save MP4 or WAV |

---

## 18. PowerShell and cURL examples

### Health

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

```bash
curl -s http://127.0.0.1:8000/health
```

### Register → Session → Chat

```powershell
$base = "http://127.0.0.1:8000/api/v1"
$reg = Invoke-RestMethod -Method POST -Uri "$base/auth/register" -ContentType "application/json" -Body '{"name":"test_doc","languagePreference":"en"}'
$uid = $reg.user.id
$sess = Invoke-RestMethod -Uri "$base/auth/session/$uid"
$sid = $sess.session.id
Invoke-RestMethod -Method POST -Uri "$base/chat/message" -ContentType "application/json" -Body (@{userId=$uid;sessionId=$sid;message="I feel anxious"} | ConvertTo-Json)
```

### Admin with header

```powershell
$admin = Invoke-RestMethod -Method POST -Uri "$base/admin/login" -ContentType "application/json" -Body '{"username":"admin","password":"sakoon123"}'
Invoke-RestMethod -Uri "$base/admin/stats" -Headers @{"X-Admin-Key"=$admin.adminKey}
```

### Assessment answer

```powershell
Invoke-RestMethod -Method POST -Uri "$base/assessment/answer" -ContentType "application/json" -Body '{"assessment_id":14,"question_key":"s1_current_feeling","answer_text":"low and tired"}'
```

---

## HTTP status code summary

| Code | Meaning in this API |
|------|---------------------|
| 200 | Success (including empty history) |
| 400 | Business rule (assessment order, incomplete sessions) |
| 401 | Admin key missing/invalid |
| 404 | User, assignment, assessment result not found |
| 422 | Validation (Pydantic, mood score, assessment answer) |
| 503 | TTS or avatar generation unavailable |
| 500 | Unhandled server error (e.g. missing ML models) |

---

*Document generated for Sakoon AI backend testing. Examples marked **verified** were captured from a live run on 2026-05-20 against `http://127.0.0.1:8000`.*
