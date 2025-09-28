/**
 * Configuration settings for the Web Research Agent Frontend
 */

export const API_CONFIG = {
  // Backend API settings - env-driven
  baseURL: process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : 'http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com'),
  timeout: 120000, // 2 minutes for research queries
  
  // Environment settings
  environment: process.env.REACT_APP_ENVIRONMENT || 'development',
  
  // API endpoints
  endpoints: {
    root: '/',
    health: '/health',
    research: '/research',
  }
};

export const UI_CONFIG = {
  // Modern professional palette (Linear/GitHub-inspired)
  colors: {
    primary: '#2563eb',
    secondary: '#6b7280',
    dark: '#111827',
    darkest: '#0f1419',
    white: '#ffffff',
    error: '#ef4444',
    success: '#10b981',
    warning: '#f59e0b'
  },
  
  // Font settings
  fonts: {
    main: 'Roboto Flex, sans-serif'
  },
  
  // UI settings
  maxQueryLength: 1000,
  pollingInterval: 2000,    // 2 seconds for when we implement async polling
  exportFormats: ['json', 'csv', 'pdf']
};

// Session management
export const generateSessionId = (): string => {
  return 'session-' + Math.random().toString(36).substr(2, 9) + '-' + Date.now();
};

// Get or create session ID
export const getSessionId = (): string => {
  let sessionId = sessionStorage.getItem('research_session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    sessionStorage.setItem('research_session_id', sessionId);
  }
  return sessionId;
};
