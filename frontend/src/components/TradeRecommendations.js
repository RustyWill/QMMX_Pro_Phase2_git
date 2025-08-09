import React from 'react';
import '../App.css';

function TradeRecommendations({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return <div className="panel"><h2>Trade Recommendations</h2><p>No trades yet.</p></div>;
  }

  return (
    <div className="panel">
      <h2>Trade Recommendations</h2>
      <div className="recommendation-list">
        {recommendations.map((rec, index) => (
          <div className="recommendation-card" key={index}>
            <p><strong>Symbol:</strong> {rec.symbol}</p>
            <p><strong>Setup:</strong> {rec.setup}</p>
            <p><strong>Confidence:</strong> {rec.confidence}%</p>
            <p><strong>Price:</strong> ${rec.price}</p>
            <p><strong>Option:</strong> {rec.option}</p>
            <p><strong>Timestamp:</strong> {rec.timestamp}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TradeRecommendations;
