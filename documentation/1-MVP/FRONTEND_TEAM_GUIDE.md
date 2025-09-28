# Frontend Team Implementation Guide

**Version:** 2.0.0  
**Date:** September 2025  
**Team:** Frontend Development  
**Status:** Ready for Implementation  

## 🎯 Frontend Team Objectives (MVP-focused)

Transform the existing React application into a **conversational political analyst interface** featuring:
1. **ChatGPT-Style Chat Interface** - Natural language interaction with the analysis system
2. **Real-time Agent Monitoring** - Live dashboard showing AI agent progress
3. **Interactive Results Explorer** - Progressive disclosure of analysis results
4. **Modern Professional UI** - Linear/GitHub-inspired design system
5. **Export Functionality** - Download reports in multiple formats

## 🚀 Development Principles (MVP)

### **📱 MVP-First Approach**
**Phase 1 MVP:** Basic chat interface with core functionality
- Simple message display (user/assistant bubbles)
- Basic form input and submission
- Static API integration (no WebSocket initially)
- Minimal styling with new color scheme
- Error handling with simple fallbacks

**Phase 2 Features (Post-MVP):** Enhanced user experience
- Real-time WebSocket integration
- Progressive message typing animation
- Interactive results exploration
- Loading states and progress indicators
- Responsive design optimization

**Phase 3 Polish (Post-MVP):** Production-ready enhancements
- Advanced animations and transitions
- Comprehensive error recovery
- Export functionality
- Accessibility features
- Performance optimization

### **🔄 Build on Existing Foundation**
- **Keep current React setup** - Don't change build process or deployment
- **Enhance existing components** - Improve ResearchForm, ResearchResults, etc.
- **Maintain responsive design** - Keep mobile compatibility
- **Preserve accessibility** - Enhance existing a11y features

## 📋 Implementation Checklist

### Phase 1: Project Setup & Design System (Week 1)

#### ✅ Task 1.1: Update Project Dependencies
**Priority:** Critical | **Estimate:** 2 hours

**File to modify:** `frontend/package.json` (MVP minimal additions)
```json
{
  "dependencies": {
    // Existing dependencies remain
    "react": "^18.0.0",
    "typescript": "^4.9.0",
    
    // Add new dependencies (no versions per user rules)
    "zustand": "",
    "react-markdown": "",
    "react-syntax-highlighter": "",
    "recharts": "",
    "date-fns": "",
    "react-hook-form": "",
    "framer-motion": ""
  }
}
```

**Commands to run:**
```bash
cd frontend
npm install
```

**Acceptance Criteria:**
- [ ] All new packages installed successfully
- [ ] No dependency conflicts
- [ ] Package.json updated and committed

---

#### ✅ Task 1.2: Implement Modern Color Scheme (replace Aistra fully)
**Priority:** High | **Estimate:** 3 hours

**File to replace:** `frontend/src/App.css`

