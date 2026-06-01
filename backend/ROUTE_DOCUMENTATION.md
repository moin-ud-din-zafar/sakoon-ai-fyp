# Sakoon AI — API Route Reference

**Base URL:** `http://127.0.0.1:8000`  
**API prefix:** `/api/v1`  
**Interactive docs:** `/docs`  
**Version:** 2.0.0 (`app/main.py`)

---

## System

### GET `/`
**Purpose:** API root — welcome message and link to docs  
**Auth Required:** No  

**Success Response (200):**
```json
{
  "message": "Sakoon AI API",
  "docs": "/docs"
}
```

---

### GET `/health`
**Purpose:** Health check for monitoring and test bootstrap  
**Auth Required:** No  

**Success Response (200):**
```json
{
  "status": "ok"
}
```

---

## Auth (`/api/v1/auth`)

### POST `/api/v1/auth/register`
**Purpose:** Create a new user account  
**Auth Required:** No  

**Request Body:**
```json
{
  "name": "string (required, 1–100 chars)",
  "languagePreference": "en | ur | hi | ps | sd | sk (optional, default: en)"
}
```

**Success Response (200):**
```json
{
  "user": {
    "id": 1,
    "name": "Ali Khan",
    "languagePreference": "en",
    "totalSessions": 0,
    "createdAt": "2026-05-19 12:00:00"
  }
}
```

**Error Responses:**
- **422:** Missing or invalid `name` / `languagePreference`

**Notes:** Duplicate names are allowed — each register creates a **new** `user.id`.

---

### POST `/api/v1/auth/login`
**Purpose:** Login returning user by display name  
**Auth Required:** No  

**Request Body:**
```json
{
  "name": "string (required)"
}
```

**Success Response (200):** Same shape as register `user` object.

**Error Responses:**
- **404:** `{"detail": "User not found. Please register first."}`
- **422:** Missing `name`

---

### GET `/api/v1/auth/session/{user_id}`
**Purpose:** Get active session or create next session (max 3 per user)  
**Auth Required:** No  

**Path Parameters:** `user_id` (integer)

**Success Response (200):**
```json
{
  "session": {
    "id": 5,
    "userId": 1,
    "sessionNo": 1,
    "status": "active",
    "stressLevel": 0,
    "createdAt": "2026-05-19 12:05:00"
  },
  "totalSessions": 1,
  "isLimitReached": false
}
```

**When session limit reached:**
```json
{
  "session": null,
  "totalSessions": 3,
  "isLimitReached": true
}
```

**Error Responses:**
- **404:** User not found

---

## Chat (`/api/v1/chat`)

### POST `/api/v1/chat/message`
**Purpose:** Main therapeutic chat — classify, risk check, LLM reply, exercise, logging  
**Auth Required:** No  

**Request Body:**
```json
{
  "userId": 1,
  "sessionId": 5,
  "message": "string (required)"
}
```

**Success Response (200):**
```json
{
  "aiResponse": "string",
  "replyLanguage": "en",
  "mhClassification": "Stress",
  "mhConfidence": 0.79,
  "emotionLabel": "anxious",
  "emotionConfidence": 0.0,
  "sentiment": "neutral",
  "sentimentConfidence": 0.0,
  "riskLevel": "low",
  "isCrisis": false,
  "helplineNumbers": [],
  "recommendations": [],
  "suggestedExercise": { },
  "chatLogId": 42
}
```

**Crisis example:** `isCrisis: true`, `helplineNumbers` populated, `riskLevel: "high"`.

**Empty/whitespace message:** Returns gentle prompt, `chatLogId: null`, no DB write for full pipeline.

**Error Responses:**
- **422:** Missing `userId`, `sessionId`, or `message` field

---

### POST `/api/v1/chat/journal-reflection`
**Purpose:** Short LLM reflection on coping journal text  
**Auth Required:** No  

**Request Body:**
```json
{
  "text": "string (required)",
  "language": "en (optional)"
}
```

**Success Response (200):**
```json
{
  "reflection": "2–3 line gentle reflection"
}
```

---

## Session (`/api/v1/session`)

### GET `/api/v1/session/{session_id}/history`
**Purpose:** Chat history for a session (user + assistant pairs)  
**Auth Required:** No  

**Success Response (200):**
```json
{
  "messages": [
    {
      "id": 10,
      "role": "user",
      "content": "I feel stressed.",
      "mhClassification": null,
      "timestamp": "2026-05-19T12:00:00"
    },
    {
      "id": 10,
      "role": "assistant",
      "content": "AI reply...",
      "mhClassification": "Stress",
      "timestamp": "2026-05-19T12:00:00"
    }
  ]
}
```

**Notes:** Unknown `session_id` returns **200** with `"messages": []`.

---

## User (`/api/v1/user`)

