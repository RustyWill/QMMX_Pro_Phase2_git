# alerts.py

import sqlite3
import datetime

def get_current_alerts(limit=5):
    try:
        conn = sqlite3.connect("qmmx.db")
        cur = conn.cursor()
        # Create table if it doesn’t exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              message TEXT,
              timestamp TEXT
            )
        """)
        # Now read the latest alerts
        cur.execute(
            "SELECT message, timestamp FROM alerts ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        conn.close()

        # Format as “timestamp – message”
        return [f"{row[1]} – {row[0]}" for row in rows]

    except Exception as e:
        print("❌ Failed to load alerts:", e)
        return ["⚠ Error loading alerts"]
