# Political Analyst Workbench - Monolithic Architecture Specification

**Version:** 2.0.0  
**Date:** September 2025  
**Status:** Approved for Implementation  

## Executive Summary

This document defines the monolithic backend architecture for the Political Analyst Workbench, maintaining separate backend and frontend deployments while enabling rapid parallel development.

## Architecture Overview

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                        │
│  React Frontend (Separate Deployment)                          │
│  • Conversational Chat Interface                               │
│  • Real-time Agent Monitoring Dashboard                        │
│  • Results Exploration & Visualization                         │
│  • Export & Reporting UI                                       │
│  Deployment: AWS S3 + CloudFront                               │
└─────────────────────────────────────────────────────────────────┘
                                    ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                           │
│  FastAPI Application (app.py)                                  │
│  • HTTP REST Endpoints                                         │
│  • WebSocket Connections                                       │
│  • Authentication & Authorization                              │
│  • Rate Limiting & Validation                                  │
└─────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                        │
│  Core Services (Monolithic)                                    │
│  • Conversational Query Engine                                 │
│  • POC Integration Service                                     │
│  • Real-time Streaming Manager                                │
│  • Export & Report Generator                                  │
└─────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                           │
│  • MongoDB (User sessions, analysis results)                   │
│  • Redis (Real-time state, caching)                           │
│  • S3 (Export files, reports)                                 │
└─────────────────────────────────────────────────────────────────┘
                                    ↕
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                           │
│  • Tavily API (Web Intelligence)                              │
│  • OpenAI API (Sentiment Analysis)                            │
│  • MongoDB Atlas (Database)                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Backend Monolithic Structure

```
backend/
├── app.py                           # Main FastAPI application
├── application.py                   # AWS EB entry point
├── config.py                        # Configuration management
├── requirements.txt                 # Python dependencies
├── Procfile                         # AWS EB deployment
├── .ebextensions/                   # AWS EB configuration
│
├── api/                             # API Route Handlers
│   ├── __init__.py
│   ├── chat_routes.py               # Conversational interface endpoints
│   ├── analysis_routes.py           # Analysis execution endpoints  
│   ├── monitoring_routes.py         # Real-time monitoring endpoints
│   ├── export_routes.py             # Export and reporting endpoints
│   └── auth_routes.py               # Authentication endpoints
│
├── core/                            # Business Logic Services
│   ├── __init__.py
│   ├── conversational_engine.py     # Natural language query processing
│   ├── poc_integration_service.py   # Wrapper for existing POC algorithms
│   ├── websocket_manager.py         # Real-time connection management
│   ├── export_service.py            # Report generation service
│   └── auth_service.py              # User authentication service
│
├── poc_agents/                      # Existing POC Integration
│   ├── __init__.py
│   ├── geo_sentiment_poc.py         # Moved from POCs/
│   ├── geo_sentiment_agent.py       # Moved from POCs/
│   ├── agent_utils.py               # Moved from POCs/
│   └── create_sources_review.py     # Moved from POCs/
│
├── services/                        # Data Access Services
│   ├── __init__.py
│   ├── mongo_service.py             # MongoDB operations (existing)
│   ├── analytics_service.py         # Analytics operations (existing)
│   ├── cache_service.py             # Redis caching service
│   └── storage_service.py           # File storage operations
│
├── models/                          # Data Models
│   ├── __init__.py
│   ├── base_model.py                # Base model classes (existing)
│   ├── query_models.py              # Query request/response models (existing)
│   ├── analysis_models.py           # Analysis result models
│   ├── user_models.py               # User and session models
│   └── websocket_models.py          # WebSocket message models
│
└── utils/                           # Utility Functions
    ├── __init__.py
    ├── validation.py                # Input validation helpers
    ├── formatting.py                # Response formatting
    ├── background_tasks.py          # Background processing
    └── logging_config.py            # Logging configuration
```

### 2. Frontend Structure (Unchanged)

```
frontend/
├── src/
│   ├── components/
│   │   ├── chat/                    # NEW - Conversational interface
│   │   ├── monitoring/              # NEW - Real-time agent monitoring
│   │   ├── results/                 # ENHANCED - Results exploration
│   │   └── export/                  # NEW - Export functionality
│   ├── hooks/
│   │   ├── useWebSocket.ts          # NEW - WebSocket connection
│   │   └── useChat.ts               # NEW - Chat interface logic
│   └── services/
│       └── api.ts                   # ENHANCED - API service layer
├── public/
└── deployment files (unchanged)
```

## Technology Stack (MVP)

### Backend Technologies
- **Framework:** FastAPI 0.104+
- **Language:** Python 3.11+
- **Database:** MongoDB Atlas (Redis optional post-MVP)
- **Real-time:** WebSocket
- **Background Tasks:** Deferred to Phase 3 (Celery optional)
- **Authentication:** Deferred to Phase 2 (JWT)
- **Deployment:** AWS Elastic Beanstalk
- **Monitoring:** AWS CloudWatch

### Frontend Technologies
- **Framework:** React 18+ TypeScript
- **State Management:** Zustand + React Query
- **WebSocket Client:** native WebSocket API
- **UI Components:** Custom components with Linear-inspired design
- **Deployment:** AWS S3 + CloudFront
- **Build Tool:** Create React App / Vite

