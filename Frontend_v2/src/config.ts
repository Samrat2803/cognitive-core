// Application Configuration

const isProd = import.meta.env.PROD;

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || (isProd 
    ? 'https://d1h4cjcbl77aah.cloudfront.net'
    : 'http://localhost:8000'),
  
  wsUrl: import.meta.env.VITE_WS_URL || (isProd
    ? 'wss://d1h4cjcbl77aah.cloudfront.net/ws/analyze'
    : 'ws://localhost:8000/ws/analyze'),
};

