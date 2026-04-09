import sqlite3
import os
from modules.db.connection import get_connection, placeholder

SQLITE_PATH = os.getenv("SQLITE_DB_PATH", "bot_data.db")

def safe_get(row, key, default=None):
    """sqlite3.Row doesn't have .get() — this adds that behaviour."""
    try:
        return row[key]
    except (IndexError, KeyError):
        return default

def migrate():
    if not os.path.exists(SQLITE_PATH):
        print(f"No SQLite DB found at {SQLITE_PATH} — skipping migration.")
        return

    src = sqlite3.connect(SQLITE_PATH)
    src.row_factory = sqlite3.Row
    ph = placeholder()

    users_migrated = 0
    phq9_migrated = 0

    with get_connection() as dst:
        cur = dst.cursor()

        for row in src.execute("SELECT * FROM users"):
            cur.execute(
                f"""INSERT INTO users (user_id, username, created_at)
                    VALUES ({ph}, {ph}, {ph})
                    ON CONFLICT (user_id) DO NOTHING""",
                (row["user_id"], safe_get(row, "username"), safe_get(row, "created_at")),
            )
            users_migrated += 1

        for row in src.execute("SELECT * FROM phq9_results"):
            cur.execute(
                f"""INSERT INTO phq9_results (user_id, score, level, answers, taken_at)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph})""",
                (row["user_id"], row["score"], row["level"],
                 safe_get(row, "answers", "[]"), safe_get(row, "taken_at")),
            )
            phq9_migrated += 1

    src.close()
    print(f"[Migration] Done. Users: {users_migrated}, PHQ-9 results: {phq9_migrated}")

if __name__ == "__main__":
    migrate()