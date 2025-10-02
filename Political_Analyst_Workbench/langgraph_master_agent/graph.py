"""
Master Agent LangGraph Definition
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from langgraph.graph import StateGraph, END
from langgraph_master_agent.state import MasterAgentState
from langgraph_master_agent.nodes.conversation_manager import conversation_manager
from langgraph_master_agent.nodes.strategic_planner import strategic_planner
from langgraph_master_agent.nodes.tool_executor import tool_executor
from langgraph_master_agent.nodes.decision_gate import decision_gate
from langgraph_master_agent.nodes.response_synthesizer import response_synthesizer
from langgraph_master_agent.nodes.artifact_decision import artifact_decision
from langgraph_master_agent.nodes.artifact_creator import artifact_creator


def create_master_agent_graph():
    """
    Create the master agent graph
    
    Flow:
    START → Conversation Manager → Strategic Planner → Tool Executor → 
    Decision Gate → [Loop or Continue] → Response Synthesizer → END
    """
    
    # Create graph
    workflow = StateGraph(MasterAgentState)
    
    # Add nodes
    workflow.add_node("conversation_manager", conversation_manager)
    workflow.add_node("strategic_planner", strategic_planner)
    workflow.add_node("tool_executor", tool_executor)
    workflow.add_node("decision_gate", decision_gate)
    workflow.add_node("response_synthesizer", response_synthesizer)
    workflow.add_node("artifact_decision", artifact_decision)
    workflow.add_node("artifact_creator", artifact_creator)
    
    # Define edges
    workflow.set_entry_point("conversation_manager")
    
    # Conversation → Planner
    workflow.add_edge("conversation_manager", "strategic_planner")
    
    # Planner → Tool Executor
    workflow.add_edge("strategic_planner", "tool_executor")
    
    # Tool Executor → Decision Gate
    workflow.add_edge("tool_executor", "decision_gate")
    
    # Decision Gate → Conditional routing
    def should_continue(state: dict) -> str:
        """Determine if we should continue or synthesize"""
        
        if state.get("needs_more_tools", False):
            # Loop back to tool executor
            return "tool_executor"
        elif state.get("has_sufficient_info", True):
            # Proceed to synthesis
            return "response_synthesizer"
        else:
            # Default to synthesis
            return "response_synthesizer"
    
    workflow.add_conditional_edges(
        "decision_gate",
        should_continue,
        {
            "tool_executor": "tool_executor",
            "response_synthesizer": "response_synthesizer"
        }
    )
    
    # Response Synthesizer → Artifact Decision
    workflow.add_edge("response_synthesizer", "artifact_decision")
    
    # Artifact Decision → Conditional routing
    def should_create_artifact(state: dict) -> str:
        """Determine if we should create artifact"""
        if state.get("should_create_artifact", False):
            return "create_artifact"
        else:
            return "end"
    
    workflow.add_conditional_edges(
        "artifact_decision",
        should_create_artifact,
        {
            "create_artifact": "artifact_creator",
            "end": END
        }
    )
    
    # Artifact Creator → END
    workflow.add_edge("artifact_creator", END)
    
    # Compile graph
    app = workflow.compile()
    
    return app


def visualize_graph():
    """Generate graph visualization (if mermaid available)"""
    try:
        app = create_master_agent_graph()
        
        # Try to get mermaid diagram
        mermaid_code = app.get_graph().draw_mermaid()
        
        print("📊 Master Agent Graph Structure:")
        print("=" * 60)
        print(mermaid_code)
        print("=" * 60)
        
        return mermaid_code
    
    except Exception as e:
        print(f"Visualization not available: {e}")
        print("\nGraph Structure:")
        print("START → conversation_manager → strategic_planner → tool_executor")
        print("      → decision_gate → [loop or continue] → response_synthesizer → END")
        
        return None


if __name__ == "__main__":
    print("🎯 Creating Master Agent Graph...\n")
    
    # Visualize
    visualize_graph()
    
    # Create graph
    graph = create_master_agent_graph()
    print("\n✅ Master Agent Graph created successfully!")
    print(f"   Nodes: conversation_manager, strategic_planner, tool_executor, decision_gate, response_synthesizer")
    print(f"   Edges: Linear flow with conditional loop at decision_gate")

