# Backend Team Implementation Guide

**Version:** 2.0.0  
**Date:** September 2025  
**Team:** Backend Development  
**Status:** Ready for Implementation  

## 🎯 Backend Team Objectives (MVP-focused)

Transform the existing FastAPI application into a **monolithic backend** that supports:
1. **Conversational Chat Interface** - ChatGPT-style natural language processing
2. **Real-time WebSocket Streaming** - Live agent monitoring and progress updates
3. **POC Algorithm Integration** - Wrap existing geo_sentiment_* code seamlessly
4. **Export & Reporting** - Generate PDF/CSV/Excel reports
5. **User Authentication** - JWT-based user management

## 🚀 Development Principles (MVP)

### **🔄 Use Existing Code as Much as Possible**
- **Preserve POC Algorithms:** Keep `geo_sentiment_poc.py`, `geo_sentiment_agent.py`, and `agent_utils.py` unchanged
- **Wrap, Don't Rewrite:** Create service layers around existing functionality instead of rewriting
- **Leverage Current Infrastructure:** Use existing MongoDB, Redis, and AWS setup
- **Maintain API Compatibility:** Keep existing `/research` endpoint for backward compatibility

### **📱 MVP-First Approach**
**Phase 1 MVP:** Basic analysis via legacy `/research` and minimal chat endpoints
- Simple message processing (no AI parsing initially)
- Direct integration with existing POC code
- Basic WebSocket connection (ping/pong only)
- Minimal error handling

**Phase 2 Features (Post-MVP):** Enhanced conversational capabilities
- AI-powered query parsing
- Real-time progress streaming
- Advanced error handling and recovery
- User authentication and sessions

**Phase 3 Polish (Post-MVP):** Production-ready enhancements
- Export functionality
- Performance optimization
- Comprehensive monitoring
- Advanced security features

### **🧪 Test-Driven Development**
**Before coding any feature (MVP):**
1. **Write test cases first** - Define expected behavior
2. **Create failing tests** - Red phase of TDD
3. **Implement minimum code** - Green phase to pass tests
4. **Refactor and optimize** - Blue phase for clean code

**Test Hierarchy:**
```
Unit Tests → Integration Tests → API Tests → E2E Tests
```

## 📋 Implementation Checklist

### MongoDB Schemas & Indexes (MVP)
Minimal collections to avoid ambiguity.

Analyses collection (`analyses`):
```json
{
  "_id": "ObjectId",
  "user_id": "string|null",
  "query_text": "string",
  "params": { "countries": ["string"], "days": 7 },
  "status": "queued|processing|completed|failed",
  "progress": { "percent": 0, "step": "string" },
  "summary": { "overall_sentiment": 0.0 },
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

Required indexes:
```js
db.analyses.createIndex({ user_id: 1, created_at: -1 });
db.analyses.createIndex({ status: 1, created_at: -1 });
```

Exports collection (`exports`) (Phase 2):
```json
{ "_id": "ObjectId", "analysis_id": "ObjectId", "format": "pdf|csv|json|excel", "status": "generating|completed|failed", "s3_key": "string", "expires_at": "ISODate", "created_at": "ISODate" }
```

Retention: `analyses` 90 days; logs 30 days.

### Phase 1: Project Setup & Structure (Week 1)

#### ✅ Task 1.1: Create Monolithic Backend Structure
**Priority:** Critical | **Estimate:** 4 hours

```bash
cd backend

# Create new directory structure
mkdir -p core api poc_agents utils
mkdir -p tests/unit tests/integration tests/api

# Create __init__.py files
touch core/__init__.py api/__init__.py poc_agents/__init__.py utils/__init__.py
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/api/__init__.py

