"""
MVP Endpoint Tests
Tests for all new chat, analysis, and WebSocket endpoints
"""

import asyncio
import json
import pytest
from datetime import datetime
from typing import Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the app
from app import app

# Test data
TEST_SESSION_ID = "test_session_123"
TEST_ANALYSIS_QUERY = "Analyze Hamas sentiment in US, Iran, and Israel"
TEST_ANALYSIS_PARAMS = {
    "countries": ["United States", "Iran", "Israel"],
    "days": 7,
    "results_per_country": 20,
    "include_bias_analysis": True
}


class TestChatEndpoints:
    """Test chat endpoints"""
    
    @pytest.mark.asyncio
    async def test_chat_message_intent_parsing(self):
        """Test intent parsing for geopolitical analysis"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/message",
                json={
                    "message": TEST_ANALYSIS_QUERY,
                    "session_id": TEST_SESSION_ID,
                    "context": {}
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert "response_type" in data
            
            if data["response_type"] == "query_parsed":
                assert "analysis_id" in data
                assert "parsed_intent" in data
                assert "confirmation" in data
                print(f"✅ Intent parsed successfully: {data['parsed_intent']['action']}")
            else:
                assert "message" in data
                assert "suggestions" in data
                print(f"✅ Direct response provided with suggestions")
    
    @pytest.mark.asyncio
    async def test_chat_message_invalid_request(self):
        """Test chat message with invalid data"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/message",
                json={
                    "message": "",  # Empty message should fail
                    "session_id": TEST_SESSION_ID
                }
            )
            
            assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_chat_confirm_analysis(self):
        """Test analysis confirmation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/confirm-analysis",
                json={
                    "analysis_id": "test_analysis_123",
                    "confirmed": True,
                    "modifications": {
                        "countries": ["United States", "Iran"],
                        "days": 14
                    }
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["status"] == "queued"
            assert "analysis_id" in data
            assert "websocket_session" in data
            print(f"✅ Analysis confirmed: {data['analysis_id']}")


class TestAnalysisEndpoints:
    """Test analysis endpoints"""
    
    @pytest.mark.asyncio
    async def test_analysis_execute(self):
        """Test direct analysis execution"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/analysis/execute",
                json={
                    "query_text": TEST_ANALYSIS_QUERY,
                    "parameters": TEST_ANALYSIS_PARAMS,
                    "session_id": TEST_SESSION_ID
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["status"] == "processing"
            assert "analysis_id" in data
            assert "websocket_session" in data
            assert "created_at" in data
            print(f"✅ Analysis started: {data['analysis_id']}")
            
            return data["analysis_id"]  # Return for follow-up tests
    
    @pytest.mark.asyncio
    async def test_analysis_get_status(self):
        """Test analysis status retrieval"""
        # First create an analysis
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create analysis
            create_response = await client.post(
                "/api/analysis/execute",
                json={
                    "query_text": "Test analysis",
                    "parameters": {"countries": ["United States"], "days": 7},
                    "session_id": TEST_SESSION_ID
                }
            )
            
            analysis_id = create_response.json()["analysis_id"]
            
            # Wait a moment for processing to start
            await asyncio.sleep(0.5)
            
            # Get status
            status_response = await client.get(f"/api/analysis/{analysis_id}")
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            assert status_data["success"] is True
            assert status_data["analysis_id"] == analysis_id
            assert status_data["status"] in ["processing", "completed", "failed"]
            
            if status_data["status"] == "processing":
                assert "progress" in status_data
                print(f"✅ Analysis in progress: {status_data['progress']['completion_percentage']}%")
            elif status_data["status"] == "completed":
                assert "results" in status_data
                print(f"✅ Analysis completed with results")
            
    @pytest.mark.asyncio
    async def test_analysis_invalid_parameters(self):
        """Test analysis with invalid parameters"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/analysis/execute",
                json={
                    "query_text": "Test query",
                    "parameters": {
                        "countries": [],  # Empty countries should fail
                        "days": 100  # Too many days should fail
                    },
                    "session_id": TEST_SESSION_ID
                }
            )
            
            assert response.status_code == 400
            print("✅ Invalid parameters correctly rejected")
    
    @pytest.mark.asyncio
    async def test_analysis_not_found(self):
        """Test getting non-existent analysis"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/analysis/nonexistent_id")
            
            assert response.status_code == 404
            print("✅ Non-existent analysis correctly returns 404")
    
    @pytest.mark.asyncio
    async def test_list_analyses(self):
        """Test listing analyses"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/analysis/")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert "total_analyses" in data
            assert "analyses" in data
            print(f"✅ Listed {data['total_analyses']} analyses")


class TestWebSocketEndpoint:
    """Test WebSocket functionality"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection and basic message handling"""
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        with client.websocket_connect(f"/ws/{TEST_SESSION_ID}") as websocket:
            # Send a pong message
            websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}))
            
            # The connection should stay open
            # In a real test, we'd wait for ping messages, but this basic test just validates connection
            print("✅ WebSocket connection established and pong sent")


