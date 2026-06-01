#!/usr/bin/env python3
"""
Sakoon AI — sequential API test runner (no pytest required).

Usage:
  python run_tests.py
  python run_tests.py --verbose
  python run_tests.py --base-url http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

from qa_helpers import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    BASE_URL,
    API_TIMEOUT,
    CRISIS_KEYWORD_SAMPLE,
    DEFAULT_TEST_PASSWORD,
    SakoonTestState,
    answer_payload,
    apply_auth_from_response,
    complete_assessment_session,
    register_payload,
)

# ANSI colors (Windows 10+ supports)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


@dataclass
class RunResult:
    index: int
    name: str
    method: str
    path: str
    passed: bool
    warning: bool = False
    status: Optional[int] = None
    elapsed_ms: float = 0.0
    message: str = ""
    response_preview: str = ""


class SequentialRunner:
    def __init__(self, base_url: str, verbose: bool = False) -> None:
        self.base = base_url.rstrip("/")
        self.verbose = verbose
        self.session = requests.Session()
        self.state = SakoonTestState()
        self.results: List[RunResult] = []
        self._index = 0

    def _preview(self, data: Any, limit: int = 300) -> str:
        if isinstance(data, bytes):
            return f"<binary {len(data)} bytes>"
        try:
            s = json.dumps(data, ensure_ascii=False, default=str)
        except Exception:
            s = str(data)
        return s if len(s) <= limit else s[:limit] + "..."

    def _run(
        self,
        name: str,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        expect: Tuple[int, ...] = (200,),
        warning_codes: Tuple[int, ...] = (),
        assert_fn: Optional[Callable[[Any, requests.Response], None]] = None,
    ) -> Optional[requests.Response]:
        self._index += 1
        url = self.base + path
        hdrs = dict(headers or {})
        t0 = time.perf_counter()
        passed = False
        warning = False
        status: Optional[int] = None
        preview = ""
        message = ""

        try:
            resp = self.session.request(
                method.upper(),
                url,
                json=json_body,
                headers=hdrs,
                timeout=API_TIMEOUT,
            )
            status = resp.status_code
            elapsed = (time.perf_counter() - t0) * 1000

            if resp.headers.get("content-type", "").startswith("application/json"):
                try:
                    body: Any = resp.json()
                except Exception:
                    body = {"_raw": resp.text[:500]}
            elif "audio" in resp.headers.get("content-type", "") or "video" in resp.headers.get("content-type", ""):
                body = {"_binary": len(resp.content), "content_type": resp.headers.get("content-type")}
            else:
                body = resp.text[:500]

            preview = self._preview(body)

            if status in expect:
                passed = True
                if assert_fn:
                    try:
                        assert_fn(body, resp)
                    except AssertionError as ae:
                        passed = False
                        message = str(ae)
            elif status in warning_codes:
                passed = True
                warning = True
                message = f"acceptable status {status}"
            else:
                message = f"expected {expect}, got {status}"

            mark = f"{YELLOW}WARN{RESET}" if warning else (f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}")
            print(f"[{mark}] {self._index:02d}. {name}")
            print(f"       {method.upper()} {path} -> {status} ({elapsed:.0f}ms)")
            if self.verbose or not passed:
                print(f"       {preview}")
            if message and (not passed or warning):
                print(f"       {message}")

            self.results.append(
                RunResult(
                    index=self._index,
                    name=name,
                    method=method.upper(),
                    path=path,
                    passed=passed,
                    warning=warning,
                    status=status,
                    elapsed_ms=elapsed,
                    message=message,
                    response_preview=preview,
                )
            )
            return resp
        except requests.exceptions.ConnectionError:
            print(f"[{RED}FAIL{RESET}] {self._index:02d}. {name}")
            print(f"       Connection refused — start uvicorn on {self.base}")
            self.results.append(
                RunResult(
                    index=self._index,
                    name=name,
                    method=method.upper(),
                    path=path,
                    passed=False,
                    message="connection refused",
                )
            )
            return None
        except Exception as exc:
            print(f"[{RED}FAIL{RESET}] {self._index:02d}. {name} — {exc}")
            self.results.append(
                RunResult(
                    index=self._index,
                    name=name,
                    method=method.upper(),
                    path=path,
                    passed=False,
                    message=str(exc),
                )
            )
            return None

    def execute_all(self) -> int:
        s = self.state
        print(f"{BOLD}{CYAN}Sakoon AI API Tests{RESET} -> {self.base}\n")

        # System
        self._run("Root", "GET", "/", expect=(200,))
        self._run("Health", "GET", "/health", expect=(200,))

        # Auth 01-08
        def _save_auth(body, _):
            apply_auth_from_response(s, body)
            assert s.user_id, "missing user.id"
            assert s.access_token, "missing accessToken"
            self.session.headers["Authorization"] = f"Bearer {s.access_token}"

        self._run(
            "test_01_register_new_user_success",
            "POST",
            "/api/v1/auth/register",
            json_body=register_payload(s.user_name, s.email, s.password),
            assert_fn=_save_auth,
        )

        dup_payload = register_payload(
            f"dup_{uuid.uuid4().hex[:6]}",
            s.duplicate_email,
            s.password,
        )

        self._run(
            "test_02_register_duplicate_email_first",
            "POST",
            "/api/v1/auth/register",
            json_body=dup_payload,
            expect=(200,),
        )
        self._run(
            "test_02_register_duplicate_email_second",
            "POST",
            "/api/v1/auth/register",
            json_body=dup_payload,
            expect=(409,),
        )

        self._run(
            "test_03_register_missing_fields",
            "POST",
            "/api/v1/auth/register",
            json_body={"name": "only_name", "languagePreference": "en"},
            expect=(422,),
        )
        self._run(
            "test_04_register_with_language_preference",
            "POST",
            "/api/v1/auth/register",
            json_body=register_payload(
                f"ur_{uuid.uuid4().hex[:8]}",
                f"ur_{uuid.uuid4().hex[:8]}@example.com",
                DEFAULT_TEST_PASSWORD,
                "ur",
            ),
            assert_fn=lambda b, _: b["user"]["languagePreference"] == "ur",
        )
        self._run(
            "test_05_login_existing_user",
            "POST",
            "/api/v1/auth/login",
            json_body={"email": s.email, "password": s.password},
            assert_fn=lambda b, _: b["user"]["id"] == s.user_id and b.get("accessToken"),
        )
        self._run(
            "test_06_login_invalid_credentials",
            "POST",
            "/api/v1/auth/login",
            json_body={"email": "ghost@example.com", "password": "WrongPass99!"},
            expect=(401,),
        )
        self._run(
            "test_07_login_empty_body",
            "POST",
            "/api/v1/auth/login",
            json_body={},
            expect=(422,),
        )
        def _save_session(body, _):
            assert body.get("session"), "no session"
            s.session_id = body["session"]["id"]

        self._run(
            "test_08_get_session_valid_user",
            "GET",
            "/api/v1/auth/session",
            assert_fn=_save_session,
        )

        # Chat 09-14
        self._run(
            "test_09_send_chat_message_success",
            "POST",
            "/api/v1/chat/message",
            json_body={
                "userId": s.user_id,
                "sessionId": s.session_id,
                "message": "I feel stressed about exams.",
            },
            assert_fn=lambda b, _: bool(b.get("aiResponse", "").strip()),
        )
        self._run(
            "test_10_chat_has_classification",
            "POST",
            "/api/v1/chat/message",
            json_body={
                "userId": s.user_id,
                "sessionId": s.session_id,
                "message": "I cannot sleep.",
            },
            assert_fn=lambda b, _: b.get("mhClassification") is not None,
        )
        self._run(
            "test_11_chat_has_emotion",
            "POST",
            "/api/v1/chat/message",
            json_body={
                "userId": s.user_id,
                "sessionId": s.session_id,
                "message": "I am sad today.",
            },
            assert_fn=lambda b, _: b.get("emotionLabel") is not None,
        )
        self._run(
            "test_12_chat_crisis_keyword",
            "POST",
            "/api/v1/chat/message",
            json_body={
                "userId": s.user_id,
                "sessionId": s.session_id,
                "message": CRISIS_KEYWORD_SAMPLE,
            },
            assert_fn=lambda b, _: b.get("isCrisis") is True and len(b.get("helplineNumbers") or []) > 0,
        )
        self._run(
            "test_13_chat_missing_userId",
            "POST",
            "/api/v1/chat/message",
            json_body={"sessionId": s.session_id, "message": "hi"},
            expect=(422,),
        )
        self._run(
            "test_14_journal_reflection",
            "POST",
            "/api/v1/chat/journal-reflection",
            json_body={"text": "I took a walk today.", "language": "en"},
            assert_fn=lambda b, _: bool(b.get("reflection", "").strip()),
        )

        # Session 15-16
        self._run(
            "test_15_get_session_history",
            "GET",
            f"/api/v1/session/{s.session_id}/history",
            assert_fn=lambda b, _: len(b.get("messages", [])) >= 2,
        )
        self._run(
            "test_16_get_invalid_session",
            "GET",
            "/api/v1/session/999999/history",
            expect=(403,),
        )

        # User 17-20
        self._run(
            "test_17_mood_summary_valid_user",
            "GET",
            f"/api/v1/user/{s.user_id}/mood-summary",
            assert_fn=lambda b, _: "summary" in b and "trend" in b,
        )
        self._run(
            "test_18_mood_summary_wrong_user",
            "GET",
            "/api/v1/user/999999/mood-summary",
            expect=(403,),
        )
        rec = self._run(
            "test_19_get_recommendations",
            "GET",
            f"/api/v1/user/{s.user_id}/recommendations",
            assert_fn=lambda b, _: isinstance(b.get("recommendations"), list),
        )
        if rec and rec.status_code == 200:
            recs = rec.json().get("recommendations") or []
            if recs:
                s.assignment_id = recs[0].get("assignmentId")
        self._run(
            "test_20_exercise_feedback_no_assignment",
            "POST",
            f"/api/v1/user/{s.user_id}/exercise-feedback",
            json_body={"assignmentId": 999999, "helped": True},
            expect=(404,),
        )

        # Mood 21-28
        self._run(
            "test_21_log_mood_score_1",
            "POST",
            "/api/v1/mood/log",
            json_body={"user_id": s.user_id, "mood_score": 1},
        )
        self._run(
            "test_22_log_mood_score_5",
            "POST",
            "/api/v1/mood/log",
            json_body={"user_id": s.user_id, "mood_score": 5},
        )
        self._run(
            "test_23_log_mood_score_invalid_6",
            "POST",
            "/api/v1/mood/log",
            json_body={"user_id": s.user_id, "mood_score": 6},
            expect=(422,),
        )
        self._run(
            "test_24_log_mood_score_0",
            "POST",
            "/api/v1/mood/log",
            json_body={"user_id": s.user_id, "mood_score": 0},
            expect=(422,),
        )
        self._run(
            "test_25_get_mood_history",
            "GET",
            f"/api/v1/mood/history/{s.user_id}",
            assert_fn=lambda b, _: len(b.get("entries", [])) >= 2,
        )
        self._run(
            "test_26_log_behavior_all_fields",
            "POST",
            "/api/v1/mood/behavior",
            json_body={
                "user_id": s.user_id,
                "sleep_hours": 7.0,
                "physical_activity": "moderate",
                "social_interaction": "active",
            },
        )
        self._run(
            "test_27_log_behavior_partial_fields",
            "POST",
            "/api/v1/mood/behavior",
            json_body={"user_id": s.user_id, "sleep_hours": 6.0},
        )
        self._run(
            "test_28_get_behavior_history",
            "GET",
            f"/api/v1/mood/behavior/{s.user_id}",
            assert_fn=lambda b, _: len(b.get("entries", [])) >= 1,
        )

        # Assessment 29-38
        self._run(
            "test_29_create_profile",
            "POST",
            "/api/v1/assessment/profile",
            json_body={
                "user_id": s.user_id,
                "age": 22,
                "gender": "other",
                "sleep_pattern": "irregular",
            },
        )
        self._run(
            "test_30_get_profile",
            "GET",
            f"/api/v1/assessment/profile/{s.user_id}",
            assert_fn=lambda b, _: b.get("profile", {}).get("user_id") == s.user_id,
        )
        self._run(
            "test_31_get_status_before_assessment",
            "GET",
            f"/api/v1/assessment/status/{s.user_id}",
            assert_fn=lambda b, _: "completedSessions" in b,
        )
        start1 = self._run(
            "test_32_start_session_1",
            "POST",
            "/api/v1/assessment/start",
            json_body={"user_id": s.user_id, "session_number": 1},
            assert_fn=lambda b, _: b.get("assessmentId") and b.get("nextQuestion"),
        )
        if start1 and start1.status_code == 200:
            s.assessment_id = start1.json().get("assessmentId")
        self._run(
            "test_33_get_next_question",
            "GET",
            f"/api/v1/assessment/next/{s.assessment_id}",
            assert_fn=lambda b, _: b.get("nextQuestion") is not None,
        )
        self._run(
            "test_34_answer_question",
            "POST",
            "/api/v1/assessment/answer",
            json_body={
                "assessment_id": s.assessment_id,
                "question_key": "s1_current_feeling",
                "answer_text": "Tired.",
            },
        )
        for sn, label in [(1, "35"), (2, "36"), (3, "37")]:
            aid, ok = self._complete_session(sn)
            self.results.append(
                RunResult(
                    index=self._index + 1,
                    name=f"test_{label}_complete_session_{sn}",
                    method="FLOW",
                    path=f"/assessment/session/{sn}",
                    passed=ok,
                    message="" if ok else f"session {sn} incomplete",
                )
            )
            self._index += 1
            mark = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
            print(f"[{mark}] {self._index:02d}. test_{label}_complete_session_{sn}")
            print(f"       complete session {sn} -> {'ok' if ok else 'failed'}")
            if ok:
                s.assessment_id = aid

        self._run(
            "test_38_get_final_result",
            "POST",
            f"/api/v1/assessment/scores/{s.user_id}",
            expect=(200,),
        )
        self._run(
            "test_38b_get_final_result",
            "GET",
            f"/api/v1/assessment/result/{s.user_id}",
            assert_fn=lambda b, _: b.get("depressionScore") is not None and b.get("anxietyScore") is not None,
        )

        # TTS 39-41
        self._run(
            "test_39_tts_speak_english",
            "POST",
            "/api/v1/tts/speak",
            json_body={"text": "Hello test.", "language": "en"},
            expect=(200,),
            warning_codes=(503,),
        )
        self._run(
            "test_40_tts_speak_empty_text",
            "POST",
            "/api/v1/tts/speak",
            json_body={"text": ""},
            expect=(422, 400, 503),
            warning_codes=(503,),
        )
        self._run(
            "test_41_tts_speak_urdu",
            "POST",
            "/api/v1/tts/speak",
            json_body={"text": "Salam", "language": "ur"},
            expect=(200,),
            warning_codes=(503,),
        )

        # Avatar 42-44
        self._run(
            "test_42_avatar_status",
            "GET",
            "/api/v1/avatar/status",
            assert_fn=lambda b, _: "wav2lipReady" in b,
        )
        self._run(
            "test_43_avatar_speak",
            "POST",
            "/api/v1/avatar/speak",
            json_body={"text": "Hi", "language": "en"},
            expect=(200,),
            warning_codes=(503,),
        )
        self._run(
            "test_44_avatar_speak_no_text",
            "POST",
            "/api/v1/avatar/speak",
            json_body={"text": "  "},
            expect=(422,),
        )

        # Admin 45-52
        def _save_admin_key(body, _):
            assert body.get("adminKey")
            s.admin_key = body["adminKey"]

        self._run(
            "test_45_admin_login_valid",
            "POST",
            "/api/v1/admin/login",
            json_body={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            assert_fn=_save_admin_key,
        )
        self._run(
            "test_46_admin_login_wrong_password",
            "POST",
            "/api/v1/admin/login",
            json_body={"username": ADMIN_USERNAME, "password": "wrong"},
            expect=(401,),
        )
        self._run(
            "test_47_admin_login_wrong_username",
            "POST",
            "/api/v1/admin/login",
            json_body={"username": "wrong", "password": ADMIN_PASSWORD},
            expect=(401,),
        )
        hdr = {"X-Admin-Key": s.admin_key or ""}
        self._run(
            "test_48_get_stats_with_key",
            "GET",
            "/api/v1/admin/stats",
            headers=hdr,
            assert_fn=lambda b, _: "totalSessions" in b,
        )
        self._run(
            "test_49_get_stats_no_key",
            "GET",
            "/api/v1/admin/stats",
            expect=(401,),
        )
        self._run(
            "test_50_get_sessions_list",
            "GET",
            "/api/v1/admin/sessions",
            headers=hdr,
            assert_fn=lambda b, _: isinstance(b.get("sessions"), list),
        )
        self._run(
            "test_51_get_session_logs",
            "GET",
            f"/api/v1/admin/sessions/{s.session_id}/logs",
            headers=hdr,
            assert_fn=lambda b, _: isinstance(b.get("messages"), list),
        )
        self._run(
            "test_52_get_crisis_alerts",
            "GET",
            "/api/v1/admin/crisis-alerts",
            headers=hdr,
            assert_fn=lambda b, _: isinstance(b.get("alerts"), list),
        )

        return self._summary()

    def _complete_session(self, session_number: int) -> Tuple[int, bool]:
        """Use qa_helpers with a httpx-like adapter over requests.Session."""

        class _ClientAdapter:
            def __init__(self, runner: SequentialRunner) -> None:
                self._r = runner

            def post(self, path: str, json: Optional[Dict] = None):
                return self._r.session.post(
                    self._r.base + path, json=json, timeout=API_TIMEOUT
                )

            def get(self, path: str):
                return self._r.session.get(
                    self._r.base + path, timeout=API_TIMEOUT
                )

        return complete_assessment_session(
            _ClientAdapter(self), self.state.user_id, session_number
        )

    def _summary(self) -> int:
        passed = sum(1 for r in self.results if r.passed and not r.warning)
        warnings = sum(1 for r in self.results if r.warning)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        print(f"\n{BOLD}{'=' * 60}{RESET}")
        print(f"{BOLD}SUMMARY{RESET}")
        print(f"  Total:    {total}")
        print(f"  {GREEN}Passed:{RESET}   {passed}")
        print(f"  {YELLOW}Warnings:{RESET} {warnings}")
        print(f"  {RED}Failed:{RESET}   {failed}")
        print(f"{'=' * 60}\n")

        out = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "base_url": self.base,
            "total": total,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "state": {
                "user_id": self.state.user_id,
                "session_id": self.state.session_id,
                "assessment_id": self.state.assessment_id,
                "admin_key_set": bool(self.state.admin_key),
            },
            "results": [
                {
                    "index": r.index,
                    "name": r.name,
                    "method": r.method,
                    "path": r.path,
                    "passed": r.passed,
                    "warning": r.warning,
                    "status": r.status,
                    "elapsed_ms": r.elapsed_ms,
                    "message": r.message,
                    "response_preview": r.response_preview,
                }
                for r in self.results
            ],
        }
        out_path = os.path.join(os.path.dirname(__file__), "test_results.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"Full results saved to: {out_path}")

        return 0 if failed == 0 else 1


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Sakoon AI sequential API tests")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()

    runner = SequentialRunner(args.base_url, verbose=args.verbose)
    return runner.execute_all()


if __name__ == "__main__":
    sys.exit(main())
