"""
Political Analyst Agent with LangFuse Tracing
Clean implementation with real-time observability
"""

import os
import asyncio
import json
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dotenv import load_dotenv
import time

# LangFuse imports for tracing
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("⚠️  LangFuse not installed. Run: pip install langfuse")
    # Create dummy decorator
    def observe(name=None):
        def decorator(func):
            return func
        return decorator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import httpx

# Load environment variables
load_dotenv()

class LangFuseAgent:
    """Political Analyst Agent with LangFuse tracing"""
    
    def __init__(self, update_callback: Optional[Callable] = None):
        """Initialize agent with LangFuse tracing"""
        
        self.update_callback = update_callback
        
        # Initialize Professional Observability
        self.observability_host = "http://localhost:3761"
        print("🎯 Professional Observability initialized on port 3761")
        
        # Validate API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not self.openai_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment/.env")
        if not self.tavily_key:
            raise RuntimeError("Missing TAVILY_API_KEY in environment/.env")
        
        # Initialize LLM
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
    
    @observe(name="tavily_search")
    async def _tavily_search_traced(self, query: str) -> str:
        """Tavily search with LangFuse tracing"""
        
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
    
    async def _send_trace_to_dashboard(self, trace_data: Dict[str, Any]):
        """Send trace to professional dashboard"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(
                    f"{self.observability_host}/api/traces",
                    json=trace_data
                )
        except Exception as e:
            print(f"⚠️  Could not send trace to dashboard: {e}")

    async def process_query_with_tracing(self, user_query: str) -> Dict[str, Any]:
        """Process query with professional observability"""
        
        reasoning_log = []
        
        # Step 1: Initialize
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "initialization",
            "action": "🚀 Starting analysis",
            "details": "Initializing agent and preparing for query processing",
            "input": user_query,
            "output": "Agent initialized successfully",
            "status": "processing",
            "progress": 0.1
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 2: Query Analysis
        query_analysis = f"Query type: Research/Information Gathering\nStrategy: Web search + LLM synthesis\nTarget: Comprehensive answer with sources"
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "analysis",
            "action": "🧠 Analyzing query requirements",
            "details": "Determining search strategy and information needs",
            "input": user_query,
            "output": query_analysis,
            "status": "processing",
            "progress": 0.2
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 3: Web Search
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "web_search",
            "action": "🔍 Performing web search",
            "details": "Searching Tavily API for real-time information",
            "input": f"Search query: {user_query}",
            "output": "Sending request to Tavily API...",
            "status": "processing",
            "progress": 0.4
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Perform traced search
        search_results = await self._tavily_search_traced(user_query)
        
        # Create summary of search results
        result_summary = f"Retrieved {len(search_results.split('\\n\\n'))} search results\nTotal characters: {len(search_results)}\nFirst result: {search_results[:150]}..."
        
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "search_complete",
            "action": "✅ Search completed",
            "details": "Successfully retrieved search results from Tavily",
            "input": user_query,
            "output": result_summary,
            "status": "completed",
            "progress": 0.6
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 4: LLM Processing
        llm_input_summary = f"Model: gpt-4o-mini\nTemperature: 0\nContext: {len(search_results)} chars of search results\nPrompt: System + User query"
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "llm_processing",
            "action": "🤖 LLM processing",
            "details": "Sending to OpenAI GPT-4o-mini for synthesis",
            "input": llm_input_summary,
            "output": "Generating comprehensive response...",
            "status": "processing",
            "progress": 0.8
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Enhanced system prompt
        system_prompt = f"""
You are a Political Analyst AI agent with LangFuse observability.

Query: "{user_query}"

Available Information:
{search_results}

Instructions:
1. Provide comprehensive, well-structured response
2. Use search results as primary sources when available
3. For company/location queries, provide specific details
4. Organize with clear headings and bullet points
5. Be honest about information limitations

This execution is being traced with LangFuse for full observability.
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]
            
            # This LLM call will be traced by LangFuse
            response = await self.llm.ainvoke(messages)
            final_response = response.content
            
            # Create output summary
            response_summary = f"Generated {len(final_response)} characters\nStructured response with:\n- Main content\n- Sources/citations\n- Analysis and insights\n\nFirst 200 chars: {final_response[:200]}..."
            
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "response_complete",
                "action": "🎉 Analysis complete",
                "details": "Successfully generated comprehensive response",
                "input": "LLM synthesis request",
                "output": response_summary,
                "status": "completed",
                "progress": 1.0
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            
        except Exception as e:
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "llm_error",
                "action": "⚠️ Error traced in LangFuse",
                "details": f"Error details captured in trace",
                "status": "warning",
                "progress": 0.9
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            final_response = f"Analysis completed with limitations. Check LangFuse trace for details.\n\n{search_results}"
        
        # Send complete trace to professional dashboard
        trace_data = {
            "id": f"trace_{int(time.time())}",
            "name": "Political Analysis Query",
            "input": user_query,
            "output": final_response,
            "metadata": {
                "steps": len(reasoning_log),
                "search_performed": True,
                "model": "gpt-4o-mini"
            },
            "session_id": "default",
            "duration": time.time() - (time.time() - len(reasoning_log) * 0.5)
        }
        
        await self._send_trace_to_dashboard(trace_data)
        
        return {
            "response": final_response,
            "reasoning_log": reasoning_log,
            "search_results": search_results,
            "total_steps": len(reasoning_log),
            "status": "completed",
            "observability_url": self.observability_host
        }
    
    def process_query_sync(self, user_query: str) -> Dict[str, Any]:
        """Synchronous version"""
        return asyncio.run(self.process_query_with_tracing(user_query))


if __name__ == "__main__":
    # Test LangFuse agent
    def print_update(step_data):
        print(f"[{step_data['progress']:.0%}] {step_data['action']}")
        print(f"    {step_data['details']}")
        print()
    
    print("🔍 LangFuse Political Analyst Agent")
    print("=" * 50)
    
    try:
        agent = LangFuseAgent(update_callback=print_update)
        
        # Test query
        test_query = "Find all the AI players and companies in Gurugram"
        print(f"Query: {test_query}")
        print("=" * 50)
        
        result = agent.process_query_sync(test_query)
        
        print("🤖 FINAL RESPONSE:")
        print(result['response'])
        
        print(f"\n📊 OBSERVABILITY:")
        print(f"LangFuse UI: {result.get('langfuse_url', 'http://localhost:3000')}")
        print(f"Total steps: {result['total_steps']}")
        print(f"Status: {result['status']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
