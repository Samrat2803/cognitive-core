import { useState, useEffect, useCallback } from 'react';
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
 */
export function useWebSocketMessage(
  messageType: MessageType,
  handler: (message: ServerMessage) => void
) {
  useEffect(() => {
    const unsubscribe = wsService.on(messageType, handler);
    return unsubscribe;
  }, [messageType, handler]);
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

