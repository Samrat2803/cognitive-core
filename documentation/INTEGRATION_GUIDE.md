# Integration & Deployment Guide

**Version:** 2.0.0  
**Date:** September 2025  
**Purpose:** End-to-end integration and deployment procedures  
**Status:** Ready for Implementation  

## 🎯 Integration Overview

This guide ensures seamless integration between Backend and Frontend teams, maintaining your existing deployment infrastructure while adding new conversational capabilities.

## 🔄 Integration Phases (MVP Simplified)

### MVP Scope Summary
- Backend: `/health`, legacy `/research` (kept), `/api/chat/message`, `/api/analysis/execute`, `/api/analysis/{analysis_id}`, WebSocket `/ws/{session_id}` (no auth)
- Frontend: Chat UI (submit, confirmation, results), basic WebSocket updates, results rendering
- No authentication, no Celery/queues, no export, no role-based access in MVP
- Production URLs unchanged; WebSocket must use `wss://` in production

### Canonical URLs & Environments (Use these everywhere)
| Environment | Frontend URL | API Base URL | WebSocket URL |
|-------------|--------------|--------------|---------------|
| Development | `http://localhost:3000` | `http://localhost:8000` | `ws://localhost:8000/ws` |
| Production  | `https://dgbfif5o7v03y.cloudfront.net` | `http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com` | `wss://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/ws` |

Environment variables:
- Frontend: `REACT_APP_API_URL`, `REACT_APP_WS_URL`
- Backend: `CORS_ORIGINS` must include the production Frontend URL

### Phase 1: Local Development Integration (Week 1–2)

#### Backend Integration Checklist
```bash
# 1. Start your enhanced backend
cd backend
source .venv/bin/activate
python app.py

# 2. Verify new endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/chat/message -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock_token" \
  -d '{"message": "test", "session_id": "test123"}'

# 3. Test WebSocket connection (no auth in MVP)
const ws = new WebSocket('ws://localhost:8000/ws/test123');
```

#### Frontend Integration Checklist
```bash
# 1. Start your enhanced frontend
cd frontend
npm start

# 2. Test chat interface
# Open http://localhost:3000
# Verify chat UI renders
# Test message sending
# Verify WebSocket connection

# 3. Test API integration
# Send test message
# Verify API calls to backend
# Check error handling
```

#### Integration Test Scenarios
1. **Chat Flow Test**
   - User sends message → Backend processes → Response received
   - WebSocket connection established → Real-time updates working
   - Error handling → Graceful failure modes

2. **Analysis Flow Test**  
   - Query parsing → Intent extraction → Confirmation flow
   - Analysis execution → Progress updates → Results display
   - Export functionality → File generation → Download working

---

### Phase 2: Staging Integration (Week 3)

#### Backend Staging Deployment

**Your existing AWS EB deployment process (unchanged):**
```bash
cd backend

# 1. Update environment variables in AWS EB Console
# - CORS_ORIGINS: Add your frontend staging URL
# - All existing API keys remain the same

# 2. Deploy using your existing process
eb deploy

# 3. Test staging backend
curl http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/health
```

#### Frontend Staging Deployment

**Your existing S3/CloudFront deployment process (unchanged):**
```bash
cd frontend

# 1. Update API configuration for staging
# Edit src/config.ts or create .env.staging

# 2. Build and deploy using your existing script
npm run build
./aws-deploy.sh

# 3. Test staging frontend
open https://dgbfif5o7v03y.cloudfront.net
```

#### Staging Integration Tests
```bash
# Test end-to-end flow
# Frontend (staging) → Backend (staging) → External APIs

# 1. Chat functionality
curl http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/api/chat/message \
  -X POST -H "Content-Type: application/json" \
  -d '{"message": "test integration", "session_id": "staging_test"}'

# 2. WebSocket connectivity  
# Test from staging frontend to staging backend WebSocket

# 3. Analysis pipeline
# Send real analysis request
# Verify POC integration working
# Check Tavily/OpenAI API calls successful
```

