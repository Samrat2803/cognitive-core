import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { LiveMonitorDashboard } from '../components/dashboard/LiveMonitorDashboard';
import './HomePage.css';

export function HomePage() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      // Navigate to chat with query as state
      navigate('/chat', { state: { initialQuery: query.trim() } });
    }
  };

  return (
    <div className="home-page">
      <Header />
      
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Cognitive Core</h1>
          <p className="hero-subtitle">
            AI-powered intelligence platform for political analysis and real-time insights
          </p>
          
          {/* Search Box */}
          <form className="hero-search" onSubmit={handleSubmit}>
            <input
              type="text"
              className="hero-search-input"
              placeholder="Ask me about political events, trends, policies..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button type="submit" className="hero-search-button">
              Analyze →
            </button>
          </form>
        </div>
      </div>

      {/* Live Monitor Dashboard - Expanded */}
      <div className="home-monitor-section-expanded">
        <LiveMonitorDashboard />
      </div>
    </div>
  );
}

