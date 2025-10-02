import { useState, useEffect } from 'react';
import { X, Download, Maximize2, Minimize2, ExternalLink, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { EnhancedTooltip, AgentTooltip } from '../ui/EnhancedTooltip';
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
  artifacts: Artifact[];
  selectedIndex: number;
  onSelectArtifact: (index: number) => void;
  onClose: () => void;
}

export function ArtifactPanel({ artifacts, selectedIndex, onSelectArtifact, onClose }: ArtifactPanelProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [pngLoadFailed, setPngLoadFailed] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);
  
  // Get the currently selected artifact
  const artifact = artifacts[selectedIndex] || null;
  
  // Zoom controls
  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 25, 50));
  const handleZoomReset = () => setZoomLevel(100);
  
  // Reset PNG load state when artifact changes
  useEffect(() => {
    setPngLoadFailed(false);
  }, [artifact?.artifact_id]);

  // DEBUG: Log panel state
  console.log('🎨 ArtifactPanel Render:', {
    artifactsCount: artifacts.length,
    selectedIndex,
    hasArtifact: !!artifact,
    artifactId: artifact?.artifact_id,
    artifactTitle: artifact?.title
  });

  if (artifacts.length === 0) {
    console.log('   ⚠️  Showing empty state: no artifacts');
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

  if (!artifact) {
    console.log('   ⚠️  Showing empty state: invalid selectedIndex');
    return (
      <div className="artifact-panel artifact-panel-empty">
        <div className="artifact-empty-state">
          <div className="artifact-empty-icon">⚠️</div>
          <h3>Artifact Not Found</h3>
          <p>Selected artifact index is invalid</p>
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
      {/* Artifact Tabs - Show when multiple artifacts exist */}
      {artifacts.length > 1 && (
        <div className="artifact-tabs">
          {artifacts.map((art, index) => (
            <button
              key={art.artifact_id}
              className={`artifact-tab ${index === selectedIndex ? 'active' : ''}`}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onSelectArtifact(index);
              }}
              type="button"
              title={art.title}
            >
              <span className="artifact-tab-icon">📊</span>
              <span className="artifact-tab-label">
                {art.title || `Chart ${index + 1}`}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Header */}
      <div className="artifact-header">
        <div className="artifact-header-info">
          <div className="artifact-type-badge">
            {artifact.type.replace('_', ' ')}
            {artifacts.length > 1 && (
              <span className="artifact-count"> ({selectedIndex + 1}/{artifacts.length})</span>
            )}
          </div>
          <div className="artifact-title">{artifact.title}</div>
        </div>
        
        <div className="artifact-header-actions">
          {/* Zoom Controls */}
          {artifact.png_url && (
            <>
              <EnhancedTooltip
                content="Zoom out (Min: 50%)"
                icon="feature"
                position="bottom"
              >
                <button
                  className="artifact-action-button"
                  onClick={handleZoomOut}
                  aria-label="Zoom Out"
                  disabled={zoomLevel <= 50}
                >
                  <ZoomOut size={18} />
                </button>
              </EnhancedTooltip>
              
              <EnhancedTooltip
                content="Current zoom level"
                icon="info"
                position="bottom"
              >
                <span className="artifact-zoom-level">{zoomLevel}%</span>
              </EnhancedTooltip>
              
              <EnhancedTooltip
                content="Zoom in (Max: 200%)"
                icon="feature"
                position="bottom"
              >
                <button
                  className="artifact-action-button"
                  onClick={handleZoomIn}
                  aria-label="Zoom In"
                  disabled={zoomLevel >= 200}
                >
                  <ZoomIn size={18} />
                </button>
              </EnhancedTooltip>
              
              <EnhancedTooltip
                content="Reset zoom to 100%"
                icon="feature"
                position="bottom"
              >
                <button
                  className="artifact-action-button"
                  onClick={handleZoomReset}
                  aria-label="Reset Zoom"
                >
                  <RotateCcw size={18} />
                </button>
              </EnhancedTooltip>
            </>
          )}
          
          {artifact.png_url && (
            <EnhancedTooltip
              content="Download visualization as PNG image"
              icon="feature"
              position="bottom"
            >
              <button
                className="artifact-action-button"
                onClick={handleDownload}
                aria-label="Download PNG"
              >
                <Download size={18} />
              </button>
            </EnhancedTooltip>
          )}
          
          <EnhancedTooltip
            content={isFullscreen ? "Exit fullscreen mode" : "View in fullscreen mode"}
            icon="feature"
            position="bottom"
          >
            <button
              className="artifact-action-button"
              onClick={() => setIsFullscreen(!isFullscreen)}
              aria-label={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
            >
              {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
            </button>
          </EnhancedTooltip>

          {artifact.html_url && (
            <EnhancedTooltip
              content="Open interactive HTML version in new tab"
              icon="feature"
              position="bottom"
            >
              <button
                className="artifact-action-button"
                onClick={() => window.open(artifact.html_url, '_blank')}
                aria-label="View Interactive"
              >
                <ExternalLink size={18} />
              </button>
            </EnhancedTooltip>
          )}
          
          <EnhancedTooltip
            content="Close visualization panel"
            icon="info"
            position="bottom"
          >
            <button
              className="artifact-action-button"
              onClick={onClose}
              aria-label="Close"
            >
              <X size={18} />
            </button>
          </EnhancedTooltip>
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

        {/* Data Table: Show link to download JSON */}
        {artifact.status === 'ready' && artifact.type === 'data_table' && artifact.data_url && (
          <div className="artifact-data-table">
            <div className="artifact-data-icon">📊</div>
            <h3>Sentiment Data Export</h3>
            <p>Download the sentiment analysis data in JSON format for further processing.</p>
            <a
              href={artifact.data_url}
              download
              className="artifact-download-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              📥 Download JSON Data
            </a>
          </div>
        )}

        {/* Show PNG by default (faster, no CORS issues), fallback to HTML iframe */}
        {artifact.status === 'ready' && artifact.type !== 'data_table' && artifact.png_url && !pngLoadFailed && (
          <div className="artifact-image-container">
            <img
              src={artifact.png_url}
              alt={artifact.title}
              className="artifact-image"
              style={{
                transform: `scale(${zoomLevel / 100})`,
                transition: 'transform 0.2s ease-out'
              }}
              onError={() => {
                console.log('   ⚠️  PNG load failed, falling back to HTML iframe');
                setPngLoadFailed(true);
              }}
            />
          </div>
        )}

        {artifact.status === 'ready' && artifact.type !== 'data_table' && ((!artifact.png_url || pngLoadFailed) && artifact.html_url) && (
          <>
            {console.log('   🎯 Loading iframe with URL:', artifact.html_url)}
            <iframe
              src={artifact.html_url}
              className="artifact-iframe"
              title={artifact.title}
              style={{ border: 'none', width: '100%', height: '100%' }}
              onLoad={() => console.log('   ✅ Iframe loaded successfully')}
              onError={(e) => console.error('   ❌ Iframe load error:', e)}
            />
          </>
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

