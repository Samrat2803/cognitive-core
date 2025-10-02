# Integration Protocol - New Agents & Tools

## 🚨 CRITICAL RULE: Zero Impact on Existing Code

**DO NOT modify existing code until new agent is fully tested and approved.**

---

## 🔒 Isolation Strategy

### Phase 1: Development in Isolation
All new agents MUST be developed and tested in their own folders **WITHOUT touching any existing files**.

### Phase 2: Integration (Only After Approval)
After testing and approval, integrate with existing codebase through minimal changes.

---

## 📁 Folder Structure - Complete Isolation

Each agent folder is **100% self-contained**:

```
sub_agents/{agent_name}/
├── README.md                    # Complete instructions
├── __init__.py                  # Isolated package
├── state.py                     # Agent-specific state
├── config.py                    # Agent config
├── graph.py                     # Standalone graph
├── main.py                      # ⭐ STANDALONE RUNNER (test without master)
├── nodes/                       # All processing logic
├── tools/                       # Agent-specific tools
├── artifacts/                   # Test artifacts output here
├── tests/                       # Complete test suite
│   ├── test_agent.py           # Unit tests
│   ├── test_integration.py     # Integration tests
│   └── test_standalone.py      # Run agent standalone
└── examples/                    # Example queries and outputs
    ├── example_queries.txt
    └── sample_outputs.json
```

---

## 🧪 Testing Protocol

### Stage 1: Standalone Testing (NO master agent)
Run agent in complete isolation using `main.py`:

```python
# sub_agents/sentiment_analyzer/main.py

import asyncio
from graph import create_sentiment_analyzer_graph
from state import SentimentAnalyzerState

async def test_standalone():
    """Run agent WITHOUT master agent"""
    
    graph = create_sentiment_analyzer_graph()
    
    # Test with hardcoded input
    initial_state: SentimentAnalyzerState = {
        "query": "nuclear energy policy",
        "countries": ["US", "France", "Germany"],
        "time_range_days": 7,
        # ... initialize all state fields
    }
    
    print("🚀 Running Sentiment Analyzer in STANDALONE mode...")
    result = await graph.ainvoke(initial_state)
    
    print(f"\n✅ SUCCESS")
    print(f"Sentiment Scores: {result['sentiment_scores']}")
    print(f"Artifacts Generated: {len(result['artifacts'])}")
    print(f"Confidence: {result['confidence']}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_standalone())
```

**Run standalone:**
```bash
cd backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer
python main.py
```

**Stage 1 Checklist:**
- [ ] Agent runs without any imports from master agent
- [ ] Generates all expected artifacts
- [ ] Artifacts saved in local `artifacts/` folder
- [ ] All unit tests passing
- [ ] No errors in execution log
- [ ] Response time acceptable

---

### Stage 2: Mock Integration Testing
Test integration points using MOCK master agent:

```python
# sub_agents/sentiment_analyzer/tests/test_mock_integration.py

import asyncio
from unittest.mock import Mock
from ..graph import create_sentiment_analyzer_graph

async def test_mock_integration():
    """Test as if called by master agent (but mocked)"""
    
    # Mock the master agent call
    mock_master_state = {
        "sub_agent_results": {},
        "execution_log": []
    }
    
    # Call our agent
    graph = create_sentiment_analyzer_graph()
    result = await graph.ainvoke({
        "query": "climate policy",
        "countries": ["US", "UK"],
        "time_range_days": 7,
        # ... rest
    })
    
    # Verify it returns expected format
    assert "sentiment_scores" in result
    assert "artifacts" in result
    assert "confidence" in result
    
    # Simulate master agent receiving result
    mock_master_state["sub_agent_results"]["sentiment_analyzer"] = result
    
    print("✅ Mock integration successful")
    return True

if __name__ == "__main__":
    asyncio.run(test_mock_integration())
```

**Run mock integration:**
```bash
cd backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer
python -m pytest tests/test_mock_integration.py -v
```

