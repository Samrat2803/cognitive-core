"""
LangGraph workflow for Live Political Monitor Agent
"""

from langgraph.graph import StateGraph, END
from state import LiveMonitorState
from nodes import (
    generate_queries,
    fetch_articles,
    filter_by_relevance,
    extract_topics,
    calculate_explosiveness
)


def create_live_monitor_graph():
    """
    Create the LangGraph workflow
    
    Flow:
    1. Generate Queries (from keywords)
    2. Fetch Articles (from Tavily)
    3. Filter by Relevance (keyword matching)
    4. Extract Topics (LLM)
    5. Calculate Explosiveness (4-signal scoring)
    """
    
    workflow = StateGraph(LiveMonitorState)
    
    # Add nodes
    workflow.add_node("generate_queries", generate_queries)
    workflow.add_node("fetch_articles", fetch_articles)
    workflow.add_node("filter_by_relevance", filter_by_relevance)
    workflow.add_node("extract_topics", extract_topics)
    workflow.add_node("calculate_explosiveness", calculate_explosiveness)
    
    # Define edges (linear flow)
    workflow.set_entry_point("generate_queries")
    workflow.add_edge("generate_queries", "fetch_articles")
    workflow.add_edge("fetch_articles", "filter_by_relevance")
    workflow.add_edge("filter_by_relevance", "extract_topics")
    workflow.add_edge("extract_topics", "calculate_explosiveness")
    workflow.add_edge("calculate_explosiveness", END)
    
    return workflow.compile()


if __name__ == "__main__":
    # Test graph creation
    print("Creating Live Monitor graph...")
    graph = create_live_monitor_graph()
    print("✓ Graph created successfully")
    print(f"✓ Nodes: {len(graph.nodes)}")

