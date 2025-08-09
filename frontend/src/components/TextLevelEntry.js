import React, { useState } from "react";
import "../App.css";

const levelTypes = [
  { color: "BLUE", solid: 4, dashed: 5 },
  { color: "ORANGE", solid: 4, dashed: 5 },
  { color: "BLACK", solid: 4, dashed: 5 },
  { color: "TEAL", solid: 3, dashed: 0 },
];

export default function TextLevelEntry() {
  const initialLevels = {};
  levelTypes.forEach(({ color, solid, dashed }) => {
    initialLevels[color] = {
      solid: Array(solid).fill(""),
      dashed: Array(dashed).fill(""),
    };
  });

  const [levels, setLevels] = useState(initialLevels);
  const [statusMessage, setStatusMessage] = useState("");

  const handleChange = (color, type, index, value) => {
    const updated = { ...levels };
    updated[color][type][index] = value;
    setLevels(updated);
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/submit_levels", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ levels_by_color: levels }),
      });

      const data = await response.json();
      if (data.success) {
        setStatusMessage("✅ Levels saved successfully.");
      } else {
        setStatusMessage(`❌ Error: ${data.error || "Save failed."}`);
      }
    } catch (error) {
      console.error("Submit error:", error);
      setStatusMessage("❌ Network error.");
    }
  };

  return (
    <div className="text-level-container vertical">
      <h2 className="entry-header">Text Level Entry</h2>

      <div className="vertical-grid">
        {levelTypes.map(({ color, solid, dashed }) => (
          <div key={color} className="color-column">
            <h3>{color} Levels</h3>

            {solid > 0 && (
              <div className="column-group">
                <label>Solid Lines:</label>
                {levels[color].solid.map((val, idx) => (
                  <input
                    key={`solid-${color}-${idx}`}
                    value={val}
                    onChange={(e) =>
                      handleChange(color, "solid", idx, e.target.value)
                    }
                    className="level-input"
                    placeholder={`S${idx + 1}`}
                  />
                ))}
              </div>
            )}

            {dashed > 0 && (
              <div className="column-group">
                <label>Dashed Lines:</label>
                {levels[color].dashed.map((val, idx) => (
                  <input
                    key={`dashed-${color}-${idx}`}
                    value={val}
                    onChange={(e) =>
                      handleChange(color, "dashed", idx, e.target.value)
                    }
                    className="level-input"
                    placeholder={`D${idx + 1}`}
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="footer-controls">
        <button className="save-button" onClick={handleSubmit}>
          Save Levels
        </button>
        {statusMessage && <div className="status-message">{statusMessage}</div>}
      </div>
    </div>
  );
}
