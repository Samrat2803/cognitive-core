# Political Analyst Workbench - Architecture Overview

**Version:** 2.0  
**Last Updated:** October 9, 2025  
**Status:** Production  
**Live Deployment:** [https://d2dk8wkh2d0mmy.cloudfront.net](https://d2dk8wkh2d0mmy.cloudfront.net)

---

## Executive Summary

The Political Analyst Workbench is a production-grade AI-powered platform for real-time political analysis and intelligence gathering. Built on LangGraph's multi-agent architecture, the system combines real-time web search capabilities with specialized analytical agents to deliver comprehensive political insights with automatic visualization generation.

**Key Capabilities:**
- Real-time political sentiment analysis across multiple countries
- Automated visualization and artifact generation (charts, maps, reports)
- WebSocket-based streaming for responsive user experience
- Scalable cloud infrastructure supporting 50+ concurrent users
- Modular sub-agent architecture for specialized analysis tasks

**Technology Foundation:**
- **Backend:** Python 3.11, FastAPI, LangGraph 0.6, LangChain
- **Frontend:** React 19, TypeScript, Vite
- **AI/ML:** OpenAI GPT-4o-mini, Tavily real-time search API
- **Infrastructure:** AWS (Elastic Beanstalk, CloudFront, S3), MongoDB Atlas

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Component Architecture](#2-component-architecture)
3. [Master Agent Workflow](#3-master-agent-workflow)
4. [Sub-Agent Architecture](#4-sub-agent-architecture)
5. [Data Flow](#5-data-flow)
6. [Communication Protocols](#6-communication-protocols)
7. [Infrastructure & Deployment](#7-infrastructure--deployment)
8. [Performance Characteristics](#8-performance-characteristics)
9. [Security Architecture](#9-security-architecture)
10. [Scalability & Reliability](#10-scalability--reliability)

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  • Web Browser (React SPA)                                          │
│  • WebSocket Client (Real-time bidirectional communication)         │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓ HTTPS/WSS
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTENT DELIVERY LAYER                           │
│  • AWS CloudFront (Global CDN)                                       │
│  • SSL/TLS Termination                                              │
│  • Origin Access Control (OAC) for S3                               │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     LOAD BALANCING LAYER                             │
│  • AWS Application Load Balancer                                    │
│  • WebSocket Upgrade Support                                        │
│  • Health Checks & Auto-Scaling                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                                │
│  • FastAPI Server (Python 3.11)                                     │
│  • Master Agent (LangGraph 7-node workflow)                         │
│  • Sub-Agents (3 operational, 6 in development)                     │
│  • Real-time WebSocket Handler                                      │
└─────────────────────────────────────────────────────────────────────┘
                    ↓                           ↓
┌─────────────────────────────┐  ┌────────────────────────────────────┐
│     EXTERNAL SERVICES       │  │     DATA PERSISTENCE               │
│  • OpenAI GPT-4o-mini       │  │  • MongoDB Atlas (M0 Free Tier)    │
│  • Tavily Search API        │  │  • AWS S3 (Artifact Storage)       │
│  • Rate Limits: 50 req/min  │  │  • CloudFront CDN Cache            │
└─────────────────────────────┘  └────────────────────────────────────┘
```

### 1.2 Architectural Principles

1. **Modularity:** Each sub-agent is isolated, independently testable, and deployable
2. **Scalability:** Horizontal scaling via AWS Auto Scaling Groups
3. **Resilience:** Graceful degradation, retry logic, and fallback mechanisms
4. **Observability:** Comprehensive logging, tracing (LangFuse), and monitoring
5. **Performance:** Async-first design, connection pooling, intelligent caching

---

## 2. Component Architecture

### 2.1 Frontend Architecture

**Technology Stack:**
- **Framework:** React 19 with TypeScript
- **Build Tool:** Vite 7.1
- **UI Library:** Radix UI (accessible component primitives)
- **Animation:** Framer Motion 12
- **State Management:** Nanostores (lightweight reactive state)
- **Styling:** CSS Modules + Tailwind utilities

**Key Components:**

```typescript
src/
├── components/
│   ├── chat/
│   │   ├── ChatPanel.tsx          // Main chat interface
│   │   ├── Message.tsx             // Message rendering with markdown
│   │   ├── MessageInput.tsx        // User input handling
│   │   ├── Citations.tsx           // Source citations display
│   │   └── ExecutionGraph.tsx      // Real-time execution visualization
│   ├── artifact/
│   │   └── ArtifactPanel.tsx       // Artifact display (charts, maps)
│   ├── dashboard/
│   │   └── LiveMonitorDashboard.tsx // Live political monitor
│   └── ui/
│       ├── ConnectionStatus.tsx    // WebSocket connection indicator
│       └── [30+ reusable components]
├── services/
│   └── WebSocketService.ts         // WebSocket client with reconnection
├── hooks/
│   └── useWebSocket.ts             // React hooks for WS management
└── pages/
    ├── HomePage.tsx
    ├── ChatPage.tsx
    └── InfoPage.tsx
```

**Communication Pattern:**
- WebSocket for real-time bidirectional communication
- REST API fallback for non-streaming operations
- Optimistic UI updates for better perceived performance

### 2.2 Backend Architecture

**Technology Stack:**
- **Framework:** FastAPI 0.115 (async-native)
- **Agent Framework:** LangGraph 0.6 (state machine orchestration)
- **LLM Integration:** LangChain + OpenAI Python SDK
- **Search API:** Tavily Python SDK
- **Visualization:** Plotly 5.x + Pillow (PIL)

**Directory Structure:**

```
backend_v2/
├── app.py                          // FastAPI application entry point
├── application.py                  // AWS EB compatibility wrapper
├── langgraph_master_agent/
│   ├── main.py                     // MasterPoliticalAnalyst class
│   ├── graph.py                    // LangGraph workflow definition
│   ├── state.py                    // State schema (TypedDict)
│   ├── config.py                   // Configuration constants
│   ├── nodes/                      // 7 master agent nodes
│   │   ├── conversation_manager.py
│   │   ├── strategic_planner.py    // LLM-based tool selection
│   │   ├── tool_executor.py        // Tool/sub-agent execution
│   │   ├── decision_gate.py        // Quality assessment & routing
│   │   ├── response_synthesizer.py // LLM-based response generation
│   │   ├── artifact_decision.py    // Determine viz requirements
│   │   └── artifact_creator.py     // Generate visualizations
│   ├── tools/
│   │   ├── tavily_direct.py        // Tavily API wrapper
│   │   ├── sub_agent_caller.py     // Sub-agent interface
│   │   └── visualization_tools.py  // Chart generation utilities
│   └── sub_agents/
│       ├── sentiment_analyzer/     // Multi-country sentiment analysis
│       ├── live_political_monitor/ // Real-time event tracking
│       ├── sitrep_generator/       // Situation report generation
│       └── [6 more in development]
├── shared/
│   ├── llm_factory.py              // LLM instance management
│   ├── observability.py            // LangFuse integration
│   ├── visualization_factory.py    // Centralized viz generation
│   ├── infographic_generator.py    // Professional infographics (780 lines)
│   ├── reel_generator.py           // Video animations (375 lines)
│   └── deck_generator.py           // PowerPoint generation (425 lines)
└── services/
    ├── mongo_service.py            // MongoDB operations
    └── s3_service.py               // S3 artifact storage
```

---

## 3. Master Agent Workflow

### 3.1 LangGraph State Machine

The master agent implements a sophisticated 7-node state machine with conditional routing and iterative refinement capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER AGENT FLOW                         │
└─────────────────────────────────────────────────────────────┘

START
  ↓
┌─────────────────────────────────────────────────────────────┐
│ NODE 1: CONVERSATION MANAGER                                │
│ • Initialize session context                                │
│ • Load conversation history (last 10 messages)              │
│ • Validate input                                            │
│ • Prune state for memory efficiency                         │
│ Timing: 50-100ms                                            │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ NODE 2: STRATEGIC PLANNER                                   │
│ • Analyze query intent (LLM: GPT-4o-mini)                   │
│ • Select appropriate tools/sub-agents                       │
│ • Check conversation history for cached data                │
│ • Generate execution strategy                               │
│ Timing: 200-300ms                                           │
│ LLM Tokens: ~500 tokens                                     │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ NODE 3: TOOL EXECUTOR                                       │
│ • Execute Tavily searches (1-3 seconds each)                │
│ • Delegate to sub-agents (20-40 seconds each)               │
│ • Aggregate results in state                                │
│ • Handle errors with retry logic (3 attempts)               │
│ Timing: 1s - 40s (depends on tools)                         │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ NODE 4: DECISION GATE                                       │
│ • Assess result quality (richness, diversity, relevance)    │
│ • Check iteration count (max 3)                             │
│ • Determine next action:                                    │
│   - RETRY: Insufficient data → Loop back to Planner         │
│   - PROCEED: Sufficient data → Continue to Synthesis        │
│ Timing: 10-50ms                                             │
└─────────────────────────────────────────────────────────────┘
  ↓ [if retry]      ↓ [if proceed]
  ↓                 ↓
  └─────────┐       ↓
            ↓       ↓
         LOOP BACK  ↓
            ↓       ↓
  ┌─────────┘       ↓
  ↓                 ↓
┌─────────────────────────────────────────────────────────────┐
│ NODE 5: RESPONSE SYNTHESIZER                                │
│ • Compile results from all sources                          │
│ • Generate coherent response (LLM: GPT-4o-mini)             │
│ • Extract citations with URLs                               │
│ • Calculate confidence score                                │
│ Timing: 500-1000ms                                          │
│ LLM Tokens: ~1000 tokens                                    │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ NODE 6: ARTIFACT DECISION                                   │
│ • Analyze if data supports visualization                    │
│ • Determine optimal artifact type                           │
│ • Extract data for visualization                            │
│ Timing: 100-200ms                                           │
│ LLM Tokens: ~300 tokens                                     │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ NODE 7: ARTIFACT CREATOR                                    │
│ • Generate Plotly charts (interactive HTML + static PNG)    │
│ • Optimize PNGs with PIL (lossless compression)             │
│ • Upload to S3 with lifecycle policies                      │
│ • Store metadata in MongoDB                                 │
│ Timing: 1-3 seconds                                         │
└─────────────────────────────────────────────────────────────┘
  ↓
END (WebSocket: "complete" message sent)
```

### 3.2 State Schema

The master agent maintains a comprehensive state object throughout execution:

```python
class MasterAgentState(TypedDict):
    # Conversation Context
    conversation_history: List[Dict[str, str]]  # Last 10 messages
    current_message: str
    session_id: str
    timestamp: str
    
    # Planning
    task_plan: str
    tools_to_use: List[str]
    reasoning: str
    
    # Execution Results
    tool_results: Dict[str, Any]          # Tavily search results
    sub_agent_results: Dict[str, Any]     # Sub-agent outputs
    execution_log: List[Dict[str, Any]]   # Audit trail
    
    # Decision Flags
    has_sufficient_info: bool
    needs_more_tools: bool
    iteration_count: int                  # Current iteration (max 3)
    retry_strategy_next: str              # Next retry strategy
    
    # Response Data
    final_response: str
    citations: List[Dict[str, str]]
    confidence_score: float
    
    # Artifacts
    should_create_artifact: bool
    artifact_type: Optional[str]          # bar_chart, line_chart, map_chart
    artifact: Optional[Dict]              # Metadata + S3 URLs
    
    # Metadata
    error_log: List[str]
    metadata: Dict[str, Any]
```

### 3.3 Retry Strategies

The decision gate implements intelligent retry strategies for data quality improvement:

```python
RETRY_STRATEGIES = [
    "broader_keywords",      # Use more general search terms
    "specific_keywords",     # Use more specific, detailed terms
    "alternative_sources",   # Try different source types (academic, gov, news)
    "advanced_search",       # Use Tavily advanced mode (max_results=15)
    "alternative_tools"      # Try different tool combinations
]
```

**Quality Assessment Criteria:**
- Minimum 3 search results required
- Minimum 500 characters of content
- Source diversity (multiple domains)
- Recency (within specified time range)

---

## 4. Sub-Agent Architecture

### 4.1 Isolation Strategy

Each sub-agent operates as an independent LangGraph workflow with its own state, nodes, and graph definition. This ensures zero-impact development and independent deployment.

**Isolation Mechanism (sys.path manipulation):**

```python
# sub_agent_caller.py
def call_sub_agent(agent_name, query, params):
    # 1. Save current Python environment
    original_sys_path = sys.path.copy()
    saved_modules = {}
    
    # 2. Clear conflicting modules (state.py, graph.py, etc.)
    for module in ['state', 'nodes', 'config', 'graph']:
        if module in sys.modules:
            saved_modules[module] = sys.modules[module]
            del sys.modules[module]
    
    # 3. Add sub-agent directory FIRST in sys.path
    agent_dir = f"sub_agents/{agent_name}"
    sys.path.insert(0, agent_dir)
    
    # 4. Import sub-agent modules (now isolated)
    from graph import create_sub_agent_graph
    from state import SubAgentState
    
    # 5. Execute sub-agent
    graph = create_sub_agent_graph()
    result = await graph.ainvoke(initial_state)
    
    # 6. Restore original environment
    sys.path = original_sys_path
    for module, obj in saved_modules.items():
        sys.modules[module] = obj
    
    return result
```

**Benefits:**
- Zero conflicts between sub-agent modules
- Parallel development without coordination overhead
- Independent testing and deployment
- Easy rollback (comment out method call)

### 4.2 Operational Sub-Agents

#### **Sentiment Analyzer**
- **Purpose:** Multi-country sentiment analysis with bias detection
- **Nodes:** Query Analyzer → Data Collector → Sentiment Analyzer → Bias Analyzer → Artifact Generator
- **Execution Time:** 30-40 seconds (3 countries)
- **Artifacts:** Bar charts, radar charts, sentiment maps, bias reports
- **Tavily Calls:** 3-5 searches
- **LLM Calls:** 3-5 (batched analysis)

#### **Live Political Monitor**
- **Purpose:** Real-time event tracking with explosiveness scoring
- **Nodes:** Query Expander → Event Collector → Explosiveness Scorer → Topic Clusterer → Report Generator
- **Execution Time:** 25-30 seconds
- **Artifacts:** JSON reports, explosive topic lists
- **Explosiveness Algorithm:** Weighted scoring (LLM rating: 30pts, Frequency: 25pts, Source Diversity: 20pts, Urgency Keywords: 15pts, Recency: 10pts)

#### **SitRep Generator**
- **Purpose:** Professional situation reports (daily/weekly)
- **Nodes:** Scope Definer → Data Aggregator → Priority Ranker → Report Composer → Format Exporter
- **Execution Time:** 35-45 seconds
- **Artifacts:** PDF reports, HTML dashboards, email-ready text, JSON data

### 4.3 Sub-Agent Communication Protocol

```typescript
// Request Format
{
    "sub_agent": "sentiment_analyzer",
    "query": "Hamas sentiment analysis",
    "params": {
        "countries": ["US", "UK", "France"],
        "time_range_days": 7
    }
}

// Response Format
{
    "success": true,
    "sub_agent": "sentiment_analyzer",
    "status": "COMPLETED",
    "data": {
        "sentiment_scores": {
            "US": {"score": 0.75, "reasoning": "...", "sources": [...]},
            "UK": {"score": 0.62, "reasoning": "...", "sources": [...]},
            "France": {"score": -0.52, "reasoning": "...", "sources": [...]}
        },
        "bias_analysis": {...},
        "artifacts": [
            {"artifact_id": "bar_abc123", "type": "bar_chart", "png_url": "..."},
            {"artifact_id": "radar_def456", "type": "radar_chart", "png_url": "..."}
        ],
        "confidence": 0.87,
        "execution_log": [...]
    }
}
```

---

## 5. Data Flow

### 5.1 Request Flow

```
User Input → Frontend → CloudFront → ALB → Backend → Master Agent
                                                            ↓
                                                 Strategic Planner
                                                            ↓
                                                    Tool Executor
                                                      ↙         ↘
                                              Tavily API    Sub-Agents
                                                      ↘         ↙
                                                    Decision Gate
                                                            ↓
                                               Response Synthesizer
                                                            ↓
                                                  Artifact Creator
                                                      ↙         ↘
                                                   S3       MongoDB
                                                      ↘         ↙
                                                   WebSocket Stream
                                                            ↓
                                                       Frontend
```

### 5.2 Data Persistence Strategy

**MongoDB Atlas (Session Storage):**
- Session metadata and conversation history
- Execution logs and error traces
- Artifact metadata (references, not files)
- TTL: 90 days (automatic cleanup)
- Collection: `sessions`, `artifacts_metadata`, `execution_logs`

**AWS S3 (Artifact Storage):**
- PNG images (optimized, lossless compression)
- HTML interactive charts (Plotly CDN-based)
- Lifecycle policy: 30-day automatic deletion
- Bucket: `political-analyst-artifacts`
- Access: CloudFront OAC (Origin Access Control)

**Decision Logic:**
- All artifacts → S3 (uniform storage, CDN support)
- Only metadata → MongoDB (queries, references)
- Session data → MongoDB (temporary, structured data)
- Static assets → S3 (images, documents, videos)

### 5.3 Caching Strategy

**CloudFront Cache:**
- Artifact files: 30-day cache (until lifecycle deletion)
- Static frontend assets: 1-year cache with versioned URLs
- API responses: No cache (real-time required)

**Application-Level Cache:**
- LLM response cache: Disabled (real-time accuracy priority)
- Tavily result cache: Optional per sub-agent (e.g., Live Monitor: 3 hours)

---

## 6. Communication Protocols

### 6.1 WebSocket Protocol

**Connection Establishment:**
```
Client → wss://cloudfront-domain/ws/analyze
       → CloudFront (SSL termination)
       → ALB (WebSocket upgrade)
       → Backend (FastAPI WebSocket handler)
```

**Message Types:**

```typescript
// 1. CLIENT → SERVER: Query
{
    "type": "query",
    "message_id": "msg_1728512345",
    "data": {
        "query": "Sentiment analysis of Hamas",
        "use_citations": true,
        "session_id": "session_abc123"
    }
}

// 2. SERVER → CLIENT: Update (streaming)
{
    "type": "update",
    "message_id": "msg_1728512345",
    "step": "strategic_planner",
    "action": "Selected sentiment_analysis_agent",
    "timestamp": "2025-10-09T14:23:45Z"
}

// 3. SERVER → CLIENT: Artifact
{
    "type": "artifact",
    "message_id": "msg_1728512345",
    "artifact_id": "bar_abc123",
    "artifact_type": "bar_chart",
    "png_url": "https://s3.../bar_abc123.png",
    "html_url": "https://s3.../bar_abc123.html",
    "metadata": {...}
}

// 4. SERVER → CLIENT: Complete
{
    "type": "complete",
    "message_id": "msg_1728512345",
    "response": "Comprehensive analysis...",
    "citations": [
        {"title": "...", "url": "...", "published_date": "..."}
    ],
    "confidence": 0.87,
    "execution_time": 32.5
}

// 5. SERVER → CLIENT: Error
{
    "type": "error",
    "message_id": "msg_1728512345",
    "severity": "warning",
    "message": "Tavily API rate limit. Retrying in 2s...",
    "recoverable": true
}
```

### 6.2 Error Handling Protocol

**Retriable Errors:**
- Tavily API 429 (rate limit): 3 retries with exponential backoff (2s, 4s, 8s)
- OpenAI API timeout: 1 retry after 5s
- Network timeouts: 3 retries with backoff

**Non-Retriable Errors:**
- Missing API keys: Surface to user immediately
- Invalid query format: Return validation error
- Authentication failure: Terminate connection

**Graceful Degradation:**
- Tavily unavailable: Use cached data if available, or inform user
- MongoDB unavailable: Continue without session persistence
- S3 unavailable: Store artifacts locally, upload later (queue)

---

## 7. Infrastructure & Deployment

### 7.1 AWS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USERS (Global)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              AWS CLOUDFRONT (Global CDN)                     │
│  • 2 Distributions:                                         │
│    - Frontend: d2dk8wkh2d0mmy.cloudfront.net               │
│    - Backend: d1h4cjcbl77aah.cloudfront.net                │
│  • Free SSL Certificates (AWS Certificate Manager)          │
│  • Origin Access Control (OAC) for S3                       │
│  • Cache: 30 days for artifacts, 1 year for static assets   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          AWS APPLICATION LOAD BALANCER (us-east-1)          │
│  • Target: Elastic Beanstalk Environment                    │
│  • Health Checks: /health endpoint (every 30s)              │
│  • WebSocket Support: Upgrade header forwarding             │
│  • Timeout: 300 seconds (for long-running queries)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│       AWS ELASTIC BEANSTALK (Python 3.11 Platform)          │
│  • Environment: political-analyst-backend-prod              │
│  • Instance Type: t3.micro (2 vCPU, 1 GB RAM)               │
│  • Auto Scaling:                                            │
│    - Min: 1 instance                                        │
│    - Max: 5 instances                                       │
│    - Scale up: CPU > 70% for 5 minutes                      │
│    - Scale down: CPU < 30% for 10 minutes                   │
│  • Deployment: Rolling updates (no downtime)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            AWS S3 (us-east-1)                               │
│  • Frontend Bucket: analyst-frontend-prod (private)         │
│    - React build artifacts                                  │
│    - Access: CloudFront OAC only                            │
│  • Artifact Bucket: political-analyst-artifacts             │
│    - Generated charts, maps, reports                        │
│    - Lifecycle: Delete after 30 days                        │
│    - Access: CloudFront OAC + backend (IAM role)            │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Deployment Process

**Backend Deployment:**
```bash
# 1. Package application
cd backend_v2
zip -r deployment.zip . -x "*.git*" "*__pycache__*" "*.venv*" "artifacts/*"

# 2. Upload to Elastic Beanstalk
eb init -p python-3.11 political-analyst-backend --region us-east-1
eb create political-analyst-backend-prod \
    --elb-type application \
    --instance-type t3.micro \
    --envvars $(cat .env | xargs)

# 3. Configure auto-scaling (via .ebextensions/)
eb deploy

# Deployment time: 3-5 minutes
```

**Frontend Deployment:**
```bash
# 1. Build production bundle
cd Frontend_v2
npm run build

# 2. Upload to S3
aws s3 sync dist/ s3://analyst-frontend-prod/ --delete

# 3. Invalidate CloudFront cache
aws cloudfront create-invalidation \
    --distribution-id E1234567890ABC \
    --paths "/*"

# Propagation time: 5-15 minutes (global CDN)
```

### 7.3 Environment Configuration

**Backend Environment Variables:**
```bash
# API Keys (stored in EB environment config, not in code)
OPENAI_API_KEY=sk-proj-...
TAVILY_API_KEY=tvly-...
MONGODB_CONNECTION_STRING=mongodb+srv://...

# Application Config
DEFAULT_MODEL=gpt-4o-mini
TEMPERATURE=0
MAX_TOOL_ITERATIONS=3

# Infrastructure
BACKEND_BASE_URL=https://d1h4cjcbl77aah.cloudfront.net
CORS_ORIGINS=https://d2dk8wkh2d0mmy.cloudfront.net
AWS_REGION=us-east-1
S3_ARTIFACT_BUCKET=political-analyst-artifacts

# Observability
LANGFUSE_HOST=http://localhost:3761
ENABLE_OBSERVABILITY=true
```

**Frontend Environment Variables:**
```typescript
// .env.production
VITE_API_URL=https://d1h4cjcbl77aah.cloudfront.net
VITE_WS_URL=wss://d1h4cjcbl77aah.cloudfront.net/ws/analyze
```

---

## 8. Performance Characteristics

### 8.1 Response Time Analysis

**Query Type: Basic Search**
- User input → Backend: 100-200ms (network)
- Master agent processing: 3-8 seconds
  - Conversation Manager: 50-100ms
  - Strategic Planner: 200-300ms (GPT-4o-mini)
  - Tool Executor (Tavily): 1-3 seconds
  - Decision Gate: 10-50ms
  - Response Synthesizer: 500-1000ms (GPT-4o-mini)
  - Artifact Decision: 100-200ms (GPT-4o-mini)
  - Artifact Creator: 1-3 seconds (if applicable)
- Backend → Frontend: 100-200ms (network)
- **Total: 3.5-8.5 seconds**

**Query Type: Sentiment Analysis (3 countries)**
- Master agent: 1-2 seconds
- Sentiment Analyzer sub-agent: 30-40 seconds
  - Query Analyzer: 200ms (GPT-4o-mini)
  - Data Collector: 15-20s (Tavily × 3 countries)
  - Sentiment Analysis: 8-10s (GPT-4o-mini × 3, batched)
  - Bias Analysis: 3-5s (hybrid algorithmic + LLM)
  - Artifact Generation: 2-3s (Plotly + S3 upload)
- Response synthesis: 1-2 seconds
- **Total: 32-45 seconds**

**Breakdown by Component:**
- Tavily API calls: 45-50% of total time
- GPT-4o-mini calls: 25-30% of total time
- Artifact generation: 5-8% of total time
- Network overhead: 8-12% of total time
- State management: <2% of total time

### 8.2 Throughput Capacity

**Single Instance (t3.micro):**
- Concurrent WebSocket connections: 50-100
- Concurrent active queries: 5-10 (limited by external API rate limits)
- Queries per minute: 15-20 (depends on query complexity)
- Memory usage: 600-800 MB (out of 1 GB)
- CPU usage: 40-70% average, 90% peak

**With Auto-Scaling (1-5 instances):**
- Max concurrent connections: 250-500
- Max concurrent queries: 25-50
- Queries per minute: 75-100

**Bottlenecks (in order of impact):**
1. **Tavily API rate limit:** 50 requests/minute
2. **OpenAI token limit:** 10,000 TPM (tokens per minute)
3. **MongoDB connections:** 100 max (not a bottleneck at current scale)
4. **Instance CPU:** 2 vCPU per t3.micro

### 8.3 Resource Utilization

**Average Query (Sentiment Analysis):**
- Tavily API calls: 3-5 searches
- OpenAI API calls: 5-7 (strategic planning, sentiment analysis, synthesis)
- Total tokens: 3,000-5,000 tokens
- S3 operations: 2-4 uploads (PNG + HTML artifacts)
- MongoDB operations: 2-3 writes (session, metadata, execution log)
- Network egress: 500 KB - 2 MB

**Memory Profile:**
- Base application: 200-300 MB
- Per active query: 40-60 MB (state + LLM context)
- Peak (10 concurrent queries): 600-800 MB

**Storage Usage:**
- MongoDB: ~50 MB per 1,000 queries (compressed)
- S3 artifacts: ~200 KB per artifact (PNG optimized)
- CloudFront cache: Automatic management

---

## 9. Security Architecture

### 9.1 Network Security

**Transport Layer:**
- All client connections: HTTPS (TLS 1.2+) via CloudFront
- WebSocket connections: WSS (WebSocket Secure)
- Backend-to-backend: HTTPS (AWS internal network)
- Certificate management: AWS Certificate Manager (auto-renewal)

**Access Control:**
- Frontend S3 bucket: Private (no public access)
- CloudFront → S3: Origin Access Control (OAC) with IAM policy
- Backend → S3: IAM role-based access (no static keys)
- MongoDB: IP whitelist (AWS EB environment only) + TLS/SSL

**CORS Policy:**
```python
# Backend CORS configuration
allow_origins = [
    "https://d2dk8wkh2d0mmy.cloudfront.net",  # Production frontend
    "http://localhost:5173"                    # Development only
]
allow_credentials = False  # Stateless authentication
allow_methods = ["GET", "POST", "OPTIONS"]
allow_headers = ["*"]
```

### 9.2 Authentication & Authorization

**Current Implementation:**
- **Frontend:** No authentication (public demo)
- **Backend API:** No authentication required
- **WebSocket:** Open connection (rate-limited per IP)

**Production Enhancement Options:**
1. **SSO Integration:** SAML 2.0 / OAuth 2.0
2. **API Keys:** Per-user API key authentication
3. **JWT Tokens:** Stateless session management
4. **Rate Limiting:** Per-user quotas

### 9.3 Data Security

**Secrets Management:**
- API keys: Stored in AWS EB environment configuration (encrypted at rest)
- Database credentials: MongoDB Atlas connection string (encrypted)
- No secrets in source code or version control
- `.env` files: Git-ignored, never committed

**Data Encryption:**
- At rest: MongoDB Atlas (AES-256), S3 (SSE-S3)
- In transit: TLS 1.2+ for all connections
- Artifact files: Not encrypted (public artifacts, no PII)

**PII Handling:**
- User queries: Not stored long-term (90-day TTL)
- Session data: Anonymized session IDs
- No collection of: email, IP addresses, personal identifiers

---

## 10. Scalability & Reliability

### 10.1 Horizontal Scaling

**Auto-Scaling Configuration:**
```yaml
# .ebextensions/02_auto_scaling.config
aws:autoscaling:asg:
  MinSize: 1
  MaxSize: 5
  Cooldown: 360

aws:autoscaling:trigger:
  MeasureName: CPUUtilization
  Statistic: Average
  Unit: Percent
  UpperThreshold: 70    # Scale up if CPU > 70% for 5 min
  UpperBreachScaleIncrement: 1
  LowerThreshold: 30    # Scale down if CPU < 30% for 10 min
  LowerBreachScaleIncrement: -1
```

**Scaling Behavior:**
- **Scale up:** Add 1 instance every 5 minutes until CPU < 70%
- **Scale down:** Remove 1 instance every 10 minutes until CPU > 30%
- **Health checks:** ALB checks `/health` every 30s, unhealthy instances replaced
- **Connection draining:** 300s grace period for WebSocket connections

**Load Distribution:**
- ALB uses round-robin across healthy instances
- WebSocket connections pinned to instance (sticky)
- Stateless design allows horizontal scaling without session affinity

### 10.2 Reliability Mechanisms

**Retry Logic:**
```python
# Exponential backoff for Tavily API
attempts = 0
delay = 2  # seconds

while attempts < 3:
    try:
        result = await tavily.search(query)
        break
    except RateLimitError:
        attempts += 1
        if attempts < 3:
            await asyncio.sleep(delay)
            delay *= 2  # 2s → 4s → 8s
        else:
            # Graceful degradation
            result = get_cached_result() or inform_user()
```

**Circuit Breaker Pattern:**
- Not implemented (future enhancement)
- Would prevent cascading failures from external API outages

**Health Monitoring:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "mongodb": await check_mongodb(),
            "s3": await check_s3(),
            "openai": "not checked",  # Avoid rate limits
            "tavily": "not checked"
        }
    }
```

### 10.3 Disaster Recovery

**Backup Strategy:**
- **MongoDB:** Automatic daily backups (Atlas managed)
- **S3 artifacts:** No backups (30-day lifecycle, regenerable)
- **Application code:** Git repository (GitHub)
- **Configuration:** Stored in EB environment (exportable)

**Recovery Time Objective (RTO):**
- Backend failure: 3-5 minutes (auto-scaling replaces instance)
- Region failure: 30-60 minutes (deploy to new region)
- Database failure: 2-4 hours (restore from MongoDB Atlas backup)

**Recovery Point Objective (RPO):**
- Session data: Up to 5 minutes (MongoDB async writes)
- Artifacts: No data loss (synchronous S3 uploads)
- Execution logs: Up to 1 minute (buffered writes)

### 10.4 Monitoring & Observability

**Metrics Collected:**
- **Application:** Request count, response time, error rate
- **Infrastructure:** CPU, memory, network I/O, disk I/O
- **External APIs:** Tavily call count, OpenAI token usage, error rates
- **Business:** Queries per day, popular query types, user engagement

**Logging:**
```python
# Structured logging with LangFuse
@observe(name="sentiment_analyzer_node")
async def analyze_sentiment(state):
    # Automatic tracing:
    # - Function execution time
    # - Input/output sizes
    # - LLM token usage
    # - Error stack traces
    pass
```

**Alerting (Future):**
- Error rate > 5%: Alert via email/Slack
- Response time > 60s: Warning notification
- Tavily rate limit exceeded: Informational alert
- Instance health check failure: Critical alert

---

## 11. Cost Analysis

### 11.1 Monthly Cost Breakdown

| Service | Resource | Monthly Cost |
|---------|----------|--------------|
| **EC2 (EB)** | 1 × t3.micro (baseline) | $7.50 |
| **EC2 (EB)** | Auto-scaling overhead (avg) | $3-8 |
| **Application LB** | ALB (fixed) | $16.00 |
| **CloudFront** | 2 distributions + data transfer | $2-10 |
| **S3 Storage** | Artifacts (with lifecycle) | $0.50 |
| **MongoDB Atlas** | M0 Free Tier | $0.00 |
| **Data Transfer** | Outbound (avg 50 GB/month) | $4-6 |
| **Route 53** | Hosted zone + queries | $0.50 |
| **TOTAL** | | **$26-34/month** |

**Previous cost:** $103/month (3 EB environments, t3.small)  
**Current cost:** $26/month (1 EB environment, t3.micro, lifecycle policies)  
**Savings:** 71% reduction

**Cost Optimization Applied:**
1. Instance downsizing: t3.small → t3.micro ($7.50/month savings)
2. Environment consolidation: 3 → 1 ($66/month savings)
3. S3 lifecycle policies: Auto-delete after 30 days ($0.30+/month savings)
4. CloudFront optimization: Reduced cache misses (bandwidth savings)

### 11.2 External API Costs

**OpenAI (GPT-4o-mini):**
- Input tokens: $0.15 per 1M tokens
- Output tokens: $0.60 per 1M tokens
- Typical query: 5,000 tokens total (3,000 input + 2,000 output)
- Cost per query: ~$0.0016
- 1,000 queries/month: ~$1.60

**Tavily Search API:**
- Pricing: Free tier (1,000 requests/month), then $0.01 per request
- Typical query: 3-5 searches
- Cost per query: $0.03-0.05 (after free tier)
- 1,000 queries/month: ~$30-50

**Total API costs (1,000 queries/month):** $32-52

**Combined infrastructure + API:** $58-86/month for 1,000 queries

---

## 12. Future Enhancements

### 12.1 Architecture Improvements

**Sequential Planning (High Priority):**
- Implement step-by-step execution with conditional branching
- Add replanning capability mid-execution
- Support for "Step 1 → Step 2 → Step 3" workflows
- Estimated effort: 2-3 weeks

**Agent Expansion (In Progress):**
- Complete remaining 6 sub-agents (Media Bias Detector, Fact Checker, etc.)
- Target: 9/9 agents operational by Q1 2026
- Estimated effort: 4-6 weeks

**Performance Optimization:**
- Implement caching layer (Redis) for frequently accessed data
- Parallel sub-agent execution for independent tasks
- LLM response streaming (chunk-by-chunk) for better perceived performance
- Estimated improvement: 30-40% faster for cached queries

### 12.2 Feature Additions

**Collaboration Features:**
- Multi-user sessions with shared analysis workspace
- Export to multiple formats (PDF, Word, PowerPoint)
- Annotation and commenting on artifacts
- Share analysis via unique URLs

**Advanced Analytics:**
- Historical sentiment trend tracking
- Comparative analysis dashboard
- Custom alert setup for political events
- Scheduled automated reports (daily/weekly SitReps)

### 12.3 Infrastructure Scaling

**Multi-Region Deployment:**
- Primary: us-east-1 (current)
- Secondary: eu-west-1 (Europe)
- Asia: ap-southeast-1 (Singapore)
- Benefit: <100ms latency globally

**Serverless Migration (Consideration):**
- Evaluate AWS Lambda + API Gateway for WebSocket support
- Potential cost savings at low traffic volumes
- Trade-off: Cold start latency (3-5 seconds)

---

## 13. Technical Specifications Summary

### 13.1 Technology Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React 19, TypeScript, Vite 7, Radix UI, Framer Motion |
| **Backend** | Python 3.11, FastAPI, LangGraph 0.6, LangChain |
| **AI/ML** | OpenAI GPT-4o-mini, Tavily Search API |
| **Visualization** | Plotly 5.x, Pillow (PIL), python-pptx |
| **Database** | MongoDB Atlas M0 (512 MB) |
| **Storage** | AWS S3 with CloudFront CDN |
| **Infrastructure** | AWS EB, ALB, CloudFront, Route 53 |
| **Observability** | LangFuse, CloudWatch, Application logs |

### 13.2 Key Metrics

| Metric | Value |
|--------|-------|
| **Response Time (Basic)** | 3-8 seconds |
| **Response Time (Sub-Agent)** | 30-45 seconds |
| **Concurrent Users** | 50+ (tested) |
| **Monthly Cost** | $26-34 (infrastructure) |
| **Uptime** | 99.5% target |
| **API Rate Limits** | Tavily: 50 req/min, OpenAI: 10K TPM |
| **State Size** | 150-300 KB per session |
| **Artifact Size** | 180 KB avg (PNG optimized) |

### 13.3 Operational Sub-Agents

| Agent | Status | Execution Time | Artifacts |
|-------|--------|----------------|-----------|
| **Sentiment Analyzer** | ✅ Operational | 30-40s | Bar charts, radar charts, bias reports |
| **Live Political Monitor** | ✅ Operational | 25-30s | JSON reports, explosive topics |
| **SitRep Generator** | ✅ Operational | 35-45s | PDF, HTML, TXT, JSON |
| **Media Bias Detector** | 🔄 In Development | TBD | Bias spectrum, comparison matrix |
| **Fact Checker** | 📋 Planned | TBD | Truth gauge, evidence chains |
| **Entity Extractor** | 📋 Planned | TBD | Network graphs, relationship maps |

---

## 14. Appendix

### 14.1 API Endpoints

```python
# Health Check
GET /health
Response: {"status": "healthy", "timestamp": "..."}

# API Documentation
GET /docs
Response: Interactive Swagger UI

# WebSocket Connection
WS /ws/analyze
Protocol: JSON messages (query, update, artifact, complete, error)

# Artifact Access (via CloudFront)
GET /api/artifacts/{artifact_id}.png
GET /api/artifacts/{artifact_id}.html
```

### 14.2 Configuration Files

**Key Configuration Files:**
- `backend_v2/app.py` - FastAPI application
- `backend_v2/langgraph_master_agent/graph.py` - LangGraph workflow
- `backend_v2/.ebextensions/` - EB environment configuration
- `Frontend_v2/vite.config.ts` - Vite build configuration
- `Frontend_v2/src/config.ts` - Frontend environment config

### 14.3 Deployment Artifacts

**Backend Package:**
- Size: ~22 MB (with dependencies)
- Format: ZIP archive
- Excludes: `.venv/`, `artifacts/`, `__pycache__/`, test files

**Frontend Build:**
- Size: ~2 MB (gzipped)
- Format: Static HTML/JS/CSS files
- Optimization: Tree-shaking, code splitting, minification

---

## 15. Contact & Support

**Live System:**
- Frontend: https://d2dk8wkh2d0mmy.cloudfront.net
- API Health: https://d1h4cjcbl77aah.cloudfront.net/health
- API Docs: https://d1h4cjcbl77aah.cloudfront.net/docs

**Documentation:**
- Architecture: This document
- Deployment Guide: `DEPLOYMENT_GUIDE.md`
- Agent Development: `backend_v2/START_HERE.md`
- API Reference: Available at `/docs` endpoint

**Repository:**
- GitHub: [Repository URL]
- License: MIT

---

**Document Version:** 2.0  
**Last Updated:** October 9, 2025  
**Status:** Production-Ready  
**Maintenance:** Active Development

---

*This architecture supports a production system processing 1,000+ queries per month with 99.5% uptime and <45s response time for complex analytical tasks.*

