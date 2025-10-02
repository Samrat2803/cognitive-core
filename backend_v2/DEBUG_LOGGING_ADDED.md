# Debug Logging Added - Artifact Investigation

**Date:** October 2, 2025  
**Issue:** Artifacts generated but not displayed in frontend  
**Status:** ✅ Debug logging implemented

---

## 🔍 **What Was Added:**

### **1. Master Agent Result Debug** ✅

**File:** `backend_v2/langgraph_master_agent/main.py` (lines 115-134)

**Logs:**
- Whether `sub_agent_results` exists in final_state
- Which sub-agents ran
- Success status of each sub-agent
- Number of artifacts in each sub-agent's data

**Output Example:**
```
======================================================================
🔍 MASTER AGENT RESULT DEBUG
======================================================================
final_state has 'sub_agent_results': True
Sub-agents that ran: ['sentiment_analysis']
  sentiment_analysis:
    success: True
    artifacts: 3 items

Result dict includes sub_agent_results: True
======================================================================
```

---

### **2. HTTP Artifact Extraction Debug** ✅

**File:** `backend_v2/app.py` (lines 489-532)

**Logs:**
- Keys in result dict
- Whether sub_agent_results is present
- Which sub-agents are in the results
- Success status and artifact count
- Individual artifact IDs and types

**Output Example:**
```
======================================================================
🔍 HTTP ARTIFACT EXTRACTION DEBUG
======================================================================
result.keys(): ['response', 'citations', ..., 'sub_agent_results']
sub_agent_results present: True
Sub-agents in result: ['sentiment_analysis']
✅ Found sentiment_analysis in sub_agent_results
   Success: True
   Has data: True
   ✅ Artifacts found: 3
      1. sentiment_bar_chart: sentiment_bar_chart_abc123
      2. sentiment_radar_chart: sentiment_radar_chart_def456
      3. sentiment_data_table: sentiment_data_table_ghi789

Final sub_agent_artifacts dict: True
  sentiment_analysis: 3 artifacts
======================================================================
```

---

### **3. WebSocket Artifact Sending Debug** ✅

**File:** `backend_v2/app.py` (lines 971-996)

**Logs:**
- Keys in result dict
- Whether main artifact exists
- Whether sub_agent_artifacts exists
- Number of agents with artifacts
- Number of artifacts per agent
- Falls back to check sub_agent_results if extraction failed

**Output Example:**
```
======================================================================
🔍 WEBSOCKET ARTIFACT DEBUG CHECKPOINT
======================================================================
result.keys(): ['response', ..., 'sub_agent_artifacts', 'sub_agent_results']
result.get('artifact'): False
result.get('sub_agent_artifacts') exists: True
sub_agent_artifacts after extraction: True
✅ Found sub_agent_artifacts with 1 agent(s)
   Agent 'sentiment_analysis': 3 artifacts
======================================================================
```

**If artifacts missing:**
```
❌ sub_agent_artifacts is EMPTY or missing!
   Checking if sub_agent_results exists in result...
   ✓ sub_agent_results found: ['sentiment_analysis']
```

---

### **4. Enhanced Artifact Serving** ✅

**File:** `backend_v2/app.py` (lines 564-587)

**Logs:**
- Artifact ID requested
- Whether found in main artifacts folder
- Whether found in sentiment analyzer folder
- Full path being served

**Output Example:**
```
📊 Artifact HTML requested: sentiment_bar_chart_abc123
✅ Found artifact in sentiment analyzer folder: langgraph_master_agent/sub_agents/sentiment_analyzer/artifacts/sentiment_bar_chart_abc123.html
✅ Serving artifact from: langgraph_master_agent/sub_agents/sentiment_analyzer/artifacts/sentiment_bar_chart_abc123.html
```

---

### **5. Test Endpoint: Sentiment Artifacts** ✅

**Endpoint:** `GET /api/test-sentiment-artifacts`

**Purpose:** Directly test if sentiment analyzer creates artifacts

**Output Example:**
```json
{
  "success": true,
  "artifacts_count": 3,
  "artifacts": [
    {
      "artifact_id": "sentiment_bar_chart_abc123",
      "type": "sentiment_bar_chart",
      "title": "Sentiment Score Comparison",
      "html_path": "..."
    },
    ...
  ]
}
```

**Test:**
```bash
curl http://localhost:8000/api/test-sentiment-artifacts
```

---

### **6. Test Endpoint: List Recent Artifacts** ✅

**Endpoint:** `GET /api/artifacts/list`

**Purpose:** List all recently generated artifacts

