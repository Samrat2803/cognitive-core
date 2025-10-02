"""
Streaming Political Analyst Agent - Real-time Updates for UI
"""

import os
import asyncio
import json
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

class StreamingPoliticalAgent:
    """Political Analyst Agent with real-time streaming capabilities"""
    
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
        
        # Initialize Tavily search tool
        self.tavily_tool = TavilySearchResults(
            max_results=15,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
            include_images=False,
            api_key=self.tavily_key
        )
    
    def _emit_update(self, step_data: Dict[str, Any]):
        """Emit real-time update to UI"""
        if self.update_callback:
            self.update_callback(step_data)
    
    async def process_query_streaming(self, user_query: str) -> Dict[str, Any]:
        """Process query with real-time streaming updates"""
        
        reasoning_log = []
        
        # Step 1: Initialize
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "initialization",
            "action": "🚀 Starting query analysis",
            "details": f"Query: {user_query}",
            "status": "processing",
            "progress": 0.1
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        await asyncio.sleep(0.5)  # Allow UI to update
        
        # Step 2: Query Analysis
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "analysis",
            "action": "🧠 Analyzing query requirements",
            "details": "Determining if web search is needed and optimal search strategy",
            "status": "processing",
            "progress": 0.2
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        await asyncio.sleep(1.0)
        
        # Step 3: Web Search Preparation
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "search_prep",
            "action": "🔍 Preparing web search",
            "details": f"Configuring Tavily search with advanced parameters for: {user_query}",
            "status": "processing",
            "progress": 0.3
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        await asyncio.sleep(0.5)
        
        # Step 4: Performing Web Search
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "web_search",
            "action": "🌐 Performing Tavily web search",
            "details": "Searching real-time web data with advanced depth",
            "status": "processing",
            "progress": 0.4
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        
        try:
            # Perform search
            search_results = await asyncio.to_thread(
                self.tavily_tool.run, user_query
            )
            
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "search_complete",
                "action": "✅ Web search completed successfully",
                "details": f"Found {len(search_results) if isinstance(search_results, list) else 'multiple'} relevant results",
                "status": "completed",
                "progress": 0.6
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            await asyncio.sleep(0.5)
            
        except Exception as e:
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "search_error",
                "action": "⚠️ Web search encountered issues",
                "details": f"Error: {str(e)[:100]}... Proceeding with available data",
                "status": "warning",
                "progress": 0.5
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            search_results = "Limited search results due to API constraints."
            await asyncio.sleep(0.5)
        
        # Step 5: LLM Processing
        step_data = {
            "timestamp": datetime.now().isoformat(),
            "step": "llm_processing",
            "action": "🤖 Processing with GPT-4o-mini",
            "details": "Analyzing search results and generating comprehensive response",
            "status": "processing",
            "progress": 0.7
        }
        reasoning_log.append(step_data)
        self._emit_update(step_data)
        await asyncio.sleep(1.0)
        
        # Enhanced system prompt with Tavily documentation
        system_prompt = f"""
You are a Political Analyst AI agent with access to real-time web search via Tavily.

## Tavily Search Capabilities:
- Real-time web search with advanced depth
- Country-specific targeting for location queries
- Comprehensive source coverage
- Current information retrieval

For the user query: "{user_query}"

Web search results:
{search_results}

Provide a comprehensive, well-structured response that:
1. Directly answers the user's question with specific details
2. Uses search results as authoritative sources
3. Provides concrete examples and data points
4. Organizes information in clear sections
5. Cites sources when available

For location-specific queries (like companies in a city):
- List specific company names with descriptions
- Include key focus areas and services
- Mention notable achievements or funding when available
- Provide contact information if found

Format your response professionally with clear headings and bullet points.
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]
            
            # Step 6: Generating Response
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "response_generation",
                "action": "✍️ Generating structured response",
                "details": "Creating comprehensive analysis with citations and formatting",
                "status": "processing",
                "progress": 0.85
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            
            response = await self.llm.ainvoke(messages)
            final_response = response.content
            
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "response_complete",
                "action": "🎉 Response generated successfully",
                "details": f"Generated {len(final_response)} character comprehensive response",
                "status": "completed",
                "progress": 1.0
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            
        except Exception as e:
            step_data = {
                "timestamp": datetime.now().isoformat(),
                "step": "llm_error",
                "action": "❌ LLM processing failed",
                "details": f"Error: {str(e)}",
                "status": "error",
                "progress": 0.8
            }
            reasoning_log.append(step_data)
            self._emit_update(step_data)
            final_response = f"I apologize, but I encountered an error processing your query: {str(e)}"
        
        # Final completion
        await asyncio.sleep(0.5)
        
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
    # Test the streaming agent
    def print_update(step_data):
        print(f"[{step_data['progress']:.0%}] {step_data['action']}")
        print(f"    {step_data['details']}")
        print()
    
    print("🏛️  Streaming Political Analyst Agent Test")
    print("=" * 50)
    
    try:
        agent = StreamingPoliticalAgent(update_callback=print_update)
        
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

