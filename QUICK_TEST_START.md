# 🚀 Quick Test Start Guide - V2 App

**Last Updated:** October 2, 2025

This guide helps you quickly test all features of the V2 application.

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Start Backend Server

```bash
# Terminal 1
cd backend_v2
source .venv/bin/activate
python app.py
```

**Wait for:** "🎯 Backend server ready!" message

### Step 2: Start Frontend Server

```bash
# Terminal 2
cd Frontend_v2
npm run dev
```

**Wait for:** Server running at http://localhost:5173

### Step 3: Run Backend Tests

```bash
# Terminal 3
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2
./run_tests.sh
```

**Expected:** All tests pass in ~3-5 minutes

---

## 📋 Manual Testing Checklist

### Frontend Testing (5 Minutes)

**File:** Open browser at http://localhost:5173

#### Test 1: Homepage
- [ ] Homepage loads
- [ ] Header displays "Cognitive Core"
- [ ] Live Monitor Dashboard visible
- [ ] Topics carousel working (if topics available)
- [ ] Search box functional

#### Test 2: Basic Query
- [ ] Enter query: "What is happening in Indian politics?"
- [ ] Click "Analyze →"
- [ ] Chat page opens
- [ ] Status updates appear
- [ ] AI response received (within 30 seconds)
- [ ] Citations displayed (if available)

#### Test 3: Artifact Generation
- [ ] Enter query: "Show me a visualization of GDP trends"
- [ ] Send message
- [ ] Artifact panel appears (right side)
- [ ] Chart/visualization loads
- [ ] Can view artifact (HTML/interactive)

#### Test 4: Multi-turn Conversation
- [ ] Ask follow-up: "How does this compare to 2020?"
- [ ] Response uses context from previous query
- [ ] Message history maintained

#### Test 5: Live Monitor
- [ ] Go back to homepage
- [ ] Check Live Monitor Dashboard
- [ ] Topics displayed (if available)
- [ ] Click on a topic
- [ ] Modal/details appear

---

## 🧪 Automated Test Results

After running `./run_tests.sh`, you should see:

```
==========================================
✅ ALL BACKEND TESTS PASSED!
==========================================

📊 Test Summary:
   ✅ API Health & Connectivity
   ✅ Master Agent Query Processing
   ✅ Sub-Agents Functionality
```

---

## 🔍 Detailed Testing (Optional)

### Test Specific Sub-Agents

#### Sentiment Analyzer
```bash
# In browser chat
Query: "Analyze sentiment about climate change in US, UK, France"
Expected: Response with sentiment analysis, possibly with artifacts
```

#### Live Monitor
```bash
# Via API
curl -X POST http://localhost:8000/api/live-monitor/explosive-topics \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["election", "Bihar"], "cache_hours": 1, "max_results": 5}'

Expected: JSON response with explosive topics
```

#### Media Bias Detector
```bash
# In browser chat
Query: "Analyze media bias on healthcare reporting"
Expected: Response analyzing bias in media coverage
```

#### SitRep Generator
```bash
# In browser chat
Query: "Generate a situation report for current events in South Asia"
Expected: Structured situation report
```

---

## 🐛 Troubleshooting

### Backend Not Starting

**Problem:** `❌ Backend server is not running!`

**Solution:**
```bash
cd backend_v2
source .venv/bin/activate

# Check .env file
cat .env | grep -E "OPENAI_API_KEY|TAVILY_API_KEY"

# If missing, create .env:
echo "OPENAI_API_KEY=your_key_here" >> .env
echo "TAVILY_API_KEY=your_key_here" >> .env

# Start server
python app.py
```

### Frontend Not Loading

**Problem:** http://localhost:5173 not accessible

**Solution:**
```bash
cd Frontend_v2

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Test Failures

**Problem:** Test fails with timeout

**Solution:**
- Check internet connection (API calls require network)
- Verify API keys are valid
- Increase timeout in test file (e.g., `timeout=120.0`)

**Problem:** "Connection refused"

**Solution:**
- Ensure backend server is running on port 8000
- Check firewall settings
- Try: `curl http://localhost:8000/health`

---

## 📊 Expected Test Times

| Test Suite | Duration | Notes |
|-----------|----------|-------|
| API Health | 5-10s | Fast, no LLM calls |
| Master Agent | 45-90s | Includes Tavily searches |
| Sub-Agents | 120-180s | Multiple agent calls |
| **Total Backend** | **3-5 minutes** | Sequential execution |

| Manual Test | Duration | Notes |
|------------|----------|-------|
| Homepage | 10s | Visual check |
| Basic Query | 30-60s | One analysis |
| Artifacts | 60-90s | Chart generation |
| Multi-turn | 45-60s | Two queries |
| **Total Frontend** | **5-10 minutes** | Interactive |

---

## ✅ Success Criteria

Your V2 app is working correctly if:

### Backend ✅
- [x] All health endpoints return 200
- [x] Simple queries return responses
- [x] Artifacts can be generated
- [x] At least 3 sub-agents work
- [x] WebSocket connection succeeds

### Frontend ✅
- [x] Homepage loads without errors
- [x] Chat interface functional
- [x] Messages send and receive
- [x] Artifacts display correctly
- [x] Live Monitor shows topics (if available)

---

## 📝 Test Report Template

After testing, fill this out:

```markdown
# Test Report - V2 App

**Date:** [Your Date]
**Tester:** [Your Name]

## Backend Tests
- API Health: ✅ Pass / ❌ Fail
- Master Agent: ✅ Pass / ❌ Fail
- Sub-Agents: ✅ Pass / ❌ Fail

## Frontend Tests
- Homepage: ✅ Pass / ❌ Fail
- Chat: ✅ Pass / ❌ Fail
- Artifacts: ✅ Pass / ❌ Fail
- Live Monitor: ✅ Pass / ❌ Fail

## Issues Found
1. [List any issues]

## Overall Status
Ready for Production: Yes / No
```

---

## 🎯 Next Steps

After all tests pass:

1. **Document Results:** Fill in test report
2. **Review Logs:** Check for warnings in console
3. **Performance Test:** Optional but recommended
4. **User Acceptance Testing:** Have someone else try it
5. **Deploy:** Follow deployment guide

---

## 📞 Need Help?

If tests fail or you need clarification:

1. Check `TESTING_PLAN_V2.md` for detailed test descriptions
2. Review logs in `backend_v2/app.log`
3. Check browser console for frontend errors
4. Review `SENTIMENT_VIZ_ARCHITECTURE.md` for architecture details

---

**Ready to test! 🚀**

Run `./run_tests.sh` to begin.

