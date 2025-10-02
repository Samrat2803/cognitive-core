"""
Simple validation script for MVP implementation
Tests basic functionality without complex async test setup
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_SESSION = "validate_mvp_session"

def test_health_endpoint():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Agent initialized: {data.get('agent_initialized')}")
            print(f"   Database available: {data.get('database_available')}")
        return True
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_chat_message():
    """Test chat message endpoint"""
    try:
        payload = {
            "message": "Analyze Hamas sentiment in US, Iran, and Israel",
            "session_id": TEST_SESSION,
            "context": {}
        }
        
        response = requests.post(f"{BASE_URL}/api/chat/message", json=payload)
        print(f"✅ Chat message endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response type: {data.get('response_type')}")
            if data.get('response_type') == 'query_parsed':
                print(f"   Analysis ID: {data.get('analysis_id')}")
                print(f"   Intent action: {data.get('parsed_intent', {}).get('action')}")
                return data.get('analysis_id')
            else:
                print(f"   Message: {data.get('message', '')[:50]}...")
        return None
    except Exception as e:
        print(f"❌ Chat message endpoint failed: {e}")
        return None

def test_analysis_execute():
    """Test analysis execute endpoint"""
    try:
        payload = {
            "query_text": "Geopolitical sentiment analysis test",
            "parameters": {
                "countries": ["United States", "Iran"],
                "days": 7,
                "results_per_country": 20
            },
            "session_id": TEST_SESSION
        }
        
        response = requests.post(f"{BASE_URL}/api/analysis/execute", json=payload)
        print(f"✅ Analysis execute endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Analysis ID: {data.get('analysis_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   WebSocket session: {data.get('websocket_session')}")
            return data.get('analysis_id')
        return None
    except Exception as e:
        print(f"❌ Analysis execute endpoint failed: {e}")
        return None

def test_analysis_status(analysis_id):
    """Test analysis status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/{analysis_id}")
        print(f"✅ Analysis status endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            if data.get('status') == 'processing' and 'progress' in data:
                progress = data['progress']
                print(f"   Progress: {progress.get('completion_percentage')}%")
                print(f"   Current step: {progress.get('current_step')}")
            elif data.get('status') == 'completed':
                print("   Analysis completed!")
        return True
    except Exception as e:
        print(f"❌ Analysis status endpoint failed: {e}")
        return False

def test_config_endpoint():
    """Test config endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/config")
        print(f"✅ Config endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   LLM provider: {data.get('llm_provider')}")
        return True
    except Exception as e:
        print(f"❌ Config endpoint failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🧪 Starting MVP validation...")
    print("=" * 50)
    
    # Test basic endpoints
    if not test_health_endpoint():
        print("❌ Server may not be running. Start with: python app.py")
        return
    
    test_config_endpoint()
    
    # Test MVP endpoints
    analysis_id_from_chat = test_chat_message()
    analysis_id_from_direct = test_analysis_execute()
    
    # Test status checking
    if analysis_id_from_direct:
        print("\n⏳ Waiting 2 seconds for processing to start...")
        time.sleep(2)
        test_analysis_status(analysis_id_from_direct)
    
    print("\n" + "=" * 50)
    print("✅ MVP validation completed!")
    print("\nTo test WebSocket functionality:")
    print("1. Connect to ws://localhost:8000/ws/test_session")
    print("2. Send: {\"type\": \"pong\"}")
    print("3. Watch for ping messages from server")

if __name__ == "__main__":
    main()
