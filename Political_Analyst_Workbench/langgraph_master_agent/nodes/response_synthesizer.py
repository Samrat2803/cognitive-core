"""
Response Synthesizer Node
Compiles results into final user response
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from shared.llm_factory import LLMFactory
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


@observe(name="response_synthesizer_node")
async def response_synthesizer(state: dict) -> dict:
    """
    Synthesize final response for user
    
    Responsibilities:
    - Compile results from all tools/sub-agents
    - Format response for readability
    - Add citations and sources
    - Create confidence score
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with final response
    """
    llm = LLMFactory.create_llm()
    
    current_message = state.get("current_message", "")
    tool_results = state.get("tool_results", {})
    sub_agent_results = state.get("sub_agent_results", {})
    conversation_history = state.get("conversation_history", [])
    
    # Build conversation context from history
    conversation_context = ""
    if len(conversation_history) > 1:
        # Get last few exchanges (excluding current user message)
        recent_history = conversation_history[-5:]  # Last 2-3 turns
        conversation_context = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in recent_history[:-1]  # Exclude current message
        ])
    
    # Compile all results
    results_summary = "TOOL RESULTS:\n"
    
    for tool_name, result in tool_results.items():
        results_summary += f"\n{tool_name}:\n"
        
        if tool_name == "tavily_search" and result.get("success"):
            results_summary += f"Answer: {result.get('answer', 'N/A')}\n"
            results_summary += f"Found {result.get('result_count', 0)} results:\n"
            for i, item in enumerate(result.get("results", [])[:5], 1):
                results_summary += f"{i}. {item.get('title', '')}\n"
                results_summary += f"   {item.get('content', '')[:200]}...\n"
                results_summary += f"   Source: {item.get('url', '')}\n"
        else:
            results_summary += f"{str(result)[:300]}\n"
    
    results_summary += "\n\nSUB-AGENT RESULTS:\n"
    for agent_name, result in sub_agent_results.items():
        results_summary += f"\n{agent_name}:\n{str(result)[:300]}\n"
    
    synthesis_prompt = f"""
You are a Political Analyst AI assistant synthesizing results for a user query.

{"CONVERSATION HISTORY:" if conversation_context else ""}
{conversation_context if conversation_context else ""}

USER QUERY:
{current_message}

GATHERED INFORMATION:
{results_summary}

YOUR TASK:
Create a comprehensive, well-structured response that:
1. Directly answers the user's question
2. Uses information from the gathered results AND conversation history (if the user is referring to previous context)
3. Includes citations and sources
4. Is formatted with clear headings and bullet points
5. Is conversational and professional

IMPORTANT: If the user says "create a chart for this" or "visualize this data", extract the numerical data from the conversation history above.

If results are incomplete or tools failed, acknowledge limitations honestly.

Generate a helpful response now:
"""
    
    try:
        messages = [
            SystemMessage(content=synthesis_prompt),
            HumanMessage(content="Synthesize the final response.")
        ]
        
        response = await llm.ainvoke(messages)
        final_response = response.content
        
        # Extract citations (simplified)
        citations = []
        if tool_results.get("tavily_search", {}).get("success"):
            for result in tool_results["tavily_search"].get("results", []):
                citations.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "source": "Tavily Search"
                })
        
        state["final_response"] = final_response
        state["citations"] = citations
        state["confidence_score"] = 0.8 if tool_results or sub_agent_results else 0.3
        
        # Add to conversation history
        state["conversation_history"].append({
            "role": "assistant",
            "content": final_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Log completion
        sources_count = len(state.get("citations", []))
        state["execution_log"].append({
            "step": "response_synthesizer",
            "action": "Final response generated",
            "confidence": state["confidence_score"],
            "timestamp": datetime.now().isoformat(),
            "input": f"Tool results: {len(tool_results)} tools, Sub-agents: {len(sub_agent_results)}",
            "output": f"Response: {len(final_response)} chars, Citations: {sources_count}, Confidence: {state['confidence_score']:.0%}"
        })
        
    except Exception as e:
        error_msg = f"Synthesis error: {str(e)}"
        state["error_log"] = state.get("error_log", [])
        state["error_log"].append(error_msg)
        
        state["final_response"] = f"I encountered an error synthesizing the response. Here are the raw results:\n\n{results_summary}"
        state["confidence_score"] = 0.2
    
    return state

