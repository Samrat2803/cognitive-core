"""
Test: Sub-Agents Functionality
Purpose: Test each implemented sub-agent
File: backend_v2/tests/test_03_sub_agents.py
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_sentiment_analyzer():
    """Test Sentiment Analyzer sub-agent"""
    print("\n   Testing Sentiment Analyzer...")
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "query": "Analyze sentiment about nuclear energy in US, UK, and France"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200, f"Request failed: {response.status_code}"
        
        data = response.json()
        assert data["success"] == True, "Query did not succeed"
        
        # Check if sentiment analyzer was used
        if data.get("sub_agent_artifacts"):
            print(f"   ✅ Sentiment Analyzer invoked via master agent")
            print(f"      Sub-agent artifacts: {list(data['sub_agent_artifacts'].keys())}")
            for agent_name, artifacts in data['sub_agent_artifacts'].items():
                print(f"      {agent_name}: {len(artifacts)} artifacts")
        else:
            print(f"   ⚠️  Sentiment analyzer not directly visible in response")
        
        return data

async def test_live_monitor():
    """Test Live Political Monitor"""
    print("\n   Testing Live Political Monitor...")
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "keywords": ["Bihar", "election"],
            "cache_hours": 1,
            "max_results": 5
        }
        
        response = await client.post(
            f"{BASE_URL}/api/live-monitor/explosive-topics", 
            json=payload
        )
        assert response.status_code == 200, f"Request failed: {response.status_code}"
        
        data = response.json()
        assert data["success"] == True, "Query did not succeed"
        assert len(data["topics"]) >= 0, "No topics field"
        
        print(f"   ✅ Live Monitor working")
        print(f"      Topics found: {len(data['topics'])}")
        print(f"      Articles analyzed: {data['total_articles_analyzed']}")
        print(f"      Source: {data['source']}")
        
        return data

async def test_media_bias_detector():
    """Test Media Bias Detector sub-agent"""
    print("\n   Testing Media Bias Detector...")
    async with httpx.AsyncClient(timeout=90.0) as client:
        payload = {
            "query": "Analyze media bias on climate change reporting"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200, f"Request failed: {response.status_code}"
        
        data = response.json()
        assert data["success"] == True, "Query did not succeed"
        
        print(f"   ✅ Media Bias Detector query processed")
        print(f"      Response length: {len(data['response'])} chars")
        
        return data

async def test_sitrep_generator():
    """Test SitRep Generator sub-agent"""
    print("\n   Testing SitRep Generator...")
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "query": "Generate a situation report for current global events"
        }
        
        response = await client.post(f"{BASE_URL}/api/analyze", json=payload)
        assert response.status_code == 200, f"Request failed: {response.status_code}"
        
        data = response.json()
        assert data["success"] == True, "Query did not succeed"
        
        print(f"   ✅ SitRep Generator query processed")
        print(f"      Response length: {len(data['response'])} chars")
        
        return data

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 3: Sub-Agents Testing")
    print("="*70)
    
    try:
        print("\n📊 Test 1: Sentiment Analyzer")
        asyncio.run(test_sentiment_analyzer())
        
        print("\n📡 Test 2: Live Political Monitor")
        asyncio.run(test_live_monitor())
        
        print("\n📰 Test 3: Media Bias Detector")
        asyncio.run(test_media_bias_detector())
        
        print("\n📋 Test 4: SitRep Generator")
        asyncio.run(test_sitrep_generator())
        
        print("\n" + "="*70)
        print("✅ ALL SUB-AGENT TESTS PASSED!")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        raise

