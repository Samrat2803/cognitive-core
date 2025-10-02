import { useState, useEffect, useCallback, useRef } from 'react';
import { wsService, type ConnectionStatus, type MessageType, type ServerMessage } from '../services/WebSocketService';

/**
 * React hook for WebSocket connection management
 */
export function useWebSocket() {
  const [status, setStatus] = useState<ConnectionStatus>(wsService.getStatus());

  useEffect(() => {
    // Subscribe to status changes
    const unsubscribe = wsService.onStatusChange(setStatus);

    // Connect on mount
    wsService.connect();

    // Cleanup on unmount
    return () => {
      unsubscribe();
      // Don't disconnect - keep connection alive for the app
    };
  }, []);

  return {
    status,
    isConnected: status === 'connected',
    connect: () => wsService.connect(),
    disconnect: () => wsService.disconnect(),
  };
}

/**
 * Hook to listen for specific message types
 * Uses useRef to avoid duplicate subscriptions when handler changes
 */
export function useWebSocketMessage(
  messageType: MessageType,
  handler: (message: ServerMessage) => void
) {
  // Store handler in ref to avoid re-subscription when it changes
  const handlerRef = useRef(handler);
  
  // Update ref when handler changes
  useEffect(() => {
    handlerRef.current = handler;
  }, [handler]);
  
  // Subscribe once based on messageType only
  useEffect(() => {
    const wrappedHandler = (message: ServerMessage) => {
      handlerRef.current(message);
    };
    
    const unsubscribe = wsService.on(messageType, wrappedHandler);
    return unsubscribe;
  }, [messageType]); // Only re-subscribe if messageType changes
}

/**
 * Hook to send messages
 */
export function useWebSocketSend() {
  const send = useCallback((type: 'query' | 'cancel', data: any) => {
    const message = {
      type,
      data,
      message_id: `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
    };
    wsService.send(message);
    return message.message_id;
  }, []);

  return send;
}

