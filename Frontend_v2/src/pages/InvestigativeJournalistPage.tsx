import React, { useState, useEffect, useRef } from 'react';
import { Send, Download, ExternalLink, Loader2, AlertCircle, StopCircle, FileText } from 'lucide-react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Markdown } from '../components/ui/Markdown';
import { Header } from '../components/layout/Header';
import { InvestigativeJournalistStateViewer } from '../components/InvestigativeJournalistStateViewer';
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
  
  // State viewer - now includes artifact-specific tabs
  const [activeTab, setActiveTab] = useState<'report' | 'network' | 'timeline' | 'evidence' | 'state'>('report');
  const [investigationState, setInvestigationState] = useState<any>(null);
  const [iframeLoading, setIframeLoading] = useState<{[key: string]: boolean}>({
    network: false,
    timeline: false,
    evidence: false
  });
  
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

    // Debug: Log all message types
    console.log(`📨 WebSocket message: ${type}`, { hasData: !!data });

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
        // Display question with better formatting
        const questionText = data.question || data.q || 'New question';
        const hypothesisId = data.hypothesis_id || 'general';
        addSystemMessage(`❓ **Question** (${hypothesisId}): ${questionText}`, 'question');
        break;
      
      case 'question_answered':
        // Display answer when a question gets answered
        const answeredQuestion = data.question || data.q || 'Question';
        const answer = data.answer || data.a || 'Answer found';
        addSystemMessage(`✅ **Answered**: ${answeredQuestion}\n   💡 ${answer}`, 'success');
        break;
      
      case 'strategist_decision':
        // Display the LLM's strategic decision
        const decisionType = data.decision_type || 'N/A';
        const decisionPhase = data.phase || 'unknown';
        const iterNum = data.iteration || '?';
        
        let decisionMsg = `🤖 **Strategist Decision** (Iteration ${iterNum}, Phase: ${decisionPhase})\n`;
        decisionMsg += `   📍 Decision: ${decisionType}\n`;
        
        if (data.question) {
          decisionMsg += `   ❓ Question: ${data.question}\n`;
        }
        
        if (data.novel_angle) {
          decisionMsg += `   💡 Novel Angle: ${data.novel_angle}\n`;
        }
        
        if (decisionType === 'complete' && data.completion_reason) {
          decisionMsg += `   🛑 Reason: ${data.completion_reason}\n`;
        }
        
        if (decisionType === 'search' && data.search_query) {
          decisionMsg += `   🔍 Search Query: ${data.search_query}\n`;
        }
        
        if (decisionType === 'query_local_rag' && data.rag_query) {
          decisionMsg += `   📖 RAG Query: ${data.rag_query}\n`;
        }
        
        addSystemMessage(decisionMsg, 'info');
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

      case 'state_update':
        // Update investigation state for State tab
        // Backend sends the state directly as data, not nested under data.state
        setInvestigationState(data);
        console.log('📊 State update received:', { 
          iteration: data.meta?.iteration,
          facts: data.facts?.length,
          entities: data.entities?.length 
        });
        
        // Show iteration progress in chat
        const iteration = data.meta?.iteration;
        const maxIter = data.meta?.max_iterations;
        const factsCount = data.facts?.length || 0;
        const entitiesCount = data.entities?.length || 0;
        addSystemMessage(
          `📊 Iteration ${iteration}/${maxIter} complete: ${factsCount} facts, ${entitiesCount} entities discovered. Check State tab →`,
          'info'
        );
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
    
    // System messages with different variants based on content
    const content = msg.content.toLowerCase();
    
    // Error messages
    if (content.includes('error') || content.includes('❌')) {
      return 'message message-system message-error';
    }
    
    // Success/completion messages
    if (content.includes('complete') || content.includes('✅') || content.includes('answered')) {
      return 'message message-system message-success';
    }
    
    // Hypothesis messages
    if (content.includes('hypothesis') || content.includes('💡')) {
      return 'message message-system message-hypothesis';
    }
    
    // Question messages
    if (content.includes('question') || content.includes('❓')) {
      return 'message message-system message-question';
    }
    
    // Answer messages (but not "answered" which is success)
    if ((content.includes('**answer') || content.includes('answer:')) && !content.includes('answered')) {
      return 'message message-system message-answer';
    }
    
    // Entity discovered messages
    if (content.includes('entity') || content.includes('👤')) {
      return 'message message-system message-entity';
    }
    
    // Fact messages
    if (content.includes('fact') || content.includes('📌')) {
      return 'message message-system message-fact';
    }
    
    // Strategist decision messages
    if (content.includes('strategist') || content.includes('decision') || content.includes('🤖')) {
      return 'message message-system message-decision';
    }
    
    // Iteration progress messages
    if (content.includes('iteration') && content.includes('complete')) {
      return 'message message-system message-info';
    }
    
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
                  {msg.role === 'assistant' || msg.role === 'system' ? (
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
          {/* Tab Header - Separate tab for each artifact */}
          <div className="artifacts-header">
            <div className="tab-buttons">
              <button 
                className={`tab-button ${activeTab === 'report' ? 'active' : ''}`}
                onClick={() => setActiveTab('report')}
                disabled={!artifacts.find(a => a.type === 'article')}
              >
                📄 Report
                {artifacts.find(a => a.type === 'article') && <span className="tab-badge">✓</span>}
              </button>
              <button 
                className={`tab-button ${activeTab === 'network' ? 'active' : ''}`}
                onClick={() => setActiveTab('network')}
                disabled={!artifacts.find(a => a.name === 'Entity Network Graph')}
              >
                🕸️ Network
                {artifacts.find(a => a.name === 'Entity Network Graph') && <span className="tab-badge">✓</span>}
              </button>
              <button 
                className={`tab-button ${activeTab === 'timeline' ? 'active' : ''}`}
                onClick={() => setActiveTab('timeline')}
                disabled={!artifacts.find(a => a.name === 'Investigation Timeline')}
              >
                📅 Timeline
                {artifacts.find(a => a.name === 'Investigation Timeline') && <span className="tab-badge">✓</span>}
              </button>
              <button 
                className={`tab-button ${activeTab === 'evidence' ? 'active' : ''}`}
                onClick={() => setActiveTab('evidence')}
                disabled={!artifacts.find(a => a.name === 'Evidence Flow Diagram')}
              >
                🔗 Evidence
                {artifacts.find(a => a.name === 'Evidence Flow Diagram') && <span className="tab-badge">✓</span>}
              </button>
              <button 
                className={`tab-button ${activeTab === 'state' ? 'active' : ''}`}
                onClick={() => setActiveTab('state')}
              >
                🔍 State
                {investigationState && <span className="tab-badge">✓</span>}
              </button>
            </div>
          </div>

          {/* Report Tab - Article */}
          {activeTab === 'report' && (
            <div className="artifacts-content">
              {artifacts.filter(a => a.type === 'article' && a.article_text).length === 0 ? (
                <div className="artifacts-empty">
                  <div className="empty-icon">📄</div>
                  <p>Investigation report will appear here when complete</p>
                </div>
              ) : (
                <div className="artifact-full-view">
                  {artifacts.filter(a => a.type === 'article' && a.article_text).map((article) => (
                    <div key={article.id} className="artifact-article-full">
                      <div className="artifact-article-header">
                        <h3>{article.name}</h3>
                        <span className="artifact-timestamp">
                          {article.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="artifact-article-content">
                        <Markdown>
                          {article.article_text || ''}
                        </Markdown>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Network Tab - Entity Network Graph */}
          {activeTab === 'network' && (
            <div className="artifacts-content">
              {!artifacts.find(a => a.name === 'Entity Network Graph') ? (
                <div className="artifacts-empty">
                  <div className="empty-icon">🕸️</div>
                  <p>Entity network will appear here when investigation completes</p>
                </div>
              ) : (
                <div className="artifact-iframe-container">
                  {iframeLoading.network && (
                    <div className="iframe-loading">
                      <Loader2 className="spinner" size={48} />
                      <p>Loading entity network graph...</p>
                    </div>
                  )}
                  {artifacts.filter(a => a.name === 'Entity Network Graph').map((artifact) => (
                    <iframe
                      key={artifact.id}
                      src={artifact.url}
                      title="Entity Network Graph"
                      className="artifact-iframe"
                      style={{ display: iframeLoading.network ? 'none' : 'block' }}
                      onLoad={() => setIframeLoading(prev => ({ ...prev, network: false }))}
                      onLoadStart={() => setIframeLoading(prev => ({ ...prev, network: true }))}
                      sandbox="allow-scripts allow-same-origin allow-downloads"
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Timeline Tab - Investigation Timeline */}
          {activeTab === 'timeline' && (
            <div className="artifacts-content">
              {!artifacts.find(a => a.name === 'Investigation Timeline') ? (
                <div className="artifacts-empty">
                  <div className="empty-icon">📅</div>
                  <p>Timeline will appear here when investigation completes</p>
                </div>
              ) : (
                <div className="artifact-iframe-container">
                  {iframeLoading.timeline && (
                    <div className="iframe-loading">
                      <Loader2 className="spinner" size={48} />
                      <p>Loading investigation timeline...</p>
                    </div>
                  )}
                  {artifacts.filter(a => a.name === 'Investigation Timeline').map((artifact) => (
                    <iframe
                      key={artifact.id}
                      src={artifact.url}
                      title="Investigation Timeline"
                      className="artifact-iframe"
                      style={{ display: iframeLoading.timeline ? 'none' : 'block' }}
                      onLoad={() => setIframeLoading(prev => ({ ...prev, timeline: false }))}
                      sandbox="allow-scripts allow-same-origin allow-downloads"
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Evidence Tab - Evidence Flow Diagram */}
          {activeTab === 'evidence' && (
            <div className="artifacts-content">
              {!artifacts.find(a => a.name === 'Evidence Flow Diagram') ? (
                <div className="artifacts-empty">
                  <div className="empty-icon">🔗</div>
                  <p>Evidence flow will appear here when investigation completes</p>
                </div>
              ) : (
                <div className="artifact-iframe-container">
                  <div className="artifact-explanation">
                    <h4>📖 How to Read This Diagram</h4>
                    <p>
                      This Sankey diagram shows how evidence flows through the investigation:
                    </p>
                    <ul>
                      <li><strong>Investigation</strong> (left) → All evidence gathered</li>
                      <li><strong>Middle section</strong> → Hypotheses being tested</li>
                      <li><strong>Right side</strong> → Status (Proven ✅, Exploring 🔄, Disproven ❌)</li>
                      <li><strong>Flow thickness</strong> → Amount of evidence supporting each path</li>
                    </ul>
                  </div>
                  {iframeLoading.evidence && (
                    <div className="iframe-loading">
                      <Loader2 className="spinner" size={48} />
                      <p>Loading evidence flow diagram...</p>
                    </div>
                  )}
                  {artifacts.filter(a => a.name === 'Evidence Flow Diagram').map((artifact) => (
                    <iframe
                      key={artifact.id}
                      src={artifact.url}
                      title="Evidence Flow Diagram"
                      className="artifact-iframe"
                      style={{ display: iframeLoading.evidence ? 'none' : 'block' }}
                      onLoad={() => setIframeLoading(prev => ({ ...prev, evidence: false }))}
                      sandbox="allow-scripts allow-same-origin allow-downloads"
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* State Tab Content */}
          {activeTab === 'state' && (
            <div className="state-content">
              <InvestigativeJournalistStateViewer state={investigationState} />
            </div>
          )}
        </div>
          </Panel>
        </PanelGroup>
      </div>
      </div>
    </div>
  );
}
