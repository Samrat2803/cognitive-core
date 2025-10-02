import { useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Header } from './Header';
import { ChatPanel } from '../chat/ChatPanel';
import { ArtifactPanel, type Artifact } from '../artifact/ArtifactPanel';
import './MainLayout.css';

export function MainLayout() {
  const [currentArtifact, setCurrentArtifact] = useState<Artifact | null>(null);

  const handleArtifactReceived = (artifact: Artifact) => {
    console.log('📊 New artifact received:', artifact.artifact_id, artifact.title);
    // Always update to show LATEST artifact
    setCurrentArtifact(artifact);
  };

  const handleCloseArtifact = () => {
    setCurrentArtifact(null);
  };

  return (
    <div className="main-layout">
      <Header />
      <div className="content">
        <PanelGroup direction="horizontal">
          {/* Left Panel - Chat */}
          <Panel 
            defaultSize={currentArtifact ? 50 : 100} 
            minSize={30}
          >
            <ChatPanel onArtifactReceived={handleArtifactReceived} />
          </Panel>

          {/* Right Panel - Artifacts (conditional) */}
          {currentArtifact && (
            <>
              {/* Resize Handle */}
              <PanelResizeHandle className="resize-handle">
                <div className="resize-handle-line" />
              </PanelResizeHandle>

              <Panel 
                defaultSize={50} 
                minSize={20}
                collapsible
                onCollapse={handleCloseArtifact}
              >
                <ArtifactPanel 
                  key={currentArtifact.artifact_id} // Force re-render on new artifact
                  artifact={currentArtifact} 
                  onClose={handleCloseArtifact} 
                />
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>
    </div>
  );
}

