import numpy as np

class FeatureEngineer:
    def __init__(self, context):
        self.context = context  # Contains price levels, volume norms, contact history, etc.

    def extract_features(self, pattern, current_price, current_volume, timestamp):
        """
        Converts pattern and environment into a structured ML feature vector.
        """
        features = []

        level = pattern["level"]
        color = pattern["color"]
        level_type = pattern["level_type"]  # solid/dashed
        reaction = pattern["dominant_reaction"]
        contact_order = pattern["contact_order"]
        approach_direction = pattern["approach_direction"]
        confluence = 1 if pattern.get("is_confluence") else 0

        # --- Volume Behavior ---
        norm_volume = self.context.get("volume_norm", 1.0)
        vol_ratio = current_volume / norm_volume if norm_volume > 0 else 1.0
        features.append(round(vol_ratio, 3))

        # --- Distance to Next Level ---
        all_levels = self.context.get("all_levels", [])
        if all_levels:
            min_dist = min([abs(current_price - lvl) for lvl in all_levels])
            features.append(round(min_dist, 2))
        else:
            features.append(999999.0)

        # --- Time Features ---
        minutes_since_open = self._minutes_since_open(timestamp)
        features.append(minutes_since_open)

        # --- Contact Order / Reaction ---
        features.append(contact_order)
        features.append(1 if level_type == "solid" else 0)
        features.append(1 if reaction == "rejection" else (2 if reaction == "break" else 0))
        features.append(1 if approach_direction == "from_above" else 0)
        features.append(confluence)

        # --- Color encoding ---
        features.extend(self._encode_color(color))

        return features

    def _minutes_since_open(self, timestamp):
        try:
            hour = int(timestamp.split(":")[0])
            minute = int(timestamp.split(":")[1])
            total = (hour - 9) * 60 + (minute - 30)
            return max(total, 0)
        except:
            return 0

    def _encode_color(self, color):
        # One-hot: [blue, orange, black, teal]
        return [
            1 if color == "blue" else 0,
            1 if color == "orange" else 0,
            1 if color == "black" else 0,
            1 if color == "teal" else 0
        ]
