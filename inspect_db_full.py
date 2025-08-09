import sqlite3
from datetime import datetime, timedelta

# Adjust this if your database file has a different name
DB_PATH = "qmmx.db"

def get_tables_and_counts(db_path):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        # Get all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]

        # Get row counts
        counts = []
        for tbl in tables:
            cur.execute(f"SELECT COUNT(*) FROM '{tbl}';")
            count = cur.fetchone()[0]
            counts.append((tbl, count))
    return counts

if __name__ == "__main__":
    print(f"Inspecting database: {DB_PATH}\n")
    table_counts = get_tables_and_counts(DB_PATH)
    for tbl, cnt in table_counts:
        print(f"  {tbl:<20} {cnt:>6} rows")
