/**
 * Configuration settings for the Web Research Agent Frontend
 */

export const API_CONFIG = {
  // Backend API settings - env-driven
  baseURL: process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : 'http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com'),
  wsBaseURL: process.env.REACT_APP_WS_URL || (process.env.NODE_ENV === 'development' ? 'ws://localhost:8000/ws' : 'wss://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/ws'),
  timeout: 120000, // 2 minutes for research queries
  
  // Environment settings
  environment: process.env.REACT_APP_ENVIRONMENT || 'development',
  
  // Mock backend flag - set REACT_APP_USE_MOCK=true to use mock data
  useMockBackend: process.env.REACT_APP_USE_MOCK === 'true' || false,
  
  // API endpoints (aligned to MVP contracts)
  endpoints: {
    root: '/',
    health: '/health',
    // legacy
    research: '/research',
    // chat
    chatMessage: '/api/chat/message',
    chatConfirm: '/api/chat/confirm-analysis',
    // analysis
    analysisExecute: '/api/analysis/execute',
    analysisById: (analysisId: string) => `/api/analysis/${analysisId}`,
    // export
    exportCreate: '/api/export/create',
    exportById: (exportId: string) => `/api/export/${exportId}`,
    exportDownload: (exportId: string) => `/api/export/download/${exportId}`,
  }
};

export const UI_CONFIG = {
  // Modern professional palette (Linear/GitHub-inspired)
  colors: {
    // Aistra palette
    primary: '#d9f378',
    secondary: '#5d535c',
    dark: '#333333',
    darkest: '#1c1e20',
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
