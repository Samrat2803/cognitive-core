# **INVESTIGATIVE JOURNALIST V2 - COMPLETE IMPLEMENTATION GUIDE**

---

## **TABLE OF CONTENTS**

1. [Core Philosophy](#1-core-philosophy)
2. [State Schema](#2-state-schema)
3. [Input/Output Schema](#3-inputoutput-schema)
4. [Graph Workflow](#4-graph-workflow)
5. [Node Implementations](#5-node-implementations)
6. [LLM Context Strategy](#6-llm-context-strategy)
7. [Prompt Templates](#7-prompt-templates)
8. [Helper Functions](#8-helper-functions)
9. [Main Entry Point](#9-main-entry-point)
10. [Example: First 5 Iterations](#10-example-first-5-iterations)

---

## **1. CORE PHILOSOPHY**

### **1.1 Investigation Philosophy: Novel Insights**

**Primary Goal**: Write articles that provide FRESH perspectives, not rehash existing coverage.

**What "Novel" Means**:
- **New connections**: "Entity A funds Entity B who appointed Entity C" (others missed this chain)
- **Overlooked facts**: Small details buried in documents that reveal larger patterns
- **Fresh perspectives**: "Everyone reports deaths, but no one asked why regulator ignored 3 prior warnings"
- **Anomaly detection**: "Company claims X but documents show Y" (contradictions others didn't catch)
- **Temporal patterns**: "Event Z happened exactly 6 months after funding Y" (timing others missed)

**Strategic Prompts Should Ask**:
- "What did other journalists miss?"
- "What's the connection no one has drawn?"
- "What should have happened but didn't?"
- "Who benefits from the current narrative?"
- "What's suspicious about the timing?"

### **1.2 Iteration Philosophy: Aggressive Efficiency**

**Secondary Goal**: Prove/disprove hypotheses in MINIMUM iterations.

**Efficiency Principles**:
1. **Targeted searches**: Each search must answer specific hypothesis question
2. **Multiple questions per search**: One article can answer 3-5 questions simultaneously
3. **Aggressive threshold**: If 3 questions answered with 80% confidence → mark hypothesis proven (don't over-verify)
4. **Parallel evidence**: Extract evidence for ALL hypotheses from each article (not just active one)
5. **Early discard**: If 2 searches find zero supporting evidence → mark hypothesis disproven (don't waste iterations)

**Anti-Patterns to Avoid**:
- ❌ Vague searches: "Tell me more about X" (generates fluff)
- ❌ Repetitive searches: Searching same topic from different angles without new insight
- ❌ Over-verification: Proving same fact 5 different ways
- ❌ Tangential exploration: Following interesting but irrelevant entities

**Prompts Should Push For**:
- "What's the ONE search that would prove/disprove this hypothesis?"
- "Can this article answer multiple questions simultaneously?"
- "Is there enough evidence to conclude now, or do we genuinely need more?"

---

## **2. STATE SCHEMA**

### **2.1 Complete State Definition**

```python
"""
state.py - Investigation State Schema
"""

from typing import TypedDict, List, Dict, Optional, Literal

class EntityQuestion(TypedDict):
    """Question about an entity"""
    q: str                          # Question text
    a: Optional[str]                # Answer (null = unanswered)

class Entity(TypedDict):
    """Entity in the investigation"""
    name: str                       # Entity name
    type: Literal["person", "organization", "location", "substance", "event"]
    importance: float               # 0-1: investigation_relevance × knowledge_gap
    investigated: bool              # Have we searched about this entity?
    role: str                       # One-sentence description
    questions_about: List[EntityQuestion]
    sources: List[str]              # URLs where entity mentioned

class HypothesisQuestion(TypedDict):
    """Question testing a hypothesis"""
    q: str                          # Question text
    a: Optional[str]                # Answer (null = unanswered)
    src: Optional[str]              # Source URL if answered

class Hypothesis(TypedDict):
    """Hypothesis being tested or proven"""
    id: str                         # h1, h2, h3...
    statement: str                  # Clear claim to test
    status: Literal["exploring", "proven", "disproven", "pending"]
    confidence: float               # 0-1
    importance: float               # 0-1
    questions: List[HypothesisQuestion]  # Questions to prove/disprove

class HypothesisSummary(TypedDict):
    """Compressed form of proven hypothesis"""
    id: str
    statement: str
    status: Literal["proven", "disproven"]
    confidence: float
    key_evidence: List[str]         # Bullet points

class Narrative(TypedDict):
    """Current investigation narrative"""
    last_updated: int               # Iteration when last updated
    updated_when: str               # What triggered update (e.g., "h1_proven")
    story: str                      # 3-4 sentence current story
    based_on_hypotheses: List[str]  # Which hypothesis IDs inform this
    key_findings: List[str]         # Bullet points

class Connection(TypedDict):
    """Relationship between entities (for graph viz)"""
    from_entity: str                # Entity name (using from_entity to avoid Python keyword)
    to: str                         # Entity name
    type: str                       # Type of relationship

class TimelineEvent(TypedDict):
    """Event on timeline"""
    date: str                       # YYYY-MM or YYYY-MM-DD
    event: str                      # What happened
    source: str                     # URL

class Cache(TypedDict):
    """Investigation cache"""
    seen_urls: List[str]            # Already processed URLs
    previous_queries: List[str]     # Already executed search queries
    documents_in_rag: int           # Count of docs in vector DB

class Costs(TypedDict):
    """Cost tracking"""
    tavily_searches: int
    free_extractions: int
    tavily_extractions: int
    llm_calls: int
    total_cost: float

class Meta(TypedDict):
    """Investigation metadata"""
    investigation_id: str
    query: str                      # Original investigation question
    iteration: int
    max_iterations: int
    overall_confidence: float       # 0-1
    phase: Literal["exploratory", "hypothesis_testing", "synthesis"]

class InvestigativeJournalistState(TypedDict):
    """Complete investigation state"""
    meta: Meta
    facts: List[str]                # Flat list of verified facts
    entities: List[Entity]
    hypotheses: List[Hypothesis]    # Active and pending hypotheses
    narrative: Narrative
    anomalies: List[str]            # Flat list of suspicious patterns
    connections: List[Connection]   # For graph visualization
    timeline: List[TimelineEvent]
    cache: Cache
    costs: Costs

class CompressedState(InvestigativeJournalistState):
    """State after compression"""
    entities_archived: List[Dict[str, str]]  # {"name": "...", "reason": "..."}
    _compressed: bool
    _compressed_at_iteration: int
```

### **2.2 State Design Principles**

1. **Flat structures where possible**: `facts` and `anomalies` are simple string lists
2. **Questions nested in owners**: Entity questions inside entities, hypothesis questions inside hypotheses
3. **No separate "findings"**: Proven hypotheses ARE the findings
4. **Importance = relevance × knowledge_gap**: LLM calculates both factors in one field
5. **Null = unanswered**: No boolean flags; if answer is null/empty → unanswered

---

## **3. INPUT/OUTPUT SCHEMA**

```python
"""
Input and output schemas
"""

class InvestigationInput(TypedDict):
    """Input to start or resume investigation"""
    query: str                          # Investigation question
    max_iterations: int                 # Maximum iterations (default: 50)
    investigation_id: Optional[str]     # For resuming (if None, new investigation)
    user_instruction: Optional[str]     # User directive (e.g., "query local rag")
    event_callback: Optional[callable]  # WebSocket callback for real-time updates

class InvestigationOutput(TypedDict):
    """Output from completed investigation"""
    investigation_id: str
    final_report: str                   # Markdown article
    state: InvestigativeJournalistState # Final state
    proven_hypotheses: List[HypothesisSummary]
    total_cost: float
    iterations_completed: int
```

---

## **4. GRAPH WORKFLOW**

### **4.1 Node Graph**

```
STRATEGIST
    ↓ (decides next action)
    ├─→ "search" → SEARCHER → EXTRACTOR → ANALYZER → back to STRATEGIST
    ├─→ "analyze_only" → ANALYZER → back to STRATEGIST
    ├─→ "compress" → COMPRESSOR → back to STRATEGIST
    └─→ "complete" → SYNTHESIZER → END
```

### **4.2 Implementation**

```python
"""
graph.py - LangGraph workflow definition
"""

from langgraph.graph import StateGraph, END

def build_investigation_graph():
    """
    Build investigation workflow
    
    Flow:
    STRATEGIST → [search/analyze/complete]
         ↓
    SEARCHER → EXTRACTOR → ANALYZER → STRATEGIST (loop)
         ↓
    SYNTHESIZER (final)
    """
    
    workflow = StateGraph(InvestigativeJournalistState)
    
    # Nodes
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("searcher", searcher_node)
    workflow.add_node("extractor", extractor_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("compressor", compressor_node)
    
    # Entry point
    workflow.set_entry_point("strategist")
    
    # Routing
    workflow.add_conditional_edges(
        "strategist",
        route_from_strategist,
        {
            "search": "searcher",
            "analyze_only": "analyzer",
            "compress": "compressor",
            "complete": "synthesizer"
        }
    )
    
    workflow.add_edge("searcher", "extractor")
    workflow.add_edge("extractor", "analyzer")
    workflow.add_edge("analyzer", "strategist")
    workflow.add_edge("compressor", "strategist")
    workflow.add_edge("synthesizer", END)
    
    return workflow.compile()


def route_from_strategist(state: InvestigativeJournalistState) -> str:
    """Determine next node based on strategist decision"""
    
    # Max iterations reached
    if state["meta"]["iteration"] >= state["meta"]["max_iterations"]:
        return "complete"
    
    # Compression needed
    if should_compress(state):
        return "compress"
    
    # Phase-based routing
    phase = state["meta"]["phase"]
    
    if phase == "exploratory":
        return "search"
    
    elif phase == "hypothesis_testing":
        # Check if we should skip search this iteration
        if not should_search_this_iteration(state):
            return "analyze_only"
        return "search"
    
    elif phase == "synthesis":
        return "complete"
    
    return "search"  # Default


def should_compress(state: InvestigativeJournalistState) -> bool:
    """Check if state compression needed"""
    iteration = state["meta"]["iteration"]
    token_estimate = estimate_tokens(state)
    
    return (
        token_estimate > 8000 or
        iteration % 20 == 0 and iteration > 0
    )


def should_search_this_iteration(state: InvestigativeJournalistState) -> bool:
    """Phase-based search frequency"""
    iteration = state["meta"]["iteration"]
    
    # Phase 1 (1-20): Every iteration
    if iteration <= 20:
        return True
    
    # Phase 2 (21-60): Every 2 iterations
    if iteration <= 60:
        return iteration % 2 == 1
    
    # Phase 3 (61+): Every 5 iterations
    return iteration % 5 == 1
```

---

## **5. NODE IMPLEMENTATIONS**

### **5.1 Strategist Node** (Decision Maker)

```python
"""
nodes/strategist.py
"""

async def strategist_node(state: InvestigativeJournalistState) -> Dict[str, Any]:
    """
    Decide what to investigate next
    
    Logic:
    1. If no hypotheses → exploratory phase (form hypotheses)
    2. If hypotheses exist → get active hypothesis
    3. Get next unanswered question from active hypothesis
    4. Generate search query to answer that question
    
    Returns:
        Updated state with:
        - next_action: "search" | "analyze_only" | "complete"
        - search_query: Query string (if action=search)
    """
    
    iteration = state["meta"]["iteration"]
    log(f"\n{'='*80}")
    log(f"🧠 STRATEGIST - Iteration {iteration}")
    log(f"{'='*80}")
    
    # Prepare context for LLM (filtered)
    llm_context = prepare_strategist_context(state)
    
    # Get active hypothesis
    active_hypothesis = get_active_hypothesis(state["hypotheses"])
    
    if not active_hypothesis:
        # No active hypothesis - check if exploratory or complete
        if len(state["hypotheses"]) == 0:
            phase = "exploratory"
        else:
            # All hypotheses tested
            phase = "complete"
    else:
        phase = "hypothesis_testing"
    
    # Build prompt based on phase
    if phase == "exploratory":
        prompt = build_exploratory_prompt(llm_context)
    elif phase == "hypothesis_testing":
        prompt = build_hypothesis_testing_prompt(llm_context, active_hypothesis)
    else:
        # All done
        return {**state, "meta": {**state["meta"], "phase": "synthesis"}}
    
    # Call LLM
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    decision = parse_json(response.content)
    
    # Validate and enhance decision
    decision = validate_strategist_decision(decision, state)
    
    return {
        **state,
        "meta": {
            **state["meta"],
            "iteration": iteration + 1,
            "phase": phase
        },
        "next_action": decision["action"],
        "search_query": decision.get("search_query")
    }


def prepare_strategist_context(state: InvestigativeJournalistState) -> Dict:
    """Filter state for strategist LLM call"""
    return {
        "meta": state["meta"],
        "facts": state["facts"],
        "entities": [e for e in state["entities"] if e["importance"] > 0.6][:10],
        "hypotheses": {
            "active": get_active_hypothesis(state["hypotheses"]),
            "proven": [summarize_hypothesis(h) for h in state["hypotheses"] if h["status"] == "proven"]
        },
        "narrative": {"story": state["narrative"]["story"]},
        "anomalies": state["anomalies"]
    }
```

### **5.2 Searcher Node** (Tavily Search)

```python
"""
nodes/searcher.py
"""

async def searcher_node(state: InvestigativeJournalistState) -> Dict[str, Any]:
    """
    Execute Tavily search
    
    Returns:
        Updated state with:
        - search_results: List of article metadata
        - cache.seen_urls: Updated with new URLs
    """
    
    query = state.get("search_query")
    log(f"\n🔍 SEARCHER: {query}")
    
    # Execute search (with caching)
    results = await tavily_client.search(
        query=query,
        max_results=5,
        search_depth="basic"
    )
    
    articles = results.get("results", [])
    
    # Filter new URLs
    new_articles = [
        a for a in articles
        if a["url"] not in state["cache"]["seen_urls"]
    ]
    
    log(f"   Found {len(articles)} articles, {len(new_articles)} new")
    
    return {
        **state,
        "search_results": new_articles,
        "cache": {
            **state["cache"],
            "seen_urls": state["cache"]["seen_urls"] + [a["url"] for a in new_articles],
            "previous_queries": state["cache"]["previous_queries"] + [query]
        },
        "costs": {
            **state["costs"],
            "tavily_searches": state["costs"]["tavily_searches"] + 1,
            "total_cost": state["costs"]["total_cost"] + 0.01
        }
    }
```

### **5.3 Extractor Node** (Content Extraction)

```python
"""
nodes/extractor.py
"""

async def extractor_node(state: InvestigativeJournalistState) -> Dict[str, Any]:
    """
    Extract content using free methods waterfall
    
    Methods (in order):
    1. Jina AI Reader (free, 60% success)
    2. Trafilatura (free, 40% success)
    3. BeautifulSoup (free, fallback)
    4. Tavily Extract (paid, last resort)
    
    Returns:
        Updated state with:
        - extracted_content: List[{url, content, method}]
    """
    
    articles = state.get("search_results", [])
    log(f"\n📖 EXTRACTOR: Processing {len(articles)} articles")
    
    extracted = []
    
    for i, article in enumerate(articles[:2], 1):  # Top 2 only
        url = article["url"]
        log(f"   [{i}] {url[:60]}...")
        
        # Try extraction waterfall
        content = await extract_with_waterfall(url, state)
        
        if content:
            extracted.append({
                "url": url,
                "content": content["text"],
                "method": content["method"]
            })
            
            # Update costs
            if content["method"] == "tavily":
                state["costs"]["tavily_extractions"] += 1
                state["costs"]["total_cost"] += 0.05
            else:
                state["costs"]["free_extractions"] += 1
    
    return {
        **state,
        "extracted_content": extracted
    }


async def extract_with_waterfall(url: str, state: InvestigativeJournalistState) -> Optional[Dict]:
    """Try extraction methods in order"""
    
    # Check file cache first
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache_file = Path(f"extraction_cache/{cache_key}.txt")
    
    if cache_file.exists():
        return {"text": cache_file.read_text(), "method": "cache"}
    
    # Method 1: Jina AI
    try:
        response = requests.get(f"https://r.jina.ai/{url}", timeout=15)
        if response.status_code == 200 and len(response.text) > 500:
            cache_file.write_text(response.text)
            return {"text": response.text, "method": "jina_ai"}
    except:
        pass
    
    # Method 2: Trafilatura
    try:
        response = requests.get(url, timeout=10)
        content = trafilatura.extract(response.content)
        if content and len(content) > 500:
            cache_file.write_text(content)
            return {"text": content, "method": "trafilatura"}
    except:
        pass
    
    # Method 3: BeautifulSoup
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator='\n', strip=True)
        if len(text) > 500:
            cache_file.write_text(text)
            return {"text": text, "method": "beautifulsoup"}
    except:
        pass
    
    # Method 4: Tavily Extract (paid)
    try:
        result = await tavily_client.extract(urls=[url])
        if result and result.get("results"):
            content = result["results"][0].get("raw_content", "")
            if len(content) > 500:
                cache_file.write_text(content)
                return {"text": content, "method": "tavily"}
    except:
        pass
    
    return None
```

### **5.4 Analyzer Node** (Extract Structured Data)

```python
"""
nodes/analyzer.py
"""

async def analyzer_node(state: InvestigativeJournalistState) -> Dict[str, Any]:
    """
    Extract entities, facts, answer questions from articles
    
    Returns:
        Updated state with:
        - entities: Updated with new entities and answered questions
        - facts: New facts added
        - hypotheses: Questions answered, confidence updated
        - anomalies: New anomalies added
        - connections: New connections added
    """
    
    extracted = state.get("extracted_content", [])
    log(f"\n🔬 ANALYZER: Analyzing {len(extracted)} articles")
    
    if not extracted:
        return state
    
    # Prepare context for analyzer
    llm_context = prepare_analyzer_context(state, extracted)
    
    # Build analyzer prompt
    prompt = build_analyzer_prompt(llm_context)
    
    # Call LLM
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    analysis = parse_json(response.content)
    
    # Merge analysis into state
    updated_state = merge_analysis(state, analysis)
    
    # Store in local RAG
    if state["meta"]["investigation_id"]:
        await store_in_local_rag(extracted, state)
        updated_state["cache"]["documents_in_rag"] += len(extracted)
    
    # Save to MongoDB (incremental)
    if state["meta"]["investigation_id"]:
        await save_to_mongodb(updated_state)
    
    return updated_state


def merge_analysis(state: InvestigativeJournalistState, analysis: Dict) -> InvestigativeJournalistState:
    """Merge analyzer output into state"""
    
    # Add new facts
    new_facts = state["facts"] + analysis.get("new_facts", [])
    
    # Merge new entities (avoid duplicates)
    entities = state["entities"].copy()
    for new_entity in analysis.get("new_entities", []):
        if not any(e["name"] == new_entity["name"] for e in entities):
            entities.append({
                **new_entity,
                "investigated": False,
                "sources": [analysis.get("source_url", "")]
            })
    
    # Answer questions in hypotheses
    hypotheses = state["hypotheses"].copy()
    for answered in analysis.get("answered_questions", []):
        for hyp in hypotheses:
            if hyp["id"] == answered["hypothesis_id"]:
                for q in hyp["questions"]:
                    if q["q"] == answered["question"]:
                        q["a"] = answered["answer"]
                        q["src"] = answered["source"]
                
                # Update hypothesis confidence
                hyp["confidence"] = calculate_hypothesis_confidence(hyp)
                
                # Update status if threshold reached
                if hyp["confidence"] >= 0.8:
                    hyp["status"] = "proven"
                    state["narrative"]["last_updated"] = state["meta"]["iteration"]
                    state["narrative"]["updated_when"] = f"{hyp['id']}_proven"
                elif hyp["confidence"] <= 0.3:
                    hyp["status"] = "disproven"
    
    # Add connections, anomalies
    connections = state["connections"] + analysis.get("new_connections", [])
    anomalies = state["anomalies"] + analysis.get("new_anomalies", [])
    
    return {
        **state,
        "facts": new_facts,
        "entities": entities,
        "hypotheses": hypotheses,
        "connections": connections,
        "anomalies": anomalies
    }
```

### **5.5 Synthesizer Node** (Final Report)

```python
"""
nodes/synthesizer.py
"""

async def synthesizer_node(state: InvestigativeJournalistState) -> Dict[str, Any]:
    """
    Generate final investigative report
    
    Returns:
        Updated state with:
        - final_report: Markdown article
    """
    
    log(f"\n📝 SYNTHESIZER: Generating final report")
    
    # Prepare full context
    llm_context = prepare_synthesizer_context(state)
    
    # Build synthesis prompt
    prompt = build_synthesis_prompt(llm_context)
    
    # Call LLM
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    report = response.content
    
    # Append sources
    sources = list(set(state["cache"]["seen_urls"]))
    report += "\n\n---\n\n## **SOURCES**\n\n"
    for i, url in enumerate(sources, 1):
        report += f"{i}. {url}\n"
    
    return {
        **state,
        "final_report": report,
        "meta": {
            **state["meta"],
            "phase": "complete"
        }
    }
```

### **5.6 Compressor Node** (State Reduction)

```python
"""
nodes/compressor.py
"""

async def compressor_node(state: InvestigativeJournalistState) -> CompressedState:
    """
    Compress state to reduce token usage
    
    Strategy:
    - Merge related facts
    - Summarize proven hypotheses
    - Archive low-importance entities
    - Remove answered questions from proven hypotheses
    
    Returns:
        Compressed state
    """
    
    log(f"\n🗜️  COMPRESSOR: Reducing state size")
    
    prompt = f"""
Compress this investigation state to reduce token usage while preserving critical information.

CURRENT STATE:
{json.dumps(state, indent=2)}

COMPRESSION RULES:
1. FACTS: Merge related facts into comprehensive statements
2. PROVEN HYPOTHESES: Convert to summary form (remove detailed questions)
3. ENTITIES: Archive entities with importance < 0.6 that haven't been mentioned in 5+ iterations
4. PRESERVE: All exploring/pending hypotheses fully

Return compressed state in same JSON format.
"""
    
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    compressed = parse_json(response.content)
    
    compressed["_compressed"] = True
    compressed["_compressed_at_iteration"] = state["meta"]["iteration"]
    
    log(f"   Compressed: {estimate_tokens(state)} → {estimate_tokens(compressed)} tokens")
    
    return compressed
```

---

## **6. LLM CONTEXT STRATEGY**

### **6.1 What Gets Sent to Each Node**

| Field | Strategist | Analyzer | Synthesizer | Compressor |
|-------|-----------|----------|-------------|------------|
| **meta** | ✅ Partial | ✅ Query only | ✅ Full | ✅ Full |
| **facts** | ✅ All | ⚠️ Last 10 | ✅ All | ✅ All |
| **entities** | ⚠️ Top 10 | ⚠️ Names only | ✅ All | ✅ All |
| **hypotheses (active)** | ✅ Full | ✅ Full | ❌ No | ✅ Full |
| **hypotheses (proven)** | ⚠️ Summary | ❌ No | ✅ Full | ✅ Full |
| **narrative** | ✅ Story only | ❌ No | ✅ Full | ✅ Full |
| **anomalies** | ✅ All | ❌ No | ✅ All | ✅ All |
| **connections** | ❌ No | ❌ No | ✅ All | ✅ All |
| **timeline** | ❌ No | ❌ No | ✅ All | ✅ All |
| **cache** | ❌ No | ❌ No | ❌ No | ✅ Full |
| **costs** | ❌ No | ❌ No | ❌ No | ✅ Full |

**Legend**:
- ✅ = Sent fully
- ⚠️ = Sent with filters/truncation
- ❌ = Not sent

### **6.2 Token Budgets**

```python
MAX_TOKENS_PER_NODE = {
    "strategist": 3500,      # Decide next action
    "analyzer": 5000,        # Extract from articles (articles are large)
    "synthesizer": 8000,     # Write full report (needs everything)
    "compressor": 10000      # Process entire state
}
```

---

## **7. PROMPT TEMPLATES**

### **7.1 Strategist Prompt (Hypothesis Testing)**

```python
def build_hypothesis_testing_prompt(context: Dict, active_hyp: Hypothesis) -> str:
    """
    PHILOSOPHY:
    - Aggressively pursue novel insights
    - Minimize iterations via targeted searches
    - Push for connections others missed
    """
    
    # Get next unanswered question
    unanswered = [q for q in active_hyp["questions"] if not q.get("a")]
    
    if not unanswered:
        # All questions answered - evaluate hypothesis
        return f"""
All questions for hypothesis "{active_hyp['statement']}" have been answered.

QUESTIONS & ANSWERS:
{json.dumps(active_hyp["questions"], indent=2)}

Based on these answers, should this hypothesis be:
1. PROVEN (confidence >= 0.8)
2. DISPROVEN (confidence <= 0.3)
3. NEEDS MORE QUESTIONS (add new questions to test further)

⚠️  BE AGGRESSIVE: If 3+ questions answered with clear evidence, mark proven/disproven.
Don't waste iterations over-verifying.

Return JSON:
{{
  "action": "mark_proven" | "mark_disproven" | "add_questions",
  "new_confidence": 0.0-1.0,
  "new_questions": [...] (if adding questions),
  "reasoning": "Why you made this decision"
}}
"""
    
    next_question = unanswered[0]
    
    return f"""
You are an investigative strategist seeking NOVEL insights that others missed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR MISSION: Find what other journalists MISSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HYPOTHESIS: {active_hyp['statement']}
CURRENT CONFIDENCE: {active_hyp['confidence']}
NEXT QUESTION: "{next_question['q']}"

INVESTIGATION CONTEXT:
{json.dumps(context, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL THINKING FRAMEWORKS (Use These!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **The Dog That Didn't Bark**: What SHOULD have happened but didn't?
2. **Cui Bono**: Who benefits from the current narrative?
3. **Follow the Money**: Financial flows, donations, contracts
4. **Power Networks**: Who appointed whom? Conflicts of interest?
5. **Temporal Anomalies**: Why NOW? What changed 6 months ago?
6. **Comparative Baseline**: How does this compare to similar cases?
7. **Hidden Connections**: Entity A → Entity B → Entity C (multi-hop)
8. **Contradictions**: Official story vs documents vs timing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TASK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate ONE surgical search query that will:
1. Answer the next question with SPECIFIC evidence
2. Potentially answer MULTIPLE other questions simultaneously
3. Reveal connections or patterns others overlooked
4. Use targeted keywords (not vague exploratory searches)

⚠️  EFFICIENCY MANDATE:
- If this article can answer 3+ questions → extract ALL answers (not just one)
- If 2 searches found ZERO evidence → hypothesis likely disproven (don't waste more iterations)
- Be SPECIFIC: "Company X inspection records 2022" NOT "tell me about Company X"

ENTITY IMPORTANCE GUIDANCE:
When assigning/updating entity importance, consider:
- **Investigation relevance**: How central to answering main query? (0-1)
- **Knowledge gap**: How much do we NOT know? (WHO=0.3, obscure company=0.95)
- **Formula**: importance = relevance × knowledge_gap

Return JSON:
{{
  "action": "search",
  "search_query": "Specific keywords for Tavily (not questions, not vague)",
  "novel_angle": "What overlooked connection/fact are you seeking?",
  "expected_evidence": "What would prove/disprove the hypothesis?",
  "multiple_questions_answerable": ["q1", "q2", ...] (if this search could answer multiple questions)
}}

🔥 REMEMBER: Your job is to find what others MISSED, not rehash existing coverage!
"""
```

### **7.2 Analyzer Prompt**

```python
def build_analyzer_prompt(context: Dict) -> str:
    """
    PHILOSOPHY:
    - Extract evidence for ALL hypotheses (not just active)
    - Find novel connections (multi-hop, timing, contradictions)
    - Be aggressive: If article answers question, mark it answered (don't require perfect certainty)
    """
    
    return f"""
You are an investigative analyst extracting structured information from articles.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR MISSION: Extract NOVEL insights, not obvious facts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARTICLES TO ANALYZE:
{context["articles_text"]}

ACTIVE HYPOTHESIS (focus here):
{json.dumps(context["active_hypothesis"], indent=2)}

ALL HYPOTHESES (extract evidence for these too if found):
{json.dumps(context["all_hypotheses"], indent=2)}

EXISTING ENTITIES (for matching):
{context["entity_names"]}

RECENT FACTS (avoid duplication):
{json.dumps(context["recent_facts"], indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT TO EXTRACT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **NEW FACTS** (only if NOVEL or OBSCURE):
   ✅ Specific numbers, dates, names (not generic statements)
   ✅ Buried details others would miss
   ❌ Obvious/widely-known information

2. **NEW ENTITIES** (only if IMPORTANT):
   - Assign importance = investigation_relevance × knowledge_gap
   - WHO = low importance (0.5), obscure company = high (0.95)
   - Include questions_about for context gaps

3. **ANSWER HYPOTHESIS QUESTIONS** (AGGRESSIVE):
   - If article provides ANY evidence → answer the question (don't require 100% certainty)
   - Answer for ALL hypotheses (not just active one)
   - Be specific: Quote exact evidence from article

4. **NEW CONNECTIONS** (CRITICAL):
   - Multi-hop: A funds B who appointed C
   - Timing: Event X happened 6 months after funding Y
   - Contradictions: Entity claims X but did Y
   - Hidden patterns: Multiple entities connected to same funder

5. **ANOMALIES**:
   - What's suspicious? What doesn't add up?
   - What SHOULD have happened but didn't?
   - Contradictions between claims and evidence

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return JSON:
{{
  "new_facts": ["Specific fact with numbers/names/dates", ...],
  
  "new_entities": [
    {{
      "name": "Entity name",
      "type": "person|organization|location|substance|event",
      "importance": 0.0-1.0,
      "role": "One sentence description",
      "questions_about": [{{"q": "What we don't know?", "a": null}}]
    }}
  ],
  
  "answered_questions": [
    {{
      "hypothesis_id": "h2",
      "question": "Did CDSCO inspect?",
      "answer": "No inspections conducted in 2022 (specific evidence from article)",
      "source": "article_url",
      "supports_hypothesis": true | false
    }}
  ],
  
  "new_connections": [
    {{"from": "Entity A", "to": "Entity B", "type": "funds|appointed|owns|regulates|..."}}
  ],
  
  "new_anomalies": [
    "CONTRADICTION: Entity X claims Y but documents show Z",
    "TIMING ANOMALY: Event happened exactly 6 months after funding",
    ...
  ]
}}

🔥 REMEMBER: Find what others MISSED - buried facts, hidden connections, suspicious patterns!
⚡ BE AGGRESSIVE: If article answers question (even partially), mark it answered!
"""
```

### **7.3 Synthesizer Prompt**

```python
def build_synthesis_prompt(context: Dict) -> str:
    """
    PHILOSOPHY:
    - Lead with novel insights (not obvious facts)
    - Structure: What we found that others missed
    - Professional journalism tone
    """
    
    return f"""
Write a professional investigative journalism report.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR MISSION: Write article with FRESH perspective
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INVESTIGATION: {context["query"]}
ITERATIONS: {context["iterations"]}
CONFIDENCE: {context["confidence"]}

PROVEN FINDINGS (These are your KEY FINDINGS):
{json.dumps(context["proven_hypotheses"], indent=2)}

ALL FACTS:
{json.dumps(context["facts"], indent=2)}

ENTITIES & CONNECTIONS:
{json.dumps(context["entities"], indent=2)}
{json.dumps(context["connections"], indent=2)}

ANOMALIES (Unanswered questions):
{json.dumps(context["anomalies"], indent=2)}

TIMELINE:
{json.dumps(context["timeline"], indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARTICLE STRUCTURE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## **HEADLINE**
[Compelling, specific headline highlighting NOVEL angle]

---

## **EXECUTIVE SUMMARY**
[2-3 paragraphs: Lead with what others MISSED. What's the fresh angle? Then context.]

---

## **KEY FINDINGS**

[List proven hypotheses as findings. LEAD with novel insights:]

1. **[Novel Finding That Others Missed]**: Specific evidence with names, numbers, dates
2. **[Connection Others Didn't Draw]**: Multi-hop relationship or timing anomaly
3. **[Obvious Finding]**: Important but widely reported (can include but not first)

---

## **ANALYSIS & INSIGHTS**

### **What This Investigation Uncovered**
[What did we find that other journalists missed?]

### **Hidden Connections**
[Network of actors: Who's connected to whom? Multi-hop relationships]

### **Suspicious Patterns**
[Anomalies, timing coincidences, contradictions]

### **Timeline Analysis**
[What does the sequence of events reveal?]

---

## **UNANSWERED QUESTIONS**

[Critical questions that remain unresolved]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WRITING GUIDELINES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ DO:
- Lead with NOVEL insights (not obvious facts everyone knows)
- Use specific evidence (names, numbers, dates, quotes)
- Highlight connections others missed
- Professional investigative journalism tone
- Factual, evidence-based

❌ DON'T:
- Rehash what other outlets already reported
- Lead with obvious facts
- Be vague or speculative without evidence
- Editorialize or make unsupported claims

🔥 REMEMBER: This article should make readers say "I didn't know that!" not "I've heard this before."

Write the complete report now.
"""
```

---

## **8. HELPER FUNCTIONS**

```python
"""
utils.py - Helper functions
"""

def get_active_hypothesis(hypotheses: List[Hypothesis]) -> Optional[Hypothesis]:
    """Get hypothesis with status='exploring'"""
    for hyp in hypotheses:
        if hyp["status"] == "exploring":
            return hyp
    
    # No exploring - activate next pending
    for hyp in hypotheses:
        if hyp["status"] == "pending":
            hyp["status"] = "exploring"
            return hyp
    
    return None


def calculate_hypothesis_confidence(hypothesis: Hypothesis) -> float:
    """
    Calculate confidence based on answered questions
    
    AGGRESSIVE: If 80% of questions answered with supporting evidence → 0.8 confidence
    """
    questions = hypothesis["questions"]
    if not questions:
        return 0.5
    
    answered = [q for q in questions if q.get("a")]
    if not answered:
        return hypothesis["confidence"]  # Keep current
    
    # Count supporting answers
    supporting = sum(
        1 for q in answered 
        if q.get("a") and "no" not in q["a"].lower()[:20]
    )
    
    # Simple ratio
    confidence = supporting / len(questions)
    
    return min(1.0, max(0.0, confidence))


def estimate_tokens(state: Dict) -> int:
    """Rough token estimate (1 token ≈ 4 chars)"""
    return len(json.dumps(state)) // 4


def parse_json(content: str) -> Dict:
    """Parse JSON from LLM response"""
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return json.loads(content.strip())
    except:
        return {}


def summarize_hypothesis(hypothesis: Hypothesis) -> HypothesisSummary:
    """Convert proven hypothesis to summary (for context reduction)"""
    evidence = [
        q["a"] for q in hypothesis["questions"]
        if q.get("a")
    ]
    
    return {
        "id": hypothesis["id"],
        "statement": f"PROVEN: {hypothesis['statement']}",
        "status": hypothesis["status"],
        "confidence": hypothesis["confidence"],
        "key_evidence": evidence[:3]  # Top 3
    }


def create_initial_state(
    query: str, 
    max_iterations: int, 
    investigation_id: str
) -> InvestigativeJournalistState:
    """Create fresh investigation state"""
    return {
        "meta": {
            "investigation_id": investigation_id,
            "query": query,
            "iteration": 0,
            "max_iterations": max_iterations,
            "overall_confidence": 0.0,
            "phase": "exploratory"
        },
        "facts": [],
        "entities": [],
        "hypotheses": [],
        "narrative": {
            "last_updated": 0,
            "updated_when": "",
            "story": "",
            "based_on_hypotheses": [],
            "key_findings": []
        },
        "anomalies": [],
        "connections": [],
        "timeline": [],
        "cache": {
            "seen_urls": [],
            "previous_queries": [],
            "documents_in_rag": 0
        },
        "costs": {
            "tavily_searches": 0,
            "free_extractions": 0,
            "tavily_extractions": 0,
            "llm_calls": 0,
            "total_cost": 0.0
        }
    }
```

---

## **9. MAIN ENTRY POINT**

```python
"""
main.py - Entry point for investigations
"""

async def investigate(
    query: str,
    max_iterations: int = 50,
    investigation_id: Optional[str] = None,
    user_instruction: Optional[str] = None,
    event_callback: Optional[callable] = None
) -> InvestigationOutput:
    """
    Run investigation
    
    Args:
        query: Investigation question
        max_iterations: Max iterations (default: 50)
        investigation_id: Resume ID (None = new)
        user_instruction: User directive
        event_callback: WebSocket callback for real-time updates
    
    Returns:
        InvestigationOutput with report and state
    """
    
    log(f"\n{'#'*80}")
    log(f"🔬 INVESTIGATIVE JOURNALIST V2")
    log(f"{'#'*80}")
    log(f"Query: {query}")
    log(f"Max Iterations: {max_iterations}")
    log(f"{'#'*80}\n")
    
    # Load or create state
    if investigation_id:
        log(f"   ✅ Resuming investigation: {investigation_id}")
        state = await load_from_mongodb(investigation_id)
        state["meta"]["max_iterations"] = max_iterations  # Update if changed
    else:
        investigation_id = f"inv_{uuid.uuid4().hex[:12]}"
        log(f"   🆕 Starting new investigation: {investigation_id}")
        state = create_initial_state(query, max_iterations, investigation_id)
    
    # Build graph
    graph = build_investigation_graph()
    
    # Run investigation
    try:
        final_state = await graph.ainvoke(
            state,
            config={
                "recursion_limit": max_iterations * 5,
                "event_callback": event_callback
            }
        )
    except Exception as e:
        log(f"\n❌ Investigation failed: {e}")
        raise
    
    # Extract proven hypotheses
    proven = [
        summarize_hypothesis(h)
        for h in final_state["hypotheses"]
        if h["status"] == "proven"
    ]
    
    log(f"\n{'#'*80}")
    log(f"✅ INVESTIGATION COMPLETE")
    log(f"{'#'*80}")
    log(f"Iterations: {final_state['meta']['iteration']}")
    log(f"Proven Hypotheses: {len(proven)}")
    log(f"Total Facts: {len(final_state['facts'])}")
    log(f"Total Entities: {len(final_state['entities'])}")
    log(f"Total Cost: ${final_state['costs']['total_cost']:.3f}")
    log(f"{'#'*80}\n")
    
    return {
        "investigation_id": investigation_id,
        "final_report": final_state.get("final_report", ""),
        "state": final_state,
        "proven_hypotheses": proven,
        "total_cost": final_state["costs"]["total_cost"],
        "iterations_completed": final_state["meta"]["iteration"]
    }


# CLI testing
if __name__ == "__main__":
    async def main():
        query = input("Investigation query: ").strip()
        if not query:
            query = "Why did cough syrup deaths occur in India and Gambia 2022?"
        
        max_iter = input("Max iterations (default 50): ").strip()
        max_iter = int(max_iter) if max_iter.isdigit() else 50
        
        result = await investigate(query, max_iterations=max_iter)
        
        print("\n" + "="*80)
        print("FINAL REPORT:")
        print("="*80)
        print(result["final_report"])
    
    asyncio.run(main())
```

---

## **10. EXAMPLE: FIRST 5 ITERATIONS**

See detailed walkthrough of state evolution in separate section of this document showing:
- Iteration 0: Empty state
- Iteration 1: Exploratory search, form initial hypotheses
- Iteration 2-3: Test hypothesis h1 (contamination cause)
- Iteration 4-5: Switch to h2 (regulatory failure)
- Compression example after iteration 3

---

## **IMPLEMENTATION CHECKLIST**

### **Phase 1: Core Infrastructure**
- [ ] `state.py`: Define all TypedDict schemas
- [ ] `graph.py`: Build LangGraph workflow
- [ ] `utils.py`: Helper functions

### **Phase 2: Nodes**
- [ ] `nodes/strategist.py`: Decision making
- [ ] `nodes/searcher.py`: Tavily search
- [ ] `nodes/extractor.py`: Content extraction waterfall
- [ ] `nodes/analyzer.py`: Structured extraction
- [ ] `nodes/synthesizer.py`: Final report
- [ ] `nodes/compressor.py`: State compression

### **Phase 3: Prompts**
- [ ] Exploratory prompt (form hypotheses)
- [ ] Hypothesis testing prompt (novel insights focus)
- [ ] Analyzer prompt (aggressive extraction)
- [ ] Synthesis prompt (fresh perspective)
- [ ] Compression prompt

### **Phase 4: Integration**
- [ ] MongoDB persistence (incremental saves)
- [ ] Local RAG storage (vector DB)
- [ ] WebSocket events (real-time updates)
- [ ] Cost tracking

### **Phase 5: Testing**
- [ ] Test: Exploratory phase (iteration 1)
- [ ] Test: Hypothesis testing (iterations 2-10)
- [ ] Test: State compression (iteration 20)
- [ ] Test: Full 50-iteration investigation
- [ ] Test: Resume capability

---

## **COST ESTIMATES**

| Component | Per Iteration | 50 Iterations |
|-----------|--------------|---------------|
| Strategist LLM | $0.009 | $0.45 |
| Analyzer LLM | $0.018 | $0.90 |
| Tavily Search | $0.010 | $0.50 |
| Free Extraction | $0.000 | $0.00 |
| **TOTAL** | **~$0.037** | **~$1.85** |

With compression every 20 iterations: +$0.15
**Grand Total: ~$2.00 per 50-iteration investigation**

---

## **KEY DESIGN DECISIONS SUMMARY**

1. **Hypothesis-driven**: Investigation organized around hypotheses, not entities
2. **Questions nested**: Questions live inside hypotheses/entities (clear ownership)
3. **Proven = findings**: No separate findings structure
4. **Flat where possible**: Facts and anomalies are simple string lists
5. **Null = unanswered**: No boolean flags; absence indicates unanswered
6. **Aggressive efficiency**: Prove/disprove in minimum iterations
7. **Novel focus**: Prompts push for connections/facts others missed
8. **Context filtering**: Each node gets only what it needs
9. **Compression on demand**: LLM-driven state reduction like Cursor
10. **Cost optimized**: Free extraction waterfall, phase-based search frequency

---

**END OF IMPLEMENTATION GUIDE**

