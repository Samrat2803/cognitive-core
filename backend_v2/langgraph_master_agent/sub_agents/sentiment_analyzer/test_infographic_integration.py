"""
Test Sentiment Analyzer with Infographic Integration

This script tests the complete workflow including the new infographic generation.
"""

import sys
import os
import asyncio

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, '../../..'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(current_dir, '../../../.env'))

from state import SentimentAnalyzerState
from graph import create_sentiment_analyzer_graph


async def test_sentiment_analyzer_with_infographics():
    """Test the sentiment analyzer with infographic generation"""
    
    print("=" * 80)
    print("🧪 TESTING SENTIMENT ANALYZER WITH INFOGRAPHIC INTEGRATION")
    print("=" * 80)
    print()
    
    # Create test input
    test_query = "US Climate Policy"
    
    print(f"📝 Test Query: {test_query}")
    print()
    
    # Initialize state
    initial_state = {
        "query": test_query,
        "countries": ["US", "UK", "France"],
        "search_results": {},
        "sentiment_scores": {},
        "bias_analysis": {},
        "final_summary": "",
        "artifacts": [],
        "execution_log": []
    }
    
    # Create graph
    print("🔧 Creating sentiment analyzer graph...")
    graph = create_sentiment_analyzer_graph()
    print("✅ Graph created")
    print()
    
    # Run workflow
    print("🚀 Running workflow...")
    print("-" * 80)
    
    try:
        final_state = await graph.ainvoke(initial_state)
        
        print()
        print("=" * 80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print()
        
        # Print results
        print("📊 RESULTS:")
        print("-" * 80)
        
        print(f"\n1. Sentiment Scores:")
        for country, score_data in final_state.get("sentiment_scores", {}).items():
            # score_data is a dict with keys: positive, negative, neutral, score
            score = score_data.get('score', 0) if isinstance(score_data, dict) else score_data
            print(f"   • {country}: {score:.1%}")
        
        print(f"\n2. Artifacts Generated: {len(final_state.get('artifacts', []))}")
        for i, artifact in enumerate(final_state.get("artifacts", []), 1):
            artifact_type = artifact.get("type", "unknown")
            artifact_id = artifact.get("artifact_id", "N/A")
            path = artifact.get("path", "N/A")
            
            print(f"   {i}. {artifact_type}")
            print(f"      ID: {artifact_id}")
            print(f"      Path: {path}")
            
            # Check if it's an infographic
            if "infographic" in artifact_type.lower() or "infographic" in artifact_id.lower():
                print(f"      ✨ INFOGRAPHIC DETECTED!")
        
        print(f"\n3. Final Summary:")
        summary = final_state.get("final_summary", "No summary")
        print(f"   {summary[:200]}..." if len(summary) > 200 else f"   {summary}")
        
        print()
        print("=" * 80)
        print("🎨 INFOGRAPHIC TEST RESULTS")
        print("=" * 80)
        
        # Check for infographics specifically
        infographics = [a for a in final_state.get("artifacts", []) 
                       if "infographic" in a.get("type", "").lower() 
                       or "infographic" in a.get("artifact_id", "").lower()]
        
        if infographics:
            print(f"\n✅ {len(infographics)} INFOGRAPHIC(S) CREATED!")
            for i, infographic in enumerate(infographics, 1):
                print(f"\n   Infographic {i}:")
                print(f"   • Type: {infographic.get('type', 'N/A')}")
                print(f"   • Schema: {infographic.get('schema_type', 'N/A')}")
                print(f"   • Template: {infographic.get('visual_template', 'N/A')}")
                print(f"   • Path: {infographic.get('path', 'N/A')}")
                print(f"   • Size: {infographic.get('size_bytes', 0) / 1024:.1f} KB")
            
            print()
            print("🌐 To view infographics:")
            for infographic in infographics:
                print(f"   open {infographic.get('path', '')}")
        else:
            print("\n❌ NO INFOGRAPHICS CREATED")
            print("   Check error messages above")
        
        print()
        print("=" * 80)
        
        # Open infographics in browser
        if infographics:
            print("\n🌐 Opening infographics in browser...")
            for infographic in infographics:
                path = infographic.get('path', '')
                if path and os.path.exists(path):
                    os.system(f"open '{path}'")
            print("   ✅ Infographics opened")
        
        return final_state
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ WORKFLOW FAILED")
        print("=" * 80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    print()
    result = asyncio.run(test_sentiment_analyzer_with_infographics())
    print()
    print("🎉 Test complete!")

