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
            # Log tool execution start with full details
            exec_log_start = {
                "step": "tool_executor",
                "action": f"Executing {tool_name}",
                "timestamp": datetime.now().isoformat(),
                "input": f"Tool: {tool_name}\nQuery: {current_message}",
                "output": "Starting execution..."
            }
            
            if tool_name == "tavily_search":
                exec_log_start["input"] += f"\nSearch Depth: basic\nMax Results: 8"
                state["execution_log"].append(exec_log_start)
                
                result = await tavily_tools.search(
                    query=current_message,
                    search_depth="basic",
                    max_results=8
                )
                state["tool_results"]["tavily_search"] = result
                
                # Log detailed search results
                result_summary = ""
                if result and isinstance(result, dict):
                    # Tavily returns dict with "results" key
                    results_list = result.get("results", [])
                    answer = result.get("answer", "")
                    
                    if results_list:
                        result_summary = f"✅ Found {len(results_list)} sources\n\n"
                        
                        # Add Tavily's AI answer if available
                        if answer:
                            result_summary += f"📝 Tavily AI Answer:\n{answer[:300]}{'...' if len(answer) > 300 else ''}\n\n"
                        
                        # Add source details
                        result_summary += f"📚 Sources:\n"
                        for i, source in enumerate(results_list[:3], 1):  # Show first 3 sources
                            title = source.get('title', 'N/A')
                            url = source.get('url', 'N/A')
                            content = source.get('content', '')[:200]
                            result_summary += f"\n{i}. {title}\n"
                            result_summary += f"   🔗 {url}\n"
                            result_summary += f"   📄 {content}...\n"
                        
                        if len(results_list) > 3:
                            result_summary += f"\n... and {len(results_list) - 3} more sources"
                    else:
                        result_summary = "⚠️ No search results returned from Tavily"
                    
                    # Add error if present
                    if result.get("error"):
                        result_summary = f"❌ Error: {result['error']}"
                else:
                    result_summary = "⚠️ Invalid result format"
                
                state["execution_log"].append({
                    "step": "tool_executor",
                    "action": f"Completed {tool_name}",
                    "timestamp": datetime.now().isoformat(),
                    "input": f"Search Query: {current_message}",
                    "output": result_summary
                })
            
            elif tool_name == "tavily_extract":
                exec_log_start["input"] += f"\nURLs to extract: {state.get('urls_to_extract', [])}"
                state["execution_log"].append(exec_log_start)
                
                # Extract URLs from previous results or state
                urls = state.get("urls_to_extract", [])
                if urls:
                    result = await tavily_tools.extract(urls=urls)
                    state["tool_results"]["tavily_extract"] = result
                    
                    extract_summary = f"Extracted content from {len(urls)} URLs"
                    state["execution_log"].append({
                        "step": "tool_executor",
                        "action": f"Completed {tool_name}",
                        "timestamp": datetime.now().isoformat(),
                        "input": f"URLs: {', '.join(urls[:2])}{'...' if len(urls) > 2 else ''}",
                        "output": extract_summary
                    })
                else:
                    state["tool_results"]["tavily_extract"] = {
                        "success": False,
                        "error": "No URLs provided for extraction"
                    }
                    state["execution_log"].append({
                        "step": "tool_executor",
                        "action": f"Failed {tool_name}",
                        "timestamp": datetime.now().isoformat(),
                        "input": "No URLs provided",
                        "output": "Error: No URLs to extract"
                    })
            
            elif tool_name == "sentiment_analysis_agent":
                countries = state.get("countries", None)
                time_range = state.get("time_range_days", 7)
                exec_log_start["input"] += f"\nCountries: {countries or 'All'}\nTime Range: {time_range} days"
                state["execution_log"].append(exec_log_start)
                
                result = await sub_agent_caller.call_sentiment_analyzer(
                    query=current_message,
                    countries=countries,
                    time_range_days=time_range
                )
                state["sub_agent_results"]["sentiment_analysis"] = result
                
                # Log sentiment analysis results
                sentiment_summary = f"Sentiment Analysis completed\n"
                if result and isinstance(result, dict):
                    sentiment_summary += f"Countries analyzed: {result.get('countries_count', 'N/A')}\n"
                    sentiment_summary += f"Sources: {result.get('sources_count', 'N/A')}"
                
                state["execution_log"].append({
                    "step": "tool_executor",
                    "action": f"Completed {tool_name}",
                    "timestamp": datetime.now().isoformat(),
                    "input": f"Query: {current_message}\nCountries: {countries}\nTime Range: {time_range} days",
                    "output": sentiment_summary
                })
            
            elif tool_name == "media_bias_detector_agent":
                sources = state.get("sources", None)
                time_range = state.get("time_range_days", 7)
                exec_log_start["input"] += f"\nSources: {sources or 'Auto-select'}\nTime Range: {time_range} days"
                state["execution_log"].append(exec_log_start)
                
                result = await sub_agent_caller.call_media_bias_detector(
                    query=current_message,
                    sources=sources,
                    time_range_days=time_range
                )
                state["sub_agent_results"]["media_bias_detection"] = result
                
                # Log media bias detection results
                bias_summary = f"Media Bias Detection completed\n"
                if result and isinstance(result, dict) and result.get("success"):
                    data = result.get("data", {})
                    bias_summary += f"Sources analyzed: {len(data.get('sources_analyzed', []))}\n"
                    bias_summary += f"Articles: {data.get('total_articles', 0)}\n"
                    bias_summary += f"Confidence: {data.get('confidence', 0.0):.2f}"
                
                state["execution_log"].append({
                    "step": "tool_executor",
                    "action": f"Completed {tool_name}",
                    "timestamp": datetime.now().isoformat(),
                    "input": f"Query: {current_message}\nSources: {sources}\nTime Range: {time_range} days",
                    "output": bias_summary
                })
            
            elif tool_name == "create_plotly_chart":
                # Chart creation is handled by artifact_creator node
                state["execution_log"].append({
                    "step": "tool_executor",
                    "action": f"Delegating {tool_name} to artifact_creator",
                    "timestamp": datetime.now().isoformat(),
                    "input": "Chart creation requested",
                    "output": "Will be handled by artifact_creator node"
                })
            
            else:
                state["execution_log"].append({
                    "step": "tool_executor",
                    "action": f"Unknown tool: {tool_name}",
                    "timestamp": datetime.now().isoformat(),
                    "input": f"Tool: {tool_name}",
                    "output": "Error: Tool not recognized"
                })
        
        except Exception as e:
            error_msg = f"Tool execution error ({tool_name}): {str(e)}"
            state["error_log"] = state.get("error_log", [])
            state["error_log"].append(error_msg)
            
            state["execution_log"].append({
                "step": "tool_executor",
                "action": f"Error in {tool_name}",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "input": f"Tool: {tool_name}\nQuery: {current_message}",
                "output": f"Exception: {str(e)}"
            })
    
    return state

