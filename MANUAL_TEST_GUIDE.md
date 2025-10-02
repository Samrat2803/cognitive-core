# Manual Testing Guide - Sentiment Analyzer Integration

## 🚀 Quick Start

### Start Backend
```bash
cd backend_v2
source .venv/bin/activate
uvicorn app:app --reload
```
**Backend URL:** http://localhost:8000

---

### Start Frontend
```bash
cd Frontend_v2
npm run dev
```
**Frontend URL:** http://localhost:3000

---

## 🎯 Test Queries to Prove Sentiment Analyzer Works

Copy-paste any of these into the chat interface:

### ✅ **Test Query 1: Direct Sentiment Request**
```
Analyze sentiment on nuclear energy policy across US, France, and Germany
```

**Expected Behavior:**
- ✅ Agent calls `sentiment_analysis_agent`
- ✅ Generates 3 artifacts (bar chart, radar chart, JSON)
- ✅ Response includes sentiment scores for each country
- ✅ Shows bias detection results
- ✅ Execution log shows sentiment analyzer steps

---

### ✅ **Test Query 2: International Perspective**
```
How do different countries view climate change policy?
```

**Expected Behavior:**
- ✅ Agent detects this needs sentiment analysis
- ✅ Analyzes multiple countries (US, UK, France by default)
- ✅ Creates visual comparisons
- ✅ Mentions bias detection

---

### ✅ **Test Query 3: Bias Detection Focus**
```
Give me an unbiased analysis of AI regulation from multiple perspectives
```

**Expected Behavior:**
- ✅ Triggers sentiment analyzer with bias detection
- ✅ Shows 7 types of bias analysis
- ✅ Provides balanced perspective across countries
- ✅ Generates comparison charts

---

### ✅ **Test Query 4: Geopolitical Comparison**
```
Compare how US, China, and Russia view renewable energy development
```

**Expected Behavior:**
- ✅ Multi-country sentiment analysis
- ✅ Extracts specific countries from query
- ✅ Creates sentiment comparison chart
- ✅ Shows bias analysis per country

---

### ✅ **Test Query 5: Short Sentiment Request**
```
Sentiment on Ukraine conflict across Europe
```

**Expected Behavior:**
- ✅ Agent recognizes "sentiment" keyword
- ✅ Calls sentiment analyzer
- ✅ Analyzes European countries
- ✅ Shows regional sentiment patterns

---

## 🔍 What to Look For in the Response

### 1. **Sentiment Analyzer Was Called**
Look for mentions of:
- ✅ Sentiment scores (e.g., "positive: 0.8", "negative: -0.3")
- ✅ Country-specific analysis
- ✅ Bias detection (selection bias, framing bias, etc.)
- ✅ Confidence scores

### 2. **Artifacts Were Generated**
The response should mention:
- ✅ "Bar chart created"
- ✅ "Radar chart created"
- ✅ "Data export created"
- ✅ Links to visualizations

### 3. **Execution Log Shows It**
In the UI execution details:
- ✅ Step: "tool_executor: Executing sentiment_analysis_agent"
- ✅ Step: "Sentiment Analyzer: Creating artifacts using shared tools"
- ✅ Step: "Sentiment Analyzer: Processing complete"

### 4. **Visual Indicators**
- ✅ Response is longer (sentiment analysis adds depth)
- ✅ Structured format with country sections
- ✅ Numerical sentiment scores
- ✅ Bias type mentions

---

## 📊 Sample Expected Response Format

