"""
Detailed Execution Trace Visualizer for Master Agent
Shows data flow, decisions, and inputs/outputs at each node
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from langgraph_master_agent.main import MasterPoliticalAnalyst
from langgraph_master_agent.graph import create_master_agent_graph


class ExecutionTracer:
    """Traces execution through the graph with detailed logging"""
    
    def __init__(self):
        self.trace_log = []
        self.current_step = 0
    
    def log_node_execution(self, node_name: str, state_before: dict, state_after: dict):
        """Log detailed node execution"""
        self.current_step += 1
        
        # Extract key changes
        changes = self._detect_state_changes(state_before, state_after)
        
        entry = {
            "step": self.current_step,
            "node": node_name,
            "timestamp": datetime.now().isoformat(),
            "input_summary": self._summarize_input(state_before, node_name),
            "processing": self._describe_processing(node_name, state_before, state_after),
            "output_summary": self._summarize_output(state_after, node_name),
            "decisions": self._extract_decisions(state_after, node_name),
            "data_passed_to_next": self._get_next_node_input(state_after, node_name),
            "state_changes": changes
        }
        
        self.trace_log.append(entry)
    
    def _detect_state_changes(self, before: dict, after: dict) -> dict:
        """Detect what changed in state"""
        changes = {}
        
        # Check key fields
        key_fields = [
            'tools_to_use', 'task_plan', 'reasoning', 'tool_results', 
            'sub_agent_results', 'has_sufficient_info', 'needs_more_tools',
            'final_response', 'should_create_artifact', 'artifact_type',
            'artifact', 'confidence_score', 'citations'
        ]
        
        for field in key_fields:
            before_val = before.get(field)
            after_val = after.get(field)
            
            if before_val != after_val:
                changes[field] = {
                    "before": self._truncate(str(before_val), 100),
                    "after": self._truncate(str(after_val), 100)
                }
        
        return changes
    
    def _summarize_input(self, state: dict, node_name: str) -> dict:
        """Summarize input to node"""
        if node_name == "conversation_manager":
            return {
                "current_message": state.get("current_message", "N/A")[:100],
                "history_length": len(state.get("conversation_history", []))
            }
        
        elif node_name == "strategic_planner":
            return {
                "current_message": state.get("current_message", "N/A")[:100],
                "conversation_context": len(state.get("conversation_history", [])),
                "previous_tools": state.get("tools_to_use", [])
            }
        
        elif node_name == "tool_executor":
            return {
                "tools_to_execute": state.get("tools_to_use", []),
                "query": state.get("current_message", "N/A")[:100]
            }
        
        elif node_name == "decision_gate":
            return {
                "has_tool_results": bool(state.get("tool_results")),
                "has_sub_agent_results": bool(state.get("sub_agent_results")),
                "iteration_count": state.get("iteration_count", 0)
            }
        
        elif node_name == "response_synthesizer":
            return {
                "query": state.get("current_message", "N/A")[:100],
                "tool_results_count": len(state.get("tool_results", {})),
                "sub_agent_results_count": len(state.get("sub_agent_results", {})),
                "conversation_length": len(state.get("conversation_history", []))
            }
        
        elif node_name == "artifact_decision":
            return {
                "message": state.get("current_message", "N/A")[:100],
                "response_length": len(state.get("final_response", "")),
                "has_conversation_history": len(state.get("conversation_history", [])) > 0
            }
        
        elif node_name == "artifact_creator":
            return {
                "artifact_type": state.get("artifact_type"),
                "has_artifact_data": state.get("artifact_data") is not None
            }
        
        return {}
    
    def _describe_processing(self, node_name: str, before: dict, after: dict) -> str:
        """Describe what the node did"""
        if node_name == "conversation_manager":
            return "Initialized conversation context, added user message to history"
        
        elif node_name == "strategic_planner":
            tools = after.get("tools_to_use", [])
            return f"Analyzed query using LLM, selected tools: {', '.join(tools) if tools else 'none'}"
        
        elif node_name == "tool_executor":
            tools = before.get("tools_to_use", [])
            results = len(after.get("tool_results", {}))
            return f"Executed {len(tools)} tools, got {results} result sets"
        
        elif node_name == "decision_gate":
            decision = "CONTINUE" if after.get("needs_more_tools") else "SYNTHESIZE"
            return f"Evaluated results, decided to: {decision}"
        
        elif node_name == "response_synthesizer":
            length = len(after.get("final_response", ""))
            citations = len(after.get("citations", []))
            return f"Synthesized response using LLM ({length} chars, {citations} citations)"
        
        elif node_name == "artifact_decision":
            should_create = after.get("should_create_artifact", False)
            artifact_type = after.get("artifact_type", "N/A")
            return f"Decided: {'CREATE' if should_create else 'NO'} artifact ({artifact_type if should_create else 'none'})"
        
        elif node_name == "artifact_creator":
            artifact_id = after.get("artifact_id", "N/A")
            return f"Created and uploaded artifact to S3 (ID: {artifact_id})"
        
        return "Processing..."
    
    def _summarize_output(self, state: dict, node_name: str) -> dict:
        """Summarize output from node"""
        output = {}
        
        if node_name == "conversation_manager":
            output["history_length"] = len(state.get("conversation_history", []))
            output["session_id"] = state.get("session_id", "N/A")
        
        elif node_name == "strategic_planner":
            output["tools_selected"] = state.get("tools_to_use", [])
            output["reasoning"] = self._truncate(state.get("reasoning", "N/A"), 150)
        
        elif node_name == "tool_executor":
            output["tool_results"] = list(state.get("tool_results", {}).keys())
            output["sub_agent_results"] = list(state.get("sub_agent_results", {}).keys())
        
        elif node_name == "decision_gate":
            output["has_sufficient_info"] = state.get("has_sufficient_info", False)
            output["needs_more_tools"] = state.get("needs_more_tools", False)
            output["iteration_count"] = state.get("iteration_count", 0)
        
        elif node_name == "response_synthesizer":
            output["response_length"] = len(state.get("final_response", ""))
            output["citations_count"] = len(state.get("citations", []))
            output["confidence"] = state.get("confidence_score", 0)
        
        elif node_name == "artifact_decision":
            output["should_create"] = state.get("should_create_artifact", False)
            output["artifact_type"] = state.get("artifact_type")
            data = state.get("artifact_data", {})
            if data:
                output["data_points"] = len(data.get("x", data.get("categories", [])))
        
        elif node_name == "artifact_creator":
            output["artifact_id"] = state.get("artifact_id")
            output["storage"] = state.get("artifact", {}).get("storage", "N/A")
        
        return output
    
    def _extract_decisions(self, state: dict, node_name: str) -> List[str]:
        """Extract decisions made at this node"""
        decisions = []
        
        if node_name == "strategic_planner":
            tools = state.get("tools_to_use", [])
            if tools:
                decisions.append(f"Selected tools: {', '.join(tools)}")
            else:
                decisions.append("No tools selected (LLM returned empty)")
        
        elif node_name == "decision_gate":
            if state.get("needs_more_tools"):
                decisions.append("DECISION: Loop back to tool executor")
            elif state.get("has_sufficient_info"):
                decisions.append("DECISION: Proceed to response synthesis")
            
            if state.get("iteration_count", 0) >= 3:
                decisions.append("WARNING: Hit max iterations")
        
        elif node_name == "artifact_decision":
            if state.get("should_create_artifact"):
                artifact_type = state.get("artifact_type", "unknown")
                decisions.append(f"DECISION: Create {artifact_type}")
            else:
                decisions.append("DECISION: No artifact needed")
        
        return decisions
    
    def _get_next_node_input(self, state: dict, node_name: str) -> dict:
        """Get what will be passed to next node"""
        # Key fields that next node will see
        next_input = {
            "conversation_history_length": len(state.get("conversation_history", [])),
            "current_message": state.get("current_message", "N/A")[:50] + "...",
        }
        
        if state.get("tools_to_use"):
            next_input["tools_to_use"] = state["tools_to_use"]
        
        if state.get("tool_results"):
            next_input["has_tool_results"] = True
            next_input["tool_results_keys"] = list(state["tool_results"].keys())
        
        if state.get("final_response"):
            next_input["has_final_response"] = True
        
        if state.get("should_create_artifact"):
            next_input["artifact_type"] = state.get("artifact_type")
        
        return next_input
    
    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text to max length"""
        if len(text) <= max_len:
            return text
        return text[:max_len] + "..."
    
    def generate_html_visualization(self, output_file: str = "execution_trace.html"):
        """Generate HTML visualization"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Master Agent Execution Trace</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: #4ec9b0;
            text-align: center;
            margin-bottom: 30px;
        }
        .trace-step {
            background: #252526;
            border-left: 4px solid #007acc;
            margin: 20px 0;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        .step-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            border-bottom: 1px solid #3e3e42;
            padding-bottom: 10px;
        }
        .step-number {
            background: #007acc;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        .node-name {
            color: #4ec9b0;
            font-size: 1.3em;
            font-weight: bold;
        }
        .timestamp {
            color: #858585;
            font-size: 0.9em;
        }
        .section {
            margin: 15px 0;
            padding: 10px;
            background: #2d2d30;
            border-radius: 3px;
        }
        .section-title {
            color: #dcdcaa;
            font-weight: bold;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }
        .section-title::before {
            content: "▶";
            margin-right: 8px;
            color: #569cd6;
        }
        .section-content {
            padding-left: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .key-value {
            margin: 5px 0;
        }
        .key {
            color: #9cdcfe;
            font-weight: bold;
        }
        .value {
            color: #ce9178;
        }
        .decision {
            background: #3a3d41;
            padding: 8px 12px;
            margin: 5px 0;
            border-left: 3px solid #f48771;
            border-radius: 3px;
        }
        .arrow {
            text-align: center;
            color: #007acc;
            font-size: 2em;
            margin: 10px 0;
        }
        .changes {
            background: #1e1e1e;
            padding: 10px;
            border-radius: 3px;
            margin-top: 10px;
        }
        .change-item {
            margin: 8px 0;
            padding: 8px;
            background: #252526;
            border-radius: 3px;
        }
        .before {
            color: #f48771;
        }
        .after {
            color: #4ec9b0;
        }
        ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Master Agent Execution Trace</h1>
        <p style="text-align: center; color: #858585; margin-bottom: 40px;">
            Detailed step-by-step execution with inputs, processing, outputs, and decisions
        </p>
"""
        
        for entry in self.trace_log:
            html += f"""
        <div class="trace-step">
            <div class="step-header">
                <span class="step-number">Step {entry['step']}</span>
                <span class="node-name">{entry['node']}</span>
                <span class="timestamp">{entry['timestamp'].split('T')[1].split('.')[0]}</span>
            </div>
            
            <div class="section">
                <div class="section-title">📥 Input to Node</div>
                <div class="section-content">
"""
            for key, value in entry['input_summary'].items():
                html += f'                    <div class="key-value"><span class="key">{key}:</span> <span class="value">{value}</span></div>\n'
            
            html += """
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">⚙️ Processing</div>
                <div class="section-content">
"""
            html += f'                    {entry["processing"]}\n'
            html += """
                </div>
            </div>
"""
            
            if entry['decisions']:
                html += """
            <div class="section">
                <div class="section-title">🎯 Decisions Made</div>
                <div class="section-content">
"""
                for decision in entry['decisions']:
                    html += f'                    <div class="decision">{decision}</div>\n'
                html += """
                </div>
            </div>
"""
            
            html += """
            <div class="section">
                <div class="section-title">📤 Output from Node</div>
                <div class="section-content">
"""
            for key, value in entry['output_summary'].items():
                html += f'                    <div class="key-value"><span class="key">{key}:</span> <span class="value">{value}</span></div>\n'
            
            html += """
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">🔄 Data Passed to Next Node</div>
                <div class="section-content">
"""
            for key, value in entry['data_passed_to_next'].items():
                html += f'                    <div class="key-value"><span class="key">{key}:</span> <span class="value">{value}</span></div>\n'
            
            html += """
                </div>
            </div>
"""
            
            if entry['state_changes']:
                html += """
            <div class="section">
                <div class="section-title">📝 State Changes</div>
                <div class="changes">
"""
                for field, change in entry['state_changes'].items():
                    html += f"""
                    <div class="change-item">
                        <strong>{field}</strong><br>
                        <span class="before">Before:</span> {change['before']}<br>
                        <span class="after">After:</span> {change['after']}
                    </div>
"""
                html += """
                </div>
            </div>
"""
            
            html += """
        </div>
"""
            
            # Add arrow between steps (except after last step)
            if entry['step'] < len(self.trace_log):
                html += '        <div class="arrow">↓</div>\n'
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML visualization saved to: {output_file}")
        return output_file
    
    def print_trace(self):
        """Print trace to console"""
        print("\n" + "=" * 80)
        print("EXECUTION TRACE - DETAILED DATA FLOW")
        print("=" * 80 + "\n")
        
        for entry in self.trace_log:
            print(f"\n{'=' * 80}")
            print(f"STEP {entry['step']}: {entry['node'].upper()}")
            print(f"{'=' * 80}\n")
            
            print("📥 INPUT:")
            for key, value in entry['input_summary'].items():
                print(f"   • {key}: {value}")
            
            print(f"\n⚙️  PROCESSING:")
            print(f"   {entry['processing']}")
            
            if entry['decisions']:
                print(f"\n🎯 DECISIONS:")
                for decision in entry['decisions']:
                    print(f"   • {decision}")
            
            print(f"\n📤 OUTPUT:")
            for key, value in entry['output_summary'].items():
                print(f"   • {key}: {value}")
            
            print(f"\n🔄 DATA PASSED TO NEXT NODE:")
            for key, value in entry['data_passed_to_next'].items():
                print(f"   • {key}: {value}")
            
            if entry['state_changes']:
                print(f"\n📝 STATE CHANGES:")
                for field, change in entry['state_changes'].items():
                    print(f"   • {field}:")
                    print(f"     Before: {change['before']}")
                    print(f"     After:  {change['after']}")
            
            print("\n" + "↓" * 40)


