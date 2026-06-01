# Push to `Backend_sakoon_Ai` branch

**Repo:** https://github.com/moin-ud-din-zafar/sakoon-ai-fyp.git  
**Branch:** `Backend_sakoon_Ai`  
**Folders included:** `.devcontainer`, `backend`, `database`, `Dataset`, `docs`, `Documentation`

**NOT included:** `frontend`, `wav2lip`, `howtorun.txt`, etc.

---

## CMD commands (copy in order)

### 1) Go to project
```cmd
cd /d "E:\Ai Virtual Assistant"
```

### 2) Add GitHub remote (once)
```cmd
"C:\Program Files\Git\bin\git.exe" remote add sakoon https://github.com/moin-ud-din-zafar/sakoon-ai-fyp.git
```
If error "already exists", skip or run:
```cmd
"C:\Program Files\Git\bin\git.exe" remote set-url sakoon https://github.com/moin-ud-din-zafar/sakoon-ai-fyp.git
```

### 3) Create branch with ONLY these folders
```cmd
"C:\Program Files\Git\bin\git.exe" checkout --orphan Backend_sakoon_Ai
"C:\Program Files\Git\bin\git.exe" reset
"C:\Program Files\Git\bin\git.exe" add .gitignore .devcontainer backend database Dataset docs Documentation
"C:\Program Files\Git\bin\git.exe" status
"C:\Program Files\Git\bin\git.exe" commit -m "Backend Sakoon AI: API, database, dataset, and documentation"
```

### 4) Push (login when asked)
```cmd
"C:\Program Files\Git\bin\git.exe" push -u sakoon Backend_sakoon_Ai
```
- **Username:** `Noor-Ul-ain68`
- **Password:** Use a **GitHub Personal Access Token** (not account password).  
  Create: GitHub → Settings → Developer settings → Personal access tokens → Generate (repo scope).

### 5) Return to main branch (local work)
```cmd
"C:\Program Files\Git\bin\git.exe" checkout main
```

---

## Verify on GitHub
Open: https://github.com/moin-ud-din-zafar/sakoon-ai-fyp/tree/Backend_sakoon_Ai
