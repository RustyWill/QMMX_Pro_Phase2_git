import joblib
import numpy as np

class PatternRecognizer:
    def __init__(self, model_path="models/qmmx_model_v1.joblib"):
        try:
            self.model = joblib.load(model_path)
        except Exception as e:
            print("Error loading ML model:", e)
            self.model = None

    def recognize(self, feature_vector):
        """
        Takes a feature vector from FeatureEngineer and scores it.
        Returns confidence and decision label.
        """
        if self.model is None:
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
        except:
            confidence = 0.0
            label = "review"

        return {
            "confidence": round(confidence, 3),
            "label": label  # 'approve', 'review', or 'reject'
        }
