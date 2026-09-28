import sqlite3, json, uuid
from datetime import datetime
from config import DB_PATH


def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.executescript("""
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS users (
            user_id        TEXT PRIMARY KEY,
            username       TEXT,
            full_name      TEXT,
            joined_at      TEXT DEFAULT (datetime('now')),
            cv_count       INTEGER DEFAULT 0,
            last_active    TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS cv_sessions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        TEXT NOT NULL,
            session_id     TEXT UNIQUE NOT NULL,
            template       TEXT DEFAULT 'modern',
            status         TEXT DEFAULT 'in_progress',
            pdf_path       TEXT,
            created_at     TEXT DEFAULT (datetime('now')),
            completed_at   TEXT
        );

        CREATE TABLE IF NOT EXISTS cv_data (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id     TEXT NOT NULL,
            field          TEXT NOT NULL,
            value          TEXT,
            UNIQUE(session_id, field)
        );
        """)


def upsert_user(user_id, username="", full_name=""):
    with conn() as c:
        c.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES (?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
              username=excluded.username,
              full_name=excluded.full_name,
              last_active=datetime('now')
        """, (str(user_id), username or "", full_name or ""))


def get_user(user_id):
    with conn() as c:
        r = c.execute("SELECT * FROM users WHERE user_id=?",
                      (str(user_id),)).fetchone()
        return dict(r) if r else None


def increment_cv_count(user_id):
    with conn() as c:
        c.execute("UPDATE users SET cv_count=cv_count+1 WHERE user_id=?",
                  (str(user_id),))


def new_session(user_id, template="modern") -> str:
    sid = uuid.uuid4().hex[:12].upper()
    with conn() as c:
        c.execute("INSERT INTO cv_sessions (user_id, session_id, template) VALUES (?,?,?)",
                  (str(user_id), sid, template))
    return sid


def get_active_session(user_id):
    with conn() as c:
        r = c.execute(
            "SELECT * FROM cv_sessions WHERE user_id=? AND status='in_progress' "
            "ORDER BY created_at DESC LIMIT 1",
            (str(user_id),)).fetchone()
        return dict(r) if r else None


def save_field(session_id, field, value):
    with conn() as c:
        c.execute("""
            INSERT INTO cv_data (session_id, field, value) VALUES (?,?,?)
            ON CONFLICT(session_id, field) DO UPDATE SET value=excluded.value
        """, (session_id, field, str(value)))


def get_all_fields(session_id) -> dict:
    with conn() as c:
        rows = c.execute("SELECT field, value FROM cv_data WHERE session_id=?",
                         (session_id,)).fetchall()
        return {r["field"]: r["value"] for r in rows}


def complete_session(session_id, pdf_path):
    with conn() as c:
        c.execute("""
            UPDATE cv_sessions SET status='completed', pdf_path=?,
            completed_at=datetime('now') WHERE session_id=?
        """, (pdf_path, session_id))


def cancel_session(session_id):
    with conn() as c:
        c.execute("UPDATE cv_sessions SET status='cancelled' WHERE session_id=?",
                  (session_id,))


def get_user_cvs(user_id, limit=5) -> list:
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM cv_sessions WHERE user_id=? AND status='completed' "
            "ORDER BY completed_at DESC LIMIT ?",
            (str(user_id), limit))]


def get_stats() -> dict:
    with conn() as c:
        return {
            "total_users": c.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "total_cvs":   c.execute("SELECT COUNT(*) FROM cv_sessions WHERE status='completed'").fetchone()[0],
            "today_cvs":   c.execute("SELECT COUNT(*) FROM cv_sessions WHERE status='completed' AND date(completed_at)=date('now')").fetchone()[0],
        }
