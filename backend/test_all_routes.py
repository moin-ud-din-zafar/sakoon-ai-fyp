#!/usr/bin/env python3
"""
Sakoon AI — full API route tester.

Usage (server must be running first):
  cd backend
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

  # another terminal:
  cd backend
  python test_all_routes.py

Optional env:
  API_BASE_URL=http://127.0.0.1:8000
  ADMIN_USERNAME=admin
  ADMIN_PASSWORD=sakoon123
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    import httpx
except ImportError:
    print("Install httpx: pip install httpx")
    sys.exit(1)

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "sakoon123")
TIMEOUT = float(os.getenv("API_TEST_TIMEOUT", "90"))


@dataclass
class TestResult:
    name: str
    method: str
    path: str
    passed: bool
    status: Optional[int] = None
    detail: str = ""
    response_preview: str = ""


class Runner:
    def __init__(self) -> None:
        self.results: List[TestResult] = []
        self.client = httpx.Client(base_url=BASE_URL, timeout=TIMEOUT)
        self.admin_key: Optional[str] = None
        self.user_id: Optional[int] = None
        self.session_id: Optional[int] = None
        self.assessment_id: Optional[int] = None
        self.assignment_id: Optional[int] = None
        self.unique_name = f"test_user_{uuid.uuid4().hex[:8]}"

    def close(self) -> None:
        self.client.close()

    def _preview(self, data: Any, limit: int = 400) -> str:
        try:
            s = json.dumps(data, ensure_ascii=False, default=str)
        except Exception:
            s = str(data)
        return s if len(s) <= limit else s[:limit] + "..."

    def run(
        self,
        name: str,
        method: str,
        path: str,
        *,
        expect: Tuple[int, ...] = (200,),
        json_body: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        content: Optional[bytes] = None,
        allow_skip: bool = False,
        skip_reason: str = "",
    ) -> Optional[httpx.Response]:
        url = path if path.startswith("http") else path
        hdrs = dict(headers or {})
        t0 = time.perf_counter()
        try:
            resp = self.client.request(
                method.upper(),
                url,
                json=json_body,
                headers=hdrs,
                content=content,
            )
            elapsed = (time.perf_counter() - t0) * 1000
            ok = resp.status_code in expect
            body: Any
            try:
                body = resp.json()
            except Exception:
                body = {"_raw": resp.text[:500], "_bytes": len(resp.content)}

            detail = f"{resp.status_code} ({elapsed:.0f}ms)"
            if not ok:
                detail += f" - expected {expect}"

            self.results.append(
                TestResult(
                    name=name,
                    method=method.upper(),
                    path=path,
                    passed=ok,
                    status=resp.status_code,
                    detail=detail,
                    response_preview=self._preview(body),
                )
            )
            mark = "PASS" if ok else "FAIL"
            print(f"[{mark}] {name}")
            print(f"       {method.upper()} {path} -> {resp.status_code}")
            preview = self._preview(body, 220).encode("ascii", errors="replace").decode("ascii")
            print(f"       {preview}")
            if not ok and allow_skip:
                print(f"       (optional) {skip_reason}")
            return resp
        except httpx.ConnectError:
            self.results.append(
                TestResult(
                    name=name,
                    method=method.upper(),
                    path=path,
                    passed=False,
                    detail="Connection refused - is uvicorn running?",
                )
            )
            print(f"[FAIL] {name} - cannot connect to {BASE_URL}")
            return None
        except Exception as exc:
            self.results.append(
                TestResult(
                    name=name,
                    method=method.upper(),
                    path=path,
                    passed=False,
                    detail=str(exc),
                )
            )
            print(f"[FAIL] {name} - {exc}")
            return None

    def summary(self) -> int:
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        failed = [r for r in self.results if not r.passed]
        print("\n" + "=" * 60)
        print(f"RESULTS: {passed}/{total} passed")
        if failed:
            print("\nFailed:")
            for r in failed:
                print(f"  - {r.name}: {r.detail}")
        print("=" * 60)
        return 0 if passed == total else 1


def complete_assessment_session(r: Runner, user_id: int, session_number: int) -> bool:
    """Answer every question in one assessment session via API."""
    resp = r.run(
        f"Assessment start session {session_number}",
        "POST",
        "/api/v1/assessment/start",
        json_body={"user_id": user_id, "session_number": session_number},
        expect=(200,),
    )
    if not resp or resp.status_code != 200:
        return False
    data = resp.json()
    aid = data.get("assessmentId")
    if not aid:
        return False
    r.assessment_id = aid

    for _ in range(80):
        nxt = r.run(
            f"Assessment next (session {session_number})",
            "GET",
            f"/api/v1/assessment/next/{aid}",
            expect=(200,),
        )
        if not nxt or nxt.status_code != 200:
            return False
        payload = nxt.json()
        if payload.get("status") == "completed" or not payload.get("nextQuestion"):
            break
        q = payload["nextQuestion"]
        key = q["key"]
        qtype = q.get("type", "select")
        if qtype == "text":
            body = {
                "assessment_id": aid,
                "question_key": key,
                "answer_text": "Test answer for automated run.",
            }
        else:
            opts = q.get("options") or []
            val = opts[0]["value"] if opts else 0
            body = {
                "assessment_id": aid,
                "question_key": key,
                "answer_value": val,
            }
        ans = r.run(
            f"Assessment answer {key}",
            "POST",
            "/api/v1/assessment/answer",
            json_body=body,
            expect=(200,),
        )
        if not ans or ans.status_code != 200:
            return False
        if ans.json().get("status") == "completed":
            break
    return True


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    print(f"Sakoon AI API tests -> {BASE_URL}\n")
    r = Runner()

    # ── Root / health ─────────────────────────────────────────────────────
    r.run("Root", "GET", "/")
    r.run("Health", "GET", "/health")

    # ── Auth flow ─────────────────────────────────────────────────────────
    reg = r.run(
        "Register user",
        "POST",
        "/api/v1/auth/register",
        json_body={"name": r.unique_name, "languagePreference": "en"},
        expect=(200,),
    )
    if reg and reg.status_code == 200:
        r.user_id = reg.json()["user"]["id"]

    r.run(
        "Login user (success)",
        "POST",
        "/api/v1/auth/login",
        json_body={"name": r.unique_name},
        expect=(200,),
    )
    r.run(
        "Login user (404)",
        "POST",
        "/api/v1/auth/login",
        json_body={"name": "nonexistent_user_xyz_999"},
        expect=(404,),
    )

    if r.user_id:
        sess = r.run(
            "Get or create session",
            "GET",
            f"/api/v1/auth/session/{r.user_id}",
            expect=(200,),
        )
        if sess and sess.status_code == 200:
            s = sess.json().get("session")
            if s:
                r.session_id = s["id"]

    # ── Chat (may fail without ML models / heavy HF download) ───────────────
    if r.user_id and r.session_id:
        r.run(
            "Chat message",
            "POST",
            "/api/v1/chat/message",
            json_body={
                "userId": r.user_id,
                "sessionId": r.session_id,
                "message": "I feel a bit stressed about exams.",
            },
            expect=(200, 500),
            allow_skip=True,
            skip_reason="Needs backend/models/*.joblib — run train_model.py",
        )
        r.run(
            "Chat empty message",
            "POST",
            "/api/v1/chat/message",
            json_body={"userId": r.user_id, "sessionId": r.session_id, "message": "   "},
            expect=(200,),
        )
        r.run(
            "Journal reflection",
            "POST",
            "/api/v1/chat/journal-reflection",
            json_body={"text": "Today I took a short walk.", "language": "en"},
            expect=(200,),
        )

    # ── Session history ───────────────────────────────────────────────────
    if r.session_id:
        r.run(
            "Session chat history",
            "GET",
            f"/api/v1/session/{r.session_id}/history",
            expect=(200,),
        )

    # ── User routes ───────────────────────────────────────────────────────
    if r.user_id:
        r.run(
            "User mood summary",
            "GET",
            f"/api/v1/user/{r.user_id}/mood-summary",
            expect=(200,),
        )
        rec = r.run(
            "User recommendations",
            "GET",
            f"/api/v1/user/{r.user_id}/recommendations",
            expect=(200,),
        )
        if rec and rec.status_code == 200:
            recs = rec.json().get("recommendations") or []
            if recs and recs[0].get("assignmentId"):
                r.assignment_id = recs[0]["assignmentId"]

        r.run(
            "Exercise feedback",
            "POST",
            f"/api/v1/user/{r.user_id}/exercise-feedback",
            json_body={
                "assignmentId": r.assignment_id,
                "sessionId": r.session_id,
                "helped": True,
            },
            expect=(200,),
        )
        r.run(
            "Exercise feedback (404 assignment)",
            "POST",
            f"/api/v1/user/{r.user_id}/exercise-feedback",
            json_body={"assignmentId": 999999, "helped": False},
            expect=(404,),
        )

    # ── Mood routes ───────────────────────────────────────────────────────
    if r.user_id:
        r.run(
            "Mood log",
            "POST",
            "/api/v1/mood/log",
            json_body={"user_id": r.user_id, "mood_score": 4, "note": "Feeling okay"},
            expect=(200,),
        )
        r.run(
            "Mood history",
            "GET",
            f"/api/v1/mood/history/{r.user_id}",
            expect=(200,),
        )
        r.run(
            "Behavior log",
            "POST",
            "/api/v1/mood/behavior",
            json_body={
                "user_id": r.user_id,
                "sleep_hours": 7.5,
                "physical_activity": "light",
                "social_interaction": "moderate",
            },
            expect=(200,),
        )
        r.run(
            "Behavior log (422 invalid activity)",
            "POST",
            "/api/v1/mood/behavior",
            json_body={"user_id": r.user_id, "physical_activity": "invalid"},
            expect=(422,),
        )
        r.run(
            "Behavior history",
            "GET",
            f"/api/v1/mood/behavior/{r.user_id}",
            expect=(200,),
        )
        r.run(
            "Mood log (404 user)",
            "POST",
            "/api/v1/mood/log",
            json_body={"user_id": 999999, "mood_score": 3},
            expect=(404,),
        )

    # ── Assessment ────────────────────────────────────────────────────────
    if r.user_id:
        r.run(
            "Assessment save profile",
            "POST",
            "/api/v1/assessment/profile",
            json_body={
                "user_id": r.user_id,
                "age": 22,
                "gender": "other",
                "sleep_pattern": "irregular",
                "past_therapy": False,
            },
            expect=(200,),
        )
        r.run(
            "Assessment get profile",
            "GET",
            f"/api/v1/assessment/profile/{r.user_id}",
            expect=(200,),
        )
        r.run(
            "Assessment status",
            "GET",
            f"/api/v1/assessment/status/{r.user_id}",
            expect=(200,),
        )
        r.run(
            "Assessment scores before complete (400)",
            "POST",
            f"/api/v1/assessment/scores/{r.user_id}",
            expect=(400,),
        )
        r.run(
            "Assessment result before complete (404)",
            "GET",
            f"/api/v1/assessment/result/{r.user_id}",
            expect=(404,),
        )
        r.run(
            "Assessment answer missing fields (422)",
            "POST",
            "/api/v1/assessment/answer",
            json_body={"assessment_id": 1, "question_key": "x"},
            expect=(400, 404, 422),
        )

        print("\n--- Completing all 3 assessment sessions (may take a minute) ---\n")
        all_ok = True
        for sn in (1, 2, 3):
            if not complete_assessment_session(r, r.user_id, sn):
                all_ok = False
                print(f"Warning: session {sn} did not complete fully")
                break

        if all_ok:
            r.run(
                "Assessment calculate scores",
                "POST",
                f"/api/v1/assessment/scores/{r.user_id}",
                expect=(200,),
            )
            r.run(
                "Assessment get result",
                "GET",
                f"/api/v1/assessment/result/{r.user_id}",
                expect=(200,),
            )

    # ── TTS ───────────────────────────────────────────────────────────────
    tts = r.run(
        "TTS speak",
        "POST",
        "/api/v1/tts/speak",
        json_body={"text": "Hello from Sakoon test.", "language": "en"},
        expect=(200, 503),
    )
    r.run(
        "TTS speak empty (edge)",
        "POST",
        "/api/v1/tts/speak",
        json_body={"text": " "},
        expect=(200, 422, 503),
    )

    # ── Avatar ────────────────────────────────────────────────────────────
    r.run("Avatar status", "GET", "/api/v1/avatar/status", expect=(200,))
    av = r.run(
        "Avatar speak",
        "POST",
        "/api/v1/avatar/speak",
        json_body={"text": "Hello.", "language": "en"},
        expect=(200, 503),
    )
    if av and av.status_code == 200:
        mode = av.headers.get("x-avatar-mode", "?")
        print(f"       Avatar mode: {mode}, bytes: {len(av.content)}", flush=True)

    r.run(
        "Avatar speak blank (422)",
        "POST",
        "/api/v1/avatar/speak",
        json_body={"text": "   "},
        expect=(422,),
    )

    # ── Admin ─────────────────────────────────────────────────────────────
    adm = r.run(
        "Admin login",
        "POST",
        "/api/v1/admin/login",
        json_body={"username": ADMIN_USER, "password": ADMIN_PASS},
        expect=(200, 401),
    )
    if adm and adm.status_code == 200:
        r.admin_key = adm.json().get("adminKey")

    r.run(
        "Admin stats (no key - 401)",
        "GET",
        "/api/v1/admin/stats",
        expect=(401,),
    )

    if r.admin_key:
        hdr = {"X-Admin-Key": r.admin_key}
        r.run(
            "Admin stats",
            "GET",
            "/api/v1/admin/stats",
            headers=hdr,
            expect=(200,),
        )
        r.run(
            "Admin list sessions",
            "GET",
            "/api/v1/admin/sessions",
            headers=hdr,
            expect=(200,),
        )
        r.run(
            "Admin crisis alerts",
            "GET",
            "/api/v1/admin/crisis-alerts",
            headers=hdr,
            expect=(200,),
        )
        if r.session_id:
            r.run(
                "Admin session logs",
                "GET",
                f"/api/v1/admin/sessions/{r.session_id}/logs",
                headers=hdr,
                expect=(200,),
            )

    r.run(
        "Admin login wrong password",
        "POST",
        "/api/v1/admin/login",
        json_body={"username": ADMIN_USER, "password": "wrong"},
        expect=(401,),
    )

    r.close()
    return r.summary()


if __name__ == "__main__":
    sys.exit(main())
