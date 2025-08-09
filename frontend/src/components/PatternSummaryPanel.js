import React, { useEffect, useState } from "react";

export default function PatternSummaryPanel() {
  const [patterns, setPatterns] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/analyze")
      .then((res) => res.json())
      .then((data) => setPatterns(data.patterns || []))
      .catch(() => setPatterns([]));
  }, []);

  return (
    <div>
      <h2>🧠 Pattern Summary</h2>
      {patterns.length === 0 ? (
        <p>No patterns detected.</p>
      ) : (
        <ul>
          {patterns.map((p, idx) => (
            <li key={idx}>
              {p.name} — Confidence: {p.confidence}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
