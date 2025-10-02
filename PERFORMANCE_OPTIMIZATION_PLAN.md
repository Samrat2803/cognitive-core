# Performance Optimization Plan for Political Analyst Agent

**Date**: October 2, 2025  
**Status**: Analysis Complete - Awaiting Approval  
**Estimated Speed Improvement**: 60-80% reduction in query response time

---

## Executive Summary

Current response times are **30-90 seconds** for typical queries. Analysis reveals **7 major bottlenecks** causing sequential execution where parallel processing would be more efficient. Implementing the proposed optimizations can reduce response times to **10-25 seconds** (60-80% improvement).

---

## Current Performance Bottlenecks

### 🔴 **CRITICAL BOTTLENECKS**

#### 1. **Sequential Tool Execution** (HIGH IMPACT)
**Location**: `backend_v2/langgraph_master_agent/nodes/tool_executor.py` (line 48)

```python
# CURRENT: Sequential execution
for tool_name in tools_to_use:
    if tool_name == "tavily_search":
        result = await tavily_tools.search(...)  # Waits 2-5s
    elif tool_name == "sentiment_analysis_agent":
        result = await sub_agent_caller.call_sentiment_analyzer(...)  # Waits 20-40s
```

**Problem**: Tools execute one by one. If planner selects `["tavily_search", "sentiment_analysis_agent"]`, total time is **25-45 seconds** instead of running in parallel.

**Impact**: 🔴 **Very High** - Adds 10-30 seconds per query  
**Estimated Speedup**: 40-60% for queries using multiple tools

---

#### 2. **Sequential Country Searches in Sentiment Analyzer** (HIGH IMPACT)
**Location**: `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/search_executor.py` (line 46)

```python
# CURRENT: Sequential searches
for country in countries:  # Usually 5 countries
    country_query = f"{query} public opinion {full_country_name}"
    result = await client.search(...)  # Each takes 2-4s
    search_results[country] = result["results"]
```

**Problem**: 5 countries = 5 sequential Tavily API calls = **10-20 seconds**

**Impact**: 🔴 **Very High** - Adds 10-20 seconds for sentiment analysis  
**Estimated Speedup**: 60-80% for sentiment queries

---

#### 3. **Sequential LLM Calls for Sentiment Scoring** (HIGH IMPACT)
**Location**: `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/sentiment_scorer.py` (line 31)

```python
# CURRENT: Sequential LLM scoring
for country, results in search_results.items():  # 5 countries
    response = await client.chat.completions.create(...)  # Each takes 2-4s
    sentiment_scores[country] = json.loads(response.choices[0].message.content)
```

**Problem**: 5 countries = 5 sequential OpenAI API calls = **10-20 seconds**

**Impact**: 🔴 **Very High** - Adds 10-20 seconds for sentiment analysis  
**Estimated Speedup**: 70-85% for sentiment scoring phase

---

### 🟡 **MODERATE BOTTLENECKS**

#### 4. **Multiple Sequential LLM Calls in Master Agent Pipeline**
**Locations**: 
- Strategic Planner (line 93)
- Response Synthesizer (line 157)
- Artifact Decision (line 125)

**Problem**: Each node makes an LLM call sequentially:
1. Strategic Planner: 1-2s
2. Tool Executor: Variable (tools + sub-agents)
3. Response Synthesizer: 2-4s
4. Artifact Decision: 1-2s
5. Artifact Creator: 1-2s

Total LLM overhead: **5-10 seconds**

**Impact**: 🟡 **Moderate** - Fixed overhead on every query  
**Optimization Potential**: 20-30% (batch some calls, optimize prompts)

---

#### 5. **No Caching for Repeated Queries**
**Location**: Multiple (Tavily calls, LLM calls, sub-agent results)

**Problem**: Same queries are re-executed fully every time. Example:
- "Sentiment on nuclear policy in US, UK, France" → 20s
- (User asks follow-up 2 minutes later) → Still 20s

**Impact**: 🟡 **Moderate** - No benefit for repeated/similar queries  
**Estimated Speedup**: 90%+ for cached queries

---

### 🟢 **MINOR BOTTLENECKS**

#### 6. **Heavy Visualization Generation**
**Location**: `backend_v2/shared/visualization_factory.py`

**Problem**: Plotly chart generation adds 0.5-2 seconds

**Impact**: 🟢 **Low** - Only affects queries requesting visualizations  
**Optimization Potential**: 10-20%

