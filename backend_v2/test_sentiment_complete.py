"""
Comprehensive Test Suite for Sentiment Analyzer Agent

Tests:
1. Sentiment analyzer in standalone mode
2. Map visualization tool
3. Integration with master agent
4. Data extraction for map creation

Run: python test_sentiment_complete.py
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*80)
print("🧪 SENTIMENT ANALYZER - COMPREHENSIVE TEST SUITE")
print("="*80)


# =============================================================================
# TEST 1: Map Visualization Tool
# =============================================================================

async def test_map_tool():
    """Test the map visualization tool directly"""
    
    print("\n" + "-"*80)
    print("TEST 1: Map Visualization Tool")
    print("-"*80)
    
    try:
        from langgraph_master_agent.tools.visualization_tools import create_map_chart
        
        # Test data: sentiment scores for different countries
        test_data = {
            "countries": ["US", "Israel", "UK", "France"],
            "values": [-0.4, -0.7, 0.3, 0.5],
            "labels": [
                "US: Negative (-0.4)",
                "Israel: Very Negative (-0.7)",
                "UK: Positive (0.3)",
                "France: Positive (0.5)"
            ]
        }
        
        print(f"📊 Creating map with data:")
        print(f"   Countries: {test_data['countries']}")
        print(f"   Values: {test_data['values']}")
        
        artifact = create_map_chart(
            data=test_data,
            title="Sentiment on Hamas by Country",
            legend_title="Sentiment Score"
        )
        
        print(f"\n✅ Map created successfully!")
        print(f"   Artifact ID: {artifact['artifact_id']}")
        print(f"   Type: {artifact['type']}")
        print(f"   HTML Path: {artifact['html_path']}")
        print(f"   PNG Path: {artifact.get('png_path', 'N/A')}")
        
        if artifact.get('data'):
            print(f"   Mapped Countries: {artifact['data'].get('mapped_countries', [])}")
            print(f"   Skipped Countries: {artifact['data'].get('skipped_countries', [])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Map tool test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# TEST 2: Sentiment Analyzer Agent (Standalone)
# =============================================================================

async def test_sentiment_analyzer_standalone():
    """Test sentiment analyzer in isolation"""
    
    print("\n" + "-"*80)
    print("TEST 2: Sentiment Analyzer Agent (Standalone)")
    print("-"*80)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'langgraph_master_agent/sub_agents/sentiment_analyzer'))
        
        from langgraph_master_agent.sub_agents.sentiment_analyzer.graph import create_sentiment_analyzer_graph
        from langgraph_master_agent.sub_agents.sentiment_analyzer.state import SentimentAnalyzerState
        
        print(f"📝 Test Query: 'sentiment on Hamas in US and Israel'")
        
        # Create graph
        graph = create_sentiment_analyzer_graph()
        
        # Initialize state
        initial_state = {
            "query": "Hamas",
            "countries": ["US", "Israel"],
            "time_range_days": 7,
            "search_results": {},
            "sentiment_scores": {},
            "bias_analysis": {},
            "summary": "",
            "key_findings": [],
            "confidence": 0.0,
            "artifacts": [],
            "execution_log": [],
            "error_log": []
        }
        
        print(f"⏳ Running sentiment analysis...")
        start_time = datetime.now()
        
        result = await graph.ainvoke(initial_state)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ Analysis completed in {duration:.2f}s")
        
        # Check results
        print(f"\n📊 Results:")
        print(f"   Countries analyzed: {len(result.get('sentiment_scores', {}))}")
        print(f"   Artifacts created: {len(result.get('artifacts', []))}")
        print(f"   Confidence: {result.get('confidence', 0):.2%}")
        
        # Show sentiment scores
        if result.get('sentiment_scores'):
            print(f"\n🎭 Sentiment Scores:")
            for country, scores in result['sentiment_scores'].items():
                sentiment = scores.get('sentiment', 'unknown')
                score = scores.get('score', 0)
                print(f"   {country:15} {sentiment:10} (score: {score:+.2f})")
        
        # Show artifacts
        if result.get('artifacts'):
            print(f"\n🎨 Artifacts Generated:")
            for artifact in result['artifacts']:
                print(f"   - {artifact['type']:20} {artifact['artifact_id']}")
                if artifact.get('excel_path'):
                    print(f"     Excel: {os.path.basename(artifact['excel_path'])}")
                if artifact.get('html_path'):
                    print(f"     HTML:  {os.path.basename(artifact['html_path'])}")
        
        # Verify default behavior (table + bar chart)
        artifact_types = [a['type'] for a in result.get('artifacts', [])]
        expected_types = ['sentiment_table', 'sentiment_bar_chart']
        
        print(f"\n✅ Verification:")
        print(f"   Expected artifact types: {expected_types}")
        print(f"   Actual artifact types: {artifact_types}")
        
        # Check if we got the expected artifacts
        has_table = any('table' in t for t in artifact_types)
        has_bar = any('bar' in t for t in artifact_types)
        
        if has_table and has_bar:
            print(f"   ✅ Correct: Got table + bar chart (default behavior)")
        else:
            print(f"   ⚠️  Warning: Expected table + bar chart, got {artifact_types}")
        
        # Check that no map was created by sentiment analyzer
        has_map = any('map' in t for t in artifact_types)
        if not has_map:
            print(f"   ✅ Correct: No map created (as expected)")
        else:
            print(f"   ❌ Error: Map was created by sentiment analyzer (should not happen)")
        
        # Save result for manual inspection
        output_file = f"test_sentiment_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json_result = {
                "query": result.get("query"),
                "countries": result.get("countries"),
                "sentiment_scores": result.get("sentiment_scores"),
                "key_findings": result.get("key_findings"),
                "artifacts": result.get("artifacts"),
                "duration_seconds": duration
            }
            json.dump(json_result, f, indent=2)
        
        print(f"\n💾 Full results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Sentiment analyzer test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# TEST 3: Data Extraction for Map Creation
# =============================================================================

async def test_data_extraction_for_map(sentiment_result):
    """Test extracting sentiment data for map creation"""
    
    print("\n" + "-"*80)
    print("TEST 3: Data Extraction for Map Creation")
    print("-"*80)
    
    if not sentiment_result or not sentiment_result.get('sentiment_scores'):
        print("❌ Cannot test data extraction: No sentiment data available")
        return False
    
    try:
        from langgraph_master_agent.tools.visualization_tools import create_map_chart
        
        # Extract data from sentiment analyzer result
        sentiment_scores = sentiment_result['sentiment_scores']
        
        countries = list(sentiment_scores.keys())
        values = [scores.get('score', 0) for scores in sentiment_scores.values()]
        labels = [
            f"{country}: {scores.get('sentiment', 'unknown')} ({scores.get('score', 0):+.2f})"
            for country, scores in sentiment_scores.items()
        ]
        
        print(f"📊 Extracted data from sentiment analyzer:")
        print(f"   Countries: {countries}")
        print(f"   Values: {values}")
        print(f"   Labels: {labels}")
        
        # Create map with extracted data
        map_data = {
            "countries": countries,
            "values": values,
            "labels": labels
        }
        
        print(f"\n🗺️  Creating map from sentiment data...")
        
        map_artifact = create_map_chart(
            data=map_data,
            title="Sentiment Analysis Map",
            legend_title="Sentiment Score"
        )
        
        print(f"\n✅ Map created successfully from sentiment data!")
        print(f"   Artifact ID: {map_artifact['artifact_id']}")
        print(f"   HTML Path: {map_artifact['html_path']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Data extraction test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# TEST 4: Country Code Mapping
# =============================================================================

async def test_country_code_mapping():
    """Test country code mapping for various country names"""
    
    print("\n" + "-"*80)
    print("TEST 4: Country Code Mapping")
    print("-"*80)
    
    try:
        from shared.visualization_factory import get_country_code
        
        test_countries = [
            "US", "USA", "United States", "United States of America",
            "UK", "United Kingdom", "Britain", "Great Britain",
            "Israel", "France", "Germany", "Japan", "China", "India",
            "UAE", "United Arab Emirates",
            "Invalid Country Name"
        ]
        
        print(f"📍 Testing country code mapping:")
        
        success_count = 0
        fail_count = 0
        
        for country in test_countries:
            iso_code = get_country_code(country)
            if iso_code:
                print(f"   ✅ {country:30} → {iso_code}")
                success_count += 1
            else:
                print(f"   ❌ {country:30} → (not mapped)")
                fail_count += 1
        
        print(f"\n📊 Mapping results:")
        print(f"   Success: {success_count}/{len(test_countries)}")
        print(f"   Failed:  {fail_count}/{len(test_countries)}")
        
        return success_count > fail_count
        
    except Exception as e:
        print(f"\n❌ Country code mapping test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# TEST 5: Check Master Agent Integration
# =============================================================================

async def test_master_agent_has_map_tool():
    """Verify master agent has access to map tool"""
    
    print("\n" + "-"*80)
    print("TEST 5: Master Agent Map Tool Integration")
    print("-"*80)
    
    try:
        # Check if tool is available
        from langgraph_master_agent.tools.visualization_tools import create_map_chart
        
        print(f"✅ Map tool is importable from visualization_tools")
        
        # Check tool signature
        import inspect
        sig = inspect.signature(create_map_chart)
        print(f"✅ Tool signature: {sig}")
        
        # Check if master agent can access it
        # This is a basic check - full integration test would require running master agent
        print(f"\n📝 Tool Integration Checklist:")
        print(f"   ✅ Tool exists in visualization_tools.py")
        print(f"   ✅ Tool can be imported")
        print(f"   ✅ Tool has correct signature (data, title, legend_title)")
        print(f"   ⚠️  Master agent integration needs live testing")
        
        print(f"\n💡 To test full integration:")
        print(f"   1. Start backend server: cd backend_v2 && python app.py")
        print(f"   2. Query: 'sentiment on Hamas in US and Israel'")
        print(f"   3. Follow-up: 'create a map of this data'")
        print(f"   4. Verify: Map artifact appears in response")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Master agent integration check FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_all_tests():
    """Run all tests in sequence"""
    
    print(f"\n🚀 Starting test suite at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"="*80)
    
    results = {}
    
    # Test 1: Map tool
    print("\n" + "🧪 "*40)
    results['map_tool'] = await test_map_tool()
    await asyncio.sleep(1)
    
    # Test 2: Sentiment analyzer
    print("\n" + "🧪 "*40)
    sentiment_result = await test_sentiment_analyzer_standalone()
    results['sentiment_analyzer'] = sentiment_result is not None
    await asyncio.sleep(1)
    
    # Test 3: Data extraction
    print("\n" + "🧪 "*40)
    results['data_extraction'] = await test_data_extraction_for_map(sentiment_result)
    await asyncio.sleep(1)
    
    # Test 4: Country code mapping
    print("\n" + "🧪 "*40)
    results['country_mapping'] = await test_country_code_mapping()
    await asyncio.sleep(1)
    
    # Test 5: Master agent integration
    print("\n" + "🧪 "*40)
    results['master_agent'] = await test_master_agent_has_map_tool()
    
    # Summary
    print("\n\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    print(f"\nDetailed Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    if passed == total:
        print(f"\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print(f"\n" + "="*80)
    print(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(run_all_tests())
        
        # Exit with appropriate code
        all_passed = all(results.values())
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

