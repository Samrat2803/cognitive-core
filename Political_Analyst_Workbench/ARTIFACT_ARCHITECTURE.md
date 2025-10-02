# Political Analyst Artifact System Architecture

## Overview

This document outlines the architecture for implementing ChatGPT-style artifacts with session management, user history, and multi-format output generation.

## Architecture Components

### 1. User & Session Management

```python
User
  ├── user_id: str (unique identifier)
  ├── profile: UserProfile
  ├── sessions: List[Session]
  └── preferences: Dict

Session
  ├── session_id: str (unique)
  ├── user_id: str
  ├── created_at: datetime
  ├── threads: List[Thread]
  └── metadata: Dict

Thread
  ├── thread_id: str (LangGraph thread ID)
  ├── session_id: str
  ├── conversation_history: List[Message]
  ├── artifacts: List[Artifact]
  └── state_checkpoints: List[Checkpoint]
```

### 2. Artifact Schema

```python
Artifact
  ├── artifact_id: str (unique)
  ├── thread_id: str
  ├── user_id: str
  ├── type: ArtifactType (viz, ppt, doc, reel, report)
  ├── title: str
  ├── content: Dict (format-specific content)
  ├── metadata: Dict
  │   ├── created_by_node: str
  │   ├── input_query: str
  │   ├── sources: List[Source]
  │   └── generation_params: Dict
  ├── storage_path: str (S3/MongoDB)
  ├── version: int
  ├── created_at: datetime
  └── updated_at: datetime

ArtifactType (Enum):
  - VISUALIZATION (charts, graphs, maps)
  - PRESENTATION (PowerPoint, Google Slides)
  - DOCUMENT (Word, PDF, Markdown)
  - REEL (Short video/animation)
  - REPORT (Comprehensive analysis document)
  - DATA_EXPORT (CSV, Excel, JSON)
```

### 3. LangGraph State Extension

```python
class ArtifactAgentState(TypedDict):
    # Standard fields
    conversation_history: List[Dict]
    current_message: str
    session_id: str
    thread_id: str  # NEW
    user_id: str    # NEW
    
    # Artifact-specific
    artifacts: List[Artifact]  # NEW
    artifact_requests: List[ArtifactRequest]  # NEW
    current_artifact: Optional[Artifact]  # NEW
    
    # Tool execution
    tool_results: Dict
    sub_agent_results: Dict
    
    # Standard output
    final_response: str
    citations: List[Dict]
    metadata: Dict
```

### 4. Graph Architecture with Artifacts

```
START
  ↓
[Conversation Manager]
  ├─ Load user session
  ├─ Load thread history
  └─ Check for artifact context
  ↓
[Strategic Planner]
  ├─ Determine if artifact needed
  └─ Select artifact type
  ↓
[Tool Executor / Analysis]
  ├─ Gather data
  └─ Process information
  ↓
[Artifact Decision Gate]  ← NEW NODE
  ├─ Should create artifact?
  ├─ What type?
  └─ What tools needed?
  ↓
┌────────────────────────────┐
│  ARTIFACT CREATION BRANCH  │
├────────────────────────────┤
│ [Visualization Creator]    │
│ [PPT Creator]              │
│ [Document Creator]         │
│ [Reel Creator]             │
│ [Report Generator]         │
└────────────────────────────┘
  ↓
[Artifact Saver]  ← NEW NODE
  ├─ Save to storage
  ├─ Link to thread
  └─ Update user history
  ↓
[Response Synthesizer]
  ├─ Include artifact reference
  └─ Provide download/view link
  ↓
END
```

### 5. Database Schema (MongoDB)

