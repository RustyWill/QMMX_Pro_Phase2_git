# pattern_evolution.py

import sqlite3
from datetime import datetime

class PatternEvolutionTracker:
    def __init__(self, db_path="qmmx.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_key TEXT,
                direction TEXT,
                confidence_weight REAL,
                wins INTEGER,
                losses INTEGER,
                last_updated TEXT
            )
        """)
        self.conn.commit()

    def _pattern_key(self, pattern_signature):
        return f"{pattern_signature.get('level_type')}|{pattern_signature.get('reaction_type')}|{pattern_signature.get('approach_direction')}|{pattern_signature.get('macro_position')}"

    def record_result(self, pattern_signature, direction, was_successful):
        pattern_key = self._pattern_key(pattern_signature)
        cursor = self.conn.cursor()

        # Fetch existing row
        cursor.execute("""
            SELECT wins, losses FROM pattern_evolution
            WHERE pattern_key = ? AND direction = ?
        """, (pattern_key, direction))
        row = cursor.fetchone()

        if row:
            wins, losses = row
            wins += 1 if was_successful else 0
            losses += 0 if was_successful else 1
            total = wins + losses
            confidence = wins / total if total else 0.5

            cursor.execute("""
                UPDATE pattern_evolution
                SET wins = ?, losses = ?, confidence_weight = ?, last_updated = ?
                WHERE pattern_key = ? AND direction = ?
            """, (wins, losses, confidence, datetime.utcnow().isoformat(), pattern_key, direction))

        else:
            wins = 1 if was_successful else 0
            losses = 0 if was_successful else 1
            confidence = wins / (wins + losses) if (wins + losses) else 0.5

            cursor.execute("""
                INSERT INTO pattern_evolution (pattern_key, direction, confidence_weight, wins, losses, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pattern_key, direction, confidence, wins, losses, datetime.utcnow().isoformat()))

        self.conn.commit()

    def get_best_direction_for_pattern(self, pattern_signature):
        pattern_key = self._pattern_key(pattern_signature)
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT direction, wins, losses FROM pattern_evolution
            WHERE pattern_key = ?
        """, (pattern_key,))
        rows = cursor.fetchall()

        if not rows:
            return None

        best_direction = None
        best_win_rate = 0
        for direction, wins, losses in rows:
            total = wins + losses
            if total == 0:
                continue
            win_rate = wins / total
            if abs(win_rate - best_win_rate) > 0.1 and win_rate > best_win_rate:
                best_direction = direction
                best_win_rate = win_rate

        return best_direction if best_win_rate >= 0.55 else None
