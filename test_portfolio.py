from portfolio_tracker import PortfolioTracker
from datetime import datetime

pt = PortfolioTracker("qmmx.db")

trade = {
    "symbol": "SPY",
    "direction": "long",
    "entry_price": 645.12,
    "entry_time": datetime.utcnow().isoformat()
}

tid = pt.execute_trade(trade)
print("OPENED:", tid)

pt.close_trade(trade, 645.42)
print("CLOSED:", tid)
