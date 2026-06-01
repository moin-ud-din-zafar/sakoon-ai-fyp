"""Pytest fixtures for Sakoon AI API integration tests."""

from __future__ import annotations

import os

import httpx
import pytest
from dotenv import load_dotenv

from qa_helpers import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    BASE_URL,
    API_TIMEOUT,
    SakoonTestState,
    assert_server_up,
)

load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def client(base_url: str, state: SakoonTestState) -> httpx.Client:
    def _attach_bearer(request: httpx.Request) -> None:
        if not state.access_token:
            return
        path = request.url.path or ""
        # Do not send user JWT to public auth, admin, or health routes
        skip_prefixes = (
            "/health",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/admin/",
        )
        if path == "/" or any(path.startswith(p) for p in skip_prefixes):
            return
        request.headers["Authorization"] = f"Bearer {state.access_token}"

    with httpx.Client(
        base_url=base_url,
        timeout=API_TIMEOUT,
        event_hooks={"request": [_attach_bearer]},
    ) as c:
        assert_server_up(c)
        yield c


@pytest.fixture(scope="session")
def state() -> SakoonTestState:
    return SakoonTestState()


@pytest.fixture(scope="session")
def admin_credentials() -> tuple[str, str]:
    return ADMIN_USERNAME, ADMIN_PASSWORD


def pytest_configure(config):  # noqa: D103
    config.addinivalue_line("markers", "smoke: quick smoke tests")
    config.addinivalue_line("markers", "regression: full regression suite")
    config.addinivalue_line("markers", "critical: safety-critical paths")


def pytest_collection_modifyitems(session, config, items):
    """Run test_01 .. test_52 in numeric order across all classes."""
    import re

    def sort_key(item):
        m = re.search(r"test_(\d+)_", item.name)
        return int(m.group(1)) if m else 9999

    items.sort(key=sort_key)
