# Testing Guide: Local RAG Implementation

**Goal:** Test both BACKWARD COMPATIBILITY and NEW FEATURES

---

## 🎯 Testing Strategy

### **What We're Testing:**

1. **Backward Compatibility** ✅
   - Cognitive Crawler still works (uses new general tool)
   - Existing MongoDB queries work (thread_id=None)
   - No breaking changes to existing functionality

2. **Forward Features** ✨
   - LOCAL RAG filtering by thread_id works
   - Investigative Journalist can store and query
   - General RAG tool works for all sub-agents

3. **Integration** 🔗
   - Cognitive crawler uses general tool seamlessly
   - Investigative journalist auto-stores content
   - Both can coexist without conflicts

---

## 🚀 Quick Test (5 minutes)

**Purpose:** Sanity check that basic functionality works

```bash
cd backend_v2
source .venv/bin/activate
python quick_test_rag.py
```

**Expected Output:**
```
🚀 QUICK TEST - Local RAG Implementation
✅ Step 1: Import successful
✅ Step 2: Testing GLOBAL RAG...
   Mode: global
   Results: X
✅ Step 3: Testing LOCAL RAG...
   Mode: local
   Results: X
🎉 QUICK TEST PASSED!
```

**If this fails:** Check imports and MongoDB connection

---

## 🧪 Comprehensive Test Suite (15-20 minutes)

**Purpose:** Full validation of backward compatibility and new features

```bash
cd backend_v2
source .venv/bin/activate
python test_local_rag_implementation.py
```

### **Test Breakdown:**

#### **Backward Compatibility Tests:**

**TEST 1: MongoDB Handler - Backward Compatibility**
- ✅ Global search with `thread_id=None` still works
- ✅ Results contain thread_id field
- ✅ Existing cognitive crawler code compatible

**TEST 3: General RAG Tool - Backward Compatibility**
- ✅ Global RAG query works (existing behavior)
- ✅ Returns mode='global'
- ✅ Generates answers and sources

**TEST 5: Cognitive Crawler Integration**
- ✅ Cognitive crawler's rag_query_handler still works
- ✅ Global search functional
- ✅ Session-specific search functional (new)

#### **New Feature Tests:**

**TEST 2: MongoDB Handler - Thread Filtering**
- ✅ Stores documents with different thread_ids
- ✅ Queries filtered by thread_id work correctly
- ✅ Global queries find all threads
- ✅ No cross-contamination between threads

**TEST 4: General RAG Tool - LOCAL Feature**
- ✅ Local RAG query works (thread_id specified)
- ✅ Returns mode='local'
- ✅ Convenience functions work (query_local_rag, query_global_rag)

**TEST 6: Investigative Journalist Storage**
- ✅ Can store extracted content in RAG
- ✅ Can query local RAG (this investigation)
- ✅ Can query global RAG (all investigations)

#### **Edge Case Tests:**

**TEST 7: Edge Cases and Error Handling**
- ✅ Empty queries handled gracefully
- ✅ Non-existent thread_ids don't crash
- ✅ Large top_k values handled
- ✅ Answer generation can be disabled

---

## 🔍 Manual Integration Tests

### **Test A: Cognitive Crawler End-to-End**

**Purpose:** Verify cognitive crawler still works with general RAG tool

```bash
# 1. Start backend
cd backend_v2
source .venv/bin/activate
python app.py

# 2. Frontend: Navigate to /cognitive-crawler
# 3. Crawl a website (e.g., https://docs.python.org/3/)
# 4. Wait for crawl to complete
# 5. Switch to Chat mode
# 6. Ask: "What is asyncio?"
# 7. Expected: Answer from crawled docs with sources
```

**Success Criteria:**
- ✅ Crawling works (no errors)
- ✅ Chat mode works (answers questions)
- ✅ Sources are cited correctly
- ✅ No console errors

---

### **Test B: Investigative Journalist with Local RAG**

**Purpose:** Verify investigative journalist can use LOCAL RAG

```bash
# 1. Run investigative journalist
cd backend_v2/langgraph_master_agent/sub_agents/investigative_journalist
source ../../../.venv/bin/activate
python main.py

# 2. Watch for these log messages:
# "💾 Stored X articles in local RAG"
# Should appear after each iteration

# 3. Check MongoDB
# Collection: tender_vectors (or cognitive_crawler_vectors)
# Filter: { "thread_id": "inv_..." }
# Should see stored documents
```

**Success Criteria:**
- ✅ See "Stored X articles in local RAG" messages
- ✅ MongoDB contains documents with investigation_id as thread_id
- ✅ No errors during storage
- ✅ Investigation completes successfully

---

### **Test C: Cross-Investigation Global RAG**

**Purpose:** Verify global RAG can search across multiple investigations

```bash
# 1. Run two investigations on related topics
cd backend_v2/langgraph_master_agent/sub_agents/investigative_journalist
python main.py  # Investigation 1: "FDA regulatory failures"
python main.py  # Investigation 2: "Pharmaceutical company violations"

# 2. Test global RAG query
cd ../../..
python -c "
import asyncio
from langgraph_master_agent.tools.rag_query import query_global_rag

async def test():
    result = await query_global_rag(
        query='What patterns of regulatory failures exist?',
        top_k=10
    )
    print(f'Found {result[\"num_results\"]} results across investigations')
    print(f'Sources: {len(result[\"sources\"])}')
    print(f'Answer: {result[\"answer\"][:200]}...')

asyncio.run(test())
"
```

**Success Criteria:**
- ✅ Finds results from both investigations
- ✅ Answer synthesizes information from multiple sources
- ✅ Sources include URLs from both investigations

