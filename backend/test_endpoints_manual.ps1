# =============================================================================
# Sakoon AI - Manual terminal test for ALL API endpoints (31 routes)
# =============================================================================
#
# BEFORE RUNNING - Terminal 1 (keep open):
#   cd "E:\Ai Virtual Assistant\backend"
#   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
#
# Terminal 2 - run this script:
#   cd "E:\Ai Virtual Assistant\backend"
#   powershell -ExecutionPolicy Bypass -File .\test_endpoints_manual.ps1
#
# Options:
#   .\test_endpoints_manual.ps1 -Pause          # press Enter after each step
#   .\test_endpoints_manual.ps1 -SkipSlow       # skip chat LLM + TTS + avatar speak
#   .\test_endpoints_manual.ps1 -BaseUrl "http://127.0.0.1:8000"
#
# =============================================================================

param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [switch]$Pause,
    [switch]$SkipSlow
)

$ErrorActionPreference = "Continue"
$Api = "$BaseUrl/api/v1"
$Json = "application/json"
$step = 0
$pass = 0
$fail = 0

# --- state saved across steps ---
$uid = $null
$sid = $null
$aid = $null
$assignId = $null
$adminKey = $null
$userName = "manual_$(Get-Date -Format 'HHmmss')"

function Step-Header($title) {
    $script:step++
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor DarkGray
    Write-Host ("STEP {0}: {1}" -f $script:step, $title) -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor DarkGray
}

function Step-Pause {
    if ($Pause) {
        Write-Host "Press Enter for next step..." -ForegroundColor Yellow
        Read-Host | Out-Null
    }
}

function Show-Json($obj) {
    if ($null -eq $obj) { Write-Host "(null)" -ForegroundColor DarkGray; return }
    $obj | ConvertTo-Json -Depth 8 | Write-Host
}

function Test-Call {
    param(
        [string]$Label,
        [scriptblock]$Action
    )
    try {
        $result = & $Action
        Write-Host "RESULT: PASS - $Label" -ForegroundColor Green
        $script:pass++
        return $result
    }
    catch {
        $msg = $_.Exception.Message
        if ($_.ErrorDetails.Message) { $msg = $_.ErrorDetails.Message }
        Write-Host "RESULT: FAIL - $Label" -ForegroundColor Red
        Write-Host $msg -ForegroundColor Red
        $script:fail++
        return $null
    }
    finally {
        Step-Pause
    }
}

# --- health check ---
Step-Header "Pre-check - Server health"
try {
    $h = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 5
    Show-Json $h
    if ($h.status -ne "ok") { throw "Health not ok" }
    Write-Host "Server is up at $BaseUrl" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "ERROR: Server not running at $BaseUrl" -ForegroundColor Red
    Write-Host "Start in another terminal:" -ForegroundColor Yellow
    Write-Host '  cd "E:\Ai Virtual Assistant\backend"' -ForegroundColor White
    Write-Host "  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" -ForegroundColor White
    exit 1
}
Step-Pause

# =============================================================================
# SYSTEM (2)
# =============================================================================

Step-Header "GET /"
Test-Call "Root" { Invoke-RestMethod -Uri $BaseUrl } | Out-Null

Step-Header "GET /health"
Test-Call "Health" { Invoke-RestMethod -Uri "$BaseUrl/health" } | Out-Null

# =============================================================================
# AUTH (3)
# =============================================================================

Step-Header "POST /api/v1/auth/register"
$reg = Test-Call "Register" {
    Invoke-RestMethod -Method POST -Uri "$Api/auth/register" -ContentType $Json `
        -Body (@{ name = $userName; languagePreference = "en" } | ConvertTo-Json)
}
if ($reg) { $uid = $reg.user.id; Write-Host ">>> userId = $uid" -ForegroundColor Magenta }

Step-Header "POST /api/v1/auth/login"
Test-Call "Login" {
    Invoke-RestMethod -Method POST -Uri "$Api/auth/login" -ContentType $Json `
        -Body (@{ name = $userName } | ConvertTo-Json)
} | Out-Null

Step-Header "GET /api/v1/auth/session/{user_id}"
$sess = Test-Call "Get session" {
    Invoke-RestMethod -Uri "$Api/auth/session/$uid"
}
if ($sess) {
    $sid = $sess.session.id
    Write-Host ">>> sessionId = $sid" -ForegroundColor Magenta
    Show-Json $sess
}

