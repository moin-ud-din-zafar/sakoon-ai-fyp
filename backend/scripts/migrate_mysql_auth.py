#!/usr/bin/env python3
"""Add email + password_hash columns to existing MySQL users table."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.db_service import _migrate_mysql_auth_columns, get_db  # noqa: E402


def main() -> None:
    with get_db() as conn:
        _migrate_mysql_auth_columns(conn)
    print("MySQL auth columns migration complete.")


if __name__ == "__main__":
    main()
