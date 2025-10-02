"""
WebSocket Manager for real-time communication with heartbeat and rate limiting
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Set, Optional, Any, List
from fastapi import WebSocket, WebSocketDisconnect
from models.api_schemas import (
    PingMessage, 
    ProgressMessage, 
    CompletedMessage, 
    ErrorMessage,
    WebSocketMessage
)

# Configuration constants (non-secret)
HEARTBEAT_INTERVAL = 30  # seconds
MAX_MESSAGES_PER_SECOND = 10
THROTTLE_WINDOW = 1.0  # seconds


class WebSocketConnection:
    """Represents a single WebSocket connection with rate limiting"""
    
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.connected = True
        self.message_queue = asyncio.Queue()
        self.last_heartbeat = time.time()
        
        # Rate limiting
        self.message_timestamps: List[float] = []
        self.throttled_messages: List[WebSocketMessage] = []
        
    async def send_message(self, message: WebSocketMessage):
        """Send a message with rate limiting"""
        if not self.connected:
            return
            
        # Add to throttled messages for batching
        self.throttled_messages.append(message)
    
    async def _flush_throttled_messages(self):
        """Flush throttled messages respecting rate limits"""
        if not self.throttled_messages or not self.connected:
            return
            
        current_time = time.time()
        
        # Clean old timestamps
        self.message_timestamps = [
            ts for ts in self.message_timestamps 
            if current_time - ts < THROTTLE_WINDOW
        ]
        
        # Calculate how many messages we can send
        available_slots = MAX_MESSAGES_PER_SECOND - len(self.message_timestamps)
        
        if available_slots > 0:
            # Send up to available slots
            messages_to_send = self.throttled_messages[:available_slots]
            self.throttled_messages = self.throttled_messages[available_slots:]
            
            for msg in messages_to_send:
                try:
                    await self.websocket.send_text(msg.json())
                    self.message_timestamps.append(current_time)
                except Exception as e:
                    print(f"❌ Error sending WebSocket message: {e}")
                    self.connected = False
                    break
    
    async def send_heartbeat(self):
        """Send heartbeat ping"""
        if not self.connected:
            return
            
        current_time = time.time()
        if current_time - self.last_heartbeat >= HEARTBEAT_INTERVAL:
            ping = PingMessage()
            try:
                await self.websocket.send_text(ping.json())
                self.last_heartbeat = current_time
            except Exception as e:
                print(f"❌ Error sending heartbeat: {e}")
                self.connected = False
    
    def disconnect(self):
        """Mark connection as disconnected"""
        self.connected = False


class WebSocketManager:
    """Manages WebSocket connections with heartbeat and message throttling"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.session_to_analysis: Dict[str, str] = {}  # session_id -> analysis_id
        self.analysis_to_sessions: Dict[str, Set[str]] = {}  # analysis_id -> set of session_ids
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._throttle_task: Optional[asyncio.Task] = None
        
    async def start_background_tasks(self):
        """Start heartbeat and throttling background tasks"""
        if not self._heartbeat_task:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        if not self._throttle_task:
            self._throttle_task = asyncio.create_task(self._throttle_loop())
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self._throttle_task:
            self._throttle_task.cancel()
            try:
                await self._throttle_task
            except asyncio.CancelledError:
                pass
    
    async def connect(self, websocket: WebSocket, session_id: str) -> bool:
        """Connect a new WebSocket client"""
        try:
            await websocket.accept()
            connection = WebSocketConnection(websocket, session_id)
            self.connections[session_id] = connection
            
            # Start background tasks if this is the first connection
            if len(self.connections) == 1:
                await self.start_background_tasks()
            
            print(f"🔗 WebSocket connected: session_id={session_id}")
            return True
            
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
    
    async def disconnect(self, session_id: str):
        """Disconnect a WebSocket client"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            connection.disconnect()
            del self.connections[session_id]
            
            # Clean up session mappings
            if session_id in self.session_to_analysis:
                analysis_id = self.session_to_analysis[session_id]
                if analysis_id in self.analysis_to_sessions:
                    self.analysis_to_sessions[analysis_id].discard(session_id)
                    if not self.analysis_to_sessions[analysis_id]:
                        del self.analysis_to_sessions[analysis_id]
                del self.session_to_analysis[session_id]
            
            print(f"🔌 WebSocket disconnected: session_id={session_id}")
            
            # Stop background tasks if no connections remain
            if not self.connections:
                await self.stop_background_tasks()
    
    def register_analysis(self, session_id: str, analysis_id: str):
        """Register analysis for a session"""
        self.session_to_analysis[session_id] = analysis_id
        if analysis_id not in self.analysis_to_sessions:
            self.analysis_to_sessions[analysis_id] = set()
        self.analysis_to_sessions[analysis_id].add(session_id)
    
    async def send_to_session(self, session_id: str, message: WebSocketMessage):
        """Send message to a specific session"""
        if session_id in self.connections:
            await self.connections[session_id].send_message(message)
    
    async def send_to_analysis(self, analysis_id: str, message: WebSocketMessage):
        """Send message to all sessions tracking an analysis"""
        if analysis_id in self.analysis_to_sessions:
            tasks = []
            for session_id in self.analysis_to_sessions[analysis_id].copy():
                if session_id in self.connections:
                    tasks.append(self.connections[session_id].send_message(message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_progress(self, analysis_id: str, progress_data: Dict[str, Any]):
        """Broadcast analysis progress to relevant sessions"""
        from models.api_schemas import AnalysisProgress
        
        try:
            progress = AnalysisProgress(**progress_data)
            message = ProgressMessage(analysis_id=analysis_id, progress=progress)
            await self.send_to_analysis(analysis_id, message)
        except Exception as e:
            print(f"❌ Error broadcasting progress: {e}")
    
    async def broadcast_completion(self, analysis_id: str, results_data: Dict[str, Any]):
        """Broadcast analysis completion to relevant sessions"""
        from models.api_schemas import AnalysisResults
        
        try:
            results = AnalysisResults(**results_data)
            message = CompletedMessage(analysis_id=analysis_id, results=results)
            await self.send_to_analysis(analysis_id, message)
        except Exception as e:
            print(f"❌ Error broadcasting completion: {e}")
    
    async def broadcast_error(self, analysis_id: str, error_data: Dict[str, Any]):
        """Broadcast analysis error to relevant sessions"""
        try:
            message = ErrorMessage(analysis_id=analysis_id, error=error_data)
            await self.send_to_analysis(analysis_id, message)
        except Exception as e:
            print(f"❌ Error broadcasting error: {e}")
    
    async def handle_client_message(self, session_id: str, message_data: Dict[str, Any]):
        """Handle incoming client messages (e.g., pong responses)"""
        message_type = message_data.get("type")
        
        if message_type == "pong":
            # Client responded to ping, connection is healthy
            print(f"💓 Received pong from session: {session_id}")
        else:
            print(f"🔍 Unknown message type from {session_id}: {message_type}")
    
    async def _heartbeat_loop(self):
        """Background task to send heartbeats to all connections"""
        while True:
            try:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                
                # Send heartbeats to all active connections
                tasks = []
                for connection in list(self.connections.values()):
                    if connection.connected:
                        tasks.append(connection.send_heartbeat())
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Clean up disconnected sessions
                disconnected_sessions = [
                    session_id for session_id, conn in self.connections.items()
                    if not conn.connected
                ]
                
                for session_id in disconnected_sessions:
                    await self.disconnect(session_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in heartbeat loop: {e}")
    
    async def _throttle_loop(self):
        """Background task to flush throttled messages"""
        while True:
            try:
                await asyncio.sleep(0.1)  # Check every 100ms
                
                # Flush messages for all connections
                tasks = []
                for connection in list(self.connections.values()):
                    if connection.connected:
                        tasks.append(connection._flush_throttled_messages())
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in throttle loop: {e}")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


if __name__ == "__main__":
    # Test WebSocket manager functionality
    async def test_websocket_manager():
        print("🧪 Testing WebSocket manager...")
        
        manager = WebSocketManager()
        
        # Test message creation
        from models.api_schemas import AnalysisProgress
        progress = AnalysisProgress(
            current_step="analyzing_articles",
            completion_percentage=45,
            articles_processed=28,
            total_articles=60
        )
        
        print(f"✅ Progress message created: {progress.dict()}")
        
        # Test rate limiting logic (without actual WebSocket)
        print("✅ WebSocket manager initialized successfully!")
    
    asyncio.run(test_websocket_manager())
