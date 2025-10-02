import { useState } from 'react';
import { X, Download, Maximize2, Minimize2, ExternalLink } from 'lucide-react';
import './ArtifactPanel.css';

export interface Artifact {
  artifact_id: string;
  type: 'line_chart' | 'bar_chart' | 'pie_chart' | 'table' | 'map';
  title: string;
  description?: string;
  status: 'generating' | 'ready' | 'failed';
  html_url?: string;
  png_url?: string;
  data_url?: string;
  created_at: string;
  size_bytes?: number;
}

interface ArtifactPanelProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export function ArtifactPanel({ artifact, onClose }: ArtifactPanelProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!artifact) {
    return (
      <div className="artifact-panel artifact-panel-empty">
        <div className="artifact-empty-state">
          <div className="artifact-empty-icon">📊</div>
          <h3>No Artifact</h3>
          <p>Artifacts like charts and visualizations will appear here</p>
        </div>
      </div>
    );
  }

  const handleDownload = async () => {
    if (!artifact.png_url) return;
    
    try {
      // Fetch the PNG file
      const response = await fetch(artifact.png_url);
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${artifact.artifact_id}.png`;
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      // Fallback: open in new tab
      window.open(artifact.png_url, '_blank');
    }
  };

  return (
    <div className={`artifact-panel ${isFullscreen ? 'artifact-panel-fullscreen' : ''}`}>
      {/* Header */}
      <div className="artifact-header">
        <div className="artifact-header-info">
          <div className="artifact-type-badge">{artifact.type.replace('_', ' ')}</div>
          <div className="artifact-title">{artifact.title}</div>
        </div>
        
        <div className="artifact-header-actions">
          {artifact.png_url && (
            <button
              className="artifact-action-button"
              onClick={handleDownload}
              title="Download PNG"
            >
              <Download size={18} />
            </button>
          )}
          
          <button
            className="artifact-action-button"
            onClick={() => setIsFullscreen(!isFullscreen)}
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>

          {artifact.html_url && (
            <button
              className="artifact-action-button"
              onClick={() => window.open(artifact.html_url, '_blank')}
              title="View Interactive"
            >
              <ExternalLink size={18} />
            </button>
          )}
          
          <button
            className="artifact-action-button"
            onClick={onClose}
            title="Close"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="artifact-content">
        {artifact.status === 'generating' && (
          <div className="artifact-loading">
            <div className="artifact-loading-spinner"></div>
            <div className="artifact-loading-text">Generating {artifact.type}...</div>
          </div>
        )}

        {artifact.status === 'failed' && (
          <div className="artifact-error">
            <div className="artifact-error-icon">⚠️</div>
            <div className="artifact-error-text">Failed to generate artifact</div>
          </div>
        )}

        {/* Show PNG by default (faster, no CORS issues), fallback to HTML iframe */}
        {artifact.status === 'ready' && artifact.png_url && (
          <div className="artifact-image-container">
            <img
              src={artifact.png_url}
              alt={artifact.title}
              className="artifact-image"
            />
          </div>
        )}

        {artifact.status === 'ready' && !artifact.png_url && artifact.html_url && (
          <iframe
            src={artifact.html_url}
            className="artifact-iframe"
            title={artifact.title}
            sandbox="allow-scripts allow-same-origin"
          />
        )}
      </div>

      {/* Footer (optional description) */}
      {artifact.description && (
        <div className="artifact-footer">
          <p className="artifact-description">{artifact.description}</p>
        </div>
      )}
    </div>
  );
}

