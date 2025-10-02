"""
LangGraph Workflow for Media Bias Detector Agent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from langgraph.graph import StateGraph, END
from state import MediaBiasDetectorState
from nodes import (
    query_analyzer,
    source_searcher,
    bias_classifier,
    language_analyzer,
    framing_analyzer,
    synthesizer,
    visualizer
)


def create_media_bias_detector_graph():
    """Create the LangGraph workflow for media bias detection"""
    
    # Initialize the graph
    workflow = StateGraph(MediaBiasDetectorState)
    
    # Add nodes
    workflow.add_node("query_analyzer", query_analyzer)
    workflow.add_node("source_searcher", source_searcher)
    workflow.add_node("bias_classifier", bias_classifier)
    workflow.add_node("language_analyzer", language_analyzer)
    workflow.add_node("framing_analyzer", framing_analyzer)
    workflow.add_node("synthesizer", synthesizer)
    workflow.add_node("visualizer", visualizer)
    
    # Define workflow edges
    workflow.set_entry_point("query_analyzer")
    workflow.add_edge("query_analyzer", "source_searcher")
    workflow.add_edge("source_searcher", "bias_classifier")
    workflow.add_edge("bias_classifier", "language_analyzer")
    workflow.add_edge("language_analyzer", "framing_analyzer")
    workflow.add_edge("framing_analyzer", "synthesizer")
    workflow.add_edge("synthesizer", "visualizer")
    workflow.add_edge("visualizer", END)
    
    return workflow.compile()


# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test_graph():
        """Test the graph with a sample query"""
        
        graph = create_media_bias_detector_graph()
        
        initial_state = {
            "query": "climate change policy",
            "sources": None,
            "time_range_days": 7,
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
        
        print("=" * 80)
        print("MEDIA BIAS DETECTOR - GRAPH TEST")
        print("=" * 80)
        
        result = await graph.ainvoke(initial_state)
        
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"\nSources analyzed: {len(result.get('bias_classification', {}))}")
        print(f"Total articles: {result.get('total_articles_found', 0)}")
        print(f"Artifacts generated: {len(result.get('artifacts', []))}")
        print(f"Confidence: {result.get('confidence', 0.0):.2f}")
        print(f"\nSummary: {result.get('summary', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("EXECUTION LOG")
        print("=" * 80)
        for log in result.get("execution_log", []):
            print(f"[{log['step']}] {log['action']}")
        
        if result.get("error_log"):
            print("\n" + "=" * 80)
            print("ERRORS")
            print("=" * 80)
            for error in result["error_log"]:
                print(f"❌ {error}")
    
    asyncio.run(test_graph())

