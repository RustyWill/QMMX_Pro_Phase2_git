from __future__ import annotations
import os, sqlite3
from datetime import datetime

try:
    from diagnostic_monitor import diagnostic_monitor as _diag  # type: ignore
    def _ping(name): 
        try: _diag.ping(name)
        except Exception: pass
    def _err(name,msg):
        try: _diag.report_error(name,msg)
        except Exception: pass
except Exception:
    def _ping(name): pass
    def _err(name,msg): pass

DB_PATH = os.environ.get("QMMX_DB_PATH", "qmmx.db")
MIN_PATTERNS_FOR_UPGRADE = 25
W_PATTERNS, W_CONF, W_REVIEW = 30, 40, 30

def _ensure(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS upgrade_score (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        pattern_count INTEGER,
        avg_confidence REAL,
        reviewed_patterns INTEGER,
        review_loop_score REAL,
        score INTEGER,
        notes TEXT)""")

def _get_int(cur,sql,default=0):
    try:
        cur.execute(sql); r=cur.fetchone(); return int(r[0] or 0)
    except Exception: return default

def _get_float(cur,sql,default=0.0):
    try:
        cur.execute(sql); r=cur.fetchone(); v=r[0]; return float(v) if v is not None else default
    except Exception: return default

def _comment(score, n, avg, review):
    if score>=85: return f"Readiness {score}. Memory n={n}, conf {avg:.2f}, review {review:.0%}. Proceed."
    if 70<=score<85: return f"Readiness {score}. Solid; consider quick calibration. Conf {avg:.2f}; review {review:.0%}."
    if n<MIN_PATTERNS_FOR_UPGRADE: 
        return f"Readiness {score}. Need {max(0,MIN_PATTERNS_FOR_UPGRADE-n)} more patterns; review {review:.0%}."
    return f"Readiness {score}. Conf {avg:.2f}. Tighten exits & expand review coverage."

def track_module_impact(db_path: str|None=None):
    db_path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(db_path); cur = conn.cursor(); _ensure(cur)
        n = _get_int(cur, "SELECT COUNT(*) FROM pattern_evolution", 0)
        avg = _get_float(cur, "SELECT AVG(confidence_weight) FROM pattern_evolution", 0.0)
        rev = _get_int(cur, "SELECT COUNT(*) FROM patterns WHERE reviewed=1", 0)
        review = min(rev/max(n,1), 1.0)
        score = int(min(max((n/max(MIN_PATTERNS_FOR_UPGRADE,1))*W_PATTERNS + avg*W_CONF + review*W_REVIEW, 0), 100))
        notes = _comment(score, n, avg, review)
        cur.execute("""INSERT INTO upgrade_score(timestamp,pattern_count,avg_confidence,reviewed_patterns,review_loop_score,score,notes)
                      VALUES(?,?,?,?,?,?,?)""", (datetime.utcnow().isoformat(), n, round(avg,3), rev, round(review,3), score, notes))
        conn.commit(); _ping("upgrade_monitor"); conn.close()
        return {"ok":True, "score":score, "pattern_count":n, "avg_confidence":round(avg,3), "review_loop_score":round(review,3), "notes":notes}
    except Exception as e:
        _err("upgrade_monitor", str(e))
        try: conn.close()
        except Exception: pass
        return {"ok":False, "error":str(e)}

def get_upgrade_status(db_path: str|None=None):
    db_path = db_path or DB_PATH
    try:
        conn = sqlite3.connect(db_path); cur = conn.cursor(); _ensure(cur)
        cur.execute("SELECT timestamp,pattern_count,avg_confidence,reviewed_patterns,review_loop_score,score,notes FROM upgrade_score ORDER BY id DESC LIMIT 1")
        r=cur.fetchone(); conn.close()
        if not r: return {"ok":True, "empty":True}
        ts,pc,ac,rp,rls,sc,notes = r
        return {"ok":True, "timestamp":ts, "pattern_count":pc, "avg_confidence":ac, "reviewed_patterns":rp, "review_loop_score":rls, "score":sc, "notes":notes}
    except Exception as e:
        return {"ok":False, "error":str(e)}
