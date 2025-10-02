import React, { useState, useEffect } from 'react';
import { TopicCarousel } from './TopicCarousel';
import { config } from '../../config';
import './LiveMonitorDashboard.css';

interface Topic {
  rank: number;
  topic: string;
  explosiveness_score: number;
  classification: string;
  frequency: number;
  image_url?: string;
  entities?: any;
  reasoning: string;
}

interface CacheInfo {
  source: string;
  cachedAt: string;
  expiresInMinutes: number;
}

export function LiveMonitorDashboard() {
  // State
  const [keywords, setKeywords] = useState('US, Hamas, Israel');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);
  const [cacheHours, setCacheHours] = useState(3);
  const [autoFetched, setAutoFetched] = useState(false);

  // API call
  const handleRefresh = async () => {
    setLoading(true);
    setError(null);

    try {
      const keywordArray = keywords
        .split(',')
        .map(k => k.trim())
        .filter(k => k.length > 0);

      if (keywordArray.length === 0) {
        setError('Please enter at least one keyword');
        setLoading(false);
        return;
      }

      const response = await fetch(`${config.apiUrl}/api/live-monitor/explosive-topics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keywords: keywordArray,
          cache_hours: cacheHours,
          max_results: 10,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setTopics(data.topics);
        setCacheInfo({
          source: data.source,
          cachedAt: data.cached_at,
          expiresInMinutes: data.cache_expires_in_minutes,
        });
      } else {
        setError('Failed to fetch topics');
      }
    } catch (err) {
      console.error('Error fetching topics:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key in input
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading) {
      handleRefresh();
    }
  };

  // Auto-fetch topics on component mount
  useEffect(() => {
    if (!autoFetched) {
      setAutoFetched(true);
      console.log('Auto-fetching topics with default keywords:', keywords);
      handleRefresh();
    }
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div className="live-monitor-dashboard">
      {/* Control Bar */}
      <div className="monitor-control-bar">
        <div className="control-left">
          <label className="control-label">🔍 Focus Keywords:</label>
          <input
            type="text"
            className="keyword-input"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter keywords (comma-separated)"
            disabled={loading}
          />
        </div>

        <div className="control-right">
          <select
            className="cache-select"
            value={cacheHours}
            onChange={(e) => setCacheHours(Number(e.target.value))}
            disabled={loading}
          >
            <option value={1}>1 hour</option>
            <option value={3}>3 hours</option>
            <option value={6}>6 hours</option>
            <option value={12}>12 hours</option>
            <option value={24}>24 hours</option>
          </select>

          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={loading}
          >
            {loading ? (
              <>⏳ Loading...</>
            ) : (
              <>🔄 Refresh</>
            )}
          </button>
        </div>
      </div>

      {/* Cache Info */}
      {cacheInfo && !loading && (
        <div className="cache-info">
          {cacheInfo.source === 'cache' ? '📦 Cached' : '🔄 Fresh'} •
          Expires in {cacheInfo.expiresInMinutes} minutes •
          {topics.length} topics found
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Carousel */}
      <TopicCarousel topics={topics} loading={loading} />
    </div>
  );
}

