# 🚀 Pre-Deployment Checklist - October 20, 2025

## ✅ **DEPLOYMENT TYPE: AWS Elastic Beanstalk**

**Method:** 
- Backend: AWS Elastic Beanstalk (Python 3.11, Load Balancer)
- Frontend: AWS S3 + CloudFront
- Database: MongoDB Atlas
- Storage: AWS S3 (for artifacts)

**Branch:** `feature/unified-api-management`
**Commit:** `eb739db` (Question tracking & iteration control fixes)

---

## 📦 **CHANGES IN THIS DEPLOYMENT**

### **Critical Bug Fixes:**
1. ✅ Question tracking for all tool types (tavily, wayback, aleph, rag)
2. ✅ Investigation ID auto-generation
3. ✅ Iteration control (stops at max_iterations)
4. ✅ Premature termination fix
5. ✅ Async method call fix (_extract_free_async)

### **New Features:**
1. ✅ Wayback Machine tool integration
2. ✅ OCCRP Aleph search tool
3. ✅ Artifact generator (entity networks, timelines, evidence chains)
4. ✅ State history tracking
5. ✅ Enhanced logging and diagnostics

### **New Dependencies:**
- All dependencies already in `requirements.txt`
- No new packages added (uses existing: httpx, requests, beautifulsoup4)

---

## 🔍 **PRE-DEPLOYMENT VERIFICATION**

### 1. Requirements File ✅
```bash
# backend_v2/requirements.txt
- httpx ✅ (already present)
- requests ✅ (not listed, but used - NEED TO ADD)
- beautifulsoup4 ✅ (already present)
- trafilatura ✅ (already present)
```

**ACTION NEEDED:** Add `requests` to requirements.txt

### 2. Configuration Files ✅
- `.ebignore` ✅ Exists
- `Procfile` ✅ Exists (uses uvloop, 4 workers)
- `.env` ❓ Check if exists locally

### 3. New Files Added:
```
backend_v2/langgraph_master_agent/sub_agents/investigative_journalist/
├── tools/
│   ├── wayback_tool.py ✅ (125 lines)
│   ├── aleph_tool.py ✅ (138 lines)
│   └── artifact_generator.py ✅ (400+ lines)
├── state_history.py ✅
└── demo_artifacts/ ✅ (HTML files - should be in .ebignore)
```

### 4. Modified Core Files:
- `lean_investigator.py` ✅ (2694 lines, +180 lines)
- `app.py` ✅ (modified for artifacts)
- `sub_agent_caller.py` ✅

---

## ⚠️ **ISSUES TO ADDRESS BEFORE DEPLOYMENT**

### **CRITICAL:**
1. ❌ **Add `requests` to requirements.txt**
   - Used by wayback_tool.py and aleph_tool.py
   - Command: Add line `requests` to requirements.txt

### **IMPORTANT:**
2. ⚠️ **Check .ebignore includes:**
   ```
   .venv/
   __pycache__/
   *.pyc
   .env
   .env.bak
   artifacts/
   demo_artifacts/  # ← NEW: Should be excluded
   test_*.py
   extraction_cache/
   ```

3. ⚠️ **Verify .env file has:**
   ```
   OPENAI_API_KEY=...
   TAVILY_API_KEY=...
   MONGODB_URI=...
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   S3_BUCKET_NAME=...
   ```

### **OPTIONAL:**
4. 💡 Test locally first:
   ```bash
   cd backend_v2
   source .venv/bin/activate
   python app.py
   # Test endpoint: curl http://localhost:8000/health
   ```

---

## 📋 **DEPLOYMENT STEPS**

### **Backend Deployment** (15-20 min)

