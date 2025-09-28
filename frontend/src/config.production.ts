// Production Configuration for AWS Deployment
export const PRODUCTION_CONFIG = {
  apiUrl: process.env.REACT_APP_API_URL || 'https://api.tavily-research.amazonaws.com',
  environment: 'production',
  enableAnalytics: true,
  enableSourceMaps: false,
  cacheTimeout: 300000, // 5 minutes
  
  // CloudFront specific settings
  cloudfront: {
    distributionDomain: process.env.REACT_APP_CLOUDFRONT_DOMAIN || '',
    cacheTTL: 86400 // 24 hours
  },
  
  // Performance optimizations
  performance: {
    enableLazyLoading: true,
    enableCodeSplitting: true,
    enablePreloading: true
  }
};

export const API_CONFIG = {
  baseURL: PRODUCTION_CONFIG.apiUrl,
  timeout: 120000, // 2 minutes for research queries
  environment: PRODUCTION_CONFIG.environment,
  retryAttempts: 3,
  retryDelay: 1000
};

export const getSessionId = (): string => {
  let sessionId = localStorage.getItem('user_session_id');
  if (!sessionId) {
    sessionId = `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem('user_session_id', sessionId);
  }
  return sessionId;
};