**Stage 2 Checklist:**
- [ ] Agent can be called as async function
- [ ] Returns dict with expected keys
- [ ] Result format matches master agent expectations
- [ ] Error handling works correctly
- [ ] No side effects on caller's state

---

### Stage 3: Real Integration (After Approval Only)

**⚠️ ONLY proceed after:**
1. Stage 1 and 2 tests passing
2. Code review approved
3. Tech lead approval
4. Example artifacts reviewed

**Integration Steps:**

#### Step 3.1: Create Integration Branch
```bash
git checkout -b integrate/sentiment-analyzer
```

#### Step 3.2: Update Sub-Agent Caller (ONLY FILE TO MODIFY)
**File:** `langgraph_master_agent/tools/sub_agent_caller.py`

Add ONLY the new method (don't touch existing methods):

```python
# ADD THIS METHOD - DON'T MODIFY ANYTHING ELSE
@observe(name="sentiment_analysis_sub_agent")
async def call_sentiment_analyzer(
    self,
    query: str,
    countries: list = None,
    time_range_days: int = 7
) -> Dict[str, Any]:
    """
    Call Sentiment Analysis Sub-Agent
    
    TESTED STANDALONE: ✅ 2025-10-02
    """
    # Import only when called (lazy loading)
    from langgraph_master_agent.sub_agents.sentiment_analyzer import create_sentiment_analyzer_graph
    
    graph = create_sentiment_analyzer_graph()
    
    initial_state = {
        "query": query,
        "countries": countries or [],
        "time_range_days": time_range_days,
        "search_results": {},
        "sentiment_scores": {},
        "bias_analysis": {},
        "summary": "",
        "key_findings": [],
        "confidence": 0.0,
        "artifacts": [],
        "execution_log": [],
        "error_log": []
    }
    
    try:
        result = await graph.ainvoke(initial_state)
        return {
            "success": True,
            "sub_agent": "sentiment_analyzer",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "sub_agent": "sentiment_analyzer",
            "error": str(e)
        }
```

#### Step 3.3: Update Strategic Planner (Optional - if auto-routing needed)
**File:** `langgraph_master_agent/nodes/strategic_planner.py`

Add detection logic for sentiment queries:

```python
# ADD to existing tool selection logic
if any(keyword in query.lower() for keyword in ["sentiment", "opinion", "view", "perception"]):
    if any(country in query for country in ["US", "UK", "France", "Germany", "China"]):
        tools_to_use.append("sentiment_analyzer")
```

#### Step 3.4: Integration Test with Real Master Agent
```bash
cd backend_v2
python test_server.py
```

Test query through full stack:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze sentiment on nuclear policy in US, France, Germany"}'
```

**Stage 3 Checklist:**
- [ ] Master agent can call new agent
- [ ] Artifacts served via `/api/artifacts/` endpoint
- [ ] No breaking changes to existing endpoints
- [ ] All existing tests still passing
- [ ] New integration test added and passing

---

## 🔄 Rollback Plan

If integration causes issues:

```bash
# Immediate rollback
git checkout main

# Or revert specific file
git checkout main -- langgraph_master_agent/tools/sub_agent_caller.py
```

The agent code remains in its folder - no cleanup needed.

---

## 📊 Files Modified During Integration (By Stage)

### Standalone Development (Stage 1)
**Modified Files:** NONE in existing codebase  
**New Files:** Only in `sub_agents/{agent_name}/` folder

### Mock Testing (Stage 2)
**Modified Files:** NONE in existing codebase  
**New Files:** Test files in agent folder

### Real Integration (Stage 3)
**Modified Files:** 
- `langgraph_master_agent/tools/sub_agent_caller.py` (add 1 method)
- `langgraph_master_agent/nodes/strategic_planner.py` (optional, add routing logic)

**That's it - ONLY 1-2 files modified!**

---

## 🎯 Integration Priority Order

Integrate ONE agent at a time:

1. **Sentiment Analyzer** (Week 1)
   - Test standalone Week 1 Day 1-2
   - Integrate Week 1 Day 3
   
2. **Media Bias Detector** (Week 1)
   - Test standalone Week 1 Day 3-4
   - Integrate Week 1 Day 5
   
3. **Comparative Analysis** (Week 2)
   - Test standalone Week 2 Day 1
   - Integrate Week 2 Day 2
   
4. **Entity Extractor** (Week 3)
   - Test standalone Week 3 Day 1-3
   - Integrate Week 3 Day 4
   
5. **Fact Checker** (Week 3-4)
   - Test standalone Week 3 Day 4-5
   - Integrate Week 4 Day 1
   
6. **Crisis Tracker** (Week 4)
   - Test standalone Week 4 Day 2-3
   - Integrate Week 4 Day 4

---

## ⚠️ What NOT To Do

### ❌ DON'T:
- Don't modify `langgraph_master_agent/state.py` (unless absolutely necessary)
- Don't change existing nodes in `langgraph_master_agent/nodes/`
- Don't modify `langgraph_master_agent/graph.py`
- Don't change `backend_v2/app.py` API endpoints
- Don't modify `shared/` utilities
- Don't update `requirements.txt` until agent is approved

### ✅ DO:
- Create completely isolated agent folders
- Test thoroughly in standalone mode
- Use lazy imports in sub_agent_caller
- Add comprehensive error handling
- Document all integration points
- Create rollback plan before integrating

---

## 🧪 Validation Checklist Before Integration PR

### Code Quality
- [ ] All unit tests passing (>80% coverage)
- [ ] All integration tests passing
- [ ] No linter errors
- [ ] Code reviewed by peer
- [ ] Documentation complete

### Functional Testing
- [ ] Agent runs standalone successfully
- [ ] Generates all expected artifacts (HTML + PNG)
- [ ] Response time within acceptable range (<8s)
- [ ] Error handling tested (API failures, bad input)
- [ ] Edge cases handled

### Integration Readiness
- [ ] Mock integration tests passing
- [ ] Return format matches expectations
- [ ] No dependencies on modified master agent code
- [ ] Lazy imports used (won't affect startup if not used)
- [ ] Rollback plan documented

### Artifacts & Examples
- [ ] 3+ sample artifacts generated
- [ ] Example queries documented
- [ ] Sample outputs saved
- [ ] Screenshots in PR description

### Approval
- [ ] Tech lead reviewed standalone implementation
- [ ] Sample artifacts approved
- [ ] Integration plan approved
- [ ] Deployment plan reviewed

---

## 📝 PR Template for Integration

```markdown
## Integration: [Agent Name]

### Standalone Testing Results
- ✅ All unit tests passing (X/X)
- ✅ Integration tests passing (X/X)
- ✅ Standalone execution successful
- ✅ Response time: Xs average

### Sample Artifacts
[Attach screenshots or links to artifacts]

### Files Modified
- `langgraph_master_agent/tools/sub_agent_caller.py` (+X lines)
- [Any other files]

### Test Queries Used
1. "Query 1"
2. "Query 2"
3. "Query 3"

### Rollback Plan
```bash
git revert <commit-hash>
```

### Checklist
- [ ] Code reviewed
- [ ] Existing tests still passing
- [ ] New tests added
- [ ] Documentation updated
- [ ] Tech lead approved
```

---

## 🚀 Deployment Strategy

### Development Environment
- Agents developed and tested locally
- No impact on dev server

### Staging Environment
- Integration tested on staging
- Run full regression suite
- Load testing with new agent

### Production Environment
- Deploy during low-traffic window
- Monitor error rates for 24 hours
- Enable feature flag if possible
- Keep previous version ready for rollback

---

## 📞 Support During Integration

### Questions Before Integration
- **Architecture questions:** Tech lead
- **Testing issues:** QA team
- **Integration blockers:** Project manager

### Issues During Integration
- **Immediate issues:** Rollback and investigate
- **Performance issues:** Profile and optimize
- **Error spikes:** Check logs, may need hotfix

---

**Last Updated:** October 2, 2025  
**Document Owner:** Tech Lead  
**Status:** 🔒 MANDATORY PROTOCOL

