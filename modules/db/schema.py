"""
Run once on startup to ensure all tables exist.
Idempotent — safe to call every deploy.
Handles both SQLite (local) and PostgreSQL (Neon/production).
"""
import os
from modules.db.connection import get_connection

# Use SERIAL for PostgreSQL, AUTOINCREMENT for SQLite
_using_postgres = bool(os.getenv("DATABASE_URL", ""))

def _pk():
    """Primary key syntax for current database."""
    if _using_postgres:
        return "SERIAL PRIMARY KEY"
    return "INTEGER PRIMARY KEY AUTOINCREMENT"

def _date_default():
    """Date default syntax for current database."""
    if _using_postgres:
        return "CURRENT_DATE"
    return "(date('now'))"

def _get_migrations():
    pk = _pk()
    date_default = _date_default()
    return [
        f"""
        CREATE TABLE IF NOT EXISTS users (
            user_id     BIGINT PRIMARY KEY,
            username    TEXT,
            language    TEXT DEFAULT 'en',
            region      TEXT DEFAULT 'IN',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            disclaimer_accepted_at TIMESTAMP,
            disclaimer_version INTEGER DEFAULT 0
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS phq9_results (
            id          {pk},
            user_id     BIGINT NOT NULL,
            score       INTEGER NOT NULL,
            level       TEXT NOT NULL,
            answers     TEXT NOT NULL,
            taken_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS gad7_results (
            id          {pk},
            user_id     BIGINT NOT NULL,
            score       INTEGER NOT NULL,
            level       TEXT NOT NULL,
            answers     TEXT NOT NULL,
            taken_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id          {pk},
            user_id     BIGINT NOT NULL,
            mood_score  INTEGER NOT NULL,
            note        TEXT,
            sentiment_compound REAL,
            logged_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS therapy_sessions (
            id          {pk},
            user_id     BIGINT NOT NULL,
            module      TEXT NOT NULL,
            step        TEXT NOT NULL,
            completed   INTEGER DEFAULT 0,
            started_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS crisis_events (
            id              {pk},
            user_id         BIGINT NOT NULL,
            trigger_text    TEXT,
            severity        TEXT NOT NULL,
            resources_sent  INTEGER DEFAULT 0,
            detected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS biomarker_logs (
            id              {pk},
            user_id         BIGINT NOT NULL,
            session_date    TEXT DEFAULT {date_default},
            avg_msg_length  REAL,
            msg_count       INTEGER,
            avg_sentiment   REAL,
            response_delay_avg REAL,
            logged_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ]

def run_migrations():
    migrations = _get_migrations()
    with get_connection() as conn:
        cur = conn.cursor()
        for sql in migrations:
            cur.execute(sql)
    print("[DB] Migrations complete.")