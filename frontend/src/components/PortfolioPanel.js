import React, { useEffect, useState } from "react";
import "./PortfolioPanel.css";

const PortfolioPanel = () => {
  const [portfolio, setPortfolio] = useState({
    balance: 10000,
    open_positions: [],
    closed_positions: [],
  });

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/get_portfolio");
        const data = await response.json();
        setPortfolio(data);
      } catch (error) {
        console.error("Error fetching portfolio:", error);
      }
    };

    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="portfolio-panel">
      <h2>QMMX Portfolio</h2>
      <div className="portfolio-balance">
        <strong>Balance:</strong> ${portfolio.balance.toFixed(2)}
      </div>

      <div className="portfolio-section">
        <h3>Open Positions</h3>
        {portfolio.open_positions.length === 0 ? (
          <p>No open trades.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Direction</th>
                <th>Entry Price</th>
                <th>Entry Time</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.open_positions.map((trade, index) => (
                <tr key={index}>
                  <td>{trade.symbol}</td>
                  <td>{trade.direction.toUpperCase()}</td>
                  <td>{trade.entry_price.toFixed(2)}</td>
                  <td>{new Date(trade.entry_time).toLocaleTimeString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="portfolio-section">
        <h3>Closed Positions</h3>
        {portfolio.closed_positions.length === 0 ? (
          <p>No closed trades.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Direction</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>PNL</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.closed_positions.map((trade, index) => (
                <tr key={index}>
                  <td>{trade.symbol}</td>
                  <td>{trade.direction.toUpperCase()}</td>
                  <td>{trade.entry_price.toFixed(2)}</td>
                  <td>{trade.exit_price.toFixed(2)}</td>
                  <td
                    className={
                      trade.pnl > 0 ? "profit" : trade.pnl < 0 ? "loss" : ""
                    }
                  >
                    {trade.pnl.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default PortfolioPanel;
