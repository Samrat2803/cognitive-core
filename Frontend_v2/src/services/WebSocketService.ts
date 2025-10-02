/**
 * WebSocket Service for Political Analyst Workbench
 * Handles real-time communication with the backend
 */

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export type MessageType = 
  | 'query' 
  | 'cancel'
  | 'connected'
  | 'session_start'
  | 'status'
  | 'content'
  | 'citation'
  | 'artifact'
  | 'complete'
  | 'error';

export interface ServerMessage {
  type: MessageType;
  data: any;
  timestamp: string;
  message_id?: string;
}

export interface ClientMessage {
  type: 'query' | 'cancel';
  data: any;
  message_id: string;
}

type MessageHandler = (message: ServerMessage) => void;
type StatusHandler = (status: ConnectionStatus) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private messageHandlers: Map<MessageType, MessageHandler[]> = new Map();
  private statusHandlers: StatusHandler[] = [];
  private status: ConnectionStatus = 'disconnected';
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

  constructor(url: string = import.meta.env.VITE_WS_URL || 'ws://localhost:8001/ws/analyze') {
    this.url = url;
    console.log('🔌 WebSocket URL:', this.url);
    console.log('📝 VITE_WS_URL env:', import.meta.env.VITE_WS_URL);
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.updateStatus('connecting');
    console.log('🔌 Connecting to WebSocket:', this.url);

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error);
      this.updateStatus('error');
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    console.log('🔌 Disconnecting from WebSocket');
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.updateStatus('disconnected');
  }

  /**
   * Send a message to the server
   */
  send(message: ClientMessage): void {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.error('❌ WebSocket is not connected');
      return;
    }

    const messageStr = JSON.stringify(message);
    console.log('📤 Sending message:', message.type, message.message_id);
    this.ws.send(messageStr);
  }

  /**
   * Register a handler for specific message types
   */
  on(type: MessageType, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    
    this.messageHandlers.get(type)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  /**
   * Register a handler for connection status changes
   */
  onStatusChange(handler: StatusHandler): () => void {
    this.statusHandlers.push(handler);

    // Call immediately with current status
    handler(this.status);

    // Return unsubscribe function
    return () => {
      const index = this.statusHandlers.indexOf(handler);
      if (index > -1) {
        this.statusHandlers.splice(index, 1);
      }
    };
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus {
    return this.status;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // Private methods

  private handleOpen(): void {
    console.log('✅ WebSocket connected');
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    this.updateStatus('connected');
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: ServerMessage = JSON.parse(event.data);
      console.log('📥 Received message:', message.type);

      // Call registered handlers for this message type
      const handlers = this.messageHandlers.get(message.type);
      if (handlers) {
        handlers.forEach(handler => handler(message));
      }
    } catch (error) {
      console.error('❌ Failed to parse message:', error);
    }
  }

  private handleError(event: Event): void {
    console.error('❌ WebSocket error:', event);
    this.updateStatus('error');
  }

  private handleClose(event: CloseEvent): void {
    console.log('🔌 WebSocket closed:', event.code, event.reason);
    this.updateStatus('disconnected');

    // Attempt to reconnect if it wasn't a clean close
    if (event.code !== 1000) {
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private updateStatus(status: ConnectionStatus): void {
    if (this.status !== status) {
      this.status = status;
      console.log('🔄 Status changed:', status);
      
      // Notify all status handlers
      this.statusHandlers.forEach(handler => handler(status));
    }
  }
}

// Singleton instance
export const wsService = new WebSocketService();

