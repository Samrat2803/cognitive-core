# Political Analyst Workbench - API Contracts

**Version:** 2.0.0  
**Date:** Sep 2025
**Status:** Contract for Parallel Development  

## Overview

This document defines the exact API contracts between Backend and Frontend teams. These contracts are **immutable during development** to enable parallel work.

### MVP Scope (Month 1)
- Endpoints included: `/health`, `/research` (legacy), `/api/chat/message`, `/api/analysis/execute`, `/api/analysis/{analysis_id}`
- WebSocket: `/ws/{session_id}` with basic progress messages (no auth)
- Authentication: None for MVP; JWT moves to Phase 2
- Exports, auth, idempotency headers, and role-based access move to Phase 2+

## Base Configuration

### API Base URLs
- **Development:** `http://localhost:8000`
- **Production Backend:** `http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com`

### Frontend URLs
- **Development:** `http://localhost:3000`
- **Production:** `https://dgbfif5o7v03y.cloudfront.net`

### WebSocket URLs
- **Development:** `ws://localhost:8000/ws`
- **Production:** `wss://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/ws`

### WebSocket Protocol (MVP)
- Heartbeat: server sends `{ "type": "ping", "timestamp": ISO8601 }` every 30s; client responds `{ "type": "pong" }`
- Rate limits: server may coalesce progress messages; target ≤ 10 msgs/sec per session
- Error envelope (applies to WS events):
```json
{ "type": "analysis_error", "analysis_id": "string", "error": { "code": "ERROR_CODE", "message": "string", "recoverable": true }, "timestamp": "ISO8601" }
```

### Environment Variables (Canonical)
- Frontend: `REACT_APP_API_URL`, `REACT_APP_WS_URL`
- Backend: set CORS origins to include `FRONTEND_URL`

### Authentication
- **MVP:** None (no auth enforced on MVP endpoints to enable rapid integration)
- **Phase 2:** Bearer JWT Token (`Authorization: Bearer <token>`), access 24h, refresh 7d

---

## 1. Authentication Endpoints
MVP: Deferred to Phase 2. Section retained for planning; not required to implement now.

### POST `/api/auth/login`
```json
// Request
{
  "username": "string",
  "password": "string"
}

// Response 200
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "user": {
    "id": "user_123",
    "username": "analyst1", 
    "role": "analyst",
    "created_at": "2024-12-01T10:00:00Z"
  }
}

// Response 401
{
  "success": false,
  "error": "Invalid credentials",
  "code": "AUTH_FAILED"
}
```

### POST `/api/auth/refresh`
```json
// Request
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

// Response 200
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

### GET `/api/auth/profile`
**Headers:** `Authorization: Bearer <token>`
```json
// Response 200
{
  "success": true,
  "user": {
    "id": "user_123",
    "username": "analyst1",
    "role": "analyst",
    "created_at": "2024-12-01T10:00:00Z",
    "last_login": "2024-12-15T14:30:00Z"
  }
}
```

---

## 2. Chat/Conversational Endpoints

### POST `/api/chat/message`
**Headers:** `Authorization: Bearer <token>`
```json
// Request
{
  "message": "Analyze Hamas sentiment in US, Iran, and Israel",
  "session_id": "session_abc123",
  "context": {
    "previous_queries": ["string"],
    "current_analysis_id": "analysis_456" // optional
  }
}

// Response 200 - Query Understanding
{
  "success": true,
  "response_type": "query_parsed",
  "parsed_intent": {
    "action": "sentiment_analysis",
    "topic": "Hamas", 
    "countries": ["United States", "Iran", "Israel"],
    "parameters": {
      "days": 7,
      "results_per_country": 20
    }
  },
  "confirmation": "I'll analyze Hamas sentiment across US, Iran, and Israel using the last 7 days of data. Proceed?",
  "analysis_id": "analysis_789"
}

