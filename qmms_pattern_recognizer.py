# qmms_pattern_recognizer.py

import datetime
from diagnostic_monitor import diagnostic_monitor
from qmms_feature_engineer import FeatureEngineer
from qmms_pattern_discovery import PatternDiscoveryEngine
from level_loader import get_today_levels
from price_feed import get_latest_price

# ✅ Shared context for learning consistency
class QContext:
    def __init__(self):
        self.last_price = None
        self.last_pattern_id = None
        self.level_cache = []

class PatternRecognizer:
    def __init__(self, levels):
        self.levels = levels
        self.latest_pattern = None
        self.context = QContext()
        self.feature_engineer = FeatureEngineer(self.context)
        self.pattern_discovery = PatternDiscoveryEngine()

    def analyze(self, symbol):
        try:
            # Load current price and today’s levels
            current_price = get_latest_price(symbol)
            levels = get_today_levels(symbol) or self.levels

            if not levels or current_price is None:
                raise ValueError("Missing price or levels")

            # Step 1: Extract engineered features (level behavior, contact proximity, etc.)
            features = self.feature_engineer.extract_features(current_price, levels)

            # Step 2: Run discovery engine
            discovered = self.pattern_discovery.discover(features, levels)

            # Step 3: Store pattern if found
            if discovered:
                pattern = {
                    "symbol": symbol,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "pattern_name": discovered["name"],
                    "structure": discovered["structure"],
                    "confidence": discovered["confidence"],
                    "levels_involved": discovered["levels"],
                }
                self.latest_pattern = pattern
                diagnostic_monitor.ping("pattern_recognizer")
                return pattern
            else:
                return {"message": "No pattern found at this moment."}

        except Exception as e:
            diagnostic_monitor.report_error("pattern_recognizer", str(e))
            return {"error": str(e)}

    def get_current_pattern(self):
        return self.latest_pattern if self.latest_pattern else {"message": "No pattern analyzed yet"}
