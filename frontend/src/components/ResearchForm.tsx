import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

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

  return (
    <form className="research-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="query">
          <Search size={20} style={{ display: 'inline', marginRight: '8px' }} />
          Research Query
        </label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your research question here... (e.g., 'What are the latest developments in quantum computing?')"
          disabled={isLoading}
          maxLength={500}
        />
        <small style={{ color: '#666', fontSize: '0.85rem' }}>
          {query.length}/500 characters
        </small>
      </div>
      
      <button 
        type="submit" 
        className="submit-button"
        disabled={!query.trim() || isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="loading-spinner" />
            Researching...
          </>
        ) : (
          <>
            <Search size={20} />
            Start Research
          </>
        )}
      </button>
    </form>
  );
};

export default ResearchForm;
