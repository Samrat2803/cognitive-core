import { useEffect, useState } from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  progress: number; // 0 to 1
  message?: string;
  showPercentage?: boolean;
}

export function ProgressBar({ progress, message, showPercentage = true }: ProgressBarProps) {
  const [displayProgress, setDisplayProgress] = useState(0);

  // Smooth animation of progress
  useEffect(() => {
    const timer = setTimeout(() => {
      setDisplayProgress(progress * 100);
    }, 50);
    return () => clearTimeout(timer);
  }, [progress]);

  return (
    <div className="progress-bar-container">
      {(message || showPercentage) && (
        <div className="progress-bar-header">
          {message && <span className="progress-message">{message}</span>}
          {showPercentage && (
            <span className="progress-percentage">{Math.round(displayProgress)}%</span>
          )}
        </div>
      )}
      <div className="progress-bar-track">
        <div 
          className="progress-bar-fill"
          style={{ width: `${displayProgress}%` }}
        />
      </div>
    </div>
  );
}