---

#### 7. **Synchronous Graph Execution**
**Location**: LangGraph workflow definition

**Problem**: Nodes execute strictly sequentially even when some could overlap

**Impact**: 🟢 **Low** - Graph design constraints  
**Optimization Potential**: 15-25% (requires graph restructuring)

---

## Proposed Optimizations (Ranked by Impact)

### 🎯 **PHASE 1: Quick Wins (1-2 hours implementation)**

#### **1.1 Parallelize Country Searches** ⭐⭐⭐
**File**: `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/search_executor.py`

**Change**:
```python
# BEFORE (Sequential - 10-20s)
for country in countries:
    result = await client.search(...)
    search_results[country] = result["results"]

# AFTER (Parallel - 2-4s)
import asyncio

async def search_country(country):
    country_query = f"{query} public opinion {country_names.get(country, country)}"
    result = await client.search(
        query=country_query,
        search_depth=SEARCH_DEPTH,
        max_results=MAX_RESULTS_PER_COUNTRY,
        include_answer=True
    )
    return country, result.get("results", [])

# Execute all searches in parallel
tasks = [search_country(country) for country in countries]
results = await asyncio.gather(*tasks)
search_results = {country: results for country, results in results}
```

**Expected Speedup**: 60-80% (10-20s → 2-4s)  
**Risk**: Low  
**Effort**: 15 minutes

---

#### **1.2 Parallelize Sentiment Scoring LLM Calls** ⭐⭐⭐
**File**: `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/sentiment_scorer.py`

**Change**:
```python
# BEFORE (Sequential - 10-20s)
for country, results in search_results.items():
    response = await client.chat.completions.create(...)
    sentiment_scores[country] = json.loads(response.choices[0].message.content)

# AFTER (Parallel - 2-4s)
async def score_country(country, results):
    combined_text = "\n\n".join([f"Title: {r.get('title')}\nContent: {r.get('content')}" for r in results[:5]])
    prompt = f"""Analyze sentiment..."""
    
    response = await client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return country, json.loads(response.choices[0].message.content)

tasks = [score_country(country, results) for country, results in search_results.items()]
results = await asyncio.gather(*tasks, return_exceptions=True)
sentiment_scores = {country: score for country, score in results if not isinstance(score, Exception)}
```

**Expected Speedup**: 70-85% (10-20s → 2-4s)  
**Risk**: Low  
**Effort**: 20 minutes

---

#### **1.3 Parallelize Bias Detection LLM Calls** ⭐⭐
**File**: `backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer/nodes/bias_detector.py`

**Change**: Same pattern as sentiment scoring - parallelize country bias analysis

**Expected Speedup**: 70-85% for bias detection phase  
**Risk**: Low  
**Effort**: 15 minutes

---

### 🎯 **PHASE 2: Medium Wins (2-4 hours implementation)**

#### **2.1 Parallelize Tool Execution** ⭐⭐⭐
**File**: `backend_v2/langgraph_master_agent/nodes/tool_executor.py`

**Problem**: If `tools_to_use = ["tavily_search", "sentiment_analysis_agent"]`, they run sequentially (25-45s total)

**Solution**: Execute independent tools in parallel

**Change**:
```python
# BEFORE (Sequential)
for tool_name in tools_to_use:
    if tool_name == "tavily_search":
        result = await tavily_tools.search(...)
    elif tool_name == "sentiment_analysis_agent":
        result = await sub_agent_caller.call_sentiment_analyzer(...)

# AFTER (Parallel)
async def execute_tool(tool_name):
    if tool_name == "tavily_search":
        return "tavily_search", await tavily_tools.search(...)
    elif tool_name == "sentiment_analysis_agent":
        return "sentiment_analysis", await sub_agent_caller.call_sentiment_analyzer(...)
    # ... other tools

# Execute all tools in parallel
tasks = [execute_tool(tool_name) for tool_name in tools_to_use]
results = await asyncio.gather(*tasks, return_exceptions=True)

for tool_name, result in results:
    if isinstance(result, Exception):
        state["error_log"].append(f"Tool {tool_name} failed: {result}")
    elif tool_name == "tavily_search":
        state["tool_results"]["tavily_search"] = result
    elif tool_name == "sentiment_analysis":
        state["sub_agent_results"]["sentiment_analysis"] = result
```

**Expected Speedup**: 40-60% when multiple tools used (25-45s → 15-20s)  
**Risk**: Medium (need to handle parallel errors carefully)  
**Effort**: 1 hour

