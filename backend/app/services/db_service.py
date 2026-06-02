"""Database service for Sakoon AI. Uses SQLite for dev, MySQL for production."""

import json
import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from app.config import USE_SQLITE, SQLITE_PATH, MYSQL_CONFIG

if not USE_SQLITE:
    import mysql.connector


def _get_sqlite_conn():
    """Get SQLite connection. Creates DB and tables if needed."""
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    _init_sqlite_schema(conn)
    return conn


def _init_sqlite_schema(conn: sqlite3.Connection):
    """Create tables for SQLite (compatible schema with MySQL)."""
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            profile_image_url TEXT,
            language_preference VARCHAR(10) DEFAULT 'en',
            total_sessions INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_no INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            stress_level INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, session_no)
        );
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            mh_classification VARCHAR(50),
            mh_confidence REAL,
            emotion_label VARCHAR(50),
            risk_level VARCHAR(20) DEFAULT 'low',
            is_crisis INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
        CREATE TABLE IF NOT EXISTS emotion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            emotion_label VARCHAR(50) NOT NULL,
            confidence REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_type VARCHAR(50) NOT NULL,
            content TEXT,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS exercise_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id INTEGER,
            assignment_id INTEGER,
            helped INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- ── Phase 2: Clinical Assessment ───────────────────────────────────────
        CREATE TABLE IF NOT EXISTS patient_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            age INTEGER,
            gender VARCHAR(20),
            sleep_pattern VARCHAR(50),
            stress_triggers TEXT,
            past_therapy INTEGER DEFAULT 0,
            medications TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            assessment_type VARCHAR(50) NOT NULL,
            session_number INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'in_progress',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS assessment_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            question_key VARCHAR(100) NOT NULL,
            question_text TEXT NOT NULL,
            answer_value INTEGER,
            answer_text TEXT,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments(id)
        );

        CREATE TABLE IF NOT EXISTS assessment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            depression_score INTEGER DEFAULT 0,
            anxiety_score INTEGER DEFAULT 0,
            risk_level VARCHAR(20) DEFAULT 'low',
            depression_severity VARCHAR(30),
            anxiety_severity VARCHAR(30),
            summary TEXT,
            recommendations TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- ── Phase 2: Daily Mood Log ─────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood_score INTEGER NOT NULL,
            note TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- ── Phase 2: Behavior Tracking ──────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS behavior_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sleep_hours REAL,
            physical_activity VARCHAR(50),
            social_interaction VARCHAR(50),
            notes TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Password reset tokens
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash VARCHAR(128) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    _migrate_sqlite_auth_columns(conn)
    conn.commit()


