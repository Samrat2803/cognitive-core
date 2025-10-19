"""
Cognitive Crawler LangGraph Workflow
"""

import sys
import os

# Add parent to path for shared modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from langgraph.graph import StateGraph, END

# Import from current directory (works with standalone execution)
from state import CognitiveCrawlerState
from nodes import (
    query_router,
    portal_discoverer,
    portal_mapper,
    tender_crawler,
    content_processor,
    embedder,
    rag_query_handler,
    synthesizer
)


def route_by_action(state: CognitiveCrawlerState) -> str:
    """Route based on action type"""
    action = state.get("action", "crawl").lower()
    
    if action == "discover":
        return "discover"
    elif action == "crawl":
        return "crawl"
    else:
        return "crawl"  # Default to crawl


def create_cognitive_crawler_graph():
    """
    Create LangGraph workflow for cognitive crawler
    
    Workflow:
    - discover: Find web pages → Map structure → Crawl → Process → Embed → Synthesize
    - crawl: Crawl pages → Process content → Generate embeddings → Synthesize
    
    Note: RAG/Chat functionality is now a separate tool (knowledge_base.py)
    """
    
    workflow = StateGraph(CognitiveCrawlerState)
    
    # Add nodes (removed rag_handler - it's now a tool)
    workflow.add_node("router", query_router)
    workflow.add_node("portal_discoverer", portal_discoverer)
    workflow.add_node("portal_mapper", portal_mapper)
    workflow.add_node("crawler", tender_crawler)
    workflow.add_node("content_processor", content_processor)
    workflow.add_node("embedder", embedder)
    workflow.add_node("synthesizer", synthesizer)
    
    # Entry point with routing
    workflow.set_entry_point("router")
    
    # Router decides which flow to take
    workflow.add_conditional_edges(
        "router",
        route_by_action,
        {
            "discover": "portal_discoverer",
            "crawl": "crawler"
        }
    )
    
    # Discovery flow: discover pages → map structure → THEN crawl → process → embed → synthesize
    workflow.add_edge("portal_discoverer", "portal_mapper")
    workflow.add_edge("portal_mapper", "crawler")  # Feed discovered URLs into crawler!
    
    # Crawling flow: crawl → process → embed → synthesize
    workflow.add_edge("crawler", "content_processor")
    workflow.add_edge("content_processor", "embedder")
    workflow.add_edge("embedder", "synthesizer")
    
    # All paths end at synthesizer
    workflow.add_edge("synthesizer", END)
    
    return workflow.compile()


if __name__ == "__main__":
    print("🎯 Creating Cognitive Crawler Graph...")
    graph = create_cognitive_crawler_graph()
    print("✅ Graph created successfully!")
    print("\nWorkflow Structure:")
    print("  Entry → router")
    print("           ├─→ [discover] → portal_discoverer → portal_mapper → crawler → process → embed → synthesize → END")
    print("           └─→ [crawl]    → crawler → content_processor → embedder → synthesizer → END")
    print("\n  Note: RAG/Chat is now a separate tool (knowledge_base.py)")


