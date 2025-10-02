import { useState, useEffect, useRef, useCallback } from 'react';
import { useWebSocket, useWebSocketMessage, useWebSocketSend } from '../../hooks/useWebSocket';
import { Message, type MessageData } from './Message';
import { MessageInput } from './MessageInput';
import { ProgressBar } from '../ui/ProgressBar';
import { StatusMessage } from '../ui/StatusMessage';
import type { Citation } from './Citations';
import type { Artifact } from '../artifact/ArtifactPanel';
import type { ServerMessage } from '../../services/WebSocketService';
import './ChatPanel.css';

interface StatusUpdate {
  step: string;
  message: string;
  progress: number;
  timestamp: number;
}

interface ChatPanelProps {
  onArtifactReceived?: (artifact: Artifact) => void;
}

export function ChatPanel({ onArtifactReceived }: ChatPanelProps) {
  const [messages, setMessages] = useState<MessageData[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentAssistantMessage, setCurrentAssistantMessage] = useState('');
  const [currentCitations, setCurrentCitations] = useState<Citation[]>([]);
  const [statusUpdates, setStatusUpdates] = useState<StatusUpdate[]>([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const { isConnected } = useWebSocket();
  const sendMessage = useWebSocketSend();

  // Auto-scroll to bottom - throttled to reduce flickering during streaming
  useEffect(() => {
    // Clear any pending scroll
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }

    // Use requestAnimationFrame for smooth rendering
    scrollTimeoutRef.current = setTimeout(() => {
      requestAnimationFrame(() => {
        if (messagesEndRef.current) {
          // Use 'auto' (instant) during streaming to avoid flicker, 'smooth' for new messages
          const behavior = isStreaming ? 'auto' : 'smooth';
          messagesEndRef.current.scrollIntoView({ behavior, block: 'nearest' });
        }
      });
    }, 50); // Throttle to 50ms

    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [messages, currentAssistantMessage, isStreaming]);

  // Handle session start
  useWebSocketMessage('session_start', useCallback((message: ServerMessage) => {
    console.log('Session started:', message.data);
    const sessionId = message.data.session_id;
    setCurrentSessionId(sessionId); // Capture session ID for execution graph
    setIsStreaming(true);
    setCurrentAssistantMessage('');
    setCurrentCitations([]);
    setStatusUpdates([]);
    setCurrentProgress(0);
  }, []));

  // Handle status updates
  useWebSocketMessage('status', useCallback((message: ServerMessage) => {
    const { step, message: statusMessage, progress } = message.data;
    
    setStatusUpdates((prev) => [
      ...prev,
      {
        step: step || 'processing',
        message: statusMessage || 'Processing...',
        progress: progress || 0,
        timestamp: Date.now(),
      },
    ]);
    
    if (progress !== undefined) {
      setCurrentProgress(progress);
    }
  }, []));

  // Handle streaming content
  useWebSocketMessage('content', useCallback((message: ServerMessage) => {
    const content = message.data.content || '';
    setCurrentAssistantMessage((prev) => prev + content);
  }, []));

  // Handle citations
  useWebSocketMessage('citation', useCallback((message: ServerMessage) => {
    console.log('Citation received:', message.data);
    const citation: Citation = {
      title: message.data.title || 'Untitled',
      url: message.data.url || '',
      snippet: message.data.snippet,
      published_date: message.data.published_date,
      score: message.data.score,
    };
    setCurrentCitations((prev) => [...prev, citation]);
  }, []));

  // Handle artifacts
  useWebSocketMessage('artifact', useCallback((message: ServerMessage) => {
    console.log('Artifact received:', message.data);
    const artifact: Artifact = {
      artifact_id: message.data.artifact_id || '',
      type: message.data.type || 'bar_chart',
      title: message.data.title || 'Visualization',
      description: message.data.description,
      status: message.data.status || 'ready',
      html_url: message.data.html_url,
      png_url: message.data.png_url,
      data_url: message.data.data_url,
      created_at: message.data.created_at || new Date().toISOString(),
      size_bytes: message.data.size_bytes,
    };
    
    // Notify parent component (App) about the artifact
    if (onArtifactReceived) {
      onArtifactReceived(artifact);
    }
  }, [onArtifactReceived]));

  // Handle completion
  useWebSocketMessage('complete', useCallback((message: ServerMessage) => {
    console.log('🎯 Analysis complete handler called:', message.data);
    console.log('   Current assistant message:', currentAssistantMessage ? `${currentAssistantMessage.substring(0, 50)}...` : 'none');
    
    // Add the completed assistant message with citations AND sessionId
    if (currentAssistantMessage) {
      setMessages((prev) => {
        console.log(`   📝 Adding assistant message (prev count: ${prev.length})`);
        return [
          ...prev,
          {
            id: `assistant_${Date.now()}`,
            role: 'assistant',
            content: currentAssistantMessage,
            timestamp: new Date(),
            citations: currentCitations.length > 0 ? currentCitations : undefined,
            sessionId: currentSessionId, // Include session ID for execution graph
          },
        ];
      });
      setCurrentAssistantMessage('');
      setCurrentCitations([]);
    } else {
      console.log('   ⚠️  No currentAssistantMessage to add');
    }
    
    setIsStreaming(false);
    setStatusUpdates([]);
    setCurrentProgress(0);
    setCurrentSessionId(undefined); // Reset for next message
  }, [currentAssistantMessage, currentCitations, currentSessionId]));

  // Handle errors
  useWebSocketMessage('error', useCallback((message: ServerMessage) => {
    console.error('Error:', message.data);
    
    // Add error message
    setMessages((prev) => [
      ...prev,
      {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: `Error: ${message.data.message || 'An error occurred'}`,
        timestamp: new Date(),
      },
    ]);
    
    setIsStreaming(false);
    setCurrentAssistantMessage('');
  }, []));

  const handleSendMessage = (query: string) => {
    if (!query.trim() || !isConnected) {
      console.warn('Cannot send message: empty or not connected');
      return;
    }

    console.log('🚀 handleSendMessage called with query:', query);

    // Add user message to chat
    setMessages((prev) => {
      console.log(`   📝 Adding user message (prev count: ${prev.length})`);
      return [
        ...prev,
        {
          id: `user_${Date.now()}`,
          role: 'user',
          content: query,
          timestamp: new Date(),
        },
      ];
    });

    // Send message to backend via WebSocket
    console.log('   📤 Calling sendMessage to backend');
    const messageId = sendMessage('query', {
      query: query,
      use_citations: true,
    });
    console.log('   ✅ Message sent with ID:', messageId);
  };

  const handleStop = () => {
    // TODO: Implement cancel functionality
    console.log('Stop requested');
    setIsStreaming(false);
  };

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && !currentAssistantMessage && (
          <div className="welcome-message">
            <h2>Welcome to Political Analyst Workbench</h2>
            <p>Ask me about:</p>
                <div className="suggestion-grid">
                  <button className="suggestion-card" onClick={() => handleSendMessage("give me a visualization of india's gdp growth since 2020")}>
                    <span className="suggestion-icon">📊</span>
                    <span className="suggestion-text">India GDP Growth Chart</span>
                  </button>
                  <button className="suggestion-card" onClick={() => handleSendMessage("Analyze the current US political landscape")}>
                    <span className="suggestion-icon">🇺🇸</span>
                    <span className="suggestion-text">US Political Analysis</span>
                  </button>
                  <button className="suggestion-card" onClick={() => handleSendMessage("What's happening in European politics?")}>
                    <span className="suggestion-icon">🇪🇺</span>
                    <span className="suggestion-text">European Politics</span>
                  </button>
                </div>
          </div>
        )}

        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}

        {/* Show streaming message */}
        {currentAssistantMessage && (
          <Message
            message={{
              id: 'streaming',
              role: 'assistant',
              content: currentAssistantMessage,
              timestamp: new Date(),
            }}
          />
        )}

        {/* Show status updates and progress */}
        {isStreaming && statusUpdates.length > 0 && (
          <div className="status-container">
            <ProgressBar 
              progress={currentProgress} 
              message="Processing your query"
              showPercentage={true}
            />
            <div className="status-updates">
              {statusUpdates.slice(-3).map((status, index) => (
                <StatusMessage
                  key={`${status.timestamp}-${index}`}
                  message={status.message}
                  step={status.step}
                  type={index === statusUpdates.slice(-3).length - 1 ? 'loading' : 'complete'}
                />
              ))}
            </div>
          </div>
        )}

        {/* Show "thinking" indicator (fallback if no status updates yet) */}
        {isStreaming && statusUpdates.length === 0 && !currentAssistantMessage && (
          <div className="thinking-indicator">
            <div className="thinking-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className="thinking-text">Analyzing...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={!isConnected}
        isStreaming={isStreaming}
        onStop={handleStop}
      />
    </div>
  );
}