```javascript
// Users Collection
{
  _id: ObjectId,
  user_id: "user_123",
  email: "analyst@example.com",
  profile: {
    name: "John Analyst",
    organization: "Political Institute",
    role: "Senior Analyst"
  },
  preferences: {
    default_artifact_format: "ppt",
    visualization_style: "professional",
    color_scheme: "blue"
  },
  created_at: ISODate,
  last_active: ISODate
}

// Sessions Collection
{
  _id: ObjectId,
  session_id: "session_456",
  user_id: "user_123",
  title: "US Election Analysis",
  created_at: ISODate,
  updated_at: ISODate,
  metadata: {
    topic: "politics",
    region: "US"
  }
}

// Threads Collection (LangGraph Threads)
{
  _id: ObjectId,
  thread_id: "thread_789",  // LangGraph thread ID
  session_id: "session_456",
  user_id: "user_123",
  conversation_history: [
    {
      role: "user",
      content: "Analyze sentiment on climate policy",
      timestamp: ISODate
    },
    {
      role: "assistant",
      content: "Here's the analysis...",
      timestamp: ISODate,
      artifacts: ["artifact_001"]
    }
  ],
  state_snapshots: [
    // LangGraph checkpoints
  ],
  created_at: ISODate,
  updated_at: ISODate
}

// Artifacts Collection
{
  _id: ObjectId,
  artifact_id: "artifact_001",
  thread_id: "thread_789",
  session_id: "session_456",
  user_id: "user_123",
  type: "VISUALIZATION",
  title: "Climate Policy Sentiment by Country",
  content: {
    chart_type: "bar",
    data: [...],
    config: {...}
  },
  metadata: {
    created_by_node: "visualization_creator",
    input_query: "Analyze sentiment on climate policy",
    sources: [...],
    generation_params: {
      countries: ["US", "EU", "China"],
      time_range: "last_month"
    }
  },
  storage_path: "s3://artifacts/artifact_001.html",
  version: 1,
  created_at: ISODate,
  updated_at: ISODate
}
```

### 6. Persistence Implementation

**Using LangGraph Checkpointer:**

```python
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.graph import StateGraph

# Initialize MongoDB checkpointer
checkpointer = MongoDBSaver(
    connection_string=os.getenv("MONGODB_CONNECTION_STRING"),
    db_name="political_analyst_db"
)

# Create graph with persistence
app = workflow.compile(checkpointer=checkpointer)

# Use with thread_id for persistence
config = {
    "configurable": {
        "thread_id": "thread_789",  # Unique thread
        "user_id": "user_123"       # User context
    }
}

# Run graph - state automatically persisted
result = app.invoke(
    initial_state,
    config=config
)

# Resume from checkpoint
result = app.invoke(
    {"current_message": "Continue analysis"},
    config=config  # Same thread_id = continues from last state
)
```

### 7. Artifact Tools

**Tool Registry:**

```python
ARTIFACT_TOOLS = {
    "create_visualization": {
        "types": ["bar_chart", "line_graph", "map", "network_graph"],
        "libraries": ["plotly", "matplotlib", "folium"],
        "output": "HTML/PNG"
    },
    "create_presentation": {
        "format": "PPTX",
        "library": "python-pptx",
        "templates": ["professional", "academic", "executive"]
    },
    "create_document": {
        "formats": ["PDF", "DOCX", "Markdown"],
        "library": "reportlab/python-docx",
        "sections": ["summary", "analysis", "sources", "appendix"]
    },
    "create_reel": {
        "format": "MP4/GIF",
        "library": "moviepy",
        "templates": ["highlight", "timeline", "comparison"]
    },
    "export_data": {
        "formats": ["CSV", "Excel", "JSON"],
        "library": "pandas"
    }
}
```

### 8. API Endpoints

```python
# User Management
POST   /api/users/register
POST   /api/users/login
GET    /api/users/{user_id}/profile

# Session Management
POST   /api/sessions/create
GET    /api/sessions/{session_id}
GET    /api/users/{user_id}/sessions
DELETE /api/sessions/{session_id}

# Thread Management (LangGraph)
POST   /api/threads/create
GET    /api/threads/{thread_id}
GET    /api/threads/{thread_id}/history
POST   /api/threads/{thread_id}/message  # Send message to thread

# Artifact Management
GET    /api/artifacts/{artifact_id}
GET    /api/threads/{thread_id}/artifacts
GET    /api/users/{user_id}/artifacts
POST   /api/artifacts/create
PUT    /api/artifacts/{artifact_id}
DELETE /api/artifacts/{artifact_id}
GET    /api/artifacts/{artifact_id}/download
```

