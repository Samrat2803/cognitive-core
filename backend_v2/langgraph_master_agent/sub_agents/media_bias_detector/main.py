"""
Standalone Test Runner for Media Bias Detector Agent

This file allows testing the agent WITHOUT the master agent.
Run: python main.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import asyncio
import json
from datetime import datetime
from graph import create_media_bias_detector_graph


async def run_test(query: str, sources: list = None, time_range_days: int = 7):
    """Run the Media Bias Detector agent"""
    
    print("=" * 80)
    print("MEDIA BIAS DETECTOR - STANDALONE TEST")
    print("=" * 80)
    print(f"\nQuery: {query}")
    print(f"Sources: {sources if sources else 'Auto-select'}")
    print(f"Time Range: {time_range_days} days")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80)
    
    # Create graph
    graph = create_media_bias_detector_graph()
    
    # Initial state
    initial_state = {
        "query": query,
        "sources": sources,
        "time_range_days": time_range_days,
        "articles_by_source": {},
        "total_articles_found": 0,
        "bias_classification": {},
        "loaded_language": {},
        "framing_analysis": {},
        "consensus_points": [],
        "divergence_points": [],
        "omission_analysis": {},
        "overall_bias_range": {},
        "summary": "",
        "key_findings": [],
        "confidence": 0.0,
        "recommendations": [],
        "artifacts": [],
        "execution_log": [],
        "error_log": []
    }
    
    # Run the graph
    start_time = datetime.now()
    result = await graph.ainvoke(initial_state)
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print(f"\n📊 Sources Analyzed: {len(result.get('bias_classification', {}))}")
    print(f"📰 Total Articles: {result.get('total_articles_found', 0)}")
    print(f"📈 Artifacts Generated: {len(result.get('artifacts', []))}")
    print(f"⏱️  Execution Time: {execution_time:.1f} seconds")
    print(f"🎯 Confidence: {result.get('confidence', 0.0):.2f}")
    
    # Bias classification
    if result.get('bias_classification'):
        print("\n" + "-" * 80)
        print("BIAS CLASSIFICATION")
        print("-" * 80)
        for source, data in result['bias_classification'].items():
            print(f"  {source}")
            print(f"    Spectrum: {data['spectrum']}")
            print(f"    Bias Score: {data['bias_score']:.2f}")
            print(f"    Confidence: {data['confidence']:.2f}")
    
    # Summary
    if result.get('summary'):
        print("\n" + "-" * 80)
        print("EXECUTIVE SUMMARY")
        print("-" * 80)
        print(f"  {result['summary']}")
    
    # Key findings
    if result.get('key_findings'):
        print("\n" + "-" * 80)
        print("KEY FINDINGS")
        print("-" * 80)
        for i, finding in enumerate(result['key_findings'], 1):
            print(f"  {i}. {finding}")
    
    # Recommendations
    if result.get('recommendations'):
        print("\n" + "-" * 80)
        print("RECOMMENDATIONS")
        print("-" * 80)
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Artifacts
    if result.get('artifacts'):
        print("\n" + "-" * 80)
        print("ARTIFACTS GENERATED")
        print("-" * 80)
        for artifact in result['artifacts']:
            print(f"  ✓ {artifact['type']}: {artifact['title']}")
            if 'html_path' in artifact:
                print(f"    HTML: {artifact['html_path']}")
            if 'json_path' in artifact:
                print(f"    JSON: {artifact['json_path']}")
    
    # Execution log
    print("\n" + "-" * 80)
    print("EXECUTION LOG")
    print("-" * 80)
    for log in result.get('execution_log', []):
        details = f" - {log.get('details', '')}" if log.get('details') else ""
        print(f"  [{log['step']}] {log['action']}{details}")
    
    # Errors
    if result.get('error_log'):
        print("\n" + "-" * 80)
        print("ERRORS")
        print("-" * 80)
        for error in result['error_log']:
            print(f"  ❌ {error}")
    
    # Save test output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"artifacts/test_output_{timestamp}.json"
    os.makedirs("artifacts", exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            "query": query,
            "execution_time_seconds": execution_time,
            "timestamp": timestamp,
            "result": {
                "sources_analyzed": list(result.get('bias_classification', {}).keys()),
                "total_articles": result.get('total_articles_found', 0),
                "bias_classification": result.get('bias_classification', {}),
                "overall_bias_range": result.get('overall_bias_range', {}),
                "summary": result.get('summary', ''),
                "key_findings": result.get('key_findings', []),
                "recommendations": result.get('recommendations', []),
                "confidence": result.get('confidence', 0.0),
                "artifacts": result.get('artifacts', []),
                "execution_log": result.get('execution_log', []),
                "error_log": result.get('error_log', [])
            }
        }, f, indent=2)
    
    print("\n" + "=" * 80)
    print(f"✅ Test output saved to: {output_file}")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    # Test queries
    TEST_QUERIES = [
        {
            "query": "climate change policy",
            "sources": None,  # Auto-select
            "time_range_days": 7
        },
        # Add more test cases as needed
    ]
    
    # Run first test
    asyncio.run(run_test(**TEST_QUERIES[0]))

