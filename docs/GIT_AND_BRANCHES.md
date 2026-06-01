# Git, GitHub login & branches — Sakoon AI team

**Last updated:** 2026-06-01

---

## Git identity (commits + push)

| Setting | Value |
|---------|--------|
| **Commit author (this repo)** | `Noor-Ul-ain68` |
| **Commit email** | `Noor-Ul-ain68@users.noreply.github.com` |
| **Remote `origin`** | https://github.com/Noor-Ul-ain68/Proj.git |
| **Remote `sakoon`** | https://github.com/moin-ud-din-zafar/sakoon-ai-fyp.git |

**Team rule:** Push GitHub par **Noor-Ul-ain68** account se karein (Personal Access Token).

### Push credentials (Windows)

1. **Settings → Credential Manager → Windows Credentials**
2. `git:https://github.com` — sahi account (**Noor-Ul-ain68**) hona chahiye
3. Galat account ho to entry delete karein, phir `git push` — login par **Noor-Ul-ain68** + PAT

---

## Branches (backend JWT work)

| Branch | Remote | Use |
|--------|--------|-----|
| **`fullstack_Sakoon_AI_`** | `sakoon` (moin-ud-din-zafar/sakoon-ai-fyp) | **Team branch** — JWT + docs + payload guide |
| **`feature/jwt-email-password-auth`** | `origin` / `sakoon` | Same code, alternate branch name |
| `Backend_sakoon_Ai` | older name | Use `fullstack_Sakoon_AI_` instead |

**Frontend developer clone:**

```powershell
git clone https://github.com/moin-ud-din-zafar/sakoon-ai-fyp.git
cd sakoon-ai-fyp
git checkout fullstack_Sakoon_AI_
```

---

## Nayi branch + push (Noor account)

```powershell
cd "E:\Ai Virtual Assistant"
git checkout -b feature/my-change-name
git add backend docs database
git commit -m "Describe your change"
git push -u sakoon feature/my-change-name
```

**Kabhi commit mat karo:** `backend/.env`, `frontend/.env` (API keys / passwords).

---

## Related

- JWT API: `backend/AUTH_JWT_TESTING.md`
- Frontend: `docs/FRONTEND_BACKEND_INTEGRATION_GUIDE.md`
- Payload JSON: `docs/API_PAYLOAD_SYNTAX.md`
