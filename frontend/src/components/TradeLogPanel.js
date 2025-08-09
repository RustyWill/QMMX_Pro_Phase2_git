import React, { useEffect, useState } from "react";

export default function TradeLogPanel() {
  const [log, setLog] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/get_recommendations")
      .then((res) => res.json())
      .then((data) => setLog(data.recommendations || []))
      .catch(() => setLog([]));
  }, []);

  return (
    <div>
      <h2>📘 Trade Log</h2>
      {log.length === 0 ? (
        <p>No trades available.</p>
      ) : (
        <ul>
          {log.map((rec, idx) => (
            <li key={idx}>
              {rec.timestamp}: {rec.contract} — {rec.direction} @ {rec.price}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
