import sqlite3
import datetime

def get_current_pattern():
    try:
        conn = sqlite3.connect("qmmx.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM patterns
            WHERE reviewed = 0
            ORDER BY timestamp ASC
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            return None

        columns = [desc[0] for desc in cur.description]
        pattern = dict(zip(columns, row))
        conn.close()
        return pattern
    except Exception as e:
        print("❌ Error fetching current pattern:", e)
        return None

def mark_pattern_decision(pattern_id, decision):
    try:
        conn = sqlite3.connect("qmmx.db")
        cur = conn.cursor()
        cur.execute("""
            UPDATE patterns
            SET decision = ?, reviewed = 1, decision_time = ?
            WHERE id = ?
        """, (decision, datetime.datetime.utcnow().isoformat(), pattern_id))
        conn.commit()
        conn.close()
        print(f"✅ Pattern {pattern_id} marked as {decision}")
    except Exception as e:
        print("❌ Failed to mark pattern decision:", e)

def get_pattern_id(pattern_name):
    try:
        conn = sqlite3.connect("qmmx.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM patterns
            WHERE name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (pattern_name,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print("❌ Failed to fetch pattern ID:", e)
        return None

