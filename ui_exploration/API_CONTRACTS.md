# API Contracts: Political Analyst Workbench
## Frontend ↔ Backend Communication Specification

**Last Updated:** 2025-10-01  
**Version:** 1.0.0

---

## 📋 **Overview**

This document defines the complete API contracts between the frontend (React) and backend (FastAPI) for the Political Analyst Workbench with **streaming support**.

### **Communication Patterns**

1. **WebSocket** - Real-time streaming (primary)
2. **REST API** - Non-streaming operations (fallback/history)

---

## 🔌 **WebSocket API (Streaming)**

### **Base URL**
```
ws://localhost:8000/ws/analyze
```

### **Connection Flow**

```typescript
// Frontend initiates WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/analyze');

ws.onopen = () => {
  console.log('Connected to Political Analyst');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleStreamMessage(message);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Connection closed');
};
```

---

## 📤 **Message Types: Client → Server**

### **1. Query Message** (Start Analysis)

```typescript
{
  type: "query",
  data: {
    query: string,              // User's question
    session_id?: string,        // Optional: Resume existing session
    context?: {                 // Optional: Additional context
      previous_queries?: string[],
      preferences?: object
    }
  },
  message_id: string            // Unique client-generated ID
}
```

**Example:**
```json
{
  "type": "query",
  "data": {
    "query": "Create a chart showing India's GDP growth from 2020-2025",
    "session_id": null
  },
  "message_id": "msg_1234567890"
}
```

---

### **2. Cancel Message** (Stop Streaming)

```typescript
{
  type: "cancel",
  data: {
    session_id: string          // Session to cancel
  },
  message_id: string
}
```

**Example:**
```json
{
  "type": "cancel",
  "data": {
    "session_id": "session_1759311175"
  },
  "message_id": "msg_cancel_123"
}
```

---

## 📥 **Message Types: Server → Client**

### **1. Connection Acknowledgment**

```typescript
{
  type: "connected",
  data: {
    connection_id: string,
    server_version: string,
    capabilities: string[]       // ["streaming", "artifacts", "citations"]
  },
  timestamp: string              // ISO 8601
}
```

**Example:**
```json
{
  "type": "connected",
  "data": {
    "connection_id": "conn_abc123",
    "server_version": "1.0.0",
    "capabilities": ["streaming", "artifacts", "citations"]
  },
  "timestamp": "2025-10-01T10:00:00Z"
}
```

---

### **2. Session Started**

```typescript
{
  type: "session_start",
  data: {
    session_id: string,
    query: string,
    started_at: string           // ISO 8601
  },
  message_id: string             // Echoes client message_id
}
```

**Example:**
```json
{
  "type": "session_start",
  "data": {
    "session_id": "session_1759311175",
    "query": "Create a chart showing India's GDP growth from 2020-2025",
    "started_at": "2025-10-01T10:00:01Z"
  },
  "message_id": "msg_1234567890"
}
```

---

### **3. Status Update** (Agent Progress)

```typescript
{
  type: "status",
  data: {
    session_id: string,
    status: "searching" | "analyzing" | "generating" | "finalizing",
    message: string,             // Human-readable status
    progress?: number            // 0-100 (optional)
  },
  timestamp: string
}
```

**Examples:**
```json
{
  "type": "status",
  "data": {
    "session_id": "session_1759311175",
    "status": "searching",
    "message": "🔍 Searching for India GDP data via Tavily...",
    "progress": 25
  },
  "timestamp": "2025-10-01T10:00:02Z"
}
```

```json
{
  "type": "status",
  "data": {
    "session_id": "session_1759311175",
    "status": "generating",
    "message": "📊 Creating visualization...",
    "progress": 75
  },
  "timestamp": "2025-10-01T10:00:08Z"
}
```

---

### **4. Content Stream** (Streaming Response Text)

```typescript
{
  type: "content",
  data: {
    session_id: string,
    content: string,             // Incremental text chunk
    delta: string,               // Same as content (for compatibility)
    is_complete: boolean         // True when done streaming
  },
  timestamp: string
}
```

**Example (Streaming):**
```json
{
  "type": "content",
  "data": {
    "session_id": "session_1759311175",
    "content": "### India's GDP Growth Analysis\n\nBased on World Bank",
    "delta": "### India's GDP Growth Analysis\n\nBased on World Bank",
    "is_complete": false
  },
  "timestamp": "2025-10-01T10:00:04.100Z"
}
```

```json
{
  "type": "content",
  "data": {
    "session_id": "session_1759311175",
    "content": " data, here are the trends:\n\n",
    "delta": " data, here are the trends:\n\n",
    "is_complete": false
  },
  "timestamp": "2025-10-01T10:00:04.250Z"
}
```

---

### **5. Citation** (Source References)

