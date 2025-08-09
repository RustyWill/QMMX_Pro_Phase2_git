from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

from ml_engine import MLDecisionEngine
from polygon_io_provider import PolygonDataProvider
from qmms_strategies import generate_strategies
from qmms_feature_engineer import FeatureEngineer
from qmms_pattern_discovery import PatternDiscovery
from qmms_pattern_recognizer import PatternRecognizer

app = Flask(__name__)
CORS(app)

# Setup placeholder context and level inputs
context = {}
levels_by_color = {
    "blue": {"solid": [], "dashed": []},
    "orange": {"solid": [], "dashed": []},
    "black": {"solid": [], "dashed": []},
    "teal": {"solid": []}
}

# Runtime settings (in-memory for Phase 1)
runtime_settings = {
    "polygon_api_key": None,
    "alert_phone_numbers": []
}

# Initialize components
feature_engineer = FeatureEngineer(context=context)
pattern_discovery = PatternDiscovery(levels_by_color=levels_by_color)
pattern_recognizer = PatternRecognizer()
strategies = generate_strategies()
ml_engine = MLDecisionEngine()
data_provider = PolygonDataProvider(api_key=runtime_settings["polygon_api_key"])

@app.route("/")
def index():
    return "QMMX Pro backend is running"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        json_data = request.get_json()

        # Extract incoming levels
        levels = json_data.get("levels_by_color", {})
        price_data = json_data.get("price_data", [])
        context.update(json_data.get("context", {}))

        # Update levels
        pattern_discovery.levels_by_color = levels

        # Feature engineering
        features = feature_engineer.extract_features(price_data, levels)

        # Pattern recognition
        recognized_patterns = pattern_recognizer.recognize(features)

        # Strategy application
        strategy_output = strategies.apply(recognized_patterns)

        # ML scoring
        ml_decision = ml_engine.score(strategy_output)

        return jsonify({
            "patterns": recognized_patterns,
            "strategy_output": strategy_output,
            "ml_decision": ml_decision
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/settings", methods=["POST"])
def update_settings():
    try:
        json_data = request.get_json()
        api_key = json_data.get("polygon_api_key")
        phones = json_data.get("alert_phone_numbers")

        if api_key:
            runtime_settings["polygon_api_key"] = api_key
            data_provider.api_key = api_key  # Apply it live

        if isinstance(phones, list):
            runtime_settings["alert_phone_numbers"] = phones

        return jsonify({"status": "Settings updated successfully"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
