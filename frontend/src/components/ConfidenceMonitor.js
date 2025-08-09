import React from 'react';
import './ConfidenceMonitor.css';

function ConfidenceMonitor() {
  return (
    <div className="confidence-monitor-container">
      <h2 className="confidence-monitor-title">📊 Confidence Monitor</h2>
      <p className="confidence-monitor-description">
        This panel displays current confidence levels for active patterns, setups, and trade signals.
      </p>

      <div className="confidence-grid">
        <div className="confidence-box">
          <h3>SPY – Reversal Setup</h3>
          <p>Confidence: <span className="high">89%</span></p>
        </div>
        <div className="confidence-box">
          <h3>SPX – Breakout Pattern</h3>
          <p>Confidence: <span className="medium">67%</span></p>
        </div>
        <div className="confidence-box">
          <h3>TSLA – Range Compression</h3>
          <p>Confidence: <span className="low">41%</span></p>
        </div>
      </div>
    </div>
  );
}

export default ConfidenceMonitor;
