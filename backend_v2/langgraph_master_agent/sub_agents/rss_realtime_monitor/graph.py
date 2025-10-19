"""
LangGraph Workflow for RSS Realtime Monitor Agent

Linear workflow:
1. Load articles from MongoDB
2. Filter by keywords (semantic + exact)
3. Cluster into topics (DBSCAN)
4. Generate topic labels (TF-IDF)
5. Score explosiveness (velocity + diversity + recency)
6. Extract entities (LLM)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langgraph.graph import StateGraph, END
from rss_realtime_monitor.state import RSSRealtimeMonitorState
from rss_realtime_monitor.nodes import (
    load_articles,
    filter_by_keywords,
    cluster_topics,
    generate_labels,
    score_explosiveness,
    extract_entities
)


def create_rss_realtime_monitor_graph():
    """
    Create the RSS Realtime Monitor workflow graph
    
    Returns:
        Compiled LangGraph workflow
    """
    
    # Create graph
    workflow = StateGraph(RSSRealtimeMonitorState)
    
    # Add nodes
    workflow.add_node("load_articles", load_articles)
    workflow.add_node("filter_by_keywords", filter_by_keywords)
    workflow.add_node("cluster_topics", cluster_topics)
    workflow.add_node("generate_labels", generate_labels)
    workflow.add_node("score_explosiveness", score_explosiveness)
    workflow.add_node("extract_entities", extract_entities)
    
    # Define linear workflow
    workflow.set_entry_point("load_articles")
    workflow.add_edge("load_articles", "filter_by_keywords")
    workflow.add_edge("filter_by_keywords", "cluster_topics")
    workflow.add_edge("cluster_topics", "generate_labels")
    workflow.add_edge("generate_labels", "score_explosiveness")
    workflow.add_edge("score_explosiveness", "extract_entities")
    workflow.add_edge("extract_entities", END)
    
    # Compile
    return workflow.compile()


# Test graph creation
if __name__ == "__main__":
    print("Testing graph creation...")
    graph = create_rss_realtime_monitor_graph()
    print("✓ Graph created successfully!")
    print(f"  Nodes: {len(graph.nodes)}")

