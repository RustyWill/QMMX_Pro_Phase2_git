import React from 'react';
import './PatternMemory.css';

function PatternMemory() {
  return (
    <div className="pattern-memory-container">
      <h2 className="pattern-memory-title">🧠 Pattern Memory</h2>
      <p className="pattern-memory-description">
        This panel displays the patterns QMMX has learned, reviewed, or is tracking for future evaluation.
      </p>

      <div className="pattern-list">
        <div className="pattern-card">
          <h3>Double Top</h3>
          <p>Status: Approved</p>
        </div>
        <div className="pattern-card">
          <h3>V-W Reversal</h3>
          <p>Status: Review Further</p>
        </div>
        <div className="pattern-card">
          <h3>Triangle Coil</h3>
          <p>Status: Rejected</p>
        </div>
      </div>
    </div>
  );
}

export default PatternMemory;
