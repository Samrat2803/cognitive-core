"""
FastAPI backend server for the Web Research Agent
"""

import asyncio
import os
import sys
import time
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from research_agent import WebResearchAgent
from config import Config

# Load environment variables (for local development)
# In production (AWS), environment variables are set via .ebextensions
load_dotenv()

# Import database services using absolute imports
DATABASE_AVAILABLE = False
MongoService = None
AnalyticsService = None

try:
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    from services.mongo_service import MongoService
    from services.analytics_service import AnalyticsService
    DATABASE_AVAILABLE = True
    print("🗄️  Database services imported successfully")
except ImportError as e:
    print(f"⚠️  Database services not available: {e}")
    DATABASE_AVAILABLE = False
    # Define dummy classes for type hints
    class MongoService: pass
    class AnalyticsService: pass

# Initialize FastAPI app
app = FastAPI(
    title="Political Analyst Workbench API",
    description="A sophisticated web research agent using LangGraph and Tavily with real-time WebSocket support",
    version="2.0.0"
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
    
    # Debug environment variables in AWS
    print("🔍 Environment Check:")
    print(f"TAVILY_API_KEY: {'✅ SET' if os.getenv('TAVILY_API_KEY') else '❌ MISSING'}")
    print(f"OPENAI_API_KEY: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ MISSING'}")
    print(f"MONGODB_CONNECTION_STRING: {'✅ SET' if os.getenv('MONGODB_CONNECTION_STRING') else '❌ MISSING'}")
    
    if not Config.validate_config():
        raise RuntimeError("Invalid configuration. Please check your API keys.")
    
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
            print(f"⚠️  Error type: {type(e).__name__}")
            print("🔄 Continuing without database persistence")
            mongo_service = None
            analytics_service = None
    else:
        print("🔄 Running without database integration")
    
    # Initialize global services for new endpoints
    from services.analysis_service import analysis_service
    from websocket_manager import websocket_manager
    
    # Initialize analysis service with database connection
    if mongo_service:
        analysis_service.mongo_service = mongo_service
    
    print("🚀 MVP endpoints initialized successfully!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Web Research Agent API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with detailed diagnostics"""
    # Test database connection if available
    db_connected = False
    if mongo_service:
        try:
            await mongo_service.connect()
            db_connected = True
        except Exception as e:
            print(f"Health check DB connection failed: {e}")
            db_connected = False
    
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "database_available": DATABASE_AVAILABLE,
        "database_connected": db_connected,
        "environment_variables": {
            "tavily_api_key": bool(os.getenv("TAVILY_API_KEY")),
            "openai_api_key": bool(os.getenv("OPENAI_API_KEY")), 
            "mongodb_connection": bool(os.getenv("MONGODB_CONNECTION_STRING"))
        },
        "services": {
            "mongo_service": mongo_service is not None,
            "analytics_service": analytics_service is not None
        }
    }

@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Perform web research on a given query with database persistence
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
                    "user_session": request.user_session or "anonymous"
                })
                await mongo_service.update_query_status(query_id, "processing")
                print(f"📝 Created database query: {query_id}")
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
        
        # Step 3: Handle results and save to database
        if result.get("error"):
            if mongo_service and query_id:
                await mongo_service.update_query_status(query_id, "failed", error_message=result["error"])
            
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
                await mongo_service.save_results(query_id, {
                    "final_answer": result.get("final_answer", ""),
                    "search_terms": result.get("search_terms", []),
                    "sources": [{"url": source, "title": f"Source from {source}", "relevance_score": 0.9} 
                               for source in result.get("sources", [])[:10]]
                })
                await mongo_service.update_query_status(query_id, "completed", processing_time_ms=processing_time_ms)
                await mongo_service.record_analytics(query_id, processing_time_ms)
                print(f"✅ Saved results to database: {query_id}")
            except Exception as e:
                print(f"⚠️  Failed to save to database: {e}")
        
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
        if mongo_service and query_id:
            await mongo_service.update_query_status(query_id, "failed", error_message=str(e))
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@app.get("/config")
async def get_config():
    """Get current configuration (without sensitive data)"""
    return {
        "llm_provider": Config.DEFAULT_LLM_PROVIDER,
        "max_query_length": Config.MAX_QUERY_LENGTH,
        "max_sources_display": Config.MAX_SOURCES_DISPLAY,
        "search_depth": Config.SEARCH_DEPTH
    }


# Include MVP routers - must be after app creation but before WebSocket
try:
    from routers import chat_router, analysis_router
    app.include_router(chat_router)
    app.include_router(analysis_router)
    print("🚀 MVP routers included successfully!")
except Exception as e:
    print(f"❌ Failed to include MVP routers: {e}")
    import traceback
    traceback.print_exc()


# WebSocket endpoint for real-time communication
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time analysis updates
    Supports heartbeat ping/pong and progress messages
    """
    from websocket_manager import websocket_manager
    
    # Connect client
    connected = await websocket_manager.connect(websocket, session_id)
    if not connected:
        return
    
    try:
        while True:
            try:
                # Wait for client messages (e.g., pong responses)
                data = await websocket.receive_text()
                message = json.loads(data)
                await websocket_manager.handle_client_message(session_id, message)
                
            except WebSocketDisconnect:
                print(f"🔌 WebSocket client disconnected: {session_id}")
                break
            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON from client: {session_id}")
            except Exception as e:
                print(f"❌ WebSocket error for {session_id}: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        await websocket_manager.disconnect(session_id)

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
