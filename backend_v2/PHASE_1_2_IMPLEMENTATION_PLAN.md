# Phase 1 & 2 Implementation Plan
## Agent Expansion for Political Analyst Platform

**Timeline:** 4 weeks  
**Team Size:** 3-6 developers (can work in parallel)  
**Tech Stack:** Python, LangGraph, Plotly, NetworkX, Tavily API, OpenAI API  
**Status:** 🟡 IN PROGRESS - 1/6 agents complete

---

## 🎉 Progress Update (Oct 2, 2025)

### ✅ Completed: Sentiment Analyzer
- **Development:** 3 hours
- **Testing:** Standalone ✅ + Integration ✅
- **Validation:** Full validation report created
- **Files Modified:** 1 (sub_agent_caller.py)
- **Documentation:** Development guide + validation report
- **Status:** OPERATIONAL & READY FOR USE

**Key Achievement:** Modular development approach VALIDATED!

---

## 📋 Overview

This document outlines the implementation plan for adding 6 new specialized sub-agents to the Political Analyst platform. Each agent operates independently within the master agent architecture and produces specific visual artifacts.

---

## 🏗️ Architecture Pattern

All sub-agents follow this structure:
```
sub_agents/{agent_name}/
├── README.md              # Team instructions (detailed)
├── __init__.py            # Package initialization
├── state.py               # TypedDict state schema
├── graph.py               # LangGraph workflow definition
├── config.py              # Agent-specific configuration
├── nodes/                 # Processing nodes
│   ├── __init__.py
│   ├── analyzer.py        # Main analysis logic
│   ├── synthesizer.py     # Result synthesis
│   └── visualizer.py      # Artifact generation
├── tools/                 # Agent-specific tools
│   ├── __init__.py
│   └── {tool_name}.py
├── artifacts/             # Generated artifacts (HTML/PNG)
└── tests/                 # Unit and integration tests
    ├── __init__.py
    ├── test_agent.py
    └── test_integration.py
```

---

## 📅 Phase 1: Quick Wins (Week 1-2)

### **Priority Level:** 🔥 CRITICAL

### Agent 1: Sentiment Analyzer
- **Folder:** `langgraph_master_agent/sub_agents/sentiment_analyzer/`
- **Team:** 2 developers
- **Timeline:** 2-3 days
- **Dependencies:** Tavily, Plotly, OpenAI
- **Artifacts:** 
  - Global sentiment choropleth map
  - Multi-country radar chart
  - Sentiment trend timeline
  - Bias detection report

### Agent 2: Media Bias Detector
- **Folder:** `langgraph_master_agent/sub_agents/media_bias_detector/`
- **Team:** 2 developers
- **Timeline:** 2-3 days
- **Dependencies:** Tavily, Plotly, OpenAI
- **Artifacts:**
  - Bias spectrum chart
  - Source comparison matrix
  - Loaded language word cloud
  - Multi-source framing analysis

### Agent 3: Comparative Analysis
- **Folder:** `langgraph_master_agent/sub_agents/comparative_analysis/`
- **Team:** 1 developer
- **Timeline:** 1-2 days
- **Dependencies:** Reuses Sentiment + Bias agents
- **Artifacts:**
  - Multi-dimensional radar chart
  - Side-by-side comparison table
  - Diverging bar chart
  - Statistical difference report

**Phase 1 Deliverable:** 3 agents producing 11 artifact types

---

## 📅 Phase 2: Premium Features (Week 3-4)

### **Priority Level:** ⭐ HIGH

### Agent 4: Entity & Relationship Extractor
- **Folder:** `langgraph_master_agent/sub_agents/entity_relationship_extractor/`
- **Team:** 2 developers
- **Timeline:** 4-5 days
- **Dependencies:** NetworkX, PyVis, Plotly, OpenAI
- **Artifacts:**
  - Interactive network graph (HTML)
  - Influence flow Sankey diagram
  - Entity timeline
  - Geopolitical alliance map

### Agent 5: Fact Checker
- **Folder:** `langgraph_master_agent/sub_agents/fact_checker/`
- **Team:** 2 developers
- **Timeline:** 4-5 days
- **Dependencies:** Tavily, Plotly, OpenAI
- **Artifacts:**
  - Truth score card
  - Evidence chain network
  - Source credibility matrix
  - Timeline verification chart

### Agent 6: Crisis Event Tracker
- **Folder:** `langgraph_master_agent/sub_agents/crisis_event_tracker/`
- **Team:** 1-2 developers
- **Timeline:** 3-4 days
- **Dependencies:** Folium, Plotly, Tavily, OpenAI
- **Artifacts:**
  - Real-time event map with markers
  - Event timeline with severity
  - Impact ripple diagram
  - Multi-country response comparison

**Phase 2 Deliverable:** 3 additional agents producing 12+ artifact types

---

## 🔧 Technical Requirements

