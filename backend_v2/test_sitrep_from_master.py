"""
Test SitRep Generator Integration with Master Agent

This test verifies that the master agent can successfully call the SitRep Generator sub-agent.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the path to import from langgraph_master_agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'langgraph_master_agent'))

from tools.sub_agent_caller import SubAgentCaller


async def test_master_agent_calls_sitrep():
    """
    Test that master agent can call SitRep Generator
    """
    
    print("=" * 80)
    print("🧪 TEST: Master Agent → SitRep Generator Integration")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize SubAgentCaller (this is what master agent uses)
    caller = SubAgentCaller()
    
    print("1️⃣  Master Agent initializing SubAgentCaller...")
    print("   ✅ SubAgentCaller initialized\n")
    
    # Test 1: Daily SitRep
    print("=" * 80)
    print("TEST 1: Generate Daily SitRep")
    print("=" * 80)
    
    start_time = datetime.now()
    
    print("📋 Master Agent: Calling call_sitrep_generator(period='daily')...")
    
    result = await caller.call_sitrep_generator(
        period="daily",
        region_focus=None,
        topic_focus=None
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"\n✅ Master Agent: Received response in {duration:.1f}s")
    print(f"   Status: {result.get('status')}")
    print(f"   Success: {result.get('success')}")
    
    # Validate response
    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)
    
    validations = []
    
    # Check success
    if result.get("success"):
        print("✅ Integration successful")
        validations.append(True)
    else:
        print(f"❌ Integration failed: {result.get('error', 'Unknown error')}")
        validations.append(False)
        return False
    
    # Check data exists
    data = result.get("data", {})
    if data:
        print("✅ Data returned from sub-agent")
        validations.append(True)
    else:
        print("❌ No data returned")
        validations.append(False)
    
    # Check executive summary
    exec_summary = data.get("executive_summary", "")
    if exec_summary and len(exec_summary) > 100:
        print(f"✅ Executive summary generated ({len(exec_summary)} chars)")
        validations.append(True)
    else:
        print("❌ Executive summary missing or too short")
        validations.append(False)
    
    # Check events
    event_count = data.get("event_count", 0)
    if event_count > 0:
        print(f"✅ Events processed: {event_count}")
        validations.append(True)
    else:
        print("❌ No events processed")
        validations.append(False)
    
    # Check artifacts
    artifacts = data.get("artifacts", [])
    if artifacts and len(artifacts) >= 3:
        print(f"✅ Artifacts generated: {len(artifacts)}")
        for artifact in artifacts:
            print(f"   - {artifact['type'].upper()}: {artifact['size_kb']:.1f} KB")
        validations.append(True)
    else:
        print("❌ Insufficient artifacts")
        validations.append(False)
    
    # Check priority breakdown
    urgent = len(data.get("urgent_events", []))
    high = len(data.get("high_priority_events", []))
    notable = len(data.get("notable_events", []))
    
    print(f"\n📊 Priority Breakdown:")
    print(f"   🔴 URGENT: {urgent}")
    print(f"   🟠 HIGH: {high}")
    print(f"   🟡 NOTABLE: {notable}")
    
    # Display executive summary
    print(f"\n📝 Executive Summary:")
    print(f"{exec_summary[:300]}...")
    
    # Display trending topics
    topics = data.get("trending_topics", [])
    if topics:
        print(f"\n🔥 Trending Topics:")
        print(f"   {', '.join(topics[:5])}")
    
    # Display watch list sample
    watch_list = data.get("watch_list", [])
    if watch_list:
        print(f"\n👁️  Watch List (first 3):")
        for i, item in enumerate(watch_list[:3], 1):
            print(f"   {i}. {item[:100]}...")
    
    # Test 2: Regional Focus
    print("\n" + "=" * 80)
    print("TEST 2: Generate SitRep with Regional Focus")
    print("=" * 80)
    
    print("📋 Master Agent: Calling call_sitrep_generator(period='daily', region_focus='Middle East')...")
    
    result2 = await caller.call_sitrep_generator(
        period="daily",
        region_focus="Middle East"
    )
    
    if result2.get("success"):
        print("✅ Regional filter test passed")
        validations.append(True)
    else:
        print(f"❌ Regional filter test failed: {result2.get('error')}")
        validations.append(False)
    
    # Final Results
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    passed = sum(validations)
    total = len(validations)
    success_rate = (passed / total) * 100
    
    print(f"\nTests Passed: {passed}/{total} ({success_rate:.0f}%)")
    
    if success_rate >= 90:
        print("\n🎉 INTEGRATION TEST: ✅ PASSED")
        print("\n✅ SitRep Generator is successfully integrated with Master Agent!")
        print("✅ Master agent can call SitRep Generator via sub_agent_caller.py")
        print("✅ All data flows correctly")
        return True
    else:
        print("\n❌ INTEGRATION TEST: ❌ FAILED")
        print("\nSome integration issues found")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting Master Agent Integration Test\n")
    
    success = asyncio.run(test_master_agent_calls_sitrep())
    
    if success:
        print("\n" + "=" * 80)
        print("✅ MASTER AGENT INTEGRATION COMPLETE!")
        print("=" * 80)
        print("\nThe master agent can now:")
        print("  1. Call SitRep Generator via call_sitrep_generator()")
        print("  2. Receive structured data and artifacts")
        print("  3. Display results to users")
        print("\nNext: Update strategic planner to route SitRep requests")
        exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ Integration test failed")
        print("=" * 80)
        exit(1)

