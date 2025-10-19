"""
Investigative Journalist Graph - LangGraph Workflow

Wraps the LeanInvestigator for integration with master agent
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add lean_investigator to path
sys.path.insert(0, '/Users/kiransah/Desktop/code/tavily_assignment/exp_3')
from lean_investigator import LeanInvestigator

# Import state
from state import InvestigativeJournalistState


def create_investigative_journalist_graph():
    """
    Create the investigative journalist LangGraph workflow
    
    Returns:
        Compiled LangGraph workflow
    """
    # For now, we return the LeanInvestigator instance
    # In the future, we can refactor to pure LangGraph nodes
    return LeanInvestigator


async def run_investigation(
    query: str,
    max_iterations: int = 20,
    resume_from_state: Dict[str, Any] = None
) -> InvestigativeJournalistState:
    """
    Run investigation with given query
    
    Args:
        query: Investigation query
        max_iterations: Maximum iterations
        resume_from_state: Optional state to resume from
        
    Returns:
        Final state with article and evidence
    """
    investigator = LeanInvestigator(max_iterations=max_iterations)
    
    # If resuming, we would load state here
    # For now, start fresh
    
    result = await investigator.investigate(query)
    
    # Convert to state format
    state: InvestigativeJournalistState = {
        "initial_query": query,
        "investigation_id": None,  # Will be set when saving to MongoDB
        "session_id": None,
        "iteration": result.get("iterations", max_iterations),
        "max_iterations": max_iterations,
        "investigation_complete": True,
        
        # Evidence
        "entities": result.get("entities", {}),
        "facts": result.get("facts", []),
        "hypotheses": result.get("hypotheses", []),
        "evidence": [],
        "connections": result.get("connections", []),
        "anomalies": result.get("anomalies", []),
        
        # Cache
        "seen_urls": [],
        "extracted_cache": {},
        "previous_queries": [],
        
        # Working variables
        "next_action": "complete",
        "search_query": None,
        "search_results": [],
        "extracted_content": [],
        
        # Outputs
        "final_report": result.get("report"),
        "artifacts": [],
        
        # Metadata
        "execution_log": [],
        "error_log": [],
        "cost_tracking": investigator.costs
    }
    
    return state