async def trace_agent_execution(query: str, conversation_history: list = None):
    """Execute agent with detailed tracing"""
    
    print(f"\n🎯 Tracing execution for query: \"{query}\"\n")
    
    # We'll need to manually step through the graph to capture state at each node
    # For now, let's use the execution log from the agent
    
    agent = MasterPoliticalAnalyst()
    result = await agent.process_query(query, conversation_history)
    
    # Print execution log from agent
    print("\n" + "=" * 80)
    print("EXECUTION LOG FROM AGENT")
    print("=" * 80 + "\n")
    
    for i, log_entry in enumerate(result.get('execution_log', []), 1):
        print(f"{i}. [{log_entry.get('step')}] {log_entry.get('action')}")
        if log_entry.get('input'):
            print(f"   INPUT: {log_entry['input']}")
        if log_entry.get('output'):
            print(f"   OUTPUT: {log_entry['output']}")
        print()
    
    return result


async def main():
    """Main visualization function"""
    print("=" * 80)
    print("  MASTER AGENT EXECUTION TRACE VISUALIZER")
    print("=" * 80)
    
    # First, show the graph structure
    print("\n📊 GRAPH STRUCTURE (Mermaid Diagram):\n")
    try:
        graph = create_master_agent_graph()
        mermaid = graph.get_graph().draw_mermaid()
        print(mermaid)
        
        # Save to file
        with open("graph_structure.md", "w") as f:
            f.write("# Master Agent Graph Structure\n\n")
            f.write("```mermaid\n")
            f.write(mermaid)
            f.write("\n```\n")
        print("\n✅ Graph structure saved to: graph_structure.md")
    except Exception as e:
        print(f"⚠️  Could not generate mermaid diagram: {e}")
    
    # Now trace actual execution
    print("\n" + "=" * 80)
    print("  EXECUTING TEST QUERIES WITH TRACING")
    print("=" * 80)
    
    # Query 1
    query1 = "how has india been affected by US tariffs"
    result1 = await trace_agent_execution(query1, [])
    
    # Build conversation history for query 2
    conversation_history = [
        {"role": "user", "content": query1, "timestamp": datetime.now().isoformat()},
        {"role": "assistant", "content": result1['response'], "timestamp": datetime.now().isoformat()}
    ]
    
    print("\n\n⏸️  Waiting 2 seconds...\n")
    await asyncio.sleep(2)
    
    # Query 2
    query2 = "create a trend visualization of this data"
    result2 = await trace_agent_execution(query2, conversation_history)
    
    print("\n" + "=" * 80)
    print("  VISUALIZATION COMPLETE")
    print("=" * 80)
    print("\n📁 Generated files:")
    print("   • graph_structure.md - Mermaid diagram of graph structure")
    print("\n💡 To create interactive HTML visualization, we need to instrument")
    print("   each node with state tracking. See EXECUTION_FLOW_LOG.md for")
    print("   detailed manual trace of the test execution.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Visualization interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

