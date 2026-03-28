"""
Database connection manager.
Uses PostgreSQL (Neon) when DATABASE_URL is set,
falls back to SQLite locally so existing dev workflow still works.
"""
import os
import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL:
    import psycopg2
    import psycopg2.pool

    _pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=1, maxconn=5, dsn=DATABASE_URL,
    )

    @contextmanager
    def get_connection():
        conn = _pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            _pool.putconn(conn)

    def placeholder():
        return "%s"

else:
    logger.warning("DATABASE_URL not set — using local SQLite fallback.")
    _sqlite_path = os.getenv("SQLITE_DB_PATH", "bot_data.db")

    @contextmanager
    def get_connection():
        conn = sqlite3.connect(_sqlite_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def placeholder():
        return "?"