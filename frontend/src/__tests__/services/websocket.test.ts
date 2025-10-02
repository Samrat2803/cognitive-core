import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { WebSocketService } from '../../services/websocket';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(public url: string) {
    // Simulate connection opening
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event('open'));
    }, 10);
  }

  send(data: string) {
    if (this.readyState === MockWebSocket.OPEN) {
      // Echo back for testing
      setTimeout(() => {
        this.onmessage?.(new MessageEvent('message', { data }));
      }, 5);
    }
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    setTimeout(() => {
      this.onclose?.(new CloseEvent('close'));
    }, 5);
  }
}

// Mock global WebSocket
global.WebSocket = MockWebSocket as any;

describe('WebSocketService', () => {
  let wsService: WebSocketService;
  
  beforeEach(() => {
    wsService = new WebSocketService();
    vi.useFakeTimers();
  });

  afterEach(() => {
    wsService.disconnect();
    vi.useRealTimers();
  });

  describe('connection', () => {
    it('should connect to WebSocket URL', async () => {
      wsService.connect('test-session');
      
      // Wait for connection to open
      await vi.advanceTimersByTimeAsync(20);
      
      expect(wsService['socket']).toBeDefined();
      expect(wsService['sessionId']).toBe('test-session');
    });

    it('should handle connection close and reconnect', async () => {
      wsService.connect('test-session');
      await vi.advanceTimersByTimeAsync(20);
      
      // Simulate connection close
      wsService['socket']?.close();
      await vi.advanceTimersByTimeAsync(10);
      
      // Should attempt reconnect
      expect(wsService['reconnectAttempts']).toBeGreaterThan(0);
    });
  });

  describe('message handling', () => {
    it('should send and receive messages', async () => {
      const messageHandler = vi.fn();
      wsService.on(messageHandler);
      
      wsService.connect('test-session');
      await vi.advanceTimersByTimeAsync(20);
      
      const testMessage = { type: 'test', data: 'hello' };
      wsService.send(testMessage);
      
      await vi.advanceTimersByTimeAsync(10);
      
      expect(messageHandler).toHaveBeenCalledWith(testMessage);
    });

    it('should handle ping/pong messages', async () => {
      const messageHandler = vi.fn();
      wsService.on(messageHandler);
      
      wsService.connect('test-session');
      await vi.advanceTimersByTimeAsync(20);
      
      // Simulate receiving ping
      const pingMessage = new MessageEvent('message', { 
        data: JSON.stringify({ type: 'ping', timestamp: new Date().toISOString() })
      });
      wsService['socket']?.onmessage?.(pingMessage);
      
      expect(messageHandler).toHaveBeenCalledWith({
        type: 'ping',
        timestamp: expect.any(String)
      });
    });

    it('should filter analysis progress messages', async () => {
      const messageHandler = vi.fn();
      wsService.on(messageHandler);
      
      wsService.connect('test-session');
      await vi.advanceTimersByTimeAsync(20);
      
      // Simulate analysis progress message
      const progressMessage = new MessageEvent('message', {
        data: JSON.stringify({
          type: 'analysis_progress',
          analysis_id: 'test_123',
          progress: { completion_percentage: 50 }
        })
      });
      wsService['socket']?.onmessage?.(progressMessage);
      
      expect(messageHandler).toHaveBeenCalledWith({
        type: 'analysis_progress',
        analysis_id: 'test_123',
        progress: { completion_percentage: 50 }
      });
    });
  });

  describe('heartbeat', () => {
    it('should start heartbeat on connection', async () => {
      const sendSpy = vi.spyOn(wsService, 'send');
      
      wsService.connect('test-session');
      await vi.advanceTimersByTimeAsync(20);
      
      // Advance time to trigger heartbeat
      await vi.advanceTimersByTimeAsync(30000);
      
      expect(sendSpy).toHaveBeenCalledWith({ type: 'pong' });
    });

    it('should stop heartbeat on disconnect', async () => {
      wsService.connect('test-session');
      await vi.advanceTimersByTimeAsync(20);
      
      wsService.disconnect();
      
      expect(wsService['heartbeatIntervalId']).toBeNull();
    });
  });

  describe('listener management', () => {
    it('should add and remove listeners', () => {
      const listener1 = vi.fn();
      const listener2 = vi.fn();
      
      const unsubscribe1 = wsService.on(listener1);
      const unsubscribe2 = wsService.on(listener2);
      
      expect(wsService['listeners'].size).toBe(2);
      
      unsubscribe1();
      expect(wsService['listeners'].size).toBe(1);
      
      unsubscribe2();
      expect(wsService['listeners'].size).toBe(0);
    });

    it('should clear all listeners on disconnect', () => {
      const listener = vi.fn();
      wsService.on(listener);
      
      expect(wsService['listeners'].size).toBe(1);
      
      wsService.disconnect();
      
      expect(wsService['listeners'].size).toBe(0);
    });
  });
});
