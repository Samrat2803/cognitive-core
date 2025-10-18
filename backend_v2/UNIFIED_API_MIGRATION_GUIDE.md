# 🔄 Migration Guide: Unified API Manager

**Date:** October 18, 2025  
**Purpose:** Consolidate all Tavily and OpenAI API calls into a single managed system

---

## 📋 **What Changed?**

### **Before:**
- Scattered Tavily API calls across multiple files
- Duplicate `TavilyTools` classes in sub-agents
- Inconsistent caching implementation
- No unified cost tracking
- Direct OpenAI API calls

### **After:**
- Single `UnifiedAPIManager` for all external APIs
- Automatic caching for all API calls
- Centralized cost tracking
- Consistent error handling
- Easy to add new API providers

---

## 🎯 **Benefits**

1. **Cost Savings**: Automatic caching saves $0.01-0.05 per repeated call
2. **Maintainability**: Change API logic in one place
3. **Monitoring**: Track costs and usage across all agents
4. **Performance**: Faster responses with caching
5. **Reliability**: Consistent error handling and fallbacks

---

## 🚀 **How to Migrate Existing Code**

### **Step 1: Import the Manager**

**Old:**
```python
from shared.tavily_client import TavilyClient
from openai import AsyncOpenAI

tavily = TavilyClient()
openai_client = AsyncOpenAI()
```

**New:**
```python
from shared.api_manager import get_api_manager

api = get_api_manager()
```

---

### **Step 2: Update Tavily Search Calls**

**Old:**
```python
# Using TavilyClient
result = await tavily.search(
    query="India cough syrup deaths",
    max_results=5
)

# Using TavilyTools
tavily_tools = TavilyTools()
result = await tavily_tools.tavily_search(
    query="India cough syrup deaths",
    max_results=5
)
```

**New:**
```python
result = await api.tavily_search(
    query="India cough syrup deaths",
    max_results=5
)
```

**Benefits:**
- ✅ Automatic caching (24h for search results)
- ✅ Cost tracking
- ✅ Consistent error handling

---

### **Step 3: Update Tavily Extract Calls**

**Old:**
```python
# Using TavilyClient
result = await tavily.extract(urls=url_list)

# Using TavilyTools
result = await tavily_tools.tavily_extract(urls=url_list)
```

**New:**
```python
result = await api.tavily_extract(urls=url_list)
```

**Benefits:**
- ✅ Automatic caching (7d for extractions)
- ✅ Automatic vector storage for RAG
- ✅ Batch cache retrieval
- ✅ Partial results if API fails

---

### **Step 4: Update OpenAI LLM Calls**

**Old:**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=4000
)

content = response.choices[0].message.content
```

**New:**
```python
result = await api.llm_complete(
    prompt=prompt,
    model="gpt-4o",
    temperature=0.7,
    max_tokens=4000
)

content = result["content"]
cost = result["cost"]
```

**Benefits:**
- ✅ Cost tracking
- ✅ Returns structured response with cost/tokens
- ✅ Optional caching for deterministic prompts

---

### **Step 5: Update OpenAI Embedding Calls**

**Old:**
```python
response = await openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)

embedding = response.data[0].embedding
```

**New:**
```python
embedding = await api.create_embedding(text=text)
```

**Benefits:**
- ✅ Automatic truncation to token limits
- ✅ Cost tracking
- ✅ Simplified error handling

---

## 📊 **Cost Tracking**

### **Get Current Stats:**

```python
stats = api.get_cost_stats()

