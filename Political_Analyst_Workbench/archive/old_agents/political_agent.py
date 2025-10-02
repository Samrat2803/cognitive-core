"""
Political Analyst Workbench - Enhanced LangGraph Agent with Tavily Integration
"""

import os
import asyncio
import json
from typing import TypedDict, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode


# Load environment variables
load_dotenv()

# Tavily API Documentation for Agent Context
TAVILY_DOCUMENTATION = """
## Tavily Web API Capabilities

### Search API Features:
- **Real-time Web Search**: Live retrieval of current information from the web
- **Search Depth**: 'basic' and 'advanced' modes to control breadth/depth
- **Country Parameter**: Prioritizes results for a specified country (e.g., "India", "US")
- **Domain Targeting**: Focus searches on specific domains or exclude domains
- **Include Media**: Optionally include images and favicons in results

### Advanced Search Parameters:
- search_depth: "basic" (faster) or "advanced" (comprehensive)
- max_results: Number of results to return (1-20)
- include_answer: Get direct answers when available
- include_raw_content: Include full page content
- include_images: Include images in results
- country: Target specific country for localized results

### Best Practices:
- Use "advanced" search_depth for comprehensive research
- Specify country parameter for location-specific queries
- Use domain targeting for authoritative sources
- Combine multiple searches for complex queries

### Example Use Cases:
- Company research: "AI companies in Gurugram India" with country="India"
- Policy analysis: Use domain targeting for government sources
- Current events: Real-time search with advanced depth
- Local information: Country-specific searches for regional data
"""


class AgentState(TypedDict):
    """Enhanced State for the Political Analyst Agent"""
    messages: List[Dict[str, Any]]
    reasoning_log: List[Dict[str, Any]]  # Track agent reasoning steps
    current_step: str  # Current processing step
    search_history: List[Dict[str, Any]]  # Track search queries and results


class PoliticalAnalystAgent:
    """Basic Political Analyst Agent using LangGraph and Tavily"""
    
    def __init__(self):
        """Initialize the agent with LLM and tools"""
        
        # Validate API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not self.openai_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment/.env")
        if not self.tavily_key:
            raise RuntimeError("Missing TAVILY_API_KEY in environment/.env")
        
        # Initialize LLM with temperature=0 (per user rules)
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_key,
            model="gpt-4o-mini",
            temperature=0
        )
        
        # Initialize Enhanced Tavily search tool
        self.tavily_tool = TavilySearchResults(
            max_results=15,  # Increased for better coverage
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
            include_images=False,
            api_key=self.tavily_key
        )
        
        # Bind tools to LLM
        self.tools = [self.tavily_tool]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """Process user query with LLM and enhanced reasoning"""
        
        # Log current step
        state["current_step"] = "agent_processing"
        
        # Add system message with Tavily documentation
        system_msg = SystemMessage(content=f"""
You are a Political Analyst AI agent with access to real-time web search via Tavily.

{TAVILY_DOCUMENTATION}

When processing queries:
1. Analyze if web search is needed for current/specific information
2. For location-specific queries (like "companies in Gurugram"), use country parameter
3. For comprehensive research, use advanced search depth
4. Provide detailed, well-structured responses with sources

Always explain your reasoning and cite sources when using web search results.
""")
        
        # Convert state messages to LangChain format
        messages = [system_msg]
        for msg in state["messages"]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "tool":
                messages.append(ToolMessage(
                    content=msg["content"],
                    tool_call_id=msg.get("tool_call_id", "")
                ))
        
        # Log reasoning step
        reasoning_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": "agent_processing",
            "action": "Processing user query with LLM",
            "details": f"Processing {len(messages)} messages"
        }
        state["reasoning_log"].append(reasoning_entry)
        
        # Get response from LLM
        response = self.llm_with_tools.invoke(messages)
        
        # Convert back to state format
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # LLM wants to use tools
            tool_calls_info = [
                {
                    "id": tc.get("id", ""),
                    "name": tc.get("name", ""),
                    "args": tc.get("args", {})
                }
                for tc in response.tool_calls
            ]
            
            # Log tool usage decision
            reasoning_entry = {
                "timestamp": datetime.now().isoformat(),
                "step": "tool_decision",
                "action": "LLM decided to use tools",
                "details": f"Tool calls: {[tc['name'] for tc in tool_calls_info]}"
            }
            state["reasoning_log"].append(reasoning_entry)
            
            state["messages"].append({
                "role": "assistant",
                "content": response.content or "",
                "tool_calls": tool_calls_info
            })
        else:
            # Regular response
            reasoning_entry = {
                "timestamp": datetime.now().isoformat(),
                "step": "direct_response",
                "action": "LLM provided direct response without tools",
                "details": f"Response length: {len(response.content or '')}"
            }
            state["reasoning_log"].append(reasoning_entry)
            
            state["messages"].append({
                "role": "assistant",
                "content": response.content
            })
        
        return state
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue to tools or end"""
        
        last_message = state["messages"][-1]
        
        # If the last message has tool calls, continue to tools
        if last_message.get("tool_calls"):
            return "continue"
        else:
            return "end"
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a single user query and return detailed response with reasoning"""
        
        # Initialize enhanced state with user query
        initial_state = AgentState(
            messages=[{
                "role": "user",
                "content": user_query
            }],
            reasoning_log=[{
                "timestamp": datetime.now().isoformat(),
                "step": "initialization",
                "action": "Starting query processing",
                "details": f"Query: {user_query[:100]}..."
            }],
            current_step="initialized",
            search_history=[]
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Extract the final assistant response
        final_response = "I apologize, but I couldn't generate a response to your query."
        for msg in reversed(final_state["messages"]):
            if msg["role"] == "assistant" and msg.get("content"):
                final_response = msg["content"]
                break
        
        return {
            "response": final_response,
            "reasoning_log": final_state["reasoning_log"],
            "search_history": final_state["search_history"],
            "total_steps": len(final_state["reasoning_log"])
        }
    
    def process_query_sync(self, user_query: str) -> Dict[str, Any]:
        """Synchronous version of process_query"""
        return asyncio.run(self.process_query(user_query))


if __name__ == "__main__":
    # Test the agent
    agent = PoliticalAnalystAgent()
    
    # Test query
    test_query = "Find all the AI players and companies in Gurugram"
    print(f"Query: {test_query}")
    print("=" * 50)
    
    result = agent.process_query_sync(test_query)
    print(f"Response: {result['response']}")
    print(f"\nReasoning Steps: {result['total_steps']}")
    for step in result['reasoning_log']:
        print(f"- {step['step']}: {step['action']}")
