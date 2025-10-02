# 🚀 Quick Test Guide - Sentiment Analyzer

## ✅ What We Just Tested

### **All 5 Tests Passed!** 🎉

```
✅ Map Visualization Tool      - Creates maps from country data
✅ Sentiment Analyzer Agent     - Analyzes sentiment, creates table + bar chart
✅ Data Extraction             - Extracts sentiment data for map creation
✅ Country Code Mapping        - Maps country names to ISO codes (94% accuracy)
✅ Master Agent Integration    - Tool is available and accessible
```

---

## 🎯 Test Results Summary

### **Test Query**: "sentiment on Hamas in US and Israel"

**Execution Time**: 54 seconds  
**Artifacts Created**: 2 (table + bar chart)  
**Confidence**: 100%

**Sentiment Scores**:
```
US:     Neutral  (score: +0.00)
Israel: Negative (score: -0.70)
```

**Generated Files**:
- ✅ `sentiment_table_3ff7fe7d5f3c.xlsx` - Excel with 3 sheets
- ✅ `sentiment_bar_chart_d6f766e970d3.html` - Interactive chart
- ✅ `map_980a4e5a027f.html` - Map created from sentiment data

---

## 🧪 Now Test in UI

### **Step 1: Check Server Status**

```bash
# Check if server is running
ps aux | grep "python app.py"

# If not running, start it:
cd backend_v2
source ../.venv/bin/activate
python app.py
```

**Expected**: Server on http://localhost:8000

---

### **Step 2: Test Basic Sentiment Analysis**

**Open your frontend** and ask:

```
"sentiment on Hamas in US and Israel"
```

**Expected Output**:
- ✅ Text analysis with key findings
- ✅ 2 artifacts in sidebar:
  - Data table (with Excel download)
  - Bar chart
- ✅ No duplication
- ✅ Execution graph shows 6 nodes

**If you see issues**:
- ❌ More than 2 artifacts → Duplication issue
- ❌ No artifacts → Check backend logs
- ❌ Error messages → Check console logs

---

### **Step 3: Test Map Creation (Follow-up)**

**After Step 2 completes**, ask:

```
"create a map visualization of this data"
```

**Expected (Best Case)**:
- ✅ Map appears showing US and Israel
- ✅ Colors reflect sentiment (green=positive, red=negative)
- ✅ No re-running of sentiment analysis

**Possible Outcomes**:

**Scenario A: Map appears ✅**
- Perfect! Master agent extracted data and created map

**Scenario B: Agent re-runs sentiment analysis ⚠️**
- Master agent didn't extract data from history
- Fix needed in `artifact_decision.py` or `tool_selector.py`

**Scenario C: Agent says "I can't do that" ❌**
- Master agent didn't detect map request
- Fix needed: Add "map" keyword detection

**Scenario D: Nothing happens ❌**
- Tool not being selected
- Check strategic planner logs

---

### **Step 4: Test Direct Map Request**

**Try in a fresh chat**:

```
"sentiment on Hamas in US, Israel, UK. Show me a map."
```

**Expected**:
- ✅ Runs sentiment analysis for 3 countries
- ✅ Creates table + bar chart
- ⚠️  May or may not create map (depends on master agent logic)

**If no map appears**, follow up with:
```
"create a map of this data"
```

---

## 🔍 What to Look For

### **✅ Good Signs**

1. **Sentiment analyzer creates exactly 2 artifacts** (table + bar)
2. **No maps from sentiment analyzer** (correct - delegated to master)
3. **No duplication** in UI or backend
4. **Fast response** (~1 minute for 2 countries)
5. **Clean execution graph** (6 nodes: analyzer → search → scorer → bias → synthesizer → visualizer)

### **❌ Red Flags**

1. **More than 2 artifacts from sentiment analyzer** → Still creating maps internally
2. **Duplicate artifacts** in UI → Frontend state issue
3. **MongoDB duplicate key errors** → Backend saving same artifact twice
4. **Map request triggers re-analysis** → Master agent not using history
5. **No map ever appears** → Master agent not detecting/using map tool