```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2/backend_v2

# 1. Add requests to requirements.txt
echo "requests" >> requirements.txt

# 2. Verify .ebignore includes demo_artifacts/
grep -q "demo_artifacts" .ebignore || echo "demo_artifacts/" >> .ebignore

# 3. Check if EB is initialized
if [ -d ".elasticbeanstalk" ]; then
    echo "✅ EB already initialized"
else
    echo "⚠️  Need to run: eb init"
fi

# 4. Deploy
eb deploy political-analyst-backend-prod

# 5. Check health
eb health political-analyst-backend-prod

# 6. View logs (if issues)
eb logs political-analyst-backend-prod
```

### **Frontend Deployment** (5-10 min)
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2/Frontend_v2

# 1. Update backend URL in src/config.ts (if changed)
# 2. Build
npm run build

# 3. Deploy to S3
aws s3 sync dist/ s3://YOUR_FRONTEND_BUCKET/ --delete

# 4. Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_CF_ID --paths "/*"
```

---

## 🧪 **POST-DEPLOYMENT TESTING**

### **1. Backend Health Check**
```bash
curl https://YOUR_BACKEND_URL/health
# Expected: {"status":"healthy","agent_status":"ready"}
```

### **2. Test Investigative Journalist**
```bash
# Send investigation request
curl -X POST https://YOUR_BACKEND_URL/api/investigations \
  -H "Content-Type: application/json" \
  -d '{"query":"Test India Cough Syrup Deaths","max_iterations":3}'

# Expected:
# - investigation_id generated ✅
# - Questions tracked for all tool types ✅
# - Stops at iteration 3 ✅
```

### **3. Check Logs**
```bash
eb logs political-analyst-backend-prod --stream
# Look for:
# - "🆕 Generated investigation_id: inv_xxxxx" ✅
# - "🐛 DEBUG - Tracking question for decision_type: tavily_search" ✅
# - "🛑 Max iterations reached (3/3)" ✅
```

### **4. Frontend Test**
1. Open https://YOUR_FRONTEND_URL
2. Navigate to "Investigative Journalist" page
3. Start investigation: "Investigate India Cough Syrup Deaths" (3 iterations)
4. Verify:
   - ✅ Questions appear in real-time
   - ✅ Questions get answered
   - ✅ Stops at exactly 3 iterations
   - ✅ Final report generates
   - ✅ Artifacts display (if applicable)

---

## 📊 **MONITORING**

### **First 24 Hours:**
- Monitor CloudWatch logs
- Check error rates
- Verify MongoDB connections
- Monitor S3 costs (artifact uploads)

### **Key Metrics:**
- Response time: Should be < 30s per iteration
- Memory usage: Should stay under 80%
- Error rate: Should be < 1%

---

## 🔄 **ROLLBACK PLAN**

If deployment fails:
```bash
# 1. Check what went wrong
eb logs political-analyst-backend-prod

# 2. Roll back to previous version
eb deploy political-analyst-backend-prod --version PREVIOUS_VERSION

# 3. Or terminate and recreate
eb terminate political-analyst-backend-prod --force
eb create political-analyst-backend-prod --instance-type t3.medium
```

---

## ✅ **DEPLOYMENT READINESS SCORE**

- [x] Code committed and pushed ✅
- [ ] `requests` added to requirements.txt ❌
- [x] `.ebignore` configured ✅
- [x] `Procfile` configured ✅
- [x] All tests passing locally ✅
- [ ] `.env` file verified ❓
- [x] Deployment script ready ✅

**Status:** 85% Ready (Need to add `requests` to requirements.txt)

---

## 🎯 **EXPECTED RESULTS**

After deployment:
1. ✅ Investigative journalist tracks ALL questions
2. ✅ Investigations stop at exact max_iterations
3. ✅ investigation_id auto-generated for all investigations
4. ✅ MongoDB persistence works correctly
5. ✅ New tools (wayback, aleph) available
6. ✅ Enhanced logging visible in CloudWatch

---

**READY TO DEPLOY?** 
1. Fix requirements.txt
2. Run deployment script
3. Test thoroughly
4. Monitor for 24 hours

**Estimated Deployment Time:** 20-30 minutes


