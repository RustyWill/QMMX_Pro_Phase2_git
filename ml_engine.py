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
import migrate; migrate.migrate()

# -------------------- ADDITIONS (safe, optional) --------------------
import os

# Demo / gating levers (affect ONLY the gate, not how confidence is computed)
DEMO_LOOSE = os.environ.get("Q_DEMO_LOOSE", "0") == "1"
# Normal required probability to act (change this to your normal if different)
_DEFAULT_MIN_PROB = 0.75
MIN_PROB = float(os.environ.get("Q_MIN_PROB", 0.40 if DEMO_LOOSE else _DEFAULT_MIN_PROB))

# Optional: simple cooldown between emitted signals (seconds)
COOLDOWN_SEC = int(os.environ.get("Q_SIGNAL_COOLDOWN", "120"))
_last_signal_ts = 0

def _cooldown_ok():
    global _last_signal_ts
    now = time.time()
    if now - _last_signal_ts < COOLDOWN_SEC:
        return False
    _last_signal_ts = now
    return True

# Optional: one-shot force for end-to-end proof. Run engine with Q_FORCE_TEST=1 to emit once.
_FORCE_ONCE = os.environ.get("Q_FORCE_TEST", "0") == "1"
# -------------------------------------------------------------------

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
            contact_event, status, mode           -- ✅ mode tag added
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade["symbol"],
        trade["direction"],
        trade["entry_price"],
        trade["entry_time"],
        trade["confidence"],
        trade["pattern_id"],
        trade["pattern"],
        str(trade["contact_event"]),
        trade["status"],
        trade.get("mode", "live")               # ✅ persist mode
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
            approach_direction, macro_position,
            mode                               -- ✅ store mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        rec["symbol"],
        rec["direction"],
        rec["pattern"].get("level_type"),
        rec["pattern"].get("reaction_type"),
        rec["pattern"].get("approach_direction"),
        rec["pattern"].get("macro_position"),
        rec.get("mode", "live")                # ✅ persist mode
    ))
    conn.commit()
    conn.close()

def trading_loop():
    global _FORCE_ONCE
    while True:
        try:
            # ✅ Heartbeats so tiles go green
            try:
                diagnostic_monitor.ping("ml engine")
                diagnostic_monitor.ping("price feed")
            except Exception:
                pass

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

            # ✅ Optional forced one-time rec to prove E2E wiring (no impact otherwise)
            if _FORCE_ONCE:
                try:
                    rec = {
                        "symbol": symbol,
                        "direction": "long",
                        "pattern": {
                            "level_type": "test",
                            "reaction_type": "test",
                            "approach_direction": "test",
                            "macro_position": "test"
                        },
                        "mode": "demo" if DEMO_LOOSE else "live"
                    }
                    log_recommendation_to_db(rec)
                    # minimal "enter" to show up in UI/DB, honoring cooldown
                    if _cooldown_ok():
                        trade = {
                            "symbol": symbol,
                            "direction": rec["direction"],
                            "entry_price": current_price,
                            "entry_time": timestamp,
                            "confidence": 0.72,
                            "pattern_id": "n/a",
                            "pattern": "test_break_retest",
                            "contact_event": rec["pattern"],
                            "status": "open",
                            "mode": "demo" if DEMO_LOOSE else "live"
                        }
                        try:
                            diagnostic_monitor.ping("trade recommender", "forced test")
                            diagnostic_monitor.ping("alerts")
                        except Exception:
                            pass
                        trade.setdefault("contract", None)
                        portfolio.execute_trade(trade)
                        log_trade_to_db(trade)
                    _FORCE_ONCE = False
                except Exception as fe:
                    print("⚠️ Forced test failed:", fe)
                # continue flow to allow normal logic as well

            pattern = recognizer.analyze(symbol)

            if pattern and "pattern_name" in pattern:
                # ✅ Heartbeats for analysis modules
                try:
                    diagnostic_monitor.ping("contact event evaluator")
                    diagnostic_monitor.ping("pattern discovery")
                    diagnostic_monitor.ping("pattern memory engine")
                    diagnostic_monitor.ping("confidence monitor")
                except Exception:
                    pass

                pattern_id = pattern.get("pattern_name", "unknown")
                ticker = symbol
                base_score = 0.5
                scored_confidence = adjust_confidence_with_memory(pattern_id, base_score, ticker)
                pattern["confidence"] = scored_confidence

                print(f"🧠 Pattern: {pattern['pattern_name']} | Confidence: {pattern.get('confidence')}")
                contact_event = pattern["structure"]

                recommendation = recommender.recommend_trade(contact_event)
                if recommendation:
                    # Tag mode for later analysis
                    recommendation["mode"] = "demo" if DEMO_LOOSE else "live"

                    print(f"✅ Reco: {recommendation['direction']} @ {current_price:.2f}")
                    log_recommendation_to_db(recommendation)

                    # -------------------- GATE (added) --------------------
                    # Only proceed if confidence meets gate AND cooldown ok
                    if (scored_confidence >= MIN_PROB) and _cooldown_ok():
                        # ✅ Heartbeat: recommender is active
                        try:
                            diagnostic_monitor.ping("trade recommender", f"emit {pattern['pattern_name']} {scored_confidence:.2f}")
                            diagnostic_monitor.ping("alerts")
                        except Exception:
                            pass
                        # ----------------------------------------------------

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
                                "status": "open",
                                "mode": "demo" if DEMO_LOOSE else "live"   # ✅ tag
                            }

                            trade.setdefault("contract", None)
                            portfolio.execute_trade(trade)
                            log_trade_to_db(trade)
                        else:
                            print("🚫 Entry rejected by SmartEntryPlanner")
                    else:
                        print(f"🧯 Skipped by gate: conf {scored_confidence:.2f} < MIN_PROB {MIN_PROB:.2f} or cooling down")
                    # ------------------ END GATE ---------------------------

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

                            # During demo/bootstrapping, we still record outcome,
                            # but since we tagged mode, you can down-weight later in training.
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
