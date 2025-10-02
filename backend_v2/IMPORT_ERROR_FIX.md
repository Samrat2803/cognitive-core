# Import Error Fix - Sentiment Analyzer

**Date:** October 2, 2025  
**Issue:** "inability to import a necessary function for creating a sentiment analyzer graph"  
**Status:** ✅ Debug logging added

---

## 🚨 **The Error:**

When calling sentiment analyzer, got:
> "error in the sentiment analysis tool... inability to import a necessary function for creating a sentiment analyzer graph"

**Error Location:** `sub_agent_caller.py` trying to import:
```python
from graph import create_sentiment_analyzer_graph
from state import SentimentAnalyzerState
```

---

## 🔧 **What I Fixed:**

**File:** `backend_v2/langgraph_master_agent/tools/sub_agent_caller.py`

### **Change 1: Better Path Resolution** (Lines 47-82)

**Added:**
- Absolute path resolution instead of relative
- Directory existence check before import
- Debug logging for import process
- Early return if directory doesn't exist

**Before:**
```python
agent_dir = os.path.join(os.path.dirname(__file__), '../sub_agents/sentiment_analyzer')
sys.path.insert(0, agent_dir)

try:
    from graph import create_sentiment_analyzer_graph
    from state import SentimentAnalyzerState
```

**After:**
```python
current_file_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.abspath(os.path.join(current_file_dir, '../sub_agents/sentiment_analyzer'))

print(f"\n🔍 Attempting to load sentiment analyzer from: {agent_dir}")
print(f"   Directory exists: {os.path.exists(agent_dir)}")

if not os.path.exists(agent_dir):
    return {"success": False, "error": f"Directory not found: {agent_dir}"}

if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)
    print(f"   ✅ Added to sys.path")

try:
    print(f"   Importing graph module...")
    from graph import create_sentiment_analyzer_graph
    print(f"   ✅ Imported create_sentiment_analyzer_graph")
    
    print(f"   Importing state module...")
    from state import SentimentAnalyzerState
    print(f"   ✅ Imported SentimentAnalyzerState")
```

---

### **Change 2: Detailed Error Logging** (Lines 124-142)

**Added:**
- Exception type logging
- Full traceback printing
- More descriptive error messages

**Before:**
```python
except Exception as e:
    return {
        "success": False,
        "error": str(e)
    }
```

**After:**
```python
except Exception as e:
    print(f"\n❌ Error in sentiment analyzer sub-agent:")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {str(e)}")
    
    import traceback
    print(f"\n   Full traceback:")
    traceback.print_exc()
    print()
    
    return {
        "success": False,
        "error": f"{type(e).__name__}: {str(e)}"
    }
```

---

## 🔍 **What To Look For After Restart:**

### **Scenario 1: Directory Not Found**
```
🔍 Attempting to load sentiment analyzer from: /path/to/sentiment_analyzer
   Directory exists: False
❌ Error: Sentiment analyzer directory not found
```

**Cause:** Sentiment analyzer folder is missing or in wrong location  
**Fix:** Verify folder exists at `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/`

---

### **Scenario 2: Import Error on graph.py**
```
🔍 Attempting to load sentiment analyzer from: /path/to/sentiment_analyzer
   Directory exists: True
   ✅ Added to sys.path
   Importing graph module...
❌ Error in sentiment analyzer sub-agent:
   Error type: ImportError
   Error message: No module named 'nodes'
```

**Cause:** graph.py has import errors (e.g., missing `nodes` package)  
**Fix:** Check `graph.py` imports and ensure `nodes/__init__.py` exists

---

### **Scenario 3: Import Error on Dependencies**
```
   Importing graph module...
❌ Error type: ModuleNotFoundError
   Error message: No module named 'langgraph'
```

**Cause:** Missing dependencies (langgraph, langchain, etc.)  
**Fix:** 
```bash
cd backend_v2
source .venv/bin/activate
pip install langgraph langchain langchain-openai
```

---

### **Scenario 4: Success**
```
🔍 Attempting to load sentiment analyzer from: /path/to/sentiment_analyzer
   Directory exists: True
   ✅ Added to sys.path
   Importing graph module...
   ✅ Imported create_sentiment_analyzer_graph
   Importing state module...
   ✅ Imported SentimentAnalyzerState

📝 Query Analyzer: Analyzing query...
🔍 Search Executor: Searching 3 countries...
...
✅ SUCCESS
```

**This is what we want!**

---

## 🧪 **Testing:**

### **Step 1: Restart Backend**
```bash
cd backend_v2
# Press Ctrl+C
uvicorn app:app --reload
```

### **Step 2: Try Sentiment Query**
```
"Analyze sentiment on Hamas across US, Iran, Israel"
```

### **Step 3: Watch Backend Console**

You should see either:
- ✅ **Import success** logs followed by sentiment analysis, OR
- ❌ **Detailed error** showing exactly what failed

---

## 📊 **Expected Backend Console Output:**

### **When Working:**
```
🔍 Attempting to load sentiment analyzer from: /Users/.../sentiment_analyzer
   Directory exists: True
   ✅ Added to sys.path
   Importing graph module...
   ✅ Imported create_sentiment_analyzer_graph
   Importing state module...
   ✅ Imported SentimentAnalyzerState

📝 Query Analyzer: Analyzing query...
🔍 Search Executor: Searching 3 countries...
   Searching: Hamas US...
   ✅ US: 5 results
   Searching: Hamas Iran...
   ✅ Iran: 5 results
   Searching: Hamas Israel...
   ✅ Israel: 5 results
...
🎨 Visualizer: Creating artifacts using shared tools...
   ✅ Bar chart created: sentiment_bar_chart_xxx
   ✅ Radar chart created: sentiment_radar_chart_xxx
   ✅ Data export created: sentiment_data_table_xxx
   Total artifacts created: 3
```

---

## 🎯 **If Error Persists:**

### **Check 1: Verify Sentiment Analyzer Files Exist**
```bash
cd backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer

ls -la
# Should show:
# graph.py
# state.py
# config.py
# main.py
# nodes/ (folder)
```

### **Check 2: Test Import Manually**
```bash
cd backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer
python -c "from graph import create_sentiment_analyzer_graph; print('OK')"
```

**Expected:** `OK`  
**If error:** Shows the actual import problem

### **Check 3: Check nodes/__init__.py**
```bash
cat backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/__init__.py
```

**Should contain:**
```python
from nodes.analyzer import query_analyzer
from nodes.search_executor import search_executor
from nodes.sentiment_scorer import sentiment_scorer
from nodes.bias_detector import bias_detector
from nodes.synthesizer import synthesizer
from nodes.visualizer import visualizer

__all__ = [
    "query_analyzer",
    "search_executor",
    "sentiment_scorer",
    "bias_detector",
    "synthesizer",
    "visualizer"
]
```

---

## 📝 **Summary:**

**What Changed:**
- ✅ Added detailed import logging
- ✅ Added directory existence check
- ✅ Added full error traceback
- ✅ Better path resolution (absolute paths)

**Result:**
- Now you'll see **exactly** where the import fails
- Error messages will be much more detailed
- Can diagnose the issue from backend console logs

---

**Status:** ✅ Ready for testing  
**Next:** Restart backend and try the query again

