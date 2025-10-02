"""
Test: Master Agent Query Processing
Purpose: Verify master agent can process queries and return results
File: backend_v2/tests/test_02_master_agent.py
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_simple_query():
    """Test simple political query"""
    print("\n   Testing simple political query...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "query": "What is the current political situation in India?",
            "user_session": "test_session_1"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200, f"Request failed: {response.status_code}"
        
        data = response.json()
        assert data["success"] == True, "Query did not succeed"
        assert len(data["response"]) > 100, f"Response too short: {len(data['response'])} chars"
        assert len(data["execution_log"]) > 0, "No execution log"
        assert data["confidence"] > 0.0, "Confidence is zero"
        
        print(f"   ✅ Simple query processed successfully")
        print(f"      Response length: {len(data['response'])} chars")
        print(f"      Confidence: {data['confidence']:.2f}")
        print(f"      Tools used: {data['tools_used']}")
        print(f"      Execution steps: {len(data['execution_log'])}")
        
        return data

async def test_query_with_artifact():
    """Test query that should generate artifact"""
    print("\n   Testing query with artifact generation...")
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "query": "Give me a visualization of India's GDP growth since 2020",
            "user_session": "test_session_2"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200, f"Request failed: {response.status_code}"
        
        data = response.json()
        assert data["success"] == True, "Query did not succeed"
        
        if data["artifact"]:
            print(f"   ✅ Artifact generated")
            print(f"      Artifact type: {data['artifact']['type']}")
            print(f"      Artifact ID: {data['artifact']['artifact_id']}")
        else:
            print(f"   ⚠️  No artifact generated (query may not have triggered artifact creation)")
        
        return data

async def test_error_handling():
    """Test error handling with invalid queries"""
    print("\n   Testing error handling...")
    
    async with httpx.AsyncClient() as client:
        # Empty query
        response = await client.post(f"{BASE_URL}/api/analyze", json={"query": ""})
        assert response.status_code == 400, "Empty query should return 400"
        print(f"   ✅ Empty query rejected (400)")
        
        # Too long query
        response = await client.post(f"{BASE_URL}/api/analyze", json={"query": "a" * 3000})
        assert response.status_code == 400, "Too long query should return 400"
        print(f"   ✅ Too long query rejected (400)")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 2: Master Agent - Basic Query Processing")
    print("="*70)
    
    try:
        asyncio.run(test_simple_query())
        asyncio.run(test_query_with_artifact())
        asyncio.run(test_error_handling())
        
        print("\n" + "="*70)
        print("✅ ALL MASTER AGENT TESTS PASSED!")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise

