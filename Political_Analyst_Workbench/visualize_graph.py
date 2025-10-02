"""
Visualize the Master Agent Graph
Generates a visual representation of the LangGraph structure
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from langgraph_master_agent.graph import create_master_agent_graph


def visualize_graph():
    """Generate and display graph visualization"""
    print("🎨 Master Agent Graph Visualization")
    print("="*70)
    
    try:
        # Create graph
        app = create_master_agent_graph()
        
        # Get mermaid diagram
        print("\n📊 Generating Mermaid diagram...\n")
        mermaid = app.get_graph().draw_mermaid()
        
        print(mermaid)
        
        print("\n"+"="*70)
        print("✅ Mermaid diagram generated!")
        print("\nTo visualize:")
        print("1. Copy the mermaid code above")
        print("2. Visit: https://mermaid.live/")
        print("3. Paste the code to see interactive diagram")
        print("\nOr use LangGraph Studio for live visualization!")
        print("="*70)
        
        # Try to save to file
        try:
            with open("master_agent_graph.mmd", "w") as f:
                f.write(mermaid)
            print("\n💾 Saved to: master_agent_graph.mmd")
        except Exception as e:
            print(f"\n⚠️  Could not save file: {e}")
        
        # Print ASCII representation
        print("\n📐 Graph Structure (ASCII):")
        print("""
        ┌─────────────────────────┐
        │       START             │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │  Conversation Manager   │
        │  - Init context         │
        │  - Track history        │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │  Strategic Planner      │
        │  - Analyze intent       │
        │  - Select tools         │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │  Tool Executor          │
        │  - Tavily Search        │
        │  - Sub-agents           │
        └───────────┬─────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │  Decision Gate          │
        │  - Check sufficiency    │
        └───────────┬─────────────┘
                    │
            ┌───────┴───────┐
            │               │
            ▼               ▼
        [Loop?]         [Continue]
            │               │
            │               ▼
            │   ┌─────────────────────────┐
            │   │  Response Synthesizer   │
            │   │  - Compile results      │
            │   │  - Format response      │
            │   └───────────┬─────────────┘
            │               │
            └───────────────┤
                            ▼
                    ┌─────────────────────────┐
                    │        END              │
                    └─────────────────────────┘
        """)
        
        # Print node details
        print("\n📋 Node Details:")
        print("="*70)
        
        nodes = [
            ("conversation_manager", "Initialize context, track history"),
            ("strategic_planner", "Analyze query, select tools (LLM)"),
            ("tool_executor", "Execute Tavily tools, call sub-agents"),
            ("decision_gate", "Route: loop or continue"),
            ("response_synthesizer", "Compile and format response (LLM)")
        ]
        
        for node_name, description in nodes:
            print(f"  • {node_name:25} → {description}")
        
        print("="*70)
        
    except Exception as e:
        print(f"❌ Error generating visualization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    visualize_graph()