```typescript
{
  type: "citation",
  data: {
    session_id: string,
    citations: Array<{
      title: string,
      url: string,
      snippet?: string,
      published_date?: string,
      score?: number             // Relevance score 0-1
    }>
  },
  timestamp: string
}
```

**Example:**
```json
{
  "type": "citation",
  "data": {
    "session_id": "session_1759311175",
    "citations": [
      {
        "title": "India GDP Growth 2020-2025 - World Bank",
        "url": "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?locations=IN",
        "snippet": "India's GDP growth rate recovered strongly in 2021...",
        "published_date": "2024-09-15",
        "score": 0.95
      },
      {
        "title": "Economic Survey of India 2024",
        "url": "https://economicsurvey.gov.in",
        "snippet": "The Indian economy demonstrated resilience...",
        "score": 0.88
      }
    ]
  },
  "timestamp": "2025-10-01T10:00:05Z"
}
```

---

### **6. Artifact Generation** (Chart/Visualization)

```typescript
{
  type: "artifact",
  data: {
    session_id: string,
    artifact: {
      artifact_id: string,       // Unique ID (e.g., "line_abc123")
      type: "line_chart" | "bar_chart" | "pie_chart" | "table" | "map",
      title: string,
      description?: string,
      status: "generating" | "ready" | "failed",
      
      // URLs for artifact access
      html_url?: string,         // Interactive Plotly HTML
      png_url?: string,          // Static PNG image
      data_url?: string,         // Raw JSON data
      
      // Metadata
      created_at: string,
      size_bytes?: number
    }
  },
  timestamp: string
}
```

**Example (Generating):**
```json
{
  "type": "artifact",
  "data": {
    "session_id": "session_1759311175",
    "artifact": {
      "artifact_id": "line_abc123",
      "type": "line_chart",
      "title": "India GDP Growth Rate (2020-2025)",
      "status": "generating",
      "created_at": "2025-10-01T10:00:06Z"
    }
  },
  "timestamp": "2025-10-01T10:00:06Z"
}
```

**Example (Ready):**
```json
{
  "type": "artifact",
  "data": {
    "session_id": "session_1759311175",
    "artifact": {
      "artifact_id": "line_abc123",
      "type": "line_chart",
      "title": "India GDP Growth Rate (2020-2025)",
      "description": "Annual GDP growth rate from 2020-2025 based on World Bank data",
      "status": "ready",
      "html_url": "http://localhost:8000/api/artifacts/line_abc123.html",
      "png_url": "http://localhost:8000/api/artifacts/line_abc123.png",
      "data_url": "http://localhost:8000/api/artifacts/line_abc123/data.json",
      "created_at": "2025-10-01T10:00:08Z",
      "size_bytes": 4567323
    }
  },
  "timestamp": "2025-10-01T10:00:08Z"
}
```

---

### **7. Completion** (Analysis Done)

```typescript
{
  type: "complete",
  data: {
    session_id: string,
    summary: {
      total_time_ms: number,
      tokens_used?: number,
      tools_used: string[],      // ["tavily_search", "plotly_chart"]
      confidence: number,        // 0-1
      has_artifact: boolean
    }
  },
  timestamp: string
}
```

**Example:**
```json
{
  "type": "complete",
  "data": {
    "session_id": "session_1759311175",
    "summary": {
      "total_time_ms": 8450,
      "tokens_used": 1250,
      "tools_used": ["tavily_search", "plotly_chart"],
      "confidence": 0.85,
      "has_artifact": true
    }
  },
  "timestamp": "2025-10-01T10:00:10Z"
}
```

---

### **8. Error** (Something Went Wrong)

```typescript
{
  type: "error",
  data: {
    session_id?: string,
    error: {
      code: string,              // "TAVILY_ERROR", "RATE_LIMIT", etc.
      message: string,           // Human-readable error
      details?: object,          // Additional error context
      recoverable: boolean       // Can retry?
    }
  },
  timestamp: string
}
```

**Example:**
```json
{
  "type": "error",
  "data": {
    "session_id": "session_1759311175",
    "error": {
      "code": "TAVILY_RATE_LIMIT",
      "message": "Tavily API rate limit exceeded. Please wait 60 seconds.",
      "details": {
        "retry_after": 60,
        "quota_remaining": 0
      },
      "recoverable": true
    }
  },
  "timestamp": "2025-10-01T10:00:05Z"
}
```

---

## 🌐 **REST API (Fallback & History)**

### **1. Create Session (Non-Streaming)**

**Endpoint:** `POST /api/analyze`

**Request:**
```typescript
{
  query: string,
  user_session?: string         // Optional user identifier
}
```

