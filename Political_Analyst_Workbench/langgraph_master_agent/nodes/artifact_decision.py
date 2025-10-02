"""
Artifact Decision Node
Decides if and what type of artifact to create, and extracts structured data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from shared.llm_factory import LLMFactory
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


@observe(name="artifact_decision_node")
async def artifact_decision(state: dict) -> dict:
    """
    Decide if artifact should be created, determine type, and extract structured data
    
    Uses LLM to:
    1. Detect if visualization is needed
    2. Choose appropriate chart type
    3. Extract structured data from agent's response
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with artifact decision and extracted data
    """
    
    message = state.get("current_message", "")
    response = state.get("final_response", "")
    
    # Initialize artifact fields
    state["should_create_artifact"] = False
    state["artifact_type"] = None
    state["artifact_data"] = None
    state["artifact_title"] = None
    
    # Only proceed if user explicitly requests visualization
    message_lower = message.lower()
    explicit_request = any(word in message_lower for word in ["chart", "graph", "visualiz", "plot", "show", "create"])
    
    if not explicit_request or not response:
        state["execution_log"].append({
            "step": "artifact_decision",
            "action": "Artifact decision: NO (no explicit request)",
            "timestamp": datetime.now().isoformat(),
            "input": f"Query: {message[:100]}",
            "output": "No visualization requested"
        })
        return state
    
    # Use LLM to extract structured data
    llm = LLMFactory.create_llm(temperature=0)
    
    # Include conversation history for context
    conversation_history = state.get("conversation_history", [])
    history_context = ""
    if len(conversation_history) > 1:
        # Get recent history (excluding current user message)
        recent_history = conversation_history[-5:]
        history_context = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content'][:1000]}"
            for msg in recent_history[:-1]
        ])
    
    extraction_prompt = f"""You are a data extraction expert. Analyze the user's query and the agent's response to determine if a visualization should be created and extract the necessary data.

{"CONVERSATION HISTORY (for context if user refers to 'this' or previous data):" if history_context else ""}
{history_context if history_context else ""}

User Query: "{message}"

Agent's Response:
{response[:2500]}

TASK 1: Decide if a data visualization is appropriate
- Look for explicit requests: "chart", "graph", "visualize", "plot"
- Check if response contains structured numerical data

TASK 2: If YES, determine the best chart type:
- "line_chart": For trends over time, temporal data, progression (years, months, quarters)
- "bar_chart": For categorical comparisons, rankings
- "mind_map": For conceptual hierarchies, relationships

TASK 3: Extract ALL the structured data from the response:
For line_chart:
- x: List of ALL x-axis labels (e.g., ["2020", "2021", "2022", "2023", "2024", "2025"])
- y: List of ALL corresponding numerical values (e.g., [-5.78, 9.69, 6.99, 8.15, 7.5, 7.8])
- x_label: Descriptive label for x-axis (e.g., "Year")
- y_label: Descriptive label with units (e.g., "GDP Growth Rate (%)")

For bar_chart:
- categories: List of category names
- values: List of values
- x_label and y_label

IMPORTANT:
- Extract EVERY data point mentioned in the response
- Keep numerical values precise (including decimals and negative numbers)
- Match the exact number of x and y values
- If the user says "create a chart for THIS" or refers to previous data, look in the CONVERSATION HISTORY above
- Extract data from EITHER the current response OR the conversation history (whichever contains the data)

Respond ONLY with valid JSON (no markdown):
{{
    "should_create": true,
    "chart_type": "line_chart",
    "data": {{
        "x": ["2020", "2021", "2022"],
        "y": [-5.78, 9.69, 6.99],
        "x_label": "Year",
        "y_label": "GDP Growth Rate (%)"
    }},
    "title": "India GDP Growth Rate (2020-2025)"
}}"""
    
    try:
        llm_response = await llm.ainvoke([
            SystemMessage(content="You are a precise data extraction assistant. Always respond with valid JSON only."),
            HumanMessage(content=extraction_prompt)
        ])
        
        response_text = llm_response.content.strip()
        
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        decision_data = json.loads(response_text)
        
        should_create = decision_data.get("should_create", False)
        chart_type = decision_data.get("chart_type")
        extracted_data = decision_data.get("data", {})
        title = decision_data.get("title", f"Visualization: {message[:50]}")
        
        # Update state
        state["should_create_artifact"] = should_create
        state["artifact_type"] = chart_type if should_create else None
        state["artifact_data"] = extracted_data if should_create and extracted_data else None
        state["artifact_title"] = title if should_create else None
        
        # Log decision
        data_points = len(extracted_data.get('x', extracted_data.get('categories', []))) if extracted_data else 0
        state["execution_log"].append({
            "step": "artifact_decision",
            "action": f"Artifact decision: YES - {chart_type}" if should_create else "Artifact decision: NO",
            "timestamp": datetime.now().isoformat(),
            "input": f"Query: {message[:80]}...",
            "output": f"Create: {should_create}, Type: {chart_type}, Data points: {data_points}"
        })
        
        print(f"🎯 Artifact Decision: {should_create}")
        if should_create:
            print(f"   Type: {chart_type}")
            print(f"   Title: {title}")
            print(f"   Data points: {data_points}")
            if extracted_data:
                print(f"   Sample data: {str(extracted_data)[:150]}...")
        
    except Exception as e:
        error_msg = f"Error in artifact decision: {str(e)}"
        print(f"❌ {error_msg}")
        state["error_log"] = state.get("error_log", [])
        state["error_log"].append(error_msg)
        
        state["execution_log"].append({
            "step": "artifact_decision",
            "action": "Error in artifact decision",
            "timestamp": datetime.now().isoformat(),
            "input": f"Query: {message[:100]}",
            "output": error_msg[:200]
        })
    
    return state

