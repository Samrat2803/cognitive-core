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
    
    # Log decision with detailed reasoning
    input_details = f"Current State Assessment:\n"
    input_details += f"- Iteration: {state['iteration_count']}/{max_iterations}\n"
    input_details += f"- Has Results: {has_results}\n"
    input_details += f"- Tool Results: {list(tool_results.keys()) if tool_results else 'None'}\n"
    input_details += f"- Sub-Agent Results: {list(sub_agent_results.keys()) if sub_agent_results else 'None'}\n"
    input_details += f"- At Iteration Limit: {at_iteration_limit}"
    
    output_details = f"Decision: {decision}\n\n"
    output_details += f"Reasoning:\n"
    if decision == "PROCEED_TO_SYNTHESIS":
        if has_results:
            result_count = len(tool_results) + len(sub_agent_results)
            output_details += f"✓ Sufficient information gathered ({result_count} result source(s))\n"
            output_details += f"✓ Ready to synthesize response"
        elif at_iteration_limit:
            output_details += f"⚠ Iteration limit reached ({max_iterations})\n"
            output_details += f"→ Proceeding with available information"
    elif decision == "RETRY_TOOLS":
        output_details += f"✗ No results yet\n"
        output_details += f"→ Will retry tool execution (attempt {state['iteration_count'] + 1}/{max_iterations})"
    
    output_details += f"\n\nNext Actions:\n"
    output_details += f"- Needs More Tools: {state.get('needs_more_tools', False)}\n"
    output_details += f"- Proceed to Synthesis: {state.get('has_sufficient_info', False)}"
    
    state["execution_log"].append({
        "step": "decision_gate",
        "action": decision,
        "timestamp": datetime.now().isoformat(),
        "input": input_details,
        "output": output_details
    })
    
    state["metadata"]["decision"] = decision
    
    return state

