# Reply for Frontend Developer — Git merge error & running FE + BE

**To:** Frontend team  
**Re:** `unable to merge unrelated histories` + how to run frontend and backend together  
**Repo:** https://github.com/moin-ud-din-zafar/sakoon-ai-fyp  
**Branch to use:** `fullstack_Sakoon_AI_`

---

Hi,

Below are clear answers for both questions. Please follow **Option A** for Git (recommended) — do not force-merge old `main` into `fullstack_Sakoon_AI_`.

---

## 1. Error: `fatal: refusing to merge unrelated histories`

### What it means

Git is saying two branches **do not share a common commit**. They were created independently (different roots). This is **expected** on our project: the team backend branch (`fullstack_Sakoon_AI_`) was rebuilt as a clean history for JWT auth, while older branches (e.g. `main`) may have a different starting point.

**This is not a bug in your machine** — merging those histories without a strategy will always warn or fail.

### What you should NOT do

- Do not run random `git pull` merges between `main` and `fullstack_Sakoon_AI_` unless you understand the result.
- Do not use `--allow-unrelated-histories` unless a senior dev asked you to — it creates a huge conflict-heavy merge.

### Recommended fix — **Option A: Fresh clone (best)**

```powershell
# New folder (example)
cd C:\Projects
git clone https://github.com/moin-ud-din-zafar/sakoon-ai-fyp.git sakoon-work
cd sakoon-work
git checkout fullstack_Sakoon_AI_
```

You now have the **correct backend + docs** for JWT integration.  
Read: `docs/API_PAYLOAD_SYNTAX.md` and `docs/FRONTEND_BACKEND_INTEGRATION_GUIDE.md`.

**Note:** This branch currently contains **backend**, **database**, and **docs**. If you already have a **frontend** folder from an older full-project clone, keep using that `frontend/` folder on your PC and only update backend from this branch — or ask the team lead for the frontend branch/repo name if frontend is stored separately.

### Option B — You already cloned and only need the right branch

```powershell
cd path\to\sakoon-ai-fyp
git fetch origin
git checkout fullstack_Sakoon_AI_
git pull origin fullstack_Sakoon_AI_
```

If checkout fails because of local changes:

```powershell
git stash
git checkout fullstack_Sakoon_AI_
git pull origin fullstack_Sakoon_AI_
git stash pop
```

### Option C — You must merge unrelated histories (only if lead approves)

```powershell
git checkout your-branch
git pull origin fullstack_Sakoon_AI_ --allow-unrelated-histories
# Resolve conflicts in VS Code / Cursor, then:
git add .
git commit -m "Merge fullstack_Sakoon_AI_ with allow unrelated histories"
```

Expect many conflict files. **Option A is faster and safer.**

---

## 2. “Separate branches” — how to run frontend and backend together?

Important: **Git branches do not run the app.** Branches are only for code versions.

Running the app = **two processes on your computer**:

| App | Folder | Command | URL |
|-----|--------|---------|-----|
| **Backend (API)** | `backend/` | `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` | http://127.0.0.1:8000/health |
| **Frontend (UI)** | `frontend/` | `npm run dev` | http://127.0.0.1:5173 |

### Step-by-step (Windows)

**Terminal 1 — Backend**

```powershell
cd "E:\Ai Virtual Assistant\backend"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env: OPENROUTER_API_KEY, DATABASE_*, JWT_SECRET
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Wait until you see: `Application startup complete`  
Test: open http://127.0.0.1:8000/health → `{"status":"ok"}`

**Terminal 2 — Frontend**

```powershell
cd "E:\Ai Virtual Assistant\frontend"
npm install
copy .env.example .env
```

In `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

```powershell
npm run dev
```

Open browser: http://127.0.0.1:5173/

**Keep both terminals open** while developing. Stop either with `Ctrl+C`.

### Architecture (simple)

```
Browser (5173)  →  React (frontend)  →  HTTP  →  FastAPI (8000)  →  MySQL/SQLite
```

Frontend never talks to the database directly — only to the API.

---

## 3. Backend auth change (must read)

Backend now uses **email + password + JWT**, not name-only login.

- Register/login payloads: see **`docs/API_PAYLOAD_SYNTAX.md`**
- Integration steps (axios interceptor, `localStorage` token): **`docs/FRONTEND_BACKEND_INTEGRATION_GUIDE.md`** Section 6–11

Until frontend is updated:

- Login/register with **name only will fail**
- Protected routes need header: `Authorization: Bearer <accessToken>`

---

## 4. Quick checklist

- [ ] On branch `fullstack_Sakoon_AI_` (or full local project with this backend)
- [ ] Backend running on port **8000**
- [ ] Frontend `.env` has `VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1`
- [ ] Frontend running on port **5173**
- [ ] Read `API_PAYLOAD_SYNTAX.md` before calling APIs

---

## 5. If something still fails

| Symptom | Fix |
|---------|-----|
| Network Error in browser | Backend not running or wrong `VITE_API_BASE_URL` |
| CORS error | Use `127.0.0.1` consistently (not `localhost` in one place and `127.0.0.1` in another) |
| 401 on API calls | Missing/expired JWT — login again, set Bearer header |
| 403 on chat | `userId` / `sessionId` must match logged-in user |
| Port 8000 busy | Close old uvicorn or use `--port 8001` and update frontend `.env` |

Swagger (all routes): http://127.0.0.1:8000/docs

---

Thanks,  
Backend / Full-stack team — Sakoon AI FYP