// Response 200 - Direct Response
{
  "success": true,
  "response_type": "direct_response",
  "message": "I can help with geopolitical sentiment analysis. Try asking 'Analyze Hamas sentiment' or 'Compare US and Iran positions'.",
  "suggestions": [
    "Analyze Hamas sentiment",
    "Compare US and Iran positions on Israel",
    "Show me European countries sentiment on Ukraine"
  ]
}

// Response 400
{
  "success": false,
  "error": "Unable to understand query",
  "code": "QUERY_PARSE_FAILED",
  "suggestions": [
    "Try 'Analyze [topic] sentiment'",
    "Specify countries: 'Compare US and Iran views on [topic]'"
  ]
}
```

### POST `/api/chat/confirm-analysis`
**Headers:** `Authorization: Bearer <token>`
```json
// Request
{
  "analysis_id": "analysis_789",
  "confirmed": true,
  "modifications": {
    "countries": ["United States", "Iran", "Israel", "Germany"], // optional
    "days": 14 // optional
  }
}

// Response 200
{
  "success": true,
  "analysis_id": "analysis_789",
  "status": "queued",
  "estimated_completion": "2024-12-15T15:35:00Z",
  "websocket_session": "ws_session_456"
}
```

---

## 3. Analysis Endpoints

### POST `/api/analysis/execute`
**Headers:** `Authorization: Bearer <token>`
```json
// Request
{
  "query_text": "Hamas sentiment analysis",
  "parameters": {
    "countries": ["United States", "Iran", "Israel"],
    "days": 7,
    "results_per_country": 20,
    "include_bias_analysis": true
  },
  "session_id": "session_abc123"
}

// Response 200
{
  "success": true,
  "analysis_id": "analysis_789",
  "status": "processing",
  "estimated_completion": "2024-12-15T15:35:00Z",
  "websocket_session": "ws_session_456",
  "created_at": "2024-12-15T15:34:00Z"
}
```

### GET `/api/analysis/{analysis_id}`
**Headers:** `Authorization: Bearer <token>`
```json
// Response 200 - In Progress
{
  "success": true,
  "analysis_id": "analysis_789",
  "status": "processing",
  "progress": {
    "current_step": "analyzing_articles",
    "completion_percentage": 45,
    "processed_countries": ["United States"],
    "remaining_countries": ["Iran", "Israel"],
    "articles_processed": 28,
    "total_articles": 60
  },
  "estimated_completion": "2024-12-15T15:35:00Z"
}

