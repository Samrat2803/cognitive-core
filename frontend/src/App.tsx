import React, { useState } from 'react';
import './App.css';
import ResearchForm from './components/ResearchForm';
import ResearchResults from './components/ResearchResults';
import Header from './components/Header';
import { ResearchResponse } from './types';
import { API_CONFIG } from './config';

function App() {
  const [results, setResults] = useState<ResearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleResearch = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch(`${API_CONFIG.baseURL}/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ResearchResponse = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSearch = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <div className="container">
          <ResearchForm 
            onResearch={handleResearch} 
            isLoading={isLoading}
          />
          
          {error && (
            <div className="error-message">
              <p>❌ {error}</p>
              <button onClick={handleNewSearch} style={{
                marginTop: '1rem',
                padding: '0.5rem 1rem',
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                Try Again
              </button>
            </div>
          )}
          
          {results && (
            <div style={{ marginTop: '2rem' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '1rem'
              }}>
                <h2 style={{ color: 'var(--primary-green)' }}>Research Results</h2>
                <button 
                  onClick={handleNewSearch}
                  style={{
                    padding: '0.5rem 1rem',
                    background: 'var(--primary-green)',
                    color: 'var(--dark-bg)',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: 600
                  }}
                >
                  🔍 New Search
                </button>
              </div>
              <ResearchResults results={results} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;