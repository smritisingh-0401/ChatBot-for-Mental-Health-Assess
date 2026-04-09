from modules.db.connection import get_connection

with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [row[0] for row in cur.fetchall()]
    print("Tables in Neon:", tables)
    print("Count:", len(tables))