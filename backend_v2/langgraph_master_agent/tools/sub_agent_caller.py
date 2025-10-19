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
        self._cognitive_crawler_graph = None  # Cache for performance
        self._cognitive_crawler_state_class = None  # Cache for performance
    
    def clear_cognitive_crawler_cache(self):
        """
        Clear the cached Cognitive Crawler graph and modules.
        
        Use this during development when you modify sub-agent code
        and want changes to take effect without restarting the server.
        
        In production, the cache is safe to keep indefinitely.
        """
        self._cognitive_crawler_graph = None
        self._cognitive_crawler_state_class = None
        print("🗑️  Cognitive Crawler cache cleared")
    
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
    
    @observe(name="investigative_journalist_sub_agent")
    async def call_investigative_journalist(
        self,
        query: str,
        max_iterations: int = 20,
        resume_from: str = None,
        event_callback: callable = None  # Simple callback for real-time updates
    ) -> Dict[str, Any]:
        """
        Call Investigative Journalist Sub-Agent
        
        ✅ IMPLEMENTED (Oct 18, 2025)
        
        This sub-agent performs:
        - Deep, multi-iteration investigative research
        - Evidence-based reporting with full source attribution  
        - Hypothesis-driven analysis
        - Cost-optimized extraction (91% cheaper than baseline)
        - Resume capability via MongoDB evidence repository
        
        Args:
            query: Investigation query (e.g. "India cough syrup deaths")
            max_iterations: Maximum iterations to run (default: 20, max: 100)
            resume_from: Optional investigation_id to resume previous investigation
            event_callback: Optional async function to call with events (type, data)
        
        Returns:
            {
                "article": "Full markdown investigative report",
                "investigation_id": "inv_abc123",
                "evidence_summary": {...},
                "status": "SUCCESS" | "ERROR"
            }
        """
        import sys
        import os
        
        # Get absolute path to investigative journalist directory
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        agent_dir = os.path.abspath(os.path.join(current_file_dir, '../sub_agents/investigative_journalist'))
        
        print(f"\n🔍 Loading Investigative Journalist from: {agent_dir}")
        print(f"   Directory exists: {os.path.exists(agent_dir)}")
        
        if not os.path.exists(agent_dir):
            return {
                "success": False,
                "sub_agent": "investigative_journalist",
                "status": "ERROR",
                "error": f"Investigative journalist directory not found: {agent_dir}",
                "query": query
            }
        
        try:
            # Add agent_dir to sys.path
            if agent_dir not in sys.path:
                sys.path.insert(0, agent_dir)
            
            print(f"   📦 Loading investigative journalist modules...")
            
            # Import agent modules using importlib for better control
            import importlib.util
            
            # Load LeanInvestigator
            investigator_path = os.path.join(agent_dir, 'lean_investigator.py')
            spec = importlib.util.spec_from_file_location("lean_investigator", investigator_path)
            lean_investigator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lean_investigator_module)
            LeanInvestigator = lean_investigator_module.LeanInvestigator
            
            # Load evidence_repository
            evidence_repo_path = os.path.join(agent_dir, 'tools', 'evidence_repository.py')
            spec = importlib.util.spec_from_file_location("evidence_repository", evidence_repo_path)
            evidence_repo_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(evidence_repo_module)
            save_investigation = evidence_repo_module.save_investigation
            load_investigation = evidence_repo_module.load_investigation
            
            print(f"   ✅ Successfully loaded investigative_journalist modules")
            
            # Load previous investigation if resuming
            initial_state = None
            actual_max_iterations = max_iterations  # Default
            
            if resume_from:
                print(f"   🔄 Resuming investigation: {resume_from}")
                initial_state = await load_investigation(resume_from)
                if initial_state:
                    # Use max_iterations from MongoDB (already calculated in app.py)
                    actual_max_iterations = initial_state.get('max_iterations', max_iterations)
                    print(f"   📊 Using max_iterations from MongoDB: {actual_max_iterations}")
            
            # Create investigator with correct max_iterations
            investigator = LeanInvestigator(max_iterations=actual_max_iterations)
            
            # Run investigation with incremental saves enabled
            print(f"   🚀 Starting investigation...")
            result = await investigator.investigate(
                query=query,
                investigation_id=resume_from,  # Pass ID for real-time MongoDB updates
                event_callback=event_callback  # Pass callback for real-time WebSocket events
            )
            
            # Save to MongoDB
            investigation_id = await save_investigation(
                {
                    "investigation_id": resume_from if resume_from else None,  # Use existing ID if resuming
                    "initial_query": query,
                    "iteration": result.get("iterations", max_iterations),
                    "max_iterations": max_iterations,
                    "entities": result.get("entities", {}),
                    "facts": result.get("facts", []),
                    "connections": result.get("connections", []),
                    "anomalies": result.get("anomalies", []),
                    "hypotheses": result.get("hypotheses", []),
                    "questions": result.get("questions", []),  # Add questions
                    "evidence": [],
                    "seen_urls": [],
                    "previous_queries": [],
                    "search_results": [],
                    "extracted_content": [],
                    "investigation_complete": True,
                    "final_report": result.get("report"),
                    "artifacts": [],
                    "execution_log": [],
                    "error_log": [],
                    "cost_tracking": investigator.costs
                }
            )
            
            print(f"   ✅ Investigation complete: {investigation_id}")
            
            return {
                "success": True,
                "sub_agent": "investigative_journalist",
                "status": "SUCCESS",
                "query": query,
                
                # Primary outputs
                "article": result.get("report"),
                "investigation_id": investigation_id,
                
                # Evidence summary
                "evidence_summary": {
                    "entities": len(result.get("entities", {})),
                    "facts": len(result.get("facts", [])),
                    "connections": len(result.get("connections", [])),
                    "anomalies": len(result.get("anomalies", [])),
                    "hypotheses": len(result.get("hypotheses", [])),
                    "cost": investigator.costs.get("total_cost", 0.0)
                },
                
                # Detailed results
                "entities": result.get("entities", {}),
                "facts": result.get("facts", []),
                "connections": result.get("connections", []),
                "anomalies": result.get("anomalies", []),
                
                # Cost breakdown
                "cost_breakdown": investigator.costs,
                
                # Artifacts
                "artifacts": [],
                
                # Metadata
                "iterations_completed": result.get("iterations", 0),
                "max_iterations": max_iterations
            }
            
        except Exception as e:
            import traceback
            print(f"   ❌ Error running investigative journalist: {e}")
            traceback.print_exc()
            
            return {
                "success": False,
                "sub_agent": "investigative_journalist",
                "status": "ERROR",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "query": query
            }
    
    @observe(name="cognitive_crawler_sub_agent")
    async def call_cognitive_crawler(
        self,
        action: str,
        query: str,
        crawl_sources: list = None,
        session_id: str = None,
        max_pages: int = 20,
        max_depth: int = 2,
        event_callback = None
    ) -> Dict[str, Any]:
        """
        Call Cognitive Crawler Sub-Agent
        
        🆕 NEW - Generic web crawler with intelligent discovery
        
        Two modes:
        1. "discover" - Find related pages using Tavily + intelligent mapping
        2. "crawl" - Crawl specified websites and store in vector DB
        
        Note: RAG/Chat functionality is now a separate tool (knowledge_base.py)
        Use query_knowledge_base() tool for querying crawled content.
        
        Args:
            action: "discover" or "crawl"
            query: Natural language query for discovery OR description for crawl
            crawl_sources: List of URLs to crawl (for crawl mode)
            session_id: Session ID for tracking
            max_pages: Max pages to crawl (user-controlled)
            max_depth: Max link depth (1=only specified URLs, 2=+1 hop)
            event_callback: Optional callback for real-time events
        
        Returns:
            Crawl results with embeddings stored in vector DB
        """
        import sys
        import os
        
        # Get absolute path to cognitive crawler directory
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        agent_dir = os.path.abspath(os.path.join(current_file_dir, '../sub_agents/cognitive_crawler'))
        
        print(f"\n🕷️  Loading Cognitive Crawler from: {agent_dir}")
        
        if not os.path.exists(agent_dir):
            return {
                "success": False,
                "sub_agent": "cognitive_crawler",
                "status": "ERROR",
                "error": f"Cognitive crawler directory not found: {agent_dir}",
                "query": query,
                "action": action
            }
        
        try:
            # PERFORMANCE: Load modules only once, then cache
            if self._cognitive_crawler_graph is None:
                print(f"\n🕷️  Loading Cognitive Crawler (first time)...")
                
                # Module isolation
                import importlib.util
                
                original_sys_path = sys.path.copy()
                saved_modules = {}
                conflict_modules = ['state', 'nodes', 'config', 'graph', 'tools']
                
                for mod_name in conflict_modules:
                    if mod_name in sys.modules:
                        saved_modules[mod_name] = sys.modules[mod_name]
                        del sys.modules[mod_name]
                
                # Put agent_dir FIRST
                clean_path = [agent_dir]
                for path in original_sys_path:
                    if 'sub_agents' not in path:
                        clean_path.append(path)
                sys.path = clean_path
                
                # Import modules
                from graph import create_cognitive_crawler_graph
                from state import CognitiveCrawlerState
                
                print(f"   ✅ Modules loaded, creating graph...")
                
                # Create and cache graph
                self._cognitive_crawler_graph = create_cognitive_crawler_graph()
                self._cognitive_crawler_state_class = CognitiveCrawlerState
                
                # Restore
                sys.path = original_sys_path
                for mod_name in conflict_modules:
                    if mod_name in sys.modules:
                        del sys.modules[mod_name]
                for mod_name, mod_obj in saved_modules.items():
                    sys.modules[mod_name] = mod_obj
                
                print(f"   ✅ Cognitive Crawler cached (subsequent calls will be instant)\n")
            
            else:
                # Use cached graph (FAST!)
                print(f"\n🕷️  Using cached Cognitive Crawler (instant)\n")
            
            # Use cached graph
            graph = self._cognitive_crawler_graph
            
            # Initialize state
            initial_state: CognitiveCrawlerState = {
                "query": query,
                "action": action,
                "crawl_sources": crawl_sources or [],
                "max_pages": max_pages,
                "max_depth": max_depth,
                "crawl_filters": None,
                "pages_discovered": [],
                "sitemap_urls": [],
                "crawl_results": [],
                "pages_crawled": 0,
                "crawl_complete": False,
                "tenders_parsed": [],  # Intermediate processing results
                "tenders_stored": 0,
                "portals_discovered": [],
                "listing_pages": [],
                "thread_id": session_id,
                "embeddings_generated": 0,
                "documents_stored": 0,
                "chat_history": [],
                "relevant_chunks": [],
                "relevant_tenders": [],  # RAG results
                "similarity_scores": [],
                "answer": "",
                "sources": [],
                "summary": "",
                "key_findings": [],
                "recommendations": [],
                "confidence": 0.0,
                "artifacts": [],
                "execution_log": [],
                "error_log": [],
                "session_id": session_id,
                "execution_time": 0.0
            }
            
            # Run agent
            result = await graph.ainvoke(initial_state)
            
            # Return in expected format
            return {
                "success": True,
                "sub_agent": "cognitive_crawler",
                "status": "COMPLETED",
                "data": {
                    "query": result.get("query"),
                    "action": result.get("action"),
                    "pages_crawled": result.get("pages_crawled", 0),
                    "embeddings_generated": result.get("embeddings_generated", 0),
                    "crawl_complete": result.get("crawl_complete", False),
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", []),
                    "relevant_chunks": result.get("relevant_chunks", []),
                    "summary": result.get("summary", ""),
                    "key_findings": result.get("key_findings", []),
                    "confidence": result.get("confidence", 0.0),
                    "artifacts": result.get("artifacts", []),
                    "execution_log": result.get("execution_log", [])
                }
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"\n❌ Cognitive crawler error: {e}")
            print(error_trace)
            
            return {
                "success": False,
                "sub_agent": "cognitive_crawler",
                "status": "ERROR",
                "error": str(e),
                "traceback": error_trace,
                "query": query,
                "action": action
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

