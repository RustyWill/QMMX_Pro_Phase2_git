import datetime
import requests

class ContactEventEvaluator:
    def __init__(self):
        self.history = {}

    def evaluate_contact(self, price, timestamp, level_data, volume, symbol="SPY"):
        level_value = level_data["value"]
        level_type = level_data["type"]
        level_color = level_data["color"]
        recent_levels = level_data.get("all_levels", [])

        # Determine approach direction
        previous = self.history.get(level_value)
        direction = "unknown"
        if previous:
            prev_price, _ = previous
            if price > prev_price:
                direction = "from_below"
            elif price < prev_price:
                direction = "from_above"

        # Track order of contact
        contact_order = self._update_contact_order(level_value, timestamp)

        # Determine reaction
        reaction = self._classify_reaction(price, level_value, direction, contact_order)

        # Estimate confidence
        confidence = self._assign_confidence(reaction, volume)

        # ✅ Heartbeat ping
        try:
            requests.post("http://127.0.0.1:5000/ping", json={"module": "contact_event_evaluator"})
        except:
            pass

        return {
            "symbol": symbol,
            "level": level_value,
            "type": level_type,
            "color": level_color,
            "approach_direction": direction,
            "reaction": reaction,
            "contact_order": contact_order,
            "confidence": confidence,
            "volume": volume,
            "context": recent_levels
        }

    def _update_contact_order(self, level, timestamp):
        if level not in self.history:
            self.history[level] = (0, [])
        order, visits = self.history[level]
        visits.append(timestamp)
        self.history[level] = (order + 1, visits)
        return order + 1

    def _classify_reaction(self, price, level_value, direction, contact_order):
        delta = price - level_value
        if abs(delta) < 0.02:
            if contact_order == 1:
                return "rejection"
            elif direction == "from_below" and delta > 0:
                return "breakthrough"
            elif direction == "from_above" and delta < 0:
                return "breakthrough"
            else:
                return "hesitation"
        return "none"

    def _assign_confidence(self, reaction, volume):
        if reaction in ["rejection", "breakthrough"]:
            if volume >= 100000:  # ← Threshold can be adjusted
                return 0.85
            elif volume >= 50000:
                return 0.7
            else:
                return 0.5
        elif reaction == "hesitation":
            return 0.4
        return 0.2

# Shared instance
evaluator_instance = ContactEventEvaluator()

# Wrapper for modules expecting a function
def evaluate_contact(current_price, level, direction, price_history, volume_profile, order):
    recent_volume = volume_profile[-1]["v"] if volume_profile else 0
    return evaluator_instance.evaluate_contact(
        price=current_price,
        timestamp=datetime.datetime.now(),
        level_data={
            "value": level["price"],
            "type": level.get("type"),
            "color": level.get("color"),
            "all_levels": [l["price"] for l in price_history[-10:]]
        },
        volume=recent_volume
    )
