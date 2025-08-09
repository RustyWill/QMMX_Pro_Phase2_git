import React from "react";

function AnalysisPanel({ levels, context, priceData }) {
  return (
    <div className="analysis-panel">
      <h2>Analysis Panel</h2>
      <div className="context-box">
        <p><strong>Session Started:</strong> {context.sessionStarted ? "Yes" : "No"}</p>
      </div>

      <div className="price-data">
        <h3>Recent Price Data</h3>
        <ul>
          {priceData.map((point, index) => (
            <li key={index}>
              Time: {point.time}, Price: ${point.price.toFixed(2)}
            </li>
          ))}
        </ul>
      </div>

      <div className="level-summary">
        <h3>Entered Levels</h3>
        {Object.keys(levels).map((color) => (
          <div key={color} className="level-group">
            <strong>{color.toUpperCase()}</strong>
            <div>Solid: {levels[color].solid.join(", ")}</div>
            {levels[color].dashed.length > 0 && (
              <div>Dashed: {levels[color].dashed.join(", ")}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AnalysisPanel;
