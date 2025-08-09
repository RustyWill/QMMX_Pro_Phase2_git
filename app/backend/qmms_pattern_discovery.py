from datetime import datetime

class PatternDiscovery:
    def __init__(self, levels_by_color):
        self.levels = levels_by_color  # Dict of lists: {color: {solid: [], dashed: []}}
        self.active_patterns = []

    def detect_pattern(self, price, volume, timestamp):
        """
        Scan through levels to identify if price is interacting with any.
        Return potential pattern object if valid.
        """
        detected = []

        for color in self.levels:
            for level_type in ["solid", "dashed"]:
                for level in self.levels[color][level_type]:
                    if self._price_touch(price, level):
                        pattern = {
                            "timestamp": timestamp,
                            "color": color,
                            "level": level,
                            "level_type": level_type,
                            "volume": volume,
                            "contact_order": self._infer_contact_order(level),
                            "approach_direction": self._infer_approach(price, level),
                            "is_confluence": self._check_confluence(price, color),
                            "dominant_reaction": self._guess_reaction(price, level),
                        }
                        detected.append(pattern)
                        self._store(pattern)

        return detected

    def _price_touch(self, price, level):
        # Consider a 0.2 point tolerance window
        return abs(price - level) <= 0.2

    def _infer_contact_order(self, level):
        # TODO: Track contact frequency dynamically
        return 1

    def _infer_approach(self, price, level):
        # Simulate approach direction using current vs previous price
        return "from_above" if price > level else "from_below"

    def _check_confluence(self, price, current_color):
        nearby_hits = 0
        for color in self.levels:
            if color == current_color:
                continue
            for level in self.levels[color]["solid"] + self.levels[color]["dashed"]:
                if abs(price - level) <= 0.4:
                    nearby_hits += 1
        return nearby_hits >= 1

    def _guess_reaction(self, price, level):
        # Placeholder for live price change window check
        return "rejection"

    def _store(self, pattern):
        self.active_patterns.append(pattern)
