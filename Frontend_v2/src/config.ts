// Application Configuration

const isProd = import.meta.env.PROD;

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || (isProd 
    ? 'http://political-analyst-backend-v3.eba-tf2vrc23.us-east-1.elasticbeanstalk.com'
    : 'http://localhost:8001'),
  
  wsUrl: import.meta.env.VITE_WS_URL || (isProd
    ? 'ws://political-analyst-backend-v3.eba-tf2vrc23.us-east-1.elasticbeanstalk.com/ws/analyze'
    : 'ws://localhost:8001/ws/analyze'),
};

