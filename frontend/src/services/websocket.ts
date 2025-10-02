import { WS } from '../api/endpoints';

type WSMessage = {
  type: string;
  [key: string]: unknown;
};

type Listener = (message: WSMessage) => void;

export class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: Set<Listener> = new Set();
  private reconnectAttempts = 0;
  private heartbeatIntervalId: number | null = null;
  private sessionId: string | null = null;

  connect(sessionId: string) {
    this.sessionId = sessionId;
    const url = WS.session(sessionId);

    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.startHeartbeat();
    };

    this.socket.onmessage = (event) => {
      try {
        const data: WSMessage = JSON.parse(event.data);
        if (data.type === 'ping') {
          this.send({ type: 'pong' });
        }
        this.emit(data);
      } catch {
        // ignore invalid json
      }
    };

    this.socket.onclose = () => {
      this.stopHeartbeat();
      this.tryReconnect();
    };

    this.socket.onerror = () => {
      this.socket?.close();
    };
  }

  private tryReconnect() {
    if (!this.sessionId) return;
    const baseDelay = 500;
    const maxDelay = 5000;
    const jitter = Math.random() * 200;
    const delay = Math.min(maxDelay, baseDelay * Math.pow(2, this.reconnectAttempts)) + jitter;
    this.reconnectAttempts += 1;
    setTimeout(() => this.connect(this.sessionId as string), delay);
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatIntervalId = window.setInterval(() => {
      this.send({ type: 'pong' });
    }, 30000);
  }

  private stopHeartbeat() {
    if (this.heartbeatIntervalId) {
      clearInterval(this.heartbeatIntervalId);
      this.heartbeatIntervalId = null;
    }
  }

  send(message: WSMessage) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  on(listener: Listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(message: WSMessage) {
    this.listeners.forEach((l) => l(message));
  }

  disconnect() {
    this.stopHeartbeat();
    this.socket?.close();
    this.socket = null;
    this.listeners.clear();
    this.reconnectAttempts = 0;
  }
}

export const wsService = new WebSocketService();


