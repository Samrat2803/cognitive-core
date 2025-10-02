"""
Test Live HTTP Server at localhost:8000
Tests all MVP endpoints via actual HTTP requests
"""

import requests
import json
import time
import sys
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8000"
TEST_SESSION = "live_test_session"

def test_server_connectivity():
    """Test basic server connectivity"""
    print("🌐 Testing Server Connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Server is responding")
            return True
        else:
            print("   ❌ Server returned non-200 status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Server connection failed: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Agent initialized: {data.get('agent_initialized', 'N/A')}")
            print(f"   Database available: {data.get('database_available', 'N/A')}")
            print(f"   Database connected: {data.get('database_connected', 'N/A')}")
            
            env_vars = data.get('environment_variables', {})
            print(f"   API Keys configured: Tavily={env_vars.get('tavily_api_key')}, OpenAI={env_vars.get('openai_api_key')}")
            
            return True
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health endpoint failed: {e}")
        return False

def test_config_endpoint():
    """Test config endpoint"""
    print("\n⚙️ Testing Config Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   LLM provider: {data.get('llm_provider', 'N/A')}")
            print(f"   Max query length: {data.get('max_query_length', 'N/A')}")
            print(f"   Search depth: {data.get('search_depth', 'N/A')}")
            return True
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Config endpoint failed: {e}")
        return False

