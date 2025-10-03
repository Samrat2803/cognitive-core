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
    
    # Check iteration limit
    max_iterations = MasterAgentConfig.MAX_TOOL_ITERATIONS
    at_iteration_limit = state["iteration_count"] >= max_iterations
    
    # Assess result quality (not just presence)
    result_quality = _assess_result_quality(tool_results, sub_agent_results, state)
    has_results = result_quality["has_any_results"]
    has_good_results = result_quality["has_good_results"]
    result_count = result_quality["result_count"]
    
    # Initialize retry strategy tracking
    if "retry_strategies_used" not in state:
        state["retry_strategies_used"] = []
    
    # Decision logic with quality assessment
    if has_good_results:
        # We have good quality results, proceed
        state["has_sufficient_info"] = True
        state["needs_more_tools"] = False
        state["needs_clarification"] = False
        decision = "PROCEED_TO_SYNTHESIS"
        state["retry_strategy_next"] = None
    
    elif has_results and state["iteration_count"] >= 2:
        # Have some results after 2+ attempts, good enough
        state["has_sufficient_info"] = True
        state["needs_more_tools"] = False
        state["needs_clarification"] = False
        decision = "PROCEED_TO_SYNTHESIS"
        state["retry_strategy_next"] = None
    
    elif not at_iteration_limit and state["iteration_count"] < max_iterations:
        # Not at limit, can retry with different strategy
        state["has_sufficient_info"] = False
        state["needs_more_tools"] = True
        state["needs_clarification"] = False
        decision = "RETRY_TOOLS"
        
        # Determine next retry strategy
        state["retry_strategy_next"] = _get_next_retry_strategy(
            state["iteration_count"],
            state.get("retry_strategies_used", []),
            has_results,
            state.get("current_message", "")
        )
    
    elif at_iteration_limit:
        # Hit iteration limit, synthesize what we have
        state["has_sufficient_info"] = True
        state["needs_more_tools"] = False
        state["needs_clarification"] = False
        decision = "PROCEED_TO_SYNTHESIS"
        state["retry_strategy_next"] = None
        
        state["error_log"] = state.get("error_log", [])
        state["error_log"].append(f"Reached iteration limit ({max_iterations})")
    
    else:
        # Default to synthesis
        state["has_sufficient_info"] = True
        state["needs_more_tools"] = False
        state["needs_clarification"] = False
        decision = "PROCEED_TO_SYNTHESIS"
        state["retry_strategy_next"] = None
    
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
    state["metadata"]["result_quality"] = result_quality
    state["metadata"]["retry_strategy_next"] = state.get("retry_strategy_next")
    
    return state


def _assess_result_quality(tool_results: dict, sub_agent_results: dict, state: dict) -> dict:
    """
    Assess the quality of results to determine if retry is needed
    
    Returns:
        Dict with quality metrics
    """
    has_any_results = bool(tool_results) or bool(sub_agent_results)
    
    # Count successful results
    successful_tools = sum(1 for r in tool_results.values() if isinstance(r, dict) and r.get("success"))
    successful_subagents = sum(1 for r in sub_agent_results.values() if isinstance(r, dict) and r.get("success"))
    result_count = successful_tools + successful_subagents
    
    # Check result richness
    has_rich_data = False
    
    # Check Tavily results
    for tool_name, result in tool_results.items():
        if isinstance(result, dict) and result.get("success"):
            if tool_name == "tavily_search":
                # Good if we have 3+ search results
                result_list = result.get("results", [])
                if len(result_list) >= 3:
                    has_rich_data = True
                    break
            elif tool_name in ["tavily_extract", "tavily_crawl"]:
                # Good if we have content
                if result.get("content") and len(result.get("content", "")) > 500:
                    has_rich_data = True
                    break
    
    # Check sub-agent results
    for agent_name, result in sub_agent_results.items():
        if isinstance(result, dict) and result.get("success"):
            data = result.get("data", {})
            # Check if data has substantial content
            if data and len(str(data)) > 200:
                has_rich_data = True
                break
    
    # Determine if results are "good enough"
    has_good_results = result_count >= 1 and has_rich_data
    
    return {
        "has_any_results": has_any_results,
        "has_good_results": has_good_results,
        "result_count": result_count,
        "has_rich_data": has_rich_data,
        "successful_tools": successful_tools,
        "successful_subagents": successful_subagents
    }


def _get_next_retry_strategy(iteration: int, used_strategies: list, has_partial_results: bool, query: str) -> str:
    """
    Determine the next retry strategy based on iteration number
    
    Strategies (in order):
    1. "broader_keywords" - Try more general search terms
    2. "specific_keywords" - Try more specific, targeted terms
    3. "alternative_sources" - Try different types of sources
    4. "advanced_search" - Use Tavily advanced search with more results
    5. "alternative_tools" - Try different tool combination
    
    Args:
        iteration: Current iteration number (1-5)
        used_strategies: List of previously used strategies
        has_partial_results: Whether we have some results already
        query: Original user query
    
    Returns:
        Strategy name for next attempt
    """
    # Define strategy order
    all_strategies = [
        "broader_keywords",
        "specific_keywords", 
        "alternative_sources",
        "advanced_search",
        "alternative_tools"
    ]
    
    # Find next unused strategy
    for strategy in all_strategies:
        if strategy not in used_strategies:
            return strategy
    
    # If all strategies used, cycle back to broader_keywords
    return "broader_keywords"

