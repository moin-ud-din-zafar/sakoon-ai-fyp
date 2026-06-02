# Sakoon AI — Missing Backend API Endpoints

> These endpoints are required to complete the frontend but **do not exist** in the current backend.  
> All affected UI is either showing placeholder data, saving to `localStorage`, or using `console.log()` stubs.  
> Backend team needs to implement these before the respective features can be fully wired up.

**Last updated:** 2026-06-02  
**Backend base:** `http://127.0.0.1:8000/api/v1`

---

## 1. Auth & User Profile

| Method | Endpoint | Purpose | Affected UI |
|--------|----------|---------|-------------|
| `PATCH` | `/auth/profile` | Update name, languagePreference | Settings → General Preferences |
| `POST` | `/auth/change-password` | Change user password (requires current + new password) | Settings → Account → Change Password modal |
| `POST` | `/auth/forgot-password` | Send password reset link to email | Forgot Password page → Send Link button |
| `POST` | `/auth/reset-password` | Confirm reset with token + new password | (needed after forgot-password flow) |
| `POST` | `/auth/profile/avatar` | Upload user profile picture | Settings → Avatar circle (currently shows initials only) |

---

## 2. User Preferences

| Method | Endpoint | Purpose | Affected UI |
|--------|----------|---------|-------------|
| `POST` | `/user/{userId}/preferences` | Save avatar look, voice style, personality traits, cultural adaptation | Settings → Avatar & Preferences + General Preferences (currently localStorage only) |
| `GET` | `/user/{userId}/preferences` | Load saved preferences on login | Settings page (currently reads from localStorage only) |

**Request body for POST:**
```json
{
  "avatarLook": "Professional",
  "voiceStyle": "Warm & Empathetic",
  "personalityTraits": "Calm, analytical...",
  "culturalAdaptation": "Global Standard"
}
```

---

## 3. Session Management

| Method | Endpoint | Purpose | Affected UI |
|--------|----------|---------|-------------|
| `POST` | `/session/{sessionId}/end` | Explicitly end/complete a session | Header → End Session button (currently just logs out) |
| `POST` | `/session/{sessionId}/save` | Save session state/notes | Header → Save Session button (currently console.log) |
| `POST` | `/session/{sessionId}/share` | Generate shareable session summary | Header → Share button (currently console.log) |

---

## 4. Psychoeducation

> The entire Psychoeducation section has no backend support. All lesson data is currently hardcoded in the frontend.

| Method | Endpoint | Purpose | Affected UI |
|--------|----------|---------|-------------|
| `GET` | `/psychoeducation/lessons` | List all lessons with pagination | Psychoeducation page → lesson cards (currently hardcoded array) |
| `GET` | `/psychoeducation/lessons?category={cat}` | Filter lessons by category | Psychoeducation page → filter tabs |
| `GET` | `/psychoeducation/lesson/{lessonId}` | Get full lesson content | Lesson detail page (not built yet) |
| `GET` | `/psychoeducation/categories` | List available categories | Filter tabs (currently hardcoded) |
| `POST` | `/psychoeducation/user/{userId}/progress` | Mark lesson as started/completed | Start button on cards |
| `GET` | `/psychoeducation/user/{userId}/progress` | Get user's lesson progress | Lesson cards (to show completion status) |

**Lesson object shape needed:**
```json
{
  "id": 1,
  "title": "Understanding Anxiety",
  "description": "...",
  "category": "Anxiety",
  "difficulty": "Beginner",
  "durationMinutes": 15,
  "exerciseCount": 1,
  "videoUrl": "https://...",
  "imageUrl": "https://...",
  "tags": ["Anxiety", "Beginner"]
}
```

---

## 5. Admin Dashboard

### 5.1 Analytics / Stats

| Method | Endpoint | Purpose | Affected UI |
|--------|----------|---------|-------------|
| `GET` | `/admin/analytics` | Total users, completed sessions, new signups last 30 days, active sessions | Admin → Stats cards (currently only `totalSessions` and `crisisCount` from `/admin/stats`) |

**Expected response:**
```json
{
  "totalUsers": 7890,
  "activeSessions": 1234,
  "completedSessions": 4567,
  "newSignupsLast30Days": 89,
  "crisisCount": 2
}
```

### 5.2 User Management

