import React from 'react';
import { Search, ExternalLink, FileText, Globe } from 'lucide-react';
import { ResearchResponse } from '../types';

interface ResearchResultsProps {
  results: ResearchResponse;
}

const ResearchResults: React.FC<ResearchResultsProps> = ({ results }) => {
  if (!results.success) {
    return (
      <div className="research-results">
        <div className="error-message">
          <p>❌ {results.error || 'Research failed'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="research-results">
      <div className="results-header">
        <h2 className="results-title">Research Results</h2>
        <div className="results-meta">
          <div className="meta-item">
            <Search size={16} />
            <span>{results.sources_count} sources</span>
          </div>
          <div className="meta-item">
            <FileText size={16} />
            <span>{results.search_terms.length} search terms</span>
          </div>
        </div>
      </div>

      {results.search_terms.length > 0 && (
        <div className="search-terms">
          <h3>Search Terms Used:</h3>
          <div className="term-tags">
            {results.search_terms.map((term, index) => (
              <span key={index} className="term-tag">
                {term}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="final-answer">
        <h3>Research Answer:</h3>
        <div className="answer-content">
          {results.final_answer}
        </div>
      </div>

      {results.sources.length > 0 && (
        <div className="sources">
          <h3>
            <Globe size={20} style={{ display: 'inline', marginRight: '8px' }} />
            Sources:
          </h3>
          <ul className="sources-list">
            {results.sources.map((source, index) => (
              <li key={index}>
                <a 
                  href={source} 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  <ExternalLink size={14} style={{ display: 'inline', marginRight: '4px' }} />
                  {source}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResearchResults;