---

#### **2.2 Implement Smart Query Caching** ⭐⭐
**File**: New file `backend_v2/shared/query_cache.py`

**Strategy**:
1. **Tavily API Cache**: Cache Tavily search results for 1-6 hours
2. **Sub-agent Result Cache**: Cache sentiment analysis for 3-12 hours (configurable)
3. **LLM Response Cache**: Cache LLM synthesis for identical queries (1 hour)

**Implementation**:
```python
from functools import lru_cache
import hashlib
import json
from datetime import datetime, timedelta

class QueryCache:
    def __init__(self, mongo_service):
        self.mongo = mongo_service
        self.memory_cache = {}  # In-memory cache for session
    
    async def get_tavily_cache(self, query: str, cache_hours: int = 3):
        """Get cached Tavily search results"""
        cache_key = hashlib.md5(query.encode()).hexdigest()
        
        # Check MongoDB
        cached = await self.mongo.db.tavily_cache.find_one({
            "cache_key": cache_key,
            "cached_at": {"$gte": datetime.utcnow() - timedelta(hours=cache_hours)}
        })
        
        if cached:
            return cached["results"]
        return None
    
    async def set_tavily_cache(self, query: str, results: dict):
        """Cache Tavily search results"""
        cache_key = hashlib.md5(query.encode()).hexdigest()
        await self.mongo.db.tavily_cache.update_one(
            {"cache_key": cache_key},
            {"$set": {
                "query": query,
                "results": results,
                "cached_at": datetime.utcnow()
            }},
            upsert=True
        )
```

**Expected Speedup**: 90%+ for cached queries (30s → 2-3s)  
**Risk**: Medium (cache invalidation complexity)  
**Effort**: 2 hours

---

#### **2.3 Optimize LLM Prompts (Reduce Token Count)** ⭐
**Files**: All nodes making LLM calls

**Strategy**:
- Reduce prompt verbosity (keep essential context only)
- Use JSON mode consistently (faster than text parsing)
- Reduce max_tokens from 4000 to 2000 for most calls

**Expected Speedup**: 15-25% on LLM calls  
**Risk**: Low  
**Effort**: 1 hour

---

### 🎯 **PHASE 3: Advanced Optimizations (4-8 hours implementation)**

#### **3.1 Implement Streaming Responses** ⭐⭐
**File**: `backend_v2/app.py` (WebSocket handler)

**Current**: User waits 30-90s for complete response  
**Proposed**: Stream partial results as they arrive

**Changes**:
1. Stream search results immediately when Tavily returns
2. Stream sentiment analysis country-by-country
3. Stream final response as it's generated

**Expected UX Improvement**: Perceived latency reduced by 50-70%  
**Risk**: Medium (requires frontend changes)  
**Effort**: 4 hours

---

#### **3.2 Pre-compute Common Queries** ⭐
**File**: New background worker

**Strategy**:
- Identify top 20 most common query patterns
- Pre-compute results every 6-12 hours
- Serve from cache instantly

**Example Pre-computed Queries**:
- "Latest news on Gaza conflict"
- "US election sentiment analysis"
- "China Taiwan relations sentiment"

**Expected Speedup**: 95%+ for pre-computed queries (30s → 1-2s)  
**Risk**: Medium (freshness concerns)  
**Effort**: 3 hours

---

#### **3.3 Implement Graph-level Parallelization** ⭐⭐
**File**: `backend_v2/langgraph_master_agent/graph.py`

**Current Flow** (Sequential):
```
Conversation → Planner → Tool Executor → Decision Gate → Synthesizer → Artifact Decision → Artifact Creator
```

**Optimized Flow** (Some Parallel Nodes):
```
Conversation → Planner → Tool Executor (parallel tools)
                              ↓
                         [Wait for all tools]
                              ↓
                         Decision Gate
                              ↓
                    ┌────────┴────────┐
                    ↓                 ↓
            Synthesizer      Artifact Decision (parallel)
                    ↓                 ↓
                    └────────┬────────┘
                             ↓
                      Artifact Creator
```

**Expected Speedup**: 10-20%  
**Risk**: High (graph refactoring)  
**Effort**: 6 hours

---

#### **3.4 Reduce Artifact Generation Latency** ⭐
**File**: `backend_v2/shared/visualization_factory.py`

