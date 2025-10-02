"""
Decision Gate Node
Determines next action based on results
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from datetime import datetime
from shared.observability import ObservabilityManager
from langgraph_master_agent.config import MasterAgentConfig

observe = ObservabilityManager.get_observe_decorator()


@observe(name="decision_gate_node")
async def decision_gate(state: dict) -> dict:
    """
    Decide next action
    
    Responsibilities:
    - Check if sufficient information gathered
    - Determine if more tools needed
    - Check iteration limits
    - Route to appropriate next step
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with decision flags
    """
    # Initialize iteration count
    if not state.get("iteration_count"):
        state["iteration_count"] = 0
    
    state["iteration_count"] += 1
    
    # Get results
    tool_results = state.get("tool_results", {})
    sub_agent_results = state.get("sub_agent_results", {})
    
    # Check if we have results
    has_results = bool(tool_results) or bool(sub_agent_results)
    
    # Check iteration limit
    max_iterations = MasterAgentConfig.MAX_TOOL_ITERATIONS
    at_iteration_limit = state["iteration_count"] >= max_iterations
    
    # Decision logic
    if has_results and (state["iteration_count"] >= 1 or at_iteration_limit):
        # We have results and have tried at least once
        state["has_sufficient_info"] = True
        state["needs_more_tools"] = False
        state["needs_clarification"] = False
        decision = "PROCEED_TO_SYNTHESIS"
    
    elif not has_results and state["iteration_count"] < max_iterations:
        # No results yet, try again
        state["has_sufficient_info"] = False
        state["needs_more_tools"] = True
        state["needs_clarification"] = False
        decision = "RETRY_TOOLS"
    
    elif at_iteration_limit:
        # Hit iteration limit, synthesize what we have
        state["has_sufficient_info"] = True
        state["needs_more_tools"] = False
        state["needs_clarification"] = False
        decision = "PROCEED_TO_SYNTHESIS"
        
        state["error_log"] = state.get("error_log", [])
        state["error_log"].append(f"Reached iteration limit ({max_iterations})")
    
    else:
        # Default to synthesis
        state["has_sufficient_info"] = True
        state["needs_more_tools"] = False
        state["needs_clarification"] = False
        decision = "PROCEED_TO_SYNTHESIS"
    
    # Log decision
    state["execution_log"].append({
        "step": "decision_gate",
        "action": f"Decision: {decision}",
        "iteration": state["iteration_count"],
        "has_results": has_results,
        "timestamp": datetime.now().isoformat(),
        "input": f"Iteration: {state['iteration_count']}, Has results: {has_results}",
        "output": f"Decision: {decision}, Continue: {state.get('needs_more_tools', False)}"
    })
    
    state["metadata"]["decision"] = decision
    
    return state