**Response:**
```typescript
{
  success: boolean,
  session_id: string,
  query: string,
  response: string,              // Full markdown response
  citations: Array<Citation>,
  confidence: number,
  tools_used: string[],
  iterations: number,
  execution_log: Array<ExecutionStep>,
  artifact?: Artifact,
  processing_time_ms: number,
  errors?: string[]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Show India GDP growth 2020-2025"}'
```

---

### **2. Get Session History**

**Endpoint:** `GET /api/sessions/{session_id}`

**Response:**
```typescript
{
  session_id: string,
  query: string,
  response: string,
  citations: Array<Citation>,
  artifact?: Artifact,
  created_at: string,
  status: "completed" | "processing" | "failed"
}
```

---

### **3. List Recent Sessions**

**Endpoint:** `GET /api/sessions`

**Query Parameters:**
- `limit` (default: 10)
- `offset` (default: 0)

**Response:**
```typescript
{
  sessions: Array<{
    session_id: string,
    query: string,
    created_at: string,
    has_artifact: boolean,
    thumbnail_url?: string
  }>,
  total: number,
  has_more: boolean
}
```

---

### **4. Get Artifact**

**Endpoints:**
- `GET /api/artifacts/{artifact_id}.html` - Interactive HTML
- `GET /api/artifacts/{artifact_id}.png` - Static PNG
- `GET /api/artifacts/{artifact_id}/data.json` - Raw data

**Response:** Binary file (HTML/PNG/JSON)

---

### **5. Download Artifact**

**Endpoint:** `GET /api/artifacts/{artifact_id}/download`

**Query Parameters:**
- `format`: `html` | `png` | `json` | `all` (default: `html`)

**Response:** 
- Single file: Binary download
- `all`: ZIP archive with all formats

---

## 📦 **TypeScript Types (Frontend)**

```typescript
// types/messages.ts

export type MessageType =
  | "query"
  | "cancel"
  | "connected"
  | "session_start"
  | "status"
  | "content"
  | "citation"
  | "artifact"
  | "complete"
  | "error";

export interface ClientMessage {
  type: "query" | "cancel";
  data: QueryData | CancelData;
  message_id: string;
}

export interface QueryData {
  query: string;
  session_id?: string;
  context?: {
    previous_queries?: string[];
    preferences?: Record<string, any>;
  };
}

export interface CancelData {
  session_id: string;
}

export interface ServerMessage {
  type: MessageType;
  data: any;
  timestamp: string;
  message_id?: string;
}

export interface StatusMessage {
  type: "status";
  data: {
    session_id: string;
    status: "searching" | "analyzing" | "generating" | "finalizing";
    message: string;
    progress?: number;
  };
  timestamp: string;
}

export interface ContentMessage {
  type: "content";
  data: {
    session_id: string;
    content: string;
    delta: string;
    is_complete: boolean;
  };
  timestamp: string;
}

export interface Citation {
  title: string;
  url: string;
  snippet?: string;
  published_date?: string;
  score?: number;
}

export interface CitationMessage {
  type: "citation";
  data: {
    session_id: string;
    citations: Citation[];
  };
  timestamp: string;
}

export interface Artifact {
  artifact_id: string;
  type: "line_chart" | "bar_chart" | "pie_chart" | "table" | "map";
  title: string;
  description?: string;
  status: "generating" | "ready" | "failed";
  html_url?: string;
  png_url?: string;
  data_url?: string;
  created_at: string;
  size_bytes?: number;
}

export interface ArtifactMessage {
  type: "artifact";
  data: {
    session_id: string;
    artifact: Artifact;
  };
  timestamp: string;
}

export interface CompleteMessage {
  type: "complete";
  data: {
    session_id: string;
    summary: {
      total_time_ms: number;
      tokens_used?: number;
      tools_used: string[];
      confidence: number;
      has_artifact: boolean;
    };
  };
  timestamp: string;
}

export interface ErrorMessage {
  type: "error";
  data: {
    session_id?: string;
    error: {
      code: string;
      message: string;
      details?: Record<string, any>;
      recoverable: boolean;
    };
  };
  timestamp: string;
}
```

---

## 🐍 **Python Types (Backend)**

