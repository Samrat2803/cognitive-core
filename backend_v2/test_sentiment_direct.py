"""
Test Sentiment Analyzer Integration - Direct Master Agent Test

This script tests the sentiment analyzer by directly calling the master agent
(without needing the FastAPI server to be running).
"""

import asyncio
import sys
import os

# Add backend_v2 to path
sys.path.insert(0, os.path.dirname(__file__))

from langgraph_master_agent.main import MasterPoliticalAnalyst
from datetime import datetime


async def test_sentiment_analyzer_direct():
    """
    Test sentiment analyzer by directly calling the master agent
    """
    
    print("=" * 80)
    print("SENTIMENT ANALYZER - DIRECT INTEGRATION TEST")
    print("=" * 80)
    print(f"Testing via: MasterPoliticalAnalyst class (no server needed)")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 80)
    print()
    
    # Test queries designed to trigger sentiment analyzer
    test_cases = [
        {
            "name": "Direct Sentiment Request",
            "query": "Analyze sentiment on AI regulation across US, UK, and France",
            "should_use_sentiment": True
        },
        {
            "name": "International Perspective",
            "query": "How do different countries view renewable energy policy?",
            "should_use_sentiment": True
        },
        {
            "name": "Simple Factual Question",
            "query": "What is the capital of France?",
            "should_use_sentiment": False
        }
    ]
    
    # Initialize master agent
    print("Initializing Master Political Analyst Agent...")
    try:
        agent = MasterPoliticalAnalyst()
        print("✅ Agent initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(test_cases)}: {test_case['name']}")
        print(f"{'=' * 80}")
        print(f"Query: {test_case['query']}")
        print(f"Expected Sentiment Analyzer: {'YES' if test_case['should_use_sentiment'] else 'NO'}")
        print()
        
        try:
            print(f"⏳ Processing query...")
            
            # Call master agent
            result = await agent.process_query(
                user_query=test_case["query"],
                session_id=f"test_{i}_{int(datetime.now().timestamp())}"
            )
            
            # Analyze results
            tools_used = result.get("tools_used", [])
            execution_log = result.get("execution_log", [])
            response = result.get("response", "")
            confidence = result.get("confidence", 0.0)
            iterations = result.get("iterations", 0)
            
            # Check if sentiment analyzer was called
            sentiment_called = "sentiment_analysis_agent" in tools_used
            
            # Check execution log
            sentiment_in_log = any(
                "sentiment" in str(step).lower()
                for step in execution_log
            )
            
            print(f"\n📊 RESULTS:")
            print(f"   Response Length: {len(response)} chars")
            print(f"   Tools Used: {tools_used}")
            print(f"   Sentiment Analyzer Called: {'✅ YES' if sentiment_called else '❌ NO'}")
            print(f"   Sentiment in Execution Log: {'✅ YES' if sentiment_in_log else '⚠️  NO'}")
            print(f"   Confidence: {confidence:.2%}")
            print(f"   Iterations: {iterations}")
            
            # Show execution steps
            print(f"\n📋 EXECUTION STEPS:")
            for j, step in enumerate(execution_log[:5], 1):  # Show first 5 steps
                step_name = step.get("step", "unknown")
                action = step.get("action", "")
                print(f"   {j}. {step_name}: {action}")
            if len(execution_log) > 5:
                print(f"   ... and {len(execution_log) - 5} more steps")
            
            # Print response preview
            print(f"\n📝 RESPONSE PREVIEW:")
            print(f"   {response[:400]}...")
            
            # Determine test result
            expected = test_case["should_use_sentiment"]
            actual = sentiment_called or sentiment_in_log
            
            if expected == actual:
                test_passed = True
                status_msg = "✅ TEST PASSED"
            else:
                test_passed = False
                if expected:
                    status_msg = "❌ TEST FAILED - Expected sentiment analyzer to be called but it wasn't"
                else:
                    status_msg = "❌ TEST FAILED - Sentiment analyzer was called unexpectedly"
            
            print(f"\n{status_msg}")
            
            results.append({
                "test": test_case["name"],
                "passed": test_passed,
                "sentiment_called": sentiment_called,
                "tools_used": tools_used,
                "confidence": confidence
            })
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            results.append({
                "test": test_case["name"],
                "passed": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    
    passed = sum(1 for r in results if r.get("passed"))
    failed = len(results) - passed
    
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result.get("passed") else "❌"
        print(f"{status_icon} Test {i}: {result['test']}")
        if result.get("sentiment_called"):
            print(f"   Sentiment Analyzer: INVOKED")
        if result.get("tools_used"):
            print(f"   Tools: {', '.join(result['tools_used'])}")
        if result.get("confidence"):
            print(f"   Confidence: {result['confidence']:.2%}")
        if result.get("error"):
            print(f"   Error: {result['error']}")
        print()
    
    print(f"{'=' * 80}")
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print(f"{'=' * 80}")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("   ✅ Sentiment Analyzer is properly integrated")
        print("   ✅ Master agent can invoke it correctly")
        print("   ✅ Ready for server deployment")
    elif passed > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {passed}/{len(results)} tests passed")
    else:
        print("\n❌ ALL TESTS FAILED!")
    
    return passed == len(results)


if __name__ == "__main__":
    print("\n⚙️  Note: This test calls the master agent directly")
    print("   No server needs to be running\n")
    
    success = asyncio.run(test_sentiment_analyzer_direct())
    
    print("\n" + "=" * 80)
    if success:
        print("✅ INTEGRATION VERIFIED")
        print("=" * 80)
        print("\nNext Steps:")
        print("1. Start the server: uvicorn app:app --reload")
        print("2. Test via server: python test_sentiment_analyzer_integration.py")
    else:
        print("❌ INTEGRATION ISSUES DETECTED")
        print("=" * 80)
        print("\nReview the errors above and check:")
        print("1. All API keys are set in .env")
        print("2. Sentiment analyzer agent is in sub_agents/ folder")
        print("3. SubAgentCaller has call_sentiment_analyzer() method")
    
    exit(0 if success else 1)

