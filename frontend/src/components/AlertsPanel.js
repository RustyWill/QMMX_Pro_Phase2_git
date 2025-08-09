import React, { useState, useEffect } from "react";

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState([]);

  const fetchAlerts = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get_alerts");
      const data = await res.json();
      setAlerts(data.alerts || []);
    } catch {
      setAlerts(["⚠ Error loading alerts."]);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>🔔 Alerts</h2>
      <ul>
        {alerts.map((a, idx) => (
          <li key={idx}>{a}</li>
        ))}
      </ul>
    </div>
  );
}