// Response 200 - Completed
{
  "success": true,
  "analysis_id": "analysis_789", 
  "status": "completed",
  "query": {
    "text": "Hamas sentiment analysis",
    "parameters": {
      "countries": ["United States", "Iran", "Israel"],
      "days": 7,
      "results_per_country": 20
    }
  },
  "results": {
    "summary": {
      "overall_sentiment": -0.23,
      "countries_analyzed": 3,
      "total_articles": 57,
      "analysis_confidence": 0.89,
      "bias_detected": true,
      "completion_time_ms": 47340
    },
    "country_results": [
      {
        "country": "United States",
        "sentiment_score": -0.45,
        "confidence": 0.87,
        "articles_count": 19,
        "dominant_sentiment": "negative",
        "key_themes": ["conflict", "terrorism", "security"],
        "bias_analysis": {
          "bias_types": ["selection", "framing"],
          "bias_severity": 0.34,
          "notes": "Predominantly western media sources"
        }
      },
      {
        "country": "Iran", 
        "sentiment_score": 0.67,
        "confidence": 0.82,
        "articles_count": 18,
        "dominant_sentiment": "positive",
        "key_themes": ["resistance", "liberation", "solidarity"],
        "bias_analysis": {
          "bias_types": ["source", "language"],
          "bias_severity": 0.52,
          "notes": "Limited English language sources"
        }
      },
      {
        "country": "Israel",
        "sentiment_score": -0.78,
        "confidence": 0.91,
        "articles_count": 20,
        "dominant_sentiment": "very negative", 
        "key_themes": ["terrorism", "security threat", "violence"],
        "bias_analysis": {
          "bias_types": ["framing", "temporal"],
          "bias_severity": 0.41,
          "notes": "Focus on recent violent events"
        }
      }
    ],
    "methodology": {
      "search_terms_used": ["Hamas", "Hamas sentiment", "Hamas opinion"],
      "time_range": "2024-12-08 to 2024-12-15",
      "sources_diversity": {
        "media_types": ["news", "analysis", "opinion"],
        "languages": ["english", "arabic", "hebrew"],
        "credibility_range": [0.6, 0.9]
      }
    },
    "bias_summary": {
      "overall_bias_severity": 0.42,
      "most_common_bias": "selection",
      "recommendations": [
        "Include more diverse source types",
        "Add non-English language sources", 
        "Extend temporal range for balance"
      ]
    }
  },
  "created_at": "2024-12-15T15:34:00Z",
  "completed_at": "2024-12-15T15:35:17Z"
}
```

### GET `/api/analysis/history`
**Headers:** `Authorization: Bearer <token>`
**Query Params:** `?limit=10&offset=0&status=completed`
```json
// Response 200
{
  "success": true,
  "analyses": [
    {
      "analysis_id": "analysis_789",
      "query_text": "Hamas sentiment analysis",
      "status": "completed",
      "countries": ["United States", "Iran", "Israel"],
      "created_at": "2024-12-15T15:34:00Z",
      "completed_at": "2024-12-15T15:35:17Z",
      "summary": {
        "overall_sentiment": -0.23,
        "articles_analyzed": 57
      }
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

---

## 4. Monitoring/Real-time Endpoints

### WebSocket Connection: `/ws/{session_id}`
**Headers:** `Authorization: Bearer <token>`

#### Connection Message
```json
{
  "type": "connection_established",
  "session_id": "ws_session_456", 
  "timestamp": "2024-12-15T15:34:01Z"
}
```

#### Analysis Progress Messages
```json
{
  "type": "analysis_progress",
  "analysis_id": "analysis_789",
  "step": "searching_articles",
  "progress": {
    "completion_percentage": 25,
    "current_country": "United States",
    "articles_found": 15,
    "estimated_remaining_ms": 35000
  },
  "timestamp": "2024-12-15T15:34:15Z"
}

{
  "type": "analysis_progress", 
  "analysis_id": "analysis_789",
  "step": "analyzing_sentiment",
  "progress": {
    "completion_percentage": 60,
    "current_country": "Iran",
    "articles_processed": 33,
    "total_articles": 57,
    "partial_results": {
      "United States": {
        "sentiment_score": -0.45,
        "articles_count": 19
      }
    }
  },
  "timestamp": "2024-12-15T15:34:45Z"
}
```

#### Analysis Complete Message
```json
{
  "type": "analysis_complete",
  "analysis_id": "analysis_789",
  "status": "completed",
  "results_url": "/api/analysis/analysis_789",
  "timestamp": "2024-12-15T15:35:17Z"
}
```

#### Error Messages
```json
{
  "type": "analysis_error",
  "analysis_id": "analysis_789",
  "error": {
    "code": "EXTERNAL_API_FAILURE",
    "message": "Tavily API rate limit exceeded",
    "retry_after": 300,
    "recoverable": true
  },
  "timestamp": "2024-12-15T15:34:30Z"
}
```

---

## 5. Export Endpoints

### POST `/api/export/create`
**Headers:** `Authorization: Bearer <token>`
```json
// Request
{
  "analysis_id": "analysis_789",
  "format": "pdf", // "pdf", "csv", "json", "excel"
  "options": {
    "include_full_articles": false,
    "include_bias_details": true,
    "template": "executive_summary" // "executive_summary", "detailed", "technical"
  }
}

// Response 200
{
  "success": true,
  "export_id": "export_456",
  "status": "generating",
  "estimated_completion": "2024-12-15T15:36:00Z",
  "format": "pdf"
}
```

### GET `/api/export/{export_id}`
**Headers:** `Authorization: Bearer <token>`
```json
// Response 200 - In Progress
{
  "success": true,
  "export_id": "export_456",
  "status": "generating",
  "progress": 75,
  "estimated_completion": "2024-12-15T15:36:00Z"
}

// Response 200 - Completed
{
  "success": true,
  "export_id": "export_456", 
  "status": "completed",
  "download_url": "https://s3.amazonaws.com/exports/export_456.pdf",
  "expires_at": "2024-12-22T15:36:00Z",
  "file_size": 2048576,
  "format": "pdf"
}
```

### GET `/api/export/download/{export_id}`
**Headers:** `Authorization: Bearer <token>`
**Returns:** File download (binary)

---

## 6. System Endpoints

### GET `/health`
```json
// Response 200
{
  "status": "healthy",
  "timestamp": "2024-12-15T15:34:00Z",
  "version": "2.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy", 
    "external_apis": {
      "tavily": "healthy",
      "openai": "healthy"
    }
  }
}
```

### GET `/api/config`
**Headers:** `Authorization: Bearer <token>`
```json
// Response 200
{
  "success": true,
  "config": {
    "supported_countries": [
      "United States", "Iran", "Israel", "Germany", "United Kingdom",
      "France", "Russia", "China", "India", "Brazil"
    ],
    "max_countries_per_analysis": 5,
    "max_days_back": 30,
    "supported_export_formats": ["pdf", "csv", "json", "excel"],
    "websocket_timeout_ms": 300000,
    "rate_limits": {
      "analyses_per_hour": 10,
      "exports_per_hour": 5
    }
  }
}
```

---

## Error Response Format

All endpoints use consistent error response format:

```json
{
  "success": false,
  "error": "Human readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details",
    "trace_id": "trace_123"
  },
  "timestamp": "2024-12-15T15:34:00Z"
}
```

### Common Error Codes
- `AUTH_REQUIRED` - Authentication required
- `AUTH_FAILED` - Invalid credentials
- `AUTH_EXPIRED` - Token expired
- `INVALID_REQUEST` - Request validation failed
- `RATE_LIMITED` - Rate limit exceeded
- `ANALYSIS_NOT_FOUND` - Analysis ID not found
- `EXPORT_FAILED` - Export generation failed
- `EXTERNAL_API_FAILURE` - External service failure
- `SERVER_ERROR` - Internal server error

---

## Rate Limits

- **Authentication:** 10 requests/minute per IP
- **Analysis execution:** 10 analyses/hour per user
- **Export generation:** 5 exports/hour per user
- **WebSocket connections:** 5 concurrent per user
- **General API:** 1000 requests/hour per user

---

## WebSocket Message Types Reference

| Type | Description | Direction |
|------|-------------|-----------|
| `connection_established` | WebSocket connection confirmed | Server → Client |
| `analysis_progress` | Real-time analysis updates | Server → Client |
| `analysis_complete` | Analysis finished successfully | Server → Client |
| `analysis_error` | Analysis encountered error | Server → Client |
| `ping` | Connection keep-alive | Server ↔ Client |
| `pong` | Connection keep-alive response | Server ↔ Client |

---

## Development Notes

### Mock Data
- Backend team should provide mock data endpoints for frontend development
- Frontend team should implement mock API service for offline development

### Testing
- All endpoints must have integration tests
- WebSocket functionality must be tested with real connections
- Error scenarios must be thoroughly tested

### Versioning
- API version in URL path: `/api/v1/`  
- Breaking changes require new version
- Backward compatibility maintained for 6 months

---

**Status:** ✅ Contract Approved  
**Next Review:** When implementation starts  
**Contact:** Architecture team for clarifications