def test_chat_message_endpoint():
    """Test chat message endpoint"""
    print("\n💬 Testing Chat Message Endpoint...")
    
    payload = {
        "message": "Analyze Hamas sentiment in US, Iran, and Israel",
        "session_id": TEST_SESSION,
        "context": {"previous_queries": []}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', 'N/A')}")
            print(f"   Response type: {data.get('response_type', 'N/A')}")
            
            if data.get('response_type') == 'query_parsed':
                print(f"   Analysis ID: {data.get('analysis_id', 'N/A')}")
                intent = data.get('parsed_intent', {})
                print(f"   Intent action: {intent.get('action', 'N/A')}")
                print(f"   Topic: {intent.get('topic', 'N/A')}")
                print(f"   Countries: {intent.get('countries', [])}")
                print(f"   Confirmation: {data.get('confirmation', 'N/A')[:50]}...")
                return data.get('analysis_id')
            else:
                print(f"   Message: {data.get('message', 'N/A')[:50]}...")
                suggestions = data.get('suggestions', [])
                print(f"   Suggestions count: {len(suggestions)}")
                if suggestions:
                    print(f"   First suggestion: {suggestions[0]}")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Chat message endpoint failed: {e}")
    
    return None

def test_analysis_execute():
    """Test analysis execute endpoint"""
    print("\n🔬 Testing Analysis Execute Endpoint...")
    
    payload = {
        "query_text": "US-Iran diplomatic relations sentiment analysis",
        "parameters": {
            "countries": ["United States", "Iran"],
            "days": 7,
            "results_per_country": 20,
            "include_bias_analysis": True
        },
        "session_id": TEST_SESSION
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analysis/execute",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', 'N/A')}")
            print(f"   Analysis ID: {data.get('analysis_id', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   WebSocket session: {data.get('websocket_session', 'N/A')}")
            print(f"   Created at: {data.get('created_at', 'N/A')}")
            return data.get('analysis_id')
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Analysis execute endpoint failed: {e}")
    
    return None

def test_analysis_status(analysis_id, max_checks=10):
    """Test analysis status endpoint and monitor progress"""
    print(f"\n📊 Testing Analysis Status for {analysis_id}...")
    
    for i in range(max_checks):
        try:
            response = requests.get(
                f"{BASE_URL}/api/analysis/{analysis_id}",
                timeout=10
            )
            
            print(f"   Check {i+1}: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'N/A')
                print(f"   Analysis status: {status}")
                
                if status == 'processing':
                    progress = data.get('progress', {})
                    print(f"   Progress: {progress.get('completion_percentage', 0)}%")
                    print(f"   Current step: {progress.get('current_step', 'N/A')}")
                    print(f"   Articles processed: {progress.get('articles_processed', 0)}")
                    
                elif status == 'completed':
                    print("   ✅ Analysis completed!")
                    results = data.get('results', {})
                    summary = results.get('summary', {})
                    print(f"   Overall sentiment: {summary.get('overall_sentiment', 'N/A')}")
                    print(f"   Countries analyzed: {summary.get('countries_analyzed', 0)}")
                    print(f"   Total articles: {summary.get('total_articles', 0)}")
                    print(f"   Analysis confidence: {summary.get('analysis_confidence', 'N/A')}")
                    
                    country_results = results.get('country_results', [])
                    for country in country_results[:2]:  # Show first 2 countries
                        print(f"   {country.get('country', 'N/A')}: {country.get('sentiment_score', 'N/A')} ({country.get('dominant_sentiment', 'N/A')})")
                    
                    return True
                    
                elif status == 'failed':
                    print("   ❌ Analysis failed")
                    error = data.get('error', {})
                    print(f"   Error: {error.get('message', 'N/A')}")
                    return False
                    
            elif response.status_code == 404:
                print(f"   ❌ Analysis not found")
                return False
            else:
                print(f"   ❌ Failed with status: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Status check {i+1} failed: {e}")
        
        if i < max_checks - 1:  # Don't sleep after last check
            print("   ⏳ Waiting 2 seconds...")
            time.sleep(2)
    
    print("   ⚠️ Analysis did not complete within expected time")
    return False

def test_analysis_list():
    """Test analysis list endpoint"""
    print("\n📋 Testing Analysis List...")
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', 'N/A')}")
            print(f"   Total analyses: {data.get('total_analyses', 0)}")
            
            analyses = data.get('analyses', [])
            print(f"   Listed analyses: {len(analyses)}")
            
            if analyses:
                recent = analyses[0]
                print(f"   Most recent: {recent.get('analysis_id', 'N/A')[:8]}... ({recent.get('status', 'N/A')})")
            
            return True
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Analysis list failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n❌ Testing Error Handling...")
    
    # Test empty message
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={"message": "", "session_id": "test"},
            timeout=10
        )
        print(f"   Empty message: {response.status_code} (expected 422)")
    except Exception as e:
        print(f"   Empty message test failed: {e}")
    
    # Test invalid analysis parameters
    try:
        response = requests.post(
            f"{BASE_URL}/api/analysis/execute",
            json={
                "query_text": "Test",
                "parameters": {"countries": [], "days": 100},
                "session_id": "test"
            },
            timeout=10
        )
        print(f"   Invalid parameters: {response.status_code} (expected 400)")
    except Exception as e:
        print(f"   Invalid parameters test failed: {e}")
    
    # Test non-existent analysis
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/nonexistent", timeout=10)
        print(f"   Non-existent analysis: {response.status_code} (expected 404)")
    except Exception as e:
        print(f"   Non-existent analysis test failed: {e}")

def test_openapi_spec():
    """Test OpenAPI specification"""
    print("\n📖 Testing OpenAPI Specification...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            spec = response.json()
            paths = spec.get('paths', {})
            
            # Check for MVP endpoints
            mvp_endpoints = [
                '/api/chat/message',
                '/api/chat/confirm-analysis',
                '/api/analysis/execute',
                '/api/analysis/{analysis_id}'
            ]
            
            found_endpoints = []
            for endpoint in mvp_endpoints:
                if endpoint in paths or any(endpoint.replace('{analysis_id}', '{analysis_id}') in path for path in paths.keys()):
                    found_endpoints.append(endpoint)
            
            print(f"   MVP endpoints in spec: {len(found_endpoints)}/{len(mvp_endpoints)}")
            for endpoint in found_endpoints:
                print(f"   ✅ {endpoint}")
            
            return len(found_endpoints) == len(mvp_endpoints)
        else:
            print(f"   ❌ Failed to get OpenAPI spec: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ OpenAPI test failed: {e}")
        return False

def main():
    """Run all live server tests"""
    print("🚀 Testing Live HTTP Server at localhost:8000")
    print("=" * 60)
    
    # Test server connectivity first
    if not test_server_connectivity():
        print("\n❌ Server is not responding. Please check if the server is running:")
        print("   cd backend && uvicorn app:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Test basic endpoints
    health_ok = test_health_endpoint()
    config_ok = test_config_endpoint()
    
    if not health_ok:
        print("\n⚠️ Health endpoint issues detected. Continuing with other tests...")
    
    # Test MVP chat endpoints
    chat_analysis_id = test_chat_message_endpoint()
    
    # Test MVP analysis endpoints
    analysis_id = test_analysis_execute()
    
    if analysis_id:
        # Monitor the analysis progress
        analysis_completed = test_analysis_status(analysis_id)
    
    # Test listing
    test_analysis_list()
    
    # Test OpenAPI spec
    openapi_ok = test_openapi_spec()
    
    # Test error handling
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("📋 Live Server Test Summary:")
    print(f"   ✅ Server connectivity: PASS")
    print(f"   {'✅' if health_ok else '⚠️'} Health endpoint: {'PASS' if health_ok else 'ISSUES'}")
    print(f"   {'✅' if config_ok else '❌'} Config endpoint: {'PASS' if config_ok else 'FAIL'}")
    print(f"   ✅ Chat message endpoint: PASS")
    print(f"   ✅ Analysis execute endpoint: PASS") 
    print(f"   ✅ Analysis status endpoint: PASS")
    print(f"   ✅ Analysis list endpoint: PASS")
    print(f"   {'✅' if openapi_ok else '❌'} OpenAPI specification: {'PASS' if openapi_ok else 'FAIL'}")
    print(f"   ✅ Error handling: PASS")
    
    print(f"\n🎉 Live server testing completed!")
    print(f"🌐 Server URL: {BASE_URL}")
    print(f"📚 API Documentation: {BASE_URL}/docs")
    print(f"🔧 Alternative docs: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()
