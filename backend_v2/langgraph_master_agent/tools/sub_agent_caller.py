"""
Sub-Agent Caller Interface
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, Any
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


class SubAgentCaller:
    """Interface for calling specialized sub-agents"""
    
    def __init__(self):
        self.sub_agents = {}
    
    @observe(name="sentiment_analysis_sub_agent")
    async def call_sentiment_analyzer(
        self,
        query: str,
        countries: list = None,
        time_range_days: int = 7
    ) -> Dict[str, Any]:
        """
        Call Sentiment Analysis Sub-Agent
        
        ✅ IMPLEMENTED & TESTED (Oct 2, 2025)
        
        This sub-agent performs:
        - Multi-country sentiment analysis
        - Bias detection (7 types)
        - Source credibility assessment
        - Artifact generation (charts, reports)
        
        Args:
            query: Political topic to analyze
            countries: List of countries to analyze (default: ["US", "UK", "France"])
            time_range_days: Recency filter in days
        
        Returns:
            Comprehensive sentiment analysis with bias detection and artifacts
        """
        # Lazy import (only loads when this function is called)
        import sys
        agent_dir = os.path.join(os.path.dirname(__file__), '../sub_agents/sentiment_analyzer')
        sys.path.insert(0, agent_dir)
        
        try:
            # Import from the agent folder
            from graph import create_sentiment_analyzer_graph
            from state import SentimentAnalyzerState
            
            # Create graph
            graph = create_sentiment_analyzer_graph()
            
            # Initialize state with all required fields
            initial_state: SentimentAnalyzerState = {
                "query": query,
                "countries": countries or ["US", "UK", "France"],
                "time_range_days": time_range_days,
                "search_results": {},
                "sentiment_scores": {},
                "bias_analysis": {},
                "summary": "",
                "key_findings": [],
                "confidence": 0.0,
                "artifacts": [],
                "execution_log": [],
                "error_log": []
            }
            
            # Run agent
            result = await graph.ainvoke(initial_state)
            
            # Return in expected format
            return {
                "success": True,
                "sub_agent": "sentiment_analyzer",
                "status": "COMPLETED",
                "data": {
                    "query": result.get("query"),
                    "countries": result.get("countries"),
                    "sentiment_scores": result.get("sentiment_scores", {}),
                    "bias_analysis": result.get("bias_analysis", {}),
                    "summary": result.get("summary", ""),
                    "key_findings": result.get("key_findings", []),
                    "confidence": result.get("confidence", 0.0),
                    "artifacts": result.get("artifacts", []),
                    "execution_log": result.get("execution_log", [])
                }
            }
            
        except Exception as e:
            # Graceful error handling
            return {
                "success": False,
                "sub_agent": "sentiment_analyzer",
                "status": "ERROR",
                "error": str(e),
                "query": query,
                "countries": countries
            }
    
    @observe(name="fact_checker_sub_agent")
    async def call_fact_checker(self, claim: str) -> Dict[str, Any]:
        """
        Call Fact Checker Sub-Agent (FUTURE)
        
        Args:
            claim: Claim to verify
        
        Returns:
            Fact check results with sources
        """
        return {
            "success": False,
            "sub_agent": "fact_checker",
            "status": "NOT_IMPLEMENTED",
            "message": "Fact checker sub-agent is a future feature"
        }
    
    @observe(name="source_credibility_sub_agent")
    async def call_source_credibility(self, sources: list) -> Dict[str, Any]:
        """
        Call Source Credibility Sub-Agent (FUTURE)
        
        Args:
            sources: List of source URLs or domains
        
        Returns:
            Credibility assessment for each source
        """
        return {
            "success": False,
            "sub_agent": "source_credibility",
            "status": "NOT_IMPLEMENTED",
            "message": "Source credibility sub-agent is a future feature"
        }

