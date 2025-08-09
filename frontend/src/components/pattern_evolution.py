# pattern_evolution.py

import sqlite3

def update_pattern_weights():
    try:
        conn = sqlite3.connect("qmmx.db")
        cur = conn.cursor()

        cur.execute("""
            UPDATE patterns
            SET weight = weight + 0.05
            WHERE id IN (
                SELECT pattern_id FROM trades
                WHERE outcome = 'win' AND closed = 1
            )
        """)
        conn.commit()
        conn.close()
        print("🔁 Pattern weights updated")
    except Exception as e:
        print(f"⚠️ Pattern evolution failed: {e}")