```css
/* Modern Professional Color Palette - Linear/GitHub Inspired */
:root {
  /* Light mode colors */
  --primary-blue: #2563eb;
  --primary-blue-light: #3b82f6;
  --primary-blue-hover: #1d4ed8;
  --secondary-gray: #6b7280;
  --background-white: #ffffff;
  --background-gray: #f9fafb;
  --background-secondary: #f3f4f6;
  --border-gray: #e5e7eb;
  --border-light: #d1d5db;
  --text-dark: #111827;
  --text-medium: #374151;
  --text-light: #6b7280;
  --success-green: #10b981;
  --warning-amber: #f59e0b;
  --error-red: #ef4444;

  /* Dark mode colors */
  --dark-bg-primary: #0f1419;
  --dark-bg-secondary: #1c2128;
  --dark-bg-tertiary: #21262d;
  --dark-bg-elevated: #2d333b;
  --dark-border: #30363d;
  --dark-border-light: #373e47;
  --dark-text-primary: #f0f6fc;
  --dark-text-secondary: #c9d1d9;
  --dark-text-muted: #8b949e;
  --dark-accent-blue: #58a6ff;
  --dark-accent-blue-hover: #79c0ff;

  /* Semantic colors */
  --chat-bg: var(--background-white);
  --chat-border: var(--border-gray);
  --message-user-bg: var(--primary-blue);
  --message-assistant-bg: var(--background-secondary);
  --code-bg: var(--background-gray);
}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  :root {
    --chat-bg: var(--dark-bg-secondary);
    --chat-border: var(--dark-border);
    --message-user-bg: var(--dark-accent-blue);
    --message-assistant-bg: var(--dark-bg-tertiary);
    --code-bg: var(--dark-bg-primary);
  }
}

/* Base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--background-white);
  color: var(--text-dark);
  line-height: 1.6;
  min-height: 100vh;
}

@media (prefers-color-scheme: dark) {
  body {
    background-color: var(--dark-bg-primary);
    color: var(--dark-text-primary);
  }
}

/* Application layout */
.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Container styles */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  width: 100%;
}

/* Button styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background-color: var(--primary-blue);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-blue-hover);
}

.btn-secondary {
  background-color: transparent;
  color: var(--text-medium);
  border: 1px solid var(--border-gray);
}

.btn-secondary:hover {
  background-color: var(--background-gray);
}

@media (prefers-color-scheme: dark) {
  .btn-primary {
    background-color: var(--dark-accent-blue);
  }
  
  .btn-primary:hover {
    background-color: var(--dark-accent-blue-hover);
  }
  
  .btn-secondary {
    color: var(--dark-text-secondary);
    border-color: var(--dark-border);
  }
  
  .btn-secondary:hover {
    background-color: var(--dark-bg-tertiary);
  }
}

/* Input styles */
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-gray);
  border-radius: 8px;
  background-color: var(--background-white);
  color: var(--text-dark);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

@media (prefers-color-scheme: dark) {
  .input {
    border-color: var(--dark-border);
    background-color: var(--dark-bg-tertiary);
    color: var(--dark-text-primary);
  }
  
  .input:focus {
    border-color: var(--dark-accent-blue);
    box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
  }
}

/* Card styles */
.card {
  background-color: var(--background-white);
  border: 1px solid var(--border-gray);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.card:hover {
  border-color: var(--border-light);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

@media (prefers-color-scheme: dark) {
  .card {
    background-color: var(--dark-bg-secondary);
    border-color: var(--dark-border);
  }
  
  .card:hover {
    border-color: var(--dark-border-light);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
}

/* Status indicators */
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-processing {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--warning-amber);
}

.status-completed {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--success-green);
}

.status-error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--error-red);
}

/* Responsive design */
@media (max-width: 768px) {
  .container {
    padding: 0 0.75rem;
  }
  
  .btn {
    padding: 0.625rem 0.875rem;
    font-size: 0.8125rem;
  }
}

/* Loading animations */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--border-gray);
  border-top: 2px solid var(--primary-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@media (prefers-color-scheme: dark) {
  .loading-spinner {
    border-color: var(--dark-border);
    border-top-color: var(--dark-accent-blue);
  }
}
```

**Acceptance Criteria:**
- [ ] Modern color scheme applied throughout
- [ ] Dark mode support implemented
- [ ] Professional Linear/GitHub-inspired design
- [ ] Responsive design maintained
- [ ] All existing components updated

---

#### ✅ Task 1.3: Create New Component Structure
**Priority:** High | **Estimate:** 2 hours

**Commands to run:**
```bash
cd frontend/src

# Create new component directories
mkdir -p components/chat
mkdir -p components/monitoring  
mkdir -p components/results
mkdir -p components/export
mkdir -p components/ui

# Create new hook directories
mkdir -p hooks
mkdir -p services
mkdir -p stores
mkdir -p types
mkdir -p utils

# Create component files
touch components/chat/ChatInterface.tsx
touch components/chat/ChatMessage.tsx
touch components/chat/ChatInput.tsx
touch components/monitoring/AnalysisMonitor.tsx
touch components/monitoring/ProgressIndicator.tsx
touch components/results/ResultsExplorer.tsx
touch components/results/CountryResults.tsx
touch components/results/BiasAnalysis.tsx
touch components/export/ExportDialog.tsx
touch components/ui/Button.tsx
touch components/ui/Card.tsx
touch components/ui/StatusBadge.tsx

# Create hooks
touch hooks/useWebSocket.ts
touch hooks/useChat.ts
touch hooks/useAnalysis.ts

# Create services
touch services/apiService.ts
touch services/websocketService.ts

# Create stores
touch stores/chatStore.ts
touch stores/analysisStore.ts

# Create types
touch types/analysis.ts
touch types/chat.ts
touch types/api.ts
```

**Acceptance Criteria:**
- [ ] All component directories created
- [ ] All placeholder files created
- [ ] Project structure organized logically
- [ ] No build errors

---

### Phase 2: Chat Interface Implementation (Week 2)

