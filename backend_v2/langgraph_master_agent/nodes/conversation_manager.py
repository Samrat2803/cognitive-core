"""
Conversation Manager Node
Handles conversation context and message history
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from datetime import datetime
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


@observe(name="conversation_manager_node")
async def conversation_manager(state: dict) -> dict:
    """
    Manage conversation context and history
    
    Responsibilities:
    - Initialize new conversations
    - Maintain conversation history
    - Detect follow-up vs new queries
    - Clean up old context
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with conversation context
    """
    # Initialize if first message
    if not state.get("conversation_history"):
        state["conversation_history"] = []
    
    if not state.get("session_id"):
        state["session_id"] = f"session_{int(datetime.now().timestamp())}"
    
    # Add current message to history
    current_msg = state.get("current_message", "")
    if current_msg:
        state["conversation_history"].append({
            "role": "user",
            "content": current_msg,
            "timestamp": datetime.now().isoformat()
        })
    
    # Keep only last N messages (per config)
    max_history = 10
    if len(state["conversation_history"]) > max_history:
        state["conversation_history"] = state["conversation_history"][-max_history:]
    
    # Initialize execution log
    if not state.get("execution_log"):
        state["execution_log"] = []
    
    state["execution_log"].append({
        "step": "conversation_manager",
        "action": "Context initialized",
        "timestamp": datetime.now().isoformat(),
        "input": f"User message: {current_msg[:100]}...",
        "output": f"Session ID: {state['session_id']}, History: {len(state['conversation_history'])} messages"
    })
    
    # Initialize metadata
    if not state.get("metadata"):
        state["metadata"] = {}
    
    state["metadata"]["conversation_managed"] = True
    state["timestamp"] = datetime.now().isoformat()
    
    return state

