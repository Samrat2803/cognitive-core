import React, { useState, useEffect } from 'react';
import { ExternalLink, Loader2, AlertCircle, Calendar, Globe, FileText, Hash } from 'lucide-react';
import { Markdown } from './ui/Markdown';
import { config } from '../config';
import './ArticleViewer.css';

interface ArticleData {
  url: string;
  domain: string;
  title: string;
  content: string;
  crawled_at: string | null;
  content_length: number;
  doc_id: string;
  metadata: {
    tender_id: string;
    organization: string;
    status: string;
    query_keywords: string[];
    relevance_score: number;
  };
}

interface ChunkData {
  chunk_id: string;
  content: string;
  index: number;
}

interface ArticleViewerProps {
  url: string | null;
}

export function ArticleViewer({ url }: ArticleViewerProps) {
  const [article, setArticle] = useState<ArticleData | null>(null);
  const [chunks, setChunks] = useState<ChunkData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showChunks, setShowChunks] = useState(false);

  useEffect(() => {
    if (url) {
      fetchArticle(url);
    } else {
      setArticle(null);
      setChunks([]);
      setError(null);
    }
  }, [url]);

  const fetchArticle = async (pageUrl: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${config.apiUrl}/api/cognitive_crawler/page?url=${encodeURIComponent(pageUrl)}`
      );
      const data = await response.json();

      if (data.success) {
        setArticle(data.page);
        setChunks(data.chunks || []);
      } else {
        setError(data.error || 'Failed to fetch article');
      }
    } catch (err) {
      setError('Network error: Could not fetch article');
      console.error('Error fetching article:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Empty state
  if (!url) {
    return (
      <div className="article-viewer-empty">
        <FileText className="empty-icon" size={64} />
        <h3>No Article Selected</h3>
        <p>Click on a source URL or crawled page to view its content</p>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="article-viewer-loading">
        <Loader2 className="spinner" size={48} />
        <p>Loading article...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="article-viewer-error">
        <AlertCircle className="error-icon" size={48} />
        <h3>Failed to Load Article</h3>
        <p>{error}</p>
        <button onClick={() => fetchArticle(url)} className="retry-btn">
          Try Again
        </button>
      </div>
    );
  }

  // Content loaded
  if (!article) {
    return null;
  }

  return (
    <div className="article-viewer">
      {/* Header with metadata */}
      <div className="article-header">
        <div className="article-title-section">
          <h2 className="article-title">{article.title}</h2>
          <a 
            href={article.url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="article-url"
          >
            <Globe size={14} />
            {article.domain}
            <ExternalLink size={14} />
          </a>
        </div>

        <div className="article-metadata">
          <div className="metadata-item">
            <Calendar size={14} />
            <span>
              {article.crawled_at 
                ? new Date(article.crawled_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })
                : 'Unknown date'
              }
            </span>
          </div>
          <div className="metadata-item">
            <FileText size={14} />
            <span>{(article.content_length / 1024).toFixed(1)} KB</span>
          </div>
          {chunks.length > 0 && (
            <div className="metadata-item">
              <Hash size={14} />
              <span>{chunks.length} chunks</span>
            </div>
          )}
        </div>

        {/* Toggle chunks button */}
        {chunks.length > 0 && (
          <button 
            className="toggle-chunks-btn"
            onClick={() => setShowChunks(!showChunks)}
          >
            {showChunks ? 'Show Article' : 'Show Chunks'}
          </button>
        )}
      </div>

      {/* Content */}
      <div className="article-content">
        {!showChunks ? (
          // Full article view
          <div className="article-body">
            <Markdown>{article.content}</Markdown>
          </div>
        ) : (
          // Chunks view (for debugging)
          <div className="chunks-view">
            <div className="chunks-header">
              <h3>Embedding Chunks ({chunks.length})</h3>
              <p className="chunks-hint">
                These are the text segments used for semantic search and RAG
              </p>
            </div>
            {chunks.map((chunk, idx) => (
              <div key={chunk.chunk_id} className="chunk-item">
                <div className="chunk-header">
                  <span className="chunk-number">Chunk {idx + 1}</span>
                  <span className="chunk-id">{chunk.chunk_id}</span>
                </div>
                <div className="chunk-content">
                  <Markdown>{chunk.content}</Markdown>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Additional metadata (collapsible) */}
      {article.metadata && (
        <details className="article-metadata-details">
          <summary>Additional Metadata</summary>
          <div className="metadata-grid">
            {article.metadata.organization && (
              <div className="metadata-row">
                <strong>Organization:</strong>
                <span>{article.metadata.organization}</span>
              </div>
            )}
            {article.metadata.status && (
              <div className="metadata-row">
                <strong>Status:</strong>
                <span>{article.metadata.status}</span>
              </div>
            )}
            {article.metadata.query_keywords && article.metadata.query_keywords.length > 0 && (
              <div className="metadata-row">
                <strong>Keywords:</strong>
                <span>{article.metadata.query_keywords.join(', ')}</span>
              </div>
            )}
            {article.metadata.relevance_score > 0 && (
              <div className="metadata-row">
                <strong>Relevance Score:</strong>
                <span>{article.metadata.relevance_score.toFixed(2)}</span>
              </div>
            )}
            <div className="metadata-row">
              <strong>Document ID:</strong>
              <span className="doc-id">{article.doc_id}</span>
            </div>
          </div>
        </details>
      )}
    </div>
  );
}