#### ✅ Task 2.1: WebSocket Hook (MVP)
**Priority:** Critical | **Estimate:** 4 hours

**📱 MVP Implementation Strategy:**
- **Phase 1:** Basic connection/disconnection (ping/pong only)
- **Phase 2:** Message handling and auto-reconnection
- **Phase 3:** Advanced features like connection pooling, heartbeat monitoring

**File to create:** `frontend/src/hooks/useWebSocket.ts`

```typescript
import { useState, useEffect, useRef, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (message: any) => void;
  connect: (sessionId: string) => void;
  disconnect: () => void;
  lastMessage: WebSocketMessage | null;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const {
    onMessage,
    onError,
    onConnect,
    onDisconnect,
    reconnectAttempts = 5,
    reconnectDelay = 3000
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const sessionIdRef = useRef<string | null>(null);

  const getWebSocketUrl = (sessionId: string): string => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    if (process.env.NODE_ENV === 'development') {
      return `ws://localhost:8000/ws/${sessionId}`;
    }
    
    // Production WebSocket URL (your actual backend)
    return `ws://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/ws/${sessionId}`;
  };

  const connect = useCallback((sessionId: string) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    sessionIdRef.current = sessionId;
    const wsUrl = getWebSocketUrl(sessionId);
    
    try {
      const ws = new WebSocket(wsUrl);
      websocketRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        onDisconnect?.();
        
        // Attempt to reconnect
        if (reconnectAttemptsRef.current < reconnectAttempts) {
          reconnectAttemptsRef.current++;
          setTimeout(() => {
            if (sessionIdRef.current) {
              connect(sessionIdRef.current);
            }
          }, reconnectDelay);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [onMessage, onError, onConnect, onDisconnect, reconnectAttempts, reconnectDelay]);

  const disconnect = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    sendMessage,
    connect,
    disconnect,
    lastMessage
  };
};
```

**Acceptance Criteria:**
- [ ] WebSocket connection established successfully
- [ ] Automatic reconnection working
- [ ] Message parsing and handling correct
- [ ] Error handling implemented
- [ ] Connection status tracking accurate

---

#### ✅ Task 2.2: Chat Store (State Management)
**Priority:** High | **Estimate:** 3 hours

**File to create:** `frontend/src/stores/chatStore.ts`

```typescript
import { create } from 'zustand';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    analysisId?: string;
    intent?: any;
    confirmationRequired?: boolean;
  };
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  currentAnalysisId?: string;
  isWaitingForConfirmation?: boolean;
  createdAt: Date;
}

interface ChatStore {
  // State
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  isLoading: boolean;
  error: string | null;

  // Actions
  startNewSession: () => void;
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  setCurrentAnalysisId: (analysisId: string | undefined) => void;
  setWaitingForConfirmation: (waiting: boolean) => void;
  
  // Session management
  loadSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  clearSessions: () => void;
}