## Data Flow Architecture

### 1. Conversational Interface Flow
```
User Input → Frontend Chat → API Gateway → Conversational Engine → 
POC Integration Service → External APIs → Response Processing → 
WebSocket Streaming → Frontend Updates → User Interface
```

### 2. Real-time Monitoring Flow
```
Analysis Start → WebSocket Connection → Backend Processing → 
Progress Updates → WebSocket Messages → Frontend Dashboard → 
User Monitoring Interface
```

### 3. Data Persistence Flow
```
Analysis Request → MongoDB Session Storage → Analysis Execution → 
Result Storage → Cache Updates → Export Generation → S3 Storage
```

## Security Architecture (MVP)

### Authentication Flow
- MVP: No authentication enforced; Phase 2 introduces JWT-based auth

### Data Security
- API keys stored in AWS EB environment variables
- Database connections encrypted (MongoDB Atlas)
- WebSocket uses `ws://` in dev, `wss://` in production
- Input validation on all endpoints
- CORS configured for `localhost:3000` and production frontend URL

## Deployment Architecture

### Backend Deployment (AWS Elastic Beanstalk)
```
Local Development → Git Push → AWS EB Deploy → 
Health Checks → Traffic Routing → Monitoring
```

### Frontend Deployment (AWS S3 + CloudFront)
```
Local Development → npm run build → S3 Upload → 
CloudFront Distribution → Global CDN → User Access
```

## Performance Requirements (MVP)

### Response Time Targets
- API endpoint response: < 200ms (excluding analysis)
- WebSocket message delivery: < 50ms
- Analysis completion: < 60 seconds (3 countries)
- Frontend page load: < 3 seconds

### Scalability Targets
- Concurrent users: 10 simultaneous (scale in Phase 2)
- WebSocket connections: 50 concurrent (scale in Phase 2)
- Analysis queue: 5 concurrent analyses (scale in Phase 2)
- Database operations: reasonable for MVP; add indexes post-MVP

### Resource Requirements
- Backend: AWS EB t3.medium minimum
- Database: MongoDB Atlas M10 minimum  
- Frontend: S3 Standard + CloudFront
- Cache: Redis 1GB minimum

## Integration Points

### External API Dependencies
1. **Tavily API**
   - Rate limits: Handled with backoff/retry
   - Failure handling: Graceful degradation
   - Data validation: Response structure validation

2. **OpenAI API**  
   - Rate limits: Queue management
   - Failure handling: Alternative models
   - Data validation: Input/output sanitization

### Internal Service Communication
- Synchronous: HTTP REST APIs
- Asynchronous: WebSocket messages  
- Background: Celery task queue
- Caching: Redis for session/state

## Monitoring and Observability

### Logging Strategy
- Structured JSON logging
- AWS CloudWatch integration
- Error tracking and alerting
- Performance metrics collection

### Health Checks
- Backend: `/health` endpoint
- Database: Connection status
- External APIs: Availability checks
- Real-time: WebSocket connection health

### Metrics Collection
- Request/response times
- Error rates by endpoint
- WebSocket connection counts
- Analysis completion rates

## Development Workflow

### Backend Development
1. Local development with `.env` file
2. Docker container for consistency
3. Unit tests with pytest
4. Integration tests with test database
5. AWS EB deployment for staging/production

### Frontend Development  
1. Local development server
2. Mock API responses for development
3. Component testing with Jest/React Testing Library
4. E2E testing with Playwright
5. S3/CloudFront deployment for staging/production

### Integration Testing
1. API contract validation
2. WebSocket message flow testing
3. End-to-end user journey testing
4. Performance and load testing
5. Security penetration testing

## Risk Mitigation

### Technical Risks
1. **Monolithic Complexity:** Modular code organization
2. **WebSocket Scale:** Connection pooling and management
3. **External API Limits:** Rate limiting and graceful degradation
4. **Database Performance:** Indexing and query optimization

### Operational Risks
1. **Deployment Issues:** Automated testing and rollback
2. **Data Loss:** Regular backups and replication
3. **Security Breaches:** Security audits and monitoring
4. **Performance Degradation:** Monitoring and alerting

## Success Criteria

### Technical Success
- All API endpoints responding < 200ms
- WebSocket connections stable for 1+ hours
- Analysis accuracy matches POC results (96%+)
- Zero data loss in production

### Business Success
- 50+ concurrent users supported
- Real-time monitoring functional
- Export functionality working
- User satisfaction > 85%

---

**Next Documents:**
- API_CONTRACTS.md - Detailed API specifications
- BACKEND_TEAM_GUIDE.md - Backend implementation guide
- FRONTEND_TEAM_GUIDE.md - Frontend implementation guide
- TEAM_STATUS_TRACKING.md - Team coordination system

## 🧪 MVP Acceptance Criteria (Pinned)
- End-to-end analysis completes under 60 seconds for 3 countries using production URLs
- WebSocket remains stable for 1 hour or auto-reconnects within 3 seconds
- Frontend and backend use env-based URLs; production envs validated in Integration Guide table
