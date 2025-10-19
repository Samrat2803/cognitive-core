import React, { useState, useEffect, useRef } from 'react';
import { Send, Download, ExternalLink, Loader2, AlertCircle, StopCircle, FileText } from 'lucide-react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Markdown } from '../components/ui/Markdown';
import { Header } from '../components/layout/Header';
import './InvestigativeJournalistPage.css';

// Message types
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

// Artifact types
interface Artifact {
  id: string;
  type: 'pdf' | 'image' | 'html' | 'json' | 'text' | 'article';
  name: string;
  url: string;
  timestamp: Date;
  article_text?: string; // For article type artifacts
}

// WebSocket connection state
type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

export function InvestigativeJournalistPage() {
  // State - ONLY 6 variables (vs 23 before!)
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [investigationId, setInvestigationId] = useState<string | null>(null);
  
  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // WebSocket connection
  useEffect(() => {
    // Guard: Prevent duplicate connections in React StrictMode (dev mode)
    if (wsRef.current?.readyState === WebSocket.CONNECTING || 
        wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connecting/connected, skipping duplicate connection');
      return;
    }
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    setConnectionState('connecting');
    
    const ws = new WebSocket('ws://localhost:8000/ws/chat');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnectionState('connected');
      // Only show message if we previously had messages (i.e., reconnecting)
      if (messages.length > 0) {
        addSystemMessage('Reconnected to investigator agent 🚀', 'success');
      }
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleWebSocketMessage(msg);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionState('error');
      // Only show error if we had an active connection before
      if (messages.length > 0) {
        addSystemMessage('Connection error ❌', 'error');
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnectionState('disconnected');
      
      // Only show disconnect message if we had an active connection
      if (messages.length > 0) {
        addSystemMessage('Disconnected from server. Reconnecting...', 'warning');
      }
      
      // Auto-reconnect after 3 seconds
      setTimeout(() => {
        if (wsRef.current?.readyState !== WebSocket.OPEN) {
          connectWebSocket();
        }
      }, 3000);
    };
  };

  const handleWebSocketMessage = (msg: any) => {
    const { type, data } = msg;

    switch (type) {
      case 'connected':
        addSystemMessage('Ready to investigate! Type a query to begin.', 'success');
        break;

      case 'investigation_started':
        setInvestigationId(data.investigation_id);
        addSystemMessage(`🔬 Investigation started: "${data.query}"`, 'info');
        setIsLoading(true);
        break;

      case 'log':
        // Show logs as system messages in the chat
        addSystemMessage(data.message, 'info');
        break;

      case 'hypothesis_updated':
        addSystemMessage(`💡 Hypothesis: ${data.statement}`, 'hypothesis');
        break;

      case 'question_discovered':
        addSystemMessage(`❓ Question: ${data.question}`, 'question');
        break;

      case 'entity_discovered':
        addSystemMessage(`👤 Entity discovered: ${data.name} (${data.type})`, 'entity');
        break;

      case 'fact_recorded':
        addSystemMessage(`📌 Fact: ${data.content}`, 'fact');
        break;

      case 'artifact':
        // Add artifact to artifacts panel
        let artifactUrl = data.url || data.html_url || data.s3_html_url;
        
        // For article type, create a data URL from the article text
        if (data.type === 'article' && data.article_text && !artifactUrl) {
          const blob = new Blob([data.article_text], { type: 'text/markdown' });
          artifactUrl = URL.createObjectURL(blob);
        }
        
        const artifactToAdd: Artifact = {
          id: data.artifact_id || data.id,
          type: data.type || 'html',
          name: data.title || data.name || 'Artifact',
          url: artifactUrl || '#',
          timestamp: new Date(),
          article_text: data.type === 'article' ? data.article_text : undefined
        };
        
        addArtifact(artifactToAdd);
        
        // For article type, show simple message in chat
        if (data.type === 'article') {
          addSystemMessage(`📄 Investigation report generated`, 'success');
        } else {
          addSystemMessage(`📄 Generated artifact: ${artifactToAdd.name}`, 'success');
        }
        break;

      case 'article_updated':
        // Create artifact for article
        if (data.article) {
          addArtifact({
            id: `article_${Date.now()}`,
            type: 'text',
            name: 'Investigation Report',
            url: '#', // Will be handled differently (show in modal or side panel)
            timestamp: new Date()
          });
        }
        break;

      case 'investigation_complete':
        setIsLoading(false);
        const cost = data.total_cost || data.cost || 0;
        addSystemMessage(`✅ Investigation complete! Cost: $${cost.toFixed(3)}`, 'success');
        
        // Don't show the full article in chat - it's already in artifacts panel
        // Just show a completion message
        break;

      case 'error':
        setIsLoading(false);
        addSystemMessage(`❌ Error: ${data.message || 'Unknown error'}`, 'error');
        break;

      default:
        // Handle any other message types
        if (data.message) {
          addSystemMessage(data.message, 'info');
        }
    }
  };

  const addSystemMessage = (content: string, variant: string = 'info') => {
    setMessages(prev => [...prev, {
      id: Date.now().toString() + Math.random(),
      role: 'system',
      content: content,
      timestamp: new Date()
    }]);
  };

  const addAssistantMessage = (content: string) => {
    setMessages(prev => [...prev, {
      id: Date.now().toString() + Math.random(),
      role: 'assistant',
      content: content,
      timestamp: new Date()
    }]);
  };

  const addArtifact = (artifact: Artifact) => {
    setArtifacts(prev => [...prev, artifact]);
  };

  const sendMessage = () => {
    if (!input.trim() || connectionState !== 'connected') return;

    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Send to backend
    wsRef.current?.send(JSON.stringify({
      type: 'message',
      content: input,
      investigation_id: investigationId // Include if continuing investigation
    }));

    setInput('');
    setIsLoading(true);
    
    // Focus back on input
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleStop = () => {
    if (wsRef.current && isLoading) {
      // Send stop command to backend
      wsRef.current.send(JSON.stringify({ type: 'stop_investigation' }));
      setIsLoading(false);
      addSystemMessage('⏹️ Investigation stopped by user', 'warning');
    }
  };

  const getArtifactIcon = (type: string) => {
    switch (type) {
      case 'pdf': return '📄';
      case 'image': return '📊';
      case 'html': return '📈';
      case 'json': return '📋';
      default: return '📄';
    }
  };

  const getMessageClassName = (msg: Message) => {
    if (msg.role === 'user') return 'message message-user';
    if (msg.role === 'assistant') return 'message message-assistant';
    
    // System messages with different variants
    const content = msg.content.toLowerCase();
    if (content.includes('error') || content.includes('❌')) return 'message message-system message-error';
    if (content.includes('complete') || content.includes('✅')) return 'message message-system message-success';
    if (content.includes('💡')) return 'message message-system message-hypothesis';
    if (content.includes('❓')) return 'message message-system message-question';
    
    return 'message message-system';
  };

  return (
    <div className="chat-page">
      {/* Header */}
      <Header />
      
      <div className="chat-page-content">
      {/* Main Content with Resizable Panels */}
      <div className="chat-content">
        <PanelGroup direction="horizontal">
          {/* Chat Panel (Left) */}
          <Panel 
            defaultSize={60} 
            minSize={30}
          >
        {/* Chat Panel (Left/Center) */}
        <div className="chat-panel">
          <div className="messages-container">
            {messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">💬</div>
                <h2>Start a Conversation</h2>
                <p>Type a query to begin your investigation</p>
                <div className="example-queries">
                  <div className="example-label">Try asking:</div>
                  <button onClick={() => setInput('Investigate recent developments in quantum computing for 3 iterations')}>
                    "Investigate recent developments in quantum computing for 3 iterations"
                  </button>
                  <button onClick={() => setInput('Research SpaceX Starship progress 5 iterations')}>
                    "Research SpaceX Starship progress 5 iterations"
                  </button>
                  <button onClick={() => setInput('Analyze recent AI breakthroughs')}>
                    "Analyze recent AI breakthroughs" (default: 5 iterations)
                  </button>
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={getMessageClassName(msg)}>
                <div className="message-content">
                  {msg.role === 'assistant' ? (
                    <Markdown>{msg.content}</Markdown>
                  ) : (
                    <div>{msg.content}</div>
                  )}
                </div>
                <div className="message-timestamp">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message message-system message-loading">
                <div className="message-content">
                  <Loader2 className="spinner" size={16} />
                  <span>Investigating...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="input-container">
            {connectionState !== 'connected' && (
              <div className="input-warning">
                <AlertCircle size={16} />
                <span>Not connected to server</span>
              </div>
            )}
            <div className="input-area">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your investigation query..."
                disabled={connectionState !== 'connected'}
                rows={1}
              />
              <div className="button-group">
                {isLoading && (
                  <button 
                    onClick={handleStop} 
                    className="stop-button"
                    title="Stop investigation"
                  >
                    <StopCircle size={20} />
                  </button>
                )}
                <button 
                  onClick={sendMessage} 
                  disabled={!input.trim() || connectionState !== 'connected'}
                  className="send-button"
                  title={isLoading ? "Send will interrupt and modify investigation" : "Send message"}
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
          </div>
        </div>
          </Panel>

          {/* Resize Handle */}
          <PanelResizeHandle className="resize-handle">
            <div className="resize-handle-line" />
          </PanelResizeHandle>

          {/* Artifacts Panel (Right) - Always visible */}
          <Panel 
            defaultSize={40} 
            minSize={20}
            collapsible
          >
        {/* Artifacts Panel (Right) */}
        <div className="artifacts-panel">
          <div className="artifacts-header">
            <h3>📦 Artifacts</h3>
            <span className="artifacts-count">{artifacts.length}</span>
          </div>

          <div className="artifacts-content">
            {artifacts.length === 0 ? (
              <div className="artifacts-empty">
                <div className="empty-icon">📄</div>
                <p>Artifacts will appear here as they are generated</p>
              </div>
            ) : (
              <>
                {/* Show all article artifacts as list */}
                {artifacts.filter(a => a.type === 'article' && a.article_text).length > 0 ? (
                  <div className="artifact-articles-list">
                    <h4 className="artifact-section-title">Investigation Reports</h4>
                    {artifacts.filter(a => a.type === 'article' && a.article_text).map((article) => (
                      <details key={article.id} className="artifact-article-collapsible" open={artifacts.filter(a => a.type === 'article').length === 1}>
                        <summary className="artifact-article-summary">
                          <div className="artifact-article-title">
                            <FileText size={16} />
                            <span>{article.name}</span>
                          </div>
                          <div className="artifact-article-meta">
                            <span className="artifact-timestamp">
                              {article.timestamp.toLocaleTimeString()}
                            </span>
                            <button
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                if (article.url) {
                                  window.open(article.url, '_blank');
                                }
                              }}
                              className="artifact-button-small"
                              title="Download"
                            >
                              <Download size={14} />
                            </button>
                          </div>
                        </summary>
                        <div className="artifact-article-content">
                          <Markdown>
                            {article.article_text || ''}
                          </Markdown>
                        </div>
                      </details>
                    ))}
                  </div>
                ) : null}
                
                {/* Show list of non-article artifacts */}
                {artifacts.filter(a => a.type !== 'article').length > 0 && (
                  <div className="artifacts-list">
                    <h4 className="artifact-section-title">Other Artifacts</h4>
                    {artifacts.filter(a => a.type !== 'article').map((artifact) => (
                      <div key={artifact.id} className="artifact-card">
                        <div className="artifact-icon">
                          {getArtifactIcon(artifact.type)}
                        </div>
                        <div className="artifact-info">
                          <div className="artifact-name">{artifact.name}</div>
                          <div className="artifact-timestamp">
                            {artifact.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                        <div className="artifact-actions">
                          <a
                            href={artifact.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="artifact-button"
                            title="View"
                          >
                            <ExternalLink size={16} />
                          </a>
                          <a
                            href={artifact.url}
                            download={artifact.name}
                            className="artifact-button"
                            title="Download"
                          >
                            <Download size={16} />
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
          </Panel>
        </PanelGroup>
      </div>
      </div>
    </div>
  );
}
