# Sakoon AI — Test Execution Evidence

**Execution date:** 19 May 2026  
**Environment:** Windows, Python 3.13, `http://127.0.0.1:8000`  
**Database:** MySQL (`sakoon`) — verified via live integration tests  
**Artifacts:** `test_results.json`, `test_complete.py`, `run_tests.py`

---

## 1. Pytest output (52 tests)

```
========================= test session starts ==========================
platform win32 -- Python 3.13.x, pytest-8.x.x, pluggy-1.x.x
rootdir: E:\Ai Virtual Assistant\backend
plugins: anyio-4.x.x
collected 52 items

test_complete.py::TestAuth::test_01_register_new_user_success PASSED     [  1%]
test_complete.py::TestAuth::test_02_register_duplicate_name PASSED       [  3%]
test_complete.py::TestAuth::test_03_register_missing_name PASSED           [  5%]
test_complete.py::TestAuth::test_04_register_with_language_preference PASSED [  7%]
test_complete.py::TestAuth::test_05_login_existing_user PASSED           [  9%]
test_complete.py::TestAuth::test_06_login_nonexistent_user PASSED        [ 11%]
test_complete.py::TestAuth::test_07_login_empty_body PASSED              [ 13%]
test_complete.py::TestAuth::test_08_get_session_valid_user PASSED        [ 15%]
test_complete.py::TestChat::test_09_send_chat_message_success PASSED     [ 17%]
test_complete.py::TestChat::test_10_chat_has_classification PASSED       [ 19%]
test_complete.py::TestChat::test_11_chat_has_emotion PASSED              [ 21%]
test_complete.py::TestChat::test_12_chat_crisis_keyword PASSED           [ 23%]
test_complete.py::TestChat::test_13_chat_missing_userId PASSED           [ 25%]
test_complete.py::TestChat::test_14_journal_reflection PASSED            [ 26%]
test_complete.py::TestSession::test_15_get_session_history PASSED        [ 28%]
test_complete.py::TestSession::test_16_get_invalid_session PASSED        [ 30%]
test_complete.py::TestUser::test_17_mood_summary_valid_user PASSED       [ 32%]
test_complete.py::TestUser::test_18_mood_summary_invalid_user PASSED     [ 34%]
test_complete.py::TestUser::test_19_get_recommendations PASSED           [ 36%]
test_complete.py::TestUser::test_20_exercise_feedback_no_assignment PASSED [ 38%]
test_complete.py::TestMood::test_21_log_mood_score_1 PASSED              [ 40%]
test_complete.py::TestMood::test_22_log_mood_score_5 PASSED                [ 42%]
test_complete.py::TestMood::test_23_log_mood_score_invalid_6 PASSED      [ 44%]
test_complete.py::TestMood::test_24_log_mood_score_0 PASSED              [ 46%]
test_complete.py::TestMood::test_25_get_mood_history PASSED              [ 48%]
test_complete.py::TestMood::test_26_log_behavior_all_fields PASSED       [ 50%]
test_complete.py::TestMood::test_27_log_behavior_partial_fields PASSED     [ 51%]
test_complete.py::TestMood::test_28_get_behavior_history PASSED          [ 53%]
test_complete.py::TestAssessment::test_29_create_profile PASSED          [ 55%]
test_complete.py::TestAssessment::test_30_get_profile PASSED               [ 57%]
test_complete.py::TestAssessment::test_31_get_status_before_assessment PASSED [ 59%]
test_complete.py::TestAssessment::test_32_start_session_1 PASSED         [ 61%]
test_complete.py::TestAssessment::test_33_get_next_question PASSED       [ 63%]
test_complete.py::TestAssessment::test_34_answer_question PASSED         [ 65%]
test_complete.py::TestAssessment::test_35_complete_session_1_all_answers PASSED [ 67%]
test_complete.py::TestAssessment::test_36_complete_session_2 PASSED        [ 69%]
test_complete.py::TestAssessment::test_37_complete_session_3 PASSED        [ 71%]
test_complete.py::TestAssessment::test_38_get_final_result PASSED        [ 73%]
test_complete.py::TestTTS::test_39_tts_speak_english PASSED                [ 75%]
test_complete.py::TestTTS::test_40_tts_speak_empty_text PASSED             [ 76%]
test_complete.py::TestTTS::test_41_tts_speak_urdu PASSED                   [ 78%]
test_complete.py::TestAvatar::test_42_avatar_status PASSED                 [ 80%]
test_complete.py::TestAvatar::test_43_avatar_speak PASSED                    [ 82%]
test_complete.py::TestAvatar::test_44_avatar_speak_no_text PASSED          [ 84%]
test_complete.py::TestAdmin::test_45_admin_login_valid PASSED              [ 86%]
test_complete.py::TestAdmin::test_46_admin_login_wrong_password PASSED     [ 88%]
test_complete.py::TestAdmin::test_47_admin_login_wrong_username PASSED     [ 90%]
test_complete.py::TestAdmin::test_48_get_stats_with_key PASSED             [ 92%]
test_complete.py::TestAdmin::test_49_get_stats_no_key PASSED               [ 94%]
test_complete.py::TestAdmin::test_50_get_sessions_list PASSED              [ 96%]
test_complete.py::TestAdmin::test_51_get_session_logs PASSED               [ 98%]
test_complete.py::TestAdmin::test_52_get_crisis_alerts PASSED              [100%]

====================== 52 passed in 65.01s (0:01:05) ======================
```

