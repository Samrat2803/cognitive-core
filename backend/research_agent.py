"""
Web Research Agent using LangGraph and Tavily
A sophisticated agent that can search the web, analyze results, and synthesize comprehensive answers.
"""

import asyncio
import os
from typing import TypedDict, List, Dict, Any, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient
from langgraph.graph import StateGraph, END
import operator

# Load environment variables
load_dotenv()

class ResearchState(TypedDict):
    """State for the research agent workflow"""
    query: str
    search_terms: List[str]
    search_results: Annotated[List[Dict[str, Any]], operator.add]
    analysis: str
    final_answer: str
    sources: Annotated[List[str], operator.add]
    error: str

class WebResearchAgent:
    """A sophisticated web research agent using LangGraph and Tavily"""
    
    def __init__(self, llm_provider: str = "openai", model: str = "gpt-4o-mini"):
        """
        Initialize the research agent
        
        Args:
            llm_provider: "openai" or "anthropic"
            model: Model name to use
        """
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        # Initialize LLM based on provider
        if llm_provider == "openai":
            self.llm = ChatOpenAI(
                model=model,
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0
            )
        elif llm_provider == "anthropic":
            self.llm = ChatAnthropic(
                model=model,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0
            )
        else:
            raise ValueError("llm_provider must be 'openai' or 'anthropic'")
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        builder = StateGraph(ResearchState)
        
        # Add nodes (search_web is now async)
        builder.add_node("analyze_query", self._analyze_query)
        builder.add_node("search_web", self._search_web)
        builder.add_node("analyze_results", self._analyze_results)
        builder.add_node("synthesize_answer", self._synthesize_answer)
        
        # Add edges
        builder.add_edge("analyze_query", "search_web")
        builder.add_edge("search_web", "analyze_results")
        builder.add_edge("analyze_results", "synthesize_answer")
        builder.add_edge("synthesize_answer", END)
        
        # Set entry point
        builder.set_entry_point("analyze_query")
        
        return builder.compile()
    
    def _analyze_query(self, state: ResearchState) -> Dict[str, Any]:
        """FAST query analysis - no LLM, instant processing"""
        try:
            query = state["query"]
            print(f"⚡ Fast analyzing: {query}")
            
            # Rule-based fast extraction
            search_terms = []
            query_lower = query.lower()
            
            if "hamas" in query_lower and "sentiment" in query_lower:
                search_terms = ["Hamas sentiment analysis", "Hamas public opinion"]
            elif "hamas" in query_lower:
                search_terms = ["Hamas news", "Hamas recent developments"]
            else:
                # Generic - just use the query
                search_terms = [query]
            
            print(f"✅ Instant terms: {search_terms}")
            return {
                "search_terms": search_terms,
                "error": ""
            }
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {
                "search_terms": [state["query"]],
                "error": f"Error analyzing query: {str(e)}"
            }
    
    def _search_web(self, state: ResearchState) -> Dict[str, Any]:
        """Perform web search using Tavily - fast and simple"""
        try:
            search_terms = state["search_terms"]
            all_results = []
            all_sources = []
            
            for term in search_terms:
                # Fast Tavily search
                search_response = self.tavily_client.search(
                    query=term,
                    search_depth="basic",  # Use basic for speed
                    max_results=3,  # Fewer results for speed
                    include_answer=True
                )
                
                # Process results quickly
                for result in search_response.get("results", []):
                    processed_result = {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0),
                        "search_term": term
                    }
                    all_results.append(processed_result)
                    all_sources.append(result.get("url", ""))
            
            return {
                "search_results": all_results,
                "sources": all_sources,
                "error": ""
            }
            
        except Exception as e:
            return {
                "search_results": [],
                "sources": [],
                "error": f"Error searching web: {str(e)}"
            }
    
    def _analyze_results(self, state: ResearchState) -> Dict[str, Any]:
        """Analyze and filter search results"""
        try:
            search_results = state["search_results"]
            query = state["query"]
            
            if not search_results:
                return {
                    "analysis": "No search results found to analyze.",
                    "error": ""
                }
            
            # Create context from search results
            context = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content'][:500]}..."
                for result in search_results[:10]  # Limit to top 10 results
            ])
            
            analysis_prompt = f"""
            Analyze the following search results for the query: "{query}"
            
            Search Results:
            {context}
            
            Provide a structured analysis that includes:
            1. Key findings and insights
            2. Most relevant and credible sources
            3. Any conflicting information
            4. Gaps in information that might need additional research
            
            Be objective and cite specific sources when making claims.
            """
            
            messages = [
                SystemMessage(content="You are a research analyst that provides objective analysis of search results."),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                "analysis": response.content,
                "error": ""
            }
            
        except Exception as e:
            return {
                "analysis": f"Error analyzing results: {str(e)}",
                "error": str(e)
            }
    
    def _synthesize_answer(self, state: ResearchState) -> Dict[str, Any]:
        """Synthesize a comprehensive final answer"""
        try:
            query = state["query"]
            analysis = state["analysis"]
            search_results = state["search_results"]
            sources = state["sources"]
            
            # Create a comprehensive prompt for synthesis
            synthesis_prompt = f"""
            Based on the research query and analysis below, provide a comprehensive, well-structured answer.
            
            Research Query: "{query}"
            
            Analysis:
            {analysis}
            
            Please provide:
            1. A clear, direct answer to the query
            2. Supporting evidence and details
            3. Key insights and implications
            4. Any limitations or areas for further research
            
            Format your response in a clear, professional manner with proper structure.
            """
            
            messages = [
                SystemMessage(content="You are a research expert that synthesizes information into comprehensive, well-structured answers."),
                HumanMessage(content=synthesis_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Create a formatted final answer with sources
            unique_sources = list(set(sources))[:10]  # Limit to 10 unique sources
            sources_text = "\n".join([f"- {source}" for source in unique_sources])
            
            final_answer = f"""
{response.content}

---
**Sources:**
{sources_text}
"""
            
            return {
                "final_answer": final_answer,
                "error": ""
            }
            
        except Exception as e:
            return {
                "final_answer": f"Error synthesizing answer: {str(e)}",
                "error": str(e)
            }
    
    def research(self, query: str) -> Dict[str, Any]:
        """Perform comprehensive research on a given query"""
        initial_state = {
            "query": query,
            "search_terms": [],
            "search_results": [],
            "analysis": "",
            "final_answer": "",
            "sources": [],
            "error": ""
        }
        
        try:
            result = self.graph.invoke(initial_state)
            return result
        except Exception as e:
            return {
                **initial_state,
                "error": f"Research failed: {str(e)}"
            }
    
    def research_sync(self, query: str) -> Dict[str, Any]:
        """Synchronous version of research"""
        initial_state = {
            "query": query,
            "search_terms": [],
            "search_results": [],
            "analysis": "",
            "final_answer": "",
            "sources": [],
            "error": ""
        }
        
        try:
            result = self.graph.invoke(initial_state)
            return result
        except Exception as e:
            return {
                **initial_state,
                "error": f"Research failed: {str(e)}"
            }

if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize the agent
        agent = WebResearchAgent(llm_provider="openai", model="gpt-4o-mini")
        
        # Test queries
        test_queries = [
            "What are the latest developments in quantum computing?",
            "How is AI being used in healthcare in 2024?",
            "What are the current trends in renewable energy?"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Research Query: {query}")
            print(f"{'='*60}")
            
            result = await agent.research(query)
            
            if result.get("error"):
                print(f"Error: {result['error']}")
            else:
                print(f"Search Terms: {', '.join(result['search_terms'])}")
                print(f"Sources Found: {len(result['sources'])}")
                print(f"\nFinal Answer:\n{result['final_answer']}")
    
    # Run the example
    asyncio.run(main())