def _migrate_sqlite_auth_columns(conn: sqlite3.Connection) -> None:
    """Add auth/profile columns to existing SQLite DBs created before JWT auth."""
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    cols = {row[1] for row in cur.fetchall()}
    if "email" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
    if "password_hash" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
    if "profile_image_url" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN profile_image_url TEXT")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash VARCHAR(128) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )"""
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_password_resets_user ON password_resets(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_password_resets_expires ON password_resets(expires_at)")
    conn.commit()


_mysql_auth_migrated = False


def _migrate_mysql_auth_columns(conn) -> None:
    """Add auth/profile/reset tables to existing MySQL DBs created before JWT auth."""
    global _mysql_auth_migrated
    if _mysql_auth_migrated:
        return
    cur = conn.cursor()
    cur.execute("SHOW COLUMNS FROM users LIKE 'email'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL")
    cur.execute("SHOW COLUMNS FROM users LIKE 'password_hash'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL")
    cur.execute("SHOW COLUMNS FROM users LIKE 'profile_image_url'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE users ADD COLUMN profile_image_url TEXT NULL")
    try:
        cur.execute(
            "CREATE UNIQUE INDEX idx_users_email ON users (email)"
        )
    except Exception:
        pass
    cur.execute(
        """CREATE TABLE IF NOT EXISTS password_resets (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            token_hash VARCHAR(128) NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            used_at DATETIME NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_password_resets_user (user_id),
            INDEX idx_password_resets_expires (expires_at),
            CONSTRAINT fk_password_resets_user FOREIGN KEY (user_id) REFERENCES users(id)
        )"""
    )
    conn.commit()
    _mysql_auth_migrated = True


@contextmanager
def get_db() -> Generator:
    """Database connection context manager."""
    if USE_SQLITE:
        conn = _get_sqlite_conn()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    else:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        _migrate_mysql_auth_columns(conn)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def execute_one(
    query: str,
    params: tuple = (),
    fetch: bool = True,
) -> Optional[Dict[str, Any]]:
    """Execute query and fetch one row."""
    with get_db() as conn:
        cur = conn.cursor(dictionary=True) if not USE_SQLITE else conn.cursor()
        cur.execute(query, params)
        if fetch:
            row = cur.fetchone()
            if USE_SQLITE and row:
                return dict(row)
            return row
    return None


def execute_many(
    query: str,
    params: tuple = (),
) -> List[Dict[str, Any]]:
    """Execute query and fetch all rows."""
    with get_db() as conn:
        cur = conn.cursor(dictionary=True) if not USE_SQLITE else conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        if USE_SQLITE and rows:
            return [dict(r) for r in rows]
        return rows or []


def execute_insert(query: str, params: tuple = ()) -> int:
    """Execute insert and return last row id."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid or 0


# --- CRUD operations ---

def create_user(name: str, language_preference: str = "en") -> int:
    """Deprecated: use create_user_account. Kept for internal compatibility."""
    raise RuntimeError("create_user is deprecated; use create_user_account with email and password")


def create_user_account(
    name: str,
    email: str,
    password_hash: str,
    language_preference: str = "en",
) -> int:
    """Create user with email and hashed password; return new user id."""
    clean_email = email.strip().lower()
    return execute_insert(
        "INSERT INTO users (name, email, password_hash, language_preference) VALUES (?, ?, ?, ?)"
        if USE_SQLITE
        else "INSERT INTO users (name, email, password_hash, language_preference) VALUES (%s, %s, %s, %s)",
        (name.strip(), clean_email, password_hash, language_preference),
    )


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by id."""
    return execute_one(
        "SELECT * FROM users WHERE id = ?" if USE_SQLITE else "SELECT * FROM users WHERE id = %s",
        (user_id,),
    )


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email (case-insensitive)."""
    clean = (email or "").strip().lower()
    if not clean:
        return None
    return execute_one(
        "SELECT * FROM users WHERE LOWER(TRIM(email)) = ? LIMIT 1"
        if USE_SQLITE
        else "SELECT * FROM users WHERE LOWER(TRIM(email)) = %s LIMIT 1",
        (clean,),
    )


def email_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


def update_user_password(user_id: int, password_hash: str) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            if USE_SQLITE
            else "UPDATE users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (password_hash, user_id),
        )


def update_user_profile_image(user_id: int, image_url: str) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET profile_image_url = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            if USE_SQLITE
            else "UPDATE users SET profile_image_url = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (image_url, user_id),
        )


def _hash_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_password_reset_token(user_id: int, raw_token: str, expires_at: datetime) -> None:
    token_hash = _hash_reset_token(raw_token)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE user_id = ? AND used_at IS NULL"
            if USE_SQLITE
            else "UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE user_id = %s AND used_at IS NULL",
            (user_id,),
        )
    execute_insert(
        "INSERT INTO password_resets (user_id, token_hash, expires_at) VALUES (?, ?, ?)"
        if USE_SQLITE
        else "INSERT INTO password_resets (user_id, token_hash, expires_at) VALUES (%s, %s, %s)",
        (user_id, token_hash, expires_at.replace(tzinfo=None)),
    )


def get_valid_password_reset(raw_token: str) -> Optional[Dict[str, Any]]:
    token_hash = _hash_reset_token(raw_token)
    row = execute_one(
        """SELECT * FROM password_resets
           WHERE token_hash = ? AND used_at IS NULL
           ORDER BY id DESC LIMIT 1"""
        if USE_SQLITE
        else """SELECT * FROM password_resets
           WHERE token_hash = %s AND used_at IS NULL
           ORDER BY id DESC LIMIT 1""",
        (token_hash,),
    )
    if not row:
        return None
    expires = row.get("expires_at")
    if not expires:
        return None
    if isinstance(expires, str):
        expires = datetime.fromisoformat(expires.replace(" ", "T"))
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) >= expires:
        return None
    return row


def mark_password_reset_used(reset_id: int) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE id = ?"
            if USE_SQLITE
            else "UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE id = %s",
            (reset_id,),
        )


def session_belongs_to_user(session_id: int, user_id: int) -> bool:
    """True if session exists and belongs to user."""
    row = execute_one(
        "SELECT user_id FROM sessions WHERE id = ?" if USE_SQLITE else "SELECT user_id FROM sessions WHERE id = %s",
        (session_id,),
    )
    if not row:
        return False
    return int(row.get("user_id") or row["user_id"]) == int(user_id)


def get_or_create_session(user_id: int) -> tuple:
    """Get current active session or create new. Returns (session, total_sessions, is_limit_reached)."""
    user = get_user(user_id)
    if not user:
        return None, 0, False

    from app.core.constants import MAX_SESSIONS_PER_USER

    total = user.get("total_sessions", 0) or 0
    is_limit_reached = total >= MAX_SESSIONS_PER_USER

    # Get active session
    sess = execute_one(
        "SELECT * FROM sessions WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1"
        if USE_SQLITE
        else "SELECT * FROM sessions WHERE user_id = %s AND status = 'active' ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    if sess:
        return sess, total, is_limit_reached

    if is_limit_reached:
        return None, total, True

    session_no = total + 1
    sid = execute_insert(
        "INSERT INTO sessions (user_id, session_no) VALUES (?, ?)"
        if USE_SQLITE
        else "INSERT INTO sessions (user_id, session_no) VALUES (%s, %s)",
        (user_id, session_no),
    )
    # Update user total_sessions
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET total_sessions = ? WHERE id = ?"
            if USE_SQLITE
            else "UPDATE users SET total_sessions = %s WHERE id = %s",
            (session_no, user_id),
        )
    sess = execute_one(
        "SELECT * FROM sessions WHERE id = ?" if USE_SQLITE else "SELECT * FROM sessions WHERE id = %s",
        (sid,),
    )
    return sess, session_no, False


def create_chat_log(
    session_id: int,
    user_message: str,
    ai_response: str,
    mh_classification: str = None,
    mh_confidence: float = None,
    emotion_label: str = None,
    risk_level: str = "low",
    is_crisis: int = 0,
) -> int:
    """Create chat log entry."""
    return execute_insert(
        """INSERT INTO chat_logs (session_id, user_message, ai_response, mh_classification,
           mh_confidence, emotion_label, risk_level, is_crisis)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        if USE_SQLITE
        else """INSERT INTO chat_logs (session_id, user_message, ai_response, mh_classification,
           mh_confidence, emotion_label, risk_level, is_crisis)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (session_id, user_message, ai_response, mh_classification, mh_confidence, emotion_label, risk_level, is_crisis),
    )


def add_emotion_history(session_id: int, emotion_label: str, confidence: float = None):
    """Add emotion record."""
    execute_insert(
        "INSERT INTO emotion_history (session_id, emotion_label, confidence) VALUES (?, ?, ?)"
        if USE_SQLITE
        else "INSERT INTO emotion_history (session_id, emotion_label, confidence) VALUES (%s, %s, %s)",
        (session_id, emotion_label, confidence or 0.0),
    )


def get_chat_history(session_id: int) -> List[Dict[str, Any]]:
    """Get chat history for session."""
    rows = execute_many(
        """SELECT id, user_message AS content, 'user' AS role, mh_classification, created_at AS timestamp
           FROM chat_logs WHERE session_id = ?"""
        if USE_SQLITE
        else """SELECT id, user_message AS content, 'user' AS role, mh_classification, created_at AS timestamp
           FROM chat_logs WHERE session_id = %s""",
        (session_id,),
    )
    # We need to interleave user and AI messages - chat_logs has both in one row
    result = []
    rows_full = execute_many(
        "SELECT * FROM chat_logs WHERE session_id = ? ORDER BY created_at"
        if USE_SQLITE
        else "SELECT * FROM chat_logs WHERE session_id = %s ORDER BY created_at",
        (session_id,),
    )
    for r in rows_full:
        result.append({"id": r["id"], "role": "user", "content": r["user_message"], "timestamp": r["created_at"]})
        result.append({
            "id": r["id"],
            "role": "assistant",
            "content": r["ai_response"],
            "mhClassification": r.get("mh_classification"),
            "timestamp": r["created_at"],
        })
    return result


def get_recent_session_turns(session_id: int, limit: int = 4) -> List[Dict[str, Any]]:
    """Latest N chat rows for this session, oldest-first (for LLM continuity)."""
    rows = execute_many(
        "SELECT user_message, ai_response FROM chat_logs WHERE session_id = ? ORDER BY id DESC LIMIT ?"
        if USE_SQLITE
        else "SELECT user_message, ai_response FROM chat_logs WHERE session_id = %s ORDER BY id DESC LIMIT %s",
        (session_id, limit),
    )
    return list(reversed(rows or []))


def get_mood_summary(user_id: int) -> List[Dict[str, Any]]:
    """Get mood summary per session for user."""
    rows = execute_many(
        """SELECT s.session_no, s.created_at, cl.mh_classification
           FROM sessions s
           LEFT JOIN chat_logs cl ON cl.session_id = s.id
           WHERE s.user_id = ? ORDER BY s.created_at"""
        if USE_SQLITE
        else """SELECT s.session_no, s.created_at, cl.mh_classification
           FROM sessions s
           LEFT JOIN chat_logs cl ON cl.session_id = s.id
           WHERE s.user_id = %s ORDER BY s.created_at""",
        (user_id,),
    )
    # Aggregate by session - take dominant classification per session
    from collections import Counter
    by_session = {}
    for r in rows:
        sn = r["session_no"]
        if sn not in by_session:
            by_session[sn] = []
        if r.get("mh_classification"):
            by_session[sn].append(r["mh_classification"])
    summary = []
    for sn, classes in sorted(by_session.items()):
        dominant = Counter(classes).most_common(1)[0][0] if classes else "Normal"
        # Get date from first row of session
        sess = execute_one(
            "SELECT created_at FROM sessions WHERE user_id = ? AND session_no = ?"
            if USE_SQLITE
            else "SELECT created_at FROM sessions WHERE user_id = %s AND session_no = %s",
            (user_id, sn),
        )
        summary.append({
            "sessionNo": sn,
            "dominantEmotion": dominant,
            "date": str(sess["created_at"])[:10] if sess else "",
        })
    return summary


def create_assignment(user_id: int, exercise_type: str, title: str, content: str) -> int:
    """Legacy flat assignment (title|content). Prefer save_exercise_assignment for interactive exercises."""
    return execute_insert(
        "INSERT INTO assignments (user_id, exercise_type, content) VALUES (?, ?, ?)"
        if USE_SQLITE
        else "INSERT INTO assignments (user_id, exercise_type, content) VALUES (%s, %s, %s)",
        (user_id, exercise_type, f"{title}|{content}"),
    )


def _parse_assignment_json(content: Any) -> Optional[Dict[str, Any]]:
    if not content:
        return None
    s = str(content).strip()
    if not s.startswith("{"):
        return None
    try:
        data = json.loads(s)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def save_exercise_assignment(user_id: int, exercise: Dict[str, Any]) -> int:
    """Store full interactive exercise JSON on assignments row."""
    blob = json.dumps(exercise, ensure_ascii=False)
    et = (exercise.get("type") or "grounding")[:50]
    return execute_insert(
        "INSERT INTO assignments (user_id, exercise_type, content) VALUES (?, ?, ?)"
        if USE_SQLITE
        else "INSERT INTO assignments (user_id, exercise_type, content) VALUES (%s, %s, %s)",
        (user_id, et, blob),
    )


def get_recent_assignment_types(user_id: int, limit: int = 8) -> List[str]:
    """Exercise types from latest assignments (for variety)."""
    rows = execute_many(
        "SELECT exercise_type, content FROM assignments WHERE user_id = ? ORDER BY assigned_at DESC LIMIT ?"
        if USE_SQLITE
        else "SELECT exercise_type, content FROM assignments WHERE user_id = %s ORDER BY assigned_at DESC LIMIT %s",
        (user_id, limit),
    )
    out: List[str] = []
    for r in rows or []:
        blob = _parse_assignment_json(r.get("content"))
        if blob and blob.get("type"):
            out.append(str(blob["type"]))
        else:
            out.append(str(r.get("exercise_type") or ""))
    return out


def get_recent_assignment_titles(user_id: int, limit: int = 6) -> List[str]:
    titles: List[str] = []
    rows = execute_many(
        "SELECT content FROM assignments WHERE user_id = ? ORDER BY assigned_at DESC LIMIT ?"
        if USE_SQLITE
        else "SELECT content FROM assignments WHERE user_id = %s ORDER BY assigned_at DESC LIMIT %s",
        (user_id, limit),
    )
    for r in rows or []:
        blob = _parse_assignment_json(r.get("content"))
        if blob and blob.get("title"):
            titles.append(str(blob["title"]))
        else:
            raw = r.get("content") or ""
            titles.append(raw.split("|", 1)[0] if "|" in raw else raw[:80])
    return titles


def get_assignments(user_id: int) -> List[Dict[str, Any]]:
    """Recent assignments; JSON rows include full payload for the exercise runner."""
    rows = execute_many(
        "SELECT * FROM assignments WHERE user_id = ? ORDER BY assigned_at DESC LIMIT 12"
        if USE_SQLITE
        else "SELECT * FROM assignments WHERE user_id = %s ORDER BY assigned_at DESC LIMIT 12",
        (user_id,),
    )
    result: List[Dict[str, Any]] = []
    for r in rows or []:
        blob = _parse_assignment_json(r.get("content"))
        if blob:
            result.append({
                "assignmentId": r["id"],
                "type": blob.get("type", r.get("exercise_type")),
                "title": blob.get("title") or "Exercise",
                "content": blob.get("description") or "",
                "assignedAt": r["assigned_at"],
                "tone": blob.get("tone"),
                "durationSeconds": blob.get("durationSeconds"),
                "source": blob.get("source", "library"),
                "payload": blob,
            })
            continue
        parts = (r.get("content") or "").split("|", 1)
        title, content = parts[0] if parts else "", parts[1] if len(parts) > 1 else ""
        result.append({
            "assignmentId": r["id"],
            "type": r["exercise_type"],
            "title": title or "Exercise",
            "content": content,
            "assignedAt": r["assigned_at"],
            "payload": None,
        })
    return result


def verify_assignment_owner(assignment_id: int, user_id: int) -> bool:
    row = execute_one(
        "SELECT id FROM assignments WHERE id = ? AND user_id = ?"
        if USE_SQLITE
        else "SELECT id FROM assignments WHERE id = %s AND user_id = %s",
        (assignment_id, user_id),
    )
    return bool(row)


def record_exercise_feedback(
    user_id: int,
    assignment_id: Optional[int],
    session_id: Optional[int],
    helped: Optional[bool],
) -> None:
    """Persist post-exercise feedback; nudge session stress_level when we have a session."""
    h: Optional[int]
    if helped is None:
        h = None
    else:
        h = 1 if helped else 0
    execute_insert(
        "INSERT INTO exercise_feedback (user_id, session_id, assignment_id, helped) VALUES (?, ?, ?, ?)"
        if USE_SQLITE
        else "INSERT INTO exercise_feedback (user_id, session_id, assignment_id, helped) VALUES (%s, %s, %s, %s)",
        (user_id, session_id, assignment_id, h),
    )
    if session_id and helped is not None:
        row = execute_one(
            "SELECT stress_level FROM sessions WHERE id = ?"
            if USE_SQLITE
            else "SELECT stress_level FROM sessions WHERE id = %s",
            (session_id,),
        )
        if row:
            sl = int(row.get("stress_level") or 0)
            sl = max(0, min(10, sl + (-1 if helped else 1)))
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE sessions SET stress_level = ? WHERE id = ?"
                    if USE_SQLITE
                    else "UPDATE sessions SET stress_level = %s WHERE id = %s",
                    (sl, session_id),
                )


def get_all_sessions(limit: int = 100) -> List[Dict[str, Any]]:
    """Get all sessions for admin."""
    rows = execute_many(
        """SELECT s.*, u.name AS user_name FROM sessions s
           JOIN users u ON u.id = s.user_id ORDER BY s.created_at DESC LIMIT ?"""
        if USE_SQLITE
        else """SELECT s.*, u.name AS user_name FROM sessions s
           JOIN users u ON u.id = s.user_id ORDER BY s.created_at DESC LIMIT %s""",
        (limit,),
    )
    return rows


def get_crisis_alerts() -> List[Dict[str, Any]]:
    """Get chat logs with crisis flag for admin."""
    rows = execute_many(
        """SELECT cl.session_id, cl.user_message AS last_message, cl.risk_level, cl.created_at,
           s.user_id, u.name AS user_name
           FROM chat_logs cl
           JOIN sessions s ON s.id = cl.session_id
           JOIN users u ON u.id = s.user_id
           WHERE cl.is_crisis = 1 ORDER BY cl.created_at DESC LIMIT 50"""
        if USE_SQLITE
        else """SELECT cl.session_id, cl.user_message AS last_message, cl.risk_level, cl.created_at,
           s.user_id, u.name AS user_name
           FROM chat_logs cl
           JOIN sessions s ON s.id = cl.session_id
           JOIN users u ON u.id = s.user_id
           WHERE cl.is_crisis = 1 ORDER BY cl.created_at DESC LIMIT 50""",
        (),
    )
    return [{
        "sessionId": r["session_id"],
        "userId": r["user_id"],
        "userName": r["user_name"],
        "timestamp": r["created_at"],
        "lastMessage": (r["last_message"] or "")[:200],
        "riskLevel": r["risk_level"],
    } for r in rows]


def get_admin_stats() -> Dict[str, Any]:
    """Admin dashboard statistics."""
    total = execute_one(
        "SELECT COUNT(*) AS c FROM sessions",
        fetch=True,
    )
    crisis = execute_one(
        "SELECT COUNT(*) AS c FROM chat_logs WHERE is_crisis = 1",
        fetch=True,
    )
    return {
        "totalSessions": total.get("c", 0) if total else 0,
        "crisisCount": crisis.get("c", 0) if crisis else 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — Patient Profile
# ─────────────────────────────────────────────────────────────────────────────

def upsert_patient_profile(user_id: int, data: Dict[str, Any]) -> None:
    """Insert or update the patient intake profile."""
    p = ("?" if USE_SQLITE else "%s")
    existing = execute_one(
        f"SELECT id FROM patient_profiles WHERE user_id = {p}",
        (user_id,),
    )
    if existing:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""UPDATE patient_profiles
                    SET age={p}, gender={p}, sleep_pattern={p}, stress_triggers={p},
                        past_therapy={p}, medications={p}, updated_at=CURRENT_TIMESTAMP
                    WHERE user_id={p}""",
                (
                    data.get("age"),
                    data.get("gender"),
                    data.get("sleep_pattern"),
                    data.get("stress_triggers"),
                    1 if data.get("past_therapy") else 0,
                    data.get("medications"),
                    user_id,
                ),
            )
    else:
        execute_insert(
            f"""INSERT INTO patient_profiles
                (user_id, age, gender, sleep_pattern, stress_triggers, past_therapy, medications)
                VALUES ({p},{p},{p},{p},{p},{p},{p})""",
            (
                user_id,
                data.get("age"),
                data.get("gender"),
                data.get("sleep_pattern"),
                data.get("stress_triggers"),
                1 if data.get("past_therapy") else 0,
                data.get("medications"),
            ),
        )


