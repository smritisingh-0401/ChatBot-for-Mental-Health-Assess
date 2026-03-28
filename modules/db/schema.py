"""
Run once on startup to ensure all tables exist.
Idempotent — safe to call every deploy.
"""
from modules.db.connection import get_connection

MIGRATIONS = [
    """
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
    """
    CREATE TABLE IF NOT EXISTS phq9_results (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     BIGINT NOT NULL,
        score       INTEGER NOT NULL,
        level       TEXT NOT NULL,
        answers     TEXT NOT NULL,
        taken_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS gad7_results (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     BIGINT NOT NULL,
        score       INTEGER NOT NULL,
        level       TEXT NOT NULL,
        answers     TEXT NOT NULL,
        taken_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS mood_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     BIGINT NOT NULL,
        mood_score  INTEGER NOT NULL,
        note        TEXT,
        sentiment_compound REAL,
        logged_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS therapy_sessions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     BIGINT NOT NULL,
        module      TEXT NOT NULL,
        step        TEXT NOT NULL,
        completed   INTEGER DEFAULT 0,
        started_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS crisis_events (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id         BIGINT NOT NULL,
        trigger_text    TEXT,
        severity        TEXT NOT NULL,
        resources_sent  INTEGER DEFAULT 0,
        detected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS biomarker_logs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id         BIGINT NOT NULL,
        session_date    TEXT DEFAULT (date('now')),
        avg_msg_length  REAL,
        msg_count       INTEGER,
        avg_sentiment   REAL,
        response_delay_avg REAL,
        logged_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
]

def run_migrations():
    with get_connection() as conn:
        cur = conn.cursor()
        for sql in MIGRATIONS:
            cur.execute(sql)
    print("[DB] Migrations complete.")