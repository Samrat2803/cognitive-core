import { FileQuestion } from 'lucide-react';
import './ArtifactPanel.css';

export function ArtifactPanel() {
  return (
    <div className="artifact-panel">
      <div className="artifact-placeholder">
        <FileQuestion size={48} className="placeholder-icon" />
        <h3>No Artifact Yet</h3>
        <p>Charts and visualizations will appear here when generated.</p>
      </div>
    </div>
  );
}