```
### Sentiment Analysis: Nuclear Energy Policy

#### United States
- **Sentiment:** Positive (0.65)
- **Key Themes:** Energy independence, economic benefits
- **Bias Detected:** Selection bias (pro-nuclear sources)
- **Confidence:** 85%

#### France
- **Sentiment:** Strongly Positive (0.82)
- **Key Themes:** Energy security, climate benefits
- **Bias Detected:** Geographic bias (European perspective)
- **Confidence:** 90%

#### Germany
- **Sentiment:** Negative (-0.45)
- **Key Themes:** Safety concerns, renewable alternatives
- **Bias Detected:** Temporal bias (post-Fukushima focus)
- **Confidence:** 88%

---

### Visualizations Generated
1. **Sentiment Bar Chart** - Country comparison
2. **Sentiment Radar Chart** - Positive/Neutral/Negative distribution
3. **Data Export** - Structured JSON with all scores

---

### Bias Analysis Summary
- **Selection Bias:** Detected in 2/3 countries
- **Framing Bias:** Present in US sources
- **Geographic Bias:** European perspective dominant
```

---

## ❌ What If It Doesn't Work?

### Sentiment Analyzer NOT Called
If you see only Tavily search results without sentiment analysis:

**Possible Causes:**
1. Query didn't trigger sentiment keywords
2. Strategic planner chose different tools
3. Integration issue

**Try:**
- Use more explicit queries: "Analyze sentiment..."
- Include country names in the query
- Use bias-related keywords: "unbiased", "multiple perspectives"

---

### No Artifacts Mentioned
If sentiment analyzer runs but no charts mentioned:

**Check:**
1. Look at execution log for artifact generation steps
2. Check `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/artifacts/` folder
3. Verify visualizer node completed

---

### Empty or Generic Response
If response doesn't include sentiment scores:

**Check:**
1. Backend logs for errors
2. Tavily API returned results (need data to analyze)
3. OpenAI API is responding

---

## 🧪 API Testing (Alternative)

### Using cURL

```bash
# Test backend directly
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze sentiment on climate policy across US, UK, France",
    "session_id": "test_manual_123"
  }'
```

**Look for in response:**
```json
{
  "tools_used": ["tavily_search", "sentiment_analysis_agent"],
  "response": "...",
  "confidence": 0.8
}
```

---

## 📝 Checklist for Manual Testing

- [ ] Backend is running (http://localhost:8000/health returns 200)
- [ ] Frontend is running (http://localhost:3000 loads)
- [ ] Used a query from the test queries above
- [ ] Response mentions sentiment scores
- [ ] Response includes country-specific analysis
- [ ] Execution log shows sentiment_analysis_agent
- [ ] Response mentions artifacts (charts)
- [ ] Confidence score is reasonable (>70%)

---

## 🎯 Success Criteria

**Test is SUCCESSFUL if you see:**

✅ **In Response:**
- Sentiment scores for countries (-1 to +1)
- Bias detection results (selection, framing, etc.)
- Country-specific analysis
- Key findings or summary
- Confidence percentage

✅ **In Execution Log:**
- "Executing sentiment_analysis_agent"
- "Sentiment Analyzer: Scoring X countries"
- "Bias Detector: Analyzing X countries"
- "Visualizer: Creating artifacts"
- "Bar chart created", "Radar chart created", "Data export created"

✅ **In UI:**
- Response has structure and detail
- Tool badge shows "Sentiment Analysis"
- Longer processing time (15-30 seconds)
- Richer, more analytical response

---

## 🚨 Troubleshooting

### Backend Won't Start
```bash
cd backend_v2
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend Won't Start
```bash
cd Frontend_v2
npm install
npm run dev
```

### No API Keys Error
```bash
# Check .env file in backend_v2/
cat backend_v2/.env

# Should have:
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### Sentiment Analyzer Not Found
```bash
# Verify folder exists
ls -la backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/

# Should show: state.py, config.py, graph.py, main.py, nodes/
```

---

## 📚 Additional Resources

- **Backend API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Test Scripts:**
  - `backend_v2/test_sentiment_direct.py` (No server needed)
  - `backend_v2/test_sentiment_analyzer_integration.py` (Server needed)

---

**Generated:** October 2, 2025  
**For:** Sentiment Analyzer Integration Testing

