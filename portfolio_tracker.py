# portfolio_tracker.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "qmmx.db"

# Optional heartbeat — safe no-op if unavailable
try:
    from diagnostic_monitor import diagnostic_monitor as _diag  # type: ignore
    def _ping(name: str, detail: str = ""):
        try:
            _diag.ping(name, detail)
        except Exception:
            pass
except Exception:
    def _ping(name: str, detail: str = ""):
        pass


class PortfolioTracker:
    """
    Minimal, DB-backed portfolio tracker for QMMX.

    Tables used (must match your DB):
      - portfolio_positions(id, opened_at, closed_at, symbol, side, qty,
                            entry, stop, target, exit_price, pnl)
      - portfolio_ledger(id, trade_id, action, price, timestamp)

    Public methods expected by the engine:
      - execute_trade(trade: dict) -> int
      - close_trade(trade: dict, exit_price: float) -> bool
      - get_open_positions() -> List[dict]
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_schema()
        self.open_positions: List[Dict] = []
        self._reload_open_positions()

    # ---------- SQLite helpers ----------

    def _conn(self):
        # small timeout for engine+API concurrent access
        con = sqlite3.connect(self.db_path, timeout=5)
        con.execute("PRAGMA busy_timeout=5000;")
        return con

    def _ensure_schema(self):
        con = self._conn()
        cur = con.cursor()

        # portfolio_positions
        cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opened_at   TEXT,
            closed_at   TEXT,
            symbol      TEXT,
            side        TEXT,       -- 'long' | 'short'
            qty         REAL,
            entry       REAL,
            stop        REAL,
            target      REAL,
            exit_price  REAL,
            pnl         REAL
        )
        """)

        # portfolio_ledger
        cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id    INTEGER,
            action      TEXT,       -- 'OPEN' | 'CLOSE'
            price       REAL,
            timestamp   TEXT
        )
        """)

        con.commit()
        con.close()

    def _reload_open_positions(self):
        """Refresh in-memory open positions from DB."""
        con = self._conn()
        cur = con.cursor()
        cur.execute("""
            SELECT id, symbol, side, qty, entry, stop, target
              FROM portfolio_positions
             WHERE closed_at IS NULL
             ORDER BY id ASC
        """)
        rows = cur.fetchall()
        con.close()

        self.open_positions = []
        for pid, sym, side, qty, entry, stop, target in rows:
            self.open_positions.append({
                "id": pid,
                "symbol": sym,
                "direction": side,
                "qty": qty if qty is not None else 1.0,
                "entry_price": entry,
                "stop": stop,
                "target": target,
            })

    # ---------- Public API used by the engine ----------

    def get_open_positions(self) -> List[Dict]:
        """Return open positions in the shape the engine/UI expect."""
        self._reload_open_positions()
        return list(self.open_positions)

    def execute_trade(self, trade: Dict) -> int:
        """
        Open a position and write an OPEN ledger row.

        trade dict should include:
          symbol, direction('long'|'short'), entry_price, entry_time (ISO)
          optional: qty, stop, target
        """
        # Ensure contract key exists to avoid KeyError elsewhere
        trade.setdefault("contract", None)

        symbol    = trade["symbol"]
        side      = trade.get("direction", "long")
        entry     = float(trade["entry_price"])
        opened_at = trade.get("entry_time", datetime.utcnow().isoformat())
        qty       = float(trade.get("qty", 1))
        stop      = float(trade.get("stop", entry - 0.50))
        target    = float(trade.get("target", entry + 0.80))

        con = self._conn()
        cur = con.cursor()

        # Insert position
        cur.execute("""
            INSERT INTO portfolio_positions (opened_at, symbol, side, qty, entry, stop, target)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (opened_at, symbol, side, qty, entry, stop, target))
        trade_id = cur.lastrowid

        # Ledger OPEN
        cur.execute("""
            INSERT INTO portfolio_ledger (trade_id, action, price, timestamp)
            VALUES (?, 'OPEN', ?, ?)
        """, (trade_id, entry, opened_at))

        con.commit()
        con.close()

        trade["portfolio_trade_id"] = trade_id

        # Update in-memory snapshot
        self._upsert_open({
            "id": trade_id,
            "symbol": symbol,
            "direction": side,
            "qty": qty,
            "entry_price": entry,
            "stop": stop,
            "target": target
        })

        _ping("portfolio tracker", f"OPEN {symbol} {side} @ {entry}")
        return trade_id

    def close_trade(self, trade: Dict, exit_price: float) -> bool:
        """
        Close a position by trade dict and write a CLOSE ledger row.
        If 'portfolio_trade_id' not present, match most recent open for (symbol, direction).
        """
        # NEW: ensure contract key exists here too (symmetric with execute_trade)
        trade.setdefault("contract", None)  # ← added safeguard

        trade_id: Optional[int] = trade.get("portfolio_trade_id")

        con = self._conn()
        cur = con.cursor()

        if not trade_id:
            # Find by symbol+side (most recent open)
            cur.execute("""
                SELECT id FROM portfolio_positions
                 WHERE closed_at IS NULL AND symbol = ? AND side = ?
              ORDER BY id DESC LIMIT 1
            """, (trade["symbol"], trade.get("direction", "long")))
            row = cur.fetchone()
            if row:
                trade_id = int(row[0])
            else:
                con.close()
                return False

        # Fetch entry & side for PnL calc
        cur.execute("SELECT entry, side FROM portfolio_positions WHERE id = ?", (trade_id,))
        row = cur.fetchone()
        if not row:
            con.close()
            return False

        entry, side = float(row[0]), row[1]
        sign = 1.0 if side == "long" else -1.0
        pnl_pct = sign * (float(exit_price) - entry) / entry
        closed_at = trade.get("exit_time", datetime.utcnow().isoformat())

        # Update position with close data
        cur.execute("""
            UPDATE portfolio_positions
               SET closed_at = ?, exit_price = ?, pnl = ?
             WHERE id = ?
        """, (closed_at, float(exit_price), float(pnl_pct), trade_id))

        # Ledger CLOSE
        cur.execute("""
            INSERT INTO portfolio_ledger (trade_id, action, price, timestamp)
            VALUES (?, 'CLOSE', ?, ?)
        """, (trade_id, float(exit_price), closed_at))

        con.commit()
        con.close()

        # Reflect in memory and annotate trade dict
        self._remove_open(trade_id)
        trade["portfolio_trade_id"] = trade_id
        trade["pnl"] = pnl_pct
        trade["exit_price"] = float(exit_price)
        trade["exit_time"] = closed_at

        _ping("portfolio tracker", f"CLOSE {trade.get('symbol','?')} {side} pnl {pnl_pct:.4f}")
        return True

    # ---------- in-memory mirror helpers ----------

    def _upsert_open(self, pos: Dict):
        for i, p in enumerate(self.open_positions):
            if p["id"] == pos["id"]:
                self.open_positions[i] = pos
                return
        self.open_positions.append(pos)

    def _remove_open(self, trade_id: int):
        self.open_positions = [p for p in self.open_positions if p["id"] != trade_id]