---

## 🛠️ Quick Debugging

### **Check Backend Logs**

```bash
# In backend_v2 directory
tail -f app.log

# Look for:
# ✅ "🎨 Visualizer: Creating artifacts..."
# ✅ "📦 Total artifacts created: 2"
# ✅ "ℹ️  For maps and other visualizations, use master agent tools"
```

### **Check Master Agent Tool Selection**

```bash
# In backend logs, look for:
# "strategic_planner_node" → Shows which tools were selected
# "tool_executor_node" → Shows which tools were called
# "artifact_decision_node" → Shows artifact creation logic
```

### **Check Artifacts Created**

```bash
# Sentiment analyzer artifacts
ls -lh backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/artifacts/ | tail -10

# Map artifacts
ls -lh backend_v2/langgraph_master_agent/artifacts/map_*.html
```

---

## 📊 Architecture Quick Reference

```
USER QUERY
    ↓
MASTER AGENT (Strategic Planner)
    ↓
    ├→ Detect: "sentiment" keyword
    ├→ Call: Sentiment Analyzer Sub-Agent
    │     ↓
    │     [6 nodes: analyzer → search → scorer → bias → synthesizer → visualizer]
    │     ↓
    │     Returns: {sentiment_scores, artifacts: [table, bar_chart]}
    ↓
MASTER AGENT (Artifact Decision)
    ↓
    ├→ Check: Did sub-agent create artifacts? YES
    ├→ Decision: Skip artifact creation
    ↓
RESPONSE to User
```

**Follow-up query: "create a map"**

```
USER QUERY: "create a map"
    ↓
MASTER AGENT (Strategic Planner)
    ↓
    ├→ Detect: "map" keyword
    ├→ Extract: Sentiment data from conversation history
    ├→ Call: create_map_chart() tool
    │     ↓
    │     Creates map from extracted data
    ↓
RESPONSE to User (with map artifact)
```

---

## 📁 Key Files

| File | Purpose | Status |
|------|---------|--------|
| `sentiment_analyzer/nodes/visualizer.py` | Creates artifacts | ✅ Clean (table + bar only) |
| `tools/visualization_tools.py` | Map tool | ✅ Working |
| `nodes/artifact_decision.py` | Decides artifact creation | ⚠️ May need update |
| `nodes/tool_selector.py` | Selects tools | ⚠️ May need update |
| `shared/visualization_factory.py` | Country mapping | ✅ Working (94%) |

---

## 🎯 Success Criteria

### **Phase 1: Sentiment Analysis** ✅

- [x] Runs without errors
- [x] Creates exactly 2 artifacts (table + bar)
- [x] No maps created by sentiment analyzer
- [x] No duplication issues
- [x] Fast execution (<60s for 2 countries)

### **Phase 2: Map Creation** ⏳ (Next to test)

- [ ] Master agent detects "map" keyword
- [ ] Master agent extracts sentiment data
- [ ] Master agent calls `create_map_chart()`
- [ ] Map artifact appears in response
- [ ] Correct colors (green=positive, red=negative)

---

## 📚 Full Documentation

**Detailed Test Report**: `SENTIMENT_ANALYZER_TEST_REPORT.md`

Contains:
- Complete test results
- Architecture overview
- Debugging guide
- Performance metrics
- All test data

---

## 🚀 Next Action

**Right now, test in your UI**:

1. ✅ Make sure backend is running (port 8000)
2. ✅ Open frontend
3. ✅ Ask: `"sentiment on Hamas in US and Israel"`
4. ✅ Verify: 2 artifacts (table + bar chart)
5. ✅ Ask: `"create a map of this data"`
6. ✅ Check: Does map appear?

**Then report back**:
- What happened in steps 4 and 6?
- Any errors or unexpected behavior?
- Screenshots of artifacts if possible

---

**Status**: Backend tests passed ✅ | UI testing pending ⏳  
**Last Updated**: 2025-10-02 18:50:57

