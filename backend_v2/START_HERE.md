# 🚀 Agent Expansion Project - START HERE

## 📋 Quick Reference

**Project Goal:** Add 9 specialized sub-agents to the Political Analyst platform  
**Timeline:** 6 weeks (3 phases)  
**Status:** 🟡 In Progress - 1/9 agents complete

---

## 📚 REQUIRED READING - Before You Start

### 🔴 CRITICAL - Must Read (Order Matters!)

1. **AGENT_DEVELOPMENT_GUIDE.md** ⭐ **READ THIS FIRST!**
   - ✅ Validated lessons from Sentiment Analyzer
   - ✅ Critical success factors (imports, env vars, APIs)
   - ✅ Common errors & fixes
   - ✅ Step-by-step build checklist
   - ✅ Integration workflow
   - ⏱️ 15-20 minutes read
   - **WHY:** Saves 2-4 hours of debugging time

2. **INTEGRATION_PROTOCOL.md** ⚠️ **MANDATORY**
   - ✅ Zero-impact development strategy
   - ✅ 3-stage testing (standalone → mock → real)
   - ✅ Rollback procedures
   - ✅ What NOT to do
   - ⏱️ 10 minutes read
   - **WHY:** Prevents breaking existing code

3. **SENTIMENT_ANALYZER_VALIDATION.md** ✅ **Proof of Concept**
   - ✅ Complete validation report
   - ✅ Real test results
   - ✅ Performance metrics
   - ✅ What worked / didn't work
   - ⏱️ 5 minutes read
   - **WHY:** Shows the approach works

### 🟡 IMPORTANT - Project Context

4. **IMPLEMENTATION_STATUS.md**
   - Current progress (1/9 agents)
   - What's completed vs. pending
   - Timeline & milestones
   - Next agent to build
   - ⏱️ 5 minutes read

5. **COMPLETE_AGENT_ROADMAP.md**
   - All 9 agents overview
   - Dependencies between agents
   - Artifact types (35+)
   - User workflows
   - ⏱️ 10 minutes read

6. **PHASE_1_2_IMPLEMENTATION_PLAN.md**
   - Original 6-agent plan
   - Team assignments
   - Success metrics
   - ⏱️ 8 minutes read

### 🟢 REFERENCE - Agent Specifics

7. **Agent-Specific READMEs** (Read when building that agent)
   - `/sub_agents/sentiment_analyzer/README.md` ✅ (Complete - use as template)
   - `/sub_agents/media_bias_detector/README.md`
   - `/sub_agents/comparative_analysis/README.md`
   - `/sub_agents/entity_relationship_extractor/README.md`
   - `/sub_agents/fact_checker/README.md`
   - `/sub_agents/crisis_event_tracker/README.md`
   - `/sub_agents/live_political_monitor/README.md`
   - `/sub_agents/sitrep_generator/README.md`
   - `/sub_agents/policy_brief_generator/README.md`

---

## ⚡ Quick Start - New Developer Onboarding

### Step 1: Read Core Docs (30 minutes)
```bash
cd backend_v2

# Critical reads (in order)
1. cat AGENT_DEVELOPMENT_GUIDE.md        # 15 min - MOST IMPORTANT
2. cat INTEGRATION_PROTOCOL.md           # 10 min
3. cat SENTIMENT_ANALYZER_VALIDATION.md  # 5 min
```

### Step 2: Check Current Status (5 minutes)
```bash
4. cat IMPLEMENTATION_STATUS.md          # See what's done/pending
```

### Step 3: Understand Your Agent (10 minutes)
```bash
5. cat sub_agents/{your_agent}/README.md  # Full implementation guide
```

### Step 4: Start Building (Follow the guide!)
```bash
cd sub_agents/{your_agent}
# Follow steps in AGENT_DEVELOPMENT_GUIDE.md
```

**Total Onboarding Time:** ~45 minutes  
**Time Saved in Development:** 2-4 hours (from avoiding common mistakes)

---

## 📁 Documentation Structure (Full List)

