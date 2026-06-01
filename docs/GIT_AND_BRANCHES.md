# Git, GitHub login & branches — Sakoon AI team

**Last updated:** 2026-06-01

---

## Abhi is PC par kya set hai?

| Setting | Current value | Matlab |
|---------|---------------|--------|
| **Git commit name** | `Mutahar456` | Sirf commit author label — push account se alag ho sakta hai |
| **Git commit email** | `amutaharhashmi456@gmail.com` | Commit metadata |
| **GitHub push (Windows saved login)** | Often **Mutahar456** | Credential Manager jo account use karta hai |
| **Remote `origin`** | https://github.com/Noor-Ul-ain68/Proj.git | **Noor-Ul-ain68** ka repo — yahan push **kaam kar chuka hai** |
| **Remote `sakoon`** | https://github.com/moin-ud-din-zafar/sakoon-ai-fyp.git | Team FYP repo — push ke liye **Noor-Ul-ain68** login zaroori (collaborator hona chahiye) |

**Important:** Repo URL `Noor-Ul-ain68/Proj` hai, lekin agar Windows ne **Mutahar456** ka token save kiya hai to `sakoon` remote par **403 Permission denied** aayega.  
**Sirf Noor-Ul-ain68 push kar sakti hain** (team rule) — push se pehle sahi account verify karein.

### Kaun sa account ab push karega?

- **`git push origin ...`** → GitHub par jo credential saved hai (check neeche) — ab tak **Noor** se `origin` par success hua.
- **`git push sakoon ...`** → Tabhi chalega jab login **Noor-Ul-ain68** ho, warna Mutahar456 par 403.

### Login check / theek karna (Windows)

1. **Settings → Credential Manager → Windows Credentials**
2. `git:https://github.com` entries **Remove**
3. Terminal:
   ```powershell
   cd "E:\Ai Virtual Assistant"
   git push origin feature/jwt-email-password-auth
   ```
4. Browser / prompt par **Noor-Ul-ain68** + **Personal Access Token** (password nahi)

Token banane: GitHub → Settings → Developer settings → Personal access tokens → `repo` scope.

---

## Branches (backend JWT work)

| Branch | Remote | Use |
|--------|--------|-----|
| **`feature/jwt-email-password-auth`** | `origin` (Noor) | **Latest** — email + password + JWT + protected APIs |
| `Backend_sakoon_Ai` | `origin` | Pehle wali backend branch (JWT commit bhi is par hai) |
| `main` | local | Purana frontend-focused history |

**Frontend developer ko kaun si branch clone kare?**

- Backend code + docs: **`feature/jwt-email-password-auth`** from `Noor-Ul-ain68/Proj`
- Ya team repo: `sakoon` remote jab Noor ke credentials se push ho jaye

```powershell
git clone https://github.com/Noor-Ul-ain68/Proj.git
cd Proj
git checkout feature/jwt-email-password-auth
```

---

## Nayi branch bana kar push (Noor account)

```powershell
cd "E:\Ai Virtual Assistant"
git checkout -b feature/my-change-name
# ... edits ...
git add backend docs database
git commit -m "Describe your change"
git push -u origin feature/my-change-name
```

**Kabhi commit mat karo:** `backend/.env`, `frontend/.env` (API keys / passwords).

---

## Remotes summary

```text
origin  →  Noor-Ul-ain68/Proj          (aapki push yahan successful)
sakoon  →  moin-ud-din-zafar/sakoon-ai-fyp   (Noor login + collaborator chahiye)
```

---

## Related

- JWT API details: `backend/AUTH_JWT_TESTING.md`
- Frontend integration: `docs/FRONTEND_BACKEND_INTEGRATION_GUIDE.md`
