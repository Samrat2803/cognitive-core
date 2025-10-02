"""
Master Political Analyst Agent
LangGraph-based master agent with tool delegation
"""

from langgraph_master_agent.main import MasterPoliticalAnalyst
from langgraph_master_agent.graph import create_master_agent_graph

__all__ = [
    "MasterPoliticalAnalyst",
    "create_master_agent_graph"
]

