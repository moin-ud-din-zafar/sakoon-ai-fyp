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
    user_name: str = field(default_factory=lambda: f"pytest_{uuid.uuid4().hex[:10]}")
    duplicate_name: str = field(default_factory=lambda: f"dup_{uuid.uuid4().hex[:8]}")


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
) -> Tuple[int, bool]:
    """
    Start assessment session and answer every question until completed.
    Returns (assessment_id, success).
    """
    start = client.post(
        "/api/v1/assessment/start",
        json={"user_id": user_id, "session_number": session_number},
    )
    if start.status_code != 200:
        return 0, False
    data = start.json()
    aid = data.get("assessmentId")
    if not aid:
        return 0, False

    for _ in range(max_steps):
        nxt = client.get(f"/api/v1/assessment/next/{aid}")
        if nxt.status_code != 200:
            return aid, False
        payload = nxt.json()
        if payload.get("status") == "completed" or not payload.get("nextQuestion"):
            return aid, True
        q = payload["nextQuestion"]
        ans = client.post(
            "/api/v1/assessment/answer",
            json=answer_payload(aid, q),
        )
        if ans.status_code != 200:
            return aid, False
        if ans.json().get("status") == "completed":
            return aid, True
    return aid, False
