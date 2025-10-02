"""
Test Script for Debugging Master Agent Execution
Tests the sequence:
1. "how has india been affected by US tariffs"
2. "create a trend visualization of this data"

Logs detailed information at each node.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import asyncio
import json
from datetime import datetime
from langgraph_master_agent.main import MasterPoliticalAnalyst


def print_separator(title: str, char="="):
    """Print a visual separator"""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def print_state_snapshot(state: dict, node_name: str):
    """Print relevant state information after each node"""
    print_separator(f"STATE AFTER: {node_name.upper()}", "-")
    
    print("📋 Key State Fields:")
    print(f"   • Session ID: {state.get('session_id', 'N/A')}")
    print(f"   • Conversation History Length: {len(state.get('conversation_history', []))}")
    print(f"   • Iteration Count: {state.get('iteration_count', 0)}")
    print(f"   • Has Sufficient Info: {state.get('has_sufficient_info', False)}")
    print(f"   • Needs More Tools: {state.get('needs_more_tools', False)}")
    
    # Task Plan
    if state.get('task_plan'):
        print(f"\n📝 Task Plan:")
        print(f"   {state['task_plan'][:200]}...")
    
    # Tools to use
    if state.get('tools_to_use'):
        print(f"\n🔧 Tools Selected: {', '.join(state['tools_to_use'])}")
    
    # Tool Results
    if state.get('tool_results'):
        print(f"\n🔍 Tool Results:")
        for tool_name, result in state['tool_results'].items():
            if isinstance(result, dict):
                success = result.get('success', False)
                result_count = result.get('result_count', 0)
                print(f"   • {tool_name}: Success={success}, Results={result_count}")
            else:
                print(f"   • {tool_name}: {str(result)[:100]}")
    
    # Response
    if state.get('final_response'):
        print(f"\n💬 Final Response (first 300 chars):")
        print(f"   {state['final_response'][:300]}...")
    
    # Artifact decision
    if state.get('should_create_artifact') is not None:
        print(f"\n🎨 Artifact Decision:")
        print(f"   • Should Create: {state.get('should_create_artifact', False)}")
        print(f"   • Type: {state.get('artifact_type', 'N/A')}")
        if state.get('artifact_data'):
            data = state['artifact_data']
            print(f"   • Data Keys: {list(data.keys())}")
            if 'x' in data and 'y' in data:
                print(f"   • Data Points: x={len(data['x'])}, y={len(data['y'])}")
    
    # Artifact created
    if state.get('artifact'):
        print(f"\n✨ Artifact Created:")
        artifact = state['artifact']
        print(f"   • ID: {artifact.get('artifact_id', 'N/A')}")
        print(f"   • Type: {artifact.get('type', 'N/A')}")
        print(f"   • HTML Path: {artifact.get('html_path', 'N/A')}")
    
    # Errors
    if state.get('error_log'):
        print(f"\n⚠️  Errors: {len(state['error_log'])}")
        for error in state['error_log']:
            print(f"   • {error}")
    
    print()


def print_execution_log(state: dict):
    """Print the execution log"""
    print_separator("EXECUTION LOG", "=")
    
    execution_log = state.get('execution_log', [])
    for i, log_entry in enumerate(execution_log, 1):
        step = log_entry.get('step', 'unknown')
        action = log_entry.get('action', 'N/A')
        timestamp = log_entry.get('timestamp', 'N/A')
        
        print(f"{i}. [{step}] {action}")
        
        if log_entry.get('input'):
            print(f"   INPUT: {log_entry['input'][:150]}")
        
        if log_entry.get('output'):
            print(f"   OUTPUT: {log_entry['output'][:150]}")
        
        if log_entry.get('error'):
            print(f"   ERROR: {log_entry['error']}")
        
        print()


async def run_query_with_detailed_logging(agent, query: str, conversation_history: list = None, turn_number: int = 1):
    """Run a single query with detailed logging"""
    
    print_separator(f"TURN {turn_number}: Query Execution", "═")
    print(f"📝 User Query: \"{query}\"")
    print(f"📚 Conversation History: {len(conversation_history) if conversation_history else 0} messages")
    
    # We'll manually step through the graph to get state at each node
    # For now, run the full query and examine results
    
    print("\n🚀 Starting agent execution...\n")
    
    result = await agent.process_query(
        user_query=query,
        conversation_history=conversation_history,
        session_id=f"debug_session_{turn_number}"
    )
    
    print_separator("FINAL RESULT", "═")
    
    print("📊 Result Summary:")
    print(f"   • Response Length: {len(result.get('response', ''))} characters")
    print(f"   • Citations: {len(result.get('citations', []))}")
    print(f"   • Confidence: {result.get('confidence', 0):.2%}")
    print(f"   • Tools Used: {', '.join(result.get('tools_used', []))}")
    print(f"   • Iterations: {result.get('iterations', 0)}")
    print(f"   • Errors: {len(result.get('errors', []))}")
    
    print("\n💬 Response:")
    print("-" * 80)
    print(result.get('response', 'No response'))
    print("-" * 80)
    
    if result.get('should_create_artifact'):
        print("\n🎨 Artifact Information:")
        print(f"   • Type: {result.get('artifact_type', 'N/A')}")
        print(f"   • ID: {result.get('artifact_id', 'N/A')}")
        if result.get('artifact'):
            artifact = result['artifact']
            print(f"   • HTML: {artifact.get('html_path', 'N/A')}")
            print(f"   • PNG: {artifact.get('png_path', 'N/A')}")
    
    if result.get('citations'):
        print("\n📚 Citations:")
        for i, citation in enumerate(result['citations'][:3], 1):
            print(f"   {i}. {citation.get('title', 'N/A')}")
            print(f"      {citation.get('url', 'N/A')}")
    
    print("\n📝 Execution Log:")
    for i, log in enumerate(result.get('execution_log', []), 1):
        step = log.get('step', 'unknown')
        action = log.get('action', 'N/A')
        print(f"   {i}. [{step}] {action}")
    
    return result


async def main():
    """Main test function"""
    
    print("=" * 80)
    print("  MASTER AGENT DEBUG TEST")
    print("  Testing Query Sequence with Detailed Logging")
    print("=" * 80)
    
    # Initialize agent
    agent = MasterPoliticalAnalyst()
    
    # Maintain conversation history across turns
    conversation_history = []
    
    # TURN 1: Information gathering query
    query_1 = "how has india been affected by US tariffs"
    
    result_1 = await run_query_with_detailed_logging(
        agent=agent,
        query=query_1,
        conversation_history=conversation_history,
        turn_number=1
    )
    
    # Update conversation history with turn 1
    conversation_history.append({
        "role": "user",
        "content": query_1,
        "timestamp": datetime.now().isoformat()
    })
    conversation_history.append({
        "role": "assistant",
        "content": result_1.get('response', ''),
        "timestamp": datetime.now().isoformat()
    })
    
    # Wait a moment
    print("\n\n⏸️  Waiting 2 seconds before next query...\n")
    await asyncio.sleep(2)
    
    # TURN 2: Visualization request
    query_2 = "create a trend visualization of this data"
    
    result_2 = await run_query_with_detailed_logging(
        agent=agent,
        query=query_2,
        conversation_history=conversation_history,
        turn_number=2
    )
    
    # Final summary
    print_separator("TEST COMPLETE - SUMMARY", "═")
    
    print("✅ Turn 1 (Information Gathering):")
    print(f"   • Query: \"{query_1}\"")
    print(f"   • Tools Used: {', '.join(result_1.get('tools_used', []))}")
    print(f"   • Response Generated: {len(result_1.get('response', ''))} chars")
    print(f"   • Citations: {len(result_1.get('citations', []))}")
    
    print("\n✅ Turn 2 (Visualization Request):")
    print(f"   • Query: \"{query_2}\"")
    print(f"   • Tools Used: {', '.join(result_2.get('tools_used', []))}")
    print(f"   • Artifact Created: {result_2.get('should_create_artifact', False)}")
    if result_2.get('artifact'):
        print(f"   • Artifact Type: {result_2['artifact'].get('type', 'N/A')}")
        print(f"   • Artifact ID: {result_2['artifact'].get('artifact_id', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("  DEBUG OBSERVATIONS")
    print("=" * 80)
    
    print("\n🔍 Key Observations:")
    print("1. Strategic Planner (Turn 1):")
    print("   - Did the LLM correctly select tavily_search?")
    print("   - Was keyword fallback used? (Should be NO)")
    
    print("\n2. Strategic Planner (Turn 2):")
    print("   - Did the LLM recognize this as a visualization request?")
    print("   - Did it select appropriate tools?")
    
    print("\n3. Artifact Decision (Turn 2):")
    print("   - Did it detect the need for visualization?")
    print("   - Did it extract data from conversation history (Turn 1)?")
    print("   - Was structured data successfully extracted?")
    
    print("\n4. Conversation History:")
    print(f"   - Messages tracked: {len(conversation_history)}")
    print("   - Includes both turns: ✓" if len(conversation_history) >= 4 else "   - Missing messages")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

