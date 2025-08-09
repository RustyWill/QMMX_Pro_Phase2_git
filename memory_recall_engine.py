import sqlite3
from datetime import datetime, timedelta
import pandas as pd

DB_PATH = "qmmx_memory.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

# 1. Recall pattern memory by ID
def recall_pattern_memory(pattern_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patterns_memory WHERE id = ?", (pattern_id,))
        return cursor.fetchone()

# 2. Recall trade memory by ticker or pattern
def recall_trade_memory(ticker: str = None, pattern_id: str = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM trades_history WHERE 1=1"
        params = []
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        if pattern_id:
            query += " AND pattern_id = ?"
            params.append(pattern_id)
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

# ✅ 3. Recall recent pattern feedback (used for scoring)
def recall_recent_feedback(limit=50):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pattern_id, confidence, outcome, timestamp
            FROM pattern_feedback
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["pattern_id", "confidence", "outcome", "timestamp"])
        return df