### GET `/api/v1/user/{user_id}/mood-summary`
**Purpose:** Per-session dominant MH classification and trend  
**Auth Required:** No  

**Success Response (200):**
```json
{
  "summary": [
    {
      "sessionNo": 1,
      "dominantEmotion": "Stress",
      "date": "2026-05-19"
    }
  ],
  "trend": "stable"
}
```

**Notes:** Invalid user → empty `summary`, still **200**.

---

### GET `/api/v1/user/{user_id}/recommendations`
**Purpose:** Coping exercise assignments for user  
**Auth Required:** No  

**Success Response (200):**
```json
{
  "recommendations": [
    {
      "assignmentId": 12,
      "type": "breathing",
      "title": "Box Breathing",
      "content": "Description...",
      "assignedAt": "2026-05-19T12:00:00",
      "tone": "calm",
      "durationSeconds": 180,
      "source": "library",
      "payload": { }
    }
  ]
}
```

---

### POST `/api/v1/user/{user_id}/exercise-feedback`
**Purpose:** Record whether an exercise helped; may adjust session `stress_level`  
**Auth Required:** No  

**Request Body:**
```json
{
  "assignmentId": 12,
  "sessionId": 5,
  "helped": true
}
```
All fields optional except path `user_id`.

**Success Response (200):**
```json
{
  "ok": true
}
```

**Error Responses:**
- **404:** `assignmentId` not owned by user

---

## Mood (`/api/v1/mood`)

### POST `/api/v1/mood/log`
**Purpose:** Manual mood entry (1–5 scale)  
**Auth Required:** No  

**Request Body:**
```json
{
  "user_id": 1,
  "mood_score": 4,
  "note": "optional string, max 500 chars"
}
```

**Success Response (200):**
```json
{
  "ok": true,
  "id": 3,
  "message": "Mood logged successfully."
}
```

**Error Responses:**
- **404:** User not found
- **422:** `mood_score` not in 1–5

---

### GET `/api/v1/mood/history/{user_id}`
**Purpose:** Recent mood logs  
**Auth Required:** No  

**Query:** `limit` (default 30, max 90)

**Success Response (200):**
```json
{
  "userId": 1,
  "entries": [
    {
      "id": 3,
      "moodScore": 4,
      "note": "okay",
      "loggedAt": "2026-05-19 12:00:00"
    }
  ]
}
```

---

### POST `/api/v1/mood/behavior`
**Purpose:** Daily behavior log (sleep, activity, social)  
**Auth Required:** No  

**Request Body:**
```json
{
  "user_id": 1,
  "sleep_hours": 7.5,
  "physical_activity": "none | light | moderate | intense",
  "social_interaction": "isolated | minimal | moderate | active",
  "notes": "optional"
}
```

**Success Response (200):**
```json
{
  "ok": true,
  "id": 2,
  "message": "Behavior log saved."
}
```

**Error Responses:**
- **422:** Invalid `physical_activity` or `social_interaction` value

---

### GET `/api/v1/mood/behavior/{user_id}`
**Purpose:** Behavior log history  
**Auth Required:** No  

**Success Response (200):** `{ "userId", "entries": [...] }`

---

## Assessment (`/api/v1/assessment`)

### POST `/api/v1/assessment/profile`
**Purpose:** Save/update patient intake profile  
**Auth Required:** No  

**Request Body:**
```json
{
  "user_id": 1,
  "age": 22,
  "gender": "female",
  "sleep_pattern": "irregular",
  "stress_triggers": "exams",
  "past_therapy": false,
  "medications": "none"
}
```

**Success Response (200):**
```json
{
  "ok": true,
  "message": "Profile saved."
}
```

---

### GET `/api/v1/assessment/profile/{user_id}`
**Purpose:** Retrieve intake profile  
**Success Response (200):** `{ "profile": { ... } }`

---

### GET `/api/v1/assessment/status/{user_id}`
**Purpose:** Which assessment sessions (1–3) are complete  
**Success Response (200):**
```json
{
  "completedSessions": [1, 2],
  "nextSession": 3,
  "allComplete": false,
  "resultReady": false
}
```

---

### POST `/api/v1/assessment/start`
**Purpose:** Start or resume assessment session 1, 2, or 3  
**Request Body:**
```json
{
  "user_id": 1,
  "session_number": 1
}
```

**Success Response (200):**
```json
{
  "assessmentId": 8,
  "sessionNumber": 1,
  "status": "started",
  "nextQuestion": {
    "key": "s1_current_feeling",
    "text": "...",
    "type": "text",
    "options": null,
    "questionNumber": 1,
    "totalInSession": 5
  },
  "totalQuestions": 5,
  "answeredCount": 0
}
```

**Error Responses:**
- **400:** Previous session not completed

---

