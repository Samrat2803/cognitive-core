"""
Test Context Awareness - Proves the fix works

Simulates the exact user scenario:
1. Ask for sentiment on Hamas in US and Israel
2. Ask for map visualization (should NOT re-run sentiment)
"""

import asyncio
import sys
import os
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langgraph_master_agent.main import MasterPoliticalAnalyst

async def test_context_awareness():
    """Test that second query doesn't re-run sentiment analysis"""
    
    print("\n" + "="*80)
    print("🧪 CONTEXT AWARENESS TEST")
    print("="*80)
    print("\nScenario: User asks for sentiment, then asks for map")
    print("Expected: Map is created WITHOUT re-running sentiment analysis")
    print("\n" + "="*80)
    
    agent = MasterPoliticalAnalyst()
    
    # =======================================================================
    # ROUND 1: Ask for sentiment analysis
    # =======================================================================
    print("\n" + "🎬 "*40)
    print("ROUND 1: Sentiment Analysis Request")
    print("🎬 "*40)
    
    query1 = "sentiment on Hamas in US and Israel"
    print(f"\n📝 Query 1: '{query1}'")
    print("⏳ Processing...")
    
    start1 = datetime.now()
    result1 = await agent.process_query(
        user_query=query1,
        conversation_history=[],
        session_id="test_session_123"
    )
    duration1 = (datetime.now() - start1).total_seconds()
    
    print(f"\n✅ ROUND 1 COMPLETE ({duration1:.1f}s)")
    print("\n📊 Results:")
    
    # Check if sentiment analyzer was called
    sub_agents = result1.get('sub_agent_results', {})
    if 'sentiment_analysis' in sub_agents:
        print("   ✅ Sentiment analyzer was called (expected)")
        sentiment_data = sub_agents['sentiment_analysis'].get('data', {})
        sentiment_scores = sentiment_data.get('sentiment_scores', {})
        
        if sentiment_scores:
            print("\n   📈 Sentiment Scores:")
            for country, scores in sentiment_scores.items():
                score = scores.get('score', 0)
                sentiment = scores.get('sentiment', 'unknown')
                print(f"      {country:15} {sentiment:10} (score: {score:+.2f})")
        
        artifacts = sub_agents['sentiment_analysis'].get('artifacts', [])
        print(f"\n   🎨 Artifacts created: {len(artifacts)}")
        for artifact in artifacts:
            print(f"      - {artifact.get('type', 'unknown')}")
    else:
        print("   ❌ Sentiment analyzer was NOT called (unexpected!)")
    
    # Build conversation history for next query
    conversation_history = [
        {
            "role": "user",
            "content": query1,
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant",
            "content": result1.get('response', ''),
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # =======================================================================
    # ROUND 2: Ask for map visualization (should use existing data!)
    # =======================================================================
    print("\n" + "🎬 "*40)
    print("ROUND 2: Map Visualization Request")
    print("🎬 "*40)
    
    query2 = "create a map visualization for the data"
    print(f"\n📝 Query 2: '{query2}'")
    print("⏳ Processing...")
    
    start2 = datetime.now()
    result2 = await agent.process_query(
        user_query=query2,
        conversation_history=conversation_history,
        session_id="test_session_123"
    )
    duration2 = (datetime.now() - start2).total_seconds()
    
    print(f"\n✅ ROUND 2 COMPLETE ({duration2:.1f}s)")
    
    # =======================================================================
    # PROOF: Check if sentiment analyzer was called in Round 2
    # =======================================================================
    print("\n" + "="*80)
    print("🔍 PROOF: Was sentiment analyzer called in Round 2?")
    print("="*80)
    
    sub_agents2 = result2.get('sub_agent_results', {})
    tools_used = result2.get('tools_used', [])
    
    print(f"\n📋 Tools used in Round 2: {tools_used if tools_used else '(none)'}")
    
    if 'sentiment_analysis' in sub_agents2:
        print("\n❌ FAILED: Sentiment analyzer was called AGAIN!")
        print("   This is the bug - it should NOT re-run!")
        print("\n   Sentiment scores from Round 2:")
        sentiment_data2 = sub_agents2['sentiment_analysis'].get('data', {})
        sentiment_scores2 = sentiment_data2.get('sentiment_scores', {})
        for country, scores in sentiment_scores2.items():
            score = scores.get('score', 0)
            print(f"      {country}: {score:+.2f}")
        success = False
    else:
        print("\n✅ SUCCESS: Sentiment analyzer was NOT called!")
        print("   The agent correctly reused data from Round 1")
        success = True
    
    # Check if artifact was created
    artifact = result2.get('artifact')
    if artifact:
        artifact_type = artifact.get('type', 'unknown')
        print(f"\n✅ Artifact created: {artifact_type}")
        if artifact_type == 'map_chart':
            print("   ✅ Correct type: map_chart")
        else:
            print(f"   ⚠️  Expected map_chart, got {artifact_type}")
    else:
        print("\n⚠️  No artifact created")
    
    # =======================================================================
    # SUMMARY
    # =======================================================================
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    print(f"\nRound 1 (Sentiment Analysis): {duration1:.1f}s")
    print(f"Round 2 (Map Visualization):  {duration2:.1f}s")
    
    if success:
        print("\n🎉 TEST PASSED!")
        print(f"   ✅ Round 2 was {duration1 - duration2:.1f}s faster (no re-analysis)")
        print("   ✅ Context awareness is working correctly")
    else:
        print("\n❌ TEST FAILED!")
        print("   ❌ Sentiment analyzer was called twice")
        print("   ❌ Context awareness is NOT working")
    
    print("\n" + "="*80)
    
    return success


if __name__ == "__main__":
    print("\n" + "🔬 "*40)
    print("CONTEXT AWARENESS PROOF TEST")
    print("🔬 "*40)
    
    try:
        success = asyncio.run(test_context_awareness())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n\n❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

