# confidence_adjuster.py

from collections import defaultdict

# Pattern outcome history
pattern_outcomes = defaultdict(lambda: {"wins": 0, "losses": 0})

def record_pattern_outcome(pattern_signature, was_successful):
    """
    Logs whether a pattern setup resulted in a successful trade.
    """
    key = _pattern_key(pattern_signature)
    if was_successful:
        pattern_outcomes[key]["wins"] += 1
    else:
        pattern_outcomes[key]["losses"] += 1

def get_confidence_score(pattern_signature):
    """
    Returns a confidence score between 0.0 and 1.0 for the given pattern.
    """
    key = _pattern_key(pattern_signature)
    history = pattern_outcomes[key]
    total = history["wins"] + history["losses"]
    if total == 0:
        return 0.5  # Neutral confidence if no history yet
    return history["wins"] / total

def _pattern_key(signature):
    """
    Converts a pattern signature dictionary into a hashable string key.
    """
    return f"{signature.get('level_type')}|{signature.get('reaction_type')}|{signature.get('approach_direction')}|{signature.get('macro_position')}"
