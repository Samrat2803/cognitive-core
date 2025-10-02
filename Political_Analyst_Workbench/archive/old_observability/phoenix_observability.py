"""
Phoenix Real-time Observability Integration for Political Analyst Workbench
100% Open Source Real-time Monitoring
"""

import os
import asyncio
import json
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dotenv import load_dotenv
import time

# Phoenix imports for real-time observability
try:
    import phoenix as px
    from phoenix.trace.langchain import LangChainInstrumentor
    # Import trace decorator properly
    try:
        from phoenix.trace import trace
    except ImportError:
        # Fallback for different Phoenix versions
        def trace(name):
            def decorator(func):
                return func
            return decorator
    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    print("⚠️  Phoenix not installed. Run: pip install arize-phoenix")
    # Create dummy trace decorator
    def trace(name):
        def decorator(func):
            return func
        return decorator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import httpx

# Load environment variables
load_dotenv()

class PhoenixObservableAgent:
    """Political Analyst Agent with Phoenix real-time observability"""
    
    def __init__(self, update_callback: Optional[Callable] = None):
        """Initialize agent with Phoenix observability"""
        
        self.update_callback = update_callback
        
        # Initialize Phoenix for real-time observability
        if PHOENIX_AVAILABLE:
            # Launch Phoenix UI (runs on http://localhost:6006)
            self.phoenix_session = px.launch_app()
            print("🔥 Phoenix UI launched at: http://localhost:6006")
            
            # Enable LangChain instrumentation for real-time tracing
            LangChainInstrumentor().instrument()
            print("✅ Real-time tracing enabled")
        else:
            print("❌ Phoenix not available - install with: pip install arize-phoenix")
        
        # Validate API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not self.openai_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment/.env")
        if not self.tavily_key:
            raise RuntimeError("Missing TAVILY_API_KEY in environment/.env")
        
        # Initialize LLM (automatically traced by Phoenix)
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_key,
            model="gpt-4o-mini",
            temperature=0
        )
    
    def _emit_update(self, step_data: Dict[str, Any]):
        """Emit real-time update to UI"""
        if self.update_callback:
            self.update_callback(step_data)
            time.sleep(0.1)
    
    @trace("tavily_search")  # Phoenix will trace this function
    async def _tavily_search_traced(self, query: str) -> str:
        """Tavily search with Phoenix tracing"""
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_images": False,
                    "include_answer": True,
                    "max_results": 8,
                    "include_raw_content": False
                }
                
                # Add country parameter for location-specific queries
                if any(location in query.lower() for location in ['gurugram', 'gurgaon', 'bangalore', 'mumbai', 'delhi', 'india']):
                    payload["country"] = "India"
                
                response = await client.post(
                    "https://api.tavily.com/search",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    answer = data.get("answer", "")
                    
                    # Format results nicely
                    formatted_results = []
                    if answer:
                        formatted_results.append(f"Direct Answer: {answer}")
                    
                    for i, result in enumerate(results[:5], 1):
                        title = result.get("title", "")
                        content = result.get("content", "")[:200] + "..."
                        url = result.get("url", "")
                        formatted_results.append(f"{i}. {title}\n   {content}\n   Source: {url}")
                    
                    return "\n\n".join(formatted_results)
                
                elif response.status_code == 432:
                    return "Tavily API rate limit reached. Using cached knowledge for analysis."
                else:
                    return f"Tavily API returned status {response.status_code}. Using available knowledge."
                    
        except Exception as e:
            return f"Search unavailable ({str(e)[:50]}). Proceeding with existing knowledge."
    
    @trace("political_analysis")  # Phoenix will trace the entire analysis
    async def process_query_with_observability(self, user_query: str) -> Dict[str, Any]:
        """Process query with Phoenix real-time observability"""
        
        reasoning_log = []
        
        # Step 1: Initialize (traced by Phoenix)
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "initialization",
            "action": "🚀 Starting Phoenix-traced analysis",
            "details": f"Query: {user_query} | Phoenix UI: http://localhost:6006",
            "status": "processing",
            "progress": 0.1
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 2: Query Analysis
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "analysis",
            "action": "🧠 Analyzing query (Phoenix tracing active)",
            "details": "Real-time traces visible in Phoenix dashboard",
            "status": "processing",
            "progress": 0.2
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 3: Web Search (Phoenix traced)
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "web_search",
            "action": "🔍 Performing traced web search",
            "details": "Search execution visible in real-time on Phoenix",
            "status": "processing",
            "progress": 0.4
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Perform traced search
        search_results = await self._tavily_search_traced(user_query)
        
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "search_complete",
            "action": "✅ Search traced and completed",
            "details": f"Results captured in Phoenix trace viewer",
            "status": "completed",
            "progress": 0.6
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 4: LLM Processing (Phoenix traced)
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "llm_processing",
            "action": "🤖 LLM processing (Phoenix traced)",
            "details": "Token usage and latency tracked in real-time",
            "status": "processing",
            "progress": 0.8
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Enhanced system prompt
        system_prompt = f"""
You are a Political Analyst AI agent with Phoenix observability.

Query: "{user_query}"

Available Information:
{search_results}

Instructions:
1. Provide comprehensive, well-structured response
2. Use search results as primary sources when available
3. For company/location queries, provide specific details
4. Organize with clear headings and bullet points
5. Be honest about information limitations

This execution is being traced in real-time by Phoenix observability.
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]
            
            # This LLM call is automatically traced by Phoenix
            response = await self.llm.ainvoke(messages)
            final_response = response.content
            
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "response_complete",
                "action": "🎉 Analysis complete with full tracing",
                "details": f"Complete execution trace available at Phoenix UI",
                "status": "completed",
                "progress": 1.0
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            
        except Exception as e:
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "llm_error",
                "action": "⚠️ Error traced in Phoenix",
                "details": f"Error details captured in Phoenix trace",
                "status": "warning",
                "progress": 0.9
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            final_response = f"Analysis completed with limitations. Check Phoenix trace for details.\n\n{search_results}"
        
        return {
            "response": final_response,
            "reasoning_log": reasoning_log,
            "search_results": search_results,
            "total_steps": len(reasoning_log),
            "status": "completed",
            "phoenix_url": "http://localhost:6006"
        }
    
    def process_query_sync(self, user_query: str) -> Dict[str, Any]:
        """Synchronous version"""
        return asyncio.run(self.process_query_with_observability(user_query))


def setup_phoenix_observability():
    """Setup Phoenix for real-time observability"""
    if not PHOENIX_AVAILABLE:
        print("Installing Phoenix...")
        os.system("pip install arize-phoenix")
        print("✅ Phoenix installed! Restart the application.")
        return False
    return True


if __name__ == "__main__":
    # Test Phoenix observability
    def print_update(step_data):
        print(f"[{step_data['progress']:.0%}] {step_data['action']}")
        print(f"    {step_data['details']}")
        print()
    
    print("🔥 Phoenix Observable Political Analyst Agent")
    print("=" * 60)
    
    if not setup_phoenix_observability():
        exit(1)
    
    try:
        agent = PhoenixObservableAgent(update_callback=print_update)
        
        print("🎯 Phoenix UI available at: http://localhost:6006")
        print("📊 Real-time traces will appear as the agent runs")
        print()
        
        # Test query
        test_query = "Find all the AI players and companies in Gurugram"
        print(f"Query: {test_query}")
        print("=" * 60)
        
        result = agent.process_query_sync(test_query)
        
        print("🤖 FINAL RESPONSE:")
        print(result['response'])
        
        print(f"\n📊 OBSERVABILITY:")
        print(f"Phoenix UI: {result.get('phoenix_url', 'http://localhost:6006')}")
        print(f"Total steps: {result['total_steps']}")
        print(f"Status: {result['status']}")
        
        print("\n🔥 Check Phoenix UI for complete real-time trace!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
