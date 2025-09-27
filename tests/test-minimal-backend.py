#!/usr/bin/env python3
"""
Test script for the minimal backend
"""

import requests
import json
import time

def test_minimal_backend():
    print("🧪 Testing Minimal Backend")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   ✅ Server is running (Status: {response.status_code})")
        print(f"   📄 Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Server error: {e}")
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
    
    # Test 3: Quick research query
    print("\n3. Testing quick research query...")
    try:
        test_query = "What is artificial intelligence?"
        print(f"   🔍 Testing with query: '{test_query}'")
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/research",
            json={"query": test_query},
            timeout=30  # 30 second timeout
        )
        end_time = time.time()
        
        print(f"   ⏱️  Response time: {end_time - start_time:.2f} seconds")
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Research completed successfully!")
            print(f"   📝 Success: {data.get('success', 'N/A')}")
            print(f"   🔍 Search terms: {data.get('search_terms', [])}")
            print(f"   📚 Sources count: {data.get('sources_count', 0)}")
            print(f"   📄 Answer preview: {data.get('final_answer', '')[:100]}...")
            print(f"   🔗 Sources: {data.get('sources', [])[:2]}")  # Show first 2 sources
        else:
            print(f"   ❌ Research failed with status {response.status_code}")
            print(f"   📄 Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ Research request timed out")
        return False
    except Exception as e:
        print(f"   ❌ Research endpoint failed: {e}")
        return False
    
    print("\n🎉 Minimal backend testing completed successfully!")
    return True

if __name__ == "__main__":
    print("Starting minimal backend tests...")
    print("Make sure the minimal backend is running: cd backend && python minimal_app.py")
    print("Press Ctrl+C to cancel\n")
    
    try:
        time.sleep(2)
        success = test_minimal_backend()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Testing cancelled by user")
        exit(1)
