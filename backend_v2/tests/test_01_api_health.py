"""
Test: API Health and Connectivity
Purpose: Verify backend server is running and healthy
File: backend_v2/tests/test_01_api_health.py
"""

import asyncio
import httpx
from datetime import datetime

# Test Configuration
BASE_URL = "http://localhost:8000"

async def test_health_endpoint():
    """Test /health endpoint"""
    print("\n   Testing /health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data["status"] == "healthy", "Status is not healthy"
        assert data["agent_status"] == "ready", "Agent is not ready"
        print(f"   ✅ Health endpoint working")
        print(f"      Status: {data['status']}")
        print(f"      Agent Status: {data['agent_status']}")
        print(f"      Version: {data['version']}")

async def test_root_endpoint():
    """Test / endpoint"""
    print("\n   Testing / endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
        data = response.json()
        print(f"   ✅ Root endpoint working")
        print(f"      Status: {data['status']}")

async def test_cors_headers():
    """Test CORS headers are present"""
    print("\n   Testing CORS headers...")
    async with httpx.AsyncClient() as client:
        response = await client.options(f"{BASE_URL}/api/analyze")
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower, "CORS headers missing"
        print(f"   ✅ CORS configured correctly")
        print(f"      Allowed Origin: {headers_lower.get('access-control-allow-origin')}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 1: API Health & Connectivity")
    print("="*70)
    
    try:
        asyncio.run(test_health_endpoint())
        asyncio.run(test_root_endpoint())
        asyncio.run(test_cors_headers())
        
        print("\n" + "="*70)
        print("✅ ALL API HEALTH TESTS PASSED!")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise

