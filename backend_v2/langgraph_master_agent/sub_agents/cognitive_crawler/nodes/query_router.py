"""
Query Router Node - Routes to appropriate workflow based on action
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from state import CognitiveCrawlerState


def query_router(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Router node - determines which workflow to execute
    
    Actions:
    - discover: Find tender portals and map structure
    - crawl: Crawl pages and store tenders
    - query: Search existing tenders via RAG
    - analyze: Deep analysis of specific tenders
    """
    
    query = state["query"]
    action = state.get("action", "query")
    
    print(f"\n{'='*70}")
    print(f"🎯 Tender Intelligence Agent")
    print(f"{'='*70}")
    print(f"Query: {query}")
    print(f"Action: {action}")
    print(f"{'='*70}\n")
    
    # Log routing decision
    state["execution_log"].append({
        "step": "query_router",
        "action": f"Routing to {action} workflow"
    })
    
    return state

