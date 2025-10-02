import { StreamingMessage, Citation } from '../types';

type Listener = (message: StreamingMessage) => void;

export class MockWebSocketService {
  private listeners: Set<Listener> = new Set();
  private isConnected = false;
  private sessionId: string | null = null;
  private simulationTimeouts: NodeJS.Timeout[] = [];

  connect(sessionId: string) {
    this.sessionId = sessionId;
    
    // Simulate connection delay
    setTimeout(() => {
      this.isConnected = true;
      this.emit({ type: 'ping', timestamp: new Date().toISOString() });
    }, 100);
  }

  disconnect() {
    this.isConnected = false;
    this.sessionId = null;
    this.listeners.clear();
    
    // Clear all simulation timeouts
    this.simulationTimeouts.forEach(timeout => clearTimeout(timeout));
    this.simulationTimeouts = [];
  }

  send(message: any) {
    if (!this.isConnected) {
      console.warn('Mock WebSocket is not connected');
      return;
    }

    // Handle pong responses
    if (message.type === 'pong') {
      return;
    }

    // Simulate analysis request
    if (message.type === 'start_analysis') {
      this.simulateStreamingAnalysis(message.query);
    }
  }

  on(listener: Listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(message: StreamingMessage) {
    this.listeners.forEach(listener => listener(message));
  }

  private simulateStreamingAnalysis(query: string) {
    const mockCitations: Citation[] = [
      {
        id: 'c1',
        url: 'https://www.reuters.com/world/middle-east/sample-article-1',
        title: 'Middle East Political Analysis: Current Sentiment Trends',
        domain: 'reuters.com',
        credibility: 0.9,
        published_at: '2024-01-15'
      },
      {
        id: 'c2',
        url: 'https://www.bbc.com/news/world-middle-east-sample-2',
        title: 'Regional Opinion Polling Shows Shifting Views',
        domain: 'bbc.com',
        credibility: 0.85,
        published_at: '2024-01-14'
      },
      {
        id: 'c3',
        url: 'https://www.aljazeera.com/news/sample-analysis-3',
        title: 'Geopolitical Sentiment Analysis Across Nations',
        domain: 'aljazeera.com',
        credibility: 0.75,
        published_at: '2024-01-13'
      }
    ];

    const analysisText = `Based on my analysis of recent news coverage and public sentiment data, I can provide insights on ${query}.

## Key Findings

The sentiment analysis reveals significant regional variations in public opinion [1]. Recent polling data indicates a complex landscape of attitudes across different countries [2].

### United States
- **Overall Sentiment**: Moderately negative (-0.3)
- **Key Themes**: Security concerns, diplomatic relations, media coverage
- **Confidence Level**: 85%

The American public shows mixed reactions, with security considerations being a primary factor in shaping opinions.

### Iran
- **Overall Sentiment**: Strongly negative (-0.7)
- **Key Themes**: Regional tensions, economic impact, government policy
- **Confidence Level**: 78%

Iranian sentiment reflects broader geopolitical tensions and domestic policy considerations [3].

### Israel
- **Overall Sentiment**: Highly polarized (ranging from -0.8 to +0.6)
- **Key Themes**: National security, political discourse, international relations
- **Confidence Level**: 82%

Israeli public opinion shows significant internal divisions based on political affiliation and regional perspectives.

## Methodology

This analysis incorporates:
- 1,247 news articles from 45 sources
- Social media sentiment from 12,000+ posts
- Official polling data from 3 countries
- Bias detection across all sources

The analysis maintains high confidence levels while accounting for potential media bias and source reliability variations.`;

    // Split text into chunks for streaming
    const words = analysisText.split(' ');
    const chunkSize = 3; // 3 words per chunk for realistic streaming
    let currentIndex = 0;

    const streamChunk = () => {
      if (currentIndex < words.length) {
        const chunk = words.slice(currentIndex, currentIndex + chunkSize).join(' ') + ' ';
        
        this.emit({
          type: 'token',
          content: chunk,
          index: currentIndex
        });

        currentIndex += chunkSize;
        
        // Random delay between 50-200ms for realistic streaming
        const delay = Math.random() * 150 + 50;
        const timeout = setTimeout(streamChunk, delay);
        this.simulationTimeouts.push(timeout);
      } else {
        // Send completion message with citations
        const timeout = setTimeout(() => {
          this.emit({
            type: 'complete',
            analysis_id: `analysis_${Date.now()}`,
            citations: mockCitations,
            usage: {
              tokens: words.length
            }
          });
        }, 500);
        this.simulationTimeouts.push(timeout);
      }
    };

    // Start streaming after a brief delay
    const initialTimeout = setTimeout(() => {
      streamChunk();
    }, 800);
    this.simulationTimeouts.push(initialTimeout);
  }

  // Simulate connection status
  get readyState() {
    return this.isConnected ? WebSocket.OPEN : WebSocket.CLOSED;
  }
}

export const mockWsService = new MockWebSocketService();
