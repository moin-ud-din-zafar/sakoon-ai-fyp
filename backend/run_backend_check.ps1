# Sakoon AI — One-click backend check (PowerShell)
# Usage (from anywhere):
#   powershell -ExecutionPolicy Bypass -File "E:\Ai Virtual Assistant\backend\run_backend_check.ps1"
#
# Or open PowerShell, then:
#   cd "E:\Ai Virtual Assistant\backend"
#   .\run_backend_check.ps1

$ErrorActionPreference = "Stop"
$BackendRoot = $PSScriptRoot
Set-Location $BackendRoot

Write-Host "`n=== Sakoon AI Backend Check ===" -ForegroundColor Cyan
Write-Host "Folder: $BackendRoot`n"

# 1) Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "ERROR: python not found. Install Python 3.11+ and add to PATH." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python: $(python --version)" -ForegroundColor Green

# 2) Optional venv
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "[..] Activating venv..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# 3) Dependencies (quick check)
python -c "import fastapi, uvicorn, requests" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[..] Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
    pip install requests python-dotenv
}

# 4) ML models
if (-not (Test-Path ".\models\mh_classifier.joblib")) {
    Write-Host "[..] Training MH classifier (first time, ~1-2 min)..." -ForegroundColor Yellow
    python scripts/train_model.py
}
else {
    Write-Host "[OK] MH models found" -ForegroundColor Green
}

# 5) .env
if (-not (Test-Path ".\.env")) {
    Write-Host "WARN: .env missing — copy .env.example to .env" -ForegroundColor Yellow
    if (Test-Path ".\.env.example") { Copy-Item ".\.env.example" ".\.env" }
}

# 6) Start server if not running
$base = "http://127.0.0.1:8000"
$healthOk = $false
try {
    $h = Invoke-RestMethod -Uri "$base/health" -TimeoutSec 2
    if ($h.status -eq "ok") { $healthOk = $true }
} catch { }

if (-not $healthOk) {
    Write-Host "[..] Starting API server on port 8000..." -ForegroundColor Yellow
    $serverJob = Start-Job -ScriptBlock {
        Set-Location $using:BackendRoot
        python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    }
    $tries = 0
    while ($tries -lt 30) {
        Start-Sleep -Seconds 1
        try {
            $h = Invoke-RestMethod -Uri "$base/health" -TimeoutSec 2
            if ($h.status -eq "ok") { $healthOk = $true; break }
        } catch { }
        $tries++
    }
    if (-not $healthOk) {
        Write-Host "ERROR: Server did not start. Check errors above." -ForegroundColor Red
        Stop-Job $serverJob -ErrorAction SilentlyContinue
        exit 1
    }
    Write-Host "[OK] Server running: $base" -ForegroundColor Green
    Write-Host "     Swagger UI: $base/docs" -ForegroundColor Gray
}
else {
    Write-Host "[OK] Server already running: $base" -ForegroundColor Green
    $serverJob = $null
}

# 7) Run all API tests
Write-Host "`n=== Running API tests (run_tests.py) ===" -ForegroundColor Cyan
python run_tests.py --verbose --base-url $base
$testExit = $LASTEXITCODE

Write-Host "`n=== Done ===" -ForegroundColor Cyan
if ($testExit -eq 0) {
    Write-Host "All automated tests PASSED." -ForegroundColor Green
}
else {
    Write-Host "Some tests FAILED. See output above. Results: test_results.json" -ForegroundColor Red
}

if ($serverJob) {
    Write-Host "`nServer was started by this script (background job)." -ForegroundColor Yellow
    Write-Host "To stop it:  Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Yellow
    Write-Host "Or close PowerShell window." -ForegroundColor Yellow
}
else {
    Write-Host "`nServer was already running — leave your uvicorn window open." -ForegroundColor Gray
}

exit $testExit
