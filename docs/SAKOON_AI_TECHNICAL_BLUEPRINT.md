# Sakoon AI — Complete Technical Blueprint

> **A Virtual AI Therapist for Inclusive Mental Health Support**  
> Professional-grade technical design for a Final Year Project — single developer, production-ready architecture.

---

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [System Architecture](#2-system-architecture)
3. [AI Pipeline](#3-ai-pipeline)
4. [State Management](#4-state-management)
5. [Data Flows](#5-data-flows)
6. [Database Schema](#6-database-schema)
7. [Backend API Design](#7-backend-api-design)
8. [Frontend Component Architecture](#8-frontend-component-architecture)
9. [Project Folder Structure](#9-project-folder-structure)
10. [Development Roadmap](#10-development-roadmap)
11. [Crisis Detection & Escalation](#11-crisis-detection--escalation)
12. [Scalability Design](#12-scalability-design)

---

## 1. Naming Conventions

### 1.1 Frontend (React)

| Item | Convention | Example |
|------|------------|---------|
| **Components** | PascalCase | `ChatInterface`, `VoiceInput`, `MoodChart` |
| **Component files** | PascalCase | `ChatInterface.jsx`, `VoiceInput.jsx` |
| **Hooks** | camelCase, `use` prefix | `useSpeechRecognition`, `useChat` |
| **Context providers** | PascalCase, `*Context` suffix | `AppContext`, `ChatContext` |
| **Custom hooks files** | camelCase | `useSpeechRecognition.js` |
| **Pages** | PascalCase | `HomePage.jsx`, `ChatPage.jsx` |
| **Utilities** | camelCase | `formatTimestamp`, `parseMoodData` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_SESSIONS`, `API_BASE_URL` |
| **CSS/Tailwind** | kebab-case for classes | `chat-message-user`, `voice-btn-active` |
| **Environment variables** | VITE_ prefix | `VITE_API_BASE_URL` |

### 1.2 Backend (Python/FastAPI)

| Item | Convention | Example |
|------|------------|---------|
| **Modules/packages** | snake_case | `preprocess.py`, `risk_detector.py` |
| **Classes** | PascalCase | `MentalHealthClassifier`, `RiskDetector` |
| **Functions** | snake_case | `predict_emotion`, `load_model` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_SESSIONS_PER_USER`, `CRISIS_THRESHOLD` |
| **API routes** | snake_case path segments | `/api/chat/message`, `/api/user/{user_id}` |
| **Pydantic models** | PascalCase | `ChatRequest`, `ChatResponse` |
| **Environment variables** | UPPER_SNAKE_CASE | `GROQ_API_KEY`, `DATABASE_URL` |

### 1.3 Database (MySQL)

| Item | Convention | Example |
|------|------------|---------|
| **Tables** | snake_case, plural | `users`, `chat_logs`, `emotion_history` |
| **Columns** | snake_case | `user_id`, `created_at`, `is_crisis` |
| **Primary keys** | `id` | `id INT PRIMARY KEY AUTO_INCREMENT` |
| **Foreign keys** | `{table_singular}_id` | `user_id`, `session_id` |
| **Indexes** | `idx_{table}_{column(s)}` | `idx_chat_logs_session_id` |

---

## 2. System Architecture

### 2.1 Decoupled Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER (React)                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ ChatPage    │ │ VoiceInput  │ │ VirtualAvatar│ │ MoodDashboard          │ │
│  │ ChatInterface│ │ VoiceOutput │ │ LipSyncSim   │ │ MoodChart              │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP (Axios)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND LOGIC LAYER (FastAPI)                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ Auth Router │ │ Chat Router │ │ Session Mgr │ │ Admin Router            │ │
│  │ Middleware  │ │ Dependencies│ │ Validation  │ │ CORS, Error Handler     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ Internal calls
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AI INTELLIGENCE LAYER (Python Services)                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ MH Classifier│ │ Risk Detector│ │ LLM Service  │ │ Personalization Eng  │ │
│  │ (Scikit-learn)│ │ (Rules+ML)   │ │ (Groq/Llama) │ │ (Mood History)       │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ MySQL Connector
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATA STORAGE LAYER (MySQL)                             │
│  users | sessions | chat_logs | emotion_history | assignments | admin_users   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Layer Responsibilities

| Layer | Responsibility | No Business Logic In |
|-------|----------------|----------------------|
| **Presentation** | Render UI, capture user input, display responses | API logic, ML inference |
| **Backend Logic** | Validate requests, orchestrate services, return responses | ML training, raw DB queries in routes |
| **AI Intelligence** | Classification, risk detection, LLM generation, personalization | HTTP handling, UI |
| **Data Storage** | Persist and retrieve data | Application logic |

---

## 3. AI Pipeline

### 3.1 Pipeline Stages (Sequential)

```
Voice Input → Speech Recognition → Text Preprocessing → MH Classification
     → Emotion Detection → Risk Detection → LLM Response → TTS Output
```

| Stage | Location | Technology | Input | Output |
|-------|----------|------------|-------|--------|
| 1. Voice Input | Frontend | Web Speech API (mic) | User speech | Raw audio stream |
| 2. Speech Recognition | Frontend | `SpeechRecognition` | Audio | Transcript (string) |
| 3. Text Preprocessing | Backend | Custom + regex | Raw text | Cleaned text |
| 4. MH Classification | Backend | TF-IDF + SVM/LogReg | Cleaned text | Class + confidence |
| 5. Emotion Detection | Backend | Keywords + sentiment | Text + class | Emotion label |
| 6. Risk Detection | Backend | Rules + classifier | Text + class + prob | risk_level, is_crisis |
| 7. LLM Response | Backend | Groq API (Llama 3) | Prompt + context | AI response text |
| 8. TTS Output | Backend → Frontend | Edge-TTS / API | Response text | Audio URL / stream |

### 3.2 Mental Health Classification Model

**Dataset:** `Dataset/Combined Data.csv` (~94k rows)

**Columns:** `statement` (text), `status` (label)

**Classes (7):**
- `Normal` | `Stress` | `Anxiety` | `Depression` | `Suicidal` | `Bipolar` | `Personality disorder`

**Training Flow:**
1. Load CSV → DataFrame
2. Preprocess: lowercase, remove URLs, trim whitespace, optional Roman Urdu normalization
3. Split: 80% train, 20% validation (stratified)
4. Vectorize: TfidfVectorizer(ngram_range=(1,3), max_features=15000)
5. Classify: LinearSVC or LogisticRegression with class_weight='balanced'
6. Evaluate: F1-macro, precision/recall per class, confusion matrix
7. Save: `mh_classifier.joblib`, `tfidf_vectorizer.joblib` via Joblib

**Inference:** Load once at startup; `classifier.predict_proba(vectorizer.transform([text]))` → top class + score.

### 3.3 Affective Computing (MVP)

**Phase 1 (MVP):** Transcript-only. Emotion inferred from text + MH classification.

**Phase 2 (Optional):** Client-side Web Audio API:
- Compute pitch (F0), speech rate (syllables/sec), energy (RMS)
- Send JSON: `{ transcript, pitchMean, speechRate, energy }`
- Backend weights: low pitch + slow rate → sadness; high pitch + fast → anxiety

---

## 4. State Management

### 4.1 Architecture: React Context + Local State

```
┌─────────────────────────────────────────────────────────────────────────┐
│ AppContext (Global)                                                      │
│ • user: { id, name, languagePreference, totalSessions }                  │
│ • currentSession: { id, sessionNo, status }                              │
│ • isSessionLimitReached: boolean                                        │
│ • setUser, setCurrentSession, refreshSession                            │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │ provides
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ChatContext (Scoped to ChatPage)                                         │
│ • messages: Message[]                                                    │
│ • isLoading: boolean                                                      │
│ • crisisDetected: boolean                                                │
│ • sendMessage(text), addMessage(msg)                                      │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │ uses
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ useSpeechRecognition (Hook - Local State)                                │
│ • isListening: boolean                                                   │
│ • transcript: string                                                     │
│ • startListening(), stopListening()                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 State Ownership Rules

| State | Owner | Scope | Persistence |
|-------|-------|-------|-------------|
| User profile | AppContext | Global | localStorage + DB |
| Current session | AppContext | Global | DB |
| Chat messages | ChatContext | ChatPage | DB (fetched on load) |
| Voice transcript | useSpeechRecognition | Component | None (ephemeral) |
| Crisis banner visibility | ChatContext | ChatPage | Derived from API response |
| Mood chart data | MoodDashboard | Page | Fetched from API |

### 4.3 Data Flow Summary

1. **User registers** → `POST /api/auth/register` → `AppContext.setUser`
2. **User starts chat** → `GET /api/auth/session/{userId}` → `AppContext.setCurrentSession`
3. **User sends message** → `POST /api/chat/message` → Response → `ChatContext.addMessage` + TTS
4. **Crisis detected** → Response `risk_level: 'HIGH'` → `ChatContext.crisisDetected = true` → Show `CrisisBanner`

---

## 5. Data Flows

### 5.1 Send Message Flow (End-to-End)

```
User speaks → [VoiceInput] startListening()
     → Web Speech API onresult → transcript
     → [ChatInterface] onSubmit(transcript)
     → [ChatContext] sendMessage(transcript)
     → POST /api/chat/message { userId, sessionId, message }
     → Backend: preprocess → classify → risk check → personalization → LLM
     → Response { aiResponse, mhClassification, riskLevel, isCrisis, recommendations }
     → [ChatContext] addMessage(userMsg), addMessage(aiMsg)
     → [VoiceOutput] optional: fetch TTS and play
     → [VirtualAvatar] animate lip-sync
```

### 5.2 Session Limit Flow

```
[AppContext] on mount / session fetch
     → GET /api/auth/session/{userId}
     → Response { session, totalSessions, isLimitReached }
     → If isLimitReached → show SessionLimitBanner
     → Prevent new session creation; suggest professional help
```

### 5.3 Crisis Escalation Flow

```
[Backend] risk_detector.check(text, classification, probability)
     → If rule match OR suicidal prob > 0.6 → is_crisis = True
     → LLM prompt variant: crisis_support_prompt + helpline
     → Response { ..., riskLevel: 'HIGH', isCrisis: true, helplineNumbers: [...] }
     → [Frontend] ChatContext.crisisDetected = true
     → [CrisisBanner] visible with helpline info
     → [ChatLogs] row with is_crisis = 1
     → [Admin] crisis-alerts surfaced
```

---

## 6. Database Schema

### 6.1 Entity-Relationship

```
Users ──< Sessions ──< ChatLogs
  │           │
  │           └──< EmotionHistory
  │
  └──< Assignments

AdminUsers (separate, for dashboard auth)
```

### 6.2 Full MySQL Schema

```sql
-- Users
CREATE TABLE users (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL,
    language_preference VARCHAR(10) DEFAULT 'en',
    total_sessions  INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_language (language_preference)
);

-- Sessions
CREATE TABLE sessions (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    session_no      INT NOT NULL,
    status          ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    stress_level    INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_sessions_user_session (user_id, session_no),
    INDEX idx_sessions_user (user_id),
    INDEX idx_sessions_status (status),
    INDEX idx_sessions_created (created_at)
);

-- Chat Logs
CREATE TABLE chat_logs (
    id                  INT PRIMARY KEY AUTO_INCREMENT,
    session_id           INT NOT NULL,
    user_message         TEXT NOT NULL,
    ai_response          TEXT NOT NULL,
    mh_classification    VARCHAR(50),
    mh_confidence        FLOAT,
    emotion_label        VARCHAR(50),
    risk_level           ENUM('low', 'medium', 'high') DEFAULT 'low',
    is_crisis            TINYINT(1) DEFAULT 0,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    INDEX idx_chat_logs_session (session_id),
    INDEX idx_chat_logs_crisis (is_crisis),
    INDEX idx_chat_logs_created (created_at)
);

-- Emotion History (per message or per session aggregate)
CREATE TABLE emotion_history (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    session_id      INT NOT NULL,
    emotion_label   VARCHAR(50) NOT NULL,
    confidence      FLOAT,
    recorded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    INDEX idx_emotion_session (session_id),
    INDEX idx_emotion_recorded (recorded_at)
);

-- Assignments (Coping exercises recommended to user)
CREATE TABLE assignments (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT NOT NULL,
    exercise_type   VARCHAR(50) NOT NULL,
    content         TEXT,
    assigned_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed       TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_assignments_user (user_id),
    INDEX idx_assignments_completed (completed)
);

-- Admin Users (simple auth for dashboard)
CREATE TABLE admin_users (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Backend API Design

### 7.1 API Base

- **Base URL:** `http://localhost:8000` (dev) / `https://api.sakoon.ai` (prod)
- **Prefix:** `/api/v1`
- **Content-Type:** `application/json`
- **Auth:** Session/user ID in body or path (MVP; no JWT initially)

### 7.2 Endpoints & Contracts

#### POST `/api/v1/auth/register`

**Request:**
```json
{
  "name": "string (required)",
  "languagePreference": "en | ur"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "name": "Ali",
    "languagePreference": "en",
    "totalSessions": 0,
    "createdAt": "2025-03-12T10:00:00Z"
  }
}
```

---

#### GET `/api/v1/auth/session/{user_id}`

**Response (200):**
```json
{
  "session": {
    "id": 1,
    "userId": 1,
    "sessionNo": 1,
    "status": "active",
    "stressLevel": 0,
    "createdAt": "2025-03-12T10:00:00Z"
  },
  "totalSessions": 1,
  "isLimitReached": false
}
```

---

#### POST `/api/v1/chat/message`

**Request:**
```json
{
  "userId": 1,
  "sessionId": 1,
  "message": "string (required)"
}
```

**Response (200):**
```json
{
  "aiResponse": "string",
  "mhClassification": "Anxiety",
  "mhConfidence": 0.85,
  "emotionLabel": "anxious",
  "riskLevel": "low",
  "isCrisis": false,
  "helplineNumbers": [],
  "recommendations": [
    {
      "type": "breathing",
      "title": "4-7-8 Breathing",
      "content": "Breathe in for 4 sec..."
    }
  ],
  "chatLogId": 42
}
```

---

#### GET `/api/v1/session/{session_id}/history`

**Response (200):**
```json
{
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "...",
      "timestamp": "2025-03-12T10:01:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "...",
      "mhClassification": "Anxiety",
      "timestamp": "2025-03-12T10:01:05Z"
    }
  ]
}
```

---

#### GET `/api/v1/user/{user_id}/mood-summary`

**Response (200):**
```json
{
  "summary": [
    { "sessionNo": 1, "dominantEmotion": "Anxiety", "date": "2025-03-12" },
    { "sessionNo": 2, "dominantEmotion": "Normal", "date": "2025-03-13" }
  ],
  "trend": "improving"
}
```

---

#### GET `/api/v1/user/{user_id}/recommendations`

**Response (200):**
```json
{
  "recommendations": [
    {
      "type": "breathing",
      "title": "4-7-8 Breathing",
      "content": "...",
      "assignedAt": "2025-03-12T10:00:00Z"
    }
  ]
}
```

---

#### GET `/api/v1/admin/sessions` (Admin)

**Headers:** `X-Admin-Key: <secret>`

**Response (200):**
```json
{
  "sessions": [
    {
      "id": 1,
      "userId": 1,
      "userName": "Ali",
      "sessionNo": 1,
      "status": "active",
      "createdAt": "2025-03-12T10:00:00Z"
    }
  ],
  "total": 100
}
```

---

#### GET `/api/v1/admin/crisis-alerts` (Admin)

**Response (200):**
```json
{
  "alerts": [
    {
      "sessionId": 5,
      "userId": 2,
      "userName": "Sara",
      "timestamp": "2025-03-12T11:00:00Z",
      "lastMessage": "...",
      "riskLevel": "high"
    }
  ]
}
```

---

## 8. Frontend Component Architecture

### 8.1 Component Hierarchy

```
App
├── AppProvider (AppContext)
├── Router
│   ├── HomePage
│   │   ├── Header
│   │   ├── HeroSection
│   │   ├── FeatureCards
│   │   └── Footer
│   │
│   ├── ChatPage
│   │   ├── ChatProvider (ChatContext)
│   │   ├── Header
│   │   ├── SessionLimitBanner (conditional)
│   │   ├── ChatLayout
│   │   │   ├── VirtualAvatar
│   │   │   │   └── LipSyncOverlay
│   │   │   ├── MessageList
│   │   │   │   └── MessageBubble (reusable)
│   │   │   └── ChatInput
│   │   │       ├── TextInput
│   │   │       └── VoiceInput (uses useSpeechRecognition)
│   │   ├── CrisisBanner (conditional)
│   │   └── VoiceOutput (hidden, plays TTS)
│   │
│   ├── MoodDashboardPage
│   │   ├── Header
│   │   ├── MoodChart (Recharts)
│   │   └── RecommendationCards
│   │
│   └── AdminDashboardPage (protected)
│       ├── AdminHeader
│       ├── SessionsTable
│       ├── CrisisAlertsPanel
│       └── EmotionalStatsChart
│
└── Layout (optional: shared nav)
```

### 8.2 Reusable Components

| Component | Props | Purpose |
|-----------|-------|---------|
| `Button` | variant, size, onClick, disabled | Primary, secondary, danger |
| `Input` | value, onChange, placeholder, type | Text input |
| `Card` | title, children, className | Container card |
| `MessageBubble` | role, content, timestamp | User vs assistant bubble |
| `LoadingSpinner` | size | Loading indicator |
| `Modal` | isOpen, onClose, children | Dialog overlay |
| `Banner` | variant (warning/success), message, onDismiss | Alert banner |

### 8.3 Hooks

| Hook | Returns | Purpose |
|------|---------|---------|
| `useSpeechRecognition` | `{ isListening, transcript, startListening, stopListening, error }` | Web Speech API wrapper |
| `useChat` | `{ messages, sendMessage, isLoading, crisisDetected }` | Chat API + state |
| `useTTS` | `{ speak, isPlaying }` | Text-to-speech playback |
| `useSession` | `{ session, totalSessions, isLimitReached, refresh }` | Session state |

---

## 9. Project Folder Structure

### 9.1 Complete Structure

```
sakoon-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app, CORS, routers
│   │   ├── config.py                  # Settings, env vars
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # get_db, get_classifier, get_llm
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py            # register, get_or_create_session
│   │   │       ├── chat.py            # send_message
│   │   │       ├── session.py         # history
│   │   │       ├── user.py            # mood-summary, recommendations
│   │   │       └── admin.py           # sessions, crisis-alerts
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── constants.py           # MAX_SESSIONS, CRISIS_KEYWORDS
│   │   │   └── exceptions.py          # Custom HTTPException handlers
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py             # Pydantic: ChatRequest, ChatResponse
│   │   │   └── db_models.py           # SQLAlchemy ORM (optional) or raw SQL
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── classifier_service.py  # MH classification
│   │   │   ├── risk_detector_service.py
│   │   │   ├── llm_service.py        # Groq API
│   │   │   ├── tts_service.py        # Edge-TTS
│   │   │   ├── personalization_service.py
│   │   │   └── db_service.py         # CRUD operations
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── preprocess.py          # text cleaning, Roman Urdu norm
│   │       └── text_utils.py          # helpers
│   │
│   ├── models/                        # Serialized ML artifacts (git LFS or .gitignore)
│   │   ├── mh_classifier.joblib
│   │   └── tfidf_vectorizer.joblib
│   │
│   ├── scripts/
│   │   ├── train_model.py             # Train classifier from Combined Data.csv
│   │   ├── seed_db.py                 # Seed tables
│   │   └── run_migrations.py          # Optional: Alembic
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_classifier.py
│   │   ├── test_risk_detector.py
│   │   └── test_api.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Input.jsx
│   │   │   │   ├── Card.jsx
│   │   │   │   ├── LoadingSpinner.jsx
│   │   │   │   ├── Modal.jsx
│   │   │   │   ├── Banner.jsx
│   │   │   │   └── index.js
│   │   │   │
│   │   │   ├── chat/
│   │   │   │   ├── ChatInterface.jsx
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   ├── MessageList.jsx
│   │   │   │   ├── MessageBubble.jsx
│   │   │   │   ├── SessionLimitBanner.jsx
│   │   │   │   ├── CrisisBanner.jsx
│   │   │   │   └── index.js
│   │   │   │
│   │   │   ├── voice/
│   │   │   │   ├── VoiceInput.jsx
│   │   │   │   ├── VoiceOutput.jsx
│   │   │   │   └── index.js
│   │   │   │
│   │   │   ├── avatar/
│   │   │   │   ├── VirtualAvatar.jsx
│   │   │   │   └── LipSyncOverlay.jsx
│   │   │   │
│   │   │   └── mood/
│   │   │       ├── MoodChart.jsx
│   │   │       ├── RecommendationCard.jsx
│   │   │       └── index.js
│   │   │
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── MoodDashboardPage.jsx
│   │   │   ├── AdminDashboardPage.jsx
│   │   │   └── index.js
│   │   │
│   │   ├── contexts/
│   │   │   ├── AppContext.jsx
│   │   │   └── ChatContext.jsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useSpeechRecognition.js
│   │   │   ├── useChat.js
│   │   │   ├── useTTS.js
│   │   │   └── useSession.js
│   │   │
│   │   ├── services/
│   │   │   ├── api.js                 # Axios instance, endpoints
│   │   │   └── constants.js           # API_BASE_URL, MAX_SESSIONS
│   │   │
│   │   ├── utils/
│   │   │   ├── formatTimestamp.js
│   │   │   └── storage.js             # localStorage helpers
│   │   │
│   │   └── styles/
│   │       └── index.css              # Tailwind imports, globals
│   │
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── Dataset/
│   ├── Combined Data.csv
│   └── Readme.md
│
├── docs/
│   ├── SAKOON_AI_TECHNICAL_BLUEPRINT.md
│   └── API.md                         # API reference (optional)
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
```

### 9.2 Folder Descriptions

| Folder | Purpose |
|--------|---------|
| `backend/app/api/routes` | FastAPI route handlers; thin layer, delegate to services |
| `backend/app/core` | App-wide config, constants, exception handling |
| `backend/app/models` | Pydantic request/response, DB models |
| `backend/app/services` | Business logic, AI inference, external API calls |
| `backend/app/utils` | Pure helpers (preprocess, text utils) |
| `frontend/src/components/common` | Reusable UI primitives |
| `frontend/src/components/chat` | Chat-specific UI |
| `frontend/src/contexts` | React Context providers |
| `frontend/src/hooks` | Custom hooks |
| `frontend/src/services` | API client, config |

---

## 10. Development Roadmap

### Phase 1: Research & Dataset (Week 1–2)

| Task | Deliverable |
|------|-------------|
| Load & explore Combined Data.csv | EDA notebook / summary |
| Define train/val split (stratified) | Split files or indices |
| Preprocessing pipeline | `preprocess.py` with tests |
| Class distribution analysis | Document imbalance strategy |

### Phase 2: AI Model (Week 3–4)

| Task | Deliverable |
|------|-------------|
| Train TF-IDF + classifier | `train_model.py` |
| Evaluate (F1-macro, confusion matrix) | Metrics report |
| Save model + vectorizer | `.joblib` files |
| Risk keyword list + rules | `risk_detector_service.py` |
| Integrate classifier in FastAPI | Load at startup, predict endpoint |

### Phase 3: Backend (Week 5–7)

| Task | Deliverable |
|------|-------------|
| FastAPI project setup | `main.py`, config |
| MySQL schema creation | SQL script / migrations |
| Auth routes (register, session) | Working endpoints |
| Chat route + full pipeline | Classify → risk → LLM → store |
| User/session/mood endpoints | API complete |
| Admin routes | Sessions, crisis alerts |
| TTS integration (Edge-TTS) | Optional: TTS endpoint or client-side |

### Phase 4: Frontend UI (Week 8–9)

| Task | Deliverable |
|------|-------------|
| Vite + React + Tailwind setup | Project scaffold |
| Routing (React Router) | Home, Chat, Mood, Admin |
| AppContext + ChatContext | State management |
| HomePage, ChatPage layout | Static UI |
| ChatInterface, MessageList, ChatInput | Chat UI |
| MoodChart (Recharts) | Mood dashboard |
| Admin dashboard (tables, crisis panel) | Admin UI |

### Phase 5: Voice Integration (Week 10–11)

| Task | Deliverable |
|------|-------------|
| useSpeechRecognition hook | Web Speech API |
| VoiceInput component | Mic button, transcript to chat |
| TTS playback (Edge-TTS API or frontend) | VoiceOutput |
| VirtualAvatar + lip-sync simulation | CSS animation |
| CrisisBanner, SessionLimitBanner | Conditional UI |

### Phase 6: Testing & Deployment (Week 12–13)

| Task | Deliverable |
|------|-------------|
| Backend unit tests | pytest |
| API integration tests | Test client |
| Frontend smoke tests | Manual / Playwright |
| Dockerfile (backend) | Container |
| docker-compose (backend + MySQL) | Local stack |
| Documentation | README, API docs |

**Total: ~12–13 weeks**

---

## 11. Crisis Detection & Escalation

### 11.1 Detection Logic

```python
# Pseudocode
def check_risk(text: str, classification: str, confidence: float) -> dict:
    is_crisis = False
    risk_level = "low"

    # Rule-based
    CRISIS_KEYWORDS = ["kill myself", "end my life", "suicide", "want to die", ...]
    if any(kw in text.lower() for kw in CRISIS_KEYWORDS):
        is_crisis = True
        risk_level = "high"

    # ML-based
    if classification == "Suicidal" and confidence > 0.6:
        is_crisis = True
        risk_level = "high"

    return {"is_crisis": is_crisis, "risk_level": risk_level}
```

### 11.2 Escalation Actions

1. Set `risk_level = 'high'`, `is_crisis = 1` in response and DB
2. Use crisis-specific LLM prompt with helpline numbers
3. Frontend shows `CrisisBanner` with Umang Pakistan, etc.
4. Admin dashboard lists crisis alerts
5. Log for human review (no auto-contact; ethical boundary)

### 11.3 Helpline Numbers (Pakistan)

- **Umang Pakistan:** 0311-7786264
- **PMHW:** 1020
- **Sehat Tahaffuz:** 1166

---

## 12. Scalability Design

### 12.1 Docker

```yaml
# docker-compose.yml (simplified)
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=mysql://user:pass@db:3306/sakoon
      - GROQ_API_KEY=${GROQ_API_KEY}
    depends_on: [db]

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: sakoon
    volumes: [mysql_data:/var/lib/mysql]

  frontend:
    build: ./frontend
    ports: ["5173:80"]
```

### 12.2 Future Scaling

| Strategy | When | How |
|----------|------|-----|
| **Uvicorn workers** | More concurrent users | `uvicorn main:app --workers 4` |
| **Redis cache** | Reduce DB load | Cache session data, mood aggregates |
| **Nginx LB** | Multiple backend instances | Reverse proxy, round-robin |
| **Cloud RDS** | Production DB | Managed MySQL (AWS RDS, etc.) |
| **CDN** | Static assets | Frontend on Vercel/Netlify |

---

## Summary Checklist

- [x] Naming conventions (frontend, backend, DB)
- [x] Four-layer architecture
- [x] AI pipeline (8 stages)
- [x] State management (AppContext, ChatContext, hooks)
- [x] Data flows (send message, session limit, crisis)
- [x] Complete MySQL schema
- [x] Full API contracts (request/response)
- [x] Component hierarchy + reusable components
- [x] Project folder structure with descriptions
- [x] 6-phase development roadmap
- [x] Crisis detection and escalation
- [x] Scalability (Docker, future options)

---

*Sakoon AI Technical Blueprint v1.0 — Production-ready design for Final Year Project.*
