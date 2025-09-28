# API Contracts - Web Research Agent

**Version:** 1.0  
**Team:** Backend Infrastructure (Team A)  
**Date:** 2024-09-27  
**Status:** ✅ APPROVED for Teams B & C Implementation

---

## 🔗 **Base Configuration**

```yaml
Base URL: https://your-app.elasticbeanstalk.com/api/v1
Content-Type: application/json
Rate Limit: 100 requests/minute per IP
Timeout: 120 seconds (research queries can take 60-90s)
```

---

## 📡 **API Endpoints**

### **1. Health Check**
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-09-27T10:30:00Z",
  "agent_initialized": true,
  "version": "1.0.0"
}
```

---

### **2. Submit Research Query**
```http
POST /research
```

**Request Body:**
```json
{
  "query": "What are the latest developments in quantum computing?",
  "user_session": "optional-session-id",
  "options": {
    "max_results": 10,
    "search_depth": "advanced",
    "export_format": "json"
  }
}
```

**Response (202 Accepted) - Async Processing:**
```json
{
  "query_id": "uuid-string",
  "status": "processing",
  "message": "Research query submitted successfully",
  "estimated_completion": "2024-09-27T10:32:30Z"
}
```

---

### **3. Get Research Results**
```http
GET /research/{query_id}
```

**Response (200 OK) - Completed:**
```json
{
  "query_id": "uuid-string",
  "status": "completed",
  "query": "What are the latest developments in quantum computing?",
  "final_answer": "## Quantum Computing Developments\n\n[Full formatted response]",
  "search_terms": ["quantum computing", "latest developments", "quantum algorithms"],
  "sources": [
    {
      "url": "https://example.com/quantum-news",
      "title": "Quantum Computing Breakthroughs 2024",
      "relevance_score": 0.95
    }
  ],
  "processing_time_ms": 45000,
  "created_at": "2024-09-27T10:30:00Z",
  "completed_at": "2024-09-27T10:31:15Z"
}
```

**Response (202 Accepted) - Still Processing:**
```json
{
  "query_id": "uuid-string",
  "status": "processing",
  "progress": 65,
  "current_step": "Analyzing search results",
  "estimated_completion": "2024-09-27T10:32:30Z"
}
```

---

### **4. Get Query History**
```http
GET /research?user_session={session_id}&limit={limit}&offset={offset}
```

**Response (200 OK):**
```json
{
  "queries": [
    {
      "query_id": "uuid-string",
      "query": "What are the latest developments in quantum computing?",
      "status": "completed",
      "created_at": "2024-09-27T10:30:00Z",
      "processing_time_ms": 45000
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

---

### **5. Export Research Results**
```http
GET /research/{query_id}/export?format={json|csv|pdf}
```

**Headers:**
```http
Accept: application/json|text/csv|application/pdf
```

**Response (200 OK):**
- **JSON**: Same as Get Results endpoint
- **CSV**: Tabular format with columns: query, answer, sources, timestamp
- **PDF**: Formatted research report

---

### **6. System Analytics** (Optional for Demo)
```http
GET /analytics
```

**Response (200 OK):**
```json
{
  "total_queries": 1250,
  "avg_processing_time_ms": 42000,
  "success_rate": 0.96,
  "popular_topics": ["AI", "quantum computing", "climate change"],
  "daily_query_count": 45
}
```

---

## ⚠️ **Error Responses**

### **Standard Error Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Query cannot be empty",
    "details": "The 'query' field is required and cannot be null or empty",
    "timestamp": "2024-09-27T10:30:00Z"
  }
}
```

### **HTTP Status Codes:**
| Code | Meaning | Use Case |
|------|---------|----------|
| `200` | OK | Successful GET requests |
| `202` | Accepted | Async processing started |
| `400` | Bad Request | Invalid query parameters |
| `404` | Not Found | Query ID not found |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server processing error |
| `503` | Service Unavailable | Agent not initialized |

### **Error Code Definitions:**
```typescript
enum ErrorCode {
  VALIDATION_ERROR = "VALIDATION_ERROR",
  QUERY_NOT_FOUND = "QUERY_NOT_FOUND", 
  RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED",
  AGENT_NOT_INITIALIZED = "AGENT_NOT_INITIALIZED",
  PROCESSING_FAILED = "PROCESSING_FAILED",
  EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
}
```

---

## 🗄️ **Database Contracts (for Team B)**

### **Collections Schema:**

#### **`queries` Collection:**
```typescript
interface QueryDocument {
  _id: ObjectId;
  query_id: string;         // UUID for external reference
  query_text: string;       // Original user query
  user_session?: string;    // Optional session tracking
  status: "processing" | "completed" | "failed";
  options: {
    max_results: number;
    search_depth: "basic" | "advanced";
    export_format: string;
  };
  created_at: Date;
  updated_at: Date;
  processing_started_at?: Date;
  completed_at?: Date;
  processing_time_ms?: number;
}
```

#### **`results` Collection:**
```typescript
interface ResultDocument {
  _id: ObjectId;
  query_id: string;         // Links to QueryDocument
  final_answer: string;     // Formatted research response
  search_terms: string[];   // Terms used for web search
  sources: {
    url: string;
    title: string;
    relevance_score: number;
  }[];
  agent_workflow: {
    step: string;
    duration_ms: number;
    output_summary: string;
  }[];
  created_at: Date;
}
```

#### **`analytics` Collection:**
```typescript
interface AnalyticsDocument {
  _id: ObjectId;
  date: Date;              // Daily aggregation
  total_queries: number;
  completed_queries: number;
  failed_queries: number;
  avg_processing_time_ms: number;
  popular_topics: string[];
  unique_sessions: number;
}
```

---

## 🔧 **Required Database Operations (Team B)**

```typescript
// Core operations Team B must implement
interface DatabaseService {
  // Query Management
  createQuery(query: QueryRequest): Promise<string>; // Returns query_id
  updateQueryStatus(queryId: string, status: QueryStatus): Promise<void>;
  getQuery(queryId: string): Promise<QueryDocument | null>;
  getUserQueries(userSession: string, limit: number, offset: number): Promise<QueryDocument[]>;
  
  // Results Management  
  saveResults(queryId: string, results: ResearchResults): Promise<void>;
  getResults(queryId: string): Promise<ResultDocument | null>;
  
  // Analytics
  recordAnalytics(queryId: string, processingTime: number): Promise<void>;
  getAnalytics(): Promise<AnalyticsDocument>;
}
```

---

## 🎨 **Frontend Integration Guide (Team C)**

### **React Hook Example:**
```typescript
// Custom hook for research queries
const useResearchQuery = () => {
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');
  const [results, setResults] = useState<ResearchResults | null>(null);
  
  const submitQuery = async (query: string) => {
    setStatus('processing');
    try {
      const response = await fetch('/api/v1/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      const { query_id } = await response.json();
      pollForResults(query_id);
    } catch (error) {
      setStatus('error');
    }
  };
  
  const pollForResults = async (queryId: string) => {
    // Implementation for polling results
  };
  
  return { status, results, submitQuery };
};
```

### **Required Frontend Components:**
1. **QueryForm**: Submit queries with validation
2. **ResultsDisplay**: Show formatted research results  
3. **LoadingIndicator**: Progress tracking during processing
4. **ErrorBoundary**: Handle API errors gracefully
5. **ExportButton**: Download results in various formats
6. **QueryHistory**: Display previous queries

---

## 🔒 **Security & Validation**

### **Request Validation:**
- Query text: 1-1000 characters, required
- User session: Optional UUID format
- Max results: 1-20, default 10
- Search depth: enum validation

### **Rate Limiting:**
- 100 requests per minute per IP
- Burst allowance: 10 requests
- Headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### **CORS Configuration:**
```javascript
{
  origin: ["https://your-frontend-domain.com"],
  methods: ["GET", "POST"],
  allowedHeaders: ["Content-Type", "Authorization"],
  credentials: true
}
```

---

## 📊 **Performance SLA**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time (Health) | < 200ms | P95 |
| Query Submission | < 1s | P95 |
| Research Completion | < 90s | P90 |
| Availability | 99.5% | Monthly uptime |

---

## 🚀 **Implementation Priority**

### **Phase 1 - Core API (Teams B & C can start):**
1. POST /research (query submission)
2. GET /research/{id} (result retrieval)
3. Database query/result operations
4. Basic error handling

### **Phase 2 - Enhanced Features:**
1. Query history
2. Export functionality  
3. Analytics endpoint
4. Rate limiting

### **Phase 3 - Production Polish:**
1. Advanced monitoring
2. Performance optimization
3. Security hardening
4. Documentation completion

---

**🔗 This contract is now APPROVED for Team B and Team C to begin implementation.**

**Teams B & C: You can start development immediately using these specifications. Any questions or clarifications needed, please coordinate through the established channels.**

---

*API Contract Version 1.0 - Team A (Backend Infrastructure)*