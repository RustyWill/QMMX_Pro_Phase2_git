# portfolio_tracker.py

import time
import requests  # ✅ Heartbeat support
from datetime import datetime

class PortfolioTracker:
    def __init__(self):
        self.balance = 10000.00
        self.open_positions = []
        self.closed_positions = []

    def execute_trade(self, trade):
        shares = 1
        cost = shares * trade["entry_price"]

        if trade["direction"] == "long":
            if self.balance < cost:
                print("❌ Not enough balance to open long position.")
                return
            self.balance -= cost
        elif trade["direction"] == "short":
            # In this simulation, assume we can short 1 share freely
            pass
        else:
            print("❌ Invalid trade direction:", trade["direction"])
            return

        trade["shares"] = shares
        trade["current_price"] = trade["entry_price"]
        trade["profit"] = 0.0

        self.open_positions.append(trade)

        # ✅ Heartbeat ping
        try:
            requests.post("http://127.0.0.1:5000/ping", json={"module": "portfolio_tracker"})
        except:
            pass

    def update_prices(self, current_price):
        for trade in self.open_positions:
            trade["current_price"] = current_price
            shares = trade.get("shares", 1)
            if trade["direction"] == "long":
                trade["profit"] = (current_price - trade["entry_price"]) * shares
            elif trade["direction"] == "short":
                trade["profit"] = (trade["entry_price"] - current_price) * shares

    def close_trade(self, trade, exit_price):
        if trade not in self.open_positions:
            print("⚠️ Trade not found in open positions.")
            return

        trade["exit_price"] = exit_price
        trade["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trade["pnl"] = trade.get("profit", 0.0)

        if trade["direction"] == "long":
            self.balance += exit_price * trade.get("shares", 1)
        elif trade["direction"] == "short":
            self.balance += (2 * trade["entry_price"] - exit_price) * trade.get("shares", 1)

        self.open_positions.remove(trade)
        self.closed_positions.append(trade)

    def log_trade_to_db(self, trade):
        # TODO: Actual DB logging (optional)
        print("📝 Logging trade:", trade)

    def get_open_positions(self):
        return self.open_positions

    def get_closed_positions(self):
        return self.closed_positions

    def get_balance(self):
        return self.balance

    def get_portfolio(self):
        return {
            "balance": round(self.balance, 2),
            "open_positions": self.open_positions,
            "closed_positions": self.closed_positions
        }