def get_patient_profile(user_id: int) -> Optional[Dict[str, Any]]:
    p = "?" if USE_SQLITE else "%s"
    return execute_one(
        f"SELECT * FROM patient_profiles WHERE user_id = {p}",
        (user_id,),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — Assessments
# ─────────────────────────────────────────────────────────────────────────────

def create_assessment(user_id: int, assessment_type: str, session_number: int) -> int:
    p = "?" if USE_SQLITE else "%s"
    return execute_insert(
        f"""INSERT INTO assessments (user_id, assessment_type, session_number)
            VALUES ({p},{p},{p})""",
        (user_id, assessment_type, session_number),
    )


def get_assessment(assessment_id: int) -> Optional[Dict[str, Any]]:
    p = "?" if USE_SQLITE else "%s"
    return execute_one(
        f"SELECT * FROM assessments WHERE id = {p}", (assessment_id,)
    )


def assessment_belongs_to_user(assessment_id: int, user_id: int) -> bool:
    row = get_assessment(assessment_id)
    if not row:
        return False
    return int(row.get("user_id") or row["user_id"]) == int(user_id)


def get_latest_assessment_for_user(user_id: int, session_number: int) -> Optional[Dict[str, Any]]:
    p = "?" if USE_SQLITE else "%s"
    return execute_one(
        f"""SELECT * FROM assessments WHERE user_id = {p} AND session_number = {p}
            ORDER BY id DESC LIMIT 1""",
        (user_id, session_number),
    )


def get_all_assessments_for_user(user_id: int) -> List[Dict[str, Any]]:
    p = "?" if USE_SQLITE else "%s"
    return execute_many(
        f"SELECT * FROM assessments WHERE user_id = {p} ORDER BY session_number, id",
        (user_id,),
    )


def complete_assessment(assessment_id: int) -> None:
    p = "?" if USE_SQLITE else "%s"
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE assessments SET status='completed', completed_at=CURRENT_TIMESTAMP WHERE id={p}",
            (assessment_id,),
        )


