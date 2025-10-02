// Application Configuration

const isProd = import.meta.env.PROD;

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || (isProd 
    ? 'http://political-analyst-backend-v3.eba-tf2vrc23.us-east-1.elasticbeanstalk.com'
    : 'http://localhost:8001'),
  
  // TEMPORARY: WebSocket disabled in production due to HTTPS/WSS requirement
  // Will be re-enabled once backend has SSL certificate configured
  wsUrl: import.meta.env.VITE_WS_URL || (isProd
    ? '' // Disabled: Browser blocks ws:// from https:// pages
    : 'ws://localhost:8001/ws/analyze'),
  
  // Use REST API in production until WebSocket SSL is configured
  useRestApi: isProd,
};

