#!/usr/bin/env python3
"""
Simple backend testing script to diagnose issues
"""

import requests
import json
import time
import sys
import os

def test_backend():
    print("🧪 Backend Testing Script")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   ✅ Server is running (Status: {response.status_code})")
        print(f"   📄 Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Server is not running or not accessible")
        print("   💡 Make sure to start the backend with: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error connecting to server: {e}")
        return False
    
    # Test 2: Health check
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   ✅ Health check passed (Status: {response.status_code})")
        health_data = response.json()
        print(f"   📊 Health data: {health_data}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 3: Config endpoint
    print("\n3. Testing config endpoint...")
    try:
        response = requests.get(f"{base_url}/config", timeout=5)
        print(f"   ✅ Config endpoint working (Status: {response.status_code})")
        config_data = response.json()
        print(f"   ⚙️  Config: {config_data}")
    except Exception as e:
        print(f"   ❌ Config endpoint failed: {e}")
        return False
    
    # Test 4: Research endpoint with simple query
    print("\n4. Testing research endpoint...")
    try:
        test_query = "What is artificial intelligence?"
        print(f"   🔍 Testing with query: '{test_query}'")
        
        response = requests.post(
            f"{base_url}/research",
            json={"query": test_query},
            timeout=30  # Research can take time
        )
        
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Research endpoint working!")
            print(f"   📝 Success: {data.get('success', 'N/A')}")
            print(f"   🔍 Search terms: {data.get('search_terms', [])}")
            print(f"   📚 Sources count: {data.get('sources_count', 0)}")
            print(f"   📄 Answer length: {len(data.get('final_answer', ''))}")
        else:
            print(f"   ❌ Research failed with status {response.status_code}")
            print(f"   📄 Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Research request timed out (this might be normal for first request)")
    except Exception as e:
        print(f"   ❌ Research endpoint failed: {e}")
        return False
    
    # Test 5: CORS headers
    print("\n5. Testing CORS headers...")
    try:
        response = requests.get(
            f"{base_url}/health",
            headers={"Origin": "http://localhost:3000"}
        )
        cors_headers = {
            key: value for key, value in response.headers.items()
            if key.lower().startswith('access-control')
        }
        if cors_headers:
            print("   ✅ CORS headers present:")
            for key, value in cors_headers.items():
                print(f"      {key}: {value}")
        else:
            print("   ⚠️  No CORS headers found")
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
    
    print("\n🎉 Backend testing completed!")
    return True

if __name__ == "__main__":
    print("Starting backend tests...")
    print("Make sure the backend is running: cd backend && python app.py")
    print("Press Ctrl+C to cancel\n")
    
    try:
        time.sleep(2)  # Give user time to read
        success = test_backend()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Testing cancelled by user")
        sys.exit(1)