---

### Phase 3: Production Integration (Week 4)

#### Production Deployment Checklist

**Backend Production:**
- [ ] Environment variables configured in AWS EB
- [ ] CORS origins include production frontend URL
- [ ] Database connections tested
- [ ] External API keys validated
- [ ] Health checks passing
- [ ] WebSocket endpoints accessible
- [ ] Logging configured

**Frontend Production:**
- [ ] API URLs pointing to production backend
- [ ] S3/CloudFront deployment successful
- [ ] Cache invalidation completed
- [ ] HTTPS working correctly
- [ ] WebSocket connections secure (WSS)
- [ ] Error tracking configured
- [ ] Performance metrics enabled

#### Production Integration Validation
```bash
# 1. Backend health check
curl http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/health

# 2. Frontend loading
curl -I https://dgbfif5o7v03y.cloudfront.net

# 3. Cross-origin requests
# Test API calls from frontend to backend
# Verify CORS headers correct

# 4. WebSocket connection
# Test secure WebSocket from production frontend

# 5. End-to-end analysis
# Complete analysis workflow from production UI
```

---

## 🔧 Development Environment Setup

### Local Development with Backend/Frontend Separation

#### Backend Setup (Port 8000)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Environment variables
export TAVILY_API_KEY="your_tavily_key"
export OPENAI_API_KEY="your_openai_key"
export MONGODB_CONNECTION_STRING="your_mongodb_url"

python app.py
# Backend running at http://localhost:8000
```

#### Frontend Setup (Port 3000)
```bash
cd frontend  
npm install

# Environment variables
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
echo "REACT_APP_WS_URL=ws://localhost:8000" >> .env.local

npm start
# Frontend running at http://localhost:3000
```

### API Integration Configuration (Env-driven)

**File to update:** `frontend/src/config.ts`
```typescript
export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : 'http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com'),
  websocketURL: process.env.REACT_APP_WS_URL || (process.env.NODE_ENV === 'development' ? 'ws://localhost:8000' : 'wss://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com'),
  timeout: 120000
};
```

---

## 🧪 Testing Strategy

### Unit Tests (MVP Minimum)

#### Backend Unit Tests
```bash
cd backend

# Test core services
pytest tests/unit/test_conversational_engine.py
pytest tests/unit/test_poc_integration_service.py
pytest tests/unit/test_websocket_manager.py

# Test API routes
pytest tests/api/test_chat_routes.py
pytest tests/api/test_analysis_routes.py
```

#### Frontend Unit Tests
```bash
cd frontend

# Test components
npm test -- components/chat/ChatInterface.test.tsx
npm test -- hooks/useWebSocket.test.ts
npm test -- stores/chatStore.test.ts

# Test API integration
npm test -- services/apiService.test.ts
```

### Integration Tests (MVP Minimum)

#### API Integration Tests
```python
# tests/integration/test_chat_flow.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from websockets import connect

def test_chat_message_flow():
    """Test complete chat message flow"""
    client = TestClient(app)
    
    # 1. Send chat message
    response = client.post("/api/chat/message", json={
        "message": "Analyze Hamas sentiment",
        "session_id": "test_session"
    })
    assert response.status_code == 200
    
    # 2. Verify response structure
    data = response.json()
    assert "response_type" in data
    assert "parsed_intent" in data or "message" in data

async def test_websocket_connection():
    """Test WebSocket connection and messaging"""
    uri = "ws://localhost:8000/ws/test_session"
    async with connect(uri) as websocket:
        
        # Send ping
        await websocket.send("ping")
        response = await websocket.recv()
        assert response == "pong"
        
        # Test would continue with analysis flow...
```

#### End-to-End Tests (Playwright)
```typescript
// tests/e2e/chat-flow.spec.ts
import { test, expect } from '@playwright/test';

