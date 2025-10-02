"""LangGraph-based geopolitical sentiment analyzer agent"""

import asyncio
import json
import os
from typing import Dict, Any, List, TypedDict, Annotated
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# Import our tools
from geo_sentiment_poc import main as run_sentiment_analysis
from agent_utils import analyze_bias_and_gaps, generate_search_params, should_stop_iteration


# State definition
class AgentState(TypedDict):
    iteration: int
    query_history: List[str]
    results_history: List[Dict[str, Any]]
    current_analysis: Dict[str, Any]
    next_params: Dict[str, Any]
    should_stop: bool
    final_summary: str


@dataclass
class SearchParams:
    query_term: str
    countries: List[str]
    include_domains: List[str] = None
    exclude_domains: List[str] = None
    days: int = None


class GeopoliticalSentimentAgent:
    """Agent that iteratively improves sentiment analysis by detecting and correcting biases"""
    
    def __init__(self):
        load_dotenv()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment/.env")
            
        # Build the graph
        self.graph = self._build_graph()
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API directly with temperature=0"""
        async with httpx.AsyncClient(timeout=60) as client:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "gpt-4o-mini",
                "temperature": 0,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            try:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=body
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                return f"Error generating response: {e}"
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("search", self._search_node) 
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("check_stop", self._check_stop_node)
        
        # Add edges
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "search")
        workflow.add_edge("search", "analyze")
        workflow.add_edge("analyze", "check_stop")
        
        # Conditional edge from check_stop
        workflow.add_conditional_edges(
            "check_stop",
            self._should_continue,
            {
                "continue": "plan",
                "stop": END
            }
        )
        
        return workflow.compile()
    
    async def _plan_node(self, state: AgentState) -> AgentState:
        """Plan the next search based on previous results"""
        
        print(f"\n🧠 Planning iteration {state['iteration'] + 1}...")
        
        if state["iteration"] == 0:
            # First iteration - use default params
            next_params = {
                "query_term": "Hamas",
                "countries": ["United States", "Iran", "Israel"],
                "include_domains": None,
                "exclude_domains": None,
                "days": None
            }
            print("📋 First iteration - using default search parameters")
        else:
            # Analyze previous results and generate new params
            last_analysis = state["current_analysis"]
            next_params = generate_search_params(last_analysis, state["iteration"])
            
            print(f"📋 Generated new search parameters based on bias analysis:")
            print(f"   Query: {next_params['query_term']}")
            if next_params.get("include_domains"):
                print(f"   Include domains: {next_params['include_domains'][:3]}...")
            if next_params.get("days"):
                print(f"   Time filter: {next_params['days']} days")
        
        state["next_params"] = next_params
        return state
    
    async def _search_node(self, state: AgentState) -> AgentState:
        """Execute the sentiment analysis search"""
        
        print(f"\n🔍 Executing search with parameters...")
        
        params = state["next_params"]
        
        try:
            # Run the sentiment analysis
            results = await run_sentiment_analysis(
                query_term=params["query_term"],
                countries=params["countries"],
                include_domains=params.get("include_domains"),
                exclude_domains=params.get("exclude_domains"),
                days=params.get("days")
            )
            
            # Store results
            state["results_history"].append(results)
            state["query_history"].append(params["query_term"])
            
            print(f"✅ Search completed - found {len(results.get('articles', []))} articles")
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            # Create empty results to continue
            results = {"query": params["query_term"], "countries": [], "articles": []}
            state["results_history"].append(results)
            state["query_history"].append(params["query_term"])
        
        return state
    
    async def _analyze_node(self, state: AgentState) -> AgentState:
        """Analyze results for biases and gaps"""
        
        print(f"\n📊 Analyzing results for biases and gaps...")
        
        if not state["results_history"]:
            state["current_analysis"] = {"has_gaps": True, "reason": "No results to analyze"}
            return state
        
        # Analyze the latest results
        latest_results = state["results_history"][-1]
        analysis = analyze_bias_and_gaps(latest_results)
        
        state["current_analysis"] = analysis
        
        # Print analysis summary
        if analysis.get("has_gaps"):
            print(f"🔍 Found {len(analysis.get('gaps', []))} potential biases:")
            for gap in analysis.get("gaps", []):
                print(f"   - {gap}")
                
            print(f"💡 Generated {len(analysis.get('suggestions', []))} suggestions for improvement")
        else:
            print("✅ No significant biases detected")
            
        # Print key metrics
        metrics = analysis.get("metrics", {})
        print(f"📈 Key metrics:")
        print(f"   - English ratio: {metrics.get('english_ratio', 0):.1%}")
        print(f"   - Avg sentiment: {metrics.get('avg_sentiment', 0):.2f}")
        print(f"   - Source types: {len(metrics.get('source_distribution', {}))}")
        print(f"   - Recent articles: {metrics.get('recent_ratio', 0):.1%}")
        
        return state
    
    async def _check_stop_node(self, state: AgentState) -> AgentState:
        """Check if we should stop iterating"""
        
        analysis = state["current_analysis"]
        iteration = state["iteration"]
        
        should_stop = should_stop_iteration(analysis, iteration, max_iterations=3)
        state["should_stop"] = should_stop
        
        if should_stop:
            # Generate final summary using LLM
            summary_prompt = self._create_summary_prompt(state)
            
            try:
                summary_response = await self._call_openai(summary_prompt)
                state["final_summary"] = summary_response
                print(f"\n🏁 Stopping after {iteration + 1} iterations")
                print(f"📋 Reason: {self._get_stop_reason(analysis, iteration)}")
            except Exception as e:
                state["final_summary"] = f"Analysis completed after {iteration + 1} iterations. Error generating summary: {e}"
                print(f"\n🏁 Stopping after {iteration + 1} iterations (summary generation failed)")
        else:
            print(f"\n🔄 Continuing to iteration {iteration + 2}")
        
        # Increment iteration for next round
        state["iteration"] = iteration + 1
        
        return state
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue or stop"""
        return "stop" if state["should_stop"] else "continue"
    
    def _create_summary_prompt(self, state: AgentState) -> str:
        """Create a prompt for LLM to summarize the analysis"""
        
        queries = state["query_history"]
        total_articles = sum(len(r.get("articles", [])) for r in state["results_history"])
        
        return f"""
        Summarize this geopolitical sentiment analysis session:
        
        Queries executed: {', '.join(queries)}
        Total iterations: {state['iteration'] + 1}
        Total articles analyzed: {total_articles}
        
        Final analysis: {json.dumps(state['current_analysis'], indent=2)}
        
        Provide a concise summary of:
        1. What biases were detected and addressed
        2. Key sentiment findings across countries
        3. Quality of the final dataset
        4. Recommendations for further analysis
        
        Keep it under 200 words and focus on actionable insights.
        """
    
    def _get_stop_reason(self, analysis: Dict[str, Any], iteration: int) -> str:
        """Get human-readable stop reason"""
        
        if iteration >= 3:
            return "Maximum iterations reached"
        elif not analysis.get("has_gaps"):
            return "No significant biases detected"
        else:
            metrics = analysis.get("metrics", {})
            if (metrics.get("english_ratio", 1.0) < 0.7 and 
                metrics.get("recent_ratio", 0.0) > 0.4 and
                len(metrics.get("source_distribution", {})) >= 3):
                return "Good coverage achieved (language diversity, recency, source variety)"
            else:
                return "Stopping criteria met"
    
    async def run_analysis(self, initial_query: str = "Hamas") -> Dict[str, Any]:
        """Run the complete geopolitical sentiment analysis"""
        
        print("🚀 Starting Geopolitical Sentiment Analysis Agent")
        print(f"🎯 Initial query: {initial_query}")
        print("=" * 60)
        
        # Initialize state
        initial_state = AgentState(
            iteration=0,
            query_history=[],
            results_history=[],
            current_analysis={},
            next_params={},
            should_stop=False,
            final_summary=""
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        print("\n" + "=" * 60)
        print("🎉 Analysis Complete!")
        print("\n📋 Final Summary:")
        print(final_state["final_summary"])
        
        return {
            "iterations": final_state["iteration"],
            "queries_executed": final_state["query_history"],
            "total_articles": sum(len(r.get("articles", [])) for r in final_state["results_history"]),
            "final_analysis": final_state["current_analysis"],
            "summary": final_state["final_summary"],
            "all_results": final_state["results_history"]
        }


# Main execution
async def main():
    """Run the geopolitical sentiment analysis agent"""
    
    agent = GeopoliticalSentimentAgent()
    results = await agent.run_analysis("Hamas")
    
    # Save final results
    os.makedirs("POCs", exist_ok=True)
    with open("POCs/agent_analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to POCs/agent_analysis_results.json")
    return results


if __name__ == "__main__":
    asyncio.run(main())