### Python Packages to Install
```bash
# Already in requirements.txt
plotly
pandas
openai
tavily-python

# NEW packages needed
uv pip install networkx
uv pip install pyvis
uv pip install folium
uv pip install wordcloud
uv pip install python-dotenv
```

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
TEMPERATURE=0
DEFAULT_MODEL=gpt-4o-mini
ARTIFACT_DIR=artifacts
```

---

## 🎯 Integration Points

### 1. Update Sub-Agent Caller
**File:** `langgraph_master_agent/tools/sub_agent_caller.py`

Add methods for each new agent:
```python
async def call_sentiment_analyzer(self, query: str, countries: list) -> Dict
async def call_media_bias_detector(self, query: str) -> Dict
async def call_comparative_analysis(self, entities: list) -> Dict
async def call_entity_extractor(self, query: str) -> Dict
async def call_fact_checker(self, claim: str) -> Dict
async def call_crisis_tracker(self, region: str) -> Dict
```

### 2. Update Strategic Planner
**File:** `langgraph_master_agent/nodes/strategic_planner.py`

Add agent selection logic to route queries to appropriate sub-agents.

### 3. Update State Schema
**File:** `langgraph_master_agent/state.py`

Ensure `sub_agent_results` can store results from all new agents.

### 4. Update API Endpoints
**File:** `backend_v2/app.py`

No changes needed - artifacts automatically served via existing `/api/artifacts/` endpoint.

---

## 🧪 Testing Strategy

### Unit Tests (Each Agent)
- Test state transitions
- Test node logic in isolation
- Test artifact generation
- Test error handling

### Integration Tests
- Test agent called from master agent
- Test artifact saved to storage
- Test WebSocket streaming
- Test end-to-end query flow

### Test Queries
```python
# Sentiment Analyzer
"Analyze sentiment on nuclear policy across US, Iran, and Israel"

# Media Bias Detector
"Compare how CNN, Fox News, and BBC covered the recent summit"

# Comparative Analysis
"Compare India's and China's climate policies"

# Entity Extractor
"Map the relationships between key NATO members"

# Fact Checker
"Verify: 'Country X increased defense spending by 40% in 2024'"

# Crisis Tracker
"Track current political crises in Middle East"
```

---

## 📊 Success Metrics

### Phase 1 (Week 2 Review)
- ✅ 3 agents operational
- ✅ 11+ artifact types generated
- ✅ <5s average response time
- ✅ 90%+ artifact generation success rate
- ✅ Unit test coverage >80%

### Phase 2 (Week 4 Review)
- ✅ 6 total agents operational
- ✅ 23+ artifact types generated
- ✅ <8s average response time (complex agents)
- ✅ Master agent can route to any sub-agent
- ✅ Integration test coverage >70%

---

## 🚀 Deployment Checklist

### Before Deployment
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Artifacts export as HTML + PNG
- [ ] Error handling for API failures
- [ ] MongoDB artifact storage working
- [ ] Frontend can display new artifact types
- [ ] Documentation updated

### Deployment Steps
1. Merge feature branch to `main`
2. Update `requirements.txt`
3. Run database migrations (if needed)
4. Deploy to staging environment
5. Run smoke tests
6. Deploy to production
7. Monitor error logs for 24 hours

---

## 👥 Team Assignments (Suggested)

### Team A (Phase 1 - Week 1)
- **Developer 1 + 2:** Sentiment Analyzer
- **Developer 3 + 4:** Media Bias Detector

### Team A (Phase 1 - Week 2)
- **Developer 1:** Comparative Analysis
- **Developer 2-4:** Start Phase 2 agents

### Team B (Phase 2 - Week 3)
- **Developer 1 + 2:** Entity & Relationship Extractor
- **Developer 3 + 4:** Fact Checker

### Team B (Phase 2 - Week 4)
- **Developer 5 + 6:** Crisis Event Tracker
- **All:** Integration testing and bug fixes

---

## 📝 Development Workflow

1. **Read agent README.md** (detailed instructions)
2. **Create feature branch** (`feature/sentiment-analyzer`)
3. **Implement in order:**
   - State schema (`state.py`)
   - Configuration (`config.py`)
   - Nodes (`nodes/*.py`)
   - Tools (if needed) (`tools/*.py`)
   - Graph workflow (`graph.py`)
   - Unit tests (`tests/test_agent.py`)
4. **Test locally** with sample queries
5. **Generate sample artifacts** (save in `artifacts/`)
6. **Create PR** with screenshots of artifacts
7. **Code review** by tech lead
8. **Merge** after approval

---

## 🔗 Key Resources

- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **Plotly Docs:** https://plotly.com/python/
- **Tavily API:** https://docs.tavily.com/
- **NetworkX Docs:** https://networkx.org/
- **Internal Wiki:** See each agent's README.md

---

## ⚠️ Common Pitfalls

1. **Forgetting temperature=0** - Always use for consistency
2. **Not handling API failures** - Tavily/OpenAI can fail, add retries
3. **Large artifacts** - Keep HTML files <2MB, optimize PNG exports
4. **Blocking calls** - Use async/await everywhere
5. **Hardcoded values** - Use config.py for all parameters
6. **Missing error logs** - Add to state.error_log for debugging

---

## 📞 Support

- **Tech Lead:** Review architecture questions before coding
- **Daily Standups:** Share progress, blockers
- **Slack Channel:** `#agent-expansion`
- **Code Reviews:** Mandatory for all PRs

---

**Last Updated:** October 2, 2025  
**Document Owner:** Tech Lead  
**Status:** 🟢 Active Development

