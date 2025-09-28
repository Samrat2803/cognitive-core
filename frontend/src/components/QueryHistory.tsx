import React, { useState, useEffect } from 'react';
import { UI_CONFIG } from '../config';

interface HistoryItem {
  id: string;
  query: string;
  timestamp: string;
  success: boolean;
  results: any;
}

interface QueryHistoryProps {
  onSelectQuery?: (query: string) => void;
  className?: string;
}

export const QueryHistory: React.FC<QueryHistoryProps> = ({ 
  onSelectQuery, 
  className = '' 
}) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    try {
      const savedHistory = localStorage.getItem('research_history');
      if (savedHistory) {
        setHistory(JSON.parse(savedHistory));
      }
    } catch (error) {
      console.error('Error loading history:', error);
      setHistory([]);
    }
  };

  const clearHistory = () => {
    localStorage.removeItem('research_history');
    setHistory([]);
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      
      if (diffMinutes < 1) return 'Just now';
      if (diffMinutes < 60) return `${diffMinutes}m ago`;
      
      const diffHours = Math.floor(diffMinutes / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays < 7) return `${diffDays}d ago`;
      
      return date.toLocaleDateString();
    } catch (error) {
      return 'Unknown';
    }
  };

  const truncateQuery = (query: string, maxLength: number = 60) => {
    return query.length > maxLength ? query.substring(0, maxLength) + '...' : query;
  };

  if (history.length === 0) {
    return (
      <div 
        className={className}
        style={{
          background: UI_CONFIG.colors.dark,
          border: `1px solid ${UI_CONFIG.colors.secondary}`,
          borderRadius: '12px',
          padding: '2rem',
          textAlign: 'center',
          color: UI_CONFIG.colors.white,
          fontFamily: UI_CONFIG.fonts.main
        }}
      >
        <div style={{ opacity: 0.7 }}>
          <span style={{ fontSize: '2rem', display: 'block', marginBottom: '1rem' }}>🔍</span>
          <p style={{ margin: '0.5rem 0' }}>No previous queries yet</p>
          <p style={{ fontSize: '0.9rem', color: UI_CONFIG.colors.secondary, margin: '0.5rem 0' }}>
            Your research history will appear here
          </p>
        </div>
      </div>
    );
  }

  const containerStyle: React.CSSProperties = {
    background: UI_CONFIG.colors.dark,
    border: `1px solid ${UI_CONFIG.colors.secondary}`,
    borderRadius: '12px',
    marginBottom: '1rem',
    fontFamily: UI_CONFIG.fonts.main,
    color: UI_CONFIG.colors.white
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem',
    borderBottom: isExpanded ? `1px solid ${UI_CONFIG.colors.secondary}` : 'none'
  };

  const titleStyle: React.CSSProperties = {
    margin: 0,
    fontSize: '1.1rem',
    color: UI_CONFIG.colors.primary,
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem'
  };

  const controlsStyle: React.CSSProperties = {
    display: 'flex',
    gap: '0.5rem'
  };

  const buttonStyle: React.CSSProperties = {
    background: 'transparent',
    border: `1px solid ${UI_CONFIG.colors.secondary}`,
    color: UI_CONFIG.colors.white,
    borderRadius: '6px',
    padding: '0.25rem 0.5rem',
    cursor: 'pointer',
    fontSize: '0.9rem',
    transition: 'all 0.2s ease'
  };

  const listStyle: React.CSSProperties = {
    maxHeight: '300px',
    overflowY: 'auto'
  };

  const itemStyle: React.CSSProperties = {
    padding: '0.75rem 1rem',
    borderBottom: `1px solid ${UI_CONFIG.colors.secondary}`,
    transition: 'background-color 0.2s ease'
  };

  return (
    <div className={className} style={containerStyle}>
      <div style={headerStyle}>
        <h3 style={titleStyle}>
          <span style={{ fontSize: '1.2rem' }}>📚</span>
          Recent Queries ({history.length})
        </h3>
        <div style={controlsStyle}>
          <button
            style={buttonStyle}
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? 'Collapse' : 'Expand'}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = UI_CONFIG.colors.secondary;
              e.currentTarget.style.borderColor = UI_CONFIG.colors.primary;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = UI_CONFIG.colors.secondary;
            }}
          >
            {isExpanded ? '▲' : '▼'}
          </button>
          {history.length > 0 && (
            <button
              style={buttonStyle}
              onClick={clearHistory}
              title="Clear all history"
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#ff6b6b';
                e.currentTarget.style.borderColor = '#ff6b6b';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.borderColor = UI_CONFIG.colors.secondary;
              }}
            >
              🗑️
            </button>
          )}
        </div>
      </div>

      {isExpanded && (
        <div style={listStyle}>
          {history.map((item, index) => (
            <div 
              key={item.id} 
              style={{
                ...itemStyle,
                borderBottom: index === history.length - 1 ? 'none' : `1px solid ${UI_CONFIG.colors.secondary}`
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = UI_CONFIG.colors.secondary;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
                <div 
                  style={{
                    flex: 1,
                    cursor: 'pointer',
                    color: UI_CONFIG.colors.white,
                    fontWeight: 500,
                    marginRight: '1rem',
                    transition: 'color 0.2s ease'
                  }}
                  onClick={() => onSelectQuery && onSelectQuery(item.query)}
                  title={item.query}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = UI_CONFIG.colors.primary;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = UI_CONFIG.colors.white;
                  }}
                >
                  {truncateQuery(item.query)}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
                  <span style={{ fontSize: '0.8rem' }}>
                    {item.success ? '✅' : '❌'}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: UI_CONFIG.colors.secondary }}>
                    {formatTimestamp(item.timestamp)}
                  </span>
                </div>
              </div>
              {item.success && item.results && (
                <div style={{
                  fontSize: '0.75rem',
                  color: UI_CONFIG.colors.secondary,
                  marginTop: '0.25rem',
                  paddingLeft: '0.5rem',
                  borderLeft: `2px solid ${UI_CONFIG.colors.primary}`
                }}>
                  Sources: {item.results.sources_count} • 
                  Terms: {item.results.search_terms?.join(', ') || 'N/A'}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
