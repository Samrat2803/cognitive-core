"""
Sentiment Analyzer LangGraph Workflow
"""

import sys
import os

# Add parent to path for shared modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from langgraph.graph import StateGraph, END

# NOTE: These imports work correctly when called via sub_agent_caller (which uses importlib)
# The sub_agent_caller loads this module with the correct context
from state import SentimentAnalyzerState
from nodes import (
    query_analyzer,
    search_executor,
    sentiment_scorer,
    bias_detector,
    synthesizer,
    visualizer
)


def create_sentiment_analyzer_graph():
    """Create sentiment analyzer LangGraph workflow"""
    
    workflow = StateGraph(SentimentAnalyzerState)
    
    # Add nodes
    workflow.add_node("analyzer", query_analyzer)
    workflow.add_node("search", search_executor)
    workflow.add_node("scorer", sentiment_scorer)
    workflow.add_node("bias_detector", bias_detector)
    workflow.add_node("synthesizer", synthesizer)
    workflow.add_node("visualizer", visualizer)
    
    # Define flow
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "search")
    workflow.add_edge("search", "scorer")
    workflow.add_edge("scorer", "bias_detector")
    workflow.add_edge("bias_detector", "synthesizer")
    workflow.add_edge("synthesizer", "visualizer")
    workflow.add_edge("visualizer", END)
    
    return workflow.compile()


if __name__ == "__main__":
    print("🎯 Creating Sentiment Analyzer Graph...")
    graph = create_sentiment_analyzer_graph()
    print("✅ Graph created successfully!")
    print("\nWorkflow: analyzer → search → scorer → bias_detector → synthesizer → visualizer → END")

