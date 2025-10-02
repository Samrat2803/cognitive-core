"""
Analysis Service for background task orchestration with progress tracking
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from research_agent import WebResearchAgent
from config import Config

# Import database services (optional)
DATABASE_AVAILABLE = False
MongoService = None

try:
    from .mongo_service import MongoService
    DATABASE_AVAILABLE = True
except ImportError:
    print("⚠️ Database services not available for analysis service")
    class MongoService: 
        pass

# Configuration constants (non-secret)
DEFAULT_ANALYSIS_TIMEOUT = 300  # 5 minutes
PROGRESS_UPDATE_INTERVAL = 2.0  # seconds


class AnalysisTask:
    """Represents a background analysis task"""
    
    def __init__(self, analysis_id: str, query_text: str, parameters: Dict[str, Any], session_id: str):
        self.analysis_id = analysis_id
        self.query_text = query_text
        self.parameters = parameters
        self.session_id = session_id
        self.status = "processing"
        self.created_at = datetime.utcnow()
        self.progress = {
            "current_step": "initializing",
            "completion_percentage": 0,
            "processed_countries": [],
            "remaining_countries": parameters.get("countries", []),
            "articles_processed": 0,
            "total_articles": 0
        }
        self.results: Optional[Dict[str, Any]] = None
        self.error: Optional[Dict[str, Any]] = None
        self.task: Optional[asyncio.Task] = None


class AnalysisService:
    """Service for managing background analysis tasks"""
    
    def __init__(self, mongo_service: Optional[MongoService] = None):
        self.mongo_service = mongo_service
        self.tasks: Dict[str, AnalysisTask] = {}  # In-memory task storage
        self.agent: Optional[WebResearchAgent] = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the research agent"""
        try:
            llm_config = Config.get_llm_config()
            self.agent = WebResearchAgent(
                llm_provider=llm_config["provider"],
                model=llm_config["model"]
            )
            print("🤖 Analysis service agent initialized")
        except Exception as e:
            print(f"❌ Failed to initialize analysis agent: {e}")
    
    async def create_analysis(
        self, 
        query_text: str, 
        parameters: Dict[str, Any], 
        session_id: str
    ) -> str:
        """Create a new analysis task"""
        analysis_id = str(uuid.uuid4())
        task = AnalysisTask(analysis_id, query_text, parameters, session_id)
        self.tasks[analysis_id] = task
        
        # Save to database if available
        if self.mongo_service and DATABASE_AVAILABLE:
            try:
                query_id = await self.mongo_service.create_query({
                    "query_text": query_text,
                    "user_session": session_id,
                    "options": parameters
                })
                # Map analysis_id to query_id for database tracking
                task.query_id = query_id
                await self.mongo_service.update_query_status(query_id, "processing")
            except Exception as e:
                print(f"⚠️ Failed to save analysis to database: {e}")
        
        print(f"📝 Created analysis: {analysis_id}")
        return analysis_id
    
    async def start_analysis(self, analysis_id: str, websocket_manager=None) -> bool:
        """Start background processing for an analysis"""
        if analysis_id not in self.tasks:
            return False
        
        task = self.tasks[analysis_id]
        if task.task is not None:  # Already started
            return False
        
        # Start background task
        task.task = asyncio.create_task(
            self._execute_analysis(analysis_id, websocket_manager)
        )
        
        print(f"🚀 Started analysis: {analysis_id}")
        return True
    
    async def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an analysis"""
        if analysis_id not in self.tasks:
            return None
        
        task = self.tasks[analysis_id]
        
        response = {
            "analysis_id": analysis_id,
            "status": task.status,
            "created_at": task.created_at
        }
        
        if task.status == "processing":
            response["progress"] = task.progress
            response["estimated_completion"] = task.created_at + timedelta(seconds=DEFAULT_ANALYSIS_TIMEOUT)
        elif task.status == "completed":
            response["results"] = task.results
            response["query"] = {
                "text": task.query_text,
                "parameters": task.parameters
            }
        elif task.status == "failed":
            response["error"] = task.error
        
        return response
    
    async def _execute_analysis(self, analysis_id: str, websocket_manager=None):
        """Execute the analysis in background"""
        task = self.tasks[analysis_id]
        start_time = time.perf_counter()
        
        try:
            # Step 1: Analyze query and extract search terms
            await self._update_progress(
                task, "analyzing_query", 10, websocket_manager
            )
            
            if not self.agent:
                raise Exception("Research agent not initialized")
            
            # Use the existing research agent to perform analysis (sync method)
            result = self.agent.research(task.query_text)
            
            if result.get("error"):
                raise Exception(result["error"])
            
            # Step 2: Simulate country-specific analysis for geopolitical queries
            countries = task.parameters.get("countries", [])
            if countries:
                await self._process_countries(task, countries, result, websocket_manager)
            else:
                # Generic research without country breakdown
                await self._update_progress(
                    task, "processing_research", 50, websocket_manager
                )
                await asyncio.sleep(2)  # Simulate processing time
                await self._update_progress(
                    task, "finalizing_results", 90, websocket_manager
                )
            
            # Step 3: Format results according to MVP contract
            formatted_results = await self._format_results(task, result, countries)
            
            # Step 4: Mark as completed
            task.status = "completed"
            task.results = formatted_results
            task.progress["completion_percentage"] = 100
            
            # Save to database if available
            if self.mongo_service and hasattr(task, 'query_id'):
                try:
                    processing_time_ms = int((time.perf_counter() - start_time) * 1000)
                    await self.mongo_service.save_results(task.query_id, {
                        "final_answer": result.get("final_answer", ""),
                        "search_terms": result.get("search_terms", []),
                        "sources": [{"url": source, "title": f"Source from {source}", "relevance_score": 0.9} 
                                   for source in result.get("sources", [])[:10]]
                    })
                    await self.mongo_service.update_query_status(
                        task.query_id, "completed", processing_time_ms=processing_time_ms
                    )
                except Exception as e:
                    print(f"⚠️ Failed to save results to database: {e}")
            
            # Broadcast completion
            if websocket_manager:
                await websocket_manager.broadcast_completion(analysis_id, formatted_results)
            
            print(f"✅ Analysis completed: {analysis_id}")
            
        except Exception as e:
            # Handle failure
            task.status = "failed"
            task.error = {
                "code": "ANALYSIS_FAILED",
                "message": str(e),
                "recoverable": True
            }
            
            # Save error to database
            if self.mongo_service and hasattr(task, 'query_id'):
                try:
                    await self.mongo_service.update_query_status(
                        task.query_id, "failed", error_message=str(e)
                    )
                except Exception as db_e:
                    print(f"⚠️ Failed to save error to database: {db_e}")
            
            # Broadcast error
            if websocket_manager:
                await websocket_manager.broadcast_error(analysis_id, task.error)
            
            print(f"❌ Analysis failed: {analysis_id} - {e}")
    
    async def _process_countries(self, task: AnalysisTask, countries: List[str], base_result: Dict[str, Any], websocket_manager=None):
        """Process analysis for each country concurrently"""
        
        # Create concurrent country analysis tasks
        country_tasks = []
        for country in countries:
            country_task = self._analyze_country_async(country, task, websocket_manager)
            country_tasks.append(country_task)
        
        # Update initial progress
        task.progress.update({
            "current_step": "analyzing_countries",
            "completion_percentage": 20,
            "processed_countries": [],
            "remaining_countries": countries,
            "articles_processed": 0,
            "total_articles": len(countries) * 20  # Estimate
        })
        
        if websocket_manager:
            await websocket_manager.broadcast_progress(task.analysis_id, task.progress)
        
        # Execute country analyses concurrently with progress updates
        processed_countries = []
        total_articles = 0
        
        # Process in batches to avoid overwhelming APIs
        batch_size = 3
        for i in range(0, len(country_tasks), batch_size):
            batch = country_tasks[i:i+batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            # Update progress after each batch
            for j, result in enumerate(batch_results):
                if not isinstance(result, Exception):
                    country_name = countries[i + j]
                    processed_countries.append(country_name)
                    total_articles += 20
                    
                    completion = 20 + (len(processed_countries) * 60 // len(countries))
                    task.progress.update({
                        "current_step": f"completed_{country_name.lower().replace(' ', '_')}",
                        "completion_percentage": completion,
                        "processed_countries": processed_countries.copy(),
                        "remaining_countries": countries[len(processed_countries):],
                        "articles_processed": total_articles,
                        "total_articles": len(countries) * 20
                    })
                    
                    if websocket_manager:
                        await websocket_manager.broadcast_progress(task.analysis_id, task.progress)
        
        # Final progress update
        task.progress.update({
            "current_step": "synthesizing_results",
            "completion_percentage": 85,
            "processed_countries": processed_countries,
            "remaining_countries": [],
            "articles_processed": total_articles,
            "total_articles": total_articles
        })
        
        if websocket_manager:
            await websocket_manager.broadcast_progress(task.analysis_id, task.progress)
    
    async def _analyze_country_async(self, country: str, task: AnalysisTask, websocket_manager=None):
        """Async country-specific analysis (simulated for MVP)"""
        # In real implementation, this would make concurrent API calls for country-specific data
        # For MVP, we simulate with minimal delay
        # No delay - instant processing
        return {
            "country": country,
            "articles_processed": 20,
            "analysis_complete": True
        }
    
    async def _update_progress(self, task: AnalysisTask, step: str, percentage: int, websocket_manager=None):
        """Update task progress and broadcast to WebSocket"""
        task.progress.update({
            "current_step": step,
            "completion_percentage": percentage
        })
        
        if websocket_manager:
            await websocket_manager.broadcast_progress(task.analysis_id, task.progress)
        
        # No delay for instant updates
        pass
    
    async def _format_results(self, task: AnalysisTask, research_result: Dict[str, Any], countries: List[str]) -> Dict[str, Any]:
        """Format results according to MVP contract"""
        
        # Create mock country results for geopolitical analysis
        country_results = []
        if countries:
            for country in countries:
                # Generate mock sentiment data (in real implementation, this would be analyzed)
                import random
                sentiment_score = random.uniform(-0.8, 0.8)
                confidence = random.uniform(0.75, 0.95)
                
                country_results.append({
                    "country": country,
                    "sentiment_score": round(sentiment_score, 2),
                    "confidence": round(confidence, 2),
                    "articles_count": random.randint(15, 25),
                    "dominant_sentiment": "positive" if sentiment_score > 0.3 else "negative" if sentiment_score < -0.3 else "neutral",
                    "key_themes": ["politics", "security", "international relations"][:random.randint(2, 3)],
                    "bias_analysis": {
                        "bias_types": ["framing", "selection"],
                        "bias_severity": round(random.uniform(0.2, 0.6), 2),
                        "notes": f"Analysis based on {random.randint(15, 25)} sources"
                    }
                })
        
        # Create summary
        overall_sentiment = sum(cr["sentiment_score"] for cr in country_results) / len(country_results) if country_results else 0.0
        
        return {
            "summary": {
                "overall_sentiment": round(overall_sentiment, 2),
                "countries_analyzed": len(countries),
                "total_articles": len(research_result.get("sources", [])),
                "analysis_confidence": 0.87,
                "bias_detected": True,
                "completion_time_ms": task.progress.get("total_processing_time", 45000)
            },
            "country_results": country_results
        }
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed/failed tasks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for analysis_id, task in self.tasks.items():
            if task.created_at < cutoff_time and task.status in ["completed", "failed"]:
                to_remove.append(analysis_id)
        
        for analysis_id in to_remove:
            del self.tasks[analysis_id]
            print(f"🗑️ Cleaned up old task: {analysis_id}")


# Global analysis service instance  
analysis_service = AnalysisService()


if __name__ == "__main__":
    # Test analysis service functionality
    async def test_analysis_service():
        print("🧪 Testing Analysis Service...")
        
        service = AnalysisService()
        
        # Test analysis creation
        analysis_id = await service.create_analysis(
            query_text="Test geopolitical sentiment analysis",
            parameters={"countries": ["United States", "Iran"], "days": 7},
            session_id="test_session"
        )
        
        print(f"✅ Created analysis: {analysis_id}")
        
        # Test status retrieval
        status = await service.get_analysis_status(analysis_id)
        print(f"✅ Status retrieved: {status['status']}")
        
        # Test result formatting
        mock_result = {
            "final_answer": "Test analysis result",
            "search_terms": ["test", "analysis"],
            "sources": ["https://example.com"]
        }
        
        task = service.tasks[analysis_id]
        formatted = await service._format_results(task, mock_result, ["United States", "Iran"])
        print(f"✅ Results formatted: {formatted['summary']['countries_analyzed']} countries")
        
        print("✅ Analysis service test completed!")
    
    asyncio.run(test_analysis_service())
