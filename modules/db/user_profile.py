"""User profile CRUD helpers."""
from modules.db.connection import get_connection, placeholder

def get_or_create_user(user_id: int, username: str = None, language: str = "en") -> dict:
    ph = placeholder()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE user_id = {ph}", (user_id,))
        row = cur.fetchone()
        if row:
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))
        cur.execute(
            f"INSERT INTO users (user_id, username, language) VALUES ({ph}, {ph}, {ph})",
            (user_id, username, language),
        )
        cur.execute(f"SELECT * FROM users WHERE user_id = {ph}", (user_id,))
        row = cur.fetchone()
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))

def update_user_region(user_id: int, region: str):
    ph = placeholder()
    with get_connection() as conn:
        conn.cursor().execute(
            f"UPDATE users SET region = {ph} WHERE user_id = {ph}",
            (region.upper(), user_id),
        )

def delete_user_data(user_id: int):
    """GDPR-style right to erasure."""
    ph = placeholder()
    tables = ["users", "phq9_results", "gad7_results", "mood_logs",
              "therapy_sessions", "crisis_events", "biomarker_logs"]
    with get_connection() as conn:
        cur = conn.cursor()
        for table in tables:
            cur.execute(f"DELETE FROM {table} WHERE user_id = {ph}", (user_id,))