def save_assessment_answer(
    assessment_id: int,
    question_key: str,
    question_text: str,
    answer_value: Optional[int],
    answer_text: Optional[str],
) -> int:
    p = "?" if USE_SQLITE else "%s"
    return execute_insert(
        f"""INSERT INTO assessment_answers (assessment_id, question_key, question_text, answer_value, answer_text)
            VALUES ({p},{p},{p},{p},{p})""",
        (assessment_id, question_key, question_text, answer_value, answer_text),
    )


def get_assessment_answers(assessment_id: int) -> List[Dict[str, Any]]:
    p = "?" if USE_SQLITE else "%s"
    return execute_many(
        f"SELECT * FROM assessment_answers WHERE assessment_id = {p} ORDER BY id",
        (assessment_id,),
    )


def get_all_answers_for_user(user_id: int) -> List[Dict[str, Any]]:
    """All answers across every assessment for a user, for score calculation."""
    p = "?" if USE_SQLITE else "%s"
    return execute_many(
        f"""SELECT aa.* FROM assessment_answers aa
            JOIN assessments a ON a.id = aa.assessment_id
            WHERE a.user_id = {p} ORDER BY aa.id""",
        (user_id,),
    )


def upsert_assessment_result(user_id: int, result: Dict[str, Any]) -> None:
    p = "?" if USE_SQLITE else "%s"
    existing = execute_one(
        f"SELECT id FROM assessment_results WHERE user_id = {p}", (user_id,)
    )
    if existing:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""UPDATE assessment_results
                    SET depression_score={p}, anxiety_score={p}, risk_level={p},
                        depression_severity={p}, anxiety_severity={p},
                        summary={p}, recommendations={p}, updated_at=CURRENT_TIMESTAMP
                    WHERE user_id={p}""",
                (
                    result.get("depression_score", 0),
                    result.get("anxiety_score", 0),
                    result.get("risk_level", "low"),
                    result.get("depression_severity", ""),
                    result.get("anxiety_severity", ""),
                    result.get("summary", ""),
                    result.get("recommendations", ""),
                    user_id,
                ),
            )
    else:
        execute_insert(
            f"""INSERT INTO assessment_results
                (user_id, depression_score, anxiety_score, risk_level,
                 depression_severity, anxiety_severity, summary, recommendations)
                VALUES ({p},{p},{p},{p},{p},{p},{p},{p})""",
            (
                user_id,
                result.get("depression_score", 0),
                result.get("anxiety_score", 0),
                result.get("risk_level", "low"),
                result.get("depression_severity", ""),
                result.get("anxiety_severity", ""),
                result.get("summary", ""),
                result.get("recommendations", ""),
            ),
        )


def get_assessment_result(user_id: int) -> Optional[Dict[str, Any]]:
    p = "?" if USE_SQLITE else "%s"
    return execute_one(
        f"SELECT * FROM assessment_results WHERE user_id = {p}", (user_id,)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — Daily Mood Log
# ─────────────────────────────────────────────────────────────────────────────

def add_mood_log(user_id: int, mood_score: int, note: Optional[str] = None) -> int:
    p = "?" if USE_SQLITE else "%s"
    return execute_insert(
        f"INSERT INTO mood_logs (user_id, mood_score, note) VALUES ({p},{p},{p})",
        (user_id, mood_score, note),
    )


def get_mood_history(user_id: int, limit: int = 30) -> List[Dict[str, Any]]:
    p = "?" if USE_SQLITE else "%s"
    return execute_many(
        f"SELECT * FROM mood_logs WHERE user_id = {p} ORDER BY logged_at DESC LIMIT {p}",
        (user_id, limit),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — Behavior Log
# ─────────────────────────────────────────────────────────────────────────────

def add_behavior_log(user_id: int, data: Dict[str, Any]) -> int:
    p = "?" if USE_SQLITE else "%s"
    return execute_insert(
        f"""INSERT INTO behavior_logs (user_id, sleep_hours, physical_activity, social_interaction, notes)
            VALUES ({p},{p},{p},{p},{p})""",
        (
            user_id,
            data.get("sleep_hours"),
            data.get("physical_activity"),
            data.get("social_interaction"),
            data.get("notes"),
        ),
    )


def get_behavior_history(user_id: int, limit: int = 30) -> List[Dict[str, Any]]:
    p = "?" if USE_SQLITE else "%s"
    return execute_many(
        f"SELECT * FROM behavior_logs WHERE user_id = {p} ORDER BY logged_at DESC LIMIT {p}",
        (user_id, limit),
    )