# =============================================================================
# CHAT (2)
# =============================================================================

if (-not $SkipSlow) {
    Step-Header "POST /api/v1/chat/message (normal)"
    Write-Host "Waiting for LLM (may take 15-60 sec)..." -ForegroundColor Yellow
    $chat = Test-Call "Chat message" {
        Invoke-RestMethod -Method POST -Uri "$Api/chat/message" -ContentType $Json -TimeoutSec 120 `
            -Body (@{
                userId    = $uid
                sessionId = $sid
                message   = "I feel stressed about exams and cannot sleep"
            } | ConvertTo-Json)
    }
    if ($chat) {
        Show-Json $chat
        if ($chat.suggestedExercise) { $assignId = $chat.suggestedExercise.assignmentId }
    }
}
else {
    Write-Host "SKIP ( -SkipSlow ): chat/message" -ForegroundColor Yellow
    Step-Pause
}

Step-Header "POST /api/v1/chat/journal-reflection"
if (-not $SkipSlow) {
    Test-Call "Journal reflection" {
        Invoke-RestMethod -Method POST -Uri "$Api/chat/journal-reflection" -ContentType $Json -TimeoutSec 90 `
            -Body '{"text":"Today I tried breathing when anxious.","language":"en"}'
    } | ForEach-Object { Show-Json $_ }
}
else {
    Write-Host "SKIP ( -SkipSlow ): journal-reflection" -ForegroundColor Yellow
    Step-Pause
}

# =============================================================================
# SESSION (1)
# =============================================================================

Step-Header "GET /api/v1/session/{session_id}/history"
$hist = Test-Call "Session history" {
    Invoke-RestMethod -Uri "$Api/session/$sid/history"
}
if ($hist) { Show-Json $hist }

# =============================================================================
# USER (3)
# =============================================================================

