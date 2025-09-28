import React from 'react';
import { UI_CONFIG } from '../config';

interface LoadingIndicatorProps {
  progress?: number;
  currentStep?: string;
  isVisible?: boolean;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  progress = 0,
  currentStep = 'Processing...',
  isVisible = true
}) => {
  if (!isVisible) return null;

  const containerStyle: React.CSSProperties = {
    background: UI_CONFIG.colors.darkest,
    border: `2px solid ${UI_CONFIG.colors.primary}`,
    borderRadius: '16px',
    padding: '2rem',
    margin: '2rem 0',
    textAlign: 'center',
    color: UI_CONFIG.colors.white,
    fontFamily: UI_CONFIG.fonts.main
  };

  const spinnerStyle: React.CSSProperties = {
    position: 'relative',
    display: 'inline-block',
    marginBottom: '1.5rem'
  };

  const spinnerRingStyle: React.CSSProperties = {
    width: '80px',
    height: '80px',
    border: `4px solid ${UI_CONFIG.colors.secondary}`,
    borderTop: `4px solid ${UI_CONFIG.colors.primary}`,
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  };

  const spinnerInnerStyle: React.CSSProperties = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)'
  };

  const detailsStyle: React.CSSProperties = {
    maxWidth: '400px',
    margin: '0 auto'
  };

  const progressBarStyle: React.CSSProperties = {
    background: UI_CONFIG.colors.secondary,
    borderRadius: '10px',
    height: '8px',
    marginBottom: '1.5rem',
    overflow: 'hidden'
  };

  const progressFillStyle: React.CSSProperties = {
    background: `linear-gradient(90deg, ${UI_CONFIG.colors.primary}, #a3e635)`,
    height: '100%',
    transition: 'width 0.5s ease-in-out',
    borderRadius: '10px',
    width: `${progress}%`
  };

  const agentsGridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '1rem',
    marginTop: '1rem'
  };

  const getAgentStepStyle = (isActive: boolean, isCompleted: boolean): React.CSSProperties => ({
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '0.5rem',
    borderRadius: '8px',
    background: isCompleted ? UI_CONFIG.colors.primary : (isActive ? UI_CONFIG.colors.secondary : UI_CONFIG.colors.dark),
    color: isCompleted ? UI_CONFIG.colors.darkest : UI_CONFIG.colors.white,
    opacity: isActive ? 1 : 0.5,
    transition: 'all 0.3s ease'
  });

  return (
    <div style={containerStyle}>
      <div style={spinnerStyle}>
        <div style={spinnerRingStyle}></div>
        <div style={spinnerInnerStyle}>
          <span style={{ fontWeight: 'bold', fontSize: '0.9rem', color: UI_CONFIG.colors.primary }}>
            {Math.round(progress)}%
          </span>
        </div>
      </div>
      
      <div style={detailsStyle}>
        <h3 style={{ color: UI_CONFIG.colors.primary, fontSize: '1.5rem', marginBottom: '0.5rem' }}>
          Researching...
        </h3>
        <p style={{ color: UI_CONFIG.colors.white, marginBottom: '1rem', fontStyle: 'italic' }}>
          {currentStep}
        </p>
        
        <div style={progressBarStyle}>
          <div style={progressFillStyle}></div>
        </div>
        
        <div style={agentsGridStyle}>
          <div style={getAgentStepStyle(progress >= 25, progress >= 50)}>
            <span style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>🔍</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 500, textAlign: 'center' }}>Query Analysis</span>
          </div>
          <div style={getAgentStepStyle(progress >= 50, progress >= 75)}>
            <span style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>🌐</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 500, textAlign: 'center' }}>Web Search</span>
          </div>
          <div style={getAgentStepStyle(progress >= 75, progress >= 90)}>
            <span style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>📊</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 500, textAlign: 'center' }}>Result Analysis</span>
          </div>
          <div style={getAgentStepStyle(progress >= 90, progress >= 100)}>
            <span style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>✨</span>
            <span style={{ fontSize: '0.8rem', fontWeight: 500, textAlign: 'center' }}>Synthesis</span>
          </div>
        </div>
      </div>
      
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};
