import time
import threading
import sqlite3
from datetime import datetime
from polygon_io_provider import get_live_stock_price
from trade_recommender import TradeRecommender
from exit_strategy import ExitStrategy
from portfolio_tracker import PortfolioTracker
from contact_event_evaluator import evaluate_contact
from backend.confidence_adjuster import record_pattern_outcome
from backend.confidence_scorer import adjust_confidence_with_memory
from backend.pattern_resilience import record_resilience
from qmms_pattern_recognizer import PatternRecognizer
from diagnostic_engine import run_diagnostics
from diagnostic_state import diagnostic_monitor
from level_loader import load_levels
from smart_entry_planner import SmartEntryPlanner
from pattern_evolution import PatternEvolutionTracker  # ✅ NEW

symbol = "SPY"
poll_interval = 0.1
db_path = "qmmx.db"

print("✅ QMMX ML Engine initialized.")
print(f"  Symbol: {symbol}, Poll Interval: {poll_interval:.01f}s")

recommender = TradeRecommender()
portfolio = PortfolioTracker()
exit_strategy = ExitStrategy()
recognizer = PatternRecognizer(levels=[])
entry_planner = SmartEntryPlanner()
evolution_tracker = PatternEvolutionTracker()  # ✅ INIT

def log_trade_to_db(trade):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (
            symbol, direction, entry_price, entry_time,
            confidence, pattern_id, pattern_name,
            contact_event, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade["symbol"],
        trade["direction"],
        trade["entry_price"],
        trade["entry_time"],
        trade["confidence"],
        trade["pattern_id"],
        trade["pattern"],
        str(trade["contact_event"]),
        trade["status"]
    ))
    conn.commit()
    conn.close()

def log_false_missed(type_, symbol, price, level, level_color, level_type,
                     reaction, pattern_id, confidence, volume, contact_order, notes=""):
    conn = sqlite3.connect("qmmx.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO false_missed_analysis (
            timestamp, type, symbol, price, level, level_color, level_type,
            reaction, pattern_id, confidence, volume, contact_order, notes
        ) VALUES (
            DATETIME('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        type_, symbol, price, level, level_color, level_type,
        reaction, pattern_id, confidence, volume, contact_order, notes
    ))
    conn.commit()
    conn.close()

