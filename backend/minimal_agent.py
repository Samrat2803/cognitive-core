"""
Minimal Web Search Agent - Fast and simple for testing
"""

import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

# Load environment variables
load_dotenv()

class MinimalWebAgent:
    """A minimal, fast web search agent for testing"""
    
    def __init__(self):
        """Initialize the minimal agent"""
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )
    
    async def search_and_answer(self, query: str) -> Dict[str, Any]:
        """Perform a quick search and return an answer"""
        try:
            print(f"🔍 Searching for: {query}")
            
            # Perform a quick search with limited results
            search_response = self.tavily_client.search(
                query=query,
                search_depth="basic",  # Use basic instead of advanced for speed
                max_results=3,  # Limit to 3 results for speed
                include_answer=True
            )
            
            print(f"📚 Found {len(search_response.get('results', []))} results")
            
            # Extract content from results
            results = search_response.get("results", [])
            if not results:
                return {
                    "success": False,
                    "error": "No search results found",
                    "query": query,
                    "search_terms": [query],
                    "sources_count": 0,
                    "final_answer": "No results found for your query.",
                    "sources": []
                }
            
            # Create a simple context from results
            context = "\n\n".join([
                f"Title: {result.get('title', '')}\nContent: {result.get('content', '')[:300]}..."
                for result in results[:3]
            ])
            
            # Generate a quick answer
            prompt = f"""
            Based on the following search results, provide a brief, accurate answer to: "{query}"
            
            Search Results:
            {context}
            
            Please provide a concise answer (2-3 sentences) based on the information above.
            """
            
            print("🤖 Generating answer...")
            response = self.llm.invoke(prompt)
            
            # Extract sources
            sources = [result.get('url', '') for result in results if result.get('url')]
            
            return {
                "success": True,
                "query": query,
                "search_terms": [query],
                "sources_count": len(sources),
                "final_answer": response.content,
                "sources": sources,
                "error": ""
            }
            
        except Exception as e:
            print(f"❌ Error in minimal agent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "search_terms": [query],
                "sources_count": 0,
                "final_answer": f"Error occurred: {str(e)}",
                "sources": []
            }

# Global instance
minimal_agent = None

def get_minimal_agent():
    """Get or create the minimal agent instance"""
    global minimal_agent
    if minimal_agent is None:
        minimal_agent = MinimalWebAgent()
    return minimal_agent

if __name__ == "__main__":
    # Test the minimal agent
    async def test():
        agent = MinimalWebAgent()
        result = await agent.search_and_answer("What is artificial intelligence?")
        print("Result:", result)
    
    asyncio.run(test())
