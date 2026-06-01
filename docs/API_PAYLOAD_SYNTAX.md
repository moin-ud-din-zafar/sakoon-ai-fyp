# Sakoon AI — API payload syntax (frontend copy-paste)

**Base URL:** `http://127.0.0.1:8000/api/v1` (prod: your `VITE_API_BASE_URL`)  
**Content-Type:** `application/json` (except TTS/avatar = binary response)

---

## Headers (har protected call par)

| Header | Value | Kab |
|--------|--------|-----|
| `Content-Type` | `application/json` | POST/PUT body ho |
| `Authorization` | `Bearer <accessToken>` | User routes (login/register ke ilawa) |
| `X-Admin-Key` | `<adminKey>` | Sirf `/admin/*` (login ke baad) |

**Axios example:**

```javascript
api.post("/chat/message", body, {
  headers: { Authorization: `Bearer ${localStorage.getItem("sakoon_token")}` },
});
```

---

## Naming rule (important)

| Area | JSON style | Example |
|------|------------|---------|
| Auth, chat, user feedback | **camelCase** | `userId`, `sessionId`, `languagePreference` |
| Mood, assessment | **snake_case** | `user_id`, `mood_score`, `session_number` |

Backend exact field names expect karta hai — neeche wahi likhe hain.

---

## 1. Auth (public — no Bearer)

### POST `/auth/register`

**Request body:**

```json
{
  "name": "Ali Khan",
  "email": "ali@example.com",
  "password": "TestPass123!",
  "languagePreference": "en"
}
```

| Field | Type | Required | Rules |
|-------|------|----------|--------|
| `name` | string | Yes | 1–100 chars |
| `email` | string | Yes | Valid email (use `@example.com` in tests, not `.local`) |
| `password` | string | Yes | Min **8** chars, max 128 |
| `languagePreference` | string | No | `en` \| `ur` \| `hi` \| `ps` \| `sd` \| `sk` (default `en`) |

**Response 200:**

```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer",
  "user": {
    "id": 1,
    "name": "Ali Khan",
    "email": "ali@example.com",
    "languagePreference": "en",
    "totalSessions": 0,
    "createdAt": "2026-06-01 16:00:00"
  }
}
```

**Errors:** `409` email exists · `422` validation

---

### POST `/auth/login`

**Request body:**

```json
{
  "email": "ali@example.com",
  "password": "TestPass123!"
}
```

**Response 200:** Same shape as register.

**Errors:** `401` invalid email/password · `422` missing fields

---

## 2. Auth (JWT required)

### GET `/auth/me`

**Body:** none  

**Response 200:**

```json
{
  "user": {
    "id": 1,
    "name": "Ali Khan",
    "email": "ali@example.com",
    "languagePreference": "en",
    "totalSessions": 1,
    "createdAt": "..."
  }
}
```

---

### GET `/auth/session`

**Body:** none  

**Response 200 (active session):**

```json
{
  "session": {
    "id": 5,
    "userId": 1,
    "sessionNo": 1,
    "status": "active",
    "stressLevel": 0,
    "createdAt": "2026-06-01 16:05:00"
  },
  "totalSessions": 1,
  "isLimitReached": false
}
```

**Response 200 (3 sessions used):**

```json
{
  "session": null,
  "totalSessions": 3,
  "isLimitReached": true
}
```

---

## 3. Chat (JWT)

### POST `/chat/message`

**Request body:**

```json
{
  "userId": 1,
  "sessionId": 5,
  "message": "I feel stressed about exams"
}
```

| Field | Type | Required |
|-------|------|----------|
| `userId` | number | Yes — must match JWT user `id` |
| `sessionId` | number | Yes — must belong to this user |
| `message` | string | Yes |

**Response 200 (main fields):**

```json
{
  "aiResponse": "I hear you...",
  "replyLanguage": "en",
  "mhClassification": "Stress",
  "mhConfidence": 0.82,
  "emotionLabel": "anxiety",
  "riskLevel": "low",
  "isCrisis": false,
  "helplineNumbers": [],
  "suggestedExercise": null,
  "recommendations": [],
  "chatLogId": 101
}
```

Crisis example: `"isCrisis": true`, `"helplineNumbers": [{ "name": "...", "number": "..." }]`

**Errors:** `401` no token · `403` wrong user/session · `422` missing field

---

### POST `/chat/journal-reflection`

**Request body:**

```json
{
  "text": "Today I tried breathing when I felt anxious.",
  "language": "en"
}
```

**Response 200:**

```json
{
  "reflection": "It sounds like you took a helpful step..."
}
```

---

## 4. Session history (JWT)

### GET `/session/{sessionId}/history`

**Body:** none  

**Response 200:**

```json
{
  "messages": [
    {
      "id": 50,
      "role": "user",
      "content": "Hello",
      "mhClassification": null,
      "timestamp": "2026-06-01 16:10:00"
    },
    {
      "id": 51,
      "role": "assistant",
      "content": "Hi, how can I help?",
      "mhClassification": "General",
      "timestamp": "2026-06-01 16:10:05"
    }
  ]
}
```

