"""
Test Master Agent with Artifact Creation
Query: Create a trend chart of India's GDP growth rate over 2020-2025
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import asyncio
from langgraph_master_agent.main import MasterPoliticalAnalyst


async def test_gdp_query():
    """Test with India GDP growth query"""
    
    query = "Create a trend chart of India's GDP growth rate over the period 2020-2025"
    
    print("=" * 70)
    print("🎯 TESTING MASTER AGENT WITH ARTIFACT CREATION")
    print("=" * 70)
    print(f"\n📝 Query: {query}\n")
    print("=" * 70)
    
    # Initialize agent
    agent = MasterPoliticalAnalyst()
    
    # Process query
    result = await agent.process_query(query)
    
    # Display results
    print("\n✅ AGENT RESPONSE:")
    print("=" * 70)
    print(result['response'])
    print("=" * 70)
    
    print(f"\n📊 EXECUTION SUMMARY:")
    print(f"   Tools Used: {', '.join(result['tools_used'])}")
    print(f"   Iterations: {result['iterations']}")
    print(f"   Confidence: {result['confidence']:.0%}")
    print(f"   Citations: {len(result['citations'])}")
    
    # Check if artifact was created
    if result.get('artifact'):
        artifact = result['artifact']
        print(f"\n🎨 ARTIFACT CREATED!")
        print(f"   Type: {artifact.get('type', 'unknown')}")
        print(f"   ID: {artifact.get('artifact_id', 'N/A')}")
        print(f"   Title: {artifact.get('title', 'N/A')}")
        print(f"   HTML: {artifact.get('html_path', 'N/A')}")
        print(f"   PNG: {artifact.get('png_path', 'N/A')}")
        
        # Check if files exist
        html_exists = os.path.exists(artifact.get('html_path', ''))
        png_exists = os.path.exists(artifact.get('png_path', ''))
        
        print(f"\n   Files Created:")
        print(f"   ✅ HTML: {html_exists}")
        print(f"   ✅ PNG: {png_exists}")
        
        if html_exists:
            print(f"\n   📂 Open in browser: file://{os.path.abspath(artifact['html_path'])}")
    else:
        print(f"\n⚠️  NO ARTIFACT CREATED")
        print(f"   Should create artifact: {result.get('should_create_artifact', 'N/A')}")
        print(f"   Artifact type: {result.get('artifact_type', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("📋 EXECUTION LOG:")
    print("=" * 70)
    for i, log in enumerate(result.get('execution_log', []), 1):
        print(f"\n{i}. {log.get('step', 'Unknown')} - {log.get('action', '')}")
        if 'input' in log:
            print(f"   📥 Input: {log['input']}")
        if 'output' in log:
            print(f"   📤 Output: {log['output']}")
    
    print("\n" + "=" * 70)
    

if __name__ == "__main__":
    try:
        asyncio.run(test_gdp_query())
        print("\n✅ TEST COMPLETED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

