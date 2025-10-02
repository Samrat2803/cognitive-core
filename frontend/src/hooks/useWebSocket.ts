import { useState, useEffect, useCallback, useRef } from 'react';
import { StreamingMessage, ChatMessage } from '../types';
import { WS } from '../api/endpoints';
import { API_CONFIG } from '../config';
import { MockWebSocketService } from '../services/mockWebSocket';

interface UseWebSocketOptions {
  onMessage?: (message: StreamingMessage) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  connect: (sessionId: string) => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  lastMessage: StreamingMessage | null;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<StreamingMessage | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const sessionIdRef = useRef<string | null>(null);

  const {
    onMessage,
    onError,
    onConnect,
    onDisconnect,
    reconnectAttempts = 5,
    reconnectInterval = 1000
  } = options;

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  const startHeartbeat = useCallback(() => {
    cleanup();
    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'pong' }));
      }
    }, 30000);
  }, [cleanup]);

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: StreamingMessage = JSON.parse(event.data);
      setLastMessage(message);
      
      // Handle ping/pong
      if (message.type === 'ping') {
        wsRef.current?.send(JSON.stringify({ type: 'pong' }));
        return;
      }
      
      onMessage?.(message);
    } catch (err) {
      console.warn('Failed to parse WebSocket message:', event.data);
    }
  }, [onMessage]);

  const handleError = useCallback((event: Event) => {
    setError('WebSocket connection error');
    onError?.(event);
  }, [onError]);

  const handleClose = useCallback(() => {
    setIsConnected(false);
    setIsConnecting(false);
    cleanup();
    onDisconnect?.();

    // Attempt reconnection if we have a session ID and haven't exceeded attempts
    if (sessionIdRef.current && reconnectAttemptsRef.current < reconnectAttempts) {
      const delay = Math.min(
        reconnectInterval * Math.pow(2, reconnectAttemptsRef.current),
        30000
      );
      
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectAttemptsRef.current++;
        connect(sessionIdRef.current!);
      }, delay);
    }
  }, [cleanup, onDisconnect, reconnectAttempts, reconnectInterval]);

  const connect = useCallback((sessionId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);
    setError(null);
    sessionIdRef.current = sessionId;

    try {
      if (API_CONFIG.useMockBackend) {
        // Use mock WebSocket service
        const mockWs = new MockWebSocketService();
        wsRef.current = mockWs as any; // Type assertion for compatibility
        
        mockWs.connect(sessionId);
        mockWs.on((message: StreamingMessage) => handleMessage({ data: JSON.stringify(message) } as MessageEvent));
        
        // Simulate connection success
        setTimeout(() => {
          setIsConnected(true);
          setIsConnecting(false);
          setError(null);
          reconnectAttemptsRef.current = 0;
          onConnect?.();
        }, 200);
        
      } else {
        // Use real WebSocket
        const wsUrl = WS.session(sessionId);
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          setIsConnected(true);
          setIsConnecting(false);
          setError(null);
          reconnectAttemptsRef.current = 0;
          startHeartbeat();
          onConnect?.();
        };

        wsRef.current.onmessage = handleMessage;
        wsRef.current.onerror = handleError;
        wsRef.current.onclose = handleClose;
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect');
      setIsConnecting(false);
    }
  }, [handleMessage, handleError, handleClose, startHeartbeat, onConnect]);

  const disconnect = useCallback(() => {
    cleanup();
    sessionIdRef.current = null;
    reconnectAttemptsRef.current = reconnectAttempts; // Prevent reconnection
    
    if (wsRef.current) {
      if (API_CONFIG.useMockBackend) {
        // Mock WebSocket service has disconnect method
        (wsRef.current as any).disconnect?.();
      } else {
        // Real WebSocket has close method
        wsRef.current.close();
      }
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setIsConnecting(false);
    setError(null);
  }, [cleanup, reconnectAttempts]);

  const sendMessage = useCallback((message: any) => {
    if (API_CONFIG.useMockBackend && wsRef.current) {
      // Use mock WebSocket send method
      (wsRef.current as any).send(message);
    } else if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', message);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup();
      if (wsRef.current) {
        if (API_CONFIG.useMockBackend) {
          (wsRef.current as any).disconnect?.();
        } else {
          wsRef.current.close();
        }
      }
    };
  }, [cleanup]);

  return {
    isConnected,
    isConnecting,
    error,
    connect,
    disconnect,
    sendMessage,
    lastMessage
  };
};

// Hook for streaming chat messages with token accumulation
export const useStreamingChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [citations, setCitations] = useState<any[]>([]);
  
  const accumulatedTokensRef = useRef<string>('');
  const animationFrameRef = useRef<number | null>(null);

  const flushTokens = useCallback(() => {
    if (accumulatedTokensRef.current) {
      setCurrentStreamingMessage(accumulatedTokensRef.current);
    }
  }, []);

  const ws = useWebSocket({
    onMessage: useCallback((message: StreamingMessage) => {
      if (message.type === 'token' && message.content) {
        // Accumulate tokens and batch render with requestAnimationFrame
        accumulatedTokensRef.current += message.content;
        
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        
        animationFrameRef.current = requestAnimationFrame(flushTokens);
        
        if (!isStreaming) {
          setIsStreaming(true);
        }
      } else if (message.type === 'complete') {
        // Finalize the streaming message
        const finalContent = accumulatedTokensRef.current;
        const newMessage: ChatMessage = {
          id: message.analysis_id || Date.now().toString(),
          role: 'assistant',
          content: finalContent,
          timestamp: new Date(),
          citations: message.citations || []
        };
        
        setMessages(prev => [...prev, newMessage]);
        setCitations(message.citations || []);
        setCurrentStreamingMessage('');
        setIsStreaming(false);
        accumulatedTokensRef.current = '';
        
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
      } else if (message.type === 'analysis_error') {
        const errorMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `Error: ${message.error?.message || 'An error occurred during analysis'}`,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, errorMessage]);
        setIsStreaming(false);
        accumulatedTokensRef.current = '';
        
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
      }
    }, [flushTokens, isStreaming])
  });

  const addUserMessage = useCallback((content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    accumulatedTokensRef.current = '';
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentStreamingMessage('');
    setCitations([]);
    setIsStreaming(false);
    accumulatedTokensRef.current = '';
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    messages,
    currentStreamingMessage,
    isStreaming,
    citations,
    addUserMessage,
    clearMessages,
    ...ws
  };
};