**Strategies**:
- Generate PNG asynchronously (don't block response)
- Lazy-load visualizations (generate on first view)
- Use simpler charting library for faster generation

**Expected Speedup**: 20-40% for visualization queries  
**Risk**: Low  
**Effort**: 2 hours

---

## Implementation Roadmap

### **Sprint 1: Critical Parallelization (1-2 hours)**
- ✅ 1.1: Parallelize country searches
- ✅ 1.2: Parallelize sentiment scoring
- ✅ 1.3: Parallelize bias detection

**Expected Result**: 50-70% speedup (30-60s → 12-20s)

---

### **Sprint 2: Tool & Cache Optimization (2-4 hours)**
- ✅ 2.1: Parallelize tool execution
- ✅ 2.2: Implement smart caching
- ✅ 2.3: Optimize LLM prompts

**Expected Result**: Additional 20-30% speedup (12-20s → 8-14s)

---

### **Sprint 3: Advanced UX (4-8 hours, optional)**
- ✅ 3.1: Implement streaming responses
- ✅ 3.2: Pre-compute common queries
- ✅ 3.3: Graph-level parallelization
- ✅ 3.4: Reduce artifact latency

**Expected Result**: Best-in-class UX (perceived latency < 5s)

---

## Performance Targets

### **Current Performance**
- Simple query (search only): **5-10s**
- Sentiment analysis query: **30-60s**
- Complex query (multiple tools): **40-90s**

### **After Phase 1** (Critical Parallelization)
- Simple query: **3-5s** (40% improvement)
- Sentiment analysis: **10-15s** (70% improvement)
- Complex query: **15-25s** (60% improvement)

### **After Phase 2** (Tool & Cache Optimization)
- Simple query: **2-3s** (cached: <1s)
- Sentiment analysis: **8-12s** (cached: 2-3s)
- Complex query: **10-18s** (cached: 3-5s)

### **After Phase 3** (Advanced UX)
- Perceived latency: **< 5s** (streaming)
- Pre-computed queries: **< 2s**
- Overall satisfaction: **Excellent**

---

## Risk Assessment

### **Low Risk** (Recommended for immediate implementation)
- ✅ 1.1: Country search parallelization
- ✅ 1.2: Sentiment scoring parallelization
- ✅ 1.3: Bias detection parallelization
- ✅ 2.3: LLM prompt optimization

### **Medium Risk** (Implement with testing)
- ⚠️ 2.1: Tool execution parallelization (need error handling)
- ⚠️ 2.2: Smart caching (cache invalidation complexity)
- ⚠️ 3.1: Streaming responses (frontend coordination required)

### **High Risk** (Defer to later)
- ⚠️⚠️ 3.3: Graph-level parallelization (major refactoring)

---

## Monitoring & Metrics

### **Key Metrics to Track**
1. **Query Response Time** (P50, P95, P99)
2. **API Call Latency** (Tavily, OpenAI)
3. **Cache Hit Rate** (%)
4. **Tool Execution Time** (per tool)
5. **Sub-agent Execution Time** (per agent)

### **Recommended Tools**
- LangSmith (already integrated)
- Custom timing decorators
- MongoDB aggregation queries for cache analytics

---

## Cost Analysis

### **Current Costs (per query)**
- OpenAI API: $0.01 - $0.05 (multiple LLM calls)
- Tavily API: $0.005 - $0.02 (search calls)
- **Total**: $0.015 - $0.07 per query

### **After Optimization (with caching)**
- OpenAI API: $0.005 - $0.03 (40% reduction via prompt optimization)
- Tavily API: $0.001 - $0.01 (50% reduction via caching)
- **Total**: $0.006 - $0.04 per query (40-50% cost reduction)

**Annual Savings** (at 10,000 queries/month): **$3,600 - $5,400**

---

## Conclusion

The current system has significant performance bottlenecks caused by **sequential execution** of inherently parallelizable operations. Implementing Phase 1 optimizations alone will provide **60-70% speedup** with minimal risk and effort (1-2 hours).

**Recommendation**: Start with Phase 1 (critical parallelization) immediately, followed by Phase 2 (caching) within the next sprint. Phase 3 can be deferred based on user feedback.

---

## Next Steps

1. **Review this plan** and approve phases to implement
2. **Select optimization priority** (Phase 1 recommended)
3. **Allocate development time** (1-2 hours for Phase 1)
4. **Test and measure** improvements
5. **Iterate based on metrics**

---

**Questions? Concerns? Let me know which phases you'd like to prioritize!**

