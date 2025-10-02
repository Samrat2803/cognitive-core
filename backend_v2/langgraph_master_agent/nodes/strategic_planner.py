"""
Strategic Planner Node
Analyzes user query and determines action plan
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from shared.llm_factory import LLMFactory
from shared.observability import ObservabilityManager
from langgraph_master_agent.config import MasterAgentConfig

observe = ObservabilityManager.get_observe_decorator()


@observe(name="strategic_planner_node")
async def strategic_planner(state: dict) -> dict:
    """
    Analyze query and create action plan
    
    Responsibilities:
    - Understand user intent
    - Determine which tools/sub-agents to use
    - Decide if direct answer is possible
    - Plan execution strategy
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with task plan and tool selection
    """
    llm = LLMFactory.create_llm()
    
    current_message = state.get("current_message", "")
    conversation_history = state.get("conversation_history", [])
    
    # Build context from history
    history_context = ""
    if len(conversation_history) > 1:
        recent_history = conversation_history[-3:]
        history_context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in recent_history[:-1]  # Exclude current message
        ])
    
    # Get available tools
    tools_desc = "\n".join([
        f"- {name}: {info['description'][:150]}..."
        for name, info in MasterAgentConfig.AVAILABLE_TOOLS.items()
    ])
    
    planning_prompt = f"""
You are a Strategic Planner for a Political Analyst AI Agent.

AVAILABLE TOOLS:
{tools_desc}

CONVERSATION HISTORY:
{history_context if history_context else "No previous context"}

CURRENT USER MESSAGE:
{current_message}

YOUR TASK:
Analyze the user's request and create an action plan.

CRITICAL RULES:
1. **Visualization-Only Requests**: If user asks to "create a map", "visualize", "show a chart" of EXISTING data from conversation history:
   - Set "can_answer_directly": true
   - Set "tools_to_use": [] (empty - no tools needed!)
   - The artifact_decision node will handle extracting data from history and creating the visualization
   - DO NOT run sentiment_analysis_agent or any other tool again!

2. **New Analysis Requests**: If user asks for NEW sentiment analysis or search:
   - Use appropriate tools (sentiment_analysis_agent, tavily_search, etc.)

3. **Check History**: If conversation history contains relevant data, DON'T re-run analysis tools!

Determine:
1. Can you answer this directly without tools? (simple questions OR visualization of existing data)
2. Which tools should be used? (only if NEW data is needed)
3. What's the execution strategy?

OUTPUT FORMAT (JSON):
{{
    "can_answer_directly": true/false,
    "reasoning": "Brief explanation of your analysis",
    "tools_to_use": ["tool1", "tool2"],
    "execution_strategy": "Description of how to execute"
}}

EXAMPLES:
- "create a map of this data" → {{"can_answer_directly": true, "tools_to_use": []}}
- "sentiment on Hamas in US" → {{"can_answer_directly": false, "tools_to_use": ["sentiment_analysis_agent"]}}

Be concise and strategic.
"""
    
    try:
        messages = [
            SystemMessage(content=planning_prompt),
            HumanMessage(content="Analyze and provide action plan in JSON format.")
        ]
        
        response = await llm.ainvoke(messages)
        plan_text = response.content
        
        # Store plan
        state["task_plan"] = plan_text
        
        # Try to parse LLM's plan to extract recommended tools
        import json
        import re
        
        tools_to_use = []
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if json_match:
                plan_json = json.loads(json_match.group())
                tools_to_use = plan_json.get("tools_to_use", [])
                state["reasoning"] = plan_json.get("reasoning", "Plan created")
                
                # If LLM says can answer directly, set empty tools
                if plan_json.get("can_answer_directly", False):
                    tools_to_use = []
        except:
            pass  # Fall back to keyword matching if JSON parsing fails
        
        # FALLBACK: Keyword matching (DISABLED for debugging - will be re-enabled later)
        # Commenting out to force LLM-based tool selection for debugging core agent execution
        # TODO: Re-enable this fallback after debugging is complete
        
        # if not tools_to_use:
        #     query_lower = current_message.lower()
        #     
        #     # Check for visualization/chart creation requests
        #     if any(word in query_lower for word in ["chart", "graph", "visuali", "plot", "trend"]):
        #         # If there's conversation history with data, create visualization
        #         if len(conversation_history) > 1:
        #             tools_to_use.append("create_plotly_chart")
        #         else:
        #             # Need to search for data first
        #             tools_to_use.append("tavily_search")
        #             tools_to_use.append("create_plotly_chart")
        #     elif any(word in query_lower for word in ["sentiment", "opinion", "view", "perspective"]):
        #         tools_to_use.append("sentiment_analysis_agent")
        #     elif any(word in query_lower for word in ["search", "find", "latest", "recent", "news", "what"]):
        #         tools_to_use.append("tavily_search")
        #     elif any(word in query_lower for word in ["extract", "read", "content from"]):
        #         tools_to_use.append("tavily_extract")
        #     else:
        #         # Default to search for general queries
        #         tools_to_use.append("tavily_search")
        
        # If LLM didn't provide tools and fallback is disabled, log warning
        if not tools_to_use:
            state["reasoning"] = "No tools selected by LLM, and keyword fallback is disabled"
        
        state["tools_to_use"] = tools_to_use
        
        # Log execution with full details
        input_details = f"User Query: {current_message}\n"
        if history_context:
            input_details += f"\nContext from history:\n{history_context[:300]}..."
        
        output_details = f"Selected Tools: {', '.join(tools_to_use)}\n\n"
        output_details += f"Reasoning:\n{plan_text}\n\n"
        output_details += f"Task Plan:\n{state.get('task_plan', 'N/A')}"
        
        state["execution_log"].append({
            "step": "strategic_planner",
            "action": f"Analysis complete - {len(tools_to_use)} tool(s) selected",
            "timestamp": datetime.now().isoformat(),
            "input": input_details,
            "output": output_details
        })
        
    except Exception as e:
        state["task_plan"] = f"Error in planning: {str(e)}"
        state["tools_to_use"] = ["tavily_search"]  # Fallback
        state["error_log"] = state.get("error_log", [])
        state["error_log"].append(f"Planning error: {str(e)}")
    
    return state

