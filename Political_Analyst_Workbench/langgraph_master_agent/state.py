"""
State Schema for Master Political Analyst Agent
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class MasterAgentState(TypedDict):
    """State management for the master agent"""
    
    # Conversation Management
    conversation_history: List[Dict[str, str]]  # [{role: "user/assistant", content: "..."}]
    current_message: str  # Current user message
    session_id: str  # Unique session identifier
    timestamp: str  # ISO format timestamp
    
    # Strategic Planning
    task_plan: str  # What the agent plans to do
    tools_to_use: List[str]  # List of tools/sub-agents to call
    reasoning: str  # Why this plan was chosen
    
    # Tool Execution Results
    tool_results: Dict[str, Any]  # Results from Tavily tools
    sub_agent_results: Dict[str, Any]  # Results from sub-agents
    execution_log: List[Dict[str, Any]]  # Step-by-step execution trace
    
    # Decision Making
    has_sufficient_info: bool  # Ready to answer?
    needs_clarification: bool  # Need to ask user?
    needs_more_tools: bool  # Need more data gathering?
    clarifying_questions: List[str]  # Questions to ask user
    
    # Response Generation
    final_response: str  # Formatted response for user
    citations: List[Dict[str, str]]  # Source citations
    confidence_score: float  # 0-1 confidence in response
    
    # Metadata
    metadata: Dict[str, Any]  # Additional tracking info
    error_log: List[str]  # Any errors encountered
    iteration_count: int  # Number of tool execution loops
    
    # Artifact fields (NEW)
    should_create_artifact: bool  # Should create artifact?
    artifact_type: Optional[str]  # viz, ppt, doc, data
    artifact_data: Optional[Dict]  # Data for artifact
    artifact: Optional[Dict]  # Created artifact metadata
    artifact_id: Optional[str]  # MongoDB ID after save

