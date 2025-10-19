"""
Deep Investigative Reporter Sub-Agent

A persistent investigative journalism agent that:
- Follows entities recursively
- Traces funding networks
- Identifies hidden connections
- Generates visual artifacts (causal diagrams + network graphs)

Usage:
    from sub_agents.deep_investigative_reporter import investigate
    
    result = await investigate(
        query="Why did X happen?",
        max_depth=5
    )
"""

from .agent import investigate, investigation_agent

__all__ = ["investigate", "investigation_agent"]


