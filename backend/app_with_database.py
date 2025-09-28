"""
FastAPI backend server with MongoDB integration for testing database writes
"""

import asyncio
import os
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from research_agent import WebResearchAgent
from config import Config

# Import our database services
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

try:
    from services.mongo_service import MongoService
    from services.analytics_service import AnalyticsService
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Database services not available: {e}")
    DATABASE_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Web Research Agent API with Database",
    description="A sophisticated web research agent using LangGraph, Tavily, and MongoDB",
    version="1.0.0"
)

# Get CORS origins from environment or use defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
agent: Optional[WebResearchAgent] = None
mongo_service: Optional[MongoService] = None
analytics_service: Optional[AnalyticsService] = None

class ResearchRequest(BaseModel):
    """Request model for research queries"""
    query: str
    user_session: Optional[str] = None
    llm_provider: Optional[str] = "openai"
    model: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class ResearchResponse(BaseModel):
    """Response model for research results"""
    success: bool
    query_id: Optional[str] = None
    query: str
    search_terms: list[str]
    sources_count: int
    final_answer: str
    sources: list[str]
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the research agent and database on startup"""
    global agent, mongo_service, analytics_service
    
    if not Config.validate_config():
        raise RuntimeError("Invalid configuration. Please check your API keys.")
    
    # Initialize research agent
    llm_config = Config.get_llm_config()
    agent = WebResearchAgent(
        llm_provider=llm_config["provider"],
        model=llm_config["model"]
    )
    print("🚀 Web Research Agent initialized successfully!")
    
    # Initialize database services if available
    if DATABASE_AVAILABLE:
        try:
            mongo_service = MongoService()
            analytics_service = AnalyticsService(mongo_service)
            await mongo_service.connect()
            print("🗄️  MongoDB connection established successfully!")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("🔄 Continuing without database persistence")
            mongo_service = None
            analytics_service = None
    else:
        print("🔄 Running without database integration")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    global mongo_service
    if mongo_service:
        await mongo_service.disconnect()
        print("🔌 Database connection closed")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Web Research Agent API with Database",
        "status": "running",
        "version": "1.0.0",
        "database_available": DATABASE_AVAILABLE and mongo_service is not None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "database_connected": mongo_service is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Perform web research on a given query with database persistence
    
    Args:
        request: Research request containing query and optional parameters
        
    Returns:
        ResearchResponse: Comprehensive research results with query_id if saved to database
    """
    if not agent:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if len(request.query) > Config.MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Query too long. Maximum length is {Config.MAX_QUERY_LENGTH} characters"
        )
    
    query_id = None
    start_time = time.perf_counter()
    
    try:
        # Step 1: Create query record in database if available
        if mongo_service:
            try:
                query_id = await mongo_service.create_query({
                    "query_text": request.query,
                    "user_session": request.user_session or "anonymous",
                    "options": request.options or {}
                })
                
                # Update status to processing
                await mongo_service.update_query_status(query_id, "processing")
                print(f"📝 Created database query record: {query_id}")
            except Exception as e:
                print(f"⚠️  Database query creation failed: {e}")
        
        # Step 2: Perform research
        if request.llm_provider != Config.DEFAULT_LLM_PROVIDER or request.model:
            custom_agent = WebResearchAgent(
                llm_provider=request.llm_provider,
                model=request.model or Config.get_llm_config()["model"]
            )
            result = await custom_agent.research(request.query)
        else:
            result = await agent.research(request.query)
        
        end_time = time.perf_counter()
        processing_time_ms = int((end_time - start_time) * 1000)
        
        # Step 3: Handle research results
        if result.get("error"):
            # Mark as failed in database
            if mongo_service and query_id:
                try:
                    await mongo_service.update_query_status(
                        query_id, "failed", error_message=result["error"]
                    )
                    print(f"❌ Marked query {query_id} as failed in database")
                except Exception as e:
                    print(f"⚠️  Failed to update query status: {e}")
            
            return ResearchResponse(
                success=False,
                query_id=query_id,
                query=request.query,
                search_terms=result.get("search_terms", []),
                sources_count=len(result.get("sources", [])),
                final_answer="",
                sources=result.get("sources", []),
                processing_time_ms=processing_time_ms,
                error=result["error"]
            )
        
        # Step 4: Save successful results to database
        if mongo_service and query_id:
            try:
                # Save research results
                await mongo_service.save_results(query_id, {
                    "final_answer": result.get("final_answer", ""),
                    "search_terms": result.get("search_terms", []),
                    "sources": [
                        {
                            "url": source,
                            "title": f"Source from {source}",
                            "relevance_score": 0.9,  # Default score
                            "content_snippet": "Research source"
                        }
                        for source in result.get("sources", [])[:10]
                    ],
                    "agent_workflow": [
                        {
                            "step_name": "Query Analysis",
                            "duration_ms": int(processing_time_ms * 0.2),
                            "output_summary": f"Analyzed query: {request.query}",
                            "agent_type": "analyzer"
                        },
                        {
                            "step_name": "Web Search",
                            "duration_ms": int(processing_time_ms * 0.6),
                            "output_summary": f"Found {len(result.get('sources', []))} sources",
                            "agent_type": "searcher"
                        },
                        {
                            "step_name": "Result Synthesis",
                            "duration_ms": int(processing_time_ms * 0.2),
                            "output_summary": "Synthesized final answer",
                            "agent_type": "synthesizer"
                        }
                    ]
                })
                
                # Mark query as completed
                await mongo_service.update_query_status(
                    query_id, "completed", processing_time_ms=processing_time_ms
                )
                
                # Record analytics
                await mongo_service.record_analytics(query_id, processing_time_ms)
                
                print(f"✅ Saved research results to database: {query_id}")
                
            except Exception as e:
                print(f"⚠️  Failed to save results to database: {e}")
        
        return ResearchResponse(
            success=True,
            query_id=query_id,
            query=request.query,
            search_terms=result.get("search_terms", []),
            sources_count=len(result.get("sources", [])),
            final_answer=result.get("final_answer", ""),
            sources=result.get("sources", [])[:Config.MAX_SOURCES_DISPLAY],
            processing_time_ms=processing_time_ms,
            error=None
        )
        
    except Exception as e:
        # Mark as failed in database
        if mongo_service and query_id:
            try:
                await mongo_service.update_query_status(
                    query_id, "failed", error_message=str(e)
                )
            except Exception as db_e:
                print(f"⚠️  Failed to update failed status: {db_e}")
        
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@app.get("/research/{query_id}")
async def get_query_results(query_id: str):
    """Get research results by query ID"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get query
        query = await mongo_service.get_query(query_id)
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        
        # Get results if completed
        if query.status == "completed":
            results = await mongo_service.get_results(query_id)
            return {
                "query_id": query_id,
                "status": "completed",
                "query": query.query_text,
                "final_answer": results.final_answer if results else "",
                "sources": [source.dict() for source in results.sources] if results else [],
                "search_terms": results.search_terms if results else [],
                "processing_time_ms": query.processing_time_ms,
                "created_at": query.created_at,
                "completed_at": query.completed_at
            }
        else:
            return {
                "query_id": query_id,
                "status": query.status,
                "query": query.query_text,
                "created_at": query.created_at,
                "error_message": query.error_message if query.status == "failed" else None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve query: {str(e)}")

@app.get("/research")
async def get_query_history(
    user_session: str = "anonymous",
    limit: int = 10,
    offset: int = 0
):
    """Get query history for a user session"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        queries = await mongo_service.get_user_queries(user_session, limit, offset)
        return {
            "queries": [
                {
                    "query_id": q.query_id,
                    "query": q.query_text,
                    "status": q.status,
                    "created_at": q.created_at,
                    "processing_time_ms": q.processing_time_ms
                }
                for q in queries
            ],
            "total": len(queries),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@app.get("/analytics")
async def get_analytics():
    """Get analytics dashboard data"""
    if not analytics_service:
        raise HTTPException(status_code=503, detail="Analytics not available")
    
    try:
        dashboard_data = await analytics_service.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")

@app.get("/config")
async def get_config():
    """Get current configuration (without sensitive data)"""
    return {
        "llm_provider": Config.DEFAULT_LLM_PROVIDER,
        "max_query_length": Config.MAX_QUERY_LENGTH,
        "max_sources_display": Config.MAX_SOURCES_DISPLAY,
        "search_depth": Config.SEARCH_DEPTH,
        "database_available": DATABASE_AVAILABLE and mongo_service is not None
    }

@app.get("/database/test")
async def test_database_connection():
    """Test database connection and basic operations"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Test creating a test query
        test_query_id = await mongo_service.create_query({
            "query_text": "Database connection test",
            "user_session": "test-connection"
        })
        
        # Test retrieving the query
        query = await mongo_service.get_query(test_query_id)
        
        return {
            "status": "success",
            "message": "Database connection is working",
            "test_query_id": test_query_id,
            "test_query_retrieved": query is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Run the server on port 8001 for testing
    uvicorn.run(
        "app_with_database:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