def log_exit_to_db(trade):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE trades
        SET exit_price = ?, exit_time = ?, pnl = ?, exit_reason = ?, status = ?
        WHERE symbol = ? AND entry_price = ? AND entry_time = ?
    """, (
        trade.get("exit_price"),
        trade.get("exit_time"),
        trade.get("pnl"),
        trade.get("exit_reason"),
        trade.get("status"),
        trade["symbol"],
        trade["entry_price"],
        trade["entry_time"]
    ))
    conn.commit()
    conn.close()

def log_recommendation_to_db(rec):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trade_recommendations (
            timestamp, symbol, direction,
            level_type, reaction_type,
            approach_direction, macro_position
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        rec["symbol"],
        rec["direction"],
        rec["pattern"].get("level_type"),
        rec["pattern"].get("reaction_type"),
        rec["pattern"].get("approach_direction"),
        rec["pattern"].get("macro_position")
    ))
    conn.commit()
    conn.close()

def trading_loop():
    while True:
        try:
            diagnostic_monitor.ping("ml_engine")

            current_price = get_live_stock_price(symbol)
            levels = load_levels()
            print(f"📡 Current Price: {current_price}")
            print(f"📏 Loaded Levels: {[round(lvl['price'], 2) for lvl in levels]}")

            # ✅ Contact Event Logging
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                for level in levels:
                    level_price = level["price"]
                    level_color = level["color"]
                    level_type = level["type"]
                    dist = abs(current_price - level_price)

                    if dist <= 0.05:
                        contact_event = evaluate_contact(
                            current_price,
                            {
                                "price": level_price,
                                "type": level_type,
                                "color": level_color
                            },
                            "from_above" if current_price < level_price else "from_below",
                            levels,
                            {},
                            1
                        )

                        cursor.execute("""
                            INSERT INTO contact_events (
                                timestamp, symbol, level_price, direction,
                                contact_type, reaction, context,
                                level_color, level_type, contact_order
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            symbol,
                            level_price,
                            contact_event.get("approach_direction"),
                            "level_touch",
                            contact_event.get("reaction"),
                            str(contact_event.get("context")),
                            level_color,
                            level_type,
                            contact_event.get("contact_order")
                        ))

                        conn.commit()
                        print(f"📍 Logged contact: {level_color} {level_type} @ {level_price} → {contact_event.get('reaction')}")

                conn.close()
            except Exception as ce:
                print("⚠️ Contact event logging failed:", ce)

            if current_price is None:
                print("⚠️ No live price")
                time.sleep(poll_interval)
                continue

            print(f"\n📍 {datetime.now().strftime('%H:%M:%S')} Price: {current_price:.2f}")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pattern = recognizer.analyze(symbol)

            if pattern and "pattern_name" in pattern:
                pattern_id = pattern.get("pattern_name", "unknown")
                ticker = symbol
                base_score = 0.5
                scored_confidence = adjust_confidence_with_memory(pattern_id, base_score, ticker)
                pattern["confidence"] = scored_confidence

                print(f"🧠 Pattern: {pattern['pattern_name']} | Confidence: {pattern.get('confidence')}")
                contact_event = pattern["structure"]

                recommendation = recommender.recommend_trade(contact_event)
                if recommendation:
                    print(f"✅ Reco: {recommendation['direction']} @ {current_price:.2f}")
                    log_recommendation_to_db(recommendation)

                    entry_check = entry_planner.should_enter(
                        current_price=current_price,
                        current_volume=0,
                        current_time=datetime.now().timestamp(),
                        pattern=pattern
                    )

                    if entry_check:
                        trade = {
                            "symbol": symbol,
                            "direction": recommendation["direction"],
                            "entry_price": current_price,
                            "entry_time": timestamp,
                            "confidence": pattern.get("confidence", 0.7),
                            "pattern_id": "n/a",
                            "pattern": pattern["pattern_name"],
                            "contact_event": contact_event,
                            "status": "open"
                        }

                        portfolio.execute_trade(trade)
                        log_trade_to_db(trade)
                    else:
                        print("🚫 Entry rejected by SmartEntryPlanner")
                else:
                    print("🛑 No trade recommendation")
            else:
                print("⚪ No pattern found")

            exits = exit_strategy.evaluate_exit_conditions(portfolio, current_price, timestamp)
            for signal in exits:
                print(f"🚪 Exit: {signal['reason']} | PnL: {signal['pnl_pct']*100:.2f}%")
                for trade in portfolio.get_open_positions():
                    if trade["symbol"] == signal["symbol"] and trade["direction"] == signal["direction"]:
                        exited = portfolio.close_trade(trade, signal["exit_price"])
                        if exited:
                            trade["exit_price"] = signal["exit_price"]
                            trade["exit_time"] = signal["timestamp"]
                            trade["pnl"] = signal["pnl_pct"]
                            trade["exit_reason"] = signal["reason"]
                            trade["status"] = "closed"

                            log_exit_to_db(trade)
                            record_pattern_outcome(trade["pattern"], trade["pnl"] > 0)
                            record_resilience(
                                pattern_name=trade["pattern"],
                                outcome="win" if trade["pnl"] > 0 else "loss",
                                confidence=trade["confidence"],
                                reaction_score=1.0
                            )
                            # ✅ Pattern Evolution Trigger
                            evolution_tracker.record_result(
                                pattern_signature=trade["contact_event"],
                                direction=trade["direction"],
                                was_successful=(trade["pnl"] > 0)
                            )

            run_diagnostics()

        except Exception as e:
            print("❌ ML Engine Error:", str(e))

        time.sleep(poll_interval)


threading.Thread(target=trading_loop, daemon=True).start()

try:
    while True:
        time.sleep(poll_interval)
except KeyboardInterrupt:
    print("🛑 Engine stopped by user.")
