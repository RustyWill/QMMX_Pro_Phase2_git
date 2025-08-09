# qmms_pattern_discovery.py

from contact_event_evaluator import evaluate_contact  # ✅ correct usage
from diagnostic_state import diagnostic_monitor       # ✅ correct source
import datetime

class PatternDiscoveryEngine:
    def __init__(self):
        self.contact_history = {}  # key: level price, value: [timestamps]

    def discover(self, features, levels):
        try:
            current_price = features.get("price")
            if current_price is None:
                return None

            # Search for the nearest level within a tight window
            window = 0.3  # adjustable
            triggered_level = None
            print(f"\n🔍 Scanning for contact at price: {current_price}")
            for level in levels:
                dist = abs(current_price - level["price"])
                print(f"  🔸 Level: {level['price']} ({level['color']} {level['type']}) → Δ = {dist:.3f}")
                if dist <= window:
                    print("    ✅ Within contact range!")
                    triggered_level = level
                    break

            if not triggered_level:
                return None  # No level contacted

            # Determine contact order
            level_key = triggered_level["price"]
            now = datetime.datetime.now()
            if level_key not in self.contact_history:
                self.contact_history[level_key] = []
            self.contact_history[level_key].append(now)
            contact_order = len(self.contact_history[level_key])

            # Run contact evaluator logic
            evaluation = evaluate_contact(
                current_price=current_price,
                level=triggered_level,
                direction=features.get("direction"),
                price_history=features.get("price_history", []),
                volume_profile=features.get("volume_profile", {}),
                order=contact_order
            )
            print(f"🧠 Contact Evaluated → reaction: {evaluation.get('reaction')}, direction: {evaluation.get('approach_direction')}, order: {contact_order}")

            # If valid, create structured pattern object
            if evaluation.get("reaction") in ["rejection", "breakthrough", "hesitation"]:
                pattern = {
                    "name": f"{evaluation['reaction'].capitalize()} at {triggered_level['color']} {triggered_level['type']} L{level_key}",
                    "structure": evaluation,
                    "confidence": evaluation.get("confidence", 0.7),
                    "levels": [triggered_level],
                    "discovered_at": now.isoformat()
                }

                diagnostic_monitor.ping("pattern_discovery")
                return pattern

            return None

        except Exception as e:
            diagnostic_monitor.report_error("pattern_discovery", str(e))
            return {"error": str(e)}
