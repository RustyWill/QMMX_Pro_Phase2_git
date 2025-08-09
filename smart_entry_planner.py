from diagnostic_monitor import diagnostic_monitor

class SmartEntryPlanner:
    def __init__(self):
        self.min_volume_threshold = 25000  # minimum per-bar volume to validate momentum
        self.slippage = 0.25  # price tolerance for entry
        self.timing_window = 2  # minute tolerance to pattern timestamp

    def should_enter(self, current_price, current_volume, current_time, pattern):
        try:
            if not self._is_recent(current_time, pattern["timestamp"]):
                diagnostic_monitor.report_error("entry_planner", "Pattern too old")
                return None

            if not self._volume_valid(current_volume):
                diagnostic_monitor.report_error("entry_planner", "Volume too low")
                return None

            if not self._is_near_level(current_price, pattern["level"]):
                diagnostic_monitor.report_error("entry_planner", "Price too far from level")
                return None

            direction = self._decide_direction(pattern)
            if not direction:
                diagnostic_monitor.report_error("entry_planner", "No entry direction inferred")
                return None

            entry_signal = {
                "timestamp": current_time,
                "direction": direction,
                "price": current_price,
                "level": pattern["level"],
                "reason": "SmartEntry (no options)"
            }

            diagnostic_monitor.ping("entry_planner")  # ✅ Success
            return entry_signal

        except Exception as e:
            diagnostic_monitor.report_error("entry_planner", f"Entry planner failed: {e}")
            return None

    def _is_recent(self, now_ts, pattern_ts):
        return abs(now_ts - pattern_ts) <= (self.timing_window * 60)

    def _volume_valid(self, volume):
        return volume >= self.min_volume_threshold

    def _is_near_level(self, price, level):
        return abs(price - level) <= self.slippage

    def _decide_direction(self, pattern):
        if pattern["dominant_reaction"] == "rejection":
            return "long" if pattern["approach_direction"] == "from_below" else "short"
        elif pattern["dominant_reaction"] == "break":
            return "short" if pattern["approach_direction"] == "from_above" else "long"
        return None
