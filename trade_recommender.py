from pattern_evolution import PatternEvolutionTracker
import requests  # ✅ Added

class TradeRecommender:
    def __init__(self):
        self.pattern_tracker = PatternEvolutionTracker()
        self.last_recommendation = None  # ✅ Store last recommendation for /get_recommendations

    def recommend_trade(self, contact_event):
        """
        Given a contact event, determine if a trade should be taken and in what direction.
        """
        # ✅ Pulse panel heartbeat
        try:
            requests.post("http://127.0.0.1:5000/ping", json={"module": "trade_recommender"})
        except:
            pass

        pattern_signature = {
            "level_type": contact_event.get("level_type"),
            "reaction_type": contact_event.get("reaction_type"),
            "approach_direction": contact_event.get("direction_of_approach"),
            "macro_position": contact_event.get("macro_position")
        }

        direction = self.pattern_tracker.get_best_direction_for_pattern(pattern_signature)
        if direction is None:
            return None  # No historical edge, skip recommendation

        recommendation = {
            "symbol": "SPY",
            "direction": direction,
            "pattern": pattern_signature
        }

        self.last_recommendation = recommendation  # ✅ Save it
        return recommendation

    def record_trade_outcome(self, contact_event, direction, was_successful):
        """
        Logs the result of a trade to help evolve pattern confidence.
        """
        pattern_signature = {
            "level_type": contact_event.get("level_type"),
            "reaction_type": contact_event.get("reaction_type"),
            "approach_direction": contact_event.get("direction_of_approach"),
            "macro_position": contact_event.get("macro_position")
        }

        self.pattern_tracker.record_result(pattern_signature, direction, was_successful)

    def get_latest_recommendation(self):
        """
        ✅ Return the most recent trade recommendation.
        """
        return self.last_recommendation
