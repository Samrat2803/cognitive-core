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
from pydantic import BaseModel
from dotenv import load_dotenv

# Add parent directory to path to import agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langgraph_master_agent.main import MasterPoliticalAnalyst
from config_server import Config
from datetime import datetime

# Load environment variables (for local development)
load_dotenv()

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

# Global instances
agent: Optional[MasterPoliticalAnalyst] = None
mongo_service = None

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
            "html_url": "http://localhost:8000/api/artifacts/india_gdp_cached_2024.html",
            "png_url": "http://localhost:8000/api/artifacts/india_gdp_cached_2024.png",
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
            "html_url": "http://localhost:8000/api/artifacts/pakistan_gdp_cached_2024.html",
            "png_url": "http://localhost:8000/api/artifacts/pakistan_gdp_cached_2024.png",
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
    processing_time_ms: Optional[int] = None
    errors: Optional[list[str]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    agent_status: str
    timestamp: str


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
    global agent, mongo_service
    
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
    
    print("=" * 70)
    print("🎯 Backend server ready!")
    print(f"📍 CORS Origins: {cors_origins}")
    print(f"📊 Database: {'MongoDB Atlas' if mongo_service else 'File System Only'}")
    print(f"🗄️  Query Cache: {'ENABLED ✅' if ENABLE_CACHE else 'DISABLED ❌'}")
    if ENABLE_CACHE:
        print(f"   Cached queries: {len(CACHED_RESPONSES)}")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mongo_service
    
    print("\n🛑 Shutting down Political Analyst Workbench Backend...")
    
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
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for AWS/load balancers"""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agent_status="ready" if agent else "not_initialized",
        timestamp=datetime.utcnow().isoformat()
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
                    completed_at=datetime.utcnow(),
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
    # Artifacts are stored in artifacts/ directory relative to backend_server/
    file_path = f"artifacts/{artifact_id}.html"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return FileResponse(
        file_path,
        media_type="text/html",
        filename=f"{artifact_id}.html"
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
            "generated_at": datetime.utcnow().isoformat()
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
    await websocket.accept()
    
    # Helper function to send formatted messages
    def create_message(msg_type: str, data: Any, message_id: str = None) -> Dict[str, Any]:
        msg = {
            "type": msg_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
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
                        # Process query with agent (with 90s timeout)
                        try:
                            print(f"⏱️  Starting agent.process_query() with 90s timeout...")
                            print(f"   📚 Conversation history: {len(conversation_history)} messages")
                            result = await asyncio.wait_for(
                                agent.process_query(
                                    query, 
                                    conversation_history=conversation_history.copy(),
                                    session_id=session_id
                                ),
                                timeout=90.0
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
                                   f"http://localhost:8000/api/artifacts/{artifact_data.get('artifact_id')}.html")
                        
                        png_url = (artifact_data.get("s3_png_url") or 
                                  artifact_data.get("png_url") or
                                  f"http://localhost:8000/api/artifacts/{artifact_data.get('artifact_id')}.png")
                        
                        await websocket.send_json(create_message(
                            "artifact",
                            {
                                "artifact_id": artifact_data.get("artifact_id"),
                                "type": artifact_data.get("type", "chart"),
                                "title": artifact_data.get("title", "Analysis Result"),
                                "html_url": html_url,
                                "png_url": png_url,
                                "storage": artifact_data.get("storage", "local"),
                                "metadata": artifact_data.get("metadata", {})
                            },
                            current_message_id
                        ))
                    
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
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    conversation_history.append({
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": datetime.utcnow().isoformat()
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
# Run Server (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8001))
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )

