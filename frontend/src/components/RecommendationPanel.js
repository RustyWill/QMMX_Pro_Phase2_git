import React, { useEffect, useState } from 'react';
import './RecommendationPanel.css';

const RecommendationPanel = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchRecommendations = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/get_recommendations")
      const data = await response.json();
      if (data.success && Array.isArray(data.recommendations)) {
        setRecommendations(data.recommendations);
        setLastUpdated(new Date().toLocaleTimeString());
      } else {
        console.warn('No recommendations received.');
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  useEffect(() => {
    fetchRecommendations();
    const interval = setInterval(fetchRecommendations, 30000); // Refresh every 30 sec
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="recommendation-panel">
      <h3>📡 Real-Time Recommendations</h3>
      <p className="last-updated">Last updated: {lastUpdated || 'loading...'}</p>

      {recommendations.length === 0 ? (
        <div className="no-recommendations">No live signals yet.</div>
      ) : (
        <table className="recommendation-table">
          <thead>
            <tr>
              <th>Pattern</th>
              <th>Confidence</th>
              <th>Price</th>
              <th>Option</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((rec, index) => (
              <tr key={index}>
                <td>{rec.pattern}</td>
                <td>{(rec.confidence * 100).toFixed(1)}%</td>
                <td>{rec.price}</td>
                <td>{rec.option || '—'}</td>
                <td>{rec.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default RecommendationPanel;
