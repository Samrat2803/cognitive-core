"""
Test Sentiment Analyzer Integration Through Server

This script tests if the sentiment analyzer is properly integrated
into the master agent and accessible through the FastAPI server.
"""

import asyncio
import httpx
import json
from datetime import datetime


# Server configuration
SERVER_URL = "http://localhost:8000"
ANALYZE_ENDPOINT = f"{SERVER_URL}/api/analyze"


async def test_sentiment_analyzer_via_server():
    """
    Test sentiment analyzer through the /api/analyze endpoint
    """
    
    print("=" * 80)
    print("SENTIMENT ANALYZER SERVER INTEGRATION TEST")
    print("=" * 80)
    print(f"Server: {SERVER_URL}")
    print(f"Endpoint: {ANALYZE_ENDPOINT}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 80)
    print()
    
    # Test queries designed to trigger sentiment analyzer
    test_cases = [
        {
            "name": "Direct Sentiment Request",
            "query": "Analyze sentiment on nuclear energy policy across US, France, and Germany",
            "expected_tool": "sentiment_analysis_agent"
        },
        {
            "name": "International Perspective Request",
            "query": "How do different countries view climate change policy?",
            "expected_tool": "sentiment_analysis_agent"
        },
        {
            "name": "Bias Detection Request",
            "query": "Give me an unbiased analysis of the Russia-Ukraine conflict from multiple perspectives",
            "expected_tool": "sentiment_analysis_agent"
        }
    ]
    
    results = []
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'=' * 80}")
            print(f"TEST {i}/{len(test_cases)}: {test_case['name']}")
            print(f"{'=' * 80}")
            print(f"Query: {test_case['query']}")
            print()
            
            try:
                # Make request to server
                payload = {
                    "query": test_case["query"],
                    "session_id": f"test_session_{i}_{int(datetime.now().timestamp())}"
                }
                
                print(f"⏳ Sending request...")
                response = await client.post(
                    ANALYZE_ENDPOINT,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    results.append({
                        "test": test_case["name"],
                        "status": "FAILED",
                        "error": f"HTTP {response.status_code}"
                    })
                    continue
                
                # Parse response
                data = response.json()
                
                # Check if sentiment analyzer was used
                tools_used = data.get("tools_used", [])
                sentiment_called = "sentiment_analysis_agent" in tools_used
                
                # Check execution log for sentiment analyzer activity
                execution_log = data.get("execution_log", [])
                sentiment_in_log = any(
                    "sentiment" in str(step).lower() 
                    for step in execution_log
                )
                
                # Check sub-agent results
                # Note: The response may have sub_agent_results nested
                has_sentiment_results = False
                response_text = data.get("response", "")
                
                # Check if sentiment data is in the response
                if "sentiment" in response_text.lower():
                    has_sentiment_results = True
                
                print(f"\n📊 RESULTS:")
                print(f"   Response Length: {len(response_text)} chars")
                print(f"   Tools Used: {tools_used}")
                print(f"   Sentiment Analyzer Called: {'✅ YES' if sentiment_called else '❌ NO'}")
                print(f"   Sentiment in Execution Log: {'✅ YES' if sentiment_in_log else '❌ NO'}")
                print(f"   Sentiment Data in Response: {'✅ YES' if has_sentiment_results else '❌ NO'}")
                print(f"   Confidence: {data.get('confidence', 0.0):.2%}")
                print(f"   Iterations: {data.get('iterations', 0)}")
                
                # Print first 500 chars of response
                print(f"\n📝 RESPONSE PREVIEW:")
                print(f"   {response_text[:500]}...")
                
                # Check for artifacts (sentiment analyzer generates 3 artifacts)
                artifacts_mentioned = "artifact" in response_text.lower() or "chart" in response_text.lower()
                if artifacts_mentioned:
                    print(f"\n🎨 Artifacts: Mentioned in response")
                
                # Determine test result
                test_passed = sentiment_called or sentiment_in_log
                
                results.append({
                    "test": test_case["name"],
                    "status": "PASSED ✅" if test_passed else "FAILED ❌",
                    "sentiment_called": sentiment_called,
                    "tools_used": tools_used,
                    "response_length": len(response_text)
                })
                
                print(f"\n{'✅ TEST PASSED' if test_passed else '❌ TEST FAILED'}")
                
            except httpx.TimeoutException:
                print(f"❌ Request timed out (>120s)")
                results.append({
                    "test": test_case["name"],
                    "status": "TIMEOUT",
                    "error": "Request exceeded 120s timeout"
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                results.append({
                    "test": test_case["name"],
                    "status": "ERROR",
                    "error": str(e)
                })
    
    # Summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    
    passed = sum(1 for r in results if "PASSED" in r.get("status", ""))
    failed = len(results) - passed
    
    for i, result in enumerate(results, 1):
        status_icon = "✅" if "PASSED" in result["status"] else "❌"
        print(f"{status_icon} Test {i}: {result['test']}")
        print(f"   Status: {result['status']}")
        if result.get("sentiment_called"):
            print(f"   Sentiment Analyzer: INVOKED")
        if result.get("tools_used"):
            print(f"   Tools: {', '.join(result['tools_used'])}")
        if result.get("error"):
            print(f"   Error: {result['error']}")
        print()
    
    print(f"{'=' * 80}")
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print(f"{'=' * 80}")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Sentiment Analyzer is fully integrated.")
    elif passed > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {passed}/{len(results)} tests passed")
    else:
        print("\n❌ ALL TESTS FAILED! Sentiment Analyzer may not be integrated properly.")
    
    return passed == len(results)


async def check_server_health():
    """Check if server is running"""
    print("Checking server health...")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SERVER_URL}/health")
            if response.status_code == 200:
                print("✅ Server is running")
                return True
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
                return False
    except httpx.ConnectError:
        print(f"❌ Cannot connect to server at {SERVER_URL}")
        print(f"   Make sure the server is running:")
        print(f"   cd backend_v2 && uvicorn app:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False


async def main():
    """Main test runner"""
    
    # Check server health first
    server_ok = await check_server_health()
    
    if not server_ok:
        print("\n" + "=" * 80)
        print("SERVER NOT AVAILABLE")
        print("=" * 80)
        print("\nTo start the server:")
        print("1. cd backend_v2")
        print("2. source .venv/bin/activate")
        print("3. uvicorn app:app --reload")
        print("\nThen run this test again.")
        return False
    
    print()
    
    # Run integration tests
    success = await test_sentiment_analyzer_via_server()
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