### Planning & Strategy
- ✅ `START_HERE.md` (this file) - Entry point & resource list
- ✅ `COMPLETE_AGENT_ROADMAP.md` - All 9 agents, full vision
- ✅ `PHASE_1_2_IMPLEMENTATION_PLAN.md` - Original implementation plan
- ✅ `IMPLEMENTATION_STATUS.md` - Current progress tracking

### Development Guides
- ✅ `AGENT_DEVELOPMENT_GUIDE.md` ⭐ **MOST IMPORTANT**
- ✅ `INTEGRATION_PROTOCOL.md` - Safety & testing protocols
- ✅ `SENTIMENT_ANALYZER_VALIDATION.md` - Proof of concept

### Agent-Specific (9 agents)
- ✅ `sub_agents/sentiment_analyzer/README.md` (COMPLETE - use as template)
- 🟢 `sub_agents/media_bias_detector/README.md` (Ready)
- 🟢 `sub_agents/comparative_analysis/README.md` (Ready)
- 🟢 `sub_agents/entity_relationship_extractor/README.md` (Ready)
- 🟢 `sub_agents/fact_checker/README.md` (Ready)
- 🟢 `sub_agents/crisis_event_tracker/README.md` (Ready)
- 🟢 `sub_agents/live_political_monitor/README.md` (Ready)
- 🟢 `sub_agents/sitrep_generator/README.md` (Ready)
- 🟢 `sub_agents/policy_brief_generator/README.md` (Ready)

---

## 🎯 Documentation Reading Strategy

### If You're Building Your First Agent
**Required Reading Order:**
1. ✅ AGENT_DEVELOPMENT_GUIDE.md (CRITICAL)
2. ✅ INTEGRATION_PROTOCOL.md (CRITICAL)
3. ✅ SENTIMENT_ANALYZER_VALIDATION.md (See proof)
4. ✅ IMPLEMENTATION_STATUS.md (Know where we are)
5. ✅ Your agent's README.md (Specific instructions)

**Time:** ~45 minutes  
**Skip at your peril:** Will cost 2-4 hours in debugging

