"""
Tool Executor Node
Executes selected tools and sub-agents
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from datetime import datetime
from langgraph_master_agent.tools.tavily_direct import TavilyDirectTools
from langgraph_master_agent.tools.sub_agent_caller import SubAgentCaller
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


@observe(name="tool_executor_node")
async def tool_executor(state: dict) -> dict:
    """
    Execute tools and sub-agents
    
    Responsibilities:
    - Execute Tavily tools (search, extract, crawl)
    - Call sub-agents (sentiment analyzer, etc.)
    - Aggregate results
    - Handle errors gracefully
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with tool results
    """
    tavily_tools = TavilyDirectTools()
    sub_agent_caller = SubAgentCaller()
    
    tools_to_use = state.get("tools_to_use", [])
    current_message = state.get("current_message", "")
    
    # Initialize result storage
    if not state.get("tool_results"):
        state["tool_results"] = {}
    if not state.get("sub_agent_results"):
        state["sub_agent_results"] = {}
    
    # Execute each tool
    for tool_name in tools_to_use:
        try:
            state["execution_log"].append({
                "step": "tool_executor",
                "action": f"Executing {tool_name}",
                "timestamp": datetime.now().isoformat(),
                "input": f"Tool: {tool_name}, Query: {current_message[:100]}...",
                "output": "Tool execution started..."
            })
            
            if tool_name == "tavily_search":
                result = await tavily_tools.search(
                    query=current_message,
                    search_depth="basic",
                    max_results=8
                )
                state["tool_results"]["tavily_search"] = result
            
            elif tool_name == "tavily_extract":
                # Extract URLs from previous results or state
                urls = state.get("urls_to_extract", [])
                if urls:
                    result = await tavily_tools.extract(urls=urls)
                    state["tool_results"]["tavily_extract"] = result
                else:
                    state["tool_results"]["tavily_extract"] = {
                        "success": False,
                        "error": "No URLs provided for extraction"
                    }
            
            elif tool_name == "sentiment_analysis_agent":
                result = await sub_agent_caller.call_sentiment_analyzer(
                    query=current_message,
                    countries=state.get("countries", None),
                    time_range_days=state.get("time_range_days", 7)
                )
                state["sub_agent_results"]["sentiment_analysis"] = result
            
            else:
                state["execution_log"].append({
                    "step": "tool_executor",
                    "action": f"Unknown tool: {tool_name}",
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            error_msg = f"Tool execution error ({tool_name}): {str(e)}"
            state["error_log"] = state.get("error_log", [])
            state["error_log"].append(error_msg)
            
            state["execution_log"].append({
                "step": "tool_executor",
                "action": f"Error in {tool_name}",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    # Log completion
    results_summary = f"Tools executed: {len(tools_to_use)}, "
    if state.get("tool_results"):
        results_summary += f"Tavily results: {len(state['tool_results'])} sources"
    
    state["execution_log"].append({
        "step": "tool_executor",
        "action": f"Completed {len(tools_to_use)} tool executions",
        "timestamp": datetime.now().isoformat(),
        "input": f"Executed: {', '.join(tools_to_use)}",
        "output": results_summary
    })
    
    return state

