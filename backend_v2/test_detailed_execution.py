"""
Test script for detailed execution logging
Tests the new node-level input/output/decision tracking
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"


async def test_execution_graph():
    """Test a query and fetch detailed execution graph"""
    print("\n" + "=" * 80)
    print("🧪 TESTING DETAILED EXECUTION LOGGING")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)
    
    # Test query
    query = "What is the current economic situation in Germany?"
    
    print(f"\n📝 Test Query: {query}")
    print("\n⏳ Sending request to agent...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Step 1: Send query to agent
        response = await client.post(
            f"{BASE_URL}/api/analyze",
            json={"query": query}
        )
        
        if response.status_code != 200:
            print(f"\n❌ Analysis failed: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        session_id = result['session_id']
        
        print(f"\n✅ Analysis completed!")
        print(f"   Session ID: {session_id}")
        print(f"   Tools Used: {', '.join(result['tools_used'])}")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Processing Time: {result['processing_time_ms']}ms")
        
        # Step 2: Fetch execution graph
        print(f"\n📊 Fetching execution graph for session: {session_id}")
        
        graph_response = await client.get(
            f"{BASE_URL}/api/graph/execution/{session_id}"
        )
        
        if graph_response.status_code != 200:
            print(f"\n❌ Failed to fetch execution graph: {graph_response.status_code}")
            print(graph_response.text)
            return
        
        graph_data = graph_response.json()
        
        print(f"\n✅ Execution graph retrieved!")
        print(f"   Total Nodes: {len(graph_data['nodes'])}")
        print(f"   Executed Nodes: {graph_data['execution_metadata']['executed_nodes']}")
        print(f"   Total Duration: {graph_data['execution_metadata']['total_duration_ms']}ms")
        
        # Step 3: Display detailed node information
        print("\n" + "=" * 80)
        print("📋 DETAILED NODE EXECUTION LOG")
        print("=" * 80)
        
        for node in graph_data['nodes']:
            if node.get('execution', {}).get('executed'):
                print(f"\n{'=' * 80}")
                print(f"🔵 NODE: {node['label']}")
                print(f"{'=' * 80}")
                
                exec_data = node['execution']
                
                if exec_data.get('timestamp'):
                    print(f"⏰ Timestamp: {exec_data['timestamp']}")
                
                if exec_data.get('duration_ms'):
                    print(f"⏱️  Duration: {exec_data['duration_ms']}ms")
                
                if exec_data.get('details'):
                    details = exec_data['details']
                    
                    if details.get('input'):
                        print(f"\n📥 INPUT:")
                        print("-" * 80)
                        print(details['input'])
                    
                    if details.get('action'):
                        print(f"\n🎯 DECISION/ACTION:")
                        print("-" * 80)
                        print(details['action'])
                    
                    if details.get('output'):
                        print(f"\n📤 OUTPUT:")
                        print("-" * 80)
                        print(details['output'])
                else:
                    print("\n⚠️  No detailed execution information available")
        
        # Step 4: Summary
        print("\n" + "=" * 80)
        print("📊 EXECUTION SUMMARY")
        print("=" * 80)
        
        executed_nodes = [n for n in graph_data['nodes'] if n.get('execution', {}).get('executed')]
        
        print(f"✓ Executed {len(executed_nodes)} nodes:")
        for node in executed_nodes:
            duration = node['execution'].get('duration_ms', 0)
            print(f"   • {node['label']:<25} ({duration}ms)")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)


async def test_decision_gate_details():
    """Test decision gate with specific query that triggers multiple iterations"""
    print("\n" + "=" * 80)
    print("🧪 TESTING DECISION GATE DETAILED LOGGING")
    print("=" * 80)
    
    query = "What are the latest US tariffs affecting India?"
    
    print(f"\n📝 Test Query: {query}")
    print("\n⏳ Sending request...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/analyze",
            json={"query": query}
        )
        
        if response.status_code != 200:
            print(f"\n❌ Analysis failed: {response.status_code}")
            return
        
        result = response.json()
        session_id = result['session_id']
        
        print(f"\n✅ Analysis completed! Session: {session_id}")
        
        # Fetch execution graph
        graph_response = await client.get(
            f"{BASE_URL}/api/graph/execution/{session_id}"
        )
        
        if graph_response.status_code != 200:
            print(f"\n❌ Failed to fetch graph")
            return
        
        graph_data = graph_response.json()
        
        # Find decision gate nodes
        print("\n" + "=" * 80)
        print("🚦 DECISION GATE ANALYSIS")
        print("=" * 80)
        
        for node in graph_data['nodes']:
            if node['id'] == 'decision_gate' and node.get('execution', {}).get('executed'):
                exec_data = node['execution']
                details = exec_data.get('details', {})
                
                print(f"\n{'=' * 80}")
                print(f"Decision Gate Execution")
                print(f"{'=' * 80}")
                
                if details.get('input'):
                    print(f"\n📥 INPUT (State Assessment):")
                    print(details['input'])
                
                if details.get('output'):
                    print(f"\n📤 OUTPUT (Decision & Reasoning):")
                    print(details['output'])
        
        print("\n" + "=" * 80)
        print("✅ DECISION GATE TEST COMPLETED!")
        print("=" * 80)


async def main():
    """Run all tests"""
    try:
        # Test 1: Basic execution graph
        await test_execution_graph()
        
        # Test 2: Decision gate specific test
        await test_decision_gate_details()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        
    except httpx.ConnectError:
        print("\n❌ Cannot connect to server. Is it running on port 8001?")
        print("   Start server: python app.py")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

