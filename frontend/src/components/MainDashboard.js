// src/components/MainDashboard.js
import React, { useState, useEffect } from "react";
import "../App.css";

import LiveChartPanel      from "./LiveChartPanel";
import TradeLogPanel       from "./TradeLogPanel";
import AlertsPanel         from "./AlertsPanel";
import PatternSummaryPanel from "./PatternSummaryPanel";
import PortfolioPanel      from "./PortfolioPanel";
import VisiblePulsePanel   from "./VisiblePulsePanel";
import DiagnosticPanel     from "./DiagnosticPanel";

export default function MainDashboard() {
  const [view, setView] = useState("dashboard");
  const [livePrice, setLivePrice]           = useState(null);
  const [tradeCount, setTradeCount]         = useState(null);
  const [alertCount, setAlertCount]         = useState(null);
  const [patternCount, setPatternCount]     = useState(null);
  const [portfolioCount, setPortfolioCount] = useState(null);

  // Fetch functions
  const fetchPrice = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/price");
      const { price } = await res.json();
      setLivePrice(parseFloat(price.toFixed(2)));
    } catch {
      setLivePrice("Error");
    }
  };

  const fetchTrades = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get_recommendations");
      const { success, recommendations } = await res.json();
      setTradeCount(success && Array.isArray(recommendations) ? recommendations.length : 0);
    } catch {
      setTradeCount(0);
    }
  };

  const fetchAlerts = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get_alerts");
      const { alerts } = await res.json();
      setAlertCount(Array.isArray(alerts) ? alerts.length : 0);
    } catch {
      setAlertCount(0);
    }
  };

  const fetchPatterns = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/analyze");
      const { patterns } = await res.json();
      setPatternCount(Array.isArray(patterns) ? patterns.length : 0);
    } catch {
      setPatternCount(0);
    }
  };

  const fetchPortfolio = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get_portfolio");
      const { success, open_positions } = await res.json();
      setPortfolioCount(success && Array.isArray(open_positions) ? open_positions.length : 0);
    } catch {
      setPortfolioCount(0);
    }
  };

  // Polling setup
  useEffect(() => {
    fetchPrice();
    fetchTrades();
    fetchAlerts();
    fetchPatterns();
    fetchPortfolio();

    const priceInterval     = setInterval(fetchPrice, 15000);
    const tradesInterval    = setInterval(fetchTrades, 15000);
    const alertsInterval    = setInterval(fetchAlerts, 15000);
    const patternsInterval  = setInterval(fetchPatterns, 15000);
    const portfolioInterval = setInterval(fetchPortfolio, 15000);

    return () => {
      clearInterval(priceInterval);
      clearInterval(tradesInterval);
      clearInterval(alertsInterval);
      clearInterval(patternsInterval);
      clearInterval(portfolioInterval);
    };
  }, []);

  // Decide which panel to render
  const renderView = () => {
    switch (view) {
      case "live":
        return <LiveChartPanel />;
      case "trades":
        return <TradeLogPanel />;
      case "alerts":
        return <AlertsPanel />;
      case "patterns":
        return <PatternSummaryPanel />;
      case "portfolio":
        return <PortfolioPanel />;
      default:
        return (
          <div className="dashboard-grid">
            <div className="dashboard-tile" onClick={() => setView("live")}>
              <span className="tile-icon">📈</span>
              <h3>Live Chart</h3>
              <p>{livePrice   !== null ? `$${livePrice}`           : "Loading..."}</p>
            </div>

            <div className="dashboard-tile" onClick={() => setView("trades")}>
              <span className="tile-icon">📘</span>
              <h3>Trade Log</h3>
              <p>{tradeCount  !== null ? `${tradeCount} Trades`    : "Loading..."}</p>
            </div>

            <div className="dashboard-tile" onClick={() => setView("alerts")}>
              <span className="tile-icon">🔔</span>
              <h3>Alerts</h3>
              <p>{alertCount  !== null ? `${alertCount} Alerts`    : "Loading..."}</p>
            </div>

            <div className="dashboard-tile" onClick={() => setView("patterns")}>
              <span className="tile-icon">🧠</span>
              <h3>Patterns</h3>
              <p>{patternCount!== null ? `${patternCount} Patterns` : "Loading..."}</p>
            </div>

            <div className="dashboard-tile" onClick={() => setView("portfolio")}>
              <span className="tile-icon">💼</span>
              <h3>Portfolio</h3>
              <p>{portfolioCount !== null ? `${portfolioCount} Open` : "Loading..."}</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="main-dashboard">
      {view !== "dashboard" && (
        <button className="back-button" onClick={() => setView("dashboard")}>
          ⬅ Back to Dashboard
        </button>
      )}
      {renderView()}
      {/* Always visible bottom panels */}
      <DiagnosticPanel />
      <VisiblePulsePanel />
    </div>
  );
}