**Output Example:**
```json
{
  "artifacts": [
    {
      "artifact_id": "sentiment_bar_chart_abc123",
      "filename": "sentiment_bar_chart_abc123.html",
      "size": 3670016,
      "modified": "2025-10-02T14:17:00",
      "url": "http://localhost:8000/api/artifacts/sentiment_bar_chart_abc123.html"
    },
    ...
  ],
  "count": 20
}
```

**Test:**
```bash
curl http://localhost:8000/api/artifacts/list
```

---

## 🧪 **How to Use This Debug Info:**

### **Step 1: Restart Backend**
```bash
cd backend_v2
# Kill existing server (Ctrl+C)
uvicorn app:app --reload
```

### **Step 2: Test Sentiment Analyzer Directly**
```bash
curl http://localhost:8000/api/test-sentiment-artifacts
```

**Expected:** Should return 3 artifacts

**If it fails:** Sentiment analyzer isn't creating artifacts at all

---

### **Step 3: Run Query via WebSocket**

In frontend, ask:
```
"Analyze sentiment on AI regulation in US, UK, France"
```

**Watch Backend Console** for these debug sections:
1. 🔍 MASTER AGENT RESULT DEBUG
2. 🔍 HTTP ARTIFACT EXTRACTION DEBUG (if using HTTP endpoint)
3. 🔍 WEBSOCKET ARTIFACT DEBUG CHECKPOINT

---

### **Step 4: Analyze Debug Output**

#### **Scenario A: No sub_agent_results**
```
❌ No sub_agent_results in final_state
```
**Problem:** Master agent isn't storing sub-agent results in state  
**Fix:** Check `tool_executor.py` - verify it saves to `state["sub_agent_results"]`

---

#### **Scenario B: sub_agent_results exists but no artifacts**
```
✅ Found sentiment_analysis in sub_agent_results
   Success: True
   Has data: True
   ❌ No artifacts in sentiment_analysis data
```
**Problem:** Sentiment analyzer ran but didn't create artifacts  
**Fix:** Check sentiment analyzer's visualizer node

---

#### **Scenario C: Artifacts exist but not extracted**
```
sub_agent_results present: True
❌ sentiment_analysis NOT in sub_agent_results
```
**Problem:** Extraction logic looking for wrong key  
**Fix:** Check extraction code (app.py lines 505-520)

---

#### **Scenario D: Extraction works but WebSocket doesn't send**
```
🔍 HTTP ARTIFACT EXTRACTION DEBUG
  sentiment_analysis: 3 artifacts  ✅

🔍 WEBSOCKET ARTIFACT DEBUG CHECKPOINT
❌ sub_agent_artifacts is EMPTY or missing!
```
**Problem:** HTTP and WebSocket use different result objects  
**Fix:** Ensure WebSocket uses same extraction logic

---

## 📊 **Expected Complete Log Flow:**

When everything works, you should see:

```
🔍 MASTER AGENT RESULT DEBUG
✅ final_state has 'sub_agent_results': True
✅ Sub-agents that ran: ['sentiment_analysis']
✅ artifacts: 3 items

🔍 HTTP ARTIFACT EXTRACTION DEBUG
✅ Found sentiment_analysis in sub_agent_results
✅ Artifacts found: 3

🔍 WEBSOCKET ARTIFACT DEBUG CHECKPOINT
✅ Found sub_agent_artifacts with 1 agent(s)
✅ Agent 'sentiment_analysis': 3 artifacts

📊 Sending artifact via WebSocket: sentiment_bar_chart_abc123
📊 Sending artifact via WebSocket: sentiment_radar_chart_def456
📊 Sending artifact via WebSocket: sentiment_data_table_ghi789
📊 Total artifacts sent to frontend: 3
```

---

## 🎯 **Next Steps After Debugging:**

Once you identify the issue from the logs:

1. **If sentiment analyzer isn't creating artifacts:**
   - Check visualizer node in sentiment analyzer
   - Verify shared visualization tools are working

2. **If artifacts created but not in sub_agent_results:**
   - Check tool_executor.py saves sentiment analyzer result
   - Verify SubAgentCaller returns proper format

3. **If in sub_agent_results but not extracted:**
   - Fix extraction logic in app.py
   - Ensure HTTP and WebSocket use same code

4. **If extracted but not sent via WebSocket:**
   - Check if WebSocket artifact sending code is reached
   - Verify sub_agent_artifacts isn't being cleared

---

## 📝 **Files Modified:**

1. ✅ `backend_v2/langgraph_master_agent/main.py` (+19 lines)
2. ✅ `backend_v2/app.py` (+125 lines total)
   - HTTP artifact extraction debug
   - WebSocket artifact sending debug
   - Enhanced artifact serving with logging
   - Test endpoints

**Total:** 2 files, ~144 lines of debug code added

---

**Status:** ✅ Ready for testing  
**Next:** Restart backend and run query to see debug output

