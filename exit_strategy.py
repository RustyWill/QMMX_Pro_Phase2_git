import sqlite3
import requests  # ✅ Added
from datetime import datetime
from pattern_memory_engine import get_pattern_id


class ExitStrategy:
    def __init__(self):
        self.max_loss_pct = 0.30  # 30% default max loss before forced exit

    def evaluate_exit_conditions(self, portfolio, current_price, timestamp):
        """
        Loop through all open positions and decide whether to exit.
        Returns a list of exits with reasons.
        """
        exits = []

        for trade in portfolio.open_positions:
            entry_price = trade["entry_price"]
            direction = trade["direction"]
            contract = trade["contract"]
            size = trade.get("quantity", 1)
            pattern_id = trade.get("pattern_id", None)

            # Determine % change
            if direction == "long":
                pct_change = (current_price - entry_price) / entry_price
            elif direction == "short":
                pct_change = (entry_price - current_price) / entry_price
            else:
                continue  # Unknown direction

            # Rule: Max Loss Exceeded
            if pct_change <= -self.max_loss_pct:
                exits.append({
                    "symbol": trade["symbol"],
                    "contract": contract,
                    "exit_price": current_price,
                    "timestamp": timestamp,
                    "pattern_id": pattern_id,
                    "reason": "max_loss_triggered",
                    "pnl_pct": pct_change,
                    "direction": direction,
                    "size": size
                })
                continue

            # Rule: Reaction at key level (basic placeholder for now)
            if self.level_reaction_detected(current_price):
                exits.append({
                    "symbol": trade["symbol"],
                    "contract": contract,
                    "exit_price": current_price,
                    "timestamp": timestamp,
                    "pattern_id": pattern_id,
                    "reason": "level_reaction",
                    "pnl_pct": pct_change,
                    "direction": direction,
                    "size": size
                })

        # ✅ Pulse after evaluation
        try:
            requests.post("http://127.0.0.1:5000/ping", json={"module": "exit_strategy"})
        except:
            pass

        return exits

    def level_reaction_detected(self, price):
        # Placeholder for now — return False to avoid dummy exits
        # You can plug in real logic here later based on Contact Event Evaluator
        return False
