"""
Test Master Agent Delegation to New Sub-Agents

This test verifies that the Master Agent's Strategic Planner correctly:
1. Recognizes investigation queries
2. Delegates to investigative_journalist
3. Delegates to government_intelligence for gov info
4. Returns properly formatted results

This is the CORRECT way to test - through the Master Agent, not bypassing it!
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_master_agent.main import MasterPoliticalAnalyst


async def test_master_agent_delegation():
    print("="*80)
    print("🧪 MASTER AGENT DELEGATION TEST")
    print("="*80)
    print("Testing: Master Agent → Strategic Planner → Sub-Agent Delegation")
    print("")
    
    # Initialize Master Agent
    agent = MasterPoliticalAnalyst()
    
    # ========================================================================
    # TEST 1: Investigation Query (should delegate to investigative_journalist)
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 1: Investigation Query → investigative_journalist")
    print("="*80)
    
    query1 = "Investigate India cough syrup deaths"
    
    print(f"\n📋 User Query: \"{query1}\"")
    print("Expected: Master Agent delegates to investigative_journalist")
    print("")
    
    result1 = await agent.process_query(query1)
    
    print(f"\n✅ Response received:")
    print(f"   Response length: {len(result1.get('response', ''))} chars")
    
    # Check if investigative_journalist was used
    tools_used = result1.get('metadata', {}).get('tools_used', [])
    if 'investigative_journalist' in tools_used:
        print(f"   ✅ Correctly delegated to investigative_journalist")
    else:
        print(f"   ❌ Did NOT delegate to investigative_journalist")
        print(f"   Tools used: {tools_used}")
    
    # Show response preview
    response_preview = result1.get('response', '')[:300]
    print(f"\n📄 Response Preview:")
    print(f"   {response_preview}...")
    
    # ========================================================================
    # TEST 2: Government Query (should delegate to government_intelligence)
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 2: Government Query → government_intelligence")
    print("="*80)
    
    query2 = "What is the government response to cough syrup deaths?"
    
    print(f"\n📋 User Query: \"{query2}\"")
    print("Expected: Master Agent delegates to government_intelligence")
    print("")
    
    result2 = await agent.process_query(query2)
    
    print(f"\n✅ Response received:")
    print(f"   Response length: {len(result2.get('response', ''))} chars")
    
    # Check if government_intelligence was used
    tools_used2 = result2.get('metadata', {}).get('tools_used', [])
    if 'government_intelligence' in tools_used2:
        print(f"   ✅ Correctly delegated to government_intelligence")
    else:
        print(f"   ❌ Did NOT delegate to government_intelligence")
        print(f"   Tools used: {tools_used2}")
    
    # Show response preview
    response_preview2 = result2.get('response', '')[:300]
    print(f"\n📄 Response Preview:")
    print(f"   {response_preview2}...")
    
    # ========================================================================
    # TEST 3: Regular Query (should use tavily_search, not sub-agents)
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 3: Regular Query → tavily_search")
    print("="*80)
    
    query3 = "What's happening with Ukraine today?"
    
    print(f"\n📋 User Query: \"{query3}\"")
    print("Expected: Master Agent uses tavily_search (not sub-agents)")
    print("")
    
    result3 = await agent.process_query(query3)
    
    print(f"\n✅ Response received:")
    print(f"   Response length: {len(result3.get('response', ''))} chars")
    
    # Check tools used
    tools_used3 = result3.get('metadata', {}).get('tools_used', [])
    if 'tavily_search' in tools_used3 and 'investigative_journalist' not in tools_used3:
        print(f"   ✅ Correctly used tavily_search (not sub-agents)")
    else:
        print(f"   ⚠️  Unexpected tool selection")
        print(f"   Tools used: {tools_used3}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("📊 DELEGATION TEST SUMMARY")
    print("="*80)
    
    test_results = {
        "Investigation Query": 'investigative_journalist' in tools_used,
        "Government Query": 'government_intelligence' in tools_used2 if tools_used2 else False,
        "Regular Query": 'tavily_search' in tools_used3 and 'investigative_journalist' not in tools_used3
    }
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name:30s} {status}")
    
    all_passed = all(test_results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Master Agent delegation working correctly!")
    else:
        print("⚠️  SOME TESTS FAILED - Check Strategic Planner logic")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_master_agent_delegation())
    sys.exit(0 if success else 1)
