import React, { useState } from "react";
import TextLevelEntry from "./components/TextLevelEntry";
import PatternReview from "./components/PatternReview";
import SettingsPanel from './components/SettingsPanel';
import MainDashboard from "./components/MainDashboard";
import RecommendationPanel from "./components/RecommendationPanel";
import QBrandHeader from "./components/QBrandHeader";
import MemoryViewerPanel from "./components/MemoryViewerPanel";
import "./App.css";

function App() {
  const [selectedTab, setSelectedTab] = useState("dashboard");

  const [levels, setLevels] = useState({
    blue: { solid: Array(4).fill(""), dashed: Array(5).fill("") },
    orange: { solid: Array(4).fill(""), dashed: Array(5).fill("") },
    black: { solid: Array(4).fill(""), dashed: Array(5).fill("") },
    teal: { solid: Array(3).fill(""), dashed: [] },
  });

  const [sessionStarted, setSessionStarted] = useState(false);

  const renderTab = () => {
    switch (selectedTab) {
      case "levels":
        return (
          <TextLevelEntry
            levels={levels}
            setLevels={setLevels}
            sessionStarted={sessionStarted}
          />
        );
      case "patterns":
        return <PatternReview />;
      case "settings":
        return <SettingsPanel />;
      case "recommendations":
        return <RecommendationPanel />;
      case "memory":
        return <MemoryViewerPanel />;
      default:
        return <MainDashboard />;
    }
  };

  return (
    <div className="app-container">
      <QBrandHeader />
      <nav>
        <button className={selectedTab === "levels" ? "active-tab" : ""} onClick={() => setSelectedTab("levels")}>
          Text Level Entry
        </button>
        <button className={selectedTab === "patterns" ? "active-tab" : ""} onClick={() => setSelectedTab("patterns")}>
          Pattern Review
        </button>
        <button className={selectedTab === "settings" ? "active-tab" : ""} onClick={() => setSelectedTab("settings")}>
          Settings
        </button>
        <button className={selectedTab === "dashboard" ? "active-tab" : ""} onClick={() => setSelectedTab("dashboard")}>
          Main Dashboard
        </button>
        <button className={selectedTab === "recommendations" ? "active-tab" : ""} onClick={() => setSelectedTab("recommendations")}>
          Trade Recommendations
        </button>
        <button className={selectedTab === "memory" ? "active-tab" : ""} onClick={() => setSelectedTab("memory")}>
          Q Memory Viewer
        </button>
      </nav>
      {renderTab()}
    </div>
  );
}

export default App;