# Move existing POC files
cp ../POCs/*.py poc_agents/
touch poc_agents/__init__.py

# Create core module files
touch core/conversational_engine.py
touch core/poc_integration_service.py  
touch core/websocket_manager.py
touch core/export_service.py
touch core/auth_service.py

# Create API route files
touch api/chat_routes.py
touch api/analysis_routes.py
touch api/monitoring_routes.py
touch api/export_routes.py
touch api/auth_routes.py

# Create utility files
touch utils/validation.py
touch utils/formatting.py
touch utils/background_tasks.py
touch utils/logging_config.py
```

**Acceptance Criteria:**
- [ ] All directories created successfully
- [ ] POC files moved to poc_agents/ directory
- [ ] All module __init__.py files exist
- [ ] Project structure matches architecture specification

---

#### ✅ Task 1.2: Update Dependencies (MVP)
**Priority:** Critical | **Estimate:** 2 hours

**File to modify:** `backend/requirements.txt`
```txt
# Add these MVP dependencies (no versions as per user rules):
websockets
python-multipart
```

**Commands to run:**
```bash
cd backend
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Acceptance Criteria:**
- [ ] All new packages installed successfully
- [ ] No dependency conflicts
- [ ] Requirements.txt updated and committed

---

#### ✅ Task 1.3: Enhance Main FastAPI Application (MVP)
**Priority:** Critical | **Estimate:** 6 hours

**🧪 Test Cases First (MVP):**
```python
# tests/api/test_app_enhancement.py
def test_health_endpoint_enhanced():
    """Test enhanced health check returns comprehensive status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "status" in data

def test_websocket_endpoint_exists():
    """Test WebSocket endpoint is accessible"""
    with client.websocket_connect("/ws/test_session") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert data == "pong"

def test_backward_compatibility():
    """Test existing /research endpoint still works"""
    response = client.post("/research", json={"query": "test"})
    assert response.status_code == 200  # Should not break
```

**File to modify:** `backend/app.py` (keep `/research` unauthenticated for MVP)

```python
"""
Enhanced FastAPI Monolithic Backend
Political Analyst Workbench - Version 2.0
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import logging
from contextlib import asynccontextmanager

# Keep existing imports
from config import Config
from services.mongo_service import MongoService
from services.analytics_service import AnalyticsService

# Add new imports
from api.chat_routes import chat_router
from api.analysis_routes import analysis_router  
from api.monitoring_routes import monitoring_router
from api.export_routes import export_router
from api.auth_routes import auth_router

from core.websocket_manager import WebSocketManager
from core.poc_integration_service import POCIntegrationService
from core.auth_service import AuthService

# Global instances
websocket_manager = WebSocketManager()
poc_service = POCIntegrationService()
auth_service = AuthService()
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logging.info("🚀 Starting Political Analyst Workbench Backend v2.0")
    
    # Initialize services
    await poc_service.initialize()
    await websocket_manager.initialize()
    
    # Validate configuration
    if not Config.validate_config():
        raise RuntimeError("Invalid configuration")
    
    logging.info("✅ All services initialized successfully")
    
    yield
    
    # Shutdown
    await websocket_manager.cleanup()
    logging.info("👋 Backend shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Political Analyst Workbench API",
    description="Monolithic backend for conversational geopolitical sentiment analysis", 
    version="2.0.0",
    lifespan=lifespan
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://dgbfif5o7v03y.cloudfront.net",  # Your production frontend URL
        "https://d1vembbjd54t86.cloudfront.net"   # Your API CDN URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate JWT token"""
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"], dependencies=[Depends(get_current_user)])
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"], dependencies=[Depends(get_current_user)])
app.include_router(monitoring_router, prefix="/api/monitoring", tags=["monitoring"], dependencies=[Depends(get_current_user)])
app.include_router(export_router, prefix="/api/export", tags=["export"], dependencies=[Depends(get_current_user)])

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket connection for real-time analysis updates"""
    try:
        await websocket_manager.connect(websocket, session_id)
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Handle ping/pong or other control messages
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(session_id)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(session_id)

# Keep existing endpoints but enhance them
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Political Analyst Workbench API v2.0",
        "status": "running",
        "features": ["conversational_interface", "real_time_monitoring", "export_reports"],
        "version": "2.0.0"
    }

@app.get("/health")  
async def health_check():
    """Enhanced health check endpoint"""
    # Keep existing health check logic but enhance
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": await mongo_service.health_check() if mongo_service else "not_available",
            "redis": await websocket_manager.health_check(),
            "poc_service": await poc_service.health_check(),
            "websocket_manager": websocket_manager.is_healthy()
        },
        "features": {
            "authentication": True,
            "websockets": True,
            "conversational_interface": True,
            "export_functionality": True
        }
    }

# Keep your existing /research endpoint for backward compatibility
@app.post("/research")
async def research_legacy(request: ResearchRequest, current_user = Depends(get_current_user)):
    """Legacy research endpoint - maintained for backward compatibility"""
    # Keep existing logic but add user context
    return await poc_service.execute_analysis(request, user=current_user)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
```

**Acceptance Criteria:**
- [ ] FastAPI app starts successfully
- [ ] All new routers included
- [ ] WebSocket endpoint accessible
- [ ] Health check returns comprehensive status
- [ ] Backward compatibility maintained

---

### Phase 2: Core Services Implementation (Week 2) – Post-MVP extensions

#### ✅ Task 2.1: Conversational Engine
**Priority:** High | **Estimate:** 8 hours

**🧪 Test Cases First:**
```python
# tests/unit/test_conversational_engine.py
def test_simple_sentiment_query_parsing():
    """Test basic sentiment analysis query parsing"""
    engine = ConversationalEngine()
    intent = await engine.parse_query("Analyze Hamas sentiment")
    
    assert intent.action == "sentiment_analysis"
    assert intent.topic == "Hamas"
    assert intent.confidence > 0.7

def test_country_extraction():
    """Test country extraction from queries"""
    engine = ConversationalEngine()
    intent = await engine.parse_query("Hamas sentiment in US and Iran")
    
    assert "United States" in intent.countries
    assert "Iran" in intent.countries

def test_help_query_recognition():
    """Test help queries are properly identified"""
    engine = ConversationalEngine()
    intent = await engine.parse_query("what can you do?")
    
    assert intent.action == "help"
    assert intent.confidence == 1.0
```

**🔄 MVP Implementation (Use Existing Code):**
- **Phase 1:** Simple pattern matching (no AI initially)
- **Phase 2:** Add OpenAI integration for complex parsing
- **Phase 3:** Advanced context handling

**File to create:** `backend/core/conversational_engine.py`

```python
"""
Conversational Query Engine
Parses natural language into analysis parameters
"""
import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
import os

@dataclass
class QueryIntent:
    action: str  # "sentiment_analysis", "comparison", "follow_up", "help"
    topic: Optional[str] = None
    countries: List[str] = None
    parameters: Dict[str, Any] = None
    confidence: float = 0.0

class ConversationalEngine:
    """Processes natural language queries into structured analysis parameters"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.supported_countries = [
            "United States", "Iran", "Israel", "Germany", "United Kingdom",
            "France", "Russia", "China", "India", "Brazil", "Canada", 
            "Australia", "Japan", "South Korea", "Turkey", "Saudi Arabia",
            "Egypt", "Pakistan", "Bangladesh", "Nigeria", "South Africa"
        ]
        
    async def parse_query(self, query_text: str, context: Dict[str, Any] = None) -> QueryIntent:
        """Parse natural language query into structured intent"""
        
        # Simple pattern matching for common queries
        query_lower = query_text.lower()
        
        # Sentiment analysis patterns
        sentiment_patterns = [
            r"analyze\s+(\w+)\s+sentiment",
            r"sentiment\s+analysis\s+(?:of|for)\s+(\w+)",
            r"how\s+do\s+(?:people|countries)\s+feel\s+about\s+(\w+)",
            r"(\w+)\s+sentiment"
        ]
        
        for pattern in sentiment_patterns:
            match = re.search(pattern, query_lower)
            if match:
                topic = match.group(1)
                countries = self._extract_countries(query_text)
                if not countries:
                    countries = ["United States", "Iran", "Israel"]  # Default
                
                return QueryIntent(
                    action="sentiment_analysis",
                    topic=topic.title(),
                    countries=countries,
                    parameters={
                        "days": self._extract_time_range(query_text),
                        "results_per_country": 20
                    },
                    confidence=0.8
                )
        
        # Comparison patterns
        comparison_patterns = [
            r"compare\s+(\w+)\s+and\s+(\w+)\s+(?:views|opinions|sentiment)\s+on\s+(\w+)",
            r"difference\s+between\s+(\w+)\s+and\s+(\w+)\s+on\s+(\w+)"
        ]
        
        for pattern in comparison_patterns:
            match = re.search(pattern, query_lower)
            if match:
                country1, country2, topic = match.groups()
                return QueryIntent(
                    action="comparison",
                    topic=topic.title(),
                    countries=[country1.title(), country2.title()],
                    parameters={"comparison_mode": True, "days": 7},
                    confidence=0.9
                )
        
        # Help/unclear patterns
        if any(word in query_lower for word in ["help", "what can you do", "how does this work"]):
            return QueryIntent(
                action="help",
                confidence=1.0
            )
        
        # If no pattern matches, try AI parsing
        if self.openai_key:
            return await self._ai_parse_query(query_text, context)
        
        # Fallback
        return QueryIntent(
            action="unclear",
            confidence=0.1
        )
    
    def _extract_countries(self, text: str) -> List[str]:
        """Extract country names from text"""
        found_countries = []
        text_lower = text.lower()
        
        for country in self.supported_countries:
            if country.lower() in text_lower:
                found_countries.append(country)
                
        return found_countries[:5]  # Max 5 countries
    
    def _extract_time_range(self, text: str) -> int:
        """Extract time range in days"""
        # Look for patterns like "last 7 days", "past week", etc.
        time_patterns = {
            r"last\s+(\d+)\s+days?": lambda x: int(x),
            r"past\s+(\d+)\s+days?": lambda x: int(x),
            r"last\s+week": lambda x: 7,
            r"past\s+week": lambda x: 7,
            r"last\s+month": lambda x: 30,
            r"past\s+month": lambda x: 30,
        }
        
        text_lower = text.lower()
        for pattern, converter in time_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return converter(match.group(1) if match.groups() else None)
                except:
                    continue
                    
        return 7  # Default to 7 days
    
    async def _ai_parse_query(self, query_text: str, context: Dict[str, Any] = None) -> QueryIntent:
        """Use AI to parse complex queries"""
        system_prompt = """You are a query parser for a geopolitical sentiment analysis system.
        Parse the user's natural language query into structured parameters.
        
        Available actions: sentiment_analysis, comparison, follow_up, help
        Available countries: United States, Iran, Israel, Germany, United Kingdom, France, Russia, China, India, Brazil
        
        Return JSON with: {"action": "sentiment_analysis", "topic": "Hamas", "countries": ["United States", "Iran"], "parameters": {"days": 7}}
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "temperature": 0,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Parse this query: {query_text}"}
                        ]
                    }
                )
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to parse JSON response
                try:
                    parsed = json.loads(content)
                    return QueryIntent(
                        action=parsed.get("action", "unclear"),
                        topic=parsed.get("topic"),
                        countries=parsed.get("countries", []),
                        parameters=parsed.get("parameters", {}),
                        confidence=0.9
                    )
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"AI parsing error: {e}")
            
        return QueryIntent(action="unclear", confidence=0.1)
    
    async def generate_confirmation_message(self, intent: QueryIntent) -> str:
        """Generate confirmation message for parsed intent"""
        if intent.action == "sentiment_analysis":
            countries_str = ", ".join(intent.countries) if intent.countries else "default countries"
            days = intent.parameters.get("days", 7) if intent.parameters else 7
            
            return f"I'll analyze {intent.topic} sentiment across {countries_str} using the last {days} days of data. Proceed with analysis?"
        
        elif intent.action == "comparison":
            return f"I'll compare how {' and '.join(intent.countries)} view {intent.topic}. Shall I proceed?"
        
        elif intent.action == "help":
            return """I can help you with geopolitical sentiment analysis. Try these examples:
            • "Analyze Hamas sentiment"
            • "Compare US and Iran views on Israel"  
            • "How do European countries feel about Ukraine war?"
            • "Hamas sentiment in last 14 days"
            """
        
        else:
            return "I didn't quite understand that. Could you try rephrasing? For example: 'Analyze Hamas sentiment' or 'Compare US and Iran views on Israel'."
```

**Acceptance Criteria:**
- [ ] Can parse common sentiment analysis queries
- [ ] Extracts countries and topics correctly
- [ ] Returns structured QueryIntent objects
- [ ] Handles edge cases gracefully
- [ ] Generates appropriate confirmation messages

---

#### ✅ Task 2.2: POC Integration Service  
**Priority:** Critical | **Estimate:** 8 hours

**🧪 Test Cases First:**
```python
# tests/unit/test_poc_integration_service.py
def test_poc_service_initialization():
    """Test POC service initializes with existing agent"""
    service = POCIntegrationService()
    await service.initialize()
    
    assert service.agent is not None
    assert await service.health_check() == "healthy"

def test_existing_poc_wrapper():
    """Test existing POC code can be called through service"""
    service = POCIntegrationService()
    
    # Mock existing POC call
    result = await service._call_poc_async(
        countries=["United States"], 
        topic="test", 
        days=7
    )
    
    assert "countries_analyzed" in result
    assert "sentiment_scores" in result

def test_analysis_status_tracking():
    """Test analysis status is properly tracked"""
    service = POCIntegrationService()
    
    request_data = {"countries": ["US"], "topic": "test"}
    result = await service.execute_analysis(request_data)
    
    assert "analysis_id" in result
    assert result["success"] in [True, False]
```

**🔄 MVP Implementation (Preserve Existing POC Code):**
- **Phase 1:** Direct wrapper around existing POC functions
- **Phase 2:** Add WebSocket streaming to existing analysis
- **Phase 3:** Enhanced progress tracking and error handling

**⚠️ CRITICAL:** Do NOT modify existing POC files (`geo_sentiment_poc.py`, `geo_sentiment_agent.py`, `agent_utils.py`). Only wrap them.

**File to create:** `backend/core/poc_integration_service.py`

```python
"""
POC Integration Service
Wraps existing POC algorithms with monolithic service patterns
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import logging

# Import your existing POC modules
from poc_agents.geo_sentiment_poc import main as run_sentiment_poc
from poc_agents.geo_sentiment_agent import GeopoliticalSentimentAgent
from poc_agents.create_sources_review import main as create_sources_review

from core.websocket_manager import WebSocketManager

class POCIntegrationService:
    """Service that integrates existing POC code with monolithic architecture"""
    
    def __init__(self):
        self.websocket_manager = None  # Will be injected
        self.agent = None
        self.active_analyses: Dict[str, Dict] = {}
        
    async def initialize(self):
        """Initialize the service"""
        try:
            self.agent = GeopoliticalSentimentAgent()
            logging.info("✅ POC Integration Service initialized")
        except Exception as e:
            logging.error(f"❌ Failed to initialize POC service: {e}")
            raise
    
    async def health_check(self) -> str:
        """Health check for the service"""
        try:
            if self.agent:
                return "healthy"
            return "not_initialized"
        except Exception:
            return "unhealthy"
    
    async def execute_analysis(self, request_data: Dict[str, Any], user: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute geopolitical sentiment analysis with real-time streaming"""
        
        analysis_id = str(uuid.uuid4())
        session_id = request_data.get("session_id", "anonymous")
        
        # Store analysis info
        self.active_analyses[analysis_id] = {
            "id": analysis_id,
            "status": "processing",
            "user": user,
            "request": request_data,
            "created_at": asyncio.get_event_loop().time()
        }
        
        try:
            # Send initial progress
            await self._send_progress(session_id, analysis_id, "initializing", 0, "Starting geopolitical sentiment analysis...")
            
            # Prepare parameters for POC
            countries = request_data.get("countries", ["United States", "Iran", "Israel"])
            topic = request_data.get("topic", request_data.get("query_text", ""))
            days = request_data.get("days", 7)
            
            # Execute POC analysis with progress streaming
            result = await self._execute_poc_with_streaming(
                analysis_id=analysis_id,
                session_id=session_id, 
                countries=countries,
                topic=topic,
                days=days
            )
            
            # Send completion
            await self._send_progress(session_id, analysis_id, "completed", 100, "Analysis completed successfully")
            
            # Update status
            self.active_analyses[analysis_id]["status"] = "completed"
            self.active_analyses[analysis_id]["result"] = result
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "status": "completed",
                "results": result
            }
            
        except Exception as e:
            logging.error(f"Analysis failed: {e}")
            
            # Send error
            await self._send_error(session_id, analysis_id, str(e))
            
            # Update status
            self.active_analyses[analysis_id]["status"] = "failed"
            self.active_analyses[analysis_id]["error"] = str(e)
            
            return {
                "success": False,
                "analysis_id": analysis_id,
                "error": str(e)
            }
    
    async def _execute_poc_with_streaming(self, analysis_id: str, session_id: str, countries: List[str], topic: str, days: int) -> Dict[str, Any]:
        """Execute POC analysis with real-time progress updates"""
        
        # Step 1: Search phase
        await self._send_progress(session_id, analysis_id, "searching", 20, f"Searching for articles about {topic}")
        
        # Step 2: Analysis phase  
        await self._send_progress(session_id, analysis_id, "analyzing", 40, "Analyzing sentiment and bias")
        
        # Modify your existing POC code to accept parameters
        # For now, we'll call it with default parameters and parse results
        try:
            # This is where you'd modify your POC code to accept dynamic parameters
            # For initial implementation, use existing POC as-is
            
            await self._send_progress(session_id, analysis_id, "processing", 60, "Processing articles with AI")
            
            # Call your existing POC main function
            # You may need to modify geo_sentiment_poc.py to accept parameters
            poc_result = await self._call_poc_async(countries, topic, days)
            
            await self._send_progress(session_id, analysis_id, "finalizing", 80, "Generating final report")
            
            # Transform POC result into API format
            formatted_result = await self._format_poc_result(poc_result, countries, topic)
            
            return formatted_result
            
        except Exception as e:
            raise Exception(f"POC execution failed: {str(e)}")
    
    async def _call_poc_async(self, countries: List[str], topic: str, days: int) -> Dict[str, Any]:
        """Call existing POC code asynchronously"""
        # Run POC code in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        # You'll need to modify your existing POC to accept these parameters
        # For now, this is a placeholder structure
        return await loop.run_in_executor(
            None,
            self._execute_poc_sync,
            countries, topic, days
        )
    
    def _execute_poc_sync(self, countries: List[str], topic: str, days: int) -> Dict[str, Any]:
        """Synchronous POC execution (modify your existing code to accept parameters)"""
        
        # TODO: Modify geo_sentiment_poc.py to accept:
        # - countries: List[str] 
        # - topic: str
        # - days: int
        
        # For initial implementation, return mock result structure
        # Replace this with actual POC call once modified
        
        mock_result = {
            "countries_analyzed": countries,
            "topic": topic,
            "sentiment_scores": {
                country: {"score": 0.5, "confidence": 0.8} 
                for country in countries
            },
            "total_articles": 57,
            "bias_detected": True
        }
        
        return mock_result
    
    async def _format_poc_result(self, poc_result: Dict[str, Any], countries: List[str], topic: str) -> Dict[str, Any]:
        """Format POC result into API response structure"""
        
        # This transforms your POC output into the API contract format
        return {
            "query": {
                "text": f"{topic} sentiment analysis",
                "parameters": {
                    "countries": countries,
                    "topic": topic,
                    "days": 7
                }
            },
            "results": {
                "summary": {
                    "overall_sentiment": poc_result.get("overall_sentiment", 0.0),
                    "countries_analyzed": len(countries),
                    "total_articles": poc_result.get("total_articles", 0),
                    "analysis_confidence": 0.85,
                    "bias_detected": poc_result.get("bias_detected", False),
                    "completion_time_ms": 45000
                },
                "country_results": [
                    {
                        "country": country,
                        "sentiment_score": poc_result.get("sentiment_scores", {}).get(country, {}).get("score", 0.0),
                        "confidence": poc_result.get("sentiment_scores", {}).get(country, {}).get("confidence", 0.8),
                        "articles_count": 19,
                        "dominant_sentiment": "neutral",
                        "key_themes": ["conflict", "politics"],
                        "bias_analysis": {
                            "bias_types": ["selection"],
                            "bias_severity": 0.3,
                            "notes": "Standard media coverage"
                        }
                    }
                    for country in countries
                ],
                "methodology": {
                    "search_terms_used": [topic],
                    "time_range": f"Last 7 days",
                    "sources_diversity": {
                        "media_types": ["news", "analysis"],
                        "languages": ["english"],
                        "credibility_range": [0.6, 0.9]
                    }
                },
                "bias_summary": {
                    "overall_bias_severity": 0.35,
                    "most_common_bias": "selection",
                    "recommendations": ["Include more diverse sources"]
                }
            }
        }
    
    async def _send_progress(self, session_id: str, analysis_id: str, step: str, percentage: int, message: str):
        """Send progress update via WebSocket"""
        if self.websocket_manager:
            await self.websocket_manager.send_to_session(session_id, {
                "type": "analysis_progress",
                "analysis_id": analysis_id,
                "step": step,
                "progress": {
                    "completion_percentage": percentage,
                    "message": message,
                    "timestamp": asyncio.get_event_loop().time()
                }
            })
    
    async def _send_error(self, session_id: str, analysis_id: str, error_message: str):
        """Send error message via WebSocket"""
        if self.websocket_manager:
            await self.websocket_manager.send_to_session(session_id, {
                "type": "analysis_error", 
                "analysis_id": analysis_id,
                "error": {
                    "code": "ANALYSIS_FAILED",
                    "message": error_message,
                    "recoverable": False
                }
            })
    
    async def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific analysis"""
        return self.active_analyses.get(analysis_id)
    
    async def list_active_analyses(self, user: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """List all active analyses for a user"""
        if user:
            return [
                analysis for analysis in self.active_analyses.values()
                if analysis.get("user", {}).get("id") == user.get("id")
            ]
        return list(self.active_analyses.values())
```

**Acceptance Criteria:**
- [ ] Successfully wraps existing POC code
- [ ] Provides real-time progress updates via WebSocket
- [ ] Transforms POC output to API contract format
- [ ] Handles errors gracefully
- [ ] Maintains analysis status tracking

---

**Status Update Required:**
After completing each task, update your status in the team tracker:

```bash
# Update your progress
echo "Task 1.1: ✅ COMPLETED" >> team_status.md
echo "Task 1.2: 🔄 IN_PROGRESS" >> team_status.md
```

**Next Phase:** After Phase 1 completion, move to WebSocket Manager and API Routes implementation.

**Questions/Blockers:** Report any issues immediately in the team communication channel.

