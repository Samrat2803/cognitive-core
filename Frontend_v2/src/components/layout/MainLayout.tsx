import { useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Header } from './Header';
import { ChatPanel } from '../chat/ChatPanel';
import { ArtifactPanel, type Artifact } from '../artifact/ArtifactPanel';
import './MainLayout.css';

interface MainLayoutProps {
  initialQuery?: string;
}

export function MainLayout({ initialQuery }: MainLayoutProps) {
  // Changed: Store multiple artifacts instead of just one
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selectedArtifactIndex, setSelectedArtifactIndex] = useState<number>(0);

  const handleArtifactReceived = (artifact: Artifact) => {
    console.log('📊 MainLayout: New artifact received:', {
      artifact_id: artifact.artifact_id,
      title: artifact.title,
      type: artifact.type,
      status: artifact.status,
      has_png: !!artifact.png_url,
      has_html: !!artifact.html_url
    });
    
    setArtifacts(prev => {
      // Check if artifact already exists (avoid duplicates)
      const exists = prev.find(a => a.artifact_id === artifact.artifact_id);
      if (exists) {
        console.log('   ℹ️  Artifact already exists, skipping duplicate');
        return prev;
      }
      
      // Add new artifact to the array
      const updated = [...prev, artifact];
      console.log(`   ✅ Added artifact. Total artifacts: ${updated.length}`);
      console.log(`   🎯 Setting selected index to: ${updated.length - 1}`);
      
      // Auto-select the newly added artifact
      setSelectedArtifactIndex(updated.length - 1);
      
      return updated;
    });
  };

  const handleCloseArtifact = () => {
    setArtifacts([]);
    setSelectedArtifactIndex(0);
  };

  const handleSelectArtifact = (index: number) => {
    setSelectedArtifactIndex(index);
    console.log(`📊 Switched to artifact ${index + 1} of ${artifacts.length}`);
  };

  // Get current artifact to display
  const currentArtifact = artifacts[selectedArtifactIndex] || null;

  // DEBUG: Log state changes
  console.log('🔍 MainLayout State:', {
    artifactsCount: artifacts.length,
    selectedIndex: selectedArtifactIndex,
    hasCurrentArtifact: !!currentArtifact,
    panelShouldShow: artifacts.length > 0
  });

  return (
    <div className="main-layout">
      <Header />
      
      <div className="content">
        <PanelGroup direction="horizontal">
          {/* Left Panel - Chat */}
          <Panel 
            defaultSize={artifacts.length > 0 ? 50 : 100} 
            minSize={30}
          >
            <ChatPanel 
              onArtifactReceived={handleArtifactReceived}
              initialQuery={initialQuery}
            />
          </Panel>

          {/* Right Panel - Artifacts (conditional) */}
          {artifacts.length > 0 && (
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
                  artifacts={artifacts}
                  selectedIndex={selectedArtifactIndex}
                  onSelectArtifact={handleSelectArtifact}
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

