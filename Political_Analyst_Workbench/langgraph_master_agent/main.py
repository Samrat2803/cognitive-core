"""
Master Political Analyst Agent - Main Entry Point
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from langgraph_master_agent.graph import create_master_agent_graph
from langgraph_master_agent.state import MasterAgentState
from shared.observability import ObservabilityManager


class MasterPoliticalAnalyst:
    """Master Agent for Political Analysis"""
    
    def __init__(self, update_callback: Optional[Callable] = None):
        """
        Initialize Master Agent
        
        Args:
            update_callback: Optional callback for real-time updates
        """
        self.graph = create_master_agent_graph()
        self.update_callback = update_callback
        self.observability = ObservabilityManager()
        
        print("🎯 Master Political Analyst Agent initialized")
        print(f"   Observability: {self.observability.host}")
    
    async def process_query(
        self, 
        user_query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user query through master agent
        
        Args:
            user_query: User's question or request
            conversation_history: Optional conversation history (list of {role, content, timestamp})
            session_id: Optional session identifier
        
        Returns:
            Complete agent response with results and metadata
        """
        
        # Initialize state
        initial_state: MasterAgentState = {
            "conversation_history": conversation_history or [],
            "current_message": user_query,
            "session_id": session_id or f"session_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat(),
            
            "task_plan": "",
            "tools_to_use": [],
            "reasoning": "",
            
            "tool_results": {},
            "sub_agent_results": {},
            "execution_log": [],
            
            "has_sufficient_info": False,
            "needs_clarification": False,
            "needs_more_tools": False,
            "clarifying_questions": [],
            
            "final_response": "",
            "citations": [],
            "confidence_score": 0.0,
            
            "metadata": {},
            "error_log": [],
            "iteration_count": 0,
            
            # Artifact fields
            "should_create_artifact": False,
            "artifact_type": None,
            "artifact_data": None,
            "artifact": None,
            "artifact_id": None
        }
        
        print(f"\n🚀 Processing query: {user_query}")
        print("=" * 60)
        
        # Run graph
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract results
            result = {
                "response": final_state.get("final_response", "No response generated"),
                "citations": final_state.get("citations", []),
                "confidence": final_state.get("confidence_score", 0.0),
                "execution_log": final_state.get("execution_log", []),
                "tools_used": final_state.get("tools_to_use", []),
                "iterations": final_state.get("iteration_count", 0),
                "errors": final_state.get("error_log", []),
                "session_id": final_state.get("session_id", ""),
                "metadata": final_state.get("metadata", {}),
                # Artifact fields
                "should_create_artifact": final_state.get("should_create_artifact", False),
                "artifact_type": final_state.get("artifact_type"),
                "artifact": final_state.get("artifact"),
                "artifact_id": final_state.get("artifact_id")
            }
            
            # Call update callback if provided
            if self.update_callback:
                self.update_callback(result)
            
            return result
        
        except Exception as e:
            error_result = {
                "response": f"Error processing query: {str(e)}",
                "citations": [],
                "confidence": 0.0,
                "execution_log": [],
                "tools_used": [],
                "iterations": 0,
                "errors": [str(e)],
                "session_id": initial_state["session_id"],
                "metadata": {"error": True}
            }
            
            return error_result
    
    def process_query_sync(
        self, 
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous version of process_query"""
        return asyncio.run(self.process_query(user_query, conversation_history, session_id))


async def test_master_agent():
    """Test the master agent with sample queries"""
    
    def print_update(result: Dict[str, Any]):
        """Print results in formatted way"""
        print("\n" + "=" * 60)
        print("🤖 MASTER AGENT RESPONSE:")
        print("=" * 60)
        print(result["response"])
        print("\n" + "=" * 60)
        print(f"📊 METADATA:")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Tools Used: {', '.join(result['tools_used'])}")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Citations: {len(result['citations'])}")
        
        if result.get("errors"):
            print(f"   ⚠️  Errors: {len(result['errors'])}")
        
        print("\n📝 EXECUTION LOG:")
        for log in result.get("execution_log", []):
            print(f"   [{log.get('step', 'unknown')}] {log.get('action', '')}")
        print("=" * 60)
    
    agent = MasterPoliticalAnalyst(update_callback=print_update)
    
    # Test queries
    test_queries = [
        "What are the latest developments in AI policy?",
        "Search for news about climate change negotiations",
        # "Analyze sentiment on nuclear energy policy"  # Will call sentiment sub-agent
    ]
    
    for query in test_queries:
        print(f"\n\n{'*' * 60}")
        print(f"TEST QUERY: {query}")
        print('*' * 60)
        
        result = await agent.process_query(query)
        
        # Results printed by callback
        
        print("\n⏸️  Press Enter to continue to next query...")
        # input()  # Uncomment for interactive testing


if __name__ == "__main__":
    print("🎯 Master Political Analyst Agent")
    print("=" * 60)
    print("Testing master agent infrastructure...\n")
    
    try:
        asyncio.run(test_master_agent())
        
        print("\n✅ Master Agent test completed!")
        print("\nNext steps:")
        print("1. ✅ Master agent infrastructure working")
        print("2. 📝 Implement sentiment analyzer sub-agent")
        print("3. 🔗 Connect sub-agent to master via sub_agent_caller")
        print("4. 🎨 Build UI for real-time visualization")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

