import React, { useState } from 'react';

interface ResearchFormProps {
  onResearch: (query: string) => void;
  isLoading: boolean;
}

const ResearchForm: React.FC<ResearchFormProps> = ({ onResearch, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onResearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
  };

  return (
    <form className="research-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="query">
          🔍 Research Query
        </label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your research question here... (e.g., 'What are the latest developments in quantum computing?')"
          disabled={isLoading}
          maxLength={500}
        />
        <small style={{ color: '#999', fontSize: '0.85rem' }}>
          {query.length}/500 characters
        </small>
      </div>
      
      <div className="form-actions">
        <button 
          type="submit" 
          className="submit-button"
          disabled={!query.trim() || isLoading}
        >
          {isLoading ? '⏳ Researching...' : '🚀 Start Research'}
        </button>
        
        {query && (
          <button 
            type="button"
            className="reset-button"
            onClick={handleClear}
            disabled={isLoading}
          >
            🧹 Clear
          </button>
        )}
      </div>
    </form>
  );
};

export default ResearchForm;
