"""
Robust Streaming Political Analyst Agent with Better Error Handling
"""

import os
import asyncio
import json
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dotenv import load_dotenv
import time

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import httpx

# Load environment variables
load_dotenv()

class RobustStreamingAgent:
    """Political Analyst Agent with robust error handling and real-time streaming"""
    
    def __init__(self, update_callback: Optional[Callable] = None):
        """Initialize the agent with optional update callback for real-time UI"""
        
        self.update_callback = update_callback
        
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
            # Small delay to allow UI to update
            time.sleep(0.1)
    
    async def _tavily_search_robust(self, query: str) -> str:
        """Robust Tavily search with better error handling"""
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": "basic",  # Use basic to avoid rate limits
                    "include_images": False,
                    "include_answer": True,
                    "max_results": 8,  # Reduced to avoid rate limits
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
    
    async def process_query_streaming(self, user_query: str) -> Dict[str, Any]:
        """Process query with real-time streaming updates and robust error handling"""
        
        reasoning_log = []
        
        # Step 1: Initialize
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "initialization",
            "action": "🚀 Starting analysis",
            "details": f"Query: {user_query}",
            "status": "processing",
            "progress": 0.1
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 2: Query Analysis
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "analysis",
            "action": "🧠 Analyzing query type",
            "details": "Determining search strategy and information requirements",
            "status": "processing",
            "progress": 0.2
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 3: Web Search
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "web_search",
            "action": "🔍 Searching web sources",
            "details": "Gathering real-time information with robust error handling",
            "status": "processing",
            "progress": 0.4
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Perform search with error handling
        search_results = await self._tavily_search_robust(user_query)
        
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "search_complete",
            "action": "✅ Information gathering complete",
            "details": f"Retrieved {len(search_results)} characters of relevant data",
            "status": "completed",
            "progress": 0.6
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Step 4: LLM Processing
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "llm_processing",
            "action": "🤖 Processing with AI",
            "details": "Analyzing information and generating comprehensive response",
            "status": "processing",
            "progress": 0.8
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        # Enhanced system prompt
        system_prompt = f"""
You are a Political Analyst AI agent with access to web search results.

Query: "{user_query}"

Available Information:
{search_results}

Instructions:
1. Provide a comprehensive, well-structured response
2. Use the search results as primary sources when available
3. If search results are limited, use your knowledge but mention this
4. For company/location queries, provide specific details like:
   - Company names and descriptions
   - Key focus areas and services
   - Notable achievements or funding
   - Contact information if available
5. Organize information with clear headings and bullet points
6. Be honest about information limitations

Format your response professionally with clear structure.
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]
            
            response = await self.llm.ainvoke(messages)
            final_response = response.content
            
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "response_complete",
                "action": "🎉 Analysis complete",
                "details": f"Generated comprehensive {len(final_response)} character response",
                "status": "completed",
                "progress": 1.0
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            
        except Exception as e:
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "llm_error",
                "action": "⚠️ Processing completed with limitations",
                "details": f"Error: {str(e)[:100]}",
                "status": "warning",
                "progress": 0.9
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            final_response = f"I encountered some technical limitations but can provide this analysis based on available information:\n\n{search_results}"
        
        return {
            "response": final_response,
            "reasoning_log": reasoning_log,
            "search_results": search_results,
            "total_steps": len(reasoning_log),
            "status": "completed"
        }
    
    def process_query_sync(self, user_query: str) -> Dict[str, Any]:
        """Synchronous version for compatibility"""
        return asyncio.run(self.process_query_streaming(user_query))


if __name__ == "__main__":
    # Test the robust streaming agent
    def print_update(step_data):
        print(f"[{step_data['progress']:.0%}] {step_data['action']}")
        print(f"    {step_data['details']}")
        print()
    
    print("🏛️  Robust Streaming Political Analyst Agent Test")
    print("=" * 50)
    
    try:
        agent = RobustStreamingAgent(update_callback=print_update)
        
        # Test query
        test_query = "Find all the AI players and companies in Gurugram"
        print(f"Query: {test_query}")
        print("=" * 50)
        
        result = agent.process_query_sync(test_query)
        
        print("🤖 FINAL RESPONSE:")
        print(result['response'])
        
        print(f"\n📊 SUMMARY:")
        print(f"Total reasoning steps: {result['total_steps']}")
        print(f"Status: {result['status']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