---

## 📊 MongoDB Verification Tests

### **Check Stored Vectors:**

```javascript
// MongoDB Compass or CLI

// 1. Check total vectors
db.tender_vectors.count()

// 2. Check vectors by thread_id
db.tender_vectors.find({ "thread_id": "inv_abc123" }).count()

// 3. Check recent vectors
db.tender_vectors.find().sort({ "created_at": -1 }).limit(5)

// 4. Check vector structure
db.tender_vectors.findOne()
// Should have: content, embedding, url, thread_id, created_at
```

---

## 🔬 Performance Tests

### **Test D: Query Performance**

```python
import asyncio
import time
from langgraph_master_agent.tools.rag_query import query_rag

async def test_performance():
    # Test global query performance
    start = time.time()
    result = await query_rag("test query", thread_id=None, top_k=30)
    global_time = time.time() - start
    
    # Test local query performance  
    start = time.time()
    result = await query_rag("test query", thread_id="test_123", top_k=30)
    local_time = time.time() - start
    
    print(f"Global query: {global_time:.2f}s")
    print(f"Local query: {local_time:.2f}s")
    print(f"Expected: Both < 3 seconds")

asyncio.run(test_performance())
```

**Success Criteria:**
- ✅ Global queries: < 3 seconds
- ✅ Local queries: < 3 seconds (should be faster due to filtering)
- ✅ No timeouts or errors

---

## 🐛 Troubleshooting

### **Issue: "No module named 'mongodb_handler'"**

**Solution:**
```bash
# Check sys.path configuration
cd backend_v2/langgraph_master_agent/tools
python -c "
import sys
import os
sys.path.append('../sub_agents/cognitive_crawler/tools')
from mongodb_handler import TenderMongoDBHandler
print('✅ Import successful')
"
```

### **Issue: "Vector index not found"**

**Solution:**
- Go to MongoDB Atlas
- Navigate to your cluster → Collections
- Create vector search index named "vector_index"
- Field: "embedding"
- Dimensions: 1536
- Similarity: cosine

### **Issue: "No results found in local RAG"**

**Possible causes:**
1. Investigation hasn't stored any documents yet (run more iterations)
2. thread_id mismatch (check logs for actual investigation_id)
3. MongoDB connection issue (check credentials)

**Debug:**
```python
# Check what's actually stored
import asyncio
from langgraph_master_agent.sub_agents.cognitive_crawler.tools.mongodb_handler import TenderMongoDBHandler

async def debug():
    db = TenderMongoDBHandler()
    collection = db.db['tender_vectors']
    count = await collection.count_documents({})
    print(f"Total vectors: {count}")
    
    # Check thread_ids
    pipeline = [{"$group": {"_id": "$thread_id", "count": {"$sum": 1}}}]
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=100)
    print(f"Thread IDs: {results}")

asyncio.run(debug())
```

---

## ✅ Expected Results Summary

### **Backward Compatibility:**
- ✅ All existing tests pass
- ✅ Cognitive crawler works unchanged
- ✅ No breaking changes

### **New Features:**
- ✅ LOCAL RAG filters by thread_id correctly
- ✅ Investigative journalist auto-stores content
- ✅ General RAG tool works for all sub-agents
- ✅ Both local and global modes functional

### **Performance:**
- ✅ Query latency < 3 seconds
- ✅ Storage is non-blocking
- ✅ No memory leaks

---

## 📋 Test Checklist

### **Before Deployment:**

- [ ] Quick test passes
- [ ] Comprehensive test suite passes (all 7 tests)
- [ ] Cognitive crawler manual test works
- [ ] Investigative journalist stores content correctly
- [ ] Global RAG finds cross-investigation results
- [ ] MongoDB vectors verified
- [ ] Performance tests acceptable
- [ ] No linter errors
- [ ] Documentation updated

### **After Deployment:**

- [ ] Monitor MongoDB vector storage growth
- [ ] Check query performance in production
- [ ] Verify no errors in production logs
- [ ] User testing feedback collected

---

## 🚀 Running All Tests (Complete Flow)

```bash
#!/bin/bash
# Complete test flow

echo "Starting comprehensive LOCAL RAG testing..."

# 1. Quick sanity check
echo "\n📊 Step 1: Quick Test"
python quick_test_rag.py
if [ $? -ne 0 ]; then
    echo "❌ Quick test failed - stopping"
    exit 1
fi

# 2. Comprehensive test suite
echo "\n📊 Step 2: Comprehensive Tests"
python test_local_rag_implementation.py
if [ $? -ne 0 ]; then
    echo "❌ Comprehensive tests failed - stopping"
    exit 1
fi

# 3. Lint check
echo "\n📊 Step 3: Linting"
# Add your linter command here

echo "\n✅ ALL TESTS PASSED!"
echo "System is ready for deployment"
```

---

## 📞 Support

**If tests fail:**
1. Check MongoDB connection
2. Verify environment variables (.env file)
3. Check Python version (3.11+)
4. Review error logs in console
5. Check MongoDB Atlas vector index exists

**Still having issues?**
- Review LOCAL_RAG_IMPLEMENTATION.md
- Check recent git commits for breaking changes
- Verify dependencies are installed: `pip install -r requirements.txt`

---

**Testing Time Estimate:**
- Quick test: 5 minutes
- Comprehensive tests: 15-20 minutes
- Manual integration tests: 15 minutes
- **Total: ~35-40 minutes for complete validation**

---

**Last Updated:** October 19, 2025  
**Status:** Ready for Testing  
**Version:** 1.0

