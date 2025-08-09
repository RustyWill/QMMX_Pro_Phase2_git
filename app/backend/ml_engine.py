import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


class MLDecisionEngine:
    def __init__(self, model_path='models/qmmx_model_v1.joblib'):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"✅ Loaded ML model from {self.model_path}")
            except Exception as e:
                print(f"⚠️ Error loading ML model: {e}")
        else:
            print("⚠️ No pre-trained ML model found. Run training first.")

    def train(self, training_csv):
        try:
            df = pd.read_csv(training_csv)
            if 'label' not in df.columns:
                raise ValueError("Missing 'label' column in training data.")

            X = df.drop('label', axis=1)
            y = df['label']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)

            print("✅ Model training complete.")
            print("📊 Classification Report:")
            print(classification_report(y_test, y_pred))

            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            print(f"💾 Model saved to {self.model_path}")

        except Exception as e:
            print(f"❌ Failed to train model: {e}")

    def predict(self, input_data: dict) -> int:
        if not self.model:
            raise Exception("No trained model available. Please train first.")

        df = pd.DataFrame([input_data])
        prediction = self.model.predict(df)[0]
        return int(prediction)


# Optional: Run training manually
if __name__ == "__main__":
    engine = MLDecisionEngine()
    engine.train("training_data.csv")
