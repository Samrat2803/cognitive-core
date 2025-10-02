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
        import os
        
        # Get absolute path to sentiment analyzer directory
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        agent_dir = os.path.abspath(os.path.join(current_file_dir, '../sub_agents/sentiment_analyzer'))
        
        print(f"\n🔍 Attempting to load sentiment analyzer from: {agent_dir}")
        print(f"   Directory exists: {os.path.exists(agent_dir)}")
        
        if not os.path.exists(agent_dir):
            return {
                "success": False,
                "sub_agent": "sentiment_analyzer",
                "status": "ERROR",
                "error": f"Sentiment analyzer directory not found: {agent_dir}",
                "query": query,
                "countries": countries
            }
        
        try:
            # SIMPLE FIX: Ensure agent_dir is FIRST in sys.path and clean conflicting modules
            import importlib.util
            
            # Save original sys.path and modules
            original_sys_path = sys.path.copy()
            saved_modules = {}
            conflict_modules = ['state', 'nodes', 'config', 'graph']
            
            for mod_name in conflict_modules:
                if mod_name in sys.modules:
                    saved_modules[mod_name] = sys.modules[mod_name]
                    del sys.modules[mod_name]
            
            # Put agent_dir FIRST, remove other sub-agent paths
            clean_path = [agent_dir]
            for path in original_sys_path:
                if 'sub_agents' not in path:
                    clean_path.append(path)
            sys.path = clean_path
            
            print(f"   🧹 Cleaned sys.path (sentiment_analyzer ONLY)")
            print(f"   📦 Loading modules with normal imports...")
            
            # Now use normal imports - they'll find the sentiment_analyzer modules
            from graph import create_sentiment_analyzer_graph
            from state import SentimentAnalyzerState
            
            print(f"   ✅ Successfully loaded sentiment_analyzer modules")
            
            # Restore
            sys.path = original_sys_path
            for mod_name in conflict_modules:
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
            for mod_name, mod_obj in saved_modules.items():
                sys.modules[mod_name] = mod_obj
            
            print(f"   🔄 Restored sys.path and sys.modules")
            print()
            
            # Create graph
            graph = create_sentiment_analyzer_graph()
            
            # Initialize state with all required fields
            # Note: If countries is None, sentiment analyzer will extract from query or use defaults
            initial_state: SentimentAnalyzerState = {
                "query": query,
                "countries": countries or [],  # Empty list = let analyzer extract from query
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
            # Graceful error handling with detailed logging
            print(f"\n❌ Error in sentiment analyzer sub-agent:")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            
            import traceback
            print(f"\n   Full traceback:")
            traceback.print_exc()
            print()
            
            return {
                "success": False,
                "sub_agent": "sentiment_analyzer",
                "status": "ERROR",
                "error": f"{type(e).__name__}: {str(e)}",
                "query": query,
                "countries": countries
            }
    
    @observe(name="sitrep_generator_sub_agent")
    async def call_sitrep_generator(
        self,
        period: str = "daily",
        region_focus: str = None,
        topic_focus: str = None
    ) -> Dict[str, Any]:
        """
        Call SitRep Generator Sub-Agent
        
        ✅ IMPLEMENTED & TESTED (Oct 2, 2025)
        
        This sub-agent generates situation reports:
        - Daily/weekly political situation reports
        - Executive summaries for decision-makers
        - Priority-ranked events (URGENT, HIGH, NOTABLE)
        - Regional breakdowns
        - Trending topics analysis
        - Watch list for next 24-48 hours
        - Multi-format artifacts (HTML, PDF, TXT, JSON)
        
        Args:
            period: "daily", "weekly", or "custom"
            region_focus: Optional region filter (e.g., "Middle East", "Europe")
            topic_focus: Optional topic filter (e.g., "elections", "conflicts")
        
        Returns:
            Comprehensive situation report with artifacts
        """
        # Lazy import (only loads when this function is called)
        import sys
        import os
        
        # Get absolute path to sitrep_generator directory
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        agent_dir = os.path.abspath(os.path.join(current_file_dir, '../sub_agents/sitrep_generator'))
        
        print(f"\n📋 Attempting to load SitRep Generator from: {agent_dir}")
        print(f"   Directory exists: {os.path.exists(agent_dir)}")
        
        if not os.path.exists(agent_dir):
            return {
                "success": False,
                "sub_agent": "sitrep_generator",
                "status": "ERROR",
                "error": f"SitRep Generator directory not found: {agent_dir}",
                "period": period,
                "region_focus": region_focus
            }
        
        try:
            # SIMPLE FIX: Ensure agent_dir is FIRST in sys.path and clean conflicting modules
            import importlib.util
            
            # Save original sys.path and modules
            original_sys_path = sys.path.copy()
            saved_modules = {}
            conflict_modules = ['state', 'nodes', 'config', 'graph']
            
            for mod_name in conflict_modules:
                if mod_name in sys.modules:
                    saved_modules[mod_name] = sys.modules[mod_name]
                    del sys.modules[mod_name]
            
            # Put agent_dir FIRST, remove other sub-agent paths
            clean_path = [agent_dir]
            for path in original_sys_path:
                if 'sub_agents' not in path:
                    clean_path.append(path)
            sys.path = clean_path
            
            print(f"   🧹 Cleaned sys.path (sitrep_generator ONLY)")
            print(f"   📦 Loading modules with normal imports...")
            
            # Now use normal imports - they'll find the sitrep_generator modules
            from graph import create_sitrep_graph
            from state import SitRepState
            
            print(f"   ✅ Successfully loaded sitrep_generator modules")
            
            # Restore
            sys.path = original_sys_path
            for mod_name in conflict_modules:
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
            for mod_name, mod_obj in saved_modules.items():
                sys.modules[mod_name] = mod_obj
            
            print(f"   🔄 Restored sys.path and sys.modules")
            print()
            
            # Create graph
            graph = create_sitrep_graph()
            
            # Initialize state with all required fields
            initial_state: SitRepState = {
                "period": period,
                "region_focus": region_focus,
                "topic_focus": topic_focus,
                "start_date": None,
                "end_date": None,
                "raw_events": [],
                "event_count": 0,
                "urgent_events": [],
                "high_priority_events": [],
                "notable_events": [],
                "regional_breakdown": {},
                "topic_clusters": {},
                "executive_summary": "",
                "trending_topics": [],
                "watch_list": [],
                "date_range": "",
                "regions_covered": [],
                "source_count": 0,
                "artifacts": [],
                "execution_log": [],
                "error_log": []
            }
            
            # Run agent
            result = await graph.ainvoke(initial_state)
            
            # Return in expected format
            return {
                "success": True,
                "sub_agent": "sitrep_generator",
                "status": "COMPLETED",
                "data": {
                    "period": result.get("period"),
                    "date_range": result.get("date_range", ""),
                    "region_focus": result.get("region_focus"),
                    "executive_summary": result.get("executive_summary", ""),
                    "urgent_events": result.get("urgent_events", []),
                    "high_priority_events": result.get("high_priority_events", []),
                    "notable_events": result.get("notable_events", []),
                    "regional_breakdown": result.get("regional_breakdown", {}),
                    "trending_topics": result.get("trending_topics", []),
                    "watch_list": result.get("watch_list", []),
                    "event_count": result.get("event_count", 0),
                    "regions_covered": result.get("regions_covered", []),
                    "artifacts": result.get("artifacts", []),
                    "execution_log": result.get("execution_log", [])
                }
            }
            
        except Exception as e:
            # Graceful error handling with detailed logging
            print(f"\n❌ Error in SitRep Generator sub-agent:")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            
            import traceback
            print(f"\n   Full traceback:")
            traceback.print_exc()
            print()
            
            return {
                "success": False,
                "sub_agent": "sitrep_generator",
                "status": "ERROR",
                "error": f"{type(e).__name__}: {str(e)}",
                "period": period,
                "region_focus": region_focus
            }
    
    @observe(name="media_bias_detector_sub_agent")
    async def call_media_bias_detector(
        self,
        query: str,
        sources: list = None,
        time_range_days: int = 7
    ) -> Dict[str, Any]:
        """
        Call Media Bias Detector Sub-Agent
        
        ✅ IMPLEMENTED & TESTED (Oct 2, 2025)
        
        This sub-agent performs:
        - Multi-source media bias analysis
        - Political lean classification (-1.0 to +1.0)
        - Loaded language detection (8 categories)
        - Framing analysis (8 frame types)
        - Bias technique identification
        - Artifact generation (charts, heatmaps, reports)
        
        Args:
            query: Political topic/event to analyze across sources
            sources: List of news sources to compare (default: auto-select 6-8 sources)
            time_range_days: Recency filter in days
        
        Returns:
            Comprehensive media bias analysis with visualizations
        """
        # Lazy import (only loads when this function is called)
        import sys
        import os
        
        # Get absolute path to media_bias_detector directory
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        agent_dir = os.path.abspath(os.path.join(current_file_dir, '../sub_agents/media_bias_detector'))
        
        print(f"\n📰 Attempting to load Media Bias Detector from: {agent_dir}")
        print(f"   Directory exists: {os.path.exists(agent_dir)}")
        
        if not os.path.exists(agent_dir):
            return {
                "success": False,
                "sub_agent": "media_bias_detector",
                "status": "ERROR",
                "error": f"Media Bias Detector directory not found: {agent_dir}",
                "query": query,
                "sources": sources
            }
        
        try:
            # SIMPLE FIX: Ensure agent_dir is FIRST in sys.path and clean conflicting modules
            import importlib.util
            
            # Save original sys.path and modules
            original_sys_path = sys.path.copy()
            saved_modules = {}
            conflict_modules = ['state', 'nodes', 'config', 'graph']
            
            for mod_name in conflict_modules:
                if mod_name in sys.modules:
                    saved_modules[mod_name] = sys.modules[mod_name]
                    del sys.modules[mod_name]
            
            # Put agent_dir FIRST, remove other sub-agent paths
            clean_path = [agent_dir]
            for path in original_sys_path:
                if 'sub_agents' not in path:
                    clean_path.append(path)
            sys.path = clean_path
            
            print(f"   🧹 Cleaned sys.path (media_bias_detector ONLY)")
            print(f"   📦 Loading modules with normal imports...")
            
            # Now use normal imports - they'll find the media_bias_detector modules
            from graph import create_media_bias_detector_graph
            from state import MediaBiasDetectorState
            
            print(f"   ✅ Successfully loaded media_bias_detector modules")
            
            # Restore
            sys.path = original_sys_path
            for mod_name in conflict_modules:
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
            for mod_name, mod_obj in saved_modules.items():
                sys.modules[mod_name] = mod_obj
            
            print(f"   🔄 Restored sys.path and sys.modules")
            print()
            
            # Create graph
            graph = create_media_bias_detector_graph()
            
            # Initialize state with all required fields
            initial_state: MediaBiasDetectorState = {
                "query": query,
                "sources": sources,
                "time_range_days": time_range_days,
                "articles_by_source": {},
                "total_articles_found": 0,
                "bias_classification": {},
                "loaded_language": {},
                "framing_analysis": {},
                "consensus_points": [],
                "divergence_points": [],
                "omission_analysis": {},
                "overall_bias_range": {},
                "summary": "",
                "key_findings": [],
                "confidence": 0.0,
                "recommendations": [],
                "artifacts": [],
                "execution_log": [],
                "error_log": []
            }
            
            # Run agent
            result = await graph.ainvoke(initial_state)
            
            # Return in expected format
            return {
                "success": True,
                "sub_agent": "media_bias_detector",
                "status": "COMPLETED",
                "data": {
                    "query": result.get("query"),
                    "sources_analyzed": list(result.get("bias_classification", {}).keys()),
                    "total_articles": result.get("total_articles_found", 0),
                    "bias_classification": result.get("bias_classification", {}),
                    "loaded_language": result.get("loaded_language", {}),
                    "framing_analysis": result.get("framing_analysis", {}),
                    "overall_bias_range": result.get("overall_bias_range", {}),
                    "summary": result.get("summary", ""),
                    "key_findings": result.get("key_findings", []),
                    "recommendations": result.get("recommendations", []),
                    "confidence": result.get("confidence", 0.0),
                    "artifacts": result.get("artifacts", []),
                    "execution_log": result.get("execution_log", [])
                }
            }
            
        except Exception as e:
            # Graceful error handling with detailed logging
            print(f"\n❌ Error in media bias detector sub-agent:")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            
            import traceback
            print(f"\n   Full traceback:")
            traceback.print_exc()
            print()
            
            return {
                "success": False,
                "sub_agent": "media_bias_detector",
                "status": "ERROR",
                "error": f"{type(e).__name__}: {str(e)}",
                "query": query,
                "sources": sources
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

