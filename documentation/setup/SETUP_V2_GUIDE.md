# Political Analyst Workbench - Setup & Deployment Guide (v2)

**Complete guide for setting up clean production folders and deploying to AWS**

## 📋 Overview

This guide walks through creating clean `backend_v2` and `frontend_v2` folders, testing them locally, and deploying to AWS.

---

## 🎯 Step 0: Preparation (CURRENT STEP)

### What We're Doing

1. ✅ Check/terminate existing EB environments
2. ✅ Create setup scripts
3. ✅ Copy backend code to `backend_v2/`
4. ✅ Copy frontend code to `frontend_v2/`
5. ✅ Create configuration files
6. ✅ Run integrated tests
7. ✅ Verify everything works locally

### Files Created

**Setup Scripts:**
- ✅ `setup-backend-v2.sh` - Copy backend files
- ✅ `setup-frontend-v2.sh` - Copy frontend files

**Test Scripts:**
- ✅ `test-backend-v2.sh` - Test backend locally
- ✅ `test-frontend-v2.sh` - Test frontend locally
- ✅ `test-integration-v2.sh` - Test full integration

**Configuration Files (in backend_v2_configs/):**
- ✅ `requirements.txt` - Python dependencies
- ✅ `.ebignore` - EB deployment exclusions
- ✅ `01_python.config` - EB Python configuration
- ✅ `02_websocket.config` - EB WebSocket configuration
- ✅ `README.md` - Backend documentation

**Configuration Files (in frontend_v2_configs/):**
- ✅ `.env.example` - Environment template
- ✅ `config.ts` - Frontend configuration
- ✅ `README.md` - Frontend documentation

---

## 🚀 Quick Start

### Step 1: Run Setup Scripts

```bash
# 1. Create backend_v2
./setup-backend-v2.sh

# 2. Create frontend_v2
./setup-frontend-v2.sh
```

### Step 2: Copy Configuration Files

```bash
# Backend configurations
cp backend_v2_configs/requirements.txt backend_v2/
cp backend_v2_configs/.ebignore backend_v2/
cp -r backend_v2_configs/01_python.config backend_v2/.ebextensions/
cp -r backend_v2_configs/02_websocket.config backend_v2/.ebextensions/
cp backend_v2_configs/README.md backend_v2/

# Frontend configurations
cp frontend_v2_configs/.env.example frontend_v2/
cp frontend_v2_configs/config.ts frontend_v2/src/
cp frontend_v2_configs/README.md frontend_v2/
```

### Step 3: Configure Environment

```bash
# Backend
cd backend_v2
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - TAVILY_API_KEY
# - LANGSMITH_API_KEY (optional)
# - MONGODB_CONNECTION_STRING (optional)
# - AWS credentials (optional)

# Frontend
cd ../frontend_v2
cp .env.example .env
# Default values should work for local testing
```

### Step 4: Test Locally

```bash
# Terminal 1: Start backend
cd backend_v2
python -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn application:application --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend_v2
npm install
npm run dev

# Terminal 3: Run integration tests
./test-integration-v2.sh
```

---

## 📦 What Gets Copied

### Backend v2 (`Political_Analyst_Workbench/backend_server/` → `backend_v2/`)

**Included:**
- ✅ `app.py` - Main FastAPI application
- ✅ `application.py` - EB entry point
- ✅ `config_server.py` - Configuration
- ✅ `Procfile` - Process configuration
- ✅ `services/` - MongoDB and S3 services
- ✅ `langgraph_master_agent/` - Complete agent code
- ✅ `shared/` - Shared utilities
- ✅ `.ebextensions/` - EB configurations (NEW)

**Excluded:**
- ❌ `test_*.py` - Test files
- ❌ `verify_*.py` - Verification scripts
- ❌ `create_*.py` - Creation scripts
- ❌ `__pycache__/` - Python cache
- ❌ `archive/` - Old code
- ❌ `*.log` - Log files

### Frontend v2 (`ui_exploration/political-analyst-ui/` → `frontend_v2/`)

**Included:**
- ✅ Complete `src/` directory
- ✅ `package.json` & lock file
- ✅ All config files (vite, tsconfig, etc.)
- ✅ `public/` assets
- ✅ `.env.example` (NEW)
- ✅ `config.ts` (NEW)

**Excluded:**
- ❌ `node_modules/` - Dependencies (reinstall)
- ❌ `e2e/` - E2E tests
- ❌ `test-results/` - Test results
- ❌ `dist/` or `build/` - Build artifacts

---

## ✅ Integrated Testing Checklist

### Backend Tests

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0","agent_status":"ready"}

# Analyze endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'
# Expected: Streaming analysis with citations