### 9. Frontend Flow

```
User logs in
  ↓
View Sessions Dashboard
  ├─ Active sessions
  ├─ Recent artifacts
  └─ Create new session
  ↓
Select/Create Session
  ↓
Chat Interface (Thread-based)
  ├─ Send message → LangGraph (with thread_id)
  ├─ Receive response + artifacts
  └─ View/Download artifacts
  ↓
Artifact Gallery
  ├─ Filter by type/date/session
  ├─ Preview artifacts
  ├─ Download/Share
  └─ Edit/Regenerate
```

### 10. Key Features

**Session Features:**
- Auto-save every interaction
- Resume from any point
- Branch conversations (fork threads)
- Share sessions with team

**Artifact Features:**
- Version control (artifact_v1, artifact_v2)
- Templates and themes
- Collaborative editing
- Export to multiple formats
- Embedding in reports

**History Management:**
- Full conversation replay
- Filter by topic/date/artifact type
- Search across all sessions
- Export conversation + artifacts

### 11. Implementation Phases

**Phase 1: Infrastructure (Week 1-2)**
- MongoDB setup for users/sessions/threads
- LangGraph checkpointer integration
- Basic session management API
- User authentication

**Phase 2: Artifact Framework (Week 3-4)**
- Artifact schema and storage
- Artifact decision gate node
- Basic artifact creators (viz, doc)
- Storage integration (S3/MongoDB)

**Phase 3: Tools Development (Week 5-8)**
- Visualization creator (Plotly/Matplotlib)
- PPT creator (python-pptx)
- Document creator (ReportLab)
- Data export tools

**Phase 4: History & UI (Week 9-10)**
- Session dashboard
- Artifact gallery
- History browser
- Download/share features

### 12. Example User Flow

```python
# User starts session
session = create_session(
    user_id="user_123",
    title="Climate Policy Analysis"
)

# Create thread in session
thread_id = create_thread(session_id=session.id)

# User: "Analyze global sentiment on climate policy"
response1 = agent.invoke(
    {"current_message": "Analyze global sentiment on climate policy"},
    config={"configurable": {"thread_id": thread_id, "user_id": "user_123"}}
)
# → Agent analyzes and creates visualization artifact

# User: "Now create a presentation from this"
response2 = agent.invoke(
    {"current_message": "Create a presentation from this"},
    config={"configurable": {"thread_id": thread_id}}  # Same thread
)
# → Agent uses previous context + artifact to create PPT

# User views artifacts
artifacts = get_thread_artifacts(thread_id)
# → Returns: [visualization_artifact, ppt_artifact]
```

## Technology Stack

**Backend:**
- LangGraph (orchestration + persistence)
- MongoDB (user/session/artifact storage)
- FastAPI (REST API)
- Redis (caching, real-time)

**Artifact Generation:**
- Plotly/Matplotlib (visualizations)
- python-pptx (presentations)
- ReportLab/python-docx (documents)
- MoviePy (video reels)
- Pandas (data exports)

**Storage:**
- MongoDB (metadata, small artifacts)
- S3/Cloud Storage (large artifacts, files)

**Frontend:**
- React (UI)
- Streamlit (quick prototyping)
- Chart.js/D3 (artifact preview)

## Benefits

1. **Persistence**: Every interaction saved, resume anytime
2. **Contextual**: Agent remembers previous artifacts
3. **Multi-format**: One analysis → multiple artifact types
4. **Collaborative**: Share sessions and artifacts
5. **Scalable**: Thread-based architecture supports millions of users
6. **Traceable**: Full audit trail of artifact creation

## Next Steps

1. Set up MongoDB with user/session/artifact collections
2. Implement LangGraph checkpointer
3. Create artifact decision gate node
4. Build first artifact creator (visualization)
5. Develop session management API
6. Build frontend session dashboard

---

**Last Updated:** October 1, 2025
**Version:** 1.0

