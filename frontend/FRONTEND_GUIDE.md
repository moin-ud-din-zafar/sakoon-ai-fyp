# Sakoon AI — Frontend Developer Guide

**Last updated:** 2026-06-02 (AppLayout container, 1050px breakpoint, console.log stubs for header buttons)  
**Stack:** React 19 · Vite 6 · Tailwind CSS v4 · React Router DOM v7 · React Icons v5 · Axios  
**Dev server:** `http://localhost:5173`  
**Backend API:** `http://127.0.0.1:8000/api/v1`

---

## Table of Contents

1. [How to Run](#1-how-to-run)
2. [Folder Structure](#2-folder-structure)
3. [Design System](#3-design-system)
4. [Routing Map](#4-routing-map)
5. [State Management](#5-state-management)
6. [API Service Layer](#6-api-service-layer)
7. [What Has Been Built](#7-what-has-been-built)
8. [What Still Needs to Be Built](#8-what-still-needs-to-be-built)
9. [Auth Flow](#9-auth-flow)
10. [Protected Routes](#10-protected-routes)
11. [Environment Variables](#11-environment-variables)
12. [Naming Conventions](#12-naming-conventions)
13. [Important Rules](#13-important-rules)

---

## 1. How to Run

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

Backend must also be running on port 8000 for API calls to work:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Build for production:

```bash
npm run build   # output → frontend/dist/
```

---

## 2. Folder Structure

```
frontend/
├── public/
├── src/
│   ├── assets/
│   │   └── images/
│   │       └── form.png              # Auth pages left-panel image
│   │
│   ├── components/
│   │   ├── ProtectedRoute.jsx        # Redirects to /login if no token
│   │   ├── GuestRoute.jsx            # Redirects to /session if already authenticated
│   │   ├── Header.jsx                # ✅ Sticky nav — route-aware actions (Session/Setting/Other), mobile menu
│   │   └── Footer.jsx                # ✅ Brand + social icons + 3 link columns + copyright
│   │
│   ├── contexts/
│   │   └── AppContext.jsx            # Global: user, session, login(), logout()
│   │
│   ├── layouts/
│   │   ├── AuthLayout.jsx            # Shared card layout for all auth pages
│   │   └── AppLayout.jsx             # ✅ Header + centered container (max-w-5xl) + Footer
│   │
│   ├── pages/
│   │   ├── RegisterPage.jsx          # ✅ Built
│   │   ├── LoginPage.jsx             # ✅ Built
│   │   ├── ForgotPasswordPage.jsx    # ✅ Built
│   │   ├── HomePage.jsx              # Deprecated — redirects to /session
│   │   ├── SessionPage.jsx           # ✅ Built (default protected page)
│   │   ├── SummaryPage.jsx           # ✅ Built — "Why Choose Sakoon AI?" static feature grid (3×2)
│   │   ├── MoodTrackerPage.jsx       # ✅ Built (placeholder)
│   │   ├── PsychoeducationPage.jsx   # ✅ Fully built — hero + filter tabs + lesson cards grid
│   │   └── SettingPage.jsx           # ✅ Fully built — preferences saved to localStorage (sakoon_preferences)
│   │
│   ├── services/
│   │   └── api.js                    # Axios instance + all API wrappers
│   │
│   ├── hooks/                        # ❌ Not built yet
│   │   ├── useSpeechRecognition.js
│   │   ├── useChat.js
│   │   ├── useTTS.js
│   │   └── useSession.js
│   │
│   ├── App.jsx                       # Routes + AppProvider wrapper
│   ├── main.jsx                      # Entry point with BrowserRouter
│   └── index.css                     # Tailwind import + custom theme
│
├── .env                              # VITE_API_BASE_URL (never commit)
├── index.html
├── package.json
├── vite.config.js
└── FRONTEND_GUIDE.md                 # This file
```

---

## 3. Design System

### Colors

Custom teal is the primary brand color. Defined in `src/index.css` via Tailwind v4 `@theme`:

```css
@theme {
  --color-primary:       #14c6be;
  --color-primary-hover: #0fb0a9;
  --color-primary-light: #e3f5f4;   /* card background tint */
}
```

Usage in JSX:

| Class | Use case |
|---|---|
| `bg-primary` | Buttons, active states |
| `hover:bg-primary-hover` | Button hover |
| `text-primary` | Links, icons, accent text |
| `bg-primary-light` | Auth card background |
| `focus-within:border-primary` | Input focus ring |

### Typography

- Headings: `font-bold text-gray-800`
- Subtitles: `text-sm text-gray-500`
- Labels: `text-sm text-gray-700`
- Links: `text-sm text-primary hover:underline`

### Input Fields

All inputs share the same pattern — icon on left, eye-toggle on right for password:

```jsx
<div className="flex items-center gap-2 border border-gray-300 rounded-lg px-3 py-2.5 focus-within:border-primary transition-colors">
  <FiMail className="text-gray-400 shrink-0" size={16} />
  <input className="flex-1 text-sm text-gray-700 outline-none bg-transparent placeholder-gray-400" />
</div>
```

### Buttons

```jsx
<button className="w-full py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors disabled:opacity-60">
```

### Error Banner

```jsx
<div className="px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
  {error}
</div>
```

---

## 4. Routing Map

| Path | Component | Protected |
|---|---|---|
| `/` | Redirects → `/session` | No |
| `/home` | Redirects → `/session` | No |
| `/login` | `LoginPage` | No |
| `/register` | `RegisterPage` | No |
| `/forgot-password` | `ForgotPasswordPage` | No |
| `/session` | `SessionPage` ⭐ default | **Yes** |
| `/summary` | `SummaryPage` | **Yes** |
| `/mood-tracker` | `MoodTrackerPage` | **Yes** |
| `/psychoeducation` | `PsychoeducationPage` | **Yes** |
| `/setting` | `SettingPage` | **Yes** |
| `*` | Redirects → `/session` | No |

Routes are defined in `src/App.jsx`. Wrap any protected page with `<ProtectedRoute>`.

---

## 5. State Management

### AppContext (`src/contexts/AppContext.jsx`)

Global state for the entire app. Wrap the app in `<AppProvider>` (already done in `App.jsx`).

```jsx
import { useApp } from "../contexts/AppContext";

const { user, currentSession, isLimitReached, login, logout } = useApp();
```

| Value | Type | Description |
|---|---|---|
| `user` | `object \| null` | `{ id, name, email, languagePreference, totalSessions }` |
| `currentSession` | `object \| null` | `{ id, userId, sessionNo, status, stressLevel }` |
| `isLimitReached` | `boolean` | True when user has used all 3 sessions |
| `login(data)` | function | Saves token + user to localStorage and state |
| `logout()` | function | Clears localStorage and resets state |
| `setCurrentSession(s)` | function | Set after `GET /auth/session` |
| `setIsLimitReached(b)` | function | Set after session fetch |

### Future contexts to build

- `ChatContext` — messages, isLoading, crisisDetected, sendMessage()
- `TTSContext` — speak(), isPlaying

---

## 6. API Service Layer

**All API calls must go through `src/services/api.js` only. Never use fetch or axios directly in components.**

### Axios instance

```js
import { api } from "../services/api";
```

- Base URL: `import.meta.env.VITE_API_BASE_URL`
- Timeout: 120 seconds (chat can take 60+ seconds)
- JWT interceptor: auto-attaches `Authorization: Bearer <token>` on every request
- 401 interceptor: auto-clears localStorage on token expiry

### Available wrappers

```js
// Auth (public)
registerUser({ name, email, password, languagePreference? })
loginUser({ email, password })
getMe()
getSession()

// Chat (JWT)
sendMessage({ userId, sessionId, message })
getChatHistory(sessionId)

// User (JWT)
getMoodSummary(userId)
getRecommendations(userId)
submitExerciseFeedback(userId, body)

// Mood (JWT)
logMood(userId, moodScore, note?)
getMoodHistory(userId, limit?)

// Admin (X-Admin-Key)
adminLogin({ username, password })
getAdminStats(adminKey)
getAdminSessions(adminKey)
getAdminCrisisAlerts(adminKey)
```

### Adding new endpoints

```js
// Pattern: thin wrapper over the axios instance
export const myNewCall = (params) =>
  api.get(`/some/path/${params}`).then((r) => r.data);
```

### Error parsing

```js
import { parseApiError } from "../services/api";

try {
  await someApiCall();
} catch (err) {
  setError(parseApiError(err)); // handles string detail, array detail, and network errors
}
```

### Token helpers

```js
import { getStoredToken, getStoredUser, setAuth, clearAuth } from "../services/api";

getStoredToken()              // string | null
getStoredUser()               // parsed user object | null
setAuth({ accessToken, user }) // saves both to localStorage
clearAuth()                   // removes both
```

---

## 7. What Has Been Built

### Auth Pages (pixel-perfect from design mockups)

#### Register Page (`/register`)
- Fields: Username (name), Email, Password (with show/hide toggle)
- Calls: `POST /auth/register`
- On success: saves token + user via `login()`, navigates to `/home`
- Error: inline red banner above form
- Links: Forgot Password, Have an account? Sign in

#### Login Page (`/login`)
- Fields: Email, Password (with show/hide toggle)
- Calls: `POST /auth/login`
- On success: saves token + user, navigates to `/home`
- Links: Forgot Password, Don't have an account? Sign Up

#### Forgot Password Page (`/forgot-password`)
- Field: Recovery email
- No backend endpoint exists yet — simulates 800ms delay, shows success message
- Back arrow navigates to previous page
- Links: Don't have an account? Sign Up

### Home Page (`/home`) — Protected, Dummy
- Shows "Hello World" + welcome message with user's name
- Logout button clears auth and redirects to `/login`
- Will be replaced with real dashboard content later

### Shared Infrastructure
- `AuthLayout.jsx` — card with `form.png` on left, white form on right; image hidden on mobile
- `ProtectedRoute.jsx` — checks `sakoon_token`, redirects to `/login` if missing
- `GuestRoute.jsx` — checks `sakoon_token`, redirects to `/home` if already authenticated (prevents back-button bypass and auto-forwards logged-in users)
- `AppContext.jsx` — global user/session state
- `api.js` — full Axios setup with JWT, error handling, and all known endpoint wrappers

---

## 8. What Still Needs to Be Built

| Page / Feature | Priority | Notes |
|---|---|---|
| `ChatPage` | High | Core feature: messages, voice input, crisis banner, session limit banner |
| `MoodDashboardPage` | High | Mood chart (Recharts), recommendations list |
| `ExercisesPage` | Medium | Exercise runner, journal reflection |
| `AdminDashboardPage` | Medium | Sessions table, crisis alerts panel (X-Admin-Key) |
| `ChatContext` | High | messages[], sendMessage(), crisisDetected, isLoading |
| `TTSContext` | Medium | POST /tts/speak → binary blob → play audio |
| `useSpeechRecognition` | Medium | Web Speech API mic wrapper |
| `useTTS` | Medium | TTS playback hook |
| `useSession` | High | Fetch + store session on app load |
| `VirtualAvatar` | Low | Lip-sync animation (optional for demo) |
| Toast/notification system | Medium | Replace inline error banners with global toast |
| Real Forgot Password | Low | Needs backend endpoint first |

---

## 9. Auth Flow

```
Register/Login
  → POST /auth/register  OR  POST /auth/login
  → save accessToken → localStorage("sakoon_token")
  → save user       → localStorage("sakoon_user")
  → AppContext.login({ accessToken, user })
  → navigate("/home")

App load (returning user)
  → AppContext reads localStorage on mount
  → user state is restored automatically

Protected page load
  → ProtectedRoute checks getStoredToken()
  → No token → redirect /login
  → Token present → render page

After login, fetch session
  → GET /auth/session  (Bearer auto-attached by interceptor)
  → AppContext.setCurrentSession(data.session)
  → AppContext.setIsLimitReached(data.isLimitReached)

Logout
  → AppContext.logout()
  → clears localStorage + state
  → navigate("/login")
```

---

## 10. Protected Routes

### ProtectedRoute — for authenticated pages

```jsx
// In App.jsx — wrap any page that requires login
<Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
```

Checks `sakoon_token` in localStorage. Redirects to `/login` with `replace` so the back button does not return to the protected page after logout.

### GuestRoute — for auth pages (login / register / forgot-password)

```jsx
// In App.jsx — wrap any page that must NOT be accessible when logged in
<Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
```

Checks `sakoon_token` in localStorage. If a token exists (user is already authenticated), redirects to `/home` immediately. This prevents authenticated users from seeing the login/register forms and ensures the app auto-redirects to home on revisit.

---

## 11. Environment Variables

File: `frontend/.env` (never commit this file)

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Only variables prefixed with `VITE_` are accessible in browser code via `import.meta.env.VITE_*`.

The axios instance in `api.js` falls back to `http://127.0.0.1:8000/api/v1` if the variable is not set.

---

## 12. Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Components / Pages / Layouts | PascalCase | `ChatPage.jsx`, `AuthLayout.jsx` |
| Hooks | camelCase + `use` prefix | `useChat.js`, `useTTS.js` |
| Context providers | PascalCase + `*Context` | `AppContext.jsx`, `ChatContext.jsx` |
| Services / utils | camelCase | `api.js`, `formatTimestamp.js` |
| Constants | UPPER_SNAKE_CASE | `MAX_SESSIONS`, `API_BASE_URL` |
| Env vars | `VITE_` prefix | `VITE_API_BASE_URL` |
| Tailwind custom classes | kebab-case | `bg-primary`, `text-primary` |

---

## 13. Important Rules

| Rule | Detail |
|---|---|
| **R1** | All API calls go in `src/services/api.js` only — never scatter `fetch` or `axios` across components |
| **R2** | Use the exported `api` axios instance — JWT header is auto-attached |
| **R3** | Chat API timeout is 120s — always show a loading/typing indicator |
| **R4** | If `isCrisis: true` in chat response → show crisis helplines, do NOT push exercises as main CTA |
| **R5** | Max 3 sessions per user — check `isLimitReached` from `AppContext` before starting chat |
| **R6** | Never commit `.env` files — use `.env.example` only |
| **R7** | `POST /tts/speak` returns binary `audio/mpeg` — use `fetch + .blob()`, not axios |
| **R8** | Chat body needs `{ userId, sessionId, message }` — must match JWT user |
| **R9** | Admin routes use `X-Admin-Key` header — not Bearer token |
| **R10** | Mood/assessment API bodies are **snake_case** — auth/chat bodies are **camelCase** |
| **R11** | Use `parseApiError(err)` from `api.js` for all error messages — handles string and array `detail` |
| **R12** | Wrap every new authenticated page in `<ProtectedRoute>` in `App.jsx` |

---

*Sakoon AI Frontend Guide — keep this file updated as new pages and features are added.*