# WebSocket
# Use browser console or wscat to test ws://localhost:8000/ws/analyze
```

**Checklist:**
- [ ] Backend starts without errors
- [ ] `/health` returns 200 OK
- [ ] `/api/analyze` accepts queries
- [ ] WebSocket `/ws/analyze` connects
- [ ] MongoDB connection works (if configured)
- [ ] S3 service available (if configured)
- [ ] No import errors in logs
- [ ] Agent responds to queries

### Frontend Tests

```bash
# Open browser
open http://localhost:5173
```

**Checklist:**
- [ ] Frontend loads without errors
- [ ] Connection status shows 🟢 (connected)
- [ ] Can type in message input
- [ ] Can send a query
- [ ] Receives streaming response
- [ ] Citations display correctly
- [ ] Progress bar updates
- [ ] Status messages appear
- [ ] No console errors in browser
- [ ] Artifacts display (if applicable)

### Integration Tests

**End-to-End Flow:**
- [ ] Frontend connects to backend
- [ ] Send query: "What is AI?"
- [ ] See status updates streaming in
- [ ] Response displays in chat
- [ ] Citations appear below response
- [ ] Artifact displays (if generated)
- [ ] Connection indicator stays green

**Reconnection Test:**
- [ ] Stop backend (Ctrl+C)
- [ ] Connection indicator turns 🔴
- [ ] Restart backend
- [ ] Connection indicator turns 🟢
- [ ] Can send queries again

**Error Handling:**
- [ ] Invalid query handling
- [ ] Network error handling
- [ ] WebSocket disconnect handling
- [ ] Empty response handling

---

## 🚢 Next Steps (After Testing)

Once all integrated tests pass, proceed to:

### Step 1: AWS Services Setup
- Create MongoDB Atlas cluster (free tier)
- Create S3 bucket for artifacts
- Configure IAM permissions

### Step 2: Backend Deployment
- Deploy `backend_v2/` to AWS Elastic Beanstalk
- Configure environment variables
- Test production endpoints

### Step 3: Frontend Deployment
- Build `frontend_v2/` for production
- Deploy to AWS S3 + CloudFront
- Update backend CORS configuration

### Step 4: Final Integration Testing
- Test production frontend → backend
- Verify WebSocket over HTTPS (wss://)
- Test artifact generation and S3 storage
- Complete end-to-end flow

---

## 📊 Project Structure Overview

```
exp_2/
├── Political_Analyst_Workbench/    # Original source code
│   ├── backend_server/             # Source for backend_v2
│   ├── langgraph_master_agent/     # Agent source
│   └── shared/                     # Utilities source
│
├── ui_exploration/
│   └── political-analyst-ui/       # Source for frontend_v2
│
├── backend_v2/                     # PRODUCTION BACKEND (new)
│   ├── app.py
│   ├── application.py
│   ├── .ebextensions/
│   ├── langgraph_master_agent/
│   ├── services/
│   └── shared/
│
├── frontend_v2/                    # PRODUCTION FRONTEND (new)
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── backend_v2_configs/             # Backend config templates
├── frontend_v2_configs/            # Frontend config templates
│
├── setup-backend-v2.sh             # Setup scripts
├── setup-frontend-v2.sh
├── test-backend-v2.sh              # Test scripts
├── test-frontend-v2.sh
└── test-integration-v2.sh
```

---

## 🔧 Troubleshooting

### Backend Issues

**Issue: Import errors for langgraph_master_agent**
```bash
# Verify directory structure
ls -la backend_v2/langgraph_master_agent/

# Check PYTHONPATH
echo $PYTHONPATH

# Solution: Add to .env
PYTHONPATH=/path/to/backend_v2:$PYTHONPATH
```

**Issue: Missing dependencies**
```bash
# Check requirements.txt exists
cat backend_v2/requirements.txt

# Reinstall
cd backend_v2
pip install -r requirements.txt
```

### Frontend Issues

**Issue: WebSocket connection fails**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check .env has correct URL
cat frontend_v2/.env

# Check browser console for errors
```

**Issue: Module not found**
```bash
# Clear cache and reinstall
cd frontend_v2
rm -rf node_modules package-lock.json
npm install
```

---

## 💡 Tips

1. **Keep terminals open:** Run backend and frontend in separate terminals
2. **Check logs:** Watch backend logs for errors
3. **Browser console:** Check frontend browser console for errors
4. **Port conflicts:** Ensure ports 8000 (backend) and 5173 (frontend) are free
5. **Virtual env:** Always activate venv before running backend
6. **Environment files:** Never commit `.env` files with real API keys

---

## 📝 Summary

**What we've accomplished:**

✅ Created clean `backend_v2/` and `frontend_v2/` folders  
✅ Separated production code from development/test code  
✅ Created AWS Elastic Beanstalk configurations  
✅ Added WebSocket support configurations  
✅ Created comprehensive test scripts  
✅ Documented everything thoroughly  

**Ready for:**

🚀 Local integrated testing  
🚀 AWS deployment  
🚀 Production rollout  

**Next Action:**

Run the setup scripts and perform integrated testing!

```bash
# Run all setup
./setup-backend-v2.sh
./setup-frontend-v2.sh

# Copy configs
# ... (see Step 2 above)

# Test everything
./test-integration-v2.sh
```

---

## 🎉 Success Criteria

The setup is successful when:

✅ Both setup scripts run without errors  
✅ Backend starts and responds to `/health`  
✅ Frontend loads in browser  
✅ WebSocket connection established (🟢)  
✅ Can send a query end-to-end  
✅ Response streams back to frontend  
✅ No console errors anywhere  

**Once all criteria are met, proceed to AWS deployment! 🚀**

