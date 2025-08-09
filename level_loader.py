# level_loader.py

import sqlite3

DB_PATH = "qmmx.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def load_levels():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT color, level_type, price
            FROM price_levels
        """)
        rows = cursor.fetchall()

    levels = []
    for row in rows:
        level = {
            "color": row[0],
            "type": row[1],
            "price": row[2]
        }
        levels.append(level)

    return levels

get_today_levels = load_levels
