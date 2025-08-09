import React, { useState } from 'react';
import '../App.css';

function SettingsPanel() {
  const [apiKey, setApiKey] = useState('');
  const [phoneNumbers, setPhoneNumbers] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:5000/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          polygon_api_key: apiKey,
          alert_phone_numbers: phoneNumbers
            .split(',')
            .map((n) => n.trim())
            .filter((n) => n.length > 0),
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStatusMessage("✅ Settings saved successfully.");
      } else {
        setStatusMessage(`❌ Error: ${data.error || "Saving settings failed."}`);
      }
    } catch (error) {
      console.error("Settings submission error:", error);
      setStatusMessage("❌ Error submitting settings.");
    }
  };

  return (
    <div className="app-container">
      <h2>Settings</h2>
      <form onSubmit={handleSubmit}>
        <label><strong>Polygon.io API Key:</strong></label>
        <input
          type="text"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="Enter your API key"
        />

        <label><strong>Alert Phone Numbers (comma separated):</strong></label>
        <input
          type="text"
          value={phoneNumbers}
          onChange={(e) => setPhoneNumbers(e.target.value)}
          placeholder="e.g. 1234567890,0987654321"
        />

        <button type="submit">Save Settings</button>
      </form>

      {statusMessage && (
        <p style={{ color: statusMessage.startsWith("✅") ? "limegreen" : "red" }}>
          {statusMessage}
        </p>
      )}
    </div>
  );
}

export default SettingsPanel;
