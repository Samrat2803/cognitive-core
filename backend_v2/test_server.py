"""
Test script for the Political Analyst Backend Server
Quick validation of API endpoints
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"


async def test_health():
    """Test health check endpoint"""
    print("\n" + "=" * 70)
    print("TEST 1: Health Check")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("✅ Health check passed")


async def test_analyze():
    """Test analysis endpoint"""
    print("\n" + "=" * 70)
    print("TEST 2: Analysis Endpoint")
    print("=" * 70)
    
    query = "What are the latest developments in US-China trade relations?"
    
    print(f"Query: {query}")
    print("\nSending request...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/analyze",
            json={"query": query}
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Analysis completed!")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Confidence: {result['confidence']:.0%}")
            print(f"   Tools Used: {', '.join(result['tools_used'])}")
            print(f"   Iterations: {result['iterations']}")
            print(f"   Processing Time: {result['processing_time_ms']}ms")
            print(f"   Citations: {len(result['citations'])}")
            print(f"\n   Response Preview:")
            print(f"   {result['response'][:200]}...")
            
            if result.get('artifact'):
                print(f"\n   🎨 Artifact Created:")
                print(f"      Type: {result['artifact']['type']}")
                print(f"      ID: {result['artifact']['artifact_id']}")
        else:
            print(f"❌ Request failed: {response.text}")


async def test_analyze_with_artifact():
    """Test analysis with artifact generation"""
    print("\n" + "=" * 70)
    print("TEST 3: Analysis with Artifact Generation")
    print("=" * 70)
    
    query = "Create a trend chart showing India's GDP growth from 2020 to 2025"
    
    print(f"Query: {query}")
    print("\nSending request...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/analyze",
            json={"query": query}
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Analysis completed!")
            print(f"   Confidence: {result['confidence']:.0%}")
            print(f"   Processing Time: {result['processing_time_ms']}ms")
            
            if result.get('artifact'):
                artifact = result['artifact']
                print(f"\n   🎨 Artifact Generated:")
                print(f"      Type: {artifact['type']}")
                print(f"      ID: {artifact['artifact_id']}")
                print(f"      HTML: {BASE_URL}/api/artifacts/{artifact['artifact_id']}.html")
                print(f"      PNG: {BASE_URL}/api/artifacts/{artifact['artifact_id']}.png")
            else:
                print("\n   ⚠️  No artifact was created")
        else:
            print(f"❌ Request failed: {response.text}")


async def test_invalid_request():
    """Test error handling"""
    print("\n" + "=" * 70)
    print("TEST 4: Error Handling (Empty Query)")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/analyze",
            json={"query": ""}
        )
        
        print(f"Status: {response.status_code}")
        assert response.status_code == 400
        print(f"Error: {response.json()['detail']}")
        print("✅ Error handling works correctly")


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 POLITICAL ANALYST BACKEND SERVER TESTS")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print("\nMake sure the server is running: python app.py")
    print("=" * 70)
    
    try:
        # Test 1: Health Check
        await test_health()
        
        # Test 2: Basic Analysis
        await test_analyze()
        
        # Test 3: Analysis with Artifact
        await test_analyze_with_artifact()
        
        # Test 4: Error Handling
        await test_invalid_request()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        
    except httpx.ConnectError:
        print("\n❌ Cannot connect to server. Is it running?")
        print("   Start server: python app.py")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

