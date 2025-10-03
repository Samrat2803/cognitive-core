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
        results_summary += f"\n{agent_name}:\n"
        
        # Special handling for sentiment analyzer
        if agent_name == "sentiment_analysis" and result.get("success"):
            data = result.get("data", {})
            results_summary += f"Status: {result.get('status', 'COMPLETED')}\n"
            results_summary += f"Query: {data.get('query', 'N/A')}\n"
            results_summary += f"Countries: {', '.join(data.get('countries', []))}\n\n"
            
            # Add sentiment scores
            sentiment_scores = data.get("sentiment_scores", {})
            if sentiment_scores:
                results_summary += "SENTIMENT SCORES:\n"
                for country, scores in sentiment_scores.items():
                    sentiment = scores.get('sentiment', 'unknown')
                    score = scores.get('score', 0)
                    pos_pct = scores.get('positive_pct', 0)
                    neu_pct = scores.get('neutral_pct', 0)
                    neg_pct = scores.get('negative_pct', 0)
                    results_summary += f"  {country}:\n"
                    results_summary += f"    Sentiment: {sentiment} (score: {score:.2f})\n"
                    results_summary += f"    Distribution: {pos_pct*100:.1f}% positive, {neu_pct*100:.1f}% neutral, {neg_pct*100:.1f}% negative\n"
            
            # Add bias analysis
            bias_analysis = data.get("bias_analysis", {})
            if bias_analysis:
                results_summary += "\nBIAS ANALYSIS:\n"
                for country, bias_data in bias_analysis.items():
                    bias_types = bias_data.get('bias_types', [])
                    overall_bias = bias_data.get('overall_bias', 'unknown')
                    results_summary += f"  {country}: {overall_bias} ({len(bias_types)} types detected)\n"
            
            # Add key findings
            key_findings = data.get("key_findings", [])
            if key_findings:
                results_summary += "\nKEY FINDINGS:\n"
                for i, finding in enumerate(key_findings[:5], 1):
                    results_summary += f"  {i}. {finding}\n"
            
            # Add summary
            summary = data.get("summary", "")
            if summary:
                results_summary += f"\nSUMMARY:\n{summary[:500]}...\n"
            
            # Add artifacts info
            artifacts = data.get("artifacts", [])
            if artifacts:
                results_summary += f"\nARTIFACTS GENERATED: {len(artifacts)} visualizations\n"
                for artifact in artifacts:
                    results_summary += f"  - {artifact.get('type')}: {artifact.get('title')}\n"
        else:
            # Default handling for other sub-agents
            results_summary += f"{str(result)[:500]}\n"
    
    # Get current date/time for recency context
    current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p %Z")
    
    synthesis_prompt = f"""
You are a Political Analyst AI assistant synthesizing results for a user query.

CURRENT DATE & TIME: {current_datetime}
Use this for understanding recency. When discussing events, provide temporal context.

{"CONVERSATION HISTORY:" if conversation_context else ""}
{conversation_context if conversation_context else ""}

USER QUERY:
{current_message}

GATHERED INFORMATION:
{results_summary}

YOUR CAPABILITIES:
You have access to the following tools and capabilities:
1. **Real-time Web Search** (Tavily): Search for current political information, news, and events
2. **Content Extraction**: Extract full content from specific URLs
3. **Sentiment Analysis Agent**: Multi-country sentiment analysis with bias detection
4. **Media Bias Detector**: Analyze and compare media bias across sources
5. **VISUALIZATION TOOLS**: 
   - Map charts (choropleth maps for geographic/country data)
   - Bar charts (categorical comparisons, rankings)
   - Line charts (trends over time)
   - Mind maps (hierarchical concepts)
   - Infographics (rich data displays)
   
IMPORTANT VISUALIZATION RULES:
- When a user asks to "create a map", "visualize", "create a chart", etc., ACKNOWLEDGE that you CAN and WILL create it
- Do NOT say "I cannot create visualizations" or "I don't have access to tools"
- Visualizations are automatically generated in the next step after your response
- If the data is already available (from previous analysis or current results), confirm that the visualization will be created

YOUR TASK:
Create a comprehensive, well-structured response that:
1. Directly answers the user's question
2. Uses information from the gathered results AND conversation history (if the user is referring to previous context)
3. Includes citations and sources
4. Is formatted with clear headings and bullet points
5. Is conversational and professional
6. If user asks about your capabilities or tools, accurately describe what you CAN do (including visualizations)
7. If user requests a visualization, acknowledge it and confirm it will be created

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

