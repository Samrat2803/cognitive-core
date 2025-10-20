"""
FastAPI backend server for the Political Analyst Agent
Using LangGraph Master Agent architecture
"""

import asyncio
import os
import sys
import time
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Add parent directory to path to import agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langgraph_master_agent.main import MasterPoliticalAnalyst
from config_server import Config
from datetime import datetime, timezone, timedelta
from services.mongo_service import MongoService

# Load environment variables (for local development)
load_dotenv()

# Base URL for artifact links (use CloudFront in production, localhost in dev)
BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

# Initialize FastAPI app
app = FastAPI(
    title="Political Analyst Workbench API",
    description="A sophisticated political analysis agent using LangGraph with Tavily real-time data and artifact generation",
    version="1.0.0"
)

# Get CORS origins from environment or use defaults
# For development: allow all origins
cors_origins = os.getenv("CORS_ORIGINS", "*")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression middleware for artifact optimization
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global instances
agent: Optional[MasterPoliticalAnalyst] = None
mongo_service = MongoService() if os.getenv("MONGODB_CONNECTION_STRING") else None

# RSS Background Poller (runs in background)
rss_poller_task: Optional[asyncio.Task] = None


# ============================================================================
# RSS Background Poller Function
# ============================================================================

async def run_rss_background_poller():
    """
    Background task that continuously polls RSS feeds every 5 minutes
    Runs independently without blocking the server startup
    """
    from shared.rss_collector import RSSCollector
    from datetime import timedelta
    
    print("\n" + "="*80)
    print("📰 RSS BACKGROUND POLLER - INITIALIZING")
    print("="*80)
    
    try:
        collector = RSSCollector()
        poll_interval = 5 * 60  # 5 minutes in seconds
        
        print(f"✅ RSS Collector initialized")
        print(f"⏰ Poll interval: 5 minutes")
        print(f"🕐 Fresh window: 72 hours")
        print(f"📦 Collection: rss_articles")
        print("="*80)
        
        # Run first poll immediately on startup
        print("\n🔄 Running initial RSS poll on startup...")
        await poll_rss_feeds_once(collector)
        
        # Then continue with regular polling
        loop_count = 1
        while True:
            next_poll = datetime.now() + timedelta(seconds=poll_interval)
            print(f"\n⏰ Next RSS poll at: {next_poll.strftime('%H:%M:%S')} (in 5 minutes)")
            
            await asyncio.sleep(poll_interval)
            
            loop_count += 1
            print(f"\n{'='*80}")
            print(f"🔄 RSS POLL CYCLE #{loop_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            
            await poll_rss_feeds_once(collector)
            
    except asyncio.CancelledError:
        print("\n🛑 RSS Background Poller: Shutdown requested")
        raise
    except Exception as e:
        print(f"\n❌ RSS Background Poller: Fatal error: {e}")
        import traceback
        traceback.print_exc()


async def poll_rss_feeds_once(collector):
    """Poll all RSS feeds once and update fresh flags"""
    start_time = datetime.now()
    
    # Get all active sources
    sources = list(collector.sources_collection.find({"active": True}))
    
    if not sources:
        print("⚠️  No active RSS sources found")
        return
    
    print(f"📡 Polling {len(sources)} RSS sources...")
    
    total_stats = {
        "sources_polled": 0,
        "new_articles": 0,
        "duplicates": 0,
        "errors": 0
    }
    
    # Poll each source
    for source in sources:
        stats = await collector.poll_and_store(source)
        total_stats["sources_polled"] += 1
        total_stats["new_articles"] += stats["new_articles"]
        total_stats["duplicates"] += stats["duplicates"]
        total_stats["errors"] += stats["errors"]
    
    # Mark fresh articles (< 72h)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=72)
    result_fresh = collector.articles_collection.update_many(
        {"published_dt": {"$gte": cutoff_time}},
        {"$set": {"fresh": True}}
    )
    result_archived = collector.articles_collection.update_many(
        {"published_dt": {"$lt": cutoff_time}},
        {"$set": {"fresh": False}}
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"\n✅ POLL COMPLETE:")
    print(f"   📊 New articles: {total_stats['new_articles']}")
    print(f"   🔁 Duplicates: {total_stats['duplicates']}")
    print(f"   ❌ Errors: {total_stats['errors']}")
    print(f"   📰 Fresh articles: {result_fresh.modified_count}")
    print(f"   📦 Archived: {result_archived.modified_count}")
    print(f"   ⏱️  Duration: {duration:.1f}s")


# ============================================================================
# QUERY CACHE (For Testing)
# ============================================================================
ENABLE_CACHE = os.getenv("ENABLE_QUERY_CACHE", "false").lower() == "true"

CACHED_RESPONSES = {
    "give me a visualization of india's gdp growth since 2020": {
        "response": """### India's GDP Growth Since 2020

India's GDP has shown remarkable resilience and growth since 2020, despite the challenges posed by the COVID-19 pandemic. Here's a comprehensive analysis:

#### Key Highlights
- **2020**: GDP contracted by approximately **7.3%** due to the pandemic and nationwide lockdowns
- **2021**: Strong recovery with growth of **9.1%**, driven by pent-up demand and economic stimulus
- **2022**: Continued growth at **7.2%**, supported by strong domestic consumption
- **2023**: Moderate growth of **6.7%** amid global economic headwinds
- **2024 (Projected)**: Expected growth of **6.5-7.0%**, maintaining India's position as the fastest-growing major economy

#### Growth Drivers
1. **Robust Domestic Consumption**: Strong middle-class spending power
2. **Infrastructure Investment**: Government's focus on capital expenditure
3. **Digital Economy**: Rapid digitalization and fintech adoption
4. **Manufacturing Push**: "Make in India" initiative gaining traction
5. **Services Sector**: IT and business services exports

#### Challenges
- Global economic slowdown
- Inflation pressures
- Geopolitical tensions
- Climate-related disruptions

The visualization below shows the year-over-year GDP growth trajectory, highlighting India's V-shaped recovery post-pandemic.""",
        
        "citations": [
            {
                "title": "India GDP Growth Rate - 2024 Data - Trading Economics",
                "url": "https://tradingeconomics.com/india/gdp-growth",
                "snippet": "GDP Annual Growth Rate in India averaged 6.43 percent from 1996 until 2024, reaching an all time high of 20.10 percent in the second quarter of 2021 and a record low of -25.70 percent in the second quarter of 2020.",
                "published_date": "2024-09-30",
                "score": 0.92
            },
            {
                "title": "India's GDP growth: A comprehensive analysis | World Economic Forum",
                "url": "https://www.weforum.org/agenda/2024/india-gdp-growth-analysis/",
                "snippet": "India remains the fastest-growing major economy in 2024, with GDP growth projected at 6.8% for FY 2024-25, driven by strong domestic demand and infrastructure investments.",
                "published_date": "2024-09-15",
                "score": 0.88
            },
            {
                "title": "IMF India Economic Outlook - October 2024",
                "url": "https://www.imf.org/en/Countries/IND",
                "snippet": "India's economy is projected to grow at 6.5% in 2024 and 6.3% in 2025, supported by robust domestic demand, infrastructure development, and ongoing structural reforms.",
                "published_date": "2024-10-01",
                "score": 0.85
            }
        ],
        
        "artifact": {
            "artifact_id": "india_gdp_cached_2024",
            "type": "line_chart",
            "title": "India's GDP Growth Rate (2020-2024)",
            "description": "Year-over-year GDP growth showing V-shaped recovery post-pandemic",
            "status": "ready",
            "html_url": f"{BASE_URL}/api/artifacts/india_gdp_cached_2024.html",
            "png_url": f"{BASE_URL}/api/artifacts/india_gdp_cached_2024.png",
            "created_at": "2024-10-01T12:00:00",
            "metadata": {
                "data_points": 5,
                "time_range": "2020-2024",
                "chart_type": "line",
                "y_axis": "GDP Growth (%)",
                "x_axis": "Year"
            }
        },
        
        "execution_log": [
            {"step": "conversation_manager", "message": "Processing query about India's GDP growth"},
            {"step": "strategic_planner", "message": "Planning search and visualization strategy"},
            {"step": "tool_executor", "message": "Searching for latest GDP data from Tavily"},
            {"step": "tool_executor", "message": "Creating GDP growth visualization"},
            {"step": "decision_gate", "message": "Evaluating if more information is needed"},
            {"step": "response_synthesizer", "message": "Synthesizing comprehensive analysis"},
            {"step": "artifact_decision", "message": "Generating line chart visualization"}
        ],
        
        "confidence": 0.87,
        "tools_used": ["tavily_search", "create_plotly_chart"]
    },
    
    "give me a visualization of pakistan's gdp growth since 2020": {
        "response": """### Pakistan's GDP Growth Since 2020

Pakistan's economy has faced significant challenges since 2020, navigating through the COVID-19 pandemic and subsequent economic pressures. Here's a detailed analysis:

#### Key Highlights
- **2020**: GDP contracted by approximately **1.0%** due to pandemic-related disruptions and lockdowns
- **2021**: Recovery with growth of **5.7%**, supported by agricultural sector and remittances
- **2022**: Growth moderated to **6.0%**, with continued recovery momentum
- **2023**: Significant slowdown to **0.3%** amid political instability and economic challenges
- **2024 (Projected)**: Expected growth of **2.5-3.0%**, as reforms and stabilization efforts take effect

#### Growth Drivers
1. **Agricultural Sector**: Contributes significantly to GDP, weather-dependent
2. **Remittances**: Critical source of foreign exchange and domestic consumption
3. **Textile Industry**: Major export sector showing resilience
4. **Services Sector**: Gradual recovery in retail and transportation
5. **IMF Program**: Economic stabilization measures being implemented

#### Challenges
- High inflation and currency depreciation
- Political instability affecting investor confidence
- Energy sector constraints
- External debt management
- Flood impacts (2022) on agriculture

The visualization below shows Pakistan's GDP growth trajectory, highlighting the volatility and recovery patterns since 2020.""",
        
        "citations": [
            {
                "title": "GDP growth (annual %) - Pakistan",
                "url": "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?locations=PK",
                "snippet": "GDP growth (annual %) - Pakistan from The World Bank: Data",
                "published_date": "2024-09-28",
                "score": 0.91
            },
            {
                "title": "Pakistan GDP Growth Rate | Historical Chart & Data",
                "url": "https://tradingeconomics.com/pakistan/gdp-growth",
                "snippet": "GDP Annual Growth Rate in Pakistan averaged 4.80 percent from 1952 until 2024, with significant variations due to economic and political factors.",
                "published_date": "2024-09-25",
                "score": 0.89
            },
            {
                "title": "Pakistan GDP | Historical Chart & Data",
                "url": "https://www.macrotrends.net/countries/PAK/pakistan/gdp-gross-domestic-product",
                "snippet": "Pakistan GDP was $374.74 billion in 2023, showing the economic scale and recent performance of the economy.",
                "published_date": "2024-09-20",
                "score": 0.86
            }
        ],
        
        "artifact": {
            "artifact_id": "pakistan_gdp_cached_2024",
            "type": "line_chart",
            "title": "Pakistan's GDP Growth Rate (2020-2024)",
            "description": "Year-over-year GDP growth showing recovery and challenges",
            "status": "ready",
            "html_url": f"{BASE_URL}/api/artifacts/pakistan_gdp_cached_2024.html",
            "png_url": f"{BASE_URL}/api/artifacts/pakistan_gdp_cached_2024.png",
            "created_at": "2024-10-01T12:00:00",
            "metadata": {
                "data_points": 5,
                "time_range": "2020-2024",
                "chart_type": "line",
                "y_axis": "GDP Growth (%)",
                "x_axis": "Year"
            }
        },
        
        "execution_log": [
            {"step": "conversation_manager", "message": "Processing query about Pakistan's GDP growth"},
            {"step": "strategic_planner", "message": "Planning search and visualization strategy"},
            {"step": "tool_executor", "message": "Searching for latest GDP data from Tavily"},
            {"step": "tool_executor", "message": "Creating GDP growth visualization"},
            {"step": "decision_gate", "message": "Evaluating if more information is needed"},
            {"step": "response_synthesizer", "message": "Synthesizing comprehensive analysis"},
            {"step": "artifact_decision", "message": "Generating line chart visualization"}
        ],
        
        "confidence": 0.83,
        "tools_used": ["tavily_search", "create_plotly_chart"]
    }
}

# Import MongoDB service
try:
    from services.mongo_service import mongo_service as mongo
    mongo_service = mongo
    print("🗄️  MongoDB service imported")
except ImportError as e:
    print(f"⚠️  MongoDB service not available: {e}")
    mongo_service = None

# Import S3 service
try:
    from services.s3_service import s3_service
    print("🗄️  S3 service imported")
except ImportError as e:
    print(f"⚠️  S3 service not available: {e}")
    s3_service = None

# Import Graph Visualization service
try:
    from services.graph_service import graph_service
    print("🗄️  Graph Visualization service imported")
except ImportError as e:
    print(f"⚠️  Graph Visualization service not available: {e}")
    graph_service = None


# ============================================================================
# Request/Response Models
# ============================================================================

class AnalysisRequest(BaseModel):
    """Request model for political analysis queries"""
    query: str
    user_session: Optional[str] = None
    create_artifact: Optional[bool] = None  # Override auto-detection


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    success: bool
    session_id: str
    query: str
    response: str
    citations: list[Dict[str, Any]]
    confidence: float
    tools_used: list[str]
    iterations: int
    execution_log: list[Dict[str, Any]]
    artifact: Optional[Dict[str, Any]] = None
    sub_agent_artifacts: Optional[Dict[str, list[Dict[str, Any]]]] = None  # NEW: artifacts from sub-agents
    processing_time_ms: Optional[int] = None
    errors: Optional[list[str]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    agent_status: str
    timestamp: str


# ============================================================================
# Investigation Models (for Investigative Journalist)
# ============================================================================

class CreateInvestigationRequest(BaseModel):
    """Request to create a new investigation"""
    query: str
    title: Optional[str] = None
    max_iterations: int = 20


class ContinueInvestigationRequest(BaseModel):
    """Request to continue an existing investigation"""
    additional_iterations: int = 10


class UpdateInvestigationRequest(BaseModel):
    """Request to update investigation fields"""
    title: Optional[str] = None
    status: Optional[str] = None  # active, paused, completed, archived


class InvestigationResponse(BaseModel):
    """Response for investigation operations"""
    success: bool
    investigation_id: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

def _sanitize_for_json(obj):
    """Convert MongoDB ObjectIds and other non-serializable types to strings"""
    if hasattr(obj, '__dict__'):
        return {k: _sanitize_for_json(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(item) for item in obj]
    elif type(obj).__name__ == 'ObjectId':  # MongoDB ObjectId
        return str(obj)
    else:
        return obj


@app.on_event("startup")
async def startup_event():
    """Initialize the political analyst agent and database on startup"""
    global agent, mongo_service, rss_poller_task
    
    print("🚀 Starting Political Analyst Workbench Backend...")
    print("=" * 70)
    
    # Debug environment variables
    print("🔍 Environment Check:")
    print(f"   TAVILY_API_KEY: {'✅ SET' if os.getenv('TAVILY_API_KEY') else '❌ MISSING'}")
    print(f"   OPENAI_API_KEY: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ MISSING'}")
    print(f"   LANGSMITH_API_KEY: {'✅ SET' if os.getenv('LANGSMITH_API_KEY') else '⚠️  OPTIONAL'}")
    print(f"   MONGODB_CONNECTION_STRING: {'✅ SET' if os.getenv('MONGODB_CONNECTION_STRING') else '⚠️  OPTIONAL'}")
    
    # Validate configuration
    if not Config.validate_config():
        raise RuntimeError("Invalid configuration. Please check your API keys.")
    
    # Initialize MongoDB
    if mongo_service:
        try:
            await mongo_service.connect()
            print("✅ MongoDB connected successfully")
        except Exception as e:
            print(f"⚠️  MongoDB connection failed (continuing without database): {e}")
            mongo_service = None
    
    # Initialize agent
    try:
        agent = MasterPoliticalAnalyst()
        print("✅ Political Analyst Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        raise
    
    # Start RSS background poller (non-blocking)
    if mongo_service:
        try:
            rss_poller_task = asyncio.create_task(run_rss_background_poller())
            print("✅ RSS Background Poller started (polling every 5 minutes)")
        except Exception as e:
            print(f"⚠️  RSS Poller failed to start: {e}")
    else:
        print("⚠️  RSS Poller skipped (MongoDB not available)")
    
    print("=" * 70)
    print("🎯 Backend server ready!")
    print(f"📍 CORS Origins: {cors_origins}")
    print(f"📊 Database: {'MongoDB Atlas' if mongo_service else 'File System Only'}")
    print(f"🗄️  Query Cache: {'ENABLED ✅' if ENABLE_CACHE else 'DISABLED ❌'}")
    if ENABLE_CACHE:
        print(f"   Cached queries: {len(CACHED_RESPONSES)}")
    print(f"📰 RSS Poller: {'RUNNING ✅' if rss_poller_task else 'DISABLED ❌'}")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mongo_service, rss_poller_task
    
    print("\n🛑 Shutting down Political Analyst Workbench Backend...")
    
    # Stop RSS poller
    if rss_poller_task and not rss_poller_task.done():
        print("🛑 Stopping RSS Background Poller...")
        rss_poller_task.cancel()
        try:
            await rss_poller_task
        except asyncio.CancelledError:
            print("✅ RSS Poller stopped")
    
    if mongo_service:
        try:
            await mongo_service.disconnect()
            print("✅ MongoDB disconnected")
        except Exception as e:
            print(f"⚠️  MongoDB disconnect error: {e}")


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agent_status="ready" if agent else "not_initialized",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# Mount static files for serving artifacts locally
# This allows artifacts to be accessed via /artifacts/... URLs
artifacts_dir = os.path.join(os.path.dirname(__file__), "langgraph_master_agent", "sub_agents", "investigative_journalist", "artifacts")
os.makedirs(artifacts_dir, exist_ok=True)
app.mount("/artifacts/investigative_journalist", StaticFiles(directory=artifacts_dir), name="artifacts")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for AWS/load balancers"""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agent_status="ready" if agent else "not_initialized",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# ============================================================================
# Analysis Endpoints
# ============================================================================

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_query(request: AnalysisRequest):
    """
    Process a political analysis query using the Master Agent
    
    Returns comprehensive analysis with optional artifact generation
    """
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if len(request.query) > 2000:
        raise HTTPException(status_code=400, detail="Query too long (max 2000 characters)")
    
    start_time = time.time()
    
    try:
        # Process query through master agent (it creates its own session_id)
        result = await agent.process_query(request.query)
        
        processing_time = int((time.time() - start_time) * 1000)
        agent_session_id = result.get("session_id", f"session_{int(time.time())}")
        
        # Save results to MongoDB (if available)
        if mongo_service:
            try:
                # Create session with the agent's session_id
                from services.mongo_service import AnalysisSession
                session = AnalysisSession(
                    session_id=agent_session_id,
                    query=request.query,
                    user_session=request.user_session,
                    status="completed",
                    completed_at=datetime.now(timezone.utc),
                    processing_time_ms=processing_time,
                    response=result.get("response", ""),
                    confidence=result.get("confidence", 0.0),
                    citations=result.get("citations", []),
                    tools_used=result.get("tools_used", []),
                    iterations=result.get("iterations", 0),
                    artifact_id=result.get("artifact", {}).get("artifact_id") if result.get("artifact") else None
                )
                
                await mongo_service.db.analysis_sessions.insert_one(session.to_dict())
                
                # Save execution log
                await mongo_service.save_execution_log(
                    session_id=agent_session_id,
                    execution_log=result.get("execution_log", [])
                )
                
                # Save artifact metadata (if artifact was created)
                if result.get("artifact"):
                    from services.mongo_service import ArtifactMetadata
                    artifact = result["artifact"]
                    artifact_meta = ArtifactMetadata(
                        artifact_id=artifact["artifact_id"],
                        session_id=agent_session_id,
                        type=artifact["type"],
                        title=artifact.get("title", ""),
                        data=artifact.get("data", {}),
                        query=request.query,
                        html_path=artifact.get("html_path", ""),
                        png_path=artifact.get("png_path", ""),
                        html_size_bytes=os.path.getsize(artifact["html_path"]) if os.path.exists(artifact["html_path"]) else 0,
                        png_size_bytes=os.path.getsize(artifact["png_path"]) if os.path.exists(artifact["png_path"]) else 0,
                        s3_html_key=artifact.get("s3_html_key"),      # S3 key (permanent)
                        s3_png_key=artifact.get("s3_png_key"),        # S3 key (permanent)
                        s3_html_url=artifact.get("s3_html_url"),      # Presigned URL (24h)
                        s3_png_url=artifact.get("s3_png_url"),        # Presigned URL (24h)
                        storage=artifact.get("storage", "local")
                    )
                    await mongo_service.save_artifact_metadata(artifact_meta)
                
                print(f"✅ Session {agent_session_id} saved to MongoDB with {len(result.get('execution_log', []))} execution steps")
                
            except Exception as db_error:
                print(f"⚠️  Failed to save to MongoDB: {db_error}")
                import traceback
                traceback.print_exc()
                # Continue without database
        
        # Sanitize result to remove MongoDB ObjectIds
        result = _sanitize_for_json(result)
        
        # DEBUG: Artifact extraction
        print("\n" + "=" * 70)
        print("🔍 HTTP ARTIFACT EXTRACTION DEBUG")
        print("=" * 70)
        print(f"result.keys(): {list(result.keys())}")
        
        # Extract sub-agent artifacts (e.g., from sentiment analyzer)
        sub_agent_artifacts = {}
        sub_agent_results = result.get("sub_agent_results", {})
        
        print(f"sub_agent_results present: {bool(sub_agent_results)}")
        
        if sub_agent_results:
            print(f"Sub-agents in result: {list(sub_agent_results.keys())}")
            
            # Extract artifacts from sentiment analyzer
            if "sentiment_analysis" in sub_agent_results:
                print("✅ Found sentiment_analysis in sub_agent_results")
                sentiment_result = sub_agent_results["sentiment_analysis"]
                print(f"   Success: {sentiment_result.get('success')}")
                print(f"   Has data: {bool(sentiment_result.get('data'))}")
                
                if sentiment_result.get("success") and sentiment_result.get("data", {}).get("artifacts"):
                    artifacts_list = sentiment_result["data"]["artifacts"]
                    print(f"   ✅ Artifacts found: {len(artifacts_list)}")
                    for i, art in enumerate(artifacts_list, 1):
                        print(f"      {i}. {art.get('type')}: {art.get('artifact_id')}")
                    sub_agent_artifacts["sentiment_analysis"] = artifacts_list
                else:
                    print("   ❌ No artifacts in sentiment_analysis data")
            else:
                print("❌ sentiment_analysis NOT in sub_agent_results")
            
            # Add more sub-agents here as they're implemented
            # if "fact_checker" in sub_agent_results: ...
            # if "media_bias_detector" in sub_agent_results: ...
        else:
            print("❌ No sub_agent_results at all")
        
        print(f"\nFinal sub_agent_artifacts dict: {bool(sub_agent_artifacts)}")
        if sub_agent_artifacts:
            for agent, arts in sub_agent_artifacts.items():
                print(f"  {agent}: {len(arts)} artifacts")
        print("=" * 70 + "\n")
        
        return AnalysisResponse(
            success=True,
            session_id=agent_session_id,
            query=request.query,
            response=result.get("response", ""),
            citations=result.get("citations", []),
            confidence=result.get("confidence", 0.0),
            tools_used=result.get("tools_used", []),
            iterations=result.get("iterations", 0),
            execution_log=result.get("execution_log", []),
            artifact=result.get("artifact"),
            sub_agent_artifacts=sub_agent_artifacts or None,  # Will be populated when master agent returns sub_agent_results
            processing_time_ms=processing_time,
            errors=result.get("errors", [])
        )
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ============================================================================
# Artifact Endpoints
# ============================================================================

@app.get("/api/artifacts/{artifact_id}.html")
async def get_artifact_html(artifact_id: str):
    """Retrieve artifact HTML file"""
    print(f"📊 Artifact HTML requested: {artifact_id}")
    
    # Artifacts are stored in artifacts/ directory relative to backend_server/
    file_path = f"artifacts/{artifact_id}.html"
    
    # Also check sentiment analyzer artifacts folder
    if not os.path.exists(file_path):
        alt_path = f"langgraph_master_agent/sub_agents/sentiment_analyzer/artifacts/{artifact_id}.html"
        if os.path.exists(alt_path):
            print(f"✅ Found artifact in sentiment analyzer folder: {alt_path}")
            file_path = alt_path
        else:
            print(f"❌ Artifact not found: {artifact_id}")
            raise HTTPException(status_code=404, detail="Artifact not found")
    
    print(f"✅ Serving artifact from: {file_path}")
    return FileResponse(
        file_path,
        media_type="text/html",
        headers={
            "Content-Disposition": "inline"  # Display in browser, not download
        }
    )


@app.get("/api/artifacts/{artifact_id}.png")
async def get_artifact_png(artifact_id: str):
    """Retrieve artifact PNG file"""
    # Artifacts are stored in artifacts/ directory relative to backend_server/
    file_path = f"artifacts/{artifact_id}.png"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        filename=f"{artifact_id}.png"
    )


@app.get("/api/artifacts/{artifact_id}.json")
async def get_artifact_json(artifact_id: str):
    """Retrieve artifact JSON file (data exports)"""
    print(f"📊 Artifact JSON requested: {artifact_id}")
    
    # Check main artifacts directory
    file_path = f"artifacts/{artifact_id}.json"
    
    # Also check sentiment analyzer artifacts folder
    if not os.path.exists(file_path):
        alt_path = f"langgraph_master_agent/sub_agents/sentiment_analyzer/artifacts/{artifact_id}.json"
        if os.path.exists(alt_path):
            print(f"✅ Found JSON artifact in sentiment analyzer folder: {alt_path}")
            file_path = alt_path
        else:
            print(f"❌ JSON artifact not found: {artifact_id}")
            raise HTTPException(status_code=404, detail="JSON artifact not found")
    
    print(f"✅ Serving JSON artifact from: {file_path}")
    return FileResponse(
        file_path,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={artifact_id}.json"  # Force download for JSON
        }
    )


@app.get("/api/artifacts/{artifact_id}/presigned-urls")
async def get_artifact_presigned_urls(artifact_id: str, expiration: int = 3600):
    """
    Generate fresh presigned URLs for an S3-stored artifact
    
    Args:
        artifact_id: Artifact identifier
        expiration: URL expiration time in seconds (default 1 hour)
    
    Returns:
        JSON with presigned URLs for HTML and PNG
    """
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    if not s3_service:
        raise HTTPException(status_code=503, detail="S3 service not available")
    
    try:
        # Get artifact from MongoDB
        artifact_meta = await mongo_service.get_artifact(artifact_id)
        
        if not artifact_meta:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        if artifact_meta.get('storage') != 's3':
            raise HTTPException(
                status_code=400,
                detail="Artifact is not stored in S3. Use /api/artifacts/{id}.html or .png endpoints."
            )
        
        # Get S3 keys
        html_key = artifact_meta.get('s3_html_key')
        png_key = artifact_meta.get('s3_png_key')
        
        if not html_key or not png_key:
            raise HTTPException(status_code=500, detail="S3 keys not found in artifact metadata")
        
        # Generate fresh presigned URLs
        html_url = s3_service.get_presigned_url(html_key, expiration=expiration)
        png_url = s3_service.get_presigned_url(png_key, expiration=expiration)
        
        if not html_url or not png_url:
            raise HTTPException(status_code=500, detail="Failed to generate presigned URLs")
        
        return {
            "artifact_id": artifact_id,
            "storage": "s3",
            "html_url": html_url,
            "png_url": png_url,
            "expires_in_seconds": expiration,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URLs: {str(e)}")


# ============================================================================
# Graph Visualization Endpoints
# ============================================================================

@app.get("/api/graph/structure")
async def get_graph_structure():
    """
    Get static graph structure (nodes and edges) for visualization
    
    Returns JSON with:
    - nodes: List of all graph nodes with metadata
    - edges: List of all edges (connections between nodes)
    - metadata: Graph-level information
    
    Frontend can use this with D3.js, Cytoscape.js, React Flow, etc.
    """
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")
    
    try:
        graph_data = graph_service.get_static_graph_structure()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get graph structure: {str(e)}")


@app.get("/api/graph/execution/{session_id}")
async def get_execution_graph(session_id: str):
    """
    Get graph with execution state for a specific session
    
    Args:
        session_id: Session identifier from conversation
    
    Returns JSON with:
    - nodes: Nodes with execution state (executed, timestamp, status)
    - edges: Edges with traversal information
    - execution_metadata: Timing, iterations, etc.
    
    Use this to show which path was taken for a specific conversation
    """
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")
    
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        # Get session from MongoDB to retrieve execution log
        session = await mongo_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Get execution log
        execution_log_doc = await mongo_service.get_execution_log(session_id)
        
        if not execution_log_doc:
            # Try to get from session itself
            execution_log = []
        else:
            execution_log = execution_log_doc.get("steps", [])
        
        # Generate graph with execution state
        graph_data = graph_service.get_execution_graph(session_id, execution_log)
        
        return graph_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get execution graph: {str(e)}")


@app.get("/api/graph/mermaid")
async def get_mermaid_diagram():
    """
    Get Mermaid diagram text representation
    
    Returns:
        Text content that can be rendered with Mermaid.js
    
    Note: Use /api/graph/structure for interactive visualizations
    """
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")
    
    try:
        mermaid_text = graph_service.get_mermaid_diagram()
        return {
            "format": "mermaid",
            "diagram": mermaid_text,
            "viewer_url": "https://mermaid.live"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Mermaid diagram: {str(e)}")


# ============================================================================
# Debug/Test Endpoints
# ============================================================================

@app.get("/api/test-sentiment-artifacts")
async def test_sentiment_artifacts():
    """Test endpoint to verify sentiment analyzer creates artifacts"""
    from langgraph_master_agent.tools.sub_agent_caller import SubAgentCaller
    
    print("\n" + "=" * 70)
    print("🧪 TEST ENDPOINT: Testing Sentiment Analyzer Artifacts")
    print("=" * 70)
    
    try:
        caller = SubAgentCaller()
        result = await caller.call_sentiment_analyzer(
            query="test nuclear policy",
            countries=["US", "UK"]
        )
        
        print(f"Sub-agent success: {result.get('success')}")
        
        if result.get("success"):
            data = result.get("data", {})
            artifacts = data.get("artifacts", [])
            
            print(f"Artifacts returned: {len(artifacts)}")
            for i, art in enumerate(artifacts, 1):
                print(f"  {i}. {art.get('type')}: {art.get('artifact_id')}")
            
            print("=" * 70 + "\n")
            
            return {
                "success": True,
                "artifacts_count": len(artifacts),
                "artifacts": [
                    {
                        "artifact_id": a.get("artifact_id"),
                        "type": a.get("type"),
                        "title": a.get("title"),
                        "html_path": a.get("html_path")
                    }
                    for a in artifacts
                ]
            }
        else:
            print(f"❌ Sub-agent failed: {result.get('error')}")
            print("=" * 70 + "\n")
            return {"success": False, "error": result.get("error")}
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70 + "\n")
        return {"success": False, "error": str(e)}


@app.get("/api/artifacts/list")
async def list_recent_artifacts():
    """Debug endpoint to list recently generated artifacts"""
    import glob
    
    artifact_dir = "langgraph_master_agent/sub_agents/sentiment_analyzer/artifacts"
    
    if not os.path.exists(artifact_dir):
        return {"artifacts": [], "error": "Artifact directory not found"}
    
    # Get all HTML and JSON files
    html_files = glob.glob(f"{artifact_dir}/*.html")
    json_files = glob.glob(f"{artifact_dir}/*.json")
    
    all_files = html_files + json_files
    all_files.sort(key=os.path.getmtime, reverse=True)
    
    artifacts = []
    for file_path in all_files[:20]:  # Last 20 artifacts
        filename = os.path.basename(file_path)
        artifact_id = os.path.splitext(filename)[0]
        
        artifacts.append({
            "artifact_id": artifact_id,
            "filename": filename,
            "size": os.path.getsize(file_path),
            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            "url": f"{BASE_URL}/api/artifacts/{filename}"
        })
    
    return {"artifacts": artifacts, "count": len(artifacts)}


# ============================================================================
# WebSocket Endpoint for Streaming
# ============================================================================

@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    WebSocket endpoint for streaming analysis updates
    
    Client sends:
    {
        "type": "query",
        "data": {"query": "...", "use_citations": true},
        "message_id": "msg_123"
    }
    
    Server streams:
    - {"type": "connected", "data": {...}, "timestamp": "..."}
    - {"type": "session_start", "data": {...}, "timestamp": "..."}
    - {"type": "status", "data": {...}, "timestamp": "..."}
    - {"type": "content", "data": {...}, "timestamp": "..."}
    - {"type": "citation", "data": {...}, "timestamp": "..."}
    - {"type": "artifact", "data": {...}, "timestamp": "..."}
    - {"type": "complete", "data": {...}, "timestamp": "..."}
    - {"type": "error", "data": {...}, "timestamp": "..."}
    """
    global agent, mongo_service
    
    await websocket.accept()
    
    # Helper function to send formatted messages
    def create_message(msg_type: str, data: Any, message_id: str = None) -> Dict[str, Any]:
        msg = {
            "type": msg_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if message_id:
            msg["message_id"] = message_id
        return msg
    
    # Create session_id ONCE per WebSocket connection
    session_id = f"session_{int(time.time())}_{os.urandom(4).hex()}"
    current_message_id = None
    conversation_history = []  # Store conversation across queries
    
    try:
        # Send connected confirmation
        await websocket.send_json(create_message(
            "connected",
            {
                "message": "WebSocket connection established",
                "server_version": "1.0.0",
                "session_id": session_id
            }
        ))
        
        print(f"🔌 New WebSocket connection: {session_id}")
        
        # Main message loop
        while True:
            try:
                # Receive message from client
                client_message = await websocket.receive_json()
                msg_type = client_message.get("type")
                msg_data = client_message.get("data", {})
                current_message_id = client_message.get("message_id")
                
                if msg_type == "query":
                    # Extract query parameters
                    query = msg_data.get("query", "")
                    use_citations = msg_data.get("use_citations", True)
                    
                    if not query:
                        await websocket.send_json(create_message(
                            "error",
                            {"message": "Query is required"},
                            current_message_id
                        ))
                        continue
                    
                    # Send session start (same session_id throughout connection)
                    await websocket.send_json(create_message(
                        "session_start",
                        {
                            "session_id": session_id,
                            "query": query,
                            "message": f"Starting analysis (query {len(conversation_history) + 1})...",
                            "conversation_length": len(conversation_history)
                        },
                        current_message_id
                    ))
                    
                    # Send status: Analyzing query
                    await websocket.send_json(create_message(
                        "status",
                        {
                            "step": "analyzing",
                            "message": "Analyzing your query...",
                            "progress": 0.1
                        },
                        current_message_id
                    ))
                    
                    # Check cache first (if enabled)
                    cached_result = None
                    query_lower = query.lower().strip()
                    
                    if ENABLE_CACHE and query_lower in CACHED_RESPONSES:
                        print(f"💾 Using cached response for query: '{query}'")
                        cached_result = CACHED_RESPONSES[query_lower].copy()
                        result = cached_result
                    else:
                        # Process query with agent (with 180s timeout for S3 uploads)
                        try:
                            print(f"⏱️  Starting agent.process_query() with 180s timeout...")
                            print(f"   📚 Conversation history: {len(conversation_history)} messages")
                            result = await asyncio.wait_for(
                                agent.process_query(
                                    query, 
                                    conversation_history=conversation_history.copy(),
                                    session_id=session_id
                                ),
                                timeout=180.0
                            )
                            print(f"✅ Agent completed successfully")
                            
                            # Save to MongoDB (if available)
                            if mongo_service:
                                try:
                                    from services.mongo_service import AnalysisSession
                                    agent_session_id = result.get("session_id", session_id)
                                    
                                    session = AnalysisSession(
                                        session_id=agent_session_id,
                                        query=query,
                                        user_session=current_message_id or "websocket",
                                        response=result.get("response", ""),
                                        confidence=result.get("confidence", 0.0),
                                        processing_time_ms=0,  # WebSocket doesn't track this
                                        tools_used=result.get("tools_used", []),
                                        iterations=result.get("iterations", 0),
                                        artifact_id=result.get("artifact", {}).get("artifact_id") if result.get("artifact") else None
                                    )
                                    
                                    await mongo_service.db.analysis_sessions.insert_one(session.to_dict())
                                    
                                    # Save execution log
                                    await mongo_service.save_execution_log(
                                        session_id=agent_session_id,
                                        execution_log=result.get("execution_log", [])
                                    )
                                    
                                    print(f"✅ Session {agent_session_id} saved to MongoDB with {len(result.get('execution_log', []))} execution steps")
                                except Exception as db_error:
                                    print(f"⚠️  Failed to save to MongoDB: {db_error}")
                        
                        except asyncio.TimeoutError:
                            print(f"❌ Agent timed out after 90s")
                            await websocket.send_json(create_message(
                                "error",
                                {
                                    "message": "Query processing timed out after 90 seconds. Please try a simpler query.",
                                    "error_type": "timeout"
                                },
                                current_message_id
                            ))
                            continue
                        except Exception as e:
                            print(f"❌ Agent error: {e}")
                            import traceback
                            traceback.print_exc()
                            await websocket.send_json(create_message(
                                "error",
                                {
                                    "message": f"Agent error: {str(e)}",
                                    "error_type": type(e).__name__
                                },
                                current_message_id
                            ))
                            continue
                    
                    # Stream execution log as status updates
                    for i, log_entry in enumerate(result.get("execution_log", [])):
                        progress = 0.1 + (0.7 * (i + 1) / len(result.get("execution_log", [1])))
                        await websocket.send_json(create_message(
                            "status",
                            {
                                "step": log_entry.get("step", "processing"),
                                "message": log_entry.get("message", "Processing..."),
                                "progress": progress
                            },
                            current_message_id
                        ))
                        await asyncio.sleep(0.05)  # Small delay for UX
                    
                    # Send content (AI response)
                    response_text = result.get("response", "")
                    if response_text:
                        # Stream content in chunks for better UX
                        chunk_size = 50
                        for i in range(0, len(response_text), chunk_size):
                            chunk = response_text[i:i+chunk_size]
                            await websocket.send_json(create_message(
                                "content",
                                {
                                    "content": chunk,
                                    "is_complete": i + chunk_size >= len(response_text)
                                },
                                current_message_id
                            ))
                            await asyncio.sleep(0.02)
                    
                    # Send citations if available
                    if use_citations and result.get("citations"):
                        for citation in result.get("citations", []):
                            await websocket.send_json(create_message(
                                "citation",
                                citation,
                                current_message_id
                            ))
                    
                    # Send artifact if available
                    if result.get("artifact"):
                        artifact_data = result["artifact"]
                        
                        # Handle both S3 and local storage URLs
                        html_url = (artifact_data.get("s3_html_url") or 
                                   artifact_data.get("html_url") or
                                   f"{BASE_URL}/api/artifacts/{artifact_data.get('artifact_id')}.html")
                        
                        # Only include png_url if it exists in artifact_data
                        artifact_message = {
                            "artifact_id": artifact_data.get("artifact_id"),
                            "type": artifact_data.get("type", "chart"),
                            "title": artifact_data.get("title", "Analysis Result"),
                            "html_url": html_url,
                            "storage": artifact_data.get("storage", "local"),
                            "metadata": artifact_data.get("metadata", {})
                        }
                        
                        # Add png_url only if it actually exists
                        if artifact_data.get("s3_png_url") or artifact_data.get("png_url"):
                            artifact_message["png_url"] = (artifact_data.get("s3_png_url") or 
                                                          artifact_data.get("png_url"))
                        
                        await websocket.send_json(create_message(
                            "artifact",
                            artifact_message,
                            current_message_id
                        ))
                    
                    # DEBUG: Check what we got from master agent
                    print("\n" + "=" * 70)
                    print("🔍 WEBSOCKET ARTIFACT DEBUG CHECKPOINT")
                    print("=" * 70)
                    print(f"result.keys(): {list(result.keys())}")
                    print(f"result.get('artifact'): {bool(result.get('artifact'))}")
                    print(f"result.get('sub_agent_results') exists: {'sub_agent_results' in result}")
                    
                    # Extract sub-agent artifacts (same logic as HTTP endpoint - Oct 2, 2025)
                    sub_agent_artifacts = {}
                    sub_agent_results = result.get("sub_agent_results", {})
                    
                    if sub_agent_results:
                        # Extract artifacts from sentiment analyzer
                        if "sentiment_analysis" in sub_agent_results:
                            sentiment_result = sub_agent_results["sentiment_analysis"]
                            if sentiment_result.get("success") and sentiment_result.get("data", {}).get("artifacts"):
                                sub_agent_artifacts["sentiment_analysis"] = sentiment_result["data"]["artifacts"]
                                print(f"✅ Extracted {len(sentiment_result['data']['artifacts'])} artifacts from sentiment_analysis")
                        
                        # Add other sub-agents here as they're developed
                        # if "other_agent" in sub_agent_results: ...
                    
                    print(f"Total sub_agent_artifacts extracted: {sum(len(v) if isinstance(v, list) else 0 for v in sub_agent_artifacts.values())}")
                    print(f"sub_agent_artifacts after extraction: {bool(sub_agent_artifacts)}")
                    
                    if sub_agent_artifacts:
                        print(f"✅ Found sub_agent_artifacts with {len(sub_agent_artifacts)} agent(s)")
                        for agent_name in sub_agent_artifacts.keys():
                            artifacts_list = sub_agent_artifacts[agent_name]
                            artifact_count = len(artifacts_list) if isinstance(artifacts_list, list) else 0
                            print(f"   Agent '{agent_name}': {artifact_count} artifacts")
                    else:
                        print("❌ sub_agent_artifacts is EMPTY or missing!")
                        print("   Checking if sub_agent_results exists in result...")
                        if 'sub_agent_results' in result:
                            print(f"   ✓ sub_agent_results found: {list(result['sub_agent_results'].keys())}")
                        else:
                            print("   ✗ sub_agent_results NOT in result")
                    print("=" * 70 + "\n")
                    
                    # Send master agent artifact first (if it exists)
                    if result.get("artifact"):
                        artifact_data = result["artifact"]
                        if artifact_data and artifact_data.get("artifact_id"):
                            # Handle both S3 and local storage URLs
                            html_url = (artifact_data.get("s3_html_url") or 
                                       artifact_data.get("html_url") or
                                       f"{BASE_URL}/api/artifacts/{artifact_data.get('artifact_id')}.html")
                            
                            # Get PNG URL (prioritize for fast loading)
                            png_url = (artifact_data.get("s3_png_url") or 
                                      artifact_data.get("png_url") or
                                      f"{BASE_URL}/api/artifacts/{artifact_data.get('artifact_id')}.png")
                            
                            # Build artifact message with PNG prioritized
                            artifact_message = {
                                "artifact_id": artifact_data.get("artifact_id"),
                                "type": artifact_data.get("type", "chart"),
                                "title": artifact_data.get("title", "Visualization"),
                                "png_url": png_url,  # PNG first for instant display
                                "html_url": html_url,  # HTML for interactive fallback
                                "storage": artifact_data.get("storage", "local"),
                                "metadata": artifact_data.get("metadata", {}),
                                "source": "master_agent"
                            }
                            
                            await websocket.send_json(create_message(
                                "artifact",
                                artifact_message,
                                current_message_id
                            ))
                            
                            print(f"📊 Sent MASTER AGENT artifact to frontend: {artifact_data.get('artifact_id')} ({artifact_data.get('type')})")
                    
                    # Send sub-agent artifacts
                    if sub_agent_artifacts:
                        for agent_name, artifacts_list in sub_agent_artifacts.items():
                            if isinstance(artifacts_list, list):
                                for artifact_data in artifacts_list:
                                    # Safety check: skip malformed artifacts
                                    if not artifact_data or not artifact_data.get("artifact_id"):
                                        print(f"⚠️  Skipping malformed artifact from {agent_name}")
                                        continue
                                    
                                    # Handle both S3 and local storage URLs
                                    html_url = (artifact_data.get("s3_html_url") or 
                                               artifact_data.get("html_url") or
                                               f"{BASE_URL}/api/artifacts/{artifact_data.get('artifact_id')}.html")
                                    
                                    # Get PNG URL (prioritize for fast loading)
                                    png_url = (artifact_data.get("s3_png_url") or 
                                              artifact_data.get("png_url") or
                                              f"{BASE_URL}/api/artifacts/{artifact_data.get('artifact_id')}.png")
                                    
                                    # Build artifact message with PNG prioritized
                                    artifact_message = {
                                        "artifact_id": artifact_data.get("artifact_id"),
                                        "type": artifact_data.get("type", "chart"),
                                        "title": artifact_data.get("title", "Visualization"),
                                        "png_url": png_url,  # PNG first for instant display
                                        "html_url": html_url,  # HTML for interactive fallback
                                        "storage": artifact_data.get("storage", "local"),
                                        "metadata": artifact_data.get("metadata", {}),
                                        "source": agent_name
                                    }
                                    
                                    await websocket.send_json(create_message(
                                        "artifact",
                                        artifact_message,
                                        current_message_id
                                    ))
                                    
                                    print(f"📊 Sent SUB-AGENT artifact to frontend: {artifact_data.get('artifact_id')} ({artifact_data.get('type')})")
                    
                        # Debug: Log total artifacts sent
                        artifact_count = 1 if result.get("artifact") else 0
                        for agent_name, artifacts_list in sub_agent_artifacts.items():
                            if isinstance(artifacts_list, list):
                                artifact_count += len(artifacts_list)
                        print(f"📊 Total artifacts sent to frontend: {artifact_count}")
                    
                    # Send complete
                    await websocket.send_json(create_message(
                        "complete",
                        {
                            "session_id": session_id,
                "confidence": result.get("confidence", 0.0),
                            "total_citations": len(result.get("citations", [])),
                            "has_artifact": bool(result.get("artifact")),
                            "message": "Analysis complete!"
                        },
                        current_message_id
                    ))
                    
                    # Store conversation in history for context
                    conversation_history.append({
                        "role": "user",
                        "content": query,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    conversation_history.append({
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
                    # Keep only last 10 messages (5 turns)
                    if len(conversation_history) > 10:
                        conversation_history = conversation_history[-10:]
                    
                    print(f"💾 Conversation history updated: {len(conversation_history)} messages")
                    
                elif msg_type == "cancel":
                    # Handle cancellation (future enhancement)
                    await websocket.send_json(create_message(
                        "status",
                        {
                            "step": "cancelled",
                            "message": "Query cancelled by user"
                        },
                        current_message_id
                    ))
                    
                else:
                    # Unknown message type
                    await websocket.send_json(create_message(
                        "error",
                        {"message": f"Unknown message type: {msg_type}"},
                        current_message_id
                    ))
            
            except WebSocketDisconnect:
                print("WebSocket client disconnected")
                break
                
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json(create_message(
                "error",
                {
                    "message": str(e),
                    "error_type": type(e).__name__
                },
                current_message_id
            ))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


# ============================================================================
# Live Political Monitor API
# ============================================================================
# Migration Date: October 19, 2025
# 
# DEFAULT: RSS-based monitor (/api/live-monitor/explosive-topics)
#   - 99.4% cheaper ($0.00003 per query vs $0.005)
#   - 60% faster (2-5s vs 8-15s response time)
#   - Real-time RSS feed monitoring (48-hour window)
#   - UI-compatible format (backward compatible)
# 
# BACKUP: Tavily-based monitor (/api/live-monitor/explosive-topics-tavily)
#   - Original Tavily implementation preserved for fallback/comparison
#   - Can be restored as default by swapping endpoint names
# ============================================================================

class ExplosiveTopicsRequest(BaseModel):
    """Request model for explosive topics detection"""
    keywords: list[str]
    cache_hours: Optional[int] = 3
    force_refresh: Optional[bool] = False
    max_results: Optional[int] = 10


class ExplosiveTopicsResponse(BaseModel):
    """Response model for explosive topics"""
    success: bool
    source: str  # 'cache' or 'fresh'
    cached_at: str
    cache_expires_in_minutes: int
    keywords_used: list[str]
    topics: list[Dict[str, Any]]
    total_articles_analyzed: int
    processing_time_seconds: float
    errors: Optional[list[str]] = None


@app.post("/api/live-monitor/explosive-topics", response_model=ExplosiveTopicsResponse)
async def get_explosive_topics(request: ExplosiveTopicsRequest):
    """
    Tavily-based explosive topics detection (DEFAULT)
    
    Proven, reliable explosive topics detection using Tavily's premium API.
    
    RSS-based version available at /explosive-topics-rss for experimental use.
    
    Features:
    - Keyword-based topic discovery
    - 4-signal explosiveness scoring
    - MongoDB caching (default: 3 hours)
    - Force refresh option
    
    Args:
        keywords: List of keywords to focus on (e.g., ["Bihar", "corruption"])
        cache_hours: Cache duration (1-24 hours, default: 3)
        force_refresh: Bypass cache and fetch fresh data
        max_results: Maximum topics to return (default: 10)
    
    Returns:
        Ranked list of explosive topics with scores
    
    Cost: ~$0.005 per query (Tavily API calls)
    Speed: 8-15 seconds typical response time
    """
    
    try:
        # Add agent path to sys.path
        agent_path = os.path.join(os.path.dirname(__file__), 'langgraph_master_agent', 'sub_agents', 'live_political_monitor')
        if agent_path not in sys.path:
            sys.path.insert(0, agent_path)
        
        # Import agent components using importlib to avoid conflicts
        import importlib.util
        
        # Load graph module
        graph_path = os.path.join(agent_path, 'graph.py')
        spec = importlib.util.spec_from_file_location("live_monitor_graph", graph_path)
        graph_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(graph_module)
        create_live_monitor_graph = graph_module.create_live_monitor_graph
        
        # Load state module
        state_path = os.path.join(agent_path, 'state.py')
        spec = importlib.util.spec_from_file_location("live_monitor_state", state_path)
        state_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(state_module)
        LiveMonitorState = state_module.LiveMonitorState
        
        # Load cache manager
        cache_path = os.path.join(agent_path, 'tools', 'cache_manager.py')
        spec = importlib.util.spec_from_file_location("cache_manager_module", cache_path)
        cache_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cache_module)
        CacheManager = cache_module.CacheManager
        
        # Initialize cache manager with global mongo_service
        cache_manager = CacheManager(mongo_service=mongo_service)
        
        # Check cache (unless force refresh)
        if not request.force_refresh:
            cached_result = await cache_manager.get_cached_topics(
                request.keywords, 
                request.cache_hours
            )
            
            if cached_result:
                return ExplosiveTopicsResponse(
                    success=True,
                    source="cache",
                    cached_at=cached_result['cached_at'],
                    cache_expires_in_minutes=cached_result['cache_expires_in_minutes'],
                    keywords_used=request.keywords,
                    topics=cached_result['topics'],
                    total_articles_analyzed=cached_result.get('total_articles_analyzed', 0),
                    processing_time_seconds=cached_result.get('processing_time_seconds', 0)
                )
        
        # Fetch fresh data
        start_time = time.time()
        
        # Create graph
        graph = create_live_monitor_graph()
        
        # Initialize state
        initial_state: LiveMonitorState = {
            "keywords": request.keywords,
            "cache_hours": request.cache_hours,
            "max_results": request.max_results,
            "generated_queries": [],
            "raw_articles": [],
            "relevant_articles": [],
            "irrelevant_articles": [],
            "extracted_topics": [],
            "scored_topics": [],
            "explosive_topics": [],
            "total_articles_analyzed": 0,
            "processing_time_seconds": 0.0,
            "execution_log": [],
            "error_log": []
        }
        
        # Run graph
        result = await graph.ainvoke(initial_state)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Cache results
        await cache_manager.cache_topics(
            keywords=request.keywords,
            topics=result['explosive_topics'],
            cache_hours=request.cache_hours,
            metadata={
                "total_articles_analyzed": result['total_articles_analyzed'],
                "processing_time_seconds": processing_time
            }
        )
        
        return ExplosiveTopicsResponse(
            success=True,
            source="fresh",
            cached_at=datetime.now().isoformat(),
            cache_expires_in_minutes=request.cache_hours * 60,
            keywords_used=request.keywords,
            topics=result['explosive_topics'],
            total_articles_analyzed=result['total_articles_analyzed'],
            processing_time_seconds=processing_time,
            errors=result.get('error_log')
        )
        
    except Exception as e:
        print(f"Live Monitor error: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect explosive topics: {str(e)}"
        )


@app.post("/api/live-monitor/explosive-topics-rss", response_model=ExplosiveTopicsResponse)
async def get_explosive_topics_rss(request: ExplosiveTopicsRequest):
    """
    RSS-based explosive topics detection (EXPERIMENTAL)
    
    Cost-effective alternative better suited for RAG and background monitoring.
    
    Features:
    - 99.4% cheaper than Tavily ($0.00003 vs $0.005 per query)
    - Real-time RSS feed monitoring (48-hour window)
    - 5-factor explosiveness scoring (velocity, recency, diversity, geo, relevance)
    - Additional metadata: velocity, sources, regions, categories
    - Backward compatible with existing UI (superset of Tavily format)
    - MongoDB caching for performance
    
    Args:
        keywords: List of keywords to focus on (e.g., ["AI", "regulation"])
        cache_hours: Cache duration (1-24 hours, default: 3)
        force_refresh: Bypass cache and fetch fresh data
        max_results: Maximum topics to return (default: 10)
    
    Returns:
        Ranked list of explosive topics with:
        - REQUIRED fields (same as Tavily monitor for UI compatibility)
        - OPTIONAL fields (velocity, sources, regions, etc.) for enhanced UI
    
    Cost: ~$0.00003 per query (LLM calls only, no search API costs)
    Speed: 2-5 seconds typical response time
    
    To use Tavily-based monitor instead, call: /api/live-monitor/explosive-topics-tavily
    """
    
    try:
        # Import RSS Monitor components (isolated import to avoid conflicts)
        import importlib.util
        
        # Path to RSS sub-agent
        rss_agent_path = os.path.join(
            os.path.dirname(__file__), 
            'langgraph_master_agent',
            'sub_agents',
            'rss_realtime_monitor'
        )
        
        # Load graph module
        graph_spec = importlib.util.spec_from_file_location(
            "rss_monitor_graph", 
            os.path.join(rss_agent_path, 'graph.py')
        )
        graph_module = importlib.util.module_from_spec(graph_spec)
        graph_spec.loader.exec_module(graph_module)
        create_rss_realtime_monitor_graph = graph_module.create_rss_realtime_monitor_graph
        
        # Load state module
        state_spec = importlib.util.spec_from_file_location(
            "rss_monitor_state",
            os.path.join(rss_agent_path, 'state.py')
        )
        state_module = importlib.util.module_from_spec(state_spec)
        state_spec.loader.exec_module(state_module)
        RSSRealtimeMonitorState = state_module.RSSRealtimeMonitorState
        
        # Check cache (same cache manager as Tavily monitor for consistency)
        import asyncio
        if not request.force_refresh and mongo_service:
            # MongoDB is using Motor (async), so await directly
            cache_key = f"rss_topics_{'_'.join(sorted(request.keywords))}"
            cached_result = await mongo_service.db["explosive_topics_cache"].find_one({
                "cache_key": cache_key,
                "cached_at": {"$gte": datetime.now() - timedelta(hours=request.cache_hours)}
            })
            
            if cached_result:
                return ExplosiveTopicsResponse(
                    success=True,
                    source="cache",
                    cached_at=cached_result['cached_at'].isoformat(),
                    cache_expires_in_minutes=int(
                        (cached_result['cached_at'] + timedelta(hours=request.cache_hours) - datetime.now()).total_seconds() / 60
                    ),
                    keywords_used=request.keywords,
                    topics=cached_result['topics'],
                    total_articles_analyzed=cached_result.get('total_articles_analyzed', 0),
                    processing_time_seconds=cached_result.get('processing_time_seconds', 0)
                )
        
        # Fetch fresh data
        start_time = time.time()
        
        # Create RSS Monitor graph
        graph = create_rss_realtime_monitor_graph()
        
        # Initialize state (ALL fields required by RSSRealtimeMonitorState)
        initial_state: RSSRealtimeMonitorState = {
            "keywords": request.keywords,
            "regions": None,  # User can filter by region if needed
            "categories": None,  # User can filter by category if needed
            "max_topics": request.max_results,
            "all_cached_articles": [],
            "filtered_articles": [],
            "embeddings": {},
            "clusters": [],
            "topics": [],
            "explosive_topics": [],
            "total_articles_cached": 0,
            "articles_analyzed": 0,
            "topics_found": 0,
            "processing_time_seconds": 0.0,
            "execution_log": [],
            "error_log": []
        }
        
        # Run graph
        print(f"\n🔥 RSS Monitor: Processing keywords {request.keywords}...")
        # RSS monitor has async nodes, so use ainvoke() directly
        result = await graph.ainvoke(initial_state)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Cache results (if MongoDB available)
        if mongo_service:
            cache_key = f"rss_topics_{'_'.join(sorted(request.keywords))}"
            # MongoDB is using Motor (async), so await directly
            await mongo_service.db["explosive_topics_cache"].update_one(
                {"cache_key": cache_key},
                {
                    "$set": {
                        "cache_key": cache_key,
                        "keywords": request.keywords,
                        "topics": result['explosive_topics'],
                        "total_articles_analyzed": result['articles_analyzed'],
                        "processing_time_seconds": processing_time,
                        "cached_at": datetime.now(),
                        "cache_hours": request.cache_hours
                    }
                },
                upsert=True
            )
        
        print(f"✓ RSS Monitor: Found {result['topics_found']} topics in {processing_time:.1f}s")
        
        return ExplosiveTopicsResponse(
            success=True,
            source="fresh",
            cached_at=datetime.now().isoformat(),
            cache_expires_in_minutes=request.cache_hours * 60,
            keywords_used=request.keywords,
            topics=result['explosive_topics'],  # Already in UI-compatible format!
            total_articles_analyzed=result['articles_analyzed'],
            processing_time_seconds=processing_time,
            errors=result.get('error_log')
        )
        
    except Exception as e:
        print(f"RSS Monitor error: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect explosive topics (RSS): {str(e)}"
        )


# ============================================================================
# Investigation Endpoints (for Investigative Journalist Sub-Agent)
# ============================================================================

@app.post("/api/investigations", response_model=InvestigationResponse)
async def create_investigation(request: CreateInvestigationRequest):
    """Create a new investigation"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        investigation_id = await mongo_service.create_investigation(
            query=request.query,
            title=request.title,
            max_iterations=request.max_iterations
        )
        
        # Get the created investigation
        investigation = await mongo_service.get_investigation(investigation_id)
        
        return InvestigationResponse(
            success=True,
            investigation_id=investigation_id,
            data=_sanitize_for_json(investigation),
            message="Investigation created successfully"
        )
    except Exception as e:
        print(f"❌ Failed to create investigation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create investigation: {str(e)}")


@app.get("/api/investigations")
async def list_investigations(
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """List all investigations with optional filtering"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        investigations = await mongo_service.list_investigations(
            status=status,
            limit=limit,
            skip=skip
        )
        
        return {
            "success": True,
            "total": len(investigations),
            "investigations": _sanitize_for_json(investigations)
        }
    except Exception as e:
        print(f"❌ Failed to list investigations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list investigations: {str(e)}")


@app.get("/api/investigations/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(investigation_id: str):
    """Get a specific investigation by ID"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        investigation = await mongo_service.get_investigation(investigation_id)
        
        if not investigation:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        return InvestigationResponse(
            success=True,
            investigation_id=investigation_id,
            data=_sanitize_for_json(investigation)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get investigation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get investigation: {str(e)}")


@app.put("/api/investigations/{investigation_id}", response_model=InvestigationResponse)
async def update_investigation(investigation_id: str, request: UpdateInvestigationRequest):
    """Update an investigation"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        # Build update dict from request
        update_data = {}
        if request.title is not None:
            update_data['title'] = request.title
        if request.status is not None:
            update_data['status'] = request.status
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = await mongo_service.update_investigation(investigation_id, update_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        # Get updated investigation
        investigation = await mongo_service.get_investigation(investigation_id)
        
        return InvestigationResponse(
            success=True,
            investigation_id=investigation_id,
            data=_sanitize_for_json(investigation),
            message="Investigation updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to update investigation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update investigation: {str(e)}")


@app.delete("/api/investigations/{investigation_id}", response_model=InvestigationResponse)
async def delete_investigation(investigation_id: str):
    """Archive an investigation (soft delete)"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        success = await mongo_service.delete_investigation(investigation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        return InvestigationResponse(
            success=True,
            investigation_id=investigation_id,
            message="Investigation archived successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to archive investigation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to archive investigation: {str(e)}")


@app.get("/api/investigations/{investigation_id}/article")
async def get_investigation_article(investigation_id: str):
    """Get the article for an investigation"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        investigation = await mongo_service.get_investigation(investigation_id)
        
        if not investigation:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        return {
            "success": True,
            "investigation_id": investigation_id,
            "article": investigation.get('article', ''),
            "article_draft": investigation.get('article_draft', '')
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get article: {str(e)}")


@app.get("/api/investigations/{investigation_id}/evidence")
async def get_investigation_evidence(investigation_id: str):
    """Get all evidence for an investigation"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        evidence = await mongo_service.get_investigation_evidence(investigation_id)
        
        return {
            "success": True,
            "investigation_id": investigation_id,
            "evidence": _sanitize_for_json(evidence)
        }
    except Exception as e:
        print(f"❌ Failed to get evidence: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get evidence: {str(e)}")


@app.get("/api/investigations/{investigation_id}/logs")
async def get_investigation_logs(investigation_id: str, limit: int = 100):
    """Get execution logs for an investigation"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        logs = await mongo_service.get_investigation_logs(investigation_id, limit=limit)
        
        return {
            "success": True,
            "investigation_id": investigation_id,
            "logs": _sanitize_for_json(logs)
        }
    except Exception as e:
        print(f"❌ Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


# ============================================
# State History API Endpoints
# ============================================

@app.get("/api/investigations/{investigation_id}/state/history")
async def get_state_history(
    investigation_id: str,
    include_full_state: bool = False
):
    """
    Get the complete history of state snapshots for an investigation.
    
    Args:
        investigation_id: Unique investigation identifier
        include_full_state: If True, include full state; if False, only summaries
    
    Returns:
        List of state snapshots ordered by iteration
    """
    try:
        from langgraph_master_agent.sub_agents.investigative_journalist.state_history import get_history_manager
        
        manager = get_history_manager()
        history = await manager.get_state_history(investigation_id, include_full_state)
        
        return {
            "success": True,
            "investigation_id": investigation_id,
            "history": _sanitize_for_json(history)
        }
    except Exception as e:
        print(f"❌ Failed to get state history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get state history: {str(e)}")


@app.get("/api/investigations/{investigation_id}/state/{iteration}")
async def get_state_at_iteration(
    investigation_id: str,
    iteration: int
):
    """
    Get the state snapshot for a specific iteration.
    
    Args:
        investigation_id: Unique investigation identifier
        iteration: Iteration number to retrieve
    
    Returns:
        State dictionary for the requested iteration
    """
    try:
        from langgraph_master_agent.sub_agents.investigative_journalist.state_history import get_state
        
        state = await get_state(investigation_id, iteration)
        
        if state is None:
            raise HTTPException(
                status_code=404,
                detail=f"State not found for iteration {iteration}"
            )
        
        return {
            "success": True,
            "investigation_id": investigation_id,
            "iteration": iteration,
            "state": _sanitize_for_json(state)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get state at iteration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get state: {str(e)}")


@app.get("/api/investigations/{investigation_id}/state/latest")
async def get_latest_state(investigation_id: str):
    """
    Get the most recent state for an investigation.
    
    Args:
        investigation_id: Unique investigation identifier
    
    Returns:
        Latest state dictionary
    """
    try:
        from langgraph_master_agent.sub_agents.investigative_journalist.state_history import get_state
        
        state = await get_state(investigation_id, None)  # None means latest
        
        if state is None:
            raise HTTPException(
                status_code=404,
                detail="No state found for this investigation"
            )
        
        return {
            "success": True,
            "investigation_id": investigation_id,
            "state": _sanitize_for_json(state)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get latest state: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get latest state: {str(e)}")


@app.post("/api/investigations/{investigation_id}/continue", response_model=InvestigationResponse)
async def continue_investigation(investigation_id: str, request: ContinueInvestigationRequest):
    """Continue an existing investigation with more iterations (WebSocket will handle the actual execution)"""
    if not mongo_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        # Get current investigation
        investigation = await mongo_service.get_investigation(investigation_id)
        
        if not investigation:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        # Update max_iterations
        new_max = investigation['current_iteration'] + request.additional_iterations
        await mongo_service.update_investigation(
            investigation_id,
            {
                'max_iterations': new_max,
                'status': 'active'  # Reactivate if paused
            }
        )
        
        # Get updated investigation
        investigation = await mongo_service.get_investigation(investigation_id)
        
        return InvestigationResponse(
            success=True,
            investigation_id=investigation_id,
            data=_sanitize_for_json(investigation),
            message=f"Investigation will continue for {request.additional_iterations} more iterations. Connect via WebSocket to see live updates."
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to continue investigation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to continue investigation: {str(e)}")


@app.websocket("/ws/investigations/{investigation_id}")
async def investigation_websocket(websocket: WebSocket, investigation_id: str):
    """
    WebSocket endpoint for real-time investigation updates
    
    Client connects to start/continue investigation
    Server streams:
    - {"type": "connected", "data": {...}}
    - {"type": "investigation_started", "data": {...}}
    - {"type": "iteration_start", "data": {"iteration": 1}}
    - {"type": "search_complete", "data": {"urls_found": 8}}
    - {"type": "extract_progress", "data": {"current": 1, "total": 8}}
    - {"type": "entity_discovered", "data": {"name": "...", "type": "..."}}
    - {"type": "fact_recorded", "data": {"content": "..."}}
    - {"type": "connection_mapped", "data": {"from": "...", "to": "...", "type": "..."}}
    - {"type": "anomaly_detected", "data": {"description": "..."}}
    - {"type": "iteration_complete", "data": {"iteration": 1, "cost": 0.036}}
    - {"type": "article_updated", "data": {"article": "..."}}
    - {"type": "investigation_complete", "data": {...}}
    - {"type": "error", "data": {"message": "..."}}
    """
    global mongo_service
    
    print(f"\n{'='*80}")
    print(f"🔌 WEBSOCKET CONNECTION ATTEMPT: {investigation_id}")
    print(f"{'='*80}\n")
    sys.stdout.flush()
    
    await websocket.accept()
    
    print(f"\n{'='*80}")
    print(f"✅ WEBSOCKET ACCEPTED: {investigation_id}")
    print(f"{'='*80}\n")
    sys.stdout.flush()
    
    # Helper to send formatted messages
    def create_ws_message(msg_type: str, data: Any) -> Dict[str, Any]:
        return {
            "type": msg_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    try:
        # Check if MongoDB is available
        if not mongo_service:
            await websocket.send_json(create_ws_message(
                "error",
                {"message": "Database service not available"}
            ))
            await websocket.close()
            return
        
        # Get investigation from database
        investigation = await mongo_service.get_investigation(investigation_id)
        
        if not investigation:
            await websocket.send_json(create_ws_message(
                "error",
                {"message": f"Investigation {investigation_id} not found"}
            ))
            await websocket.close()
            return
        
        # Send connected confirmation
        await websocket.send_json(create_ws_message(
            "connected",
            {
                "investigation_id": investigation_id,
                "title": investigation.get('title'),
                "current_iteration": investigation.get('current_iteration', 0),
                "max_iterations": investigation.get('max_iterations', 20),
                "status": investigation.get('status', 'active')
            }
        ))
        
        print(f"📡 Sent 'connected' message to client. Waiting for client to send 'start' message...")
        sys.stdout.flush()
        
        # Wait for client message to start/continue
        try:
            print(f"⏳ Waiting for client message (timeout: 30s)...")
            sys.stdout.flush()
            client_message = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
            msg_type = client_message.get("type")
            
            print(f"\n{'='*80}")
            print(f"📨 RECEIVED CLIENT MESSAGE: {client_message}")
            print(f"Message type: {msg_type}")
            print(f"{'='*80}\n")
            sys.stdout.flush()
            
            if msg_type == "start" or msg_type == "continue":
                # Extract user instruction from client message
                user_instruction = client_message.get("content") or client_message.get("instruction")
                
                if user_instruction:
                    print(f"💬 User instruction: {user_instruction[:100]}...")
                    sys.stdout.flush()
                
                # Send investigation started
                await websocket.send_json(create_ws_message(
                    "investigation_started",
                    {
                        "investigation_id": investigation_id,
                        "query": investigation.get('query'),
                        "starting_iteration": investigation.get('current_iteration', 0),
                        "max_iterations": investigation.get('max_iterations', 20)
                    }
                ))
                
                # Capture stdout/stderr and stream to frontend
                sys.path.insert(0, os.path.dirname(__file__))
                from langgraph_master_agent.tools.sub_agent_caller import SubAgentCaller
                
                # Create a queue to stream logs
                import queue
                import threading
                log_queue = queue.Queue()
                
                # Custom writer to capture stdout
                class LogCapture:
                    def __init__(self, original_stream, queue):
                        self.original_stream = original_stream
                        self.queue = queue
                    
                    def write(self, text):
                        if text.strip():
                            self.queue.put(text)
                        self.original_stream.write(text)
                        self.original_stream.flush()
                    
                    def flush(self):
                        self.original_stream.flush()
                
                # Redirect stdout
                original_stdout = sys.stdout
                original_stderr = sys.stderr
                sys.stdout = LogCapture(original_stdout, log_queue)
                sys.stderr = LogCapture(original_stderr, log_queue)
                
                # Create a task to stream logs to WebSocket
                async def stream_logs():
                    while True:
                        try:
                            # Non-blocking check for logs
                            while not log_queue.empty():
                                log_message = log_queue.get_nowait()
                                await websocket.send_json(create_ws_message(
                                    "log",
                                    {"message": log_message}
                                ))
                            await asyncio.sleep(0.1)  # Small delay to avoid busy loop
                        except Exception as e:
                            print(f"Error streaming logs: {e}")
                            break
                
                # Start log streaming in background
                log_task = asyncio.create_task(stream_logs())
                
                # Also poll MongoDB for investigation updates (hypotheses, entities, etc.)
                last_hypothesis_count = 0
                last_entity_count = 0
                last_fact_count = 0
                last_question_count = 0
                
                async def poll_investigation_updates():
                    nonlocal last_hypothesis_count, last_entity_count, last_fact_count, last_question_count
                    while True:
                        try:
                            inv_data = await mongo_service.get_investigation(investigation_id)
                            if inv_data:
                                # Check for new hypotheses
                                hypotheses = inv_data.get('hypotheses', [])
                                if len(hypotheses) > last_hypothesis_count:
                                    for hyp in hypotheses[last_hypothesis_count:]:
                                        try:
                                            await websocket.send_json(create_ws_message(
                                                "hypothesis_updated",
                                                {
                                                    "id": hyp.get('id', ''),
                                                    "statement": hyp.get('statement', ''),
                                                    "status": hyp.get('status', 'pending'),
                                                    "confidence": hyp.get('confidence', 0.0)
                                                }
                                            ))
                                        except RuntimeError:
                                            # WebSocket closed, stop polling
                                            return
                                    last_hypothesis_count = len(hypotheses)
                                
                                # Check for new questions
                                questions = inv_data.get('questions', [])
                                if len(questions) > last_question_count:
                                    for q in questions[last_question_count:]:
                                        try:
                                            await websocket.send_json(create_ws_message(
                                                "question_discovered",
                                                {
                                                    "id": q.get('id', ''),
                                                    "hypothesis_id": q.get('hypothesis_id', 'general'),
                                                    "question": q.get('question', ''),
                                                    "status": q.get('status', 'exploring'),
                                                    "iteration": q.get('iteration', 0)
                                                }
                                            ))
                                        except RuntimeError:
                                            return
                                    last_question_count = len(questions)
                                
                                # Check for new entities (entities is a dict, not a list)
                                entities = inv_data.get('entities', {})
                                entities_list = list(entities.values()) if isinstance(entities, dict) else entities
                                if len(entities_list) > last_entity_count:
                                    for entity in entities_list[last_entity_count:]:
                                        try:
                                            await websocket.send_json(create_ws_message(
                                                "entity_discovered",
                                                {
                                                    "name": entity.get('name', ''),
                                                    "type": entity.get('type', ''),
                                                    "description": entity.get('description', '')
                                                }
                                            ))
                                        except RuntimeError:
                                            return
                                    last_entity_count = len(entities_list)
                                
                                # Check for new facts
                                facts = inv_data.get('facts', [])
                                if len(facts) > last_fact_count:
                                    for fact in facts[last_fact_count:]:
                                        try:
                                            await websocket.send_json(create_ws_message(
                                                "fact_recorded",
                                                {
                                                    "content": fact.get('content', fact.get('fact', '')),
                                                    "sources": fact.get('sources', [])
                                                }
                                            ))
                                        except RuntimeError:
                                            return
                                    last_fact_count = len(facts)
                                
                                # Send article updates
                                article = inv_data.get('article', '')
                                if article:
                                    try:
                                        await websocket.send_json(create_ws_message(
                                            "article_updated",
                                            {"article": article}
                                        ))
                                    except RuntimeError:
                                        return
                            
                            await asyncio.sleep(2)  # Poll every 2 seconds
                        except Exception as e:
                            print(f"Error polling investigation updates: {e}")
                            break
                
                print(f"\n{'='*80}")
                print(f"🚀 STARTING INVESTIGATIVE JOURNALIST AGENT")
                print(f"Query: {investigation.get('query', '')}")
                print(f"Max iterations: {investigation.get('max_iterations', 20)}")
                print(f"Investigation ID: {investigation_id}")
                print(f"{'='*80}\n")
                sys.stdout.flush()
                
                # Simple event callback for real-time updates
                async def push_event(event_type: str, data: dict):
                    """Push event to WebSocket in real-time"""
                    try:
                        await websocket.send_json(create_ws_message(event_type, data))
                    except RuntimeError:
                        # WebSocket closed
                        pass
                
                try:
                    caller = SubAgentCaller()
                    
                    # Run investigation (this will take time)
                    # ALWAYS pass investigation_id to update the existing MongoDB document
                    # Pass event_callback for real-time updates (no polling needed!)
                    result = await caller.call_investigative_journalist(
                        query=investigation.get('query', ''),
                        max_iterations=investigation.get('max_iterations', 20),
                        resume_from=investigation_id,  # Always pass ID to update existing investigation
                        user_instruction=user_instruction,  # Pass user's explicit instruction
                        event_callback=push_event  # Push events directly to WebSocket!
                    )
                    
                    # Stop log streaming
                    log_task.cancel()
                    
                    # Restore stdout/stderr
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    
                    # Send completion
                    if result.get('success'):
                        evidence = result.get('evidence_summary', {})
                        try:
                            await websocket.send_json(create_ws_message(
                                "investigation_complete",
                                {
                                    "article": result.get('article', ''),
                                    "investigation_id": result.get('investigation_id'),
                                    "entities_count": evidence.get('entities', 0),
                                    "facts_count": evidence.get('facts', 0),
                                    "total_cost": evidence.get('cost', 0.0)
                                }
                            ))
                        except RuntimeError:
                            # WebSocket already closed
                            pass
                    else:
                        try:
                            await websocket.send_json(create_ws_message(
                                "error",
                                {"message": result.get('error', 'Investigation failed')}
                            ))
                        except RuntimeError:
                            pass
                except Exception as e:
                    # Stop log streaming
                    log_task.cancel()
                    
                    # Restore stdout/stderr
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    
                    print(f"❌ Investigation error: {e}")
                    import traceback
                    traceback.print_exc()
                    try:
                        await websocket.send_json(create_ws_message(
                            "error",
                            {"message": f"Investigation failed: {str(e)}"}
                        ))
                    except RuntimeError:
                        # WebSocket already closed
                        pass
            
            else:
                await websocket.send_json(create_ws_message(
                    "error",
                    {"message": f"Unknown message type: {msg_type}"}
                ))
        
        except asyncio.TimeoutError:
            await websocket.send_json(create_ws_message(
                "error",
                {"message": "Timeout waiting for start command"}
            ))
    
    except WebSocketDisconnect:
        print(f"🔌 Investigation WebSocket disconnected: {investigation_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json(create_ws_message(
                "error",
                {"message": f"WebSocket error: {str(e)}"}
            ))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


# ============================================================================
# WebSocket: Cognitive Crawler (NEW)
# ============================================================================

@app.websocket("/ws/cognitive_crawler/{session_id}")
async def cognitive_crawler_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for Cognitive Crawler
    
    Two-phase interaction:
    1. Crawl Phase: User provides URLs → Agent crawls → Stores in MongoDB
    2. Chat Phase: User asks questions → RAG answers with sources
    """
    await websocket.accept()
    print(f"🕷️  Cognitive Crawler WebSocket connected: {session_id}")
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Cognitive Crawler ready. Send 'crawl' or 'chat' command."
        })
        
        while True:
            # Wait for message from client
            try:
                message = await asyncio.wait_for(websocket.receive_json(), timeout=300.0)
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "type": "timeout",
                    "message": "Connection timed out. Please reconnect."
                })
                break
            
            msg_type = message.get("type")
            
            if msg_type == "crawl":
                # CRAWL MODE: User provides a natural language query
                # The agent will use Tavily to discover relevant URLs automatically
                query = message.get("query", "")
                suggested_domains = message.get("suggested_domains", [])
                max_pages = message.get("max_pages", 20)
                max_depth = message.get("max_depth", 2)
                
                if not query:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No query provided. Please specify what you want to crawl (e.g., 'Python documentation')."
                    })
                    continue
                
                print(f"   📥 Crawl request: query='{query}', domains={suggested_domains}, max_pages={max_pages}, max_depth={max_depth}")
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "crawl_started",
                    "query": query,
                    "suggested_domains": suggested_domains,
                    "max_pages": max_pages,
                    "max_depth": max_depth
                })
                
                try:
                    # Import SubAgentCaller
                    from langgraph_master_agent.tools.sub_agent_caller import SubAgentCaller
                    caller = SubAgentCaller()
                    
                    # Create event callback for streaming
                    async def crawl_callback(event_type: str, data: dict):
                        try:
                            await websocket.send_json({
                                "type": event_type,
                                "data": data
                            })
                        except:
                            pass
                    
                    # Run DISCOVERY + CRAWL
                    # The agent will:
                    # 1. Use Tavily to discover URLs based on the query
                    # 2. Optionally filter by suggested_domains
                    # 3. Crawl the discovered URLs
                    result = await caller.call_cognitive_crawler(
                        action="discover",  # Start with discovery to find URLs
                        query=query,
                        crawl_sources=suggested_domains,  # Optional: focus on these domains
                        session_id=session_id,
                        max_pages=max_pages,
                        max_depth=max_depth,
                        event_callback=crawl_callback
                    )
                    
                    # Send completion
                    if result.get("success"):
                        data = result.get("data", {})
                        await websocket.send_json({
                            "type": "crawl_complete",
                            "pages_crawled": data.get("pages_crawled", 0),
                            "embeddings_generated": data.get("embeddings_generated", 0),
                            "summary": data.get("summary", ""),
                            "key_findings": data.get("key_findings", [])
                        })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Crawl failed: {result.get('error', 'Unknown error')}"
                        })
                
                except Exception as e:
                    print(f"   ❌ Crawl error: {e}")
                    import traceback
                    traceback.print_exc()
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Crawl error: {str(e)}"
                    })
            
            elif msg_type == "chat":
                # CHAT MODE: User asking questions about crawled content
                # Now uses the knowledge_base tool instead of sub-agent
                question = message.get("question", "")
                
                if not question:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No question provided."
                    })
                    continue
                
                print(f"   💬 Chat question: {question}")
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "chat_started",
                    "question": question
                })
                
                try:
                    # Use the knowledge_base tool (not a sub-agent!)
                    from langgraph_master_agent.tools.knowledge_base import query_knowledge_base
                    
                    # Query the knowledge base
                    result = await query_knowledge_base(
                        query=question,
                        top_k=10,
                        min_score=0.3,
                        generate_answer=True
                    )
                    
                    # Send answer
                    if result.get("num_results", 0) > 0:
                        await websocket.send_json({
                            "type": "chat_answer",
                            "question": question,
                            "answer": result.get("answer", ""),
                            "sources": result.get("sources", []),
                            "num_results": result.get("num_results", 0),
                            "confidence": 1.0 if result.get("num_results", 0) > 0 else 0.0
                        })
                    else:
                        await websocket.send_json({
                            "type": "chat_answer",
                            "question": question,
                            "answer": "No relevant information found in the knowledge base. Try crawling some websites first!",
                            "sources": [],
                            "num_results": 0,
                            "confidence": 0.0
                        })
                
                except Exception as e:
                    print(f"   ❌ Chat error: {e}")
                    import traceback
                    traceback.print_exc()
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Chat error: {str(e)}"
                    })
            
            elif msg_type == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })
    
    except WebSocketDisconnect:
        print(f"🔌 Cognitive Crawler WebSocket disconnected: {session_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"WebSocket error: {str(e)}"
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


# ============================================================================
# REST API: Cognitive Crawler Database Stats (NEW)
# ============================================================================

@app.get("/api/cognitive_crawler/stats")
async def get_crawler_stats():
    """
    Get statistics about the crawled database
    
    Returns:
    - Total URLs crawled
    - Total pages
    - Total embeddings
    - Recent crawls
    """
    try:
        # Use the global mongo_service instance
        if mongo_service is None or mongo_service.db is None:
            return {
                "success": False,
                "error": "Database not connected"
            }
        
        # Use the actual collection names from gov_intelligence/cognitive_crawler
        pages_collection = mongo_service.db["tenders"]  # This is where pages are stored
        vectors_collection = mongo_service.db["tender_vectors"]
        portals_collection = mongo_service.db["tender_portals"]
        
        # Count documents
        total_pages = await pages_collection.count_documents({})
        total_vectors = await vectors_collection.count_documents({})
        total_portals = await portals_collection.count_documents({})
        
        # Get unique domains from tenders collection
        pipeline = [
            {"$group": {"_id": "$domain"}},
            {"$count": "total"}
        ]
        domain_cursor = pages_collection.aggregate(pipeline)
        domain_result = await domain_cursor.to_list(length=None)
        unique_domains = domain_result[0]["total"] if domain_result else 0
        
        # Get recent crawls (last 20)
        recent_pages_cursor = pages_collection.find(
            {},
            {"url": 1, "domain": 1, "stored_at": 1, "tender_id": 1, "title": 1, "organization": 1}
        ).sort("stored_at", -1).limit(20)
        recent_pages = await recent_pages_cursor.to_list(length=20)
        
        return {
            "success": True,
            "stats": {
                "total_pages": total_pages,
                "total_embeddings": total_vectors,
                "total_sessions": total_portals,
                "unique_domains": unique_domains
            },
            "recent_crawls": [
                {
                    "url": page.get("url", "N/A"),
                    "domain": page.get("domain", "Unknown"),
                    "crawled_at": page.get("stored_at").isoformat() if page.get("stored_at") else None,
                    "session_id": page.get("tender_id", "N/A"),
                    "content_length": len(str(page.get("title", ""))) * 100,  # Approximate
                    "title": page.get("title", "Untitled")
                }
                for page in recent_pages
            ]
        }
    
    except Exception as e:
        print(f"Error getting crawler stats: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/cognitive_crawler/search")
async def search_crawled_urls(
    q: str = "",
    domain: str = "",
    limit: int = 50,
    offset: int = 0
):
    """
    Search and filter crawled URLs
    
    Query params:
    - q: Search term (searches in URL and domain)
    - domain: Filter by specific domain
    - limit: Max results (default 50)
    - offset: Pagination offset (default 0)
    """
    try:
        # Use the global mongo_service instance
        if mongo_service is None or mongo_service.db is None:
            return {
                "success": False,
                "error": "Database not connected"
            }
        
        pages_collection = mongo_service.db["tenders"]  # Actual collection name
        
        # Build query
        query = {}
        
        if q:
            # Search in URL, domain, title, organization
            query["$or"] = [
                {"url": {"$regex": q, "$options": "i"}},
                {"domain": {"$regex": q, "$options": "i"}},
                {"title": {"$regex": q, "$options": "i"}},
                {"organization": {"$regex": q, "$options": "i"}}
            ]
        
        if domain:
            query["domain"] = domain
        
        # Get total count
        total = await pages_collection.count_documents(query)
        
        # Get pages
        pages_cursor = pages_collection.find(
            query,
            {
                "url": 1,
                "domain": 1,
                "stored_at": 1,
                "tender_id": 1,
                "title": 1,
                "organization": 1,
                "status": 1
            }
        ).sort("stored_at", -1).skip(offset).limit(limit)
        pages = await pages_cursor.to_list(length=limit)
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": [
                {
                    "url": page.get("url", "N/A"),
                    "domain": page.get("domain", "Unknown"),
                    "title": page.get("title", page.get("organization", "Untitled")),
                    "crawled_at": page.get("stored_at").isoformat() if page.get("stored_at") else None,
                    "session_id": page.get("tender_id", "N/A"),
                    "content_length": len(str(page.get("title", ""))) * 100,
                    "status": page.get("status", "unknown")
                }
                for page in pages
            ]
        }
    
    except Exception as e:
        print(f"Error searching crawled URLs: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/knowledge_base/query")
async def query_knowledge_base_endpoint(request: dict):
    """
    Query the knowledge base using RAG
    
    POST body:
    {
        "query": "What caused cough syrup deaths?",
        "top_k": 10,  // optional
        "min_score": 0.3,  // optional
        "generate_answer": true  // optional
    }
    
    Returns:
    {
        "success": true,
        "answer": "...",
        "sources": [...],
        "num_results": 5,
        "scores": [...]
    }
    """
    try:
        query = request.get("query")
        if not query:
            return {
                "success": False,
                "error": "No query provided"
            }
        
        top_k = request.get("top_k", 10)
        min_score = request.get("min_score", 0.3)
        generate_answer = request.get("generate_answer", True)
        
        # Import and call the knowledge base tool
        from langgraph_master_agent.tools.knowledge_base import query_knowledge_base
        
        result = await query_knowledge_base(
            query=query,
            top_k=top_k,
            min_score=min_score,
            generate_answer=generate_answer
        )
        
        return {
            "success": True,
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "num_results": result.get("num_results", 0),
            "scores": result.get("scores", []),
            "query": query
        }
    
    except Exception as e:
        print(f"Error querying knowledge base: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Run Server (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    # Enable reload for development
    uvicorn.run(
        "app:app",  # Use string for reload to work
        host="0.0.0.0",
        port=port,
        reload=True,  # Auto-reload on file changes
        log_level="info"
    )



# ============================================================================
# SIMPLIFIED CHAT WEBSOCKET (ChatGPT-style)
# ============================================================================

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    """
    Simplified WebSocket endpoint for ChatGPT-style interface
    
    Client sends:
        {
            "type": "message",
            "content": "User message",
            "investigation_id": "optional_inv_id"  # For continuing
        }
    
    Server sends (ONLY 3 types!):
        {"type": "log", "data": {"message": "..."}}
        {"type": "artifact", "data": {...}}
        {"type": "complete", "data": {"cost": 0.24}}
    """
    await websocket.accept()
    print(f"\n🔌 Chat WebSocket connected")
    sys.stdout.flush()
    
    try:
        # Send connected message
        await websocket.send_json({
            "type": "connected",
            "data": {"message": "Connected to investigator agent"}
        })
        
        # Track running investigation
        investigation_task = None
        
        # Create a message receiver task
        async def message_receiver():
            """Continuously receive messages from WebSocket"""
            while True:
                try:
                    message = await websocket.receive_json()
                    return message
                except Exception as e:
                    raise e
        
        # Main event loop - handle messages and investigations concurrently
        while True:
            # Create a new message receiver task
            message_task = asyncio.create_task(message_receiver())
            
            # Wait for either a new message or investigation completion
            if investigation_task and not investigation_task.done():
                # Investigation running - wait for either message or completion
                done, pending = await asyncio.wait(
                    [message_task, investigation_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Check what completed
                if investigation_task in done:
                    # Investigation completed
                    message_task.cancel()  # Cancel the pending message receiver
                    
                    try:
                        result = await investigation_task
                        
                        # Handle artifacts
                        if result.get("success") and result.get("artifacts"):
                            for artifact in result["artifacts"]:
                                await websocket.send_json({
                                    "type": "artifact",
                                    "data": artifact
                                })
                        
                        # Send article as artifact with unique ID (versioned by timestamp)
                        if result.get("article"):
                            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                            investigation_id_result = result.get("investigation_id", "unknown")
                            await websocket.send_json({
                                "type": "artifact",
                                "data": {
                                    "artifact_id": f"article_{investigation_id_result}_{timestamp}",
                                    "type": "article",
                                    "title": f"Investigation Report ({timestamp})",
                                    "description": "Complete investigative report with findings and analysis",
                                    "status": "ready",
                                    "article_text": result.get("article", ""),
                                    "created_at": datetime.now(timezone.utc).isoformat()
                                }
                            })
                        
                        # Send completion
                        await websocket.send_json({
                            "type": "investigation_complete",
                            "data": {
                                "total_cost": result.get("cost_breakdown", {}).get("total_cost", 0),
                                "article": result.get("article", ""),
                                "investigation_id": result.get("investigation_id")
                            }
                        })
                        
                    except asyncio.CancelledError:
                        print(f"\n⏹️  Investigation cancelled")
                        sys.stdout.flush()
                    except Exception as e:
                        print(f"❌ Error handling investigation result: {e}")
                        import traceback
                        traceback.print_exc()
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": str(e)}
                        })
                    
                    investigation_task = None
                    continue
                
                else:
                    # Message received while investigation running
                    message = await message_task
                    msg_type = message.get("type")
                    
                    # Handle stop request
                    if msg_type == "stop_investigation":
                        print(f"\n⏹️  Stop requested by user")
                        sys.stdout.flush()
                        if investigation_task and not investigation_task.done():
                            investigation_task.cancel()
                            try:
                                await investigation_task
                            except asyncio.CancelledError:
                                pass
                        await websocket.send_json({
                            "type": "log",
                            "data": {"message": "⏹️ Investigation stopped by user"}
                        })
                        investigation_task = None
                        continue
                    
                    # New message while investigation running - cancel old investigation
                    content = message.get("content", "").strip()
                    if msg_type == "message" and content:
                        print(f"\n⏹️  Cancelling previous investigation (new message received)")
                        sys.stdout.flush()
                        investigation_task.cancel()
                        try:
                            await investigation_task
                        except asyncio.CancelledError:
                            pass
                        investigation_task = None
                        # Fall through to handle the new message below
                    else:
                        continue
            else:
                # No investigation running - just wait for message
                message = await message_task
                msg_type = message.get("type")
                content = message.get("content", "").strip()
                
                if msg_type != "message" or not content:
                    continue
            
            # At this point we have a new message to process
            investigation_id = message.get("investigation_id")
            
            print(f"\n💬 User message: {content}")
            sys.stdout.flush()
            
            # Parse user intent
            content_lower = content.lower()
            
            # Start investigation (new or continue)
            try:
                # Check if this is a "continue" command
                if "continue" in content_lower and investigation_id:
                    # Extract iteration count from message
                    import re
                    match = re.search(r'(\d+)', content)
                    additional_iterations = int(match.group(1)) if match else 5
                    
                    await websocket.send_json({
                        "type": "log",
                        "data": {"message": f"🔄 Continuing investigation for {additional_iterations} more iterations..."}
                    })
                    
                    # Update max_iterations via REST API
                    if mongo_service:
                        investigation = await mongo_service.get_investigation(investigation_id)
                        if investigation:
                            current_iter = investigation.get("current_iteration", 0)
                            new_max = current_iter + additional_iterations
                            
                            await mongo_service.db.investigations.update_one(
                                {"investigation_id": investigation_id},
                                {"$set": {"max_iterations": new_max, "status": "active"}}
                            )
                
                # Create callback to stream logs to WebSocket
                async def stream_log(message: str):
                    """Stream log message to WebSocket"""
                    try:
                        await websocket.send_json({
                            "type": "log",
                            "data": {"message": message}
                        })
                    except:
                        pass
                
                # Import investigative journalist
                from langgraph_master_agent.tools.sub_agent_caller import SubAgentCaller
                
                # Determine the actual query to use
                actual_query = content
                
                # Check if this is a follow-up question to an existing investigation
                is_followup = False
                if investigation_id and mongo_service and "continue" not in content_lower:
                    investigation = await mongo_service.get_investigation(investigation_id)
                    if investigation and investigation.get("status") in ["active", "completed"]:
                        # This is a follow-up question
                        is_followup = True
                        current_iter = investigation.get("current_iteration", 0)
                        
                        # For follow-ups, extend max_iterations by default amount (5 more)
                        additional_iterations = 5
                        
                        # Check if user specified iterations
                        import re
                        match = re.search(r'(\d+)\s+(?:more\s+)?iterations?', content_lower)
                        if match:
                            additional_iterations = int(match.group(1))
                        
                        new_max = current_iter + additional_iterations
                        
                        await mongo_service.db.investigations.update_one(
                            {"investigation_id": investigation_id},
                            {"$set": {"max_iterations": new_max, "status": "active"}}
                        )
                        
                        print(f"   🔄 Follow-up question detected")
                        print(f"   📊 Extended max_iterations: {investigation.get('max_iterations')} → {new_max}")
                        print(f"   💬 New research direction: {content[:60]}...")
                
                # If continuing an existing investigation with "continue" keyword
                if "continue" in content_lower and investigation_id and mongo_service:
                    investigation = await mongo_service.get_investigation(investigation_id)
                    if investigation and investigation.get("query"):
                        actual_query = investigation.get("query")
                        print(f"   🔄 Using original query: {actual_query}")
                    else:
                        print(f"   ⚠️  Could not load original query, using continue command as query")
                
                # Parse intent: extract max_iterations if specified
                import re
                
                # Word to number mapping
                word_to_num = {
                    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
                }
                
                max_iterations = 5  # Default
                
                # Try to match digits first
                match = re.search(r'(\d+)\s+(?:more\s+)?iterations?', content_lower)
                if match:
                    max_iterations = int(match.group(1))
                else:
                    # Try to match text numbers
                    match = re.search(r'(one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:more\s+)?iterations?', content_lower)
                    if match:
                        max_iterations = word_to_num.get(match.group(1), 5)
                
                print(f"   📊 Parsed iterations: {max_iterations}")
                
                # Create investigation if new
                if not investigation_id and mongo_service:
                    # Extract query (remove iteration instructions)
                    query = re.sub(r'for\s+\d+\s+iterations?', '', content, flags=re.IGNORECASE).strip()
                    query = re.sub(r'\d+\s+iterations?', '', query, flags=re.IGNORECASE).strip()
                    
                    # Create investigation
                    import uuid
                    investigation_id = f"inv_{uuid.uuid4().hex[:12]}"
                    
                    await mongo_service.db.investigations.insert_one({
                        "investigation_id": investigation_id,
                        "query": query,
                        "title": query[:100],
                        "status": "active",
                        "max_iterations": max_iterations,
                        "current_iteration": 0,
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                        "entities": [],
                        "facts": [],
                        "connections": [],
                        "anomalies": [],
                        "hypotheses": [],
                        "questions": []
                    })
                    
                    await websocket.send_json({
                        "type": "investigation_started",
                        "data": {
                            "investigation_id": investigation_id,
                            "query": query
                        }
                    })
                
                # Run investigation as a cancellable task
                caller = SubAgentCaller()
                
                # Create event callback for real-time updates
                async def event_callback(event_type: str, data: dict):
                    """Handle real-time events from investigator"""
                    try:
                        await websocket.send_json({
                            "type": event_type,
                            "data": data
                        })
                    except:
                        pass
                
                # Create and track the investigation task
                async def run_investigation():
                    return await caller.call_investigative_journalist(
                        query=actual_query,  # Use the actual query (original or new)
                        max_iterations=max_iterations,
                        resume_from=investigation_id,
                        user_instruction=content if is_followup else None,  # Pass user's follow-up question
                        event_callback=event_callback
                    )
                
                # Start investigation as background task (don't await here!)
                # The main loop will handle it and wait for messages concurrently
                investigation_task = asyncio.create_task(run_investigation())
                
            except Exception as e:
                print(f"❌ Error in chat handler: {e}")
                import traceback
                traceback.print_exc()
                
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": str(e)}
                })
    
    except WebSocketDisconnect:
        print("🔌 Chat WebSocket disconnected")
    except Exception as e:
        print(f"❌ Chat WebSocket error: {e}")
        import traceback
        traceback.print_exc()


