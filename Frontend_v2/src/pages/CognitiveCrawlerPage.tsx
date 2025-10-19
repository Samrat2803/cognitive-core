import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, AlertCircle, Plus, X, Link as LinkIcon, MessageSquare, Search } from 'lucide-react';
import { Markdown } from '../components/ui/Markdown';
import { Header } from '../components/layout/Header';
import './CognitiveCrawlerPage.css';

// Types
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: string[];
  timestamp: Date;
}

interface DBStats {
  total_pages: number;
  total_embeddings: number;
  total_sessions: number;
  unique_domains: number;
}

interface CrawledPage {
  url: string;
  domain: string;
  title: string;
  crawled_at: string;
  content_length: number;
  status: string;
}

type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';
type Mode = 'crawl' | 'chat';

export function CognitiveCrawlerPage() {
  // Mode state - Start with CHAT mode since DB might have existing data
  const [mode, setMode] = useState<Mode>('chat');
  
  // Crawl state
  const [crawlQuery, setCrawlQuery] = useState('');
  const [suggestedDomains, setSuggestedDomains] = useState<string[]>([]);
  const [maxPages, setMaxPages] = useState<number>(20);
  const [maxDepth, setMaxDepth] = useState<number>(2);
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlProgress, setCrawlProgress] = useState({ current: 0, total: 0 });
  const [crawlComplete, setCrawlComplete] = useState(false);
  
  // Database explorer state
  const [dbStats, setDbStats] = useState<DBStats | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [crawledPages, setCrawledPages] = useState<CrawledPage[]>([]);
  const [showExplorer, setShowExplorer] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  
  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Connection state
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [sessionId] = useState<string>(() => `crawler_${Date.now()}`);
  
  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId]);

  // Load database stats when crawl mode is opened
  useEffect(() => {
    if (mode === 'crawl') {
      loadDatabaseStats();
    }
  }, [mode]);

  const loadDatabaseStats = async () => {
    setIsLoadingStats(true);
    try {
      const response = await fetch('http://localhost:8000/api/cognitive_crawler/stats');
      const data = await response.json();
      if (data.success) {
        setDbStats(data.stats);
        setCrawledPages(data.recent_crawls || []);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const searchDatabase = async () => {
    if (!searchTerm.trim()) {
      loadDatabaseStats();
      return;
    }
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/cognitive_crawler/search?q=${encodeURIComponent(searchTerm)}&limit=50`
      );
      const data = await response.json();
      if (data.success) {
        setCrawledPages(data.results || []);
      }
    } catch (error) {
      console.error('Error searching:', error);
    }
  };

  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8000/ws/cognitive_crawler/${sessionId}`;
    console.log('Connecting to:', wsUrl);
    
    setConnectionState('connecting');
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnectionState('connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionState('error');
    };
    
    ws.onclose = () => {
      console.log('WebSocket closed');
      setConnectionState('disconnected');
      // Attempt reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };
    
    wsRef.current = ws;
  };

  const handleWebSocketMessage = (data: any) => {
    console.log('WebSocket message:', data);
    
    switch (data.type) {
      case 'connected':
        addSystemMessage('Connected to Cognitive Crawler. Ready to crawl or chat!');
        break;
      
      case 'crawl_started':
        setIsCrawling(true);
        addSystemMessage(`Crawling ${data.urls?.length || 0} URLs (max ${data.max_pages} pages)...`);
        break;
      
      case 'crawl_complete':
        setIsCrawling(false);
        setCrawlComplete(true);
        // Don't auto-switch - user can manually switch when ready
        addSystemMessage(
          `✅ Crawl complete! ${data.pages_crawled} pages crawled, ${data.embeddings_generated} embeddings generated. Switch to Chat mode to ask questions!`
        );
        break;
      
      case 'chat_started':
        setIsLoading(true);
        break;
      
      case 'chat_answer':
        setIsLoading(false);
        addAssistantMessage(data.answer, data.sources);
        break;
      
      case 'error':
        setIsLoading(false);
        setIsCrawling(false);
        addSystemMessage(`❌ Error: ${data.message}`, true);
        break;
      
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const addSystemMessage = (content: string, isError: boolean = false) => {
    const message: Message = {
      id: `sys_${Date.now()}`,
      role: 'system',
      content: isError ? `⚠️ ${content}` : content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const addAssistantMessage = (content: string, sources?: string[]) => {
    const message: Message = {
      id: `asst_${Date.now()}`,
      role: 'assistant',
      content,
      sources,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const handleCrawl = () => {
    console.log('handleCrawl called', { crawlQuery, wsRef: wsRef.current?.readyState });
    
    if (!crawlQuery.trim()) {
      addSystemMessage('Please enter a search query (e.g., "Python documentation" or "React tutorials")', true);
      return;
    }
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('Sending crawl request:', {
        type: 'crawl',
        query: crawlQuery,
        suggested_domains: suggestedDomains.filter(d => d.trim()),
        max_pages: maxPages,
        max_depth: maxDepth
      });
      
      // Send the query - the agent will use Tavily to discover URLs
      wsRef.current.send(JSON.stringify({
        type: 'crawl',
        query: crawlQuery,
        suggested_domains: suggestedDomains.filter(d => d.trim()),
        max_pages: maxPages,
        max_depth: maxDepth
      }));
      
      addSystemMessage(`🔍 Starting crawl: "${crawlQuery}"`);
    } else {
      console.error('WebSocket not connected. State:', wsRef.current?.readyState);
      addSystemMessage('WebSocket not connected. Reconnecting...', true);
      connectWebSocket();
    }
  };

  const handleChat = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Send to backend
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'chat',
        question: input
      }));
    }
    
    setInput('');
    setIsLoading(true);
  };

  const addDomain = () => {
    setSuggestedDomains([...suggestedDomains, '']);
  };

  const removeDomain = (index: number) => {
    setSuggestedDomains(suggestedDomains.filter((_, i) => i !== index));
  };

  const updateDomain = (index: number, value: string) => {
    const newDomains = [...suggestedDomains];
    newDomains[index] = value;
    setSuggestedDomains(newDomains);
  };

  const resetCrawl = () => {
    setMode('crawl');
    setCrawlComplete(false);
    setCrawlQuery('');
    setSuggestedDomains([]);
    setMessages([]);
  };

  return (
    <div className="cognitive-crawler-page">
      <Header />
      
      <div className="crawler-container">
        {/* Connection Status */}
        <div className={`connection-indicator ${connectionState}`}>
          <div className="status-dot"></div>
          <span>{connectionState === 'connected' ? 'Connected' : connectionState === 'connecting' ? 'Connecting...' : 'Disconnected'}</span>
        </div>

        {/* Mode Tabs */}
        <div className="mode-tabs">
          <button 
            className={`mode-tab ${mode === 'crawl' ? 'active' : ''}`}
            onClick={() => setMode('crawl')}
            disabled={isCrawling}
          >
            <Search className="w-4 h-4" />
            Crawl Websites
          </button>
          <button 
            className={`mode-tab ${mode === 'chat' ? 'active' : ''}`}
            onClick={() => setMode('chat')}
            disabled={isCrawling}
          >
            <MessageSquare className="w-4 h-4" />
            Chat with Data
          </button>
        </div>

        {/* Crawl Mode */}
        {mode === 'crawl' && (
          <div className="crawl-section">
            <div className="section-header">
              <h2>Configure Web Crawl</h2>
              <p>Enter a natural language query - AI will discover relevant URLs automatically</p>
            </div>

            <div className="query-input-section">
              <label>What do you want to crawl?</label>
              <textarea
                value={crawlQuery}
                onChange={(e) => setCrawlQuery(e.target.value)}
                placeholder="E.g., 'Python documentation', 'React tutorials', 'AWS cloud services', 'Tesla company information'"
                className="query-textarea"
                rows={3}
              />
              <span className="query-hint">
                💡 The AI will use Tavily to search the web and discover relevant URLs based on your query
              </span>
            </div>

            <div className="optional-section">
              <div className="optional-header">
                <span>Optional: Suggest specific domains (leave empty for AI to decide)</span>
                {suggestedDomains.length === 0 && (
                  <button onClick={addDomain} className="add-domain-btn-small">
                    <Plus className="w-3 h-3" />
                    Add Domain
                  </button>
                )}
              </div>
              
              {suggestedDomains.length > 0 && (
                <div className="domains-list">
                  {suggestedDomains.map((domain, index) => (
                    <div key={index} className="domain-input-row">
                      <input
                        type="text"
                        value={domain}
                        onChange={(e) => updateDomain(index, e.target.value)}
                        placeholder="e.g., docs.python.org"
                        className="domain-input"
                      />
                      <button onClick={() => removeDomain(index)} className="remove-btn-small">
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                  <button onClick={addDomain} className="add-domain-btn">
                    <Plus className="w-3 h-3" />
                    Add Another
                  </button>
                </div>
              )}
            </div>

            <div className="crawl-settings">
              <div className="setting">
                <label htmlFor="max-pages">Max Pages</label>
                <input
                  id="max-pages"
                  type="number"
                  value={maxPages}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                  min="1"
                  max="100"
                  className="setting-input"
                />
                <span className="setting-hint">Maximum pages to crawl</span>
              </div>

              <div className="setting">
                <label htmlFor="max-depth">Max Depth</label>
                <input
                  id="max-depth"
                  type="number"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(Number(e.target.value))}
                  min="1"
                  max="5"
                  className="setting-input"
                />
                <span className="setting-hint">Link depth (1 = only specified URLs)</span>
              </div>
            </div>

            {/* Database Explorer Section */}
            <div className="db-explorer-section">
              <div className="db-stats-header">
                <h3>Database Explorer</h3>
                <button 
                  onClick={() => setShowExplorer(!showExplorer)}
                  className="toggle-explorer-btn"
                >
                  {showExplorer ? 'Hide' : 'Show'} Database ({dbStats?.total_pages || 0} pages)
                </button>
              </div>

              {dbStats && (
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-value">{dbStats.total_pages}</span>
                    <span className="stat-label">Pages</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value">{dbStats.total_embeddings}</span>
                    <span className="stat-label">Embeddings</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value">{dbStats.unique_domains}</span>
                    <span className="stat-label">Domains</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value">{dbStats.total_sessions}</span>
                    <span className="stat-label">Sessions</span>
                  </div>
                </div>
              )}

              {showExplorer && (
                <div className="explorer-content">
                  <div className="search-bar">
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && searchDatabase()}
                      placeholder="Search URLs or domains..."
                      className="search-input"
                    />
                    <button onClick={searchDatabase} className="search-btn">
                      <Search className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="pages-list">
                    {crawledPages.length > 0 ? (
                      crawledPages.map((page, idx) => (
                        <div key={idx} className="page-item">
                          <div className="page-info">
                            <span className="page-domain">{page.domain}</span>
                            <a href={page.url} target="_blank" rel="noopener noreferrer" className="page-url">
                              {page.url.length > 60 ? page.url.substring(0, 60) + '...' : page.url}
                            </a>
                            <span className="page-meta">
                              {new Date(page.crawled_at).toLocaleDateString()} • {(page.content_length / 1024).toFixed(1)}KB
                            </span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="empty-db">No pages found</div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <button 
              onClick={handleCrawl} 
              disabled={isCrawling || !crawlQuery.trim()}
              className="crawl-btn"
            >
              {isCrawling ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Crawling...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Start Crawling
                </>
              )}
            </button>

            {crawlComplete && (
              <div className="crawl-complete-banner">
                <AlertCircle className="w-5 h-5" />
                <span>Crawl complete! Switch to Chat mode to ask questions.</span>
                <button onClick={resetCrawl} className="reset-btn">
                  Start New Crawl
                </button>
              </div>
            )}
          </div>
        )}

        {/* Chat Mode */}
        {mode === 'chat' && (
          <div className="chat-section">
            <div className="section-header">
              <h2>Chat with Crawled Data</h2>
              <p>Ask questions about any content in the vector database</p>
              <button onClick={() => setMode('crawl')} className="reset-btn-small">
                Crawl More
              </button>
            </div>

            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <MessageSquare className="w-12 h-12 text-gray-400" />
                  <p>Start asking questions about the crawled content in the database!</p>
                  <p className="empty-state-hint">The system will search across all previously crawled data.</p>
                </div>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} className={`message message-${msg.role}`}>
                    <div className="message-content">
                      <Markdown>{msg.content}</Markdown>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="sources">
                          <strong>Sources:</strong>
                          <ul>
                            {msg.sources.map((source, idx) => (
                              <li key={idx}>
                                <a href={source} target="_blank" rel="noopener noreferrer">
                                  {source}
                                </a>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleChat} className="chat-input-form">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleChat(e);
                  }
                }}
                placeholder="Ask a question about the crawled content..."
                className="chat-input"
                disabled={isLoading}
                rows={3}
              />
              <button type="submit" disabled={isLoading || !input.trim()} className="send-btn">
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

