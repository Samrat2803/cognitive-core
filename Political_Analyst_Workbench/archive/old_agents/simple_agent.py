"""
Simple Political Analyst Agent - Working Version for Testing
"""

import os
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

class SimplePoliticalAgent:
    """Simple Political Analyst Agent for testing"""
    
    def __init__(self):
        """Initialize the agent"""
        
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
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process query with reasoning tracking"""
        
        reasoning_log = []
        
        # Step 1: Analyze if we need web search
        reasoning_log.append({
            "timestamp": datetime.now().isoformat(),
            "step": "analysis",
            "action": "Analyzing if web search is needed",
            "details": f"Query: {user_query}"
        })
        
        # Step 2: Perform web search
        reasoning_log.append({
            "timestamp": datetime.now().isoformat(),
            "step": "web_search",
            "action": "Performing Tavily web search",
            "details": f"Searching for: {user_query}"
        })
        
        try:
            # Perform search
            search_results = await asyncio.to_thread(
                self.tavily_tool.run, user_query
            )
            
            reasoning_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "search_complete",
                "action": "Web search completed",
                "details": f"Found {len(search_results) if isinstance(search_results, list) else 'N/A'} results"
            })
            
        except Exception as e:
            reasoning_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "search_error",
                "action": "Web search failed",
                "details": f"Error: {str(e)}"
            })
            search_results = "No search results available due to error."
        
        # Step 3: Generate response with LLM
        reasoning_log.append({
            "timestamp": datetime.now().isoformat(),
            "step": "llm_processing",
            "action": "Generating response with LLM",
            "details": "Processing search results and user query"
        })
        
        system_prompt = f"""
You are a Political Analyst AI agent. You have access to real-time web search results.

For the user query: "{user_query}"

Web search results:
{search_results}

Provide a comprehensive, well-structured response that:
1. Directly answers the user's question
2. Uses the search results as sources
3. Provides specific details and examples
4. Cites sources when possible
5. Organizes information clearly

If the query is about companies or organizations in a specific location, provide:
- Company names and brief descriptions
- Key focus areas or services
- Notable achievements or funding
- Contact information if available
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]
            
            response = await self.llm.ainvoke(messages)
            final_response = response.content
            
            reasoning_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "response_generated",
                "action": "LLM response generated successfully",
                "details": f"Response length: {len(final_response)} characters"
            })
            
        except Exception as e:
            reasoning_log.append({
                "timestamp": datetime.now().isoformat(),
                "step": "llm_error",
                "action": "LLM processing failed",
                "details": f"Error: {str(e)}"
            })
            final_response = f"I apologize, but I encountered an error processing your query: {str(e)}"
        
        return {
            "response": final_response,
            "reasoning_log": reasoning_log,
            "search_results": search_results,
            "total_steps": len(reasoning_log)
        }
    
    def process_query_sync(self, user_query: str) -> Dict[str, Any]:
        """Synchronous version"""
        return asyncio.run(self.process_query(user_query))


if __name__ == "__main__":
    # Test the agent
    print("🏛️  Simple Political Analyst Agent Test")
    print("=" * 50)
    
    try:
        agent = SimplePoliticalAgent()
        
        # Test query
        test_query = "Find all the AI players and companies in Gurugram"
        print(f"Query: {test_query}")
        print("=" * 50)
        
        result = agent.process_query_sync(test_query)
        
        print("📋 REASONING LOG:")
        for i, step in enumerate(result['reasoning_log'], 1):
            print(f"{i}. {step['step']}: {step['action']}")
            print(f"   Details: {step['details']}")
            print(f"   Time: {step['timestamp']}")
            print()
        
        print("🤖 FINAL RESPONSE:")
        print(result['response'])
        
        print(f"\n📊 SUMMARY:")
        print(f"Total reasoning steps: {result['total_steps']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