---

## 5. User (JWT)

### GET `/user/{userId}/mood-summary`

**Body:** none  

**Response 200:**

```json
{
  "summary": [
    { "sessionNo": 1, "avgMood": 3.5, "dominantClass": "Stress" }
  ],
  "trend": "stable"
}
```

---

### GET `/user/{userId}/recommendations`

**Response 200:**

```json
{
  "recommendations": [
    {
      "assignmentId": 46,
      "exerciseType": "breathing",
      "title": "Box Breathing",
      "content": "...",
      "assignedAt": "..."
    }
  ]
}
```

---

### POST `/user/{userId}/exercise-feedback`

**Request body:**

```json
{
  "assignmentId": 46,
  "sessionId": 5,
  "helped": true
}
```

All fields optional but send `assignmentId` when rating an exercise.

**Response 200:** `{ "ok": true }`

---

## 6. Mood (JWT) — snake_case body

### POST `/mood/log`

```json
{
  "user_id": 1,
  "mood_score": 4,
  "note": "Feeling better after walk"
}
```

| Field | Type | Required |
|-------|------|----------|
| `user_id` | number | Yes |
| `mood_score` | number | Yes, **1–5** |
| `note` | string | No, max 500 |

**Response 200:** `{ "ok": true, "id": 12 }`

---

### GET `/mood/history/{user_id}?limit=30`

**Response 200:**

```json
{
  "entries": [
    { "id": 1, "moodScore": 4, "note": "...", "loggedAt": "..." }
  ]
}
```

---

### POST `/mood/behavior`

```json
{
  "user_id": 1,
  "sleep_hours": 7.5,
  "physical_activity": "moderate",
  "social_interaction": "active",
  "notes": "Good day"
}
```

`physical_activity`: `none` | `light` | `moderate` | `intense`  
`social_interaction`: `isolated` | `minimal` | `moderate` | `active`

**Response 200:** `{ "ok": true, "id": 3 }`

---

## 7. Assessment (JWT) — snake_case body

### POST `/assessment/profile`

```json
{
  "user_id": 1,
  "age": 21,
  "gender": "male",
  "sleep_pattern": "irregular",
  "stress_triggers": "exams",
  "past_therapy": false,
  "medications": null
}
```

**Response 200:** `{ "ok": true, "message": "Profile saved." }`

---

### POST `/assessment/start`

```json
{
  "user_id": 1,
  "session_number": 1
}
```

`session_number`: **1**, **2**, or **3**

**Response 200:**

```json
{
  "assessmentId": 10,
  "status": "in_progress",
  "nextQuestion": {
    "key": "s1_current_feeling",
    "text": "How are you feeling?",
    "type": "text",
    "options": []
  }
}
```

---

### POST `/assessment/answer`

**Option A — numeric (PHQ/GAD style):**

```json
{
  "assessment_id": 10,
  "question_key": "phq_q1",
  "answer_value": 2,
  "answer_text": null
}
```

**Option B — text:**

```json
{
  "assessment_id": 10,
  "question_key": "s1_current_feeling",
  "answer_text": "Tired and worried",
  "answer_value": null
}
```

At least one of `answer_value` or `answer_text` required.

---

### POST `/assessment/scores/{user_id}`

**Body:** none  

**Response 200:** depression/anxiety scores object (camelCase in response).

---

### GET `/assessment/result/{user_id}`

**Response 200:**

```json
{
  "depressionScore": 8,
  "anxietyScore": 6,
  "riskLevel": "medium",
  "depressionSeverity": "mild",
  "anxietySeverity": "mild",
  "summary": "...",
  "recommendations": "...",
  "completedAt": "..."
}
```

---

## 8. TTS / Avatar (public — no JWT)

### POST `/tts/speak`

```json
{
  "text": "Hello from Sakoon",
  "language": "en"
}
```

**Response:** binary `audio/mpeg` (not JSON).

---

### POST `/admin/login` (admin only)

```json
{
  "username": "admin",
  "password": "sakoon123"
}
```

**Response 200:** `{ "adminKey": "..." }`

Then: `GET /admin/stats` with header `X-Admin-Key: <adminKey>` (not Bearer).

---

## 9. FastAPI error body

```json
{
  "detail": "Invalid email or password"
}
```

Validation `422`:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "...",
      "input": "..."
    }
  ]
}
```

**Frontend parse:**

```javascript
const d = err?.response?.data?.detail;
const message = typeof d === "string"
  ? d
  : Array.isArray(d)
    ? d.map((x) => x.msg).join(", ")
    : "Request failed";
```

---

## 10. Minimum frontend flow (payload order)

```
1. POST /auth/register  OR  POST /auth/login     → save accessToken
2. GET  /auth/session                           → save session.id
3. POST /chat/message { userId, sessionId, message }
```

---

*See also: `docs/FRONTEND_BACKEND_INTEGRATION_GUIDE.md` · `backend/AUTH_JWT_TESTING.md`*