test('complete chat analysis flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // 1. Verify chat interface loaded
  await expect(page.locator('.chat-interface')).toBeVisible();
  
  // 2. Send a message
  await page.fill('.chat-input input', 'Analyze Hamas sentiment');
  await page.click('.chat-input button');
  
  // 3. Verify message appeared
  await expect(page.locator('.message.user')).toContainText('Analyze Hamas sentiment');
  
  // 4. Wait for response
  await expect(page.locator('.message.assistant')).toBeVisible({ timeout: 10000 });
  
  // 5. Test confirmation flow if applicable
  const confirmButton = page.locator('button:has-text("Yes, proceed")');
  if (await confirmButton.isVisible()) {
    await confirmButton.click();
    
    // 6. Verify analysis starts
    await expect(page.locator('.status-indicator.processing')).toBeVisible();
  }
});
```

---

## 🚀 Deployment Procedures

### Automated Deployment Pipeline (MVP)

#### Backend Deployment (AWS EB)
```bash
#!/bin/bash
# scripts/deploy-backend.sh

set -e

echo "🚀 Deploying Backend to AWS Elastic Beanstalk"

# 1. Run tests
cd backend
pytest tests/

# 2. Check configuration
python -c "from config import Config; assert Config.validate_config()"

# 3. Deploy to AWS EB (your existing process)
eb deploy

# 4. Health check
curl -f http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/health

echo "✅ Backend deployment complete"
```

#### Frontend Deployment (S3/CloudFront)
```bash
#!/bin/bash
# scripts/deploy-frontend.sh

set -e

echo "🚀 Deploying Frontend to S3/CloudFront"

# 1. Run tests
cd frontend
npm test -- --coverage --watchAll=false

# 2. Build for production
npm run build

# 3. Deploy using your existing script
./aws-deploy.sh

# 4. Health check
curl -f https://dgbfif5o7v03y.cloudfront.net

echo "✅ Frontend deployment complete"
```

#### Combined Deployment
```bash
#!/bin/bash
# scripts/deploy-full-stack.sh

set -e

echo "🚀 Full Stack Deployment"

# 1. Deploy backend first
./scripts/deploy-backend.sh

# 2. Wait for backend to be ready
sleep 30

# 3. Deploy frontend
./scripts/deploy-frontend.sh

# 4. Run integration tests
npm run test:e2e:production

echo "✅ Full stack deployment complete"
```

---

## 🔍 Monitoring & Debugging

### CI/CD Gates (MVP)
- Backend: lint, type-check, unit+integration tests must pass; build artifacts generated
- Frontend: lint, type-check, unit tests must pass; build succeeds
- E2E smoke: minimal Playwright spec hitting chat flow in staging
- Block deploy on failures; require manual approval for production

### Rollback Steps
- Backend (EB): use EB console or CLI to redeploy the previous application version
- Frontend (S3/CloudFront): re-sync previous build folder and create a full-path invalidation
- Record rollback reason and link to logs in TEAM_STATUS_TRACKING.md

### Backend Monitoring
```python
# Health check endpoint enhancement
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "services": {
            "database": await mongo_service.health_check(),
            "redis": await websocket_manager.health_check(),
            "external_apis": {
                "tavily": await check_tavily_api(),
                "openai": await check_openai_api()
            }
        },
        "metrics": {
            "active_websockets": websocket_manager.connection_count(),
            "active_analyses": len(poc_service.active_analyses),
            "memory_usage": get_memory_usage(),
            "uptime": get_uptime()
        }
    }
```

### Frontend Monitoring
```typescript
// Error boundary and monitoring
class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to monitoring service
    console.error('Frontend error:', error, errorInfo);
    
    // Report to error tracking (e.g., Sentry)
    if (window.analytics) {
      window.analytics.track('Frontend Error', {
        error: error.message,
        stack: error.stack,
        component: errorInfo.componentStack
      });
    }
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