print(f"Total cost: ${stats['costs']['total']:.3f}")
print(f"Tavily calls: {stats['calls']['tavily_search'] + stats['calls']['tavily_extract']}")
print(f"Cache hit rate: {stats['cache']['hit_rate']*100:.1f}%")
```

### **Reset Stats (for testing):**

```python
api.reset_stats()
```

---

## 🔍 **Migration Checklist**

### **Files to Update:**

- [ ] `langgraph_master_agent/tools/sub_agent_caller.py`
- [ ] `langgraph_master_agent/tools/tavily_direct.py`
- [ ] `sub_agents/*/nodes/*.py` (any direct API calls)
- [ ] `sub_agents/investigative_journalist/lean_investigator.py`
- [ ] `sub_agents/gov_intelligence/nodes/*.py`
- [ ] `services/*.py` (any API calls)

### **Files to REMOVE (duplicates):**

- [ ] `sub_agents/gov_intelligence/tavily_tools.py`
- [ ] `sub_agents/investigative_journalist/tavily_tools.py`
- [ ] Any other duplicate `TavilyTools` classes

### **Tests to Update:**

- [ ] `test_investigative_journalist_integration.py`
- [ ] `test_gov_intelligence_integration.py`
- [ ] Any tests making direct API calls

---

## 🧪 **Testing the Migration**

### **Quick Test:**

```bash
cd backend_v2
source .venv/bin/activate
python test_unified_api_manager.py
```

**Expected:**
- ✅ All tests pass
- ✅ Cache hit rate > 0%
- ✅ Cost tracking shows real values
- ✅ Total cost < $0.05

### **Integration Test:**

Run your existing integration tests with the migrated code:

```bash
python test_investigative_journalist_integration.py
```

**Verify:**
- ✅ Same functionality as before
- ✅ Cost tracking in output
- ✅ Cache hits on repeated runs

---

## 🎛️ **Advanced Features**

### **Disable Caching (for testing):**

```python
api = get_api_manager(enable_caching=False)
```

### **Custom Cache Keys for LLM (coming soon):**

```python
result = await api.llm_complete(
    prompt=prompt,
    cache_key="sentiment_analysis_v1"  # Caches this prompt template
)
```

### **Access Cache Stats:**

```python
stats = api.get_cost_stats()
cache_stats = stats['cache_stats']

print(f"Total vectors stored: {cache_stats['vector_total']}")
print(f"Total savings: ${cache_stats['total_saved']:.2f}")
```

---

## 🚨 **Common Issues**

### **Issue 1: "OpenAI client not initialized"**

**Cause:** `OPENAI_API_KEY` not in `.env`

**Fix:**
```bash
echo "OPENAI_API_KEY=your-key-here" >> .env
```

### **Issue 2: "Tavily API key is required"**

**Cause:** `TAVILY_API_KEY` not in `.env`

**Fix:**
```bash
echo "TAVILY_API_KEY=your-key-here" >> .env
```

### **Issue 3: Caching not working**

**Cause:** MongoDB not connected

**Check:**
```python
api = get_api_manager()
print(api.cache)  # Should not be None
```

---

## 📈 **Expected Impact**

### **After Full Migration:**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Duplicate Tavily calls | Many | 0 | 100% reduction |
| Cost per session | $0.50 | $0.15 | 70% savings |
| Cache hit rate | 0% | 40-60% | New capability |
| Code maintainability | Low | High | Centralized |

### **Cost Savings Example:**

**Scenario:** User runs same investigation twice

**Before:**
- First run: $0.50
- Second run: $0.50
- **Total: $1.00**

**After:**
- First run: $0.50
- Second run: $0.10 (80% cache hits)
- **Total: $0.60 (40% savings!)**

---

## 🎯 **Next Steps**

1. **Phase 1 (This Week):**
   - ✅ Create unified API manager
   - ✅ Add caching layer
   - ✅ Test basic functionality

2. **Phase 2 (Next Week):**
   - [ ] Migrate all sub-agents
   - [ ] Remove duplicate code
   - [ ] Update tests

3. **Phase 3 (Week After):**
   - [ ] Add LLM response caching
   - [ ] Add rate limit handling
   - [ ] Add retry logic

4. **Phase 4 (Month):**
   - [ ] Add more API providers (Anthropic, etc.)
   - [ ] Add cost alerts
   - [ ] Add usage dashboards

---

## 📞 **Support**

**Questions?** Check:
- `shared/api_manager/unified_api_manager.py` - Implementation
- `test_unified_api_manager.py` - Usage examples
- `CACHING_COMPLETE_SUMMARY.md` - Caching details

**Migration Progress:** Track in `MIGRATION_PROGRESS.md`

---

**Ready to migrate!** 🚀

