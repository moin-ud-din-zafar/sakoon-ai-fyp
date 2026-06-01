# Sakoon AI — FYP Supervisor Meeting Checklist

**Meeting prep for:** Backend API testing & demonstration  
**Project:** Sakoon AI — Mental Health Support System  
**Suggested meeting date:** 20 May 2026

---

## BEFORE THE MEETING (tonight)

- [ ] Start server and confirm no startup errors:
  ```powershell
  cd "e:\Ai Virtual Assistant\backend"
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ```
- [ ] Run automated tests and **screenshot** the summary:
  ```powershell
  python run_tests.py
  ```
  Target: **56/56 passed**, `test_results.json` saved.

- [ ] Run pytest and **screenshot**:
  ```powershell
  pytest test_complete.py -v --tb=short
  ```
  Target: **52 passed** in ~60–90 seconds.

- [ ] Open API tester and **screenshot** sidebar (all endpoint groups):
  ```powershell
  python -m http.server 5500
  ```
  Open: http://127.0.0.1:5500/api_tester.html

- [ ] Open Swagger docs screenshot: http://127.0.0.1:8000/docs

- [ ] Skim **`SUPERVISOR_QA.md`** — read answers aloud once.

- [ ] Print or PDF: **`FYP_TEST_REPORT.md`** (first 8 pages).

- [ ] Confirm `.env` has `OPENROUTER_API_KEY` (for live chat demo) OR accept fallback replies.

- [ ] Confirm `backend/models/*.joblib` exist (`python scripts/train_model.py` if missing).

---

## WHAT TO SHOW IN MEETING (recommended order)

| # | What | Why |
|---|------|-----|
| 1 | Live server + `/health` | Proves deployment works |
| 2 | `/docs` (Swagger) | All **31 endpoints** visible |
| 3 | **`python run_tests.py` live** | Strongest proof — colored PASS output |
| 4 | **`api_tester.html`** — register → session → chat → crisis | End-to-end UX |
| 5 | **`FYP_TEST_REPORT.md`** | Formal university-style evidence |
| 6 | Q&A from **`SUPERVISOR_QA.md`** | Confident technical answers |

---

## DEMO SCRIPT (what to say and do)

### Step 1 — Introduction (30 sec)

> "Assalam-o-alaikum. This is **Sakoon AI**, our FYP mental health support backend. It is built with **FastAPI** and exposes **31 REST endpoints** for chat, clinical assessment, mood tracking, TTS, avatar, and admin monitoring. The server runs on port **8000**."

*Show:* browser `http://127.0.0.1:8000/health` → `{"status":"ok"}`

### Step 2 — API structure (1 min)

> "Endpoints are versioned under `/api/v1`. We use **name-based auth** for users and an **admin API key** for staff routes. OpenAPI documentation is auto-generated."

*Show:* `/docs` — expand Auth, Chat, Assessment, Admin tags.

### Step 3 — Live test suite (2–3 min) ⭐

> "We wrote **52 pytest integration tests** plus a sequential runner with **56 checks**. I will run the suite live against the real server — no mocks."

```powershell
python run_tests.py
```

> "Each test hits the actual HTTP API. We test **happy paths** and **sad paths** — for example 422 validation, 404 login, 401 admin without key, and crisis keywords from our safety constants."

*Point at:* green PASS lines, final **SUMMARY: 56 passed**.

### Step 4 — API tester demo (2 min)

> "We also built a custom **Postman-style HTML tester** for manual QA."

*Do:* Quick flow → Register → Get session → Send chat message → (optional) crisis message showing `isCrisis` and helplines.

### Step 5 — Formal report (1 min)

> "Everything is documented in our **FYP Test Report**: test strategy, all 52 cases, coverage by module, and integration flows including PHQ-9/GAD-7 assessment."

*Show:* `FYP_TEST_REPORT.md` sections 5, 7, and 12.

---

## IMPRESSIVE POINTS TO MENTION

- **100% pass rate** on last run: pytest **52/52**, runner **56/56**
- **Black-box functional testing** against live API (httpx / requests)
- **Crisis detection** tested with real keywords from `app/core/constants.py`
- **Full 3-session assessment** automated (intake → PHQ-9/GAD-7 → behavioral → scores)
- **Admin security**: 401 without `X-Admin-Key`, 200 with valid key
- **Dual database**: MySQL production path + SQLite dev (`USE_SQLITE`)
- **ML pipeline**: TF-IDF mental health classifier + OpenRouter LLM + optional HF emotion
- **Custom tooling**: `api_tester.html`, `qa_helpers.py`, `conftest.py` shared fixtures

---

## IF SUPERVISOR ASKS TO IMPROVE

| Request | Your answer |
|---------|-------------|
| Load testing | "We can add **Locust** or **k6** for concurrent users." |
| Code coverage | "`pytest --cov=app` for line coverage report." |
| CI/CD | "GitHub Actions to run `pytest` on every push." |
| Security | "JWT for users, rate limiting, HTTPS in production." |
| Unit tests | "Mock LLM in `llm_service` for faster isolated tests." |

---

## BACKUP IF SOMETHING FAILS LIVE

| Problem | Fix |
|---------|-----|
| Server won't start | `USE_SQLITE=true` in `.env` |
| Chat 500 / classifier error | Run `python scripts/train_model.py` |
| TTS 503 | Say "Edge-TTS needs network; chat still works" |
| Slow chat | "OpenRouter LLM takes 3–8s; fallback is instant" |
| Tests fail | Show **screenshot** from last green run + `test_results.json` |

---

## FILES TO HAVE OPEN

1. Terminal — server + test runner  
2. Browser — `/docs` + `api_tester.html`  
3. `FYP_TEST_REPORT.md`  
4. `SUPERVISOR_QA.md`  
5. `TEST_EVIDENCE.md`  

Good luck with your meeting.
