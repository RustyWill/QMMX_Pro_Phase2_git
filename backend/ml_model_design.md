# QMMX Pro – ML Model Design (Phase 1)

## 🧠 Model Type:
RandomForestClassifier (sklearn)

- n_estimators: 150
- max_depth: 6
- random_state: 42
- Purpose: Balance accuracy, speed, and interpretability for live pattern scoring

---

## 🎯 Prediction Goal:
Classify pattern setup into one of:

- `approve` – recommend as tradeable
- `review` – continue observing, needs more data
- `reject` – not actionable, pattern is weak

---

## 📊 Input Features:

Each detected pattern generates a vector of these inputs:

| Feature Name            | Description |
|-------------------------|-------------|
| `price_proximity_blue`  | Distance to nearest blue line |
| `price_proximity_orange`| Distance to nearest orange line |
| `price_proximity_black` | Distance to nearest black line |
| `price_proximity_teal`  | Distance to nearest teal line |
| `touch_order`           | 1st touch, 2nd touch, etc |
| `approach_angle`        | Derived direction of approach (up/down, sharp/soft) |
| `reaction_strength`     | % reaction at level (e.g., wick length, bounce size) |
| `reaction_type`         | rejection, hesitation, or break |
| `volume_context`        | spike, average, or low |
| `time_of_day`           | Encoded hour block (e.g. 9-10AM = 1) |
| `level_type`            | solid or dashed |
| `confluence_zone`       | Binary – is this level near another color group? |
| `recent_success_rate`   | Win rate of this level in recent log |
| `volatility_rank`       | Rolling ATR percentile (1–100) |
| `was_recently_flagged`  | Pattern seen recently? (boolean)

---

## 🧪 Training Dataset Format:
The training CSV should include:

- 1 row per pattern detection
- All features above as columns
- A final column called `label` with values:
  - `approve`, `review`, or `reject`

---

## 💾 Output:
Model saved as:
