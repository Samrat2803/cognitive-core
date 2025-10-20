import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { config } from '../../config';
import './Navigation.css';

export function Navigation() {
  const location = useLocation();
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  
  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };
  
  // Check backend connection
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${config.apiUrl}/health`, {
          method: 'GET',
          signal: AbortSignal.timeout(3000)
        });
        
        if (response.ok) {
          setBackendStatus('connected');
        } else {
          setBackendStatus('disconnected');
        }
      } catch (error) {
        setBackendStatus('disconnected');
      }
    };
    
    // Check immediately
    checkBackend();
    
    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <nav className="main-navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/" className="brand-link">
            <span className="brand-icon">🏛️</span>
            <span className="brand-text">Political Analyst Workbench</span>
          </Link>
        </div>
        
        <div className="nav-links">
          <Link 
            to="/" 
            className={`nav-link ${isActive('/') && !isActive('/investigations') && !isActive('/government') && !isActive('/analysis') ? 'active' : ''}`}
          >
            <span className="nav-icon">🏠</span>
            <span className="nav-text">Home</span>
          </Link>
          
          <Link 
            to="/investigations" 
            className={`nav-link ${isActive('/investigations') ? 'active' : ''}`}
          >
            <span className="nav-icon">🔍</span>
            <span className="nav-text">Investigations</span>
          </Link>
          
          <Link 
            to="/government" 
            className={`nav-link ${isActive('/government') ? 'active' : ''}`}
          >
            <span className="nav-icon">🏛️</span>
            <span className="nav-text">Government</span>
          </Link>
          
          <Link 
            to="/analysis" 
            className={`nav-link ${isActive('/analysis') ? 'active' : ''}`}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-text">Analysis</span>
          </Link>
        </div>
        
        <div className="nav-actions">
          {/* Backend Status Indicator */}
          <div className={`backend-status status-${backendStatus}`} title={`Backend: ${backendStatus}`}>
            <span className="status-dot"></span>
            <span className="status-text">{backendStatus === 'connected' ? 'Connected' : backendStatus === 'checking' ? 'Checking...' : 'Disconnected'}</span>
          </div>
          
          <button className="nav-settings-btn" aria-label="Settings">
            <span>⚙️</span>
          </button>
        </div>
      </div>
    </nav>
  );
}

