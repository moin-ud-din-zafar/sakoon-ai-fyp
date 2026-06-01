# JWT Auth Testing (Email + Password)

Backend user auth uses **bcrypt** passwords and **JWT** bearer tokens. Admin routes still use `X-Admin-Key` (unchanged).

## Environment

Add to `backend/.env` (see `.env.example`):

```env
JWT_SECRET=your-long-random-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
```

Install deps:

```bash
cd backend
pip install -r requirements.txt
```

Start API:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

For a **clean SQLite** schema (optional):

```bash
del data\sakoon.db
```

Restart uvicorn so tables migrate with `email` + `password_hash`.

## API contract

| Method | Path | Auth | Body |
|--------|------|------|------|
| POST | `/api/v1/auth/register` | No | `name`, `email`, `password` (min 8), `languagePreference?` |
| POST | `/api/v1/auth/login` | No | `email`, `password` |
| GET | `/api/v1/auth/me` | Bearer | — |
| GET | `/api/v1/auth/session` | Bearer | — |

**Register / login response:**

```json
{
  "accessToken": "<jwt>",
  "tokenType": "bearer",
  "user": { "id": 1, "name": "...", "email": "...", "languagePreference": "en" }
}
```

**Protected routes** (chat, user, mood, assessment, session history): header

```http
Authorization: Bearer <accessToken>
```

Chat body still sends `userId` and `sessionId`; they must match the JWT user and an owned session.

## PowerShell examples

```powershell
$Base = "http://127.0.0.1:8000/api/v1"
$Json = "application/json"

# Register
$reg = Invoke-RestMethod -Method POST -Uri "$Base/auth/register" -ContentType $Json `
  -Body '{"name":"Ali","email":"ali@test.com","password":"TestPass123!","languagePreference":"en"}'

$token = $reg.accessToken
$hdr = @{ Authorization = "Bearer $token" }

# Me
Invoke-RestMethod -Uri "$Base/auth/me" -Headers $hdr

# Session
$sess = Invoke-RestMethod -Uri "$Base/auth/session" -Headers $hdr
$sid = $sess.session.id
$uid = $reg.user.id

# Chat
Invoke-RestMethod -Method POST -Uri "$Base/chat/message" `
  -Headers @{ Authorization = "Bearer $token"; "Content-Type" = $Json } `
  -Body (@{ userId = $uid; sessionId = $sid; message = "Hello" } | ConvertTo-Json)
```

## Automated tests

```bash
cd backend
pytest test_complete.py -v --tb=short
# or
python run_tests.py
```

Manual script (all routes):

```powershell
powershell -ExecutionPolicy Bypass -File .\test_endpoints_manual.ps1 -SkipSlow
```

## Frontend integration

1. **Register / login** — store `accessToken` (localStorage or secure cookie).
2. **Axios/fetch** — set default header: `Authorization: Bearer ${token}`.
3. Replace name-only login with email + password forms.
4. Use `GET /auth/session` (not `/auth/session/{userId}`) after login.

## Common errors

| Status | Meaning |
|--------|---------|
| 401 | Missing/invalid/expired JWT |
| 403 | `userId` or `sessionId` does not belong to token user |
| 409 | Email already registered |
| 422 | Validation (weak password, invalid email) |
