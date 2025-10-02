import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiGetAnalysis, apiAnalysisExecute } from '../api/client';
import { getSessionId } from '../config';
import { wsService } from '../services/websocket';
import { AnalysisResponse } from '../types';

interface AnalysisResultsProps {
  analysisId?: string;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysisId: propAnalysisId }) => {
  const [analysisId, setAnalysisId] = useState(propAnalysisId || '');
  const [wsProgress, setWsProgress] = useState<any>(null);
  const [directExecuteForm, setDirectExecuteForm] = useState({
    query: '',
    countries: ['United States', 'Iran', 'Israel'],
    days: 7,
    resultsPerCountry: 20
  });

  // Query for analysis data with polling
  const { data: analysis, error, isLoading, refetch } = useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: () => apiGetAnalysis(analysisId),
    enabled: !!analysisId,
    refetchInterval: (query) => {
      // Poll every 2 seconds if still processing
      return query.state.data?.status === 'processing' ? 2000 : false;
    },
    refetchIntervalInBackground: true
  });

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!analysisId) return;

    const sessionId = getSessionId();
    wsService.connect(sessionId);

    const unsubscribe = wsService.on((message) => {
      if (message.type === 'analysis_progress' && message.analysis_id === analysisId) {
        setWsProgress(message);
      } else if (message.type === 'analysis_complete' && message.analysis_id === analysisId) {
        refetch(); // Refresh data when complete
        setWsProgress(null);
      } else if (message.type === 'analysis_error' && message.analysis_id === analysisId) {
        console.error('Analysis error:', message.error);
      }
    });

    return () => {
      unsubscribe();
      wsService.disconnect();
    };
  }, [analysisId, refetch]);

  const handleDirectExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiAnalysisExecute({
        query_text: directExecuteForm.query,
        parameters: {
          countries: directExecuteForm.countries,
          days: directExecuteForm.days,
          results_per_country: directExecuteForm.resultsPerCountry,
          include_bias_analysis: true
        },
        session_id: getSessionId()
      });
      setAnalysisId(response.analysis_id);
    } catch (err) {
      console.error('Failed to start analysis:', err);
    }
  };

  const renderProgress = () => {
    const progress = wsProgress?.progress || analysis?.progress;
    if (!progress) return null;

    return (
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h3 style={{ color: 'var(--aistra-primary)', marginTop: 0 }}>
          Analysis Progress
        </h3>
        
        <div style={{ marginBottom: '1rem' }}>
          <div style={{
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '10px',
            height: '8px',
            overflow: 'hidden'
          }}>
            <div style={{
              background: 'var(--aistra-primary)',
              height: '100%',
              width: `${progress.completion_percentage || 0}%`,
              transition: 'width 0.3s ease'
            }} />
          </div>
          <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
            {progress.completion_percentage || 0}% complete
          </p>
        </div>

        <p><strong>Current Step:</strong> {progress.current_step}</p>
        
        {progress.processed_countries && progress.processed_countries.length > 0 && (
          <p><strong>Processed Countries:</strong> {progress.processed_countries.join(', ')}</p>
        )}
        
        {progress.remaining_countries && progress.remaining_countries.length > 0 && (
          <p><strong>Remaining:</strong> {progress.remaining_countries.join(', ')}</p>
        )}
        
        {progress.articles_processed !== undefined && (
          <p><strong>Articles:</strong> {progress.articles_processed} / {progress.total_articles || '?'}</p>
        )}
      </div>
    );
  };

  const renderResults = (analysis: AnalysisResponse) => {
    if (!analysis.results) return null;

    const { summary, country_results } = analysis.results;

    return (
      <div>
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ color: 'var(--aistra-primary)', marginTop: 0 }}>
            Analysis Summary
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <p><strong>Overall Sentiment:</strong></p>
              <p style={{ 
                fontSize: '1.5rem', 
                color: summary.overall_sentiment >= 0 ? '#10b981' : '#ef4444',
                margin: 0 
              }}>
                {summary.overall_sentiment.toFixed(2)}
              </p>
            </div>
            <div>
              <p><strong>Countries Analyzed:</strong></p>
              <p style={{ fontSize: '1.5rem', margin: 0 }}>{summary.countries_analyzed}</p>
            </div>
            <div>
              <p><strong>Total Articles:</strong></p>
              <p style={{ fontSize: '1.5rem', margin: 0 }}>{summary.total_articles}</p>
            </div>
            <div>
              <p><strong>Confidence:</strong></p>
              <p style={{ fontSize: '1.5rem', margin: 0 }}>{(summary.analysis_confidence * 100).toFixed(1)}%</p>
            </div>
          </div>
          
          {summary.bias_detected && (
            <div style={{ 
              marginTop: '1rem', 
              padding: '0.75rem', 
              background: 'rgba(251, 191, 36, 0.1)',
              borderRadius: '6px',
              border: '1px solid rgba(251, 191, 36, 0.3)'
            }}>
              ⚠️ Bias detected in sources - review country-specific analysis below
            </div>
          )}
        </div>

        {country_results && country_results.map((country, index) => (
          <div key={index} className="card" style={{ marginBottom: '1.5rem' }}>
            <h4 style={{ color: 'var(--aistra-primary)', marginTop: 0 }}>
              {country.country}
            </h4>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <p><strong>Sentiment Score:</strong></p>
                <p style={{ 
                  fontSize: '1.2rem', 
                  color: country.sentiment_score >= 0 ? '#10b981' : '#ef4444',
                  margin: 0 
                }}>
                  {country.sentiment_score.toFixed(2)}
                </p>
              </div>
              <div>
                <p><strong>Dominant Sentiment:</strong></p>
                <p style={{ fontSize: '1.1rem', margin: 0, textTransform: 'capitalize' }}>
                  {country.dominant_sentiment}
                </p>
              </div>
              <div>
                <p><strong>Articles:</strong></p>
                <p style={{ fontSize: '1.1rem', margin: 0 }}>{country.articles_count}</p>
              </div>
              <div>
                <p><strong>Confidence:</strong></p>
                <p style={{ fontSize: '1.1rem', margin: 0 }}>{(country.confidence * 100).toFixed(1)}%</p>
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <p><strong>Key Themes:</strong></p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {country.key_themes.map((theme, i) => (
                  <span key={i} style={{
                    background: 'var(--aistra-secondary)',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.9rem'
                  }}>
                    {theme}
                  </span>
                ))}
              </div>
            </div>

            {country.bias_analysis && (
              <div style={{ 
                padding: '0.75rem', 
                background: 'rgba(255,255,255,0.05)',
                borderRadius: '6px'
              }}>
                <p><strong>Bias Analysis:</strong></p>
                <p>Types: {country.bias_analysis.bias_types.join(', ')}</p>
                <p>Severity: {(country.bias_analysis.bias_severity * 100).toFixed(1)}%</p>
                <p style={{ fontSize: '0.9rem', fontStyle: 'italic' }}>
                  {country.bias_analysis.notes}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto' }}>
      <h1 style={{ color: 'var(--aistra-primary)', marginBottom: '2rem' }}>
        Analysis Results
      </h1>

      {!analysisId && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ color: 'var(--aistra-primary)', marginTop: 0 }}>
            Start Direct Analysis
          </h3>
          <form onSubmit={handleDirectExecute}>
            <div style={{ marginBottom: '1rem' }}>
              <label 
                htmlFor="query-text-input"
                style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}
              >
                Query Text
              </label>
              <input
                id="query-text-input"
                type="text"
                value={directExecuteForm.query}
                onChange={(e) => setDirectExecuteForm(prev => ({ ...prev, query: e.target.value }))}
                placeholder="e.g., Hamas sentiment analysis"
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'var(--aistra-dark)',
                  color: 'var(--aistra-white)'
                }}
              />
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <label 
                htmlFor="analysis-id-input"
                style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}
              >
                Analysis ID (if continuing existing)
              </label>
              <input
                id="analysis-id-input"
                type="text"
                value={analysisId}
                onChange={(e) => setAnalysisId(e.target.value)}
                placeholder="analysis_123456789"
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  borderRadius: '6px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'var(--aistra-dark)',
                  color: 'var(--aistra-white)'
                }}
              />
            </div>

            <button type="submit" className="button-primary" disabled={!directExecuteForm.query.trim()}>
              🚀 Start Analysis
            </button>
          </form>
        </div>
      )}

      {error && (
        <div className="card" style={{ marginBottom: '2rem', borderColor: '#ef4444' }}>
          <p style={{ color: '#ef4444', margin: 0 }}>
            ❌ Error loading analysis: {error.message}
          </p>
        </div>
      )}

      {isLoading && (
        <div className="card" style={{ textAlign: 'center' }}>
          <p>⏳ Loading analysis...</p>
        </div>
      )}

      {analysis && (
        <div>
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h3 style={{ color: 'var(--aistra-primary)', marginTop: 0 }}>
              Analysis Info
            </h3>
            <p><strong>ID:</strong> {analysis.analysis_id}</p>
            <p><strong>Status:</strong> 
              <span style={{ 
                marginLeft: '0.5rem',
                padding: '0.25rem 0.5rem',
                borderRadius: '4px',
                background: analysis.status === 'completed' ? '#10b981' : 
                           analysis.status === 'processing' ? '#f59e0b' : '#6b7280',
                color: 'white',
                fontSize: '0.9rem'
              }}>
                {analysis.status}
              </span>
            </p>
            <p><strong>Created:</strong> {new Date(analysis.created_at).toLocaleString()}</p>
            {analysis.completed_at && (
              <p><strong>Completed:</strong> {new Date(analysis.completed_at).toLocaleString()}</p>
            )}
          </div>

          {analysis.status === 'processing' && renderProgress()}
          {analysis.status === 'completed' && renderResults(analysis)}
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