const generateId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const useChatStore = create<ChatStore>((set, get) => ({
  // Initial state
  currentSession: null,
  sessions: [],
  isLoading: false,
  error: null,

  // Actions
  startNewSession: () => {
    const newSession: ChatSession = {
      id: generateSessionId(),
      messages: [
        {
          id: generateId(),
          type: 'assistant',
          content: "Hello! I'm your Political Intelligence Analyst. I can help you analyze geopolitical sentiment across different countries. Try asking something like 'Analyze Hamas sentiment' or 'Compare US and Iran views on Israel'.",
          timestamp: new Date()
        }
      ],
      createdAt: new Date()
    };

    set((state) => ({
      currentSession: newSession,
      sessions: [newSession, ...state.sessions],
      error: null
    }));
  },

  addMessage: (messageData) => {
    const message: ChatMessage = {
      ...messageData,
      id: generateId(),
      timestamp: new Date()
    };

    set((state) => {
      if (!state.currentSession) {
        // Create new session if none exists
        const newSession: ChatSession = {
          id: generateSessionId(),
          messages: [message],
          createdAt: new Date()
        };
        return {
          currentSession: newSession,
          sessions: [newSession, ...state.sessions]
        };
      }

      // Add to current session
      const updatedSession = {
        ...state.currentSession,
        messages: [...state.currentSession.messages, message]
      };

      return {
        currentSession: updatedSession,
        sessions: state.sessions.map(session => 
          session.id === updatedSession.id ? updatedSession : session
        )
      };
    });
  },

  updateMessage: (messageId, updates) => {
    set((state) => {
      if (!state.currentSession) return state;

      const updatedSession = {
        ...state.currentSession,
        messages: state.currentSession.messages.map(msg =>
          msg.id === messageId ? { ...msg, ...updates } : msg
        )
      };

      return {
        currentSession: updatedSession,
        sessions: state.sessions.map(session =>
          session.id === updatedSession.id ? updatedSession : session
        )
      };
    });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setError: (error) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentAnalysisId: (analysisId) => {
    set((state) => {
      if (!state.currentSession) return state;
      
      return {
        currentSession: {
          ...state.currentSession,
          currentAnalysisId: analysisId
        }
      };
    });
  },

  setWaitingForConfirmation: (waiting) => {
    set((state) => {
      if (!state.currentSession) return state;
      
      return {
        currentSession: {
          ...state.currentSession,
          isWaitingForConfirmation: waiting
        }
      };
    });
  },

  loadSession: (sessionId) => {
    const session = get().sessions.find(s => s.id === sessionId);
    if (session) {
      set({ currentSession: session });
    }
  },

  deleteSession: (sessionId) => {
    set((state) => ({
      sessions: state.sessions.filter(s => s.id !== sessionId),
      currentSession: state.currentSession?.id === sessionId ? null : state.currentSession
    }));
  },

  clearSessions: () => {
    set({
      sessions: [],
      currentSession: null
    });
  }
}));
```

**Acceptance Criteria:**
- [ ] Chat state management working correctly
- [ ] Message persistence across sessions
- [ ] Session management functional
- [ ] Loading and error states handled
- [ ] TypeScript types properly defined

---

#### ✅ Task 2.3: Chat Interface Components
**Priority:** High | **Estimate:** 6 hours

**📱 MVP Implementation Strategy:**
- **Phase 1:** Basic message bubbles using existing UI patterns
- **Phase 2:** Add WebSocket integration (build on existing API service)
- **Phase 3:** Advanced features like typing indicators, message reactions

**🔄 Build on Existing Code:**
- Use existing `ResearchForm` patterns for input handling
- Adapt existing `ResearchResults` styling for message display
- Leverage existing error handling from current components

**File to create:** `frontend/src/components/chat/ChatInterface.tsx`

```typescript
import React, { useEffect, useRef } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import './ChatInterface.css';

export const ChatInterface: React.FC = () => {
  const {
    currentSession,
    isLoading,
    error,
    startNewSession,
    addMessage,
    setLoading,
    setError,
    clearError
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { isConnected, sendMessage, connect } = useWebSocket({
    onMessage: (message) => {
      console.log('WebSocket message:', message);
      
      if (message.type === 'analysis_progress') {
        // Handle progress updates
        addMessage({
          type: 'system',
          content: `Analysis Progress: ${message.progress?.message || 'Processing...'}`,
          metadata: { analysisId: message.analysis_id }
        });
      } else if (message.type === 'analysis_complete') {
        // Handle completion
        addMessage({
          type: 'assistant',
          content: 'Analysis completed! You can view the results below.',
          metadata: { analysisId: message.analysis_id }
        });
      } else if (message.type === 'analysis_error') {
        // Handle errors
        addMessage({
          type: 'system', 
          content: `Error: ${message.error?.message || 'Analysis failed'}`,
        });
      }
    },
    onConnect: () => {
      console.log('WebSocket connected');
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected');
    }
  });

  // Initialize session
  useEffect(() => {
    if (!currentSession) {
      startNewSession();
    }
  }, [currentSession, startNewSession]);

  // Connect WebSocket when session starts
  useEffect(() => {
    if (currentSession && !isConnected) {
      connect(currentSession.id);
    }
  }, [currentSession, isConnected, connect]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentSession?.messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Add user message
    addMessage({
      type: 'user',
      content
    });

    setLoading(true);
    clearError();

    try {
      // Send to backend
      const response = await fetch('/api/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          message: content,
          session_id: currentSession?.id
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.response_type === 'query_parsed') {
        // Show confirmation message
        addMessage({
          type: 'assistant',
          content: result.confirmation,
          metadata: {
            analysisId: result.analysis_id,
            intent: result.parsed_intent,
            confirmationRequired: true
          }
        });
      } else {
        // Direct response
        addMessage({
          type: 'assistant',
          content: result.message
        });
      }

    } catch (error) {
      console.error('Chat error:', error);
      setError(error instanceof Error ? error.message : 'Failed to send message');
      
      addMessage({
        type: 'system',
        content: 'Sorry, I encountered an error. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmAnalysis = async (analysisId: string, confirmed: boolean) => {
    if (!confirmed) {
      addMessage({
        type: 'assistant',
        content: 'Analysis cancelled. What else would you like to explore?'
      });
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/chat/confirm-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          analysis_id: analysisId,
          confirmed: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      addMessage({
        type: 'assistant', 
        content: 'Great! Starting the analysis now. I\'ll keep you updated with real-time progress.',
        metadata: { analysisId: result.analysis_id }
      });

    } catch (error) {
      console.error('Confirmation error:', error);
      setError(error instanceof Error ? error.message : 'Failed to confirm analysis');
    } finally {
      setLoading(false);
    }
  };

  if (!currentSession) {
    return (
      <div className="chat-interface loading">
        <div className="loading-spinner"></div>
        <p>Initializing chat session...</p>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Political Intelligence Chat</h2>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
        </div>
      </div>

      <div className="chat-messages">
        {currentSession.messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onConfirmAnalysis={handleConfirmAnalysis}
          />
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-content">
              <div className="loading-spinner"></div>
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-error">
          <p>{error}</p>
          <button onClick={clearError} className="btn-secondary">
            Dismiss
          </button>
        </div>
      )}

      <ChatInput 
        onSendMessage={handleSendMessage}
        disabled={isLoading}
        placeholder="Ask me about geopolitical sentiment analysis..."
      />
    </div>
  );
};
```

**File to create:** `frontend/src/components/chat/ChatInterface.css`

```css
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100vh;
  background: var(--chat-bg);
  border: 1px solid var(--chat-border);
  border-radius: 12px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--chat-border);
  background: var(--background-white);
}

@media (prefers-color-scheme: dark) {
  .chat-header {
    background: var(--dark-bg-secondary);
    border-bottom-color: var(--dark-border);
  }
}

.chat-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-dark);
}

@media (prefers-color-scheme: dark) {
  .chat-header h2 {
    color: var(--dark-text-primary);
  }
}

.connection-status {
  font-size: 0.875rem;
}

.status-indicator.connected {
  color: var(--success-green);
}

.status-indicator.disconnected {
  color: var(--error-red);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  align-items: flex-end;
}

.message.assistant,
.message.system {
  align-self: flex-start;
  align-items: flex-start;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-size: 0.9375rem;
  line-height: 1.5;
  word-wrap: break-word;
}

.message.user .message-content {
  background: var(--message-user-bg);
  color: white;
}

.message.assistant .message-content {
  background: var(--message-assistant-bg);
  color: var(--text-dark);
  border: 1px solid var(--border-gray);
}

.message.system .message-content {
  background: var(--background-gray);
  color: var(--text-medium);
  font-style: italic;
  border: 1px solid var(--border-gray);
}

@media (prefers-color-scheme: dark) {
  .message.assistant .message-content {
    color: var(--dark-text-primary);
    border-color: var(--dark-border);
  }
  
  .message.system .message-content {
    color: var(--dark-text-secondary);
    border-color: var(--dark-border);
  }
}

.message-timestamp {
  font-size: 0.75rem;
  color: var(--text-light);
  margin-top: 0.25rem;
}

@media (prefers-color-scheme: dark) {
  .message-timestamp {
    color: var(--dark-text-muted);
  }
}

.chat-error {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid var(--error-red);
  color: var(--error-red);
  font-size: 0.875rem;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-medium);
}

@media (prefers-color-scheme: dark) {
  .loading {
    color: var(--dark-text-secondary);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .message {
    max-width: 90%;
  }
  
  .chat-header {
    padding: 0.75rem 1rem;
  }
  
  .chat-messages {
    padding: 0.75rem;
  }
}
```

**Acceptance Criteria:**
- [ ] Chat interface renders correctly
- [ ] Messages display in proper order
- [ ] WebSocket integration working
- [ ] Real-time updates functional
- [ ] Responsive design implemented
- [ ] Error handling working
- [ ] Loading states displayed

---

**Status Update Required:**
After completing each task, update your status:

```bash
# Example status update
echo "✅ Task 1.1: Dependencies updated - COMPLETED" >> frontend_team_status.md
echo "🔄 Task 1.2: Color scheme - IN PROGRESS" >> frontend_team_status.md
```

**Next Phase:** Analysis monitoring components and results explorer.

**Questions/Blockers:** Report any issues immediately in the team communication channel.

**Integration Notes:**
- Backend must provide WebSocket endpoint at `/ws/{session_id}`
- API endpoints must match the contract specification
- Authentication tokens must be properly validated
