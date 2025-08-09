import joblib
import numpy as np
from diagnostic_monitor import diagnostic_monitor  # ✅ Added

class PatternRecognizer:
    def __init__(self, model_path="models/qmmx_model_v1.joblib"):
        try:
            self.model = joblib.load(model_path)
            diagnostic_monitor.ping("pattern_recognizer")  # ✅ Successful model load
        except Exception as e:
            print("Error loading ML model:", e)
            self.model = None
            diagnostic_monitor.report_error("pattern_recognizer", f"Model load failed: {e}")  # ✅ Error report

    def recognize(self, feature_vector):
        """
        Takes a feature vector from FeatureEngineer and scores it.
        Returns confidence and decision label.
        """
        if self.model is None:
            diagnostic_monitor.report_error("pattern_recognizer", "No ML model available")
            return {
                "confidence": 0.0,
                "label": "review"
            }

        X = np.array([feature_vector])
        try:
            proba = self.model.predict_proba(X)[0]
            confidence = max(proba)
            label_index = np.argmax(proba)
            label = self.model.classes_[label_index]
            diagnostic_monitor.ping("pattern_recognizer")  # ✅ Successful prediction
        except Exception as e:
            confidence = 0.0
            label = "review"
            diagnostic_monitor.report_error("pattern_recognizer", f"Prediction failed: {e}")  # ✅ Error report

        return {
            "confidence": round(confidence, 3),
            "label": label  # 'approve', 'review', or 'reject'
        }