```python
# backend/types/messages.py

from typing import Literal, Optional, List, Dict, Any, Union
from pydantic import BaseModel
from datetime import datetime

MessageType = Literal[
    "query", "cancel", "connected", "session_start", 
    "status", "content", "citation", "artifact", "complete", "error"
]

class ClientMessage(BaseModel):
    type: Literal["query", "cancel"]
    data: Union["QueryData", "CancelData"]
    message_id: str

class QueryData(BaseModel):
    query: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class CancelData(BaseModel):
    session_id: str

class ServerMessage(BaseModel):
    type: MessageType
    data: Dict[str, Any]
    timestamp: str
    message_id: Optional[str] = None

class StatusData(BaseModel):
    session_id: str
    status: Literal["searching", "analyzing", "generating", "finalizing"]
    message: str
    progress: Optional[int] = None

class ContentData(BaseModel):
    session_id: str
    content: str
    delta: str
    is_complete: bool

class Citation(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    published_date: Optional[str] = None
    score: Optional[float] = None

class CitationData(BaseModel):
    session_id: str
    citations: List[Citation]

class Artifact(BaseModel):
    artifact_id: str
    type: Literal["line_chart", "bar_chart", "pie_chart", "table", "map"]
    title: str
    description: Optional[str] = None
    status: Literal["generating", "ready", "failed"]
    html_url: Optional[str] = None
    png_url: Optional[str] = None
    data_url: Optional[str] = None
    created_at: str
    size_bytes: Optional[int] = None

class ArtifactData(BaseModel):
    session_id: str
    artifact: Artifact

class CompleteData(BaseModel):
    session_id: str
    summary: Dict[str, Any]  # Contains total_time_ms, tools_used, etc.

class ErrorData(BaseModel):
    session_id: Optional[str] = None
    error: Dict[str, Any]  # Contains code, message, details, recoverable
```

---

## 🔄 **Complete Streaming Flow Example**

### **Timeline of Messages**

```
T+0ms     [CLIENT → SERVER]  {type: "query", data: {...}}
T+50ms    [SERVER → CLIENT]  {type: "session_start", data: {...}}
T+100ms   [SERVER → CLIENT]  {type: "status", data: {status: "searching"}}
T+2000ms  [SERVER → CLIENT]  {type: "citation", data: {citations: [...]}}
T+2100ms  [SERVER → CLIENT]  {type: "status", data: {status: "analyzing"}}
T+3000ms  [SERVER → CLIENT]  {type: "content", data: {content: "### India"}}
T+3100ms  [SERVER → CLIENT]  {type: "content", data: {content: "'s GDP"}}
T+3200ms  [SERVER → CLIENT]  {type: "content", data: {content: " Growth"}}
... (continue streaming)
T+6000ms  [SERVER → CLIENT]  {type: "status", data: {status: "generating"}}
T+6500ms  [SERVER → CLIENT]  {type: "artifact", data: {status: "generating"}}
T+8000ms  [SERVER → CLIENT]  {type: "artifact", data: {status: "ready"}}
T+8100ms  [SERVER → CLIENT]  {type: "content", data: {is_complete: true}}
T+8200ms  [SERVER → CLIENT]  {type: "complete", data: {...}}
```

---

## 🛡️ **Error Handling**

### **Connection Errors**
```typescript
// Frontend handles connection loss
ws.onclose = (event) => {
  if (event.code === 1000) {
    // Normal closure
    console.log('Connection closed normally');
  } else {
    // Abnormal closure - reconnect
    console.error('Connection lost, reconnecting...');
    setTimeout(() => reconnect(), 1000);
  }
};
```

### **Timeout Handling**
```typescript
// Frontend sets timeout for responses
const TIMEOUT_MS = 30000;  // 30 seconds

const timeoutId = setTimeout(() => {
  console.error('Query timeout');
  ws.send(JSON.stringify({
    type: "cancel",
    data: { session_id: currentSessionId }
  }));
}, TIMEOUT_MS);

// Clear timeout on completion
onComplete(() => clearTimeout(timeoutId));
```

---

## ✅ **Validation Rules**

### **Query Validation**
- **Min length:** 3 characters
- **Max length:** 2000 characters
- **Required:** query string

### **Session ID Format**
- Pattern: `session_[0-9]+`
- Example: `session_1759311175`

### **Artifact ID Format**
- Pattern: `{type}_{hash}`
- Example: `line_abc123`, `bar_xyz789`

---

## 📝 **Notes for Implementation**

1. **Streaming is Incremental**
   - Content messages contain deltas, not full text
   - Frontend must accumulate content

2. **Message Order Guaranteed**
   - WebSocket ensures FIFO order
   - No need for sequence numbers

3. **Idempotency**
   - Each query gets unique session_id
   - Duplicate queries create new sessions

4. **Graceful Degradation**
   - If WebSocket fails, fallback to REST API
   - Poll `/api/sessions/{id}` for updates

5. **Artifacts are Asynchronous**
   - Artifact may arrive before content completion
   - Status updates show progress

---

## 🚀 **Next Steps**

1. ✅ Review these contracts
2. ⬜ Implement frontend WebSocket client
3. ⬜ Update backend to emit these message types
4. ⬜ Add TypeScript types to frontend
5. ⬜ Add Pydantic models to backend
6. ⬜ Test streaming flow end-to-end

---

**Questions or Changes?** Let me know and I'll update the contracts!