### WebSocket Debugging
```typescript
// WebSocket connection debugging
export const debugWebSocket = (ws: WebSocket) => {
  ws.addEventListener('open', () => {
    console.log('🟢 WebSocket connected');
  });
  
  ws.addEventListener('message', (event) => {
    console.log('📨 WebSocket message:', JSON.parse(event.data));
  });
  
  ws.addEventListener('close', (event) => {
    console.log('🔴 WebSocket closed:', event.code, event.reason);
  });
  
  ws.addEventListener('error', (event) => {
    console.error('❌ WebSocket error:', event);
  });
};
```

---

## 🛠️ Troubleshooting Guide

### Common Integration Issues

#### CORS Issues
```javascript
// Problem: Frontend can't connect to backend
// Solution: Update CORS origins in backend

// Backend: app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://dgbfif5o7v03y.cloudfront.net",  // Your actual frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### WebSocket Connection Failures
```typescript
// Problem: WebSocket won't connect
// Solutions:

// 1. Check URL format
const wsUrl = `ws://localhost:8000/ws/${sessionId}`;  // Development
const wsUrl = `ws://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com/ws/${sessionId}`;  // Production

// 2. Handle connection errors
ws.addEventListener('error', (event) => {
  console.error('WebSocket connection failed:', event);
  // Implement retry logic or fallback
});

// 3. Check backend WebSocket handler
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()  # Don't forget this!
```

#### API Authentication Issues
```typescript
// Problem: 401 Unauthorized responses
// Solution: Check token handling

// Frontend: Ensure token is included
const response = await fetch('/api/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`  // Include token
  },
  body: JSON.stringify(data)
});
```

#### Environment Variable Issues
```bash
# Problem: Environment variables not loading
# Solutions:

# Backend: Check .env file exists
ls -la backend/.env

# Frontend: Check environment variables
echo $REACT_APP_API_URL

# AWS EB: Check environment variables in console
eb printenv
```

---

## 📊 Performance Optimization

### Backend Performance
```python
# Connection pooling
from motor.motor_asyncio import AsyncIOMotorClient

# Use connection pooling for MongoDB
mongo_client = AsyncIOMotorClient(
    connection_string,
    maxPoolSize=10,
    serverSelectionTimeoutMS=5000
)

# Redis connection pooling
redis_pool = aioredis.ConnectionPool.from_url(
    redis_url,
    max_connections=20
)
```

### Frontend Performance
```typescript
// Code splitting for better loading
const ChatInterface = lazy(() => import('./components/chat/ChatInterface'));
const AnalysisMonitor = lazy(() => import('./components/monitoring/AnalysisMonitor'));

// Memoization for expensive components
const MemoizedResultsExplorer = React.memo(ResultsExplorer);

// Debounced input handling
const debouncedSendMessage = useMemo(
  () => debounce((message: string) => {
    // Send message logic
  }, 300),
  []
);
```

---

## 🎯 Success Metrics

### Integration Success Criteria
- [ ] **Local Development:** Both teams can run full stack locally
- [ ] **API Integration:** All endpoints working according to contract
- [ ] **WebSocket Communication:** Real-time updates functioning
- [ ] **Authentication Flow:** Secure token-based auth working
- [ ] **Error Handling:** Graceful error handling throughout
- [ ] **Production Deployment:** Successfully deployed to existing infrastructure

### Performance Benchmarks
- [ ] **Page Load:** < 3 seconds first contentful paint
- [ ] **API Response:** < 200ms for chat endpoints (excluding analysis)
- [ ] **WebSocket Latency:** < 100ms message delivery
- [ ] **Analysis Speed:** < 60 seconds for complete analysis
- [ ] **Concurrent Users:** 50+ simultaneous users supported

### Quality Gates
- [ ] **Test Coverage:** >80% backend, >70% frontend
- [ ] **Integration Tests:** All critical paths covered
- [ ] **E2E Tests:** Complete user journeys working
- [ ] **Security Scan:** No critical vulnerabilities
- [ ] **Performance Test:** Load testing passed

---

**Document Status:** ✅ Complete  
**Last Updated:** [TIMESTAMP]  
**Review Schedule:** Daily during integration phase  
**Owner:** Architecture Team  
**Escalation:** Tag @architecture-lead for issues
