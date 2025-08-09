from memory_recall_engine import (
    recall_pattern_memory,
    recall_trade_memory,
    recall_recent_feedback
)

def adjust_confidence_with_memory(pattern_id, base_score, ticker):
    """
    Adjusts the confidence score of a pattern using historical memory:
    - pattern success rate
    - average confidence
    - user feedback
    - trade outcome stats
    """
    memory = recall_pattern_memory(pattern_id)
    trades = recall_trade_memory(ticker=ticker, pattern_id=pattern_id)
    feedback = recall_recent_feedback()

    # Start from the base confidence score from model
    score = base_score

    # Boost or penalize based on pattern memory
    if memory:
        times_seen = memory[2]  # memory['times_seen']
        times_successful = memory[3]  # memory['times_successful']
        avg_conf = memory[4] or 0

        if times_seen >= 5:
            win_rate = times_successful / times_seen
            score += (win_rate - 0.5) * 0.4  # emphasis on actual outcomes
            score += (avg_conf - 0.5) * 0.2  # memory-based average score

    # Penalize if recently rejected
    negative_feedback = [f for f in feedback if f[2] == pattern_id and f[3] == "Reject"]
    review_feedback = [f for f in feedback if f[2] == pattern_id and f[3] == "Review Further"]
    score -= 0.1 * len(negative_feedback)
    score -= 0.05 * len(review_feedback)

    # Clamp between 0 and 1
    return max(0.0, min(1.0, score))