class TestIntegrationFlow:
    """Test complete integration flow"""
    
    @pytest.mark.asyncio
    async def test_complete_analysis_flow(self):
        """Test complete flow from chat message to analysis completion"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            # Step 1: Send chat message
            chat_response = await client.post(
                "/api/chat/message",
                json={
                    "message": "Analyze sentiment about Iran nuclear program in US and Europe",
                    "session_id": TEST_SESSION_ID
                }
            )
            
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            
            if chat_data["response_type"] == "query_parsed":
                analysis_id = chat_data["analysis_id"]
                
                # Step 2: Confirm analysis
                confirm_response = await client.post(
                    "/api/chat/confirm-analysis",
                    json={
                        "analysis_id": analysis_id,
                        "confirmed": True
                    }
                )
                
                assert confirm_response.status_code == 200
                confirm_data = confirm_response.json()
                actual_analysis_id = confirm_data["analysis_id"]
                
                # Step 3: Check status
                await asyncio.sleep(1)  # Wait for processing to start
                
                status_response = await client.get(f"/api/analysis/{actual_analysis_id}")
                assert status_response.status_code == 200
                
                print("✅ Complete integration flow successful")
            else:
                # Direct response flow
                assert "suggestions" in chat_data
                print("✅ Direct response flow successful")


class TestHealthAndCompatibility:
    """Test health endpoints and backward compatibility"""
    
    @pytest.mark.asyncio
    async def test_legacy_endpoints_still_work(self):
        """Test that existing endpoints still function"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            # Test health endpoint
            health_response = await client.get("/health")
            assert health_response.status_code == 200
            print("✅ Health endpoint working")
            
            # Test config endpoint
            config_response = await client.get("/config")
            assert config_response.status_code == 200
            print("✅ Config endpoint working")
            
            # Test root endpoint
            root_response = await client.get("/")
            assert root_response.status_code == 200
            print("✅ Root endpoint working")


if __name__ == "__main__":
    # Run basic smoke tests
    async def run_smoke_tests():
        print("🧪 Running MVP endpoint smoke tests...")
        
        # Basic endpoint availability test
        async with AsyncClient(app=app, base_url="http://test") as client:
            
            # Test chat message endpoint
            try:
                response = await client.post("/api/chat/message", json={
                    "message": "Hello",
                    "session_id": "smoke_test"
                })
                print(f"✅ Chat message endpoint: {response.status_code}")
            except Exception as e:
                print(f"❌ Chat message endpoint failed: {e}")
            
            # Test analysis execute endpoint
            try:
                response = await client.post("/api/analysis/execute", json={
                    "query_text": "Test query",
                    "parameters": {"countries": ["United States"], "days": 7},
                    "session_id": "smoke_test"
                })
                print(f"✅ Analysis execute endpoint: {response.status_code}")
            except Exception as e:
                print(f"❌ Analysis execute endpoint failed: {e}")
            
            # Test health endpoint
            try:
                response = await client.get("/health")
                print(f"✅ Health endpoint: {response.status_code}")
            except Exception as e:
                print(f"❌ Health endpoint failed: {e}")
        
        print("✅ Smoke tests completed!")
    
    # Run the smoke tests
    asyncio.run(run_smoke_tests())
