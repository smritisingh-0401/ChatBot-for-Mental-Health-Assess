"""
Run ONCE to copy existing SQLite data to Neon PostgreSQL.
Usage (PowerShell):
    $env:DATABASE_URL = "postgresql://..."
    python -m modules.db.migrate_sqlite
"""
import sqlite3
import os
from modules.db.connection import get_connection, placeholder

SQLITE_PATH = os.getenv("SQLITE_DB_PATH", "bot_data.db")

def migrate():
    if not os.path.exists(SQLITE_PATH):
        print(f"No SQLite DB found at {SQLITE_PATH} — skipping migration.")
        return

    src = sqlite3.connect(SQLITE_PATH)
    src.row_factory = sqlite3.Row
    ph = placeholder()

    with get_connection() as dst:
        cur = dst.cursor()

        for row in src.execute("SELECT * FROM users"):
            cur.execute(
                f"""INSERT INTO users (user_id, username, created_at)
                    VALUES ({ph}, {ph}, {ph})
                    ON CONFLICT (user_id) DO NOTHING""",
                (row["user_id"], row.get("username"), row.get("created_at")),
            )

        for row in src.execute("SELECT * FROM phq9_results"):
            cur.execute(
                f"""INSERT INTO phq9_results (user_id, score, level, answers, taken_at)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph})""",
                (row["user_id"], row["score"], row["level"],
                 row.get("answers", "[]"), row.get("taken_at")),
            )

    src.close()
    print("[Migration] Done.")

if __name__ == "__main__":
    migrate()