### If You've Built an Agent Before
**Quick Refresh:**
1. ✅ AGENT_DEVELOPMENT_GUIDE.md (Quick skim for reminders)
2. ✅ IMPLEMENTATION_STATUS.md (What's changed)
3. ✅ Your agent's README.md (Specific instructions)

**Time:** ~15 minutes

### If You're the Team Lead
**Everything:**
1. ✅ All planning docs (understand full scope)
2. ✅ All development guides (review process)
3. ✅ All agent READMEs (know what team is building)

**Time:** ~2 hours initial, then ~30 min/week for updates

---

## 🏆 Phase 1: Quick Wins (Week 1-2)

### Agent 1: Sentiment Analyzer 😊😐😠
- **Folder:** `sub_agents/sentiment_analyzer/`
- **Team:** 2 developers
- **Duration:** 2-3 days
- **Artifacts:** Global sentiment map, radar chart, trend line, bias report
- **Impact:** ⭐⭐⭐⭐⭐ Very High
- **Effort:** ⭐⭐ Low-Medium

### Agent 2: Media Bias Detector 📰⚖️
- **Folder:** `sub_agents/media_bias_detector/`
- **Team:** 2 developers
- **Duration:** 2-3 days
- **Artifacts:** Bias spectrum chart, comparison matrix, word cloud
- **Impact:** ⭐⭐⭐⭐⭐ Very High
- **Effort:** ⭐⭐ Low-Medium

### Agent 3: Comparative Analysis ⚖️
- **Folder:** `sub_agents/comparative_analysis/`
- **Team:** 1 developer
- **Duration:** 1-2 days
- **Artifacts:** Radar chart, comparison table, diverging bars
- **Impact:** ⭐⭐⭐⭐ High
- **Effort:** ⭐⭐ Low

**Phase 1 Deliverable:** 3 agents, 11+ artifacts

---

## 🥈 Phase 2: Premium Features (Week 3-4)

### Agent 4: Entity & Relationship Extractor 🔗
- **Folder:** `sub_agents/entity_relationship_extractor/`
- **Team:** 2 developers
- **Duration:** 4-5 days
- **Artifacts:** Interactive network graph, Sankey diagram, alliance map
- **Impact:** ⭐⭐⭐⭐⭐ Very High (Most visually impressive!)
- **Effort:** ⭐⭐⭐ Medium

### Agent 5: Fact Checker ✅
- **Folder:** `sub_agents/fact_checker/`
- **Team:** 2 developers
- **Duration:** 4-5 days
- **Artifacts:** Truth gauge, evidence chain, credibility matrix
- **Impact:** ⭐⭐⭐⭐⭐ Very High (Highest trust value!)
- **Effort:** ⭐⭐⭐ Medium

### Agent 6: Crisis Event Tracker 🚨
- **Folder:** `sub_agents/crisis_event_tracker/`
- **Team:** 1-2 developers
- **Duration:** 3-4 days
- **Artifacts:** Real-time map, event timeline, impact ripple
- **Impact:** ⭐⭐⭐⭐ High (Time-sensitive!)
- **Effort:** ⭐⭐⭐ Medium

**Phase 2 Deliverable:** 3 additional agents, 12+ artifacts

---

## 🔒 Core Principle: ISOLATION FIRST

### ⚠️ CRITICAL RULES:

1. **NO modifications to existing code** during development
2. **ALL agents must work standalone** before integration
3. **Test in 3 stages:**
   - Stage 1: Standalone (no master agent)
   - Stage 2: Mock integration
   - Stage 3: Real integration (after approval only)

### 📂 Folder Structure (Self-Contained)

```
sub_agents/{agent_name}/
├── README.md              # 📖 Your instruction manual
├── main.py                # ⭐ Standalone runner (test without master)
├── state.py               # State schema
├── config.py              # Configuration
├── graph.py               # LangGraph workflow
├── nodes/                 # Processing nodes
│   ├── analyzer.py
│   ├── synthesizer.py
│   └── visualizer.py
├── tools/                 # Agent-specific tools
├── artifacts/             # Generated artifacts (local testing)
├── tests/                 # Unit + integration tests
└── examples/              # Sample outputs
```

---

## 🚀 Getting Started (Developer Workflow)

### Step 1: Choose Your Agent
```bash
# Example: Working on Sentiment Analyzer
cd backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer
```

### Step 2: Read the README
```bash
# Open the agent-specific README
cat README.md
# or open in your editor
```

### Step 3: Create Feature Branch
```bash
git checkout -b feature/sentiment-analyzer
```

### Step 4: Implement Files (in order)
1. `state.py` - Define state schema
2. `config.py` - Configuration constants
3. `nodes/*.py` - Implement each node
4. `graph.py` - Wire nodes into LangGraph
5. `main.py` - Standalone test runner
6. `tests/test_agent.py` - Unit tests

### Step 5: Test Standalone
```bash
# Run standalone (NO master agent)
python main.py

# Run tests
python -m pytest tests/ -v
```

### Step 6: Generate Sample Artifacts
```bash
# Should create artifacts in ./artifacts/
ls artifacts/
# sentiment_map_abc123.html
# sentiment_radar_def456.png
# ...
```

### Step 7: Create PR (After Standalone Testing Passes)
```bash
git add .
git commit -m "feat: Sentiment Analyzer agent (standalone tested)"
git push origin feature/sentiment-analyzer
# Create PR with artifact screenshots
```

### Step 8: Integration (After Approval)
- Tech lead reviews standalone implementation
- Approved → Proceed to integration
- Update `sub_agent_caller.py` (ONLY FILE TO TOUCH)
- Test with master agent
- Deploy

---

## 📦 Required Packages

### Already Installed
- `plotly` - Visualizations
- `pandas` - Data manipulation
- `openai` - LLM calls
- `tavily-python` - Search API
- `python-dotenv` - Environment variables

### New Packages Needed
```bash
# Install these as needed per agent
uv pip install networkx      # For Entity Extractor
uv pip install pyvis         # For network graphs
uv pip install folium        # For crisis maps
uv pip install wordcloud     # For word clouds
```

---

## 🧪 Testing Commands

### Unit Tests (Each Agent)
```bash
cd sub_agents/{agent_name}
python -m pytest tests/test_agent.py -v
```

### Standalone Test (No Master)
```bash
cd sub_agents/{agent_name}
python main.py
```

### Mock Integration Test
```bash
cd sub_agents/{agent_name}
python -m pytest tests/test_mock_integration.py -v
```

### Real Integration Test (After integration)
```bash
cd backend_v2
python test_server.py
```

---

## 📊 Success Criteria

### Per Agent
- ✅ Runs standalone successfully
- ✅ Generates all expected artifacts (HTML + PNG)
- ✅ Response time within target (<8s)
- ✅ Unit tests passing (>80% coverage)
- ✅ No errors in execution log
- ✅ Sample artifacts reviewed and approved

### Phase 1 Completion
- ✅ 3 agents operational
- ✅ 11+ artifact types
- ✅ All standalone tests passing
- ✅ Zero impact on existing code

### Phase 2 Completion
- ✅ 6 total agents operational
- ✅ 23+ artifact types
- ✅ Integration tests passing
- ✅ Deployed to production

---

## 🆘 Need Help?

### Questions Before Starting
1. Read agent's README.md (most questions answered there)
2. Check INTEGRATION_PROTOCOL.md (testing questions)
3. Ask tech lead (architecture questions)

### During Development
- **Can't get agent working?** Check `.env` file has API keys
- **Tavily API errors?** Check rate limits
- **Visualization not rendering?** Check artifact directory path
- **Import errors?** Make sure you're in the right directory

### During Integration
- **Master agent can't find sub-agent?** Check import path
- **Existing tests failing?** You may have modified existing code (rollback!)
- **Performance issues?** Profile with `cProfile`

---

## 📞 Support Channels

- **Tech Lead:** Architecture and integration approval
- **Daily Standups:** Progress and blockers
- **Slack:** `#agent-expansion`
- **Code Reviews:** All PRs need approval

---

## 🎯 Current Status

### Completed ✅
- [x] Project planning
- [x] Folder structure created
- [x] Agent READMEs written
- [x] Integration protocol defined
- [x] Standalone runner templates created
- [x] **Phase 1 Agent 1: Sentiment Analyzer** ✅ (Oct 2, 2025)
  - Standalone tested: PASSED
  - Integration tested: PASSED
  - Real data validated: PASSED
  - Artifacts generating: PASSED
  - Development guide created: COMPLETE

### In Progress 🟡
- [ ] Phase 1 Agent 2: Media Bias Detector (NEXT)

### Ready to Start 🟢
- [ ] Phase 1 Agent 3: Comparative Analysis
- [ ] Phase 2 Agent 4: Entity Extractor
- [ ] Phase 2 Agent 5: Fact Checker
- [ ] Phase 2 Agent 6: Crisis Tracker
- [ ] Phase 0 Foundation: Live Political Monitor
- [ ] Phase 2 Core: SitRep Generator
- [ ] Phase 2 Core: Policy Brief Generator

---

## 🔥 Quick Start (TL;DR)

```bash
# 1. Choose agent
cd backend_v2/langgraph_master_agent/sub_agents/sentiment_analyzer

# 2. Read README
cat README.md

# 3. Implement files
# (follow README instructions)

# 4. Test standalone
python main.py

# 5. Run tests
python -m pytest tests/ -v

# 6. Submit PR with artifact screenshots
git push origin feature/your-agent-name
```

---

**Last Updated:** October 2, 2025  
**Project Start Date:** October 2, 2025  
**Expected Completion:** October 30, 2025  
**Status:** 🟢 Ready for Development

---

## 🎉 Let's Build This!

You have everything you need to start building. Each agent is isolated, well-documented, and designed for success.

**Remember:** Test standalone first, integrate later. Good luck! 🚀

