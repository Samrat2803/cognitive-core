"""
Test Master Agent with various queries
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import asyncio
from langgraph_master_agent.main import MasterPoliticalAnalyst


async def test_basic_search():
    """Test basic search functionality"""
    print("\n" + "="*70)
    print("TEST 1: Basic Search Query")
    print("="*70)
    
    agent = MasterPoliticalAnalyst()
    result = await agent.process_query("What happened in the US elections today?")
    
    print("\n📝 RESPONSE:")
    print(result["response"])
    print(f"\n📊 Confidence: {result['confidence']}")
    print(f"🔧 Tools Used: {', '.join(result['tools_used'])}")
    print(f"🔄 Iterations: {result['iterations']}")
    print(f"📚 Citations: {len(result['citations'])}")
    
    return result


async def test_sentiment_analysis():
    """Test sentiment analysis delegation (will use placeholder)"""
    print("\n" + "="*70)
    print("TEST 2: Sentiment Analysis (Sub-agent)")
    print("="*70)
    
    agent = MasterPoliticalAnalyst()
    result = await agent.process_query("Analyze global sentiment on climate change")
    
    print("\n📝 RESPONSE:")
    print(result["response"])
    print(f"\n📊 Confidence: {result['confidence']}")
    print(f"🔧 Tools Used: {', '.join(result['tools_used'])}")
    
    return result


async def test_multi_turn():
    """Test multi-turn conversation"""
    print("\n" + "="*70)
    print("TEST 3: Multi-turn Conversation")
    print("="*70)
    
    agent = MasterPoliticalAnalyst()
    
    # First query
    print("\n👤 User: Tell me about AI regulation in the EU")
    result1 = await agent.process_query("Tell me about AI regulation in the EU")
    print(f"\n🤖 Assistant: {result1['response'][:200]}...")
    
    # Follow-up (Note: This creates new session - for demo purposes)
    print("\n👤 User: How does that compare to US policy?")
    result2 = await agent.process_query("How does that compare to US policy?")
    print(f"\n🤖 Assistant: {result2['response'][:200]}...")
    
    return result1, result2


async def test_with_execution_log():
    """Test with detailed execution logging"""
    print("\n" + "="*70)
    print("TEST 4: Detailed Execution Logging")
    print("="*70)
    
    def log_callback(result):
        print("\n🔍 EXECUTION LOG:")
        for step in result.get("execution_log", []):
            print(f"  [{step.get('step', 'unknown')}] {step.get('action', '')}")
    
    agent = MasterPoliticalAnalyst(update_callback=log_callback)
    result = await agent.process_query("Find information about renewable energy policies")
    
    print(f"\n📊 Final Confidence: {result['confidence']}")
    
    return result


async def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀"*35)
    print("MASTER AGENT TEST SUITE")
    print("🚀"*35)
    
    try:
        # Test 1
        await test_basic_search()
        input("\n⏸️  Press Enter to continue to Test 2...")
        
        # Test 2
        await test_sentiment_analysis()
        input("\n⏸️  Press Enter to continue to Test 3...")
        
        # Test 3
        await test_multi_turn()
        input("\n⏸️  Press Enter to continue to Test 4...")
        
        # Test 4
        await test_with_execution_log()
        
        print("\n" + "✅"*35)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅"*35)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run specific test or all tests
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        if test_name == "basic":
            asyncio.run(test_basic_search())
        elif test_name == "sentiment":
            asyncio.run(test_sentiment_analysis())
        elif test_name == "multi":
            asyncio.run(test_multi_turn())
        elif test_name == "log":
            asyncio.run(test_with_execution_log())
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: basic, sentiment, multi, log")
    else:
        # Run all tests
        asyncio.run(run_all_tests())