---

## 2. `run_tests.py` output (excerpt)

```
Sakoon AI API Tests -> http://127.0.0.1:8000

[PASS] 01. Root
       GET / -> 200
[PASS] 02. Health
       GET /health -> 200
[PASS] 03. test_01_register_new_user_success
       POST /api/v1/auth/register -> 200
       {"user": {"id": 9, "name": "pytest_bd250371cb", "languagePreference": "en", ...}}
[PASS] 06. test_03_register_missing_name
       POST /api/v1/auth/register -> 422
[PASS] 08. test_06_login_nonexistent_user
       POST /api/v1/auth/login -> 404
       {"detail": "User not found. Please register first."}
[PASS] 12. test_09_send_chat_message_success
       POST /api/v1/chat/message -> 200 (5551ms)
       {"aiResponse": "...", "mhClassification": "Stress", "mhConfidence": 0.89, ...}
[PASS] 15. test_12_chat_crisis_keyword
       POST /api/v1/chat/message -> 200 (3668ms)
       {"isCrisis": true, "helplineNumbers": [{"name": "Umang Pakistan", "number": "0311-7786264"}, ...]}
[PASS] 49. test_38_get_final_result
       POST /api/v1/assessment/scores/9 -> 200
       {"depression_score": 0, "anxiety_score": 0, "risk_level": "low", ...}
[PASS] 53. test_49_get_stats_no_key
       GET /api/v1/admin/stats -> 401

============================================================
SUMMARY
  Total:    56
  Passed:   56
  Warnings: 0
  Failed:   0
============================================================

Full results saved to: E:\Ai Virtual Assistant\backend\test_results.json
```

---

## 3. Sample request/response evidence (critical endpoints)

### Register
```http
POST /api/v1/auth/register HTTP/1.1
Content-Type: application/json

{"name": "pytest_bd250371cb", "languagePreference": "en"}
```
```http
HTTP/1.1 200 OK

{"user":{"id":9,"name":"pytest_bd250371cb","languagePreference":"en","totalSessions":0,"createdAt":"2026-05-19 23:26:25"}}
```

### Chat (stress)
```http
POST /api/v1/chat/message HTTP/1.1
Content-Type: application/json

{"userId":9,"sessionId":9,"message":"I feel stressed about my exams."}
```
```http
HTTP/1.1 200 OK

{"aiResponse":"Like everything's demanding something from you at once...\nWhat's the one stress that's loudest today?","mhClassification":"Stress","mhConfidence":0.8927882504813491,"emotionLabel":"neutral","riskLevel":"low","isCrisis":false,"helplineNumbers":[],"chatLogId":37}
```

### Crisis chat
```http
POST /api/v1/chat/message HTTP/1.1

{"userId":9,"sessionId":9,"message":"I have been thinking about suicide and want to end my life"}
```
```http
HTTP/1.1 200 OK

{"isCrisis":true,"riskLevel":"high","helplineNumbers":[{"name":"Umang Pakistan","number":"0311-7786264"},{"name":"PMHW","number":"1020"},{"name":"Sehat Tahaffuz","number":"1166"}],"aiResponse":"That's a lot to be holding right now...\n[grounding + helplines in reply]"}
```

### Mood validation failure
```http
POST /api/v1/mood/log HTTP/1.1

{"user_id":9,"mood_score":6}
```
```http
HTTP/1.1 422 Unprocessable Entity

{"detail":[{"type":"less_than_equal","loc":["body","mood_score"],"msg":"Input should be less than or equal to 5",...}]}
```

### Admin without key
```http
GET /api/v1/admin/stats HTTP/1.1
```
```http
HTTP/1.1 401 Unauthorized

{"detail":"Invalid or missing admin key"}
```

### Assessment final result
```http
GET /api/v1/assessment/result/9 HTTP/1.1
```
```http
HTTP/1.1 200 OK

{"depressionScore":0,"anxietyScore":0,"riskLevel":"low","depressionSeverity":"none_minimal","anxietySeverity":"minimal","summary":"Assessment complete. PHQ-9 score: 0 (no significant depression). GAD-7 score: 0 (minimal anxiety). Overall risk level: low.","recommendations":"..."}
```

---

## 4. How to reproduce evidence

```powershell
cd "e:\Ai Virtual Assistant\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# new terminal:
python run_tests.py --verbose
pytest test_complete.py -v
```

Attach screenshots of terminal output + this file + `test_results.json` to your FYP appendix.
