"""Shared helpers for Sakoon AI API QA (pytest + run_tests.py)."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import httpx

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "sakoon123")
API_TIMEOUT = float(os.getenv("API_TEST_TIMEOUT", "120"))
DEFAULT_TEST_PASSWORD = os.getenv("TEST_USER_PASSWORD", "TestPass123!")

# From app/core/constants.py
CRISIS_KEYWORD_SAMPLE = "I have been thinking about suicide and want to end my life"


@dataclass
class SakoonTestState:
    """Mutable state shared across ordered integration tests."""

    user_id: Optional[int] = None
    session_id: Optional[int] = None
    assessment_id: Optional[int] = None
    assignment_id: Optional[int] = None
    admin_key: Optional[str] = None
    access_token: Optional[str] = None
    user_name: str = field(default_factory=lambda: f"pytest_{uuid.uuid4().hex[:10]}")
    email: str = field(default_factory=lambda: f"pytest_{uuid.uuid4().hex[:10]}@example.com")
    password: str = field(default_factory=lambda: DEFAULT_TEST_PASSWORD)
    duplicate_email: str = field(
        default_factory=lambda: f"dup_{uuid.uuid4().hex[:8]}@example.com"
    )


def auth_headers(state: SakoonTestState) -> Dict[str, str]:
    """Authorization header for protected routes."""
    if not state.access_token:
        return {}
    return {"Authorization": f"Bearer {state.access_token}"}


def register_payload(
    name: str,
    email: str,
    password: str = DEFAULT_TEST_PASSWORD,
    language: str = "en",
) -> Dict[str, Any]:
    return {
        "name": name,
        "email": email,
        "password": password,
        "languagePreference": language,
    }


def apply_auth_from_response(state: SakoonTestState, body: Dict[str, Any]) -> None:
    """Store user id and JWT from register/login response."""
    state.access_token = body.get("accessToken")
    user = body.get("user") or {}
    if user.get("id"):
        state.user_id = user["id"]


def register_and_login(
    client: httpx.Client,
    state: SakoonTestState,
    *,
    name: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
) -> Dict[str, Any]:
    """Register a new user and set state token + user_id. Returns response JSON."""
    payload = register_payload(
        name or state.user_name,
        email or state.email,
        password or state.password,
    )
    r = client.post("/api/v1/auth/register", json=payload)
    if r.status_code != 200:
        raise RuntimeError(f"Register failed {r.status_code}: {r.text}")
    body = r.json()
    apply_auth_from_response(state, body)
    return body


def fetch_session(client: httpx.Client, state: SakoonTestState) -> Dict[str, Any]:
    """GET /auth/session (JWT) and set state.session_id."""
    r = client.get("/api/v1/auth/session", headers=auth_headers(state))
    if r.status_code != 200:
        raise RuntimeError(f"Session failed {r.status_code}: {r.text}")
    data = r.json()
    sess = data.get("session")
    if sess and sess.get("id"):
        state.session_id = sess["id"]
    return data


def assert_server_up(client: httpx.Client) -> None:
    r = client.get("/health")
    if r.status_code != 200:
        raise RuntimeError(
            f"API not healthy at {BASE_URL} (status {r.status_code}). "
            "Start: python -m uvicorn app.main:app --reload --port 8000"
        )


def answer_payload(assessment_id: int, question: Dict[str, Any]) -> Dict[str, Any]:
    """Build POST /assessment/answer body from nextQuestion object."""
    key = question["key"]
    qtype = question.get("type", "select")
    if qtype == "text":
        return {
            "assessment_id": assessment_id,
            "question_key": key,
            "answer_text": "Automated test response.",
        }
    opts = question.get("options") or []
    value = opts[0]["value"] if opts else 0
    return {
        "assessment_id": assessment_id,
        "question_key": key,
        "answer_value": value,
    }


def complete_assessment_session(
    client: httpx.Client,
    user_id: int,
    session_number: int,
    max_steps: int = 100,
    headers: Optional[Dict[str, str]] = None,
) -> Tuple[int, bool]:
    """
    Start assessment session and answer every question until completed.
    Returns (assessment_id, success).
    """
    hdrs = headers or {}
    start = client.post(
        "/api/v1/assessment/start",
        json={"user_id": user_id, "session_number": session_number},
        headers=hdrs,
    )
    if start.status_code != 200:
        return 0, False
    data = start.json()
    aid = data.get("assessmentId")
    if not aid:
        return 0, False

    for _ in range(max_steps):
        nxt = client.get(f"/api/v1/assessment/next/{aid}", headers=hdrs)
        if nxt.status_code != 200:
            return aid, False
        payload = nxt.json()
        if payload.get("status") == "completed" or not payload.get("nextQuestion"):
            return aid, True
        q = payload["nextQuestion"]
        ans = client.post(
            "/api/v1/assessment/answer",
            json=answer_payload(aid, q),
            headers=hdrs,
        )
        if ans.status_code != 200:
            return aid, False
        if ans.json().get("status") == "completed":
            return aid, True
    return aid, False
