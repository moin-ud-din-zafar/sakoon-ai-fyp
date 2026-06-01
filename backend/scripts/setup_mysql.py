"""
Apply database/init_sakoon.sql to MySQL using credentials from backend/.env.

Usage (from repo root or backend folder):
  python backend/scripts/setup_mysql.py
  cd backend && python scripts/setup_mysql.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Load backend/.env before importing app config
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_ROOT.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from dotenv import load_dotenv

load_dotenv(_BACKEND_ROOT / ".env")


def _strip_sql_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _split_statements(sql: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    for line in sql.splitlines():
        buf.append(line)
        if line.rstrip().endswith(";"):
            stmt = "\n".join(buf).strip()
            if stmt:
                parts.append(stmt.rstrip(";").strip())
            buf = []
    tail = "\n".join(buf).strip()
    if tail:
        parts.append(tail.rstrip(";").strip())
    return [p for p in parts if p]


def main() -> int:
    try:
        import mysql.connector
    except ImportError:
        print("Install: pip install mysql-connector-python")
        return 1

    host = os.getenv("DATABASE_HOST", "localhost")
    port = int(os.getenv("DATABASE_PORT", "3306"))
    user = os.getenv("DATABASE_USER", "root")
    password = os.getenv("DATABASE_PASSWORD", "")
    database = os.getenv("DATABASE_NAME", "sakoon")

    sql_path = _REPO_ROOT / "database" / "init_sakoon.sql"
    if not sql_path.is_file():
        print(f"Missing SQL file: {sql_path}")
        return 1

    raw = sql_path.read_text(encoding="utf-8")
    cleaned = _strip_sql_comments(raw)
    statements = _split_statements(cleaned)

    print(f"Connecting to MySQL {host}:{port} as {user!r} …")
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
        )
    except mysql.connector.Error as e:
        print(f"Connection failed: {e}")
        print("Check MySQL is running and DATABASE_* in backend/.env are correct.")
        return 1

    cur = conn.cursor(buffered=True)
    for stmt in statements:
        try:
            cur.execute(stmt)
            if cur.description:
                cur.fetchall()
        except mysql.connector.Error as e:
            if e.errno == 1007:  # ER_DB_CREATE_EXISTS
                continue
            if e.errno == 1050:  # ER_TABLE_EXISTS_ERROR
                print(f"(skip existing) {stmt[:60]}…")
                continue
            print(f"Error on statement:\n{stmt[:200]}…\n{e}")
            conn.rollback()
            cur.close()
            conn.close()
            return 1

    conn.commit()
    cur.close()
    conn.close()

    # Verify target database
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        cur = conn.cursor(buffered=True)
        cur.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = %s",
            (database, "users"),
        )
        ok = cur.fetchone()[0] == 1
        cur.close()
        conn.close()
        if ok:
            print(f"Database {database!r} is ready (users table present).")
        else:
            print(f"Warning: could not confirm tables in {database!r}.")
    except mysql.connector.Error as e:
        print(f"Verify step failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
