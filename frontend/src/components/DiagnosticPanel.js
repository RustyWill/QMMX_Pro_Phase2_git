import React, { useEffect, useState } from 'react';
import './DiagnosticPanel.css';

const DiagnosticPanel = () => {
  const [diagnostics, setDiagnostics] = useState({});

  const fetchDiagnostics = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/module_status"); // ✅ updated route
      const data = await res.json();
      if (data.success) {
        setDiagnostics(data.status);
        const failures = Object.entries(data.status).filter(([_, v]) => !v.active);
        if (failures.length > 0) {
          const firstFail = failures[0];
          showLiveAlert(`${firstFail[0]}: ${firstFail[1].error || 'Not active'}`);
        }
      }
    } catch (err) {
      console.error("Failed to fetch diagnostics:", err);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
    const interval = setInterval(fetchDiagnostics, 10000); // poll every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="diagnostic-panel">
      <h3>Q Diagnostic Panel</h3>
      <div className="module-grid">
        {Object.entries(diagnostics).map(([name, status]) => (
          <div key={name} className={`module-box ${status.active ? 'green' : 'red'}`}>
            <strong>{name.replace(/_/g, ' ')}</strong>
            <div className="module-status">
              {status.active ? "🟢 Active" : "🔴 Inactive"}
            </div>
            <div className="module-details">
              <div>Last Ping: {status.last_ping || "—"}</div>
              {status.error && <div className="error-msg">⚠ {status.error}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

function showLiveAlert(message) {
  const id = "q-diagnostic-alert";
  const existing = document.getElementById(id);
  if (existing) existing.remove();

  const el = document.createElement("div");
  el.id = id;
  el.innerText = "⚠ " + message;
  el.style.position = "fixed";
  el.style.top = "10px";
  el.style.left = "50%";
  el.style.transform = "translateX(-50%)";
  el.style.padding = "12px 24px";
  el.style.backgroundColor = "#e74c3c";
  el.style.color = "white";
  el.style.zIndex = 9999;
  el.style.borderRadius = "6px";
  el.style.fontWeight = "bold";
  el.style.boxShadow = "0 0 10px rgba(0,0,0,0.5)";
  el.style.cursor = "pointer";

  el.onclick = () => el.remove();

  document.body.appendChild(el);
  setTimeout(() => el.remove(), 10000);
}

export default DiagnosticPanel;
