import React, { useEffect, useState } from 'react';
import './PatternReview.css';

const API_BASE = 'http://127.0.0.1:5000';

const PatternReview = () => {
  const [pattern, setPattern] = useState(null);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState('');

  const fetchPattern = async () => {
    try {
      const res = await fetch(`${API_BASE}/get_current_pattern`);
      const data = await res.json();
      if (data.success) {
        setPattern(data.pattern);
        setFeedback('');
      } else {
        setPattern(null);
        setFeedback('No pattern available.');
      }
    } catch (err) {
      console.error('Error fetching pattern:', err);
      setPattern(null);
      setFeedback('Failed to fetch pattern.');
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (decision) => {
    if (!pattern || !pattern.id) return;
    try {
      const res = await fetch(`${API_BASE}/mark_pattern_decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern_id: pattern.id, decision }),
      });
      const result = await res.json();
      if (result.success) {
        setFeedback(`Pattern ${decision.toUpperCase()}ED`);
        fetchPattern();
      } else {
        setFeedback('Failed to record decision.');
      }
    } catch (err) {
      console.error('Error submitting decision:', err);
      setFeedback('Server error submitting decision.');
    }
  };

  useEffect(() => {
    fetchPattern();
  }, []);

  if (loading) return <div className="loading">Loading pattern...</div>;

  return (
    <div className="pattern-review-panel">
      <h2>Pattern Review</h2>
      {pattern ? (
        <div className="pattern-details">
          <p><strong>ID:</strong> {pattern.id}</p>
          <p><strong>Setup:</strong> {pattern.setup}</p>
          <p><strong>Confidence:</strong> {pattern.confidence}%</p>
          <p><strong>Recommended Action:</strong> {pattern.recommendation}</p>

          <div className="stress-test-summary">
            <p><strong>Stress Test Summary:</strong> {pattern.stress_summary || 'N/A'}</p>
            <div className="robustness-bar">
              <div className="bar-fill" style={{ width: `${pattern.robustness || 0}%` }} />
              <span className="score-label">Robustness: {pattern.robustness || 0}%</span>
            </div>
          </div>

          <div className="sensitivity">
            <p><strong>Notable Weak Points:</strong></p>
            <ul>
              {(pattern.weaknesses || []).map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>

          <div className="simulation-notes">
            <p><strong>Simulation Notes:</strong></p>
            <p>{pattern.sim_notes || 'No notes available.'}</p>
          </div>

          <div className="review-buttons">
            <button onClick={() => handleDecision('approve')}>✅ Approve</button>
            <button onClick={() => handleDecision('reject')}>❌ Reject</button>
            <button onClick={() => handleDecision('review_further')}>⚠️ Review Further</button>
          </div>
        </div>
      ) : (
        <p className="no-pattern">{feedback}</p>
      )}
      {feedback && pattern && <p className="review-status">{feedback}</p>}
    </div>
  );
};

export default PatternReview;