### GET `/api/v1/assessment/next/{assessment_id}`
**Purpose:** Get next unanswered question  
**Success Response (200):** Includes `nextQuestion` or `status: "completed"`

---

### POST `/api/v1/assessment/answer`
**Purpose:** Submit one answer  
**Request Body:**
```json
{
  "assessment_id": 8,
  "question_key": "phq_1",
  "answer_value": 2,
  "answer_text": null
}
```
Provide **either** `answer_value` (scored items) **or** `answer_text` (open text).

**Error Responses:**
- **422:** Neither value nor text provided

---

### POST `/api/v1/assessment/scores/{user_id}`
**Purpose:** Calculate PHQ-9/GAD-7 scores after all 3 sessions complete  
**Success Response (200):**
```json
{
  "depression_score": 5,
  "anxiety_score": 3,
  "depression_severity": "mild",
  "anxiety_severity": "minimal",
  "risk_level": "low",
  "summary": "Assessment complete. PHQ-9 score: 5...",
  "recommendations": "..."
}
```

**Error Responses:**
- **400:** Sessions incomplete

---

### GET `/api/v1/assessment/result/{user_id}`
**Purpose:** Stored assessment result (camelCase fields)  
**Success Response (200):**
```json
{
  "depressionScore": 5,
  "anxietyScore": 3,
  "riskLevel": "low",
  "depressionSeverity": "mild",
  "anxietySeverity": "minimal",
  "summary": "...",
  "recommendations": "...",
  "completedAt": "2026-05-19 12:00:00"
}
```

**Error Responses:**
- **404:** No result yet

---

## TTS (`/api/v1/tts`)

### POST `/api/v1/tts/speak`
**Purpose:** Text-to-speech (Edge-TTS default)  
**Auth Required:** No  

**Request Body:**
```json
{
  "text": "Hello, I am Sakoon.",
  "language": "en",
  "voice": "en-US-JennyNeural"
}
```
`voice` and `language` optional.

**Success Response (200):** Raw **audio/mpeg** body.

**Error Responses:**
- **503:** `{"detail": "TTS unavailable..."}` if edge-tts fails

---

## Avatar (`/api/v1/avatar`)

### GET `/api/v1/avatar/status`
**Purpose:** Wav2Lip / face image / XTTS setup status  
**Success Response (200):**
```json
{
  "wav2lipReady": false,
  "wav2lipDir": "...",
  "faceImageExists": true,
  "xttsModeActive": false
}
```

---

### POST `/api/v1/avatar/speak`
**Purpose:** Talking avatar — TTS + optional Wav2Lip video  
**Request Body:**
```json
{
  "text": "Hello",
  "language": "en",
  "face_image_path": null
}
```

**Success Response (200):** `video/mp4` or `audio/wav`  
**Response Header:** `X-Avatar-Mode: video | audio`

**Error Responses:**
- **422:** Blank text
- **503:** Generation failed

---

## Admin (`/api/v1/admin`)

### POST `/api/v1/admin/login`
**Purpose:** Obtain admin API key  
**Request Body:**
```json
{
  "username": "admin",
  "password": "sakoon123"
}
```
Defaults from `.env` (`ADMIN_USERNAME`, `ADMIN_PASSWORD`).

**Success Response (200):**
```json
{
  "adminKey": "sakoon-admin-secret-change-in-prod"
}
```

**Error Responses:**
- **401:** Invalid credentials

---

### GET `/api/v1/admin/stats`
**Purpose:** Dashboard counts  
**Auth Required:** Header `X-Admin-Key: <adminKey>`

**Success Response (200):**
```json
{
  "totalSessions": 15,
  "crisisCount": 2
}
```

**Error Responses:**
- **401:** Missing/invalid key

---

### GET `/api/v1/admin/sessions`
**Purpose:** List recent sessions with user names  
**Auth Required:** `X-Admin-Key`

**Success Response (200):**
```json
{
  "sessions": [
    {
      "id": 5,
      "userId": 1,
      "userName": "Ali",
      "sessionNo": 1,
      "status": "active",
      "createdAt": "..."
    }
  ],
  "total": 1
}
```

---

### GET `/api/v1/admin/sessions/{session_id}/logs`
**Purpose:** Conversation logs for admin review  
**Auth Required:** `X-Admin-Key`  
**Success Response (200):** `{ "messages": [...] }` (same shape as user history)

---

### GET `/api/v1/admin/crisis-alerts`
**Purpose:** Recent chat logs flagged `is_crisis=1`  
**Auth Required:** `X-Admin-Key`  

**Success Response (200):**
```json
{
  "alerts": [
    {
      "sessionId": 5,
      "userId": 1,
      "userName": "Ali",
      "timestamp": "...",
      "lastMessage": "truncated...",
      "riskLevel": "high"
    }
  ]
}
```

---

*Total documented routes: **31** (2 system + 29 under `/api/v1`).*
