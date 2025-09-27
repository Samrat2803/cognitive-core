import React, { useState } from 'react';
import './App.css';
import ResearchForm from './components/ResearchForm';
import ResearchResults from './components/ResearchResults';
import Header from './components/Header';
import { ResearchResponse } from './types';

function App() {
  const [results, setResults] = useState<ResearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleResearch = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('http://localhost:8000/research', {
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
            </div>
          )}
          
          {results && (
            <ResearchResults results={results} />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;