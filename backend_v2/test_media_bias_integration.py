"""
Test Media Bias Detector Integration with Master Agent

This script tests that the master agent can properly delegate to the media bias detector sub-agent.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_master_agent.graph import create_master_agent_graph


async def test_media_bias_integration():
    """Test the media bias detector through the master agent"""
    
    print("=" * 80)
    print("MEDIA BIAS DETECTOR - INTEGRATION TEST")
    print("Testing master agent delegation to media bias detector sub-agent")
    print("=" * 80)
    
    # Initialize master agent graph
    master_graph = create_master_agent_graph()
    
    # Test query that should trigger media bias detector
    test_query = "Compare how CNN and Fox News cover climate change policy"
    
    print(f"\nTest Query: {test_query}")
    print("\nExpected: Master agent should delegate to media_bias_detector_agent")
    print("\n" + "-" * 80)
    
    try:
        # Create initial state
        initial_state = {
            "conversation_history": [
                {
                    "role": "user",
                    "content": test_query
                }
            ],
            "current_message": test_query,
            "tool_calls": [],
            "tool_results": {},
            "sub_agent_results": {},
            "execution_log": [],
            "error_log": [],
            "reasoning": "",
            "task_plan": ""
        }
        
        print("\n🚀 Running master agent...")
        print()
        
        # Run the graph
        result = await master_graph.ainvoke(initial_state)
        
        # Display results
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        
        # Check if media bias detector was called
        sub_agent_results = result.get("sub_agent_results", {})
        
        if "media_bias_detection" in sub_agent_results:
            bias_result = sub_agent_results["media_bias_detection"]
            
            print("\n✅ Media Bias Detector was called successfully!")
            print(f"\nStatus: {bias_result.get('status', 'UNKNOWN')}")
            print(f"Success: {bias_result.get('success', False)}")
            
            if bias_result.get("success"):
                data = bias_result.get("data", {})
                print(f"\n📊 Analysis Results:")
                print(f"  Sources Analyzed: {len(data.get('sources_analyzed', []))}")
                print(f"  Total Articles: {data.get('total_articles', 0)}")
                print(f"  Confidence: {data.get('confidence', 0.0):.2f}")
                
                if data.get('sources_analyzed'):
                    print(f"\n  Sources: {', '.join(data['sources_analyzed'])}")
                
                # Show bias classification
                bias_classification = data.get('bias_classification', {})
                if bias_classification:
                    print(f"\n  📰 Bias Classification:")
                    for source, classification in bias_classification.items():
                        print(f"    {source}: {classification.get('spectrum', 'N/A')} (score: {classification.get('bias_score', 0.0):.2f})")
                
                # Show key findings
                key_findings = data.get('key_findings', [])
                if key_findings:
                    print(f"\n  🔍 Key Findings:")
                    for i, finding in enumerate(key_findings[:3], 1):
                        print(f"    {i}. {finding}")
                
                # Show artifacts
                artifacts = data.get('artifacts', [])
                if artifacts:
                    print(f"\n  🎨 Artifacts Generated: {len(artifacts)}")
                    for artifact in artifacts:
                        print(f"    - {artifact.get('type', 'unknown')}: {artifact.get('title', 'N/A')}")
            else:
                print(f"\n❌ Media Bias Detector failed:")
                print(f"  Error: {bias_result.get('error', 'Unknown error')}")
        else:
            print("\n❌ Media Bias Detector was NOT called")
            print(f"\nSub-agents called: {list(sub_agent_results.keys())}")
            print("\nPossible reasons:")
            print("  1. Query didn't trigger media bias detector")
            print("  2. Strategic planner chose different tools")
            print("  3. Integration issue")
        
        # Show execution log
        execution_log = result.get("execution_log", [])
        if execution_log:
            print("\n" + "-" * 80)
            print("EXECUTION LOG")
            print("-" * 80)
            for log in execution_log[-10:]:  # Last 10 entries
                step = log.get('step', 'unknown')
                action = log.get('action', 'N/A')
                print(f"  [{step}] {action}")
        
        # Show errors if any
        error_log = result.get("error_log", [])
        if error_log:
            print("\n" + "-" * 80)
            print("ERRORS")
            print("-" * 80)
            for error in error_log:
                print(f"  ❌ {error}")
        
        # Show final response
        if result.get("conversation_history"):
            last_message = result["conversation_history"][-1]
            if last_message.get("role") == "assistant":
                print("\n" + "-" * 80)
                print("AGENT RESPONSE (First 500 chars)")
                print("-" * 80)
                print(last_message.get("content", "No response")[:500])
                if len(last_message.get("content", "")) > 500:
                    print("\n... (truncated)")
        
        print("\n" + "=" * 80)
        
        # Return success status
        return "media_bias_detection" in sub_agent_results
        
    except Exception as e:
        print(f"\n❌ ERROR during test:")
        print(f"   {type(e).__name__}: {str(e)}")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    print("\n🧪 Starting Media Bias Detector Integration Test\n")
    
    success = asyncio.run(test_media_bias_integration())
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED - Media Bias Detector integration working!")
    else:
        print("❌ TEST FAILED - Media Bias Detector not called or error occurred")
    print("=" * 80)
    print()

