# qmms_strategies.py

from diagnostic_monitor import diagnostic_monitor
from datetime import datetime

class QStrategyEngine:
    def __init__(self, level_data):
        self.levels = sorted(level_data, key=lambda x: x["price"])
        self.option_data = None  # Set later if available

    def update_option_chain(self, option_chain):
        self.option_data = option_chain

    def generate_trade_recommendation(self, pattern):
        try:
            structure = pattern.get("structure", {})
            base_price = structure.get("level")
            direction = structure.get("approach_direction")
            reaction = structure.get("reaction")
            confidence = pattern.get("confidence", 0.5)

            if not base_price or direction == "unknown" or reaction not in ["rejection", "breakthrough"]:
                return None

            # Determine long/short bias
            side = self._determine_side(direction, reaction)
            if side is None:
                return None

            # Dynamic levels
            target, stop = self._calculate_exit_levels(base_price, side)
            contract = self._select_option(side, base_price)

            trade = {
                "entry_price": base_price,
                "target_price": target,
                "stop_price": stop,
                "direction": side,
                "confidence": confidence,
                "pattern": pattern["name"],
                "option_contract": contract,
                "timestamp": datetime.now().isoformat()
            }

            diagnostic_monitor.ping("strategy_engine")
            return trade

        except Exception as e:
            diagnostic_monitor.report_error("strategy_engine", str(e))
            return {"error": str(e)}

    def _determine_side(self, direction, reaction):
        if direction == "from_below" and reaction == "rejection":
            return "short"
        elif direction == "from_above" and reaction == "rejection":
            return "long"
        elif direction == "from_below" and reaction == "breakthrough":
            return "long"
        elif direction == "from_above" and reaction == "breakthrough":
            return "short"
        return None

    def _calculate_exit_levels(self, base_price, side):
        offset = 1.2  # can be adaptive later
        if side == "long":
            return round(base_price + offset, 2), round(base_price - offset * 0.6, 2)
        else:
            return round(base_price - offset, 2), round(base_price + offset * 0.6, 2)

    def _select_option(self, side, strike):
        if not self.option_data:
            return "No option data"

        # Find closest strike
        sorted_chain = sorted(self.option_data, key=lambda o: abs(o["strike"] - strike))
        for opt in sorted_chain:
            if side == "long" and opt["type"] == "call":
                return opt
            elif side == "short" and opt["type"] == "put":
                return opt
        return sorted_chain[0] if sorted_chain else "N/A"
