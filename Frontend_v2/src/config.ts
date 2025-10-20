// Application Configuration

const isProd = import.meta.env.PROD;

const baseApiUrl = import.meta.env.VITE_API_URL || (isProd 
  ? 'https://d1h4cjcbl77aah.cloudfront.net'
  : 'http://localhost:8000');

const baseWsUrl = import.meta.env.VITE_WS_URL || (isProd
  ? 'wss://d1h4cjcbl77aah.cloudfront.net'
  : 'ws://localhost:8000');

export const config = {
  apiUrl: baseApiUrl,
  wsUrl: `${baseWsUrl}/ws/analyze`,
  
  // WebSocket endpoints
  ws: {
    analyze: `${baseWsUrl}/ws/analyze`,
    chat: `${baseWsUrl}/ws/chat`,
    investigations: (id: string) => `${baseWsUrl}/ws/investigations/${id}`,
    cognitiveCrawler: (sessionId: string) => `${baseWsUrl}/ws/cognitive_crawler/${sessionId}`,
  },
};

// Deployment Info:
// Frontend URL: https://d2dk8wkh2d0mmy.cloudfront.net (CloudFront Distribution: E1YO4Y7KXANJNR)
// Backend URL: https://d1h4cjcbl77aah.cloudfront.net (CloudFront with SSL for WebSocket)
// Backend Direct: http://political-analyst-backend-prod.eba-tf2vrc23.us-east-1.elasticbeanstalk.com
// S3 Bucket: tavily-research-frontend-1759377613

