# Port Configuration - Political Analyst Workbench v2

**Updated:** October 2, 2025  
**Status:** ✅ All configurations updated

---

## 🔌 Port Assignments

| Service | Port | URL |
|---------|------|-----|
| **Backend** | 8001 | http://localhost:8001 |
| **Frontend** | 3000 | http://localhost:3000 |
| **WebSocket** | 8001 | ws://localhost:8001/ws/analyze |

---

## ✅ Updated Files

### Backend Configuration

**File:** `backend_v2/.env.example`
```env
PORT=8001
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**File:** `backend_v2/app.py`
- Default port configuration uses PORT env variable (defaults to 8001)

---

### Frontend Configuration

**File:** `frontend_v2/.env.example`
```env
VITE_BACKEND_URL=http://localhost:8001
VITE_WS_URL=ws://localhost:8001/ws/analyze
```

**File:** `frontend_v2/src/config.ts`
```typescript
export const config = {
  backendUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001',
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8001/ws/analyze',
  // ...
};
```

**File:** `frontend_v2/vite.config.ts`
```typescript
export default defineConfig({
  server: {
    port: 3000,
    host: true,
  },
  // ...
});
```

**File:** `frontend_v2/src/services/WebSocketService.ts`
```typescript
constructor(url: string = config.wsUrl) {
  this.url = url;  // Uses config.wsUrl (ws://localhost:8001/ws/analyze)
}
```

---

### Test Scripts Configuration

**File:** `test-backend-v2.sh`
```bash
uvicorn application:application --host 0.0.0.0 --port 8001 --reload
```

**File:** `test-frontend-v2.sh`
```bash
npm run dev  # Runs on port 3000 (configured in vite.config.ts)
```

**File:** `test-integration-v2.sh`
```bash
# Checks ports 8001 and 3000
# Tests http://localhost:8001/health
# References http://localhost:3000 for frontend
```

---

### Playwright Configuration

**File:** `frontend_v2/playwright.config.ts`
```typescript
export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
  },
  // ...
});
```

**File:** `frontend_v2/e2e/basic-integration.spec.ts`
- Tests run against http://localhost:3000
- Expects backend on port 8001

---

## 🚀 Quick Start Commands

### Start Backend (Port 8001)
```bash
cd backend_v2
cp .env.example .env
# Edit .env with API keys
source .venv/bin/activate
uvicorn application:application --host 0.0.0.0 --port 8001
```

### Start Frontend (Port 3000)
```bash
cd frontend_v2
cp .env.example .env  # Optional, defaults work
npm install
npm run dev
# Opens at http://localhost:3000
```

### Run Integration Tests
```bash
# Make sure both backend and frontend are running first
./test-integration-v2.sh
```

### Run Playwright E2E Tests
```bash
# Make sure both backend and frontend are running first
./run-playwright-tests.sh
```

---

## 🧪 Testing Checklist

### Manual Testing

**Backend (Port 8001):**
- [ ] Health check: `curl http://localhost:8001/health`
- [ ] API endpoint: `curl -X POST http://localhost:8001/api/analyze -H "Content-Type: application/json" -d '{"query": "test"}'`
- [ ] WebSocket: Connect to `ws://localhost:8001/ws/analyze`

**Frontend (Port 3000):**
- [ ] Open http://localhost:3000 in browser
- [ ] Connection indicator shows 🟢 (green/connected)
- [ ] Can type in message input
- [ ] Can send a query
- [ ] Receives streaming response

### Automated Testing

**Integration Tests:**
```bash
./test-integration-v2.sh
```

**Playwright E2E Tests:**
```bash
./run-playwright-tests.sh
```

---

## 🔧 Troubleshooting

### Port Already in Use

**Backend (8001):**
```bash
# Find process using port 8001
lsof -i :8001

# Kill process
lsof -ti:8001 | xargs kill -9
```

**Frontend (3000):**
```bash
# Find process using port 3000
lsof -i :3000

# Kill process
lsof -ti:3000 | xargs kill -9
```

### Connection Refused

**Check backend is running:**
```bash
curl http://localhost:8001/health
```

**Check frontend is running:**
```bash
curl http://localhost:3000
```

### CORS Errors

Make sure backend `.env` has:
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### WebSocket Connection Failed

1. Check backend logs for WebSocket errors
2. Verify `VITE_WS_URL=ws://localhost:8001/ws/analyze` in frontend `.env`
3. Check browser console for connection errors
4. Ensure backend WebSocket endpoint is accessible: `wscat -c ws://localhost:8001/ws/analyze`

---

## 📊 Configuration Summary

| Configuration | Old Value | New Value | Status |
|---------------|-----------|-----------|--------|
| Backend Port | 8000 | 8001 | ✅ Updated |
| Frontend Port | 5173 | 3000 | ✅ Updated |
| WebSocket Port | 8000 | 8001 | ✅ Updated |
| Backend CORS | localhost:5173 | localhost:3000 | ✅ Updated |
| Playwright baseURL | localhost:5173 | localhost:3000 | ✅ Updated |
| Test Scripts | Port 8000/5173 | Port 8001/3000 | ✅ Updated |

---

## ✅ All Files Updated

**Backend:**
- ✅ `backend_v2/.env.example`
- ✅ `backend_v2_configs/.ebignore`
- ✅ Backend uses PORT env variable

**Frontend:**
- ✅ `frontend_v2/.env.example`
- ✅ `frontend_v2/src/config.ts`
- ✅ `frontend_v2/vite.config.ts`
- ✅ `frontend_v2/src/services/WebSocketService.ts`
- ✅ `frontend_v2/playwright.config.ts`

**Test Scripts:**
- ✅ `test-backend-v2.sh`
- ✅ `test-frontend-v2.sh`
- ✅ `test-integration-v2.sh`

**Playwright:**
- ✅ `frontend_v2/playwright.config.ts`
- ✅ `frontend_v2/e2e/basic-integration.spec.ts`
- ✅ `run-playwright-tests.sh`

---

## 🎯 Next Steps

1. **Start Backend:**
   ```bash
   cd backend_v2 && source .venv/bin/activate && uvicorn application:application --host 0.0.0.0 --port 8001
   ```

2. **Start Frontend:**
   ```bash
   cd frontend_v2 && npm run dev
   ```

3. **Run Tests:**
   ```bash
   ./run-playwright-tests.sh
   ```

---

**All port configurations updated and ready for testing!** 🚀

