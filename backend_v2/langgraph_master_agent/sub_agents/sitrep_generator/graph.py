"""
SitRep Generator Graph

Defines the LangGraph workflow for generating situation reports.
"""

from langgraph.graph import StateGraph, END
from state import SitRepState

# Import nodes
from nodes.event_retriever import retrieve_events
from nodes.priority_ranker import rank_events_by_priority
from nodes.event_grouper import group_events
from nodes.executive_summarizer import generate_executive_summary
from nodes.watch_list_generator import generate_watch_list
from nodes.artifact_generator import generate_artifacts


def create_sitrep_graph():
    """
    Create the SitRep Generator workflow graph
    
    Workflow:
    1. Retrieve Events (from Live Monitor)
    2. Rank by Priority (urgent, high, notable)
    3. Group Events (by region and topic)
    4. Generate Executive Summary (LLM)
    5. Generate Watch List (LLM)
    6. Generate Artifacts (HTML, PDF, TXT, JSON)
    
    Returns:
        Compiled LangGraph workflow
    """
    
    # Create workflow graph
    workflow = StateGraph(SitRepState)
    
    # Add nodes
    workflow.add_node("retrieve_events", retrieve_events)
    workflow.add_node("rank_priority", rank_events_by_priority)
    workflow.add_node("group_events", group_events)
    workflow.add_node("executive_summary", generate_executive_summary)
    workflow.add_node("watch_list", generate_watch_list)
    workflow.add_node("generate_artifacts", generate_artifacts)
    
    # Define edges (linear workflow)
    workflow.set_entry_point("retrieve_events")
    workflow.add_edge("retrieve_events", "rank_priority")
    workflow.add_edge("rank_priority", "group_events")
    workflow.add_edge("group_events", "executive_summary")
    workflow.add_edge("executive_summary", "watch_list")
    workflow.add_edge("watch_list", "generate_artifacts")
    workflow.add_edge("generate_artifacts", END)
    
    # Compile and return
    return workflow.compile()


if __name__ == "__main__":
    # Test graph creation
    print("Creating SitRep Generator graph...")
    graph = create_sitrep_graph()
    print("✅ Graph created successfully!")
    print("\nWorkflow:")
    print("  1. Retrieve Events")
    print("  2. Rank by Priority")
    print("  3. Group Events")
    print("  4. Generate Executive Summary")
    print("  5. Generate Watch List")
    print("  6. Generate Artifacts")