Step-Header "GET /api/v1/user/{user_id}/mood-summary"
Test-Call "Mood summary" {
    Invoke-RestMethod -Uri "$Api/user/$uid/mood-summary"
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/user/{user_id}/recommendations"
Test-Call "Recommendations" {
    Invoke-RestMethod -Uri "$Api/user/$uid/recommendations"
} | ForEach-Object { Show-Json $_ }

Step-Header "POST /api/v1/user/{user_id}/exercise-feedback"
if ($assignId) {
    Test-Call "Exercise feedback" {
        Invoke-RestMethod -Method POST -Uri "$Api/user/$uid/exercise-feedback" -ContentType $Json `
            -Body (@{ assignmentId = $assignId; sessionId = $sid; helped = $true } | ConvertTo-Json)
    } | ForEach-Object { Show-Json $_ }
}
else {
    Write-Host "SKIP: no assignmentId from chat (run without -SkipSlow)" -ForegroundColor Yellow
    Step-Pause
}

# =============================================================================
# MOOD (4)
# =============================================================================

Step-Header "POST /api/v1/mood/log"
Test-Call "Mood log" {
    Invoke-RestMethod -Method POST -Uri "$Api/mood/log" -ContentType $Json `
        -Body (@{ user_id = $uid; mood_score = 4; note = "manual test" } | ConvertTo-Json)
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/mood/history/{user_id}"
Test-Call "Mood history" {
    Invoke-RestMethod -Uri "$Api/mood/history/$uid`?limit=5"
} | ForEach-Object { Show-Json $_ }

Step-Header "POST /api/v1/mood/behavior"
Test-Call "Behavior log" {
    Invoke-RestMethod -Method POST -Uri "$Api/mood/behavior" -ContentType $Json `
        -Body (@{
            user_id             = $uid
            sleep_hours         = 7
            physical_activity   = "light"
            social_interaction  = "moderate"
            notes               = "manual test"
        } | ConvertTo-Json)
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/mood/behavior/{user_id}"
Test-Call "Behavior history" {
    Invoke-RestMethod -Uri "$Api/mood/behavior/$uid`?limit=5"
} | ForEach-Object { Show-Json $_ }

# =============================================================================
# ASSESSMENT (8) - complete all 3 sessions
# =============================================================================

function Complete-AssessmentSession {
    param([int]$SessionNumber)
    $start = Invoke-RestMethod -Method POST -Uri "$Api/assessment/start" -ContentType $Json `
        -Body (@{ user_id = $uid; session_number = $SessionNumber } | ConvertTo-Json)
    $assessmentId = $start.assessmentId
    Write-Host "assessmentId=$assessmentId session=$SessionNumber" -ForegroundColor Magenta
    $guard = 0
    while ($guard -lt 50) {
        $guard++
        $nq = $start.nextQuestion
        if (-not $nq -and $start.status -eq "session_complete") { break }
        if (-not $nq) {
            $start = Invoke-RestMethod -Uri "$Api/assessment/next/$assessmentId"
            $nq = $start.nextQuestion
            if ($start.status -eq "completed" -or -not $nq) { break }
        }
        $body = if ($nq.type -eq "text") {
            @{ assessment_id = $assessmentId; question_key = $nq.key; answer_text = "Manual test answer." }
        } else {
            $val = 1
            if ($nq.options -and $nq.options.Count -gt 0) { $val = $nq.options[0].value }
            @{ assessment_id = $assessmentId; question_key = $nq.key; answer_value = $val }
        }
        Write-Host "  answer: $($nq.key)" -ForegroundColor DarkGray
        $start = Invoke-RestMethod -Method POST -Uri "$Api/assessment/answer" -ContentType $Json `
            -Body ($body | ConvertTo-Json)
        if ($start.status -eq "session_complete") { break }
    }
    return $assessmentId
}

Step-Header "POST /api/v1/assessment/profile"
Test-Call "Assessment profile" {
    Invoke-RestMethod -Method POST -Uri "$Api/assessment/profile" -ContentType $Json `
        -Body (@{
            user_id        = $uid
            age            = 22
            gender         = "male"
            sleep_pattern  = "irregular"
            past_therapy   = $false
        } | ConvertTo-Json)
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/assessment/profile/{user_id}"
Test-Call "Get profile" {
    Invoke-RestMethod -Uri "$Api/assessment/profile/$uid"
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/assessment/status/{user_id}"
Test-Call "Assessment status (before)" {
    Invoke-RestMethod -Uri "$Api/assessment/status/$uid"
} | ForEach-Object { Show-Json $_ }

foreach ($sn in 1..3) {
    Step-Header "Assessment session $sn - start + answer all questions"
    Test-Call "Complete assessment session $sn" {
        Complete-AssessmentSession -SessionNumber $sn
        @{ ok = $true; session = $sn }
    } | Out-Null
}

Step-Header "GET /api/v1/assessment/status/{user_id} (after)"
Test-Call "Assessment status (after)" {
    Invoke-RestMethod -Uri "$Api/assessment/status/$uid"
} | ForEach-Object { Show-Json $_ }

Step-Header "POST /api/v1/assessment/scores/{user_id}"
Test-Call "Calculate scores" {
    Invoke-RestMethod -Method POST -Uri "$Api/assessment/scores/$uid"
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/assessment/result/{user_id}"
Test-Call "Assessment result" {
    Invoke-RestMethod -Uri "$Api/assessment/result/$uid"
} | ForEach-Object { Show-Json $_ }

# =============================================================================
# CRISIS CHAT (extra - same route, different payload)
# =============================================================================

if (-not $SkipSlow) {
    Step-Header "POST /api/v1/chat/message (CRISIS test)"
    $crisis = Test-Call "Crisis chat" {
        Invoke-RestMethod -Method POST -Uri "$Api/chat/message" -ContentType $Json -TimeoutSec 120 `
            -Body (@{
                userId    = $uid
                sessionId = $sid
                message   = "I have been thinking about suicide and want to end my life"
            } | ConvertTo-Json)
    }
    if ($crisis) {
        [PSCustomObject]@{
            isCrisis          = $crisis.isCrisis
            riskLevel         = $crisis.riskLevel
            mhClassification  = $crisis.mhClassification
            helplineCount     = @($crisis.helplineNumbers).Count
            aiResponsePreview = $crisis.aiResponse.Substring(0, [Math]::Min(150, $crisis.aiResponse.Length))
        } | ConvertTo-Json | Write-Host
    }
}

# =============================================================================
# TTS (1)
# =============================================================================

Step-Header "POST /api/v1/tts/speak"
if (-not $SkipSlow) {
    Test-Call "TTS speak" {
        $r = Invoke-WebRequest -Method POST -Uri "$Api/tts/speak" -ContentType $Json -TimeoutSec 20 `
            -Body '{"text":"Hello from Sakoon manual test.","language":"en"}'
        $out = Join-Path $PSScriptRoot "manual_test_tts.mp3"
        [IO.File]::WriteAllBytes($out, $r.Content)
        @{ savedTo = $out; bytes = $r.RawContentLength; contentType = $r.Headers["Content-Type"] }
    } | ForEach-Object { Show-Json $_ }
}
else {
    Write-Host "SKIP ( -SkipSlow ): tts/speak" -ForegroundColor Yellow
    Step-Pause
}

# =============================================================================
# AVATAR (2)
# =============================================================================

Step-Header "GET /api/v1/avatar/status"
Test-Call "Avatar status" {
    Invoke-RestMethod -Uri "$Api/avatar/status"
} | ForEach-Object { Show-Json $_ }

Step-Header "POST /api/v1/avatar/speak"
if (-not $SkipSlow) {
    Write-Host "Avatar timeout 30s (skip with -SkipSlow if slow)" -ForegroundColor Yellow
    Test-Call "Avatar speak" {
        $r = Invoke-WebRequest -Method POST -Uri "$Api/avatar/speak" -ContentType $Json -TimeoutSec 30 `
            -Body '{"text":"Hi","language":"en"}'
        $mode = $r.Headers["X-Avatar-Mode"]
        $ext = if ($mode -eq "video") { "mp4" } else { "wav" }
        $out = Join-Path $PSScriptRoot "manual_test_avatar.$ext"
        [IO.File]::WriteAllBytes($out, $r.Content)
        @{ savedTo = $out; mode = $mode; bytes = $r.RawContentLength }
    } | ForEach-Object { Show-Json $_ }
}
else {
    Write-Host "SKIP ( -SkipSlow ): avatar/speak" -ForegroundColor Yellow
    Step-Pause
}

# =============================================================================
# ADMIN (5)
# =============================================================================

Step-Header "POST /api/v1/admin/login"
$adm = Test-Call "Admin login" {
    Invoke-RestMethod -Method POST -Uri "$Api/admin/login" -ContentType $Json `
        -Body '{"username":"admin","password":"sakoon123"}'
}
if ($adm) { $adminKey = $adm.adminKey; Write-Host ">>> adminKey saved" -ForegroundColor Magenta }

$hdr = @{ "X-Admin-Key" = $adminKey }

Step-Header "GET /api/v1/admin/stats"
Test-Call "Admin stats" {
    Invoke-RestMethod -Uri "$Api/admin/stats" -Headers $hdr
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/admin/sessions"
Test-Call "Admin sessions" {
    Invoke-RestMethod -Uri "$Api/admin/sessions" -Headers $hdr
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/admin/sessions/{session_id}/logs"
Test-Call "Admin session logs" {
    Invoke-RestMethod -Uri "$Api/admin/sessions/$sid/logs" -Headers $hdr
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/admin/crisis-alerts"
Test-Call "Crisis alerts" {
    Invoke-RestMethod -Uri "$Api/admin/crisis-alerts" -Headers $hdr
} | ForEach-Object { Show-Json $_ }

Step-Header "GET /api/v1/admin/stats WITHOUT key (expect 401)"
try {
    Invoke-RestMethod -Uri "$Api/admin/stats" -ErrorAction Stop
    Write-Host "RESULT: FAIL - should have been 401" -ForegroundColor Red
    $script:fail++
}
catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Write-Host "RESULT: PASS - got 401 as expected" -ForegroundColor Green
        $script:pass++
    }
    else {
        Write-Host "RESULT: FAIL - unexpected error" -ForegroundColor Red
        Write-Host $_.Exception.Message
        $script:fail++
    }
}
Step-Pause

# =============================================================================
# SUMMARY
# =============================================================================

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor DarkGray
Write-Host "FINISHED - Pass: $script:pass  |  Fail: $script:fail" -ForegroundColor $(if ($script:fail -eq 0) { "Green" } else { "Yellow" })
Write-Host ("=" * 70) -ForegroundColor DarkGray
Write-Host "IDs used: userId=$uid sessionId=$sid userName=$userName" -ForegroundColor Magenta
Write-Host "Docs: $BaseUrl/docs" -ForegroundColor Gray
if ($script:fail -gt 0) { exit 1 }
exit 0
