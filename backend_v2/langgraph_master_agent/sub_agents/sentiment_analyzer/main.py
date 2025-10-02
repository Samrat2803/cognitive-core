"""
Standalone Runner for Sentiment Analyzer Agent

⚠️ IMPORTANT: This file allows testing the agent WITHOUT the master agent
DO NOT import anything from master agent except shared utilities
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add parent directories to path for shared modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# Import from current directory (simple imports like POCs)
from graph import create_sentiment_analyzer_graph
from state import SentimentAnalyzerState

# Test queries
TEST_QUERIES = [
    {
        "query": "nuclear energy policy",
        "countries": ["US", "France", "Germany", "Japan"],
        "time_range_days": 7
    },
    {
        "query": "climate change action",
        "countries": ["US", "UK", "India", "China"],
        "time_range_days": 7
    },
    {
        "query": "immigration policy",
        "countries": ["US", "UK", "Germany"],
        "time_range_days": 7
    }
]


async def run_standalone_test(query_config: dict):
    """
    Run agent in complete isolation
    
    Args:
        query_config: Dict with query, countries, time_range_days
    """
    
    print("\n" + "="*70)
    print(f"🚀 STANDALONE TEST: {query_config['query']}")
    print("="*70)
    
    # Create graph
    graph = create_sentiment_analyzer_graph()
    
    # Initialize state
    initial_state: SentimentAnalyzerState = {
        "query": query_config["query"],
        "countries": query_config["countries"],
        "time_range_days": query_config["time_range_days"],
        "search_results": {},
        "sentiment_scores": {},
        "bias_analysis": {},
        "summary": "",
        "key_findings": [],
        "confidence": 0.0,
        "artifacts": [],
        # NEW: Iteration control
        "iteration": 0,
        "should_iterate": False,
        "iteration_reason": "",
        "quality_metrics": {},
        "search_params": {},
        # Metadata
        "execution_log": [],
        "error_log": []
    }
    
    print(f"📝 Query: {query_config['query']}")
    print(f"🌍 Countries: {', '.join(query_config['countries'])}")
    print(f"📅 Time Range: {query_config['time_range_days']} days")
    print("\n⏳ Processing...")
    
    start_time = datetime.now()
    
    try:
        # Run agent
        result = await graph.ainvoke(initial_state)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Display results
        print(f"\n✅ SUCCESS (completed in {duration:.2f}s)")
        print("\n" + "-"*70)
        print("📊 RESULTS:")
        print("-"*70)
        
        # Sentiment scores
        print("\n🎭 Sentiment Scores:")
        for country, scores in result["sentiment_scores"].items():
            sentiment = scores.get("sentiment", "unknown")
            score = scores.get("score", 0)
            print(f"   {country:15} {sentiment:10} (score: {score:+.2f})")
        
        # Key findings
        print("\n🔍 Key Findings:")
        for i, finding in enumerate(result["key_findings"][:5], 1):
            print(f"   {i}. {finding}")
        
        # Bias analysis
        print("\n⚖️  Bias Analysis:")
        for country, bias in result["bias_analysis"].items():
            bias_types = bias.get("bias_types", [])
            if bias_types:
                print(f"   {country}: {', '.join(bias_types)}")
        
        # Artifacts
        print(f"\n🎨 Artifacts Generated: {len(result['artifacts'])}")
        for artifact in result["artifacts"]:
            print(f"   - {artifact['type']:20} {artifact['artifact_id']}")
            print(f"     HTML: {artifact.get('html_path', 'N/A')}")
            print(f"     PNG:  {artifact.get('png_path', 'N/A')}")
        
        # Confidence
        print(f"\n📈 Confidence: {result['confidence']:.2%}")
        
        # Execution log
        print(f"\n📋 Execution Log ({len(result['execution_log'])} steps):")
        for log_entry in result["execution_log"]:
            print(f"   [{log_entry['step']}] {log_entry['action']}")
        
        # Errors (if any)
        if result["error_log"]:
            print(f"\n⚠️  Errors Encountered ({len(result['error_log'])}):")
            for error in result["error_log"]:
                print(f"   - {error}")
        
        # Save result to file
        output_dir = "examples"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(
            output_dir, 
            f"test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_file, 'w') as f:
            # Remove non-serializable fields for JSON
            json_result = {
                "query": result.get("query"),
                "countries": result.get("countries"),
                "sentiment_scores": result.get("sentiment_scores"),
                "bias_analysis": result.get("bias_analysis"),
                "key_findings": result.get("key_findings"),
                "confidence": result.get("confidence"),
                "artifacts": result.get("artifacts"),
                "execution_log": result.get("execution_log"),
                "error_log": result.get("error_log"),
                "duration_seconds": duration
            }
            json.dump(json_result, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        print("\n" + "="*70)
        
        return result
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n❌ FAILED (after {duration:.2f}s)")
        print(f"Error: {str(e)}")
        print("\n" + "="*70)
        
        import traceback
        traceback.print_exc()
        
        return None


async def run_all_tests():
    """Run all test queries"""
    
    print("\n" + "🎯 "*35)
    print("SENTIMENT ANALYZER - STANDALONE TEST SUITE")
    print("🎯 "*35)
    print(f"\nTotal Tests: {len(TEST_QUERIES)}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for i, query_config in enumerate(TEST_QUERIES, 1):
        print(f"\n\n{'='*70}")
        print(f"TEST {i}/{len(TEST_QUERIES)}")
        print(f"{'='*70}")
        
        result = await run_standalone_test(query_config)
        results.append({
            "test_number": i,
            "query": query_config["query"],
            "success": result is not None,
            "result": result
        })
        
        # Pause between tests
        if i < len(TEST_QUERIES):
            print("\n⏸️  Pausing 2 seconds before next test...")
            await asyncio.sleep(2)
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {successful/len(results):.1%}")
    
    print("\nTest Results:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"   {status} Test {r['test_number']}: {r['query']}")
    
    print("\n" + "="*70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    return results


def main():
    """Main entry point"""
    
    # Check if specific test query provided
    if len(sys.argv) > 1:
        # Custom query from command line
        custom_query = {
            "query": " ".join(sys.argv[1:]),
            "countries": ["US", "UK", "France"],
            "time_range_days": 7
        }
        asyncio.run(run_standalone_test(custom_query))
    else:
        # Run all test queries
        asyncio.run(run_all_tests())


if __name__ == "__main__":
    print("\n" + "🔬 "*35)
    print("SENTIMENT ANALYZER AGENT - STANDALONE MODE")
    print("This tests the agent WITHOUT the master agent")
    print("🔬 "*35)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

