// frontend/src/components/LiveChartPanel.js
import React, { useEffect, useRef, useState } from "react";
import Plotly from "plotly.js-dist-min";

const LEVEL_COLORS = {
  blue:   "#1e90ff",
  orange: "#f59e0b",
  black:  "#888888", // softer black so it shows on dark bg
  teal:   "#14b8a6",
};

const LiveChartPanel = () => {
  const chartRef = useRef(null);
  const [chartData, setChartData] = useState(null);
  const [levelShapes, setLevelShapes] = useState([]);

  async function fetchCandlePayload() {
    const res = await fetch("http://127.0.0.1:5000/candlestick_chart_data");
    const payload = await res.json();
    console.log("📦 Candles payload:", payload);
    if (!payload || !payload.data) throw new Error("Bad candles payload");
    return payload;
  }

  async function fetchLevels() {
    const res = await fetch("http://127.0.0.1:5000/get_levels");
    const levels = await res.json();
    console.log("🎯 Levels:", levels);
    return levels; // { blue:{solid:[], dashed:[]}, orange:{...}, ... }
  }

  function buildLevelShapes(levels) {
    // Build Plotly "shapes" that span the full chart width at each price.
    // We use xref:'paper' so lines extend across the entire visible x-range.
    const shapes = [];
    const add = (price, color, dash) =>
      shapes.push({
        type: "line",
        xref: "paper",
        x0: 0,
        x1: 1,
        yref: "y",
        y0: price,
        y1: price,
        line: { color, width: 1, dash },
        opacity: 0.9,
      });

    const colors = ["blue", "orange", "black", "teal"];
    for (const col of colors) {
      const group = levels[col];
      if (!group) continue;
      (group.solid || []).forEach(p => add(p, LEVEL_COLORS[col], "solid"));
      (group.dashed || []).forEach(p => add(p, LEVEL_COLORS[col], "dash"));
    }
    return shapes;
  }

  const refresh = async () => {
    try {
      const [payload, levels] = await Promise.all([
        fetchCandlePayload(),
        fetchLevels(),
      ]);

      setChartData(payload);
      setLevelShapes(buildLevelShapes(levels));
    } catch (err) {
      console.error("❌ Refresh error:", err);
    }
  };

  useEffect(() => {
    refresh(); // initial
    const id = setInterval(refresh, 3000); // every 3s
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!chartData || !chartRef.current) return;

    const baseLayout = {
      ...chartData.layout,
      paper_bgcolor: "#000",
      plot_bgcolor: "#000",
      font: { color: "#fff" },
      xaxis: {
        ...(chartData.layout?.xaxis || {}),
        color: "#fff",
        rangeslider: { visible: false },
      },
      yaxis: {
        ...(chartData.layout?.yaxis || {}),
        color: "#fff",
        autorange: true,
      },
      // ⬇️ our overlay lines
      shapes: levelShapes,
      margin: { l: 50, r: 20, t: 30, b: 40 },
    };

    Plotly.react(chartRef.current, chartData.data, baseLayout, { responsive: true });
  }, [chartData, levelShapes]);

  return (
    <div style={{ padding: 10, background: "black" }}>
      <h2 style={{ color: "white", textAlign: "center" }}>🕒 Live SPY Candlestick Chart</h2>
      <div
        ref={chartRef}
        style={{ width: "100%", height: 520, backgroundColor: "#111", borderRadius: 12 }}
      />
    </div>
  );
};

export default LiveChartPanel;
