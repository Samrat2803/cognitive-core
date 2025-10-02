import { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import './Citations.css';

export interface Citation {
  title: string;
  url: string;
  snippet?: string;
  published_date?: string;
  score?: number;
}

interface CitationsProps {
  citations: Citation[];
}

export function Citations({ citations }: CitationsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!citations || citations.length === 0) {
    return null;
  }

  // Get unique URLs for favicon display
  const urlCitations = citations.filter(c => c.url).slice(0, 3);

  const decodeString = (str: string) => {
    try {
      return decodeURIComponent(str);
    } catch (e) {
      return str;
    }
  };

  const getDomain = (url: string): string => {
    try {
      const domain = url.replace('http://', '').replace('https://', '').split(/[/?#]/)[0];
      return domain.startsWith('www.') ? domain.slice(4) : domain;
    } catch {
      return url;
    }
  };

  return (
    <div className="citations-container">
      {/* Toggle Button */}
      <div className="citations-header">
        <button
          className="citations-toggle-button"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {/* Favicons for URL citations */}
          {urlCitations.length > 0 && (
            <div className="citations-favicons">
              {urlCitations.map((citation, idx) => (
                <img
                  key={idx}
                  src={`https://www.google.com/s2/favicons?sz=32&domain=${getDomain(citation.url)}`}
                  alt="favicon"
                  className="citation-favicon"
                />
              ))}
            </div>
          )}

          {/* Count */}
          <div className="citations-count">
            {citations.length === 1 ? '1 Source' : `${citations.length} Sources`}
          </div>

          {/* Expand Icon */}
          {isExpanded ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>
      </div>

      {/* Citations List */}
      {isExpanded && (
        <div className="citations-list">
          {citations.map((citation, idx) => (
            <a
              key={idx}
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="citation-item"
            >
              <div className="citation-number">{idx + 1}</div>
              <div className="citation-content">
                <div className="citation-title">
                  {decodeString(citation.title || getDomain(citation.url))}
                </div>
                {citation.snippet && (
                  <div className="citation-snippet">{citation.snippet}</div>
                )}
              </div>
              <ExternalLink size={14} className="citation-link-icon" />
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

