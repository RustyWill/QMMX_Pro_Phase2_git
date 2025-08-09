from diagnostic_monitor import diagnostic_monitor  # ✅ Added

class generate_strategies:
    def __init__(self):
        pass

    def build_trade_plan(self, pattern, current_price, option_chain):
        """
        Based on pattern characteristics, builds a directional option trade plan.
        """
        try:
            direction = self._determine_direction(pattern)
            if direction is None:
                diagnostic_monitor.report_error("strategy_engine", "Indeterminate trade direction")
                return None

            entry_price = current_price
            stop_loss = self._calculate_stop(entry_price, direction)
            target_price = self._calculate_target(entry_price, direction)

            # Select suitable contract from chain
            contract = self._choose_option_contract(option_chain, direction)

            if not contract:
                diagnostic_monitor.report_error("strategy_engine", "No valid option contract found")
                return None

            trade_plan = {
                "timestamp": pattern["timestamp"],
                "direction": direction,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "target_price": target_price,
                "option": contract
            }

            diagnostic_monitor.ping("strategy_engine")  # ✅ Success
            return trade_plan

        except Exception as e:
            diagnostic_monitor.report_error("strategy_engine", f"Strategy error: {e}")  # ✅ Failure
            return None

    def _determine_direction(self, pattern):
        if pattern["dominant_reaction"] == "rejection":
            return "long" if pattern["approach_direction"] == "from_above" else "short"
        elif pattern["dominant_reaction"] == "break":
            return "short" if pattern["approach_direction"] == "from_above" else "long"
        return None

    def _calculate_stop(self, entry, direction):
        return entry - 3 if direction == "long" else entry + 3

    def _calculate_target(self, entry, direction):
        return entry + 10 if direction == "long" else entry - 10

    def _choose_option_contract(self, option_chain, direction):
        try:
            for option in option_chain:
                if direction == "long" and option["type"] == "call" and option["strike"] > option["underlying_price"]:
                    return option
                elif direction == "short" and option["type"] == "put" and option["strike"] < option["underlying_price"]:
                    return option
        except Exception as e:
            diagnostic_monitor.report_error("strategy_engine", f"Option selection error: {e}")
        return None
