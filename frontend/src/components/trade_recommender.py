# trade_recommender.py

def recommend_trade(pattern):
    if pattern.get("confidence", 0) < 0.7:
        return None

    price = pattern.get("structure", {}).get("entry_price", 0)
    timestamp = pattern.get("timestamp", "")
    direction = pattern.get("structure", {}).get("direction", "up")

    return {
        "symbol": pattern["symbol"],
        "direction": direction,
        "entry_price": price,
        "strike": round(price),
        "type": "call" if direction == "up" else "put",
        "timestamp": timestamp,
        "pattern_id": pattern.get("pattern_name", "unknown")
    }