| Method | Endpoint | Purpose | Affected UI |
|--------|----------|---------|-------------|
| `GET` | `/admin/users` | List all users with pagination | Admin → View All Users |
| `PATCH` | `/admin/users/{userId}/role` | Update user role | Admin → Manage Roles |
| `PATCH` | `/admin/users/{userId}/status` | Activate / deactivate account | Admin → Deactivate Accounts |
| `GET` | `/admin/feedback` | List all user feedback | Admin → User Feedback |

### 5.3 Content Management

| Method | Endpoint | Purpose | Affected UI |
|--------|----------|---------|-------------|
| `POST` | `/admin/lessons` | Create a new psychoeducation lesson | Admin → Add New Lesson |
| `GET` | `/admin/lessons` | List all lessons | Admin → Manage Categories |
| `PUT` | `/admin/lessons/{id}` | Edit lesson content | Admin → lesson edit |
| `DELETE` | `/admin/lessons/{id}` | Delete a lesson | Admin → lesson delete |
| `GET` | `/admin/categories` | List lesson categories | Admin → Manage Categories |
| `POST` | `/admin/categories` | Add new category | Admin → Manage Categories |
| `GET` | `/admin/submissions` | List pending content submissions | Admin → Review Submissions |
| `PATCH` | `/admin/submissions/{id}` | Approve / reject submission | Admin → Review Submissions |
| `GET` | `/admin/psychoeducation-settings` | Get psychoeducation module settings | Admin → Psychoeducation Settings |
| `PUT` | `/admin/psychoeducation-settings` | Update psychoeducation settings | Admin → Psychoeducation Settings |

---

## 6. Mood Tracker Page

> Core mood logging APIs exist. These are enhancements needed for a richer dashboard.

| Method | Endpoint | Purpose | Affected UI |
|--------|----------|---------|-------------|
| `GET` | `/mood/trends/{userId}` | Aggregated mood trends over time (weekly/monthly) | Mood Tracker → line chart (currently derived from history entries) |
| `DELETE` | `/mood/log/{id}` | Delete a mood log entry | Mood Tracker → history list (no delete button yet) |
| `GET` | `/mood/habits/{userId}` | Habit completion data (water, read, call etc.) | Mood Tracker → Habit Completion chart (currently static placeholder) |

---

## 7. Summary

| Category | Missing Endpoints | Priority |
|----------|-------------------|----------|
| Auth / Profile | 5 | High |
| User Preferences | 2 | High |
| Session Management | 3 | Medium |
| Psychoeducation | 6 | High |
| Admin Analytics | 1 | High |
| Admin User Mgmt | 4 | Medium |
| Admin Content Mgmt | 9 | Medium |
| Mood Tracker | 2 | Low |
| **Total** | **32** | — |

---

## What IS already implemented (for reference)

| Endpoint | Status |
|----------|--------|
| `POST /auth/register` | ✅ Working |
| `POST /auth/login` | ✅ Working |
| `GET /auth/me` | ✅ Working |
| `GET /auth/session` | ✅ Working |
| `POST /chat/message` | ✅ Working |
| `POST /chat/journal-reflection` | ✅ Working |
| `GET /session/{id}/history` | ✅ Working |
| `GET /user/{id}/mood-summary` | ✅ Working |
| `GET /user/{id}/recommendations` | ✅ Working |
| `POST /user/{id}/exercise-feedback` | ✅ Working |
| `POST /mood/log` | ✅ Working |
| `GET /mood/history/{id}` | ✅ Working |
| `POST /mood/behavior` | ✅ Working |
| `GET /mood/behavior/{id}` | ✅ Working |
| `POST /assessment/profile` | ✅ Working |
| `POST /assessment/start` | ✅ Working |
| `GET /assessment/next/{id}` | ✅ Working |
| `POST /assessment/answer` | ✅ Working |
| `POST /assessment/scores/{id}` | ✅ Working |
| `GET /assessment/result/{id}` | ✅ Working |
| `POST /tts/speak` | ✅ Working |
| `GET /avatar/status` | ✅ Working |
| `POST /admin/login` | ✅ Working |
| `GET /admin/stats` | ✅ Working |
| `GET /admin/sessions` | ✅ Working |
| `GET /admin/sessions/{id}/logs` | ✅ Working |
| `GET /admin/crisis-alerts` | ✅ Working |

---

*Share this file with the backend team before starting frontend work on the affected sections.*
