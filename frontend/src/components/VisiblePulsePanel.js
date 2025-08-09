import React, { useEffect, useState } from "react";
import "./VisiblePulsePanel.css";

const moduleDisplayNames = {
  "ml_engine": "ML Engine",
  "trade_recommender": "Trade Recommender",
  "exit_strategy": "Exit Strategy",
  "diagnostic_monitor": "Diagnostic Monitor",
  "pattern_memory_engine": "Pattern Memory",
  "portfolio_tracker": "Portfolio",
  "pattern_discovery": "Pattern Discovery",
  "confidence_monitor": "Confidence Monitor",
  "contact_event_evaluator": "Contact Evaluator",
  "alerts": "Alerts Engine",
  "price_feed": "Price Feed",
  "settings_store": "Settings Manager"
};

function VisiblePulsePanel() {
  const [statuses, setStatuses] = useState({});

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch("http://localhost:5000/module_status");
        const data = await res.json();
        if (data.success && data.status) {
          setStatuses(data.status);
        }
      } catch (err) {
        console.error("Failed to fetch module status:", err);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="visible-pulse-panel">
      <h3>🧠 Visible Pulse Monitor</h3>
      <div className="pulse-grid">
        {Object.entries(moduleDisplayNames).map(([key, label]) => {
          const info  = statuses[key] || {};
          const state = info.status?.toLowerCase()       // if you return { status: "GREEN", ... }
                      ?? (info.active ? "green" : "red"); // or fall back on .active
          const color = state === "green"
            ? "#00cc66"
            : state === "yellow"
            ? "#ffcc00"
            : "#ff3333";

          return (
            <div className="pulse-card" key={key} style={{ borderColor: color }}>
              <div className="pulse-label">{label}</div>
              <div className="pulse-status" style={{ backgroundColor: color }}></div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default VisiblePulsePanel;
