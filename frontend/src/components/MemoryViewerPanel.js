import React, { useState, useEffect } from "react";
import "./MemoryViewerPanel.css";

const MemoryViewerPanel = () => {
  const [selectedTable, setSelectedTable] = useState("trades_history");
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);

  const tables = [
    "trades_history",
    "patterns_memory",
    "level_contacts",
    "user_feedback",
    "volume_profile",
    "portfolio_ledger",
    "module_diagnostics",
    "false_missed_analysis",
    "pattern_evolution"
  ];

  useEffect(() => {
    fetch(`http://127.0.0.1:5000/view_memory/${selectedTable}`)
      .then((res) => res.json())
      .then((result) => {
        const rows = result.rows || result.data || [];
        if (result.success && rows.length > 0) {
          setData(rows);
          setColumns(Object.keys(rows[0]));
        } else {
          setData([]);
          setColumns([]);
        }
      })
      .catch((error) => {
        console.error("Fetch error:", error);
        setData([]);
        setColumns([]);
      });
  }, [selectedTable]);

  return (
    <div className="memory-viewer-panel">
      <h2 className="section-title">🧠 Q Memory Viewer</h2>
      <div className="selector-container">
        <label>Select Memory Table: </label>
        <select
          value={selectedTable}
          onChange={(e) => setSelectedTable(e.target.value)}
        >
          {tables.map((table) => (
            <option key={table} value={table}>
              {table}
            </option>
          ))}
        </select>
      </div>

      <div className="table-container">
        {data.length > 0 ? (
          <table>
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {columns.map((col) => (
                    <td key={col}>{String(row[col])}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No data available.</p>
        )}
      </div>
    </div>
  );
};

export default MemoryViewerPanel;
