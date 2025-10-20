"""
Lean Investigator Agent
Optimized for 100+ iterations at minimal cost

Cost-saving strategies:
1. Tavily search only (no extract)
2. Free text extraction using Python libraries
3. Hypothesis-driven searching (not every iteration)
4. Smart caching
5. Incremental search frequency
6. Multi-tool investigation (Wayback Machine, OCCRP Aleph)
"""

import asyncio
import sys
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, TypedDict
from pathlib import Path

import httpx  # ⚡ OPTIMIZATION: Async HTTP client with connection pooling
from bs4 import BeautifulSoup
import trafilatura

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END

# Import from same directory
import os
import sys
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Add shared directory to path for cached Tavily client
shared_dir = Path(__file__).parent.parent.parent.parent / 'shared'
if str(shared_dir) not in sys.path:
    sys.path.insert(0, str(shared_dir))

# Import investigative tools
from tools.wayback_tool import WaybackMachineTool
from tools.aleph_tool import AlephTool

from tavily_tools import TavilyTools
from tavily_client import TavilyClient  # Cached client


def log(message: str):
    """Print with flush for real-time logging"""
    print(message)
    sys.stdout.flush()


class HypothesisState(TypedDict):
    """State for hypothesis-driven investigation"""
    initial_query: str
    iteration: int
    max_iterations: int
    investigation_id: Optional[str]  # For incremental MongoDB saves
    user_instruction: Optional[str]  # User's follow-up question (highest priority)
    
    # Knowledge base
    entities: Dict[str, Any]  # People, orgs, locations
    facts: List[str]  # Simple facts list
    hypotheses: List[Dict[str, Any]]  # Competing explanations
    evidence: List[Dict[str, Any]]  # Evidence supporting/refuting hypotheses
    connections: List[Dict[str, Any]]  # Entity relationships
    anomalies: List[str]  # Unusual patterns/absences
    questions: List[Dict[str, Any]]  # Question tree for UI visualization
    
    # Cache and efficiency
    seen_urls: List[str]
    extracted_cache: Dict[str, str]  # URL -> content cache
    previous_queries: List[str]  # Track all queries to avoid repetition
    
    # Working variables (passed between nodes)
    search_results: List[Dict[str, Any]]  # ⭐ CRITICAL: Results from searcher
    extracted_content: List[Dict[str, Any]]  # ⭐ CRITICAL: Content from extractor
    
    # Control
    next_action: str
    search_query: Optional[str]
    rag_query: Optional[str]  # For local RAG queries
    target_url: Optional[str]  # For wayback_machine tool
    wayback_reasoning: Optional[str]  # Reasoning for wayback check
    aleph_query: Optional[str]  # For aleph_search tool
    aleph_reasoning: Optional[str]  # Reasoning for aleph search
    investigation_complete: bool
    final_report: Optional[str]


class LeanInvestigator:
    """
    Cost-optimized investigator for deep, hypothesis-driven analysis
    """
    
    # Cost constants (approximate)
    COST_TAVILY_SEARCH = 0.01  # $0.01 per search
    COST_TAVILY_EXTRACT = 0.05  # $0.05 per extract
    COST_GPT4O_INPUT = 0.0025  # $2.50 per 1M tokens (~1000 tokens per call)
    COST_GPT4O_OUTPUT = 0.01  # $10 per 1M tokens (~500 tokens per call)
    
    # Content size limits
    MAX_CONTENT_CHARS = 50000  # 50K chars per article (~12,500 tokens)
    MAX_TOTAL_CONTENT_CHARS = 150000  # 150K chars total (~37,500 tokens)
    WARN_CONTENT_CHARS = 100000  # Warn if single article > 100K
    
    def __init__(self, max_iterations: int = 100):
        self.max_iterations = max_iterations
        # Use gpt-4o-2024-08-06 or later for prompt caching support
        self.llm = ChatOpenAI(
            model="gpt-4o-2024-08-06",  # Supports prompt caching
            temperature=0,
            model_kwargs={"store": True}  # Enable prompt caching
        )
        # Use TavilyClient with caching instead of TavilyTools
        self.tavily = TavilyClient(enable_caching=True)
        self.tavily_tools = TavilyTools()  # Keep for compatibility
        self.cache_dir = Path("extraction_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # ⚡ PERFORMANCE OPTIMIZATION: HTTP connection pooling (2-3x faster)
        # Reuses TCP connections, eliminates repeated SSL handshakes
        self.http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=100,  # Max concurrent connections
                max_keepalive_connections=20  # Keep 20 connections alive for reuse
            ),
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        
        # Initialize investigative tools
        self.wayback = WaybackMachineTool()
        self.aleph = AlephTool()
        
        # Cost tracking
        self.costs = {
            "tavily_searches": 0,
            "tavily_extracts": 0,
            "free_extracts": 0,
            "cached_extracts": 0,
            "wayback_checks": 0,
            "aleph_searches": 0,
            "llm_calls": 0,
            "total_cost": 0.0
        }
        
        # Build graph (MongoDB saves handled separately in analyzer_node)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the investigation graph (state saved to MongoDB in nodes)"""
        workflow = StateGraph(HypothesisState)
        
        # Nodes
        workflow.add_node("strategist", self._strategist_node)
        workflow.add_node("searcher", self._searcher_node)
        workflow.add_node("extractor", self._extractor_node)
        workflow.add_node("local_rag_query", self._local_rag_query_node)
        workflow.add_node("analyzer", self._analyzer_node)
        workflow.add_node("synthesizer", self._synthesizer_node)
        
        # Edges
        workflow.set_entry_point("strategist")
        workflow.add_conditional_edges(
            "strategist",
            self._route_from_strategist,
            {
                "search": "searcher",
                "query_local_rag": "local_rag_query",
                "analyze": "analyzer",
                "complete": "synthesizer"
            }
        )
        workflow.add_edge("searcher", "extractor")
        workflow.add_edge("extractor", "analyzer")
        workflow.add_edge("local_rag_query", "analyzer")  # LOCAL RAG goes directly to analyzer
        workflow.add_conditional_edges(
            "analyzer",
            self._route_from_analyzer,
            {
                "continue": "strategist",
                "complete": "synthesizer"
            }
        )
        workflow.add_edge("synthesizer", END)
        
        # Compile without checkpointer (we use MongoDB directly)
        return workflow.compile()
    
    def _route_from_analyzer(self, state: HypothesisState) -> str:
        """
        Route after analyzer completes
        Check if we've exceeded max_iterations or investigation is complete
        """
        current_iteration = state["iteration"]
        max_iterations = state["max_iterations"]
        
        # Check if investigation is complete
        if state.get("investigation_complete"):
            log(f"   🛑 Investigation marked complete by strategist")
            return "complete"
        
        # 🐛 FIX: Check if we've completed all iterations
        # After iteration N completes (analyzer runs), check if N >= max_iterations
        if current_iteration >= max_iterations:
            log(f"   🛑 Max iterations reached ({current_iteration}/{max_iterations}) - completing investigation")
            return "complete"
        
        # Continue to next iteration
        log(f"   ↻ Continuing to next iteration ({current_iteration + 1}/{max_iterations})")
        return "continue"
    
    def _route_from_strategist(self, state: HypothesisState) -> str:
        """Route based on strategy decision"""
        # 🐛 FIX: Check iteration BEFORE incrementing (strategist increments it)
        # If strategist just ran iteration 5 and incremented to 6, we should still execute the action
        current_iteration = state["iteration"] - 1  # Strategist already incremented
        
        if current_iteration > state["max_iterations"]:
            log(f"   🛑 Max iterations exceeded ({current_iteration}/{state['max_iterations']})")
            return "complete"
        if state.get("investigation_complete"):
            log(f"   🛑 Investigation marked complete")
            return "complete"
        
        action = state.get("next_action", "search")
        
        # Handle analyze_only (skip search)
        if action == "analyze_only":
            return "analyze"
        
        # Handle LOCAL RAG query
        if action == "query_local_rag":
            log(f"   🔀 Router: query_local_rag → local_rag_query node")
            return "query_local_rag"
        
        # Handle Wayback Machine
        if action == "wayback_machine":
            log(f"   🔀 Router: wayback_machine → searcher node (wayback mode)")
            return "search"
        
        # Handle Aleph search
        if action == "aleph_search":
            log(f"   🔀 Router: aleph_search → searcher node (aleph mode)")
            return "search"
        
        # Default: regular Tavily search
        log(f"   🔀 Router: {action} → searcher node (tavily mode)")
        return "search"
    
    def _build_hypothesis_context(self, state: HypothesisState, active_hypothesis: Dict) -> str:
        """Build concise hypothesis testing summary for strategist to avoid loops"""
        if not active_hypothesis:
            return ""
        
        # Get questions for this hypothesis
        hyp_id = active_hypothesis.get("id")
        hyp_questions = [q for q in state.get("questions", []) if q.get("hypothesis_id") == hyp_id]
        
        # Count patterns
        answered = [q for q in hyp_questions if q.get("answer")]
        weak_answers = [q for q in answered if any(
            phrase in q.get("answer", "").lower() 
            for phrase in ["do not", "does not", "no evidence", "no specific", "no direct", "not provide", "not available"]
        )]
        
        # Build last 3 Q&A pairs
        recent_qa = []
        for i, q in enumerate(answered[-3:] if answered else hyp_questions[-3:]):
            qa_text = f"  Q{i+1} (iter {q.get('iteration', '?')}): {q.get('question', '')[:70]}..."
            if q.get("answer"):
                qa_text += f"\n  A{i+1}: {q.get('answer', '')[:100]}..."
            else:
                qa_text += "\n  A{i+1}: NOT ANSWERED"
            recent_qa.append(qa_text)
        
        # Build warning flags
        warnings = []
        if len(weak_answers) >= 2:
            warnings.append(f"  🔴 {len(weak_answers)}/3+ weak/negative answers - HYPOTHESIS MAY BE EXHAUSTED")
        if len(hyp_questions) >= 3:
            warnings.append(f"  🔴 {len(hyp_questions)}/3+ questions asked - AVOID REPEATING SAME ANGLE")
        if len(hyp_questions) > 0 and len(answered) < len(hyp_questions) * 0.5:
            warnings.append(f"  🟡 Only {len(answered)}/{len(hyp_questions)} questions answered - Consider different tool/approach")
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 HYPOTHESIS TESTING PROGRESS (ID: {hyp_id})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Statement: {active_hypothesis.get('statement', 'N/A')[:120]}
Status: {active_hypothesis.get('status')} | Confidence: {active_hypothesis.get('confidence', 0.5):.2f}
Questions: {len(hyp_questions)} total, {len(answered)} answered, {len(weak_answers)} weak/negative

Last 3 Q&A:
{chr(10).join(recent_qa) if recent_qa else "  No questions yet"}

⚠️  EXHAUSTION SIGNALS:
{chr(10).join(warnings) if warnings else "  ✅ No exhaustion signals detected"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    async def _strategist_node(self, state: HypothesisState) -> HypothesisState:
        """
        Strategic decision maker - decides what to investigate next
        Uses hypothesis-driven approach
        
        WORKFLOW:
        1. Initial iterations: General investigation to form hypotheses
        2. Once hypotheses exist: Test them one by one
        3. When a hypothesis is complete: Move to next hypothesis
        4. When all hypotheses tested: Complete investigation
        """
        iteration = state["iteration"]
        
        log(f"\n{'='*80}")
        log(f"🧠 STRATEGIST - Iteration {iteration}/{state['max_iterations']}")
        log(f"{'='*80}")
        
        # Emit professional iteration start event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('thinking', {
                    "status": f"Starting iteration {iteration} of {state['max_iterations']}",
                    "phase": state.get('phase', 'exploration'),
                    "progress": iteration / state['max_iterations'],
                    "details": f"Analyzing hypothesis: {state.get('current_hypothesis_id', 'N/A')}"
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Initialize questions list
        questions = state.get("questions", [])
        hypotheses = state.get("hypotheses", [])
        
        # 🚨 PRIORITY: Handle user follow-up instruction (if present)
        user_instruction = state.get('user_instruction')
        if user_instruction:
            log(f"\n{'🚨'*40}")
            log(f"🔥 USER FOLLOW-UP DETECTED (HIGHEST PRIORITY)")
            log(f"   Question: {user_instruction}")
            log(f"{'🚨'*40}\n")
            
            # Check if we already created a hypothesis for this user instruction
            user_hyp_exists = any(
                h.get('statement', '').lower() == user_instruction.lower() or
                (h.get('priority') == 0 and h.get('status') == 'exploring')
                for h in hypotheses
            )
            
            if not user_hyp_exists:
                # Create new hypothesis with HIGHEST priority
                user_hyp_id = f"h_user_{len(hypotheses) + 1}"
                user_hypothesis = {
                    "id": user_hyp_id,
                    "statement": f"Investigating user's question: {user_instruction}",
                    "status": "exploring",
                    "confidence": 0.5,
                    "priority": 0,  # HIGHEST PRIORITY!
                    "evidence": [],
                    "questions": [],
                    "user_driven": True  # Flag to identify user-created hypotheses
                }
                hypotheses.append(user_hypothesis)
                log(f"   ✅ Created HIGH-PRIORITY hypothesis: {user_hyp_id}")
                log(f"   📝 Statement: {user_hypothesis['statement']}")
                
                # Emit event
                if hasattr(self, 'event_callback') and self.event_callback:
                    try:
                        await self.event_callback('hypothesis_updated', user_hypothesis)
                    except Exception as e:
                        log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Determine current phase
        if len(hypotheses) == 0:
            phase = "general_investigation"
            log("   📍 PHASE: General Investigation (no hypotheses yet)")
        else:
            # Find active hypothesis - PRIORITIZE by priority field (0 = highest)
            exploring_hypotheses = [h for h in hypotheses if h.get("status") == "exploring"]
            
            if exploring_hypotheses:
                # Sort by priority (lower number = higher priority)
                active_hypothesis = min(exploring_hypotheses, key=lambda h: h.get("priority", 10))
                phase = "testing_hypothesis"
                log(f"   📍 PHASE: Testing Hypothesis {active_hypothesis.get('id')}")
                log(f"   📝 Hypothesis: {active_hypothesis.get('statement', 'N/A')}")
                log(f"   🎯 Confidence: {active_hypothesis.get('confidence', 0.0):.2f}")
                log(f"   ⚡ Priority: {active_hypothesis.get('priority', 10)} {'(USER-DRIVEN!)' if active_hypothesis.get('priority') == 0 else ''}")
            else:
                # All hypotheses are confirmed/refuted, should we generate new ones or complete?
                completed_count = sum(1 for h in hypotheses if h.get("status") in ["confirmed", "refuted"])
                iterations_remaining = state["max_iterations"] - iteration
                
                # Generate new hypotheses if we have at least 2 iterations left AND haven't explored enough
                should_generate_new = (
                    completed_count == len(hypotheses) and 
                    iterations_remaining >= 2 and
                    (len(hypotheses) < 3 or iteration < state["max_iterations"] * 0.7)  # More aggressive threshold
                )
                
                if should_generate_new:
                    phase = "generate_new_hypotheses"
                    log(f"   📍 PHASE: All {len(hypotheses)} hypotheses tested, generating new ones ({iterations_remaining} iterations left)")
                else:
                    phase = "complete"
                    log(f"   📍 PHASE: Investigation Complete ({completed_count}/{len(hypotheses)} hypotheses tested, {iterations_remaining} iterations remaining)")
        
        # Determine search frequency based on phase
        should_search = self._should_search_this_iteration(iteration, state)
        
        if not should_search:
            log("   ⏭️  Skipping search this iteration - analyzing existing data")
            return {
                **state,
                "next_action": "analyze_only",
                "iteration": iteration + 1
            }
        
        # Get current date
        now = datetime.now(timezone.utc)
        current_date = now.strftime("%B %d, %Y")
        
        # Build phase-specific context
        if phase == "general_investigation":
            # Extract key topic words to enforce in search query
            query_lower = state['initial_query'].lower()
            core_topics = []
            if 'death' in query_lower or 'deaths' in query_lower:
                core_topics.append("deaths")
            if 'cough syrup' in query_lower or 'syrup' in query_lower:
                core_topics.append("cough syrup")
            if 'india' in query_lower:
                core_topics.append("India")
            
            phase_instruction = f"""
**CURRENT PHASE: GENERAL INVESTIGATION (ITERATION 1)**

🚨 MANDATORY REQUIREMENT FOR YOUR FIRST SEARCH:
Your search query MUST contain these exact terms from the user's question: {', '.join(core_topics) if core_topics else 'the main topic'}

The user asked about: "{state['initial_query']}"

Your search query MUST directly investigate THIS event/topic.
❌ DO NOT search for: regulations, background, industry overview, compliance
✅ DO search for: the actual event, what happened, who was involved, when it occurred

Example:
- User asks: "Investigate India Cough Syrup Deaths"
- ✅ CORRECT: "India cough syrup deaths 2024 2025 incidents victims"
- ❌ WRONG: "India pharmaceutical regulations" or "medical device compliance"

Generate your search_query now. It MUST include: {', '.join(core_topics) if core_topics else 'the core topic words'}
"""
        elif phase == "testing_hypothesis":
            # Get active hypothesis based on priority (already selected above at line 258)
            active_hyp = min(
                [h for h in hypotheses if h.get("status") == "exploring"],
                key=lambda h: h.get("priority", 10),
                default=None
            )
            
            # Check if this is a user-driven hypothesis (priority=0)
            is_user_driven = active_hyp and active_hyp.get("priority") == 0
            
            phase_instruction = f"""
**CURRENT PHASE: TESTING HYPOTHESIS**
Active Hypothesis: {active_hyp.get('statement', 'N/A') if active_hyp else 'N/A'} (ID: {active_hyp.get('id', 'N/A') if active_hyp else 'N/A'})
Current Confidence: {(active_hyp.get('confidence', 0.0) if active_hyp else 0.0):.2f}
{'🚨 PRIORITY: USER-DRIVEN QUESTION - Answer this FIRST!' if is_user_driven else ''}
Your goal: Generate a SPECIFIC question to test this hypothesis with evidence.
Focus on: Finding evidence that could CONFIRM or REFUTE this specific hypothesis.
"""
        elif phase == "generate_new_hypotheses":
            phase_instruction = """
**CURRENT PHASE: GENERATING NEW HYPOTHESES**
All current hypotheses have been tested. Based on what you've learned, formulate NEW hypotheses to explore.
Your goal: Search for information that could lead to new hypothesis generation.
"""
        else:  # complete
            phase_instruction = """
**CURRENT PHASE: INVESTIGATION COMPLETE**
All hypotheses have been sufficiently tested. Time to synthesize findings.
"""
        
        # Check if LOCAL RAG is available (iteration 2+)
        documents_in_rag = state.get('documents_in_rag', 0)
        has_local_rag = iteration >= 2 and documents_in_rag > 0
        
        # Check if user explicitly asked to query LOCAL RAG
        user_instruction = state.get('user_instruction')  # Keep as None if not present
        force_local_rag = user_instruction and ('local' in user_instruction.lower() or 'knowledge base' in user_instruction.lower())
        
        # DEBUG: Log what we received
        log(f"\n{'─'*80}")
        log(f"💾 LOCAL RAG STATUS:")
        log(f"   Documents in RAG: {documents_in_rag}")
        log(f"   Has LOCAL RAG: {has_local_rag} (iteration >= 2 and docs > 0)")
        log(f"   User instruction: {user_instruction[:80] if user_instruction else 'None'}...")
        log(f"   🐛 DEBUG - user_instruction type: {type(user_instruction)}, bool: {bool(user_instruction)}")
        log(f"   Force LOCAL RAG: {force_local_rag}")
        if force_local_rag:
            log(f"   🎯 USER EXPLICITLY ASKED TO QUERY LOCAL RAG!")
        log(f"{'─'*80}\n")
        
        # Add LOCAL RAG context if available
        local_rag_context = ""
        if has_local_rag or force_local_rag:
            local_rag_context = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 LOCAL KNOWLEDGE BASE AVAILABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You have accumulated {documents_in_rag} documents in your LOCAL knowledge base from previous iterations.

{f'🎯 USER REQUEST: "{user_instruction}"' if force_local_rag else ''}
{f'⚠️  YOU MUST query_local_rag this iteration to answer the user request!' if force_local_rag else ''}

✨ NEW OPTION AVAILABLE: "query_local_rag"

You can now choose to:
1. **query_local_rag**: Search your accumulated knowledge (FAST, NO COST, revisit past findings)
   - Use when: Reviewing what you've already learned, cross-referencing entities, checking for contradictions
   - Example: "What companies have we identified?" or "What did we learn about regulatory failures?"
   - {f'USE THIS NOW - User explicitly asked!' if force_local_rag else 'Consider this before searching web'}
   
2. **search**: Use Tavily for fresh web content (COSTS MONEY, finds new information)
   - Use when: Need new information not in local knowledge base
   
3. **complete**: End investigation

💡 TIP: Often it's smart to query LOCAL RAG first to understand what you already know, 
then decide if you need fresh information from Tavily.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Add specialized investigative tools context
        tools_context = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 SPECIALIZED INVESTIGATIVE TOOLS AVAILABLE (Use Strategically)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You have access to specialized tools beyond basic web search. Each offers unique value:

1. **tavily_search** - Current web search (news, articles, reports)
   ✅ Use when: Looking for recent news, breaking information, media coverage
   📊 Returns: News articles, press releases, public statements
   💰 Cost: $0.01 per search
   🎯 Default choice for most investigations
   
2. **local_rag_query** - Query your accumulated knowledge
   ✅ Use when: Synthesizing findings, cross-referencing entities, checking contradictions
   📊 Returns: Information from YOUR previous iterations
   💰 Cost: FREE
   🎯 HIGHLY RECOMMENDED every 2-3 iterations to consolidate learning{f" (AVAILABLE NOW - {documents_in_rag} documents)" if has_local_rag else " (will be available from iteration 2+)"}
   💡 Smart pattern: Tavily → Tavily → local_rag_query → Tavily (synthesize periodically)
   ⚠️  Most useful when you have 5+ documents (currently: {documents_in_rag})
   
3. **wayback_machine** - Historical website comparison (⚠️ USE SPARINGLY)
   ✅ Use when: SPECIFIC evidence from news articles suggests content was deleted/modified
   ✅ Good for: Government/company websites that may have removed statements
   ❌ DON'T use if:
      - Just curious (need actual evidence of cover-up)
      - No news reports mention deleted content
      - Already checked this URL before
      - First 2-3 iterations (wait for evidence first)
   📊 Returns: Website version comparison, change detection
   💰 Cost: FREE (but low value without justification)
   ⚠️  Check tool_history - NEVER check the same URL twice!
   💡 EVIDENCE NEEDED: Before using, you must cite WHY you suspect deletion
   
4. **aleph_search** - Leaked documents & sanctions (⚠️ USE SPARINGLY)
   ✅ Use when: Need specific entity details NOT in news (ownership, directors, sanctions)
   ✅ Good for: SPECIFIC company names (e.g., "Maiden Pharmaceuticals"), not concepts
   ❌ DON'T use if:
      - Searching for concepts/topics (e.g., "transparency" "accountability")
      - Basic news search hasn't been tried yet
      - Already searched this entity
      - Entity is well-known (WHO, FDA, etc.)
   📊 Returns: Company registries, sanctions lists, leaked documents
   💰 Cost: FREE (but often returns no results)
   ⚠️  Check tool_history - NEVER search the same entity twice!
   💡 BE SPECIFIC: Use exact company/person names, not broad queries

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 RECOMMENDED INVESTIGATION PATTERNS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **GOOD PATTERN** (Tool Diversity):
   Iter 1: tavily_search → Find initial facts
   Iter 2: tavily_search → Deeper investigation
   Iter 3: local_rag_query → "What have we learned? Any gaps?" (SYNTHESIZE)
   Iter 4: wayback_machine → Check government website (IF cover-up suspected)
   Iter 5: tavily_search → Follow up on new leads
   Iter 6: local_rag_query → Final synthesis

❌ **BAD PATTERN** (Tool Repetition):
   Iter 1: tavily_search → Same topic
   Iter 2: tavily_search → Same topic again
   Iter 3: tavily_search → Still same topic ← STUCK IN LOOP!
   Iter 4: tavily_search → No new information ← WASTING RESOURCES!

💡 **USE LOCAL_RAG_QUERY REGULARLY**:
   - After every 2-3 Tavily searches
   - Before using specialized tools (check what you know first)
   - When feeling stuck (synthesize before changing approach)
   - Before completion (ensure nothing missed)

🎯 **DEFAULT TOOL SELECTION LOGIC**:
   - Start with tavily_search (80% of time)
   - Use local_rag_query every 2-3 iterations (15% of time)
   - Use wayback/aleph only when unique value (5% of time)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        strategy_prompt = f"""You are an investigative strategist finding NOVEL angles others miss.

INVESTIGATION: {state['initial_query']}
ITERATION: {iteration}/{state['max_iterations']}
CURRENT DATE: {current_date}

{phase_instruction}

{"━"*80}
{"🎯 USER FOLLOW-UP QUESTION (HIGHEST PRIORITY!)" if user_instruction and not force_local_rag else ""}
{"━"*80}
{f'''
The user has asked a NEW question that you MUST address:

    "{user_instruction}"

YOUR IMMEDIATE TASK:
1. Create a NEW hypothesis specifically to answer this question
2. Generate a search query targeting this question
3. DO NOT synthesize until you've gathered evidence to answer this
4. This takes precedence over existing hypotheses

Example Response:
{{
  "decision": "search",
  "hypothesis_id": "h_user_followup",
  "question": "{user_instruction}",
  "novel_angle": "Investigating the user's specific concern about...",
  "hypothesis": "Based on the user's question, we hypothesize that...",
  "search_query": "specific keywords to answer: {user_instruction[:30]}..."
}}
''' if user_instruction and not force_local_rag else ""}
{"━"*80 if user_instruction and not force_local_rag else ""}

KNOWLEDGE GATHERED SO FAR:
- Entities identified: {len(state['entities'])}
- Facts collected: {len(state['facts'])}
- Hypotheses: {len(state['hypotheses'])}
- Connections mapped: {len(state['connections'])}
- Anomalies found: {len(state['anomalies'])}
{f"- Documents in LOCAL RAG: {documents_in_rag}" if has_local_rag else ""}

{self._build_hypothesis_context(state, active_hypothesis)}

EXISTING HYPOTHESES:
{json.dumps(state['hypotheses'], indent=2)}

RECENT FACTS (Last 5):
{json.dumps(state['facts'][-5:], indent=2)}

KEY ANOMALIES (Top 5):
{json.dumps(state['anomalies'][-5:], indent=2)}

PREVIOUS SEARCH QUERIES (MUST NOT REPEAT):
{json.dumps(state.get('previous_queries', []), indent=2)}

PREVIOUS TOOL USAGE (AVOID REPEATING):
{json.dumps(state.get('tool_history', []), indent=2) if state.get('tool_history') else "[]"}

🚨 CRITICAL: Do NOT repeat the same tool + query combination!
- If you already used wayback_machine on a URL, don't check it again
- If you already searched a company in aleph_search, don't search it again
- Only repeat if you have a DIFFERENT query or angle

{local_rag_context}
{tools_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR MISSION: Find what others missed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 MANDATORY ANTI-LOOP RULES (Check HYPOTHESIS TESTING PROGRESS above):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **IF YOU SEE 🔴 RED FLAGS ABOVE → YOU MUST PIVOT**
   - 2+ weak/negative answers? → Lower confidence to 0.25-0.35 OR try different tool
   - 3+ questions on same hypothesis? → STOP asking similar questions
   - Pattern of "does not"/"no evidence"? → Evidence doesn't exist, move on

2. **NEVER REPEAT THE SAME QUESTION TYPE 3+ TIMES**
   - Check "Last 3 Q&A" above - if they're all similar and all negative → STOP
   - Your query MUST be COMPLETELY DIFFERENT from previous queries
   - If stuck in loop → Use query_local_rag, wayback_machine, or aleph_search

3. **CHANGE APPROACH AFTER 2 FAILED SEARCHES:**
   - 1st search: No evidence → OK, try different angle
   - 2nd search: Still no evidence → Last chance, different keywords
   - 3rd search: Still no evidence → MANDATORY PIVOT:
     ✅ Use query_local_rag (synthesize what we know)
     ✅ Use different tool (wayback/aleph if justified)
     ✅ Lower confidence to < 0.3 (refute hypothesis)
     ✅ Generate alternative hypothesis
     ❌ DO NOT search again with slight rewording

4. **ARTICLE DEDUPLICATION:**
   - We already seen {len(state.get('seen_urls', []))} URLs
   - If search returns 0 new articles → same sources being found
   - This is a STRONG signal to change approach or query angle

5. **IF NO NEW INFORMATION → SYNTHESIZE OR PIVOT:**
   - If last search found 0-1 new articles → Topic exhausted
   - Use query_local_rag to consolidate findings
   - OR mark hypothesis as inconclusive and move on

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ IF YOU'RE IN A LOOP: You'll see the same patterns in "Last 3 Q&A" + many seen_urls
   → STOP and either: refute hypothesis, query local_rag, or generate new hypothesis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLE OF WHAT NOT TO DO:
❌ Iteration 3: "financial pressures to use cheaper chemicals"
❌ Iteration 4: "financial pressures to use cheaper chemicals" ← REPEAT!
❌ Iteration 5: "financial pressures to use cheaper chemicals" ← REPEAT AGAIN!

EXAMPLE OF WHAT TO DO:
✅ Iteration 3: "financial pressures" (tavily) → No clear answer
✅ Iteration 4: "check CDSCO for deleted alerts" (wayback_machine) → Different approach
✅ Iteration 5: "Sresan Pharmaceuticals ownership" (aleph_search) → Different angle

ADDITIONAL CRITICAL THINKING FRAMEWORKS:

1. **The Dog That Didn't Bark**: What SHOULD have happened but didn't?
2. **Temporal Anomalies**: Why NOW? What changed 6 months ago?
3. **Comparative Baseline**: How does this compare to similar cases?
4. **Power Networks**: Who appointed whom? Conflicts of interest?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your task:
1. Review existing knowledge and hypotheses
2. Identify which hypothesis needs testing
3. Formulate a specific QUESTION to test that hypothesis
4. **CHOOSE THE RIGHT TOOL** for the investigation need
5. Explain what NOVEL insight you're seeking

🎯 TOOL SELECTION LOGIC:
- Company/person background → aleph_search
- Government/company website → wayback_machine (check for cover-ups)
- Recent news/events → tavily_search
- Synthesize knowledge → local_rag_query{" (available now)" if has_local_rag else ""}

Return JSON (include ALL relevant fields based on your decision):

IMPORTANT: Based on your "decision" value, you MUST include the corresponding query field:
- If decision="tavily_search" → MUST include "search_query"
- If decision="wayback_machine" → MUST include "target_url"
- If decision="aleph_search" → MUST include "aleph_query"
- If decision="query_local_rag" → MUST include "rag_query"

{{
  "decision": "{'"tavily_search" OR "wayback_machine" OR "aleph_search"' if not has_local_rag else '"tavily_search" OR "wayback_machine" OR "aleph_search" OR "query_local_rag"'} OR "complete"",
  "hypothesis_id": "ID of hypothesis being tested",
  "question": "Specific question you're trying to answer",
  "hypothesis_being_tested": "Which hypothesis are you testing?",
  "novel_angle": "What new insight are you seeking?",
  "expected_evidence": "What would prove/disprove your hypothesis?",
  "tool_reasoning": "Why did you choose this specific tool?",
  
  "search_query": "REQUIRED IF decision='tavily_search': keywords like 'India cough syrup deaths 2024'",
  "target_url": "REQUIRED IF decision='wayback_machine': COMPLETE URL like 'https://cdsco.gov.in'",
  "aleph_query": "REQUIRED IF decision='aleph_search': entity name like 'Maiden Pharmaceuticals'",
  "rag_query": "REQUIRED IF decision='query_local_rag': question like 'What have we learned?'",
  "completion_reason": "REQUIRED IF decision='complete': Why investigation is complete"
}}

🚨 CRITICAL: If you choose wayback_machine, you MUST provide a complete target_url!
🚨 CRITICAL: If you choose aleph_search, you MUST provide aleph_query!
🚨 CRITICAL: If you choose tavily_search, you MUST provide search_query!

💡 EXAMPLES:
- Testing company background → {{"decision": "aleph_search", "aleph_query": "Maiden Pharmaceuticals", "hypothesis_id": "h1", "question": "Who owns Maiden Pharma?", ...}}
- Checking government response → {{"decision": "wayback_machine", "target_url": "https://cdsco.gov.in", "hypothesis_id": "h2", "question": "Did CDSCO delete alerts?", ...}}
- Finding recent news → {{"decision": "tavily_search", "search_query": "India cough syrup deaths latest", "hypothesis_id": "h1", "question": "What's the latest?", ...}}
"""
        # Add RAG example if available
        if has_local_rag:
            strategy_prompt += '- Synthesizing knowledge → {{"decision": "query_local_rag", "rag_query": "What companies have we identified?", "hypothesis_id": "general", "question": "What do we know?", ...}}\n'
        
        strategy_prompt += """
⚠️  NOTICE: Each example includes BOTH the tool-specific field (target_url/aleph_query/search_query) AND the common fields!

Be specific. Be surgical. Use the RIGHT TOOL for the job. Find what others missed.
"""
        
        response = await self.llm.ainvoke([SystemMessage(content=strategy_prompt)])
        decision = self._parse_json(response.content)
        
        # 🆕 VALIDATE REQUIRED FIELDS based on decision type
        decision_type = decision.get('decision', 'N/A')
        validation_errors = []
        
        if decision_type == 'tavily_search':
            if not decision.get('search_query'):
                validation_errors.append("Missing 'search_query' for tavily_search")
        elif decision_type == 'wayback_machine':
            if not decision.get('target_url'):
                validation_errors.append("Missing 'target_url' for wayback_machine")
        elif decision_type == 'aleph_search':
            if not decision.get('aleph_query'):
                validation_errors.append("Missing 'aleph_query' for aleph_search")
        elif decision_type == 'query_local_rag':
            if not decision.get('rag_query'):
                validation_errors.append("Missing 'rag_query' for query_local_rag")
        
        if validation_errors:
            log(f"\n{'🚨'*40}")
            log(f"❌ LLM VALIDATION ERRORS:")
            for error in validation_errors:
                log(f"   - {error}")
            log(f"   Raw LLM response: {response.content[:500]}...")
            log(f"{'🚨'*40}\n")
        
        # 🆕 LOG RAW LLM DECISION for debugging
        log(f"\n{'─'*80}")
        log(f"🤖 LLM STRATEGIST DECISION (RAW):")
        log(f"{'─'*80}")
        log(f"   Decision Type: {decision.get('decision', 'N/A')}")
        log(f"   Hypothesis ID: {decision.get('hypothesis_id', 'N/A')}")
        log(f"   Question: {decision.get('question', 'N/A')[:100]}...")
        if decision.get('decision') == 'complete':
            log(f"   🛑 COMPLETION REASON: {decision.get('completion_reason', 'Not provided')}")
        if decision.get('decision') == 'query_local_rag':
            log(f"   📖 RAG Query: {decision.get('rag_query', 'N/A')[:100]}...")
        if decision.get('decision') in ['search', 'tavily_search']:
            log(f"   🔍 Tavily Search Query: {decision.get('search_query', 'N/A')[:100]}...")
        if decision.get('decision') == 'wayback_machine':
            log(f"   ⏰ Wayback Machine URL: {decision.get('target_url', 'N/A')}")
        if decision.get('decision') == 'aleph_search':
            log(f"   🗂️  Aleph Query: {decision.get('aleph_query', 'N/A')}")
        log(f"   💡 Novel Angle: {decision.get('novel_angle', 'N/A')[:150]}...")
        log(f"   🎯 Expected Evidence: {decision.get('expected_evidence', 'N/A')[:150]}...")
        if decision.get('tool_reasoning'):
            log(f"   🔧 Tool Reasoning: {decision.get('tool_reasoning', 'N/A')[:150]}...")
        log(f"{'─'*80}\n")
        
        # 🆕 EMIT DECISION TO UI via WebSocket
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                decision_summary = {
                    "decision_type": decision.get('decision', 'N/A'),
                    "hypothesis_id": decision.get('hypothesis_id', 'N/A'),
                    "question": decision.get('question', 'N/A'),
                    "novel_angle": decision.get('novel_angle', 'N/A'),
                    "expected_evidence": decision.get('expected_evidence', 'N/A'),
                    "iteration": iteration,
                    "phase": phase
                }
                
                if decision.get('decision') == 'complete':
                    decision_summary["completion_reason"] = decision.get('completion_reason', 'Not provided')
                if decision.get('decision') == 'query_local_rag':
                    decision_summary["rag_query"] = decision.get('rag_query', 'N/A')
                if decision.get('decision') == 'search':
                    decision_summary["search_query"] = decision.get('search_query', 'N/A')
                
                await self.event_callback('strategist_decision', decision_summary)
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Track LLM cost
        self.costs["llm_calls"] += 1
        self.costs["total_cost"] += (self.COST_GPT4O_INPUT + self.COST_GPT4O_OUTPUT)
        
        # ⭐ CRITICAL FIX: FORCE INITIAL SEARCH
        searches_done = len(state.get("previous_queries", []))
        if searches_done == 0:
            log("   🔒 OVERRIDE: FORCING INITIAL SEARCH (no searches yet)")
            decision["decision"] = "search"
            if not decision.get("search_query"):
                decision["search_query"] = state["initial_query"]
        
        # ⭐ CRITICAL FIX: PREVENT PREMATURE COMPLETION
        if decision.get("decision") == "complete":
            entities = len(state.get("entities", {}))
            facts = len(state.get("facts", []))
            if entities < 5 or facts < 10:
                log(f"   ⚠️  OVERRIDE: Rejecting premature completion (entities={entities}, facts={facts})")
                log(f"   🔄 Forcing continued investigation")
                decision["decision"] = "search"
                # Generate a fallback query
                if not decision.get("search_query"):
                    decision["search_query"] = f"{state['initial_query']} detailed investigation"
            else:
                log(f"   ✅ ACCEPTING completion (entities={entities}, facts={facts} - thresholds met)")
                log(f"   📝 LLM's reasoning: {decision.get('completion_reason', 'Not provided')}")
        
        # Validate query uniqueness
        new_query = decision.get("search_query", "")
        previous_queries = state.get("previous_queries", [])
        
        if new_query and self._is_query_similar(new_query, previous_queries):
            log(f"\n⚠️  WARNING: Query too similar to previous queries!")
            log(f"   Rejected: {new_query}")
            # Force a different query with entity-specific search
            entities = list(state['entities'].keys())[:5]
            if entities:
                new_query = f"{state['initial_query']} {entities[iteration % len(entities)]}"
                log(f"   Using entity-specific: {new_query}")
            else:
                # Use iteration number to force diversity
                angles = [
                    "financial connections",
                    "political donations",
                    "regulatory oversight",
                    "supply chain",
                    "previous violations",
                    "competitor analysis",
                    "victim statements",
                    "timeline analysis"
                ]
                new_query = f"{state['initial_query']} {angles[iteration % len(angles)]}"
                log(f"   Using angle-specific: {new_query}")
        
        # 🆕 PROGRAMMATIC LOOP DETECTION
        recent_queries = previous_queries[-3:] if len(previous_queries) >= 3 else previous_queries
        if len(recent_queries) >= 2:  # Need at least 2 previous + 1 current
            # Check if queries are repetitive
            query_words = [set(q.lower().split()) for q in recent_queries + [new_query]]
            
            # Calculate average similarity
            similarities = []
            for i in range(len(query_words) - 1):
                for j in range(i + 1, len(query_words)):
                    if len(query_words[i]) > 0 and len(query_words[j]) > 0:
                        overlap = len(query_words[i].intersection(query_words[j]))
                        similarity = overlap / min(len(query_words[i]), len(query_words[j]))
                        similarities.append(similarity)
            
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
            
            if avg_similarity > 0.65:  # 65% similar across recent queries
                log(f"\n{'🚨'*40}")
                log(f"🔴 QUERY LOOP DETECTED!")
                log(f"   Average similarity: {avg_similarity:.1%}")
                log(f"   Recent queries showing repetition")
                log(f"   🔧 Breaking loop with tool diversity")
                log(f"{'🚨'*40}\n")
                
                # Emit to UI
                if hasattr(self, 'event_callback') and self.event_callback:
                    try:
                        await self.event_callback('warning', {
                            "message": "🔄 Repetitive queries detected - synthesizing knowledge",
                            "details": f"Using accumulated knowledge to find new angles",
                            "severity": "info"
                        })
                    except Exception as e:
                        pass
                
                # PREFERRED: Use local_rag_query to synthesize and find new angles
                # BUT ONLY if we have enough content to synthesize (5+ documents)
                documents_in_rag = state.get('documents_in_rag', 0)
                
                if has_local_rag and documents_in_rag >= 5:
                    log(f"   ✅ PREFERRED: Switching to local_rag_query to synthesize")
                    log(f"      (RAG has {documents_in_rag} documents - sufficient for synthesis)")
                    return {
                        **state,
                        "next_action": "query_local_rag",
                        "rag_query": "What have we learned so far? What gaps remain in our investigation? What angles haven't we explored?",
                        "questions": questions,
                        "iteration": iteration + 1
                    }
                elif has_local_rag and documents_in_rag > 0:
                    log(f"   ℹ️  RAG available but only {documents_in_rag} documents (< 5)")
                    log(f"      Not enough content to synthesize meaningfully")
                    log(f"      Trying specialized tools instead")
                
                # ALTERNATIVE: Try specialized tools if RAG not available
                tool_history = state.get("tool_history", [])
                tools_used = set(t.get("tool") for t in tool_history)
                
                if "wayback_machine" not in tools_used and "CDSCO" in str(state.get("entities", {})):
                    log(f"   ✅ ALTERNATIVE: Switching to wayback_machine")
                    return {
                        **state,
                        "next_action": "wayback_machine",
                        "target_url": "https://cdsco.gov.in",
                        "wayback_reasoning": "Breaking query loop - checking regulatory website for changes",
                        "questions": questions,
                        "iteration": iteration + 1
                    }
                elif "aleph_search" not in tools_used:
                    entities = state.get("entities", {})
                    companies = [name for name, ent in entities.items() if ent.get("type") == "company"]
                    if companies:
                        log(f"   ✅ ALTERNATIVE: Switching to aleph_search")
                        return {
                            **state,
                            "next_action": "aleph_search",
                            "aleph_query": companies[0],
                            "aleph_reasoning": "Breaking query loop - investigating corporate background",
                            "questions": questions,
                            "iteration": iteration + 1
                        }
                
                # LAST RESORT: Force a very different Tavily angle
                log(f"   ⚠️  No specialized tools available, forcing different angle")
                new_query = f"{state['initial_query']} alternative perspective {iteration}"
        
        log(f"\n📋 STRATEGY:")
        log(f"   Decision: {decision.get('decision', 'N/A')}")
        
        # Highlight if LOCAL RAG was chosen
        if decision.get('decision') == 'query_local_rag':
            log(f"   ✅ CHOSE LOCAL RAG QUERY! (User instruction was followed)")
        elif force_local_rag and decision.get('decision') == 'search':
            log(f"   ⚠️  WARNING: User asked for LOCAL RAG but LLM chose Tavily search!")
        
        log(f"   Hypothesis ID: {decision.get('hypothesis_id', 'general')}")
        log(f"   Question: {decision.get('question', 'N/A')}")
        log(f"   Novel angle: {decision.get('novel_angle', 'N/A')}")
        log(f"   Hypothesis: {decision.get('hypothesis_being_tested', 'N/A')}")
        if decision.get('decision') == 'query_local_rag':
            log(f"   RAG Query: {decision.get('rag_query', decision.get('search_query', 'N/A'))}")
        else:
            log(f"   Query: {decision.get('search_query', 'N/A')}")
        
        # Track new question if formulated
        # 🐛 FIX: Track questions for ALL action types (not just "search")
        # Previously only tracked when decision == "search", but LLM returns "tavily_search", "wayback_machine", etc.
        decision_type = decision.get("decision", "")
        is_investigation_action = decision_type in ["search", "tavily_search", "wayback_machine", "aleph_search", "query_local_rag"]
        
        if decision.get("question") and is_investigation_action:
            question_text = decision["question"]
            hypothesis_id = decision.get("hypothesis_id", "general")
            
            log(f"   🐛 DEBUG - Tracking question for decision_type: {decision_type}")
            
            # Create unique question ID using counter
            existing_count = len([q for q in questions if q.get("hypothesis_id") == hypothesis_id])
            question_id = f"{hypothesis_id}_q{existing_count + 1}"
            
            # Check if this exact question already exists (avoid duplicates)
            question_exists = any(
                q.get("question", "").strip().lower() == question_text.strip().lower()
                for q in questions
            )
            
            if not question_exists:
                new_question = {
                    "id": question_id,
                    "hypothesis_id": hypothesis_id,  # Link to hypothesis
                    "question": question_text,
                    "status": "exploring",
                    "answer": None,
                    "iteration": iteration
                }
                questions.append(new_question)
                log(f"   📝 Question added to {hypothesis_id}: {question_text}")
                
                # Push to WebSocket in real-time if callback provided
                if hasattr(self, 'event_callback') and self.event_callback:
                    try:
                        await self.event_callback('question_discovered', new_question)
                    except Exception as e:
                        log(f"   ⚠️  WebSocket push failed: {e}")
            else:
                log(f"   ⏭️  Question already exists, skipping: {question_text[:60]}...")
        else:
            # Log why question was NOT tracked (for debugging)
            if not decision.get("question"):
                log(f"   ⚠️  No question provided by strategist (decision_type: {decision_type})")
            elif not is_investigation_action:
                log(f"   ⚠️  Question NOT tracked - decision_type '{decision_type}' is not an investigation action")
            else:
                log(f"   ⚠️  Question NOT tracked - unknown reason (has_question: {bool(decision.get('question'))}, is_investigation: {is_investigation_action})")
        
        # Handle completion based on phase
        if phase == "complete" or decision.get("decision") == "complete":
            log("   ✅ Investigation complete - moving to synthesis")
            return {
                **state,
                "investigation_complete": True,
                "questions": questions,
                "iteration": iteration + 1
            }
        
        # Update previous queries
        updated_queries = state.get("previous_queries", []) + [new_query]
        
        # Normalize decision type for backwards compatibility
        action_type = decision.get("decision", "search")
        if action_type == "search":
            action_type = "tavily_search"  # Normalize old "search" to "tavily_search"
        
        # 🎯 SUMMARY LOG: Question tracking status at end of strategist
        log(f"\n{'─'*80}")
        log(f"📊 STRATEGIST SUMMARY (Iteration {iteration}):")
        log(f"   Total questions tracked: {len(questions)}")
        log(f"   Questions this iteration: {1 if decision.get('question') and is_investigation_action else 0}")
        log(f"   Active hypotheses: {len([h for h in hypotheses if h.get('status') == 'exploring'])}")
        log(f"   Decision: {action_type}")
        if decision.get('question'):
            log(f"   Question: {decision.get('question')[:80]}...")
        log(f"{'─'*80}\n")
        
        # NOTE: Do NOT clear user_instruction here - let analyzer clear it after processing
        
        if action_type == "query_local_rag":
            log(f"   📝 Next action: QUERY LOCAL RAG")
            return {
                **state,
                "next_action": "query_local_rag",
                "rag_query": decision.get("rag_query", decision.get("search_query", "")),
                "questions": questions,
                "iteration": iteration + 1
            }
        elif action_type == "wayback_machine":
            log(f"   📝 Next action: WAYBACK MACHINE")
            return {
                **state,
                "next_action": "wayback_machine",
                "target_url": decision.get("target_url", ""),
                "wayback_reasoning": decision.get("tool_reasoning", "Checking for cover-ups"),
                "questions": questions,
                "iteration": iteration + 1
            }
        elif action_type == "aleph_search":
            log(f"   📝 Next action: ALEPH SEARCH")
            return {
                **state,
                "next_action": "aleph_search",
                "aleph_query": decision.get("aleph_query", ""),
                "aleph_reasoning": decision.get("tool_reasoning", "Corporate intelligence"),
                "questions": questions,
                "iteration": iteration + 1
            }
        else:  # tavily_search
            log(f"   📝 Next action: TAVILY SEARCH")
            return {
                **state,
                "next_action": "search",
                "search_query": new_query,
                "previous_queries": updated_queries,
                "questions": questions,
                "iteration": iteration + 1
            }
    
    def _is_query_similar(self, new_query: str, previous_queries: List[str]) -> bool:
        """Check if query is too similar to previous ones"""
        if not previous_queries:
            return False
        
        # Normalize queries
        new_norm = new_query.lower().replace('2025', '').replace('october', '').replace('recent', '').replace('latest', '')
        new_words = set(new_norm.split())
        
        for prev_q in previous_queries:
            prev_norm = prev_q.lower().replace('2025', '').replace('october', '').replace('recent', '').replace('latest', '')
            prev_words = set(prev_norm.split())
            
            # Check word overlap
            if len(new_words) > 0 and len(prev_words) > 0:
                overlap = len(new_words.intersection(prev_words))
                similarity = overlap / min(len(new_words), len(prev_words))
                
                if similarity > 0.7:  # 70% similar
                    return True
        
        return False
    
    def _should_search_this_iteration(self, iteration: int, state: HypothesisState) -> bool:
        """Determine if we should search this iteration based on phase"""
        # Phase 1 (1-20): Search every iteration
        if iteration <= 20:
            return True
        
        # Phase 2 (21-60): Search every 2 iterations
        if iteration <= 60:
            return iteration % 2 == 1
        
        # Phase 3 (61-100): Search every 5 iterations (hypothesis refinement)
        return iteration % 5 == 1
    
    async def _local_rag_query_node(self, state: HypothesisState) -> HypothesisState:
        """
        Query LOCAL RAG - search accumulated knowledge from this investigation
        """
        query = state.get("rag_query", "")
        
        log(f"\n{'='*80}")
        log(f"💾 LOCAL RAG QUERY NODE")
        log(f"{'='*80}")
        log(f"Query: {query}")
        
        # Emit event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('log', {
                    "message": f"💾 Querying local knowledge base: {query}"
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Query local RAG
        result = await self._query_local_rag(
            query=query,
            investigation_id=state["investigation_id"],
            top_k=10
        )
        
        # Track RAG usage
        state["rag_queries_made"] = state.get("rag_queries_made", 0) + 1
        
        # Format results as "extracted content" for analyzer
        rag_articles = []
        if result.get('num_results', 0) > 0:
            log(f"   ✅ Found {result['num_results']} relevant documents from local knowledge base")
            
            # Create article entries from RAG chunks
            for i, chunk in enumerate(result.get('chunks', [])[:5], 1):  # Top 5
                url = chunk.get('metadata', {}).get('url', 'Local Knowledge Base')
                content = chunk.get('content', '')
                score = chunk.get('score', 0)
                
                rag_articles.append({
                    "url": url,
                    "content": content[:3000],  # Limit content
                    "method": f"local_rag (score: {score:.2f})",
                    "iteration": chunk.get('metadata', {}).get('iteration', 'N/A')
                })
                
                log(f"   [{i}] {url[:60]}... (score: {score:.2f})")
            
            # Emit event with sources
            if hasattr(self, 'event_callback') and self.event_callback:
                try:
                    await self.event_callback('log', {
                        "message": f"📄 Found {len(rag_articles)} relevant documents in local knowledge"
                    })
                except Exception as e:
                    pass
        else:
            log(f"   ⚠️  No relevant documents found in local knowledge base")
            log(f"   💡 May need to use Tavily search for fresh information")
            
            # Emit event
            if hasattr(self, 'event_callback') and self.event_callback:
                try:
                    await self.event_callback('log', {
                        "message": "⚠️ No relevant documents in local knowledge - may need fresh search"
                    })
                except Exception as e:
                    pass
        
        return {
            **state,
            "extracted_content": rag_articles,
            "rag_answer": result.get('answer', ''),
            "rag_sources": result.get('sources', [])
        }
    
    async def _searcher_node(self, state: HypothesisState) -> HypothesisState:
        """
        Multi-tool search node
        Supports: Tavily, Wayback Machine, OCCRP Aleph
        """
        action = state.get("next_action", "search")
        
        log(f"\n{'='*80}")
        log(f"🔍 MULTI-TOOL SEARCHER")
        log(f"{'='*80}")
        log(f"Tool: {action}")
        
        # Route to appropriate tool
        if action == "wayback_machine":
            return await self._wayback_search(state)
        elif action == "aleph_search":
            return await self._aleph_search(state)
        else:  # Default: tavily search
            return await self._tavily_search(state)
    
    async def _tavily_search(self, state: HypothesisState) -> HypothesisState:
        """Execute Tavily web search"""
        query = state.get("search_query", "")
        
        log(f"   Mode: Tavily Web Search")
        log(f"   Query: {query}")
        
        # Emit professional search event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('thinking', {
                    "status": "Searching current web",
                    "details": query[:100] + "..." if len(query) > 100 else query,
                    "action": "tavily_search"
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Execute single Tavily search (WITH CACHING)
        results = await self.tavily.search(
            query=query,
            max_results=5,  # Only 5 results
            search_depth="basic"  # Use basic, not advanced
        )
        
        # Track cost
        self.costs["tavily_searches"] += 1
        self.costs["total_cost"] += self.COST_TAVILY_SEARCH
        
        articles = results.get("results", [])
        log(f"   ✅ Found {len(articles)} articles (Cost: ${self.COST_TAVILY_SEARCH:.3f})")
        
        # Filter out already seen URLs
        new_articles = [
            a for a in articles 
            if a.get("url") not in state["seen_urls"]
        ]
        log(f"   📰 {len(new_articles)} new articles")
        
        # Emit professional articles found event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('thinking', {
                    "status": f"Found {len(new_articles)} relevant sources",
                    "details": f"Discovered {len(new_articles)} new articles to analyze",
                    "action": "content_discovery"
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Track tool usage
        tool_history = state.get("tool_history", [])
        tool_history.append({
            "tool": "tavily_search",
            "query": query,
            "iteration": state["iteration"]
        })
        
        return {
            **state,
            "search_results": new_articles,
            "seen_urls": state["seen_urls"] + [a.get("url") for a in new_articles],
            "tool_history": tool_history
        }
    
    async def _wayback_search(self, state: HypothesisState) -> HypothesisState:
        """Execute Wayback Machine investigation"""
        target_url = state.get("target_url", "")
        reasoning = state.get("wayback_reasoning", "Checking for cover-ups")
        
        log(f"   Mode: Wayback Machine (Cover-Up Detection)")
        log(f"   Target URL: {target_url}")
        log(f"   Reasoning: {reasoning}")
        
        # Validation: Ensure URL is provided
        used_fallback = False
        if not target_url or target_url.strip() == "":
            log(f"\n{'🚨'*40}")
            log(f"❌ CRITICAL ERROR: No target URL provided for Wayback Machine!")
            log(f"   LLM Response missing 'target_url' field")
            log(f"   This indicates the strategist prompt needs improvement")
            log(f"   💡 Falling back to default: https://cdsco.gov.in")
            log(f"{'🚨'*40}\n")
            target_url = "https://cdsco.gov.in"  # Default to Indian drug regulator
            used_fallback = True
            
            # Emit error event to UI
            if hasattr(self, 'event_callback') and self.event_callback:
                try:
                    await self.event_callback('error', {
                        "message": "⚠️ Wayback Machine: No URL provided by strategist, using fallback",
                        "details": "The LLM chose wayback_machine but didn't provide target_url field",
                        "fallback_url": target_url,
                        "severity": "warning"
                    })
                except Exception as e:
                    log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Emit event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                status_text = "🕰️ Checking historical versions"
                if used_fallback:
                    status_text = "⚠️ Checking historical versions (using fallback URL)"
                
                await self.event_callback('thinking', {
                    "status": status_text,
                    "details": f"Investigating {target_url} for content changes or deletions",
                    "action": "wayback_search",
                    "used_fallback": used_fallback
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Execute Wayback Machine comparison
        result = self.wayback.compare_versions(target_url)
        
        # Track cost (free!)
        self.costs["wayback_checks"] += 1
        
        # Format as "article" for extraction pipeline
        summary = result.get('summary', 'No data')
        wayback_article = {
            "url": target_url,
            "title": f"Wayback Machine Analysis: {target_url}",
            "content": f"""
WAYBACK MACHINE INVESTIGATION REPORT
Target: {target_url}
Status: {result.get('status', 'unknown')}

{summary}

Snapshots Available: {result.get('total_snapshots', 0)}
Earliest: {result.get('earliest_snapshot', 'N/A')}
Latest: {result.get('latest_snapshot', 'N/A')}
Suspicious Activity: {result.get('suspicious_activity', False)}

ANALYSIS:
{summary}

🚨 INVESTIGATIVE NOTE:
{"This website shows evidence of content deletion or modification, which may indicate a cover-up attempt." if result.get('suspicious_activity') else "No suspicious changes detected, but content has evolved over time."}
""",
            "score": 1.0 if result.get('suspicious_activity') else 0.7,
            "published_date": result.get('latest_snapshot', 'Unknown')
        }
        
        log(f"   ✅ Wayback analysis complete (Cost: $0.00 - FREE)")
        if result.get('suspicious_activity'):
            log(f"   🚨 SUSPICIOUS: Content deletion detected!")
        
        # Track tool usage
        tool_history = state.get("tool_history", [])
        tool_history.append({
            "tool": "wayback_machine",
            "target_url": target_url,
            "iteration": state["iteration"],
            "suspicious": result.get('suspicious_activity', False)
        })
        
        return {
            **state,
            "search_results": [wayback_article],
            "seen_urls": state["seen_urls"] + [target_url],
            "tool_history": tool_history
        }
    
    async def _aleph_search(self, state: HypothesisState) -> HypothesisState:
        """Execute OCCRP Aleph search"""
        query = state.get("aleph_query", "")
        reasoning = state.get("aleph_reasoning", "Corporate intelligence")
        
        log(f"   Mode: OCCRP Aleph (Leaked Docs & Sanctions)")
        log(f"   Query: {query}")
        log(f"   Reasoning: {reasoning}")
        
        # Validation: Ensure query is provided
        used_fallback = False
        if not query or query.strip() == "":
            log(f"\n{'🚨'*40}")
            log(f"❌ CRITICAL ERROR: No query provided for Aleph search!")
            log(f"   LLM Response missing 'aleph_query' field")
            log(f"   This indicates the strategist prompt needs improvement")
            log(f"   💡 Falling back to generic search based on initial query")
            log(f"{'🚨'*40}\n")
            
            # Try to extract company names from state
            entities = state.get("entities", {})
            companies = [name for name, ent in entities.items() if ent.get("type") == "company"]
            
            if companies:
                query = companies[0]
                log(f"   Using entity: {query}")
            else:
                # Last resort: use initial query
                query = state.get("initial_query", "India pharmaceutical")
                log(f"   Using initial query: {query}")
            
            used_fallback = True
            
            # Emit error event to UI
            if hasattr(self, 'event_callback') and self.event_callback:
                try:
                    await self.event_callback('error', {
                        "message": "⚠️ Aleph Search: No query provided by strategist, using fallback",
                        "details": "The LLM chose aleph_search but didn't provide aleph_query field",
                        "fallback_query": query,
                        "severity": "warning"
                    })
                except Exception as e:
                    log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Emit event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                status_text = "🗂️ Searching leaked documents database"
                if used_fallback:
                    status_text = "⚠️ Searching leaked documents (using fallback query)"
                
                await self.event_callback('thinking', {
                    "status": status_text,
                    "details": f"Investigating {query} in Panama Papers, sanctions lists, and corporate registries",
                    "action": "aleph_search",
                    "used_fallback": used_fallback
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Execute Aleph search
        result = self.aleph.search(query, limit=5)
        
        # Track cost (free!)
        self.costs["aleph_searches"] += 1
        
        # Format as "article" for extraction pipeline
        formatted_content = self.aleph.format_for_llm(result)
        
        aleph_article = {
            "url": f"https://aleph.occrp.org/search?q={query}",
            "title": f"OCCRP Aleph Intelligence: {query}",
            "content": formatted_content,
            "score": 0.9 if result.get('total', 0) > 0 else 0.3,
            "published_date": "Multiple sources"
        }
        
        results_count = result.get('total', 0)
        log(f"   ✅ Aleph search complete: {results_count} results (Cost: $0.00 - FREE)")
        
        # Track tool usage
        tool_history = state.get("tool_history", [])
        tool_history.append({
            "tool": "aleph_search",
            "query": query,
            "iteration": state["iteration"],
            "results_found": results_count
        })
        
        return {
            **state,
            "search_results": [aleph_article],
            "seen_urls": state["seen_urls"] + [aleph_article["url"]],
            "tool_history": tool_history
        }
    
    async def _extractor_node(self, state: HypothesisState) -> HypothesisState:
        """
        Extract content using FREE methods (no Tavily extract)
        """
        articles = state.get("search_results", [])
        
        log(f"\n{'='*80}")
        log(f"📖 EXTRACTOR (Free Methods)")
        log(f"{'='*80}")
        log(f"   📊 Extracting from {len(articles)} articles")
        
        # Emit professional extraction start event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('thinking', {
                    "status": "Extracting content from sources",
                    "details": f"Processing {min(len(articles), 2)} articles using free extraction methods",
                    "action": "content_extraction"
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        extracted_content = []
        
        # Extract only TOP 2 articles (was 3, now 2 for cost saving)
        for i, article in enumerate(articles[:2], 1):
            url = article.get("url", "")
            log(f"   [{i}] Attempting: {url[:70]}...")
            
            # Check cache first
            cache_key = self._url_to_cache_key(url)
            cache_file = self.cache_dir / f"{cache_key}.txt"
            
            if cache_file.exists():
                log(f"   [{i}] 💾 Using cached")
                content = cache_file.read_text()
                self.costs["cached_extracts"] += 1
                extracted_content.append({
                    "url": url,
                    "content": content,
                    "method": "cache"
                })
                continue
            
            # Try free extraction
            content = await self._extract_free_async(url)
            
            if content and len(content) > 500:
                log(f"   [{i}] ✅ Free extraction: {len(content)} chars (Cost: $0.00)")
                self.costs["free_extracts"] += 1
                
                # Check for oversized content
                if len(content) > self.WARN_CONTENT_CHARS:
                    log(f"   [{i}] ⚠️  WARNING: Very large document ({len(content):,} chars)")
                    log(f"        This is likely a PDF or very long page")
                    log(f"        Truncating to {self.MAX_CONTENT_CHARS:,} chars to prevent LLM overload")
                    
                    # Intelligent truncation: Keep beginning and end
                    half_limit = self.MAX_CONTENT_CHARS // 2
                    content = (
                        content[:half_limit] + 
                        f"\n\n... [CONTENT TRUNCATED - Original: {len(content):,} chars, Showing first {half_limit:,} and last {half_limit:,} chars] ...\n\n" +
                        content[-half_limit:]
                    )
                    
                    # Emit warning to UI
                    if hasattr(self, 'event_callback') and self.event_callback:
                        try:
                            await self.event_callback('warning', {
                                "message": f"⚠️ Large document truncated",
                                "details": f"Article [{i}] was {len(content):,} chars, truncated to {self.MAX_CONTENT_CHARS:,}",
                                "url": url[:60] + "..."
                            })
                        except Exception as e:
                            pass
                
                # Cache it
                cache_file.write_text(content)
                extracted_content.append({
                    "url": url,
                    "content": content,
                    "method": "free"
                })
            else:
                # Fallback to Tavily extract
                log(f"   [{i}] ⚠️  Free failed, trying Tavily extract...")
                try:
                    tavily_result = await self.tavily.extract(urls=[url])
                    
                    if tavily_result and tavily_result.get("results"):
                        content = tavily_result["results"][0].get("raw_content", "")
                        
                        if content and len(content) > 500:
                            log(f"   [{i}] ✅ Tavily extract: {len(content)} chars (Cost: ${self.COST_TAVILY_EXTRACT:.3f})")
                            self.costs["tavily_extracts"] += 1
                            self.costs["total_cost"] += self.COST_TAVILY_EXTRACT
                            # Cache it
                            cache_file.write_text(content)
                            extracted_content.append({
                                "url": url,
                                "content": content,
                                "method": "tavily"
                            })
                        else:
                            log(f"   [{i}] ❌ Both methods failed")
                    else:
                        log(f"   [{i}] ❌ Tavily extract returned no results")
                except Exception as e:
                    log(f"   [{i}] ❌ Tavily extract error: {str(e)[:50]}")
        
        log(f"   📊 Extracted {len(extracted_content)}/{len(articles)} successfully")
        
        # CRITICAL: Check total content size to prevent LLM overload
        total_content_size = sum(len(e.get("content", "")) for e in extracted_content)
        log(f"   📏 Total content size: {total_content_size:,} chars")
        
        if total_content_size > self.MAX_TOTAL_CONTENT_CHARS:
            log(f"   ⚠️  WARNING: Total content exceeds limit ({self.MAX_TOTAL_CONTENT_CHARS:,} chars)")
            log(f"        Keeping only the most relevant articles")
            
            # Sort by length (prefer shorter, more digestible articles)
            extracted_content.sort(key=lambda x: len(x.get("content", "")))
            
            # Keep articles until we hit the limit
            kept_content = []
            running_size = 0
            for article in extracted_content:
                article_size = len(article.get("content", ""))
                if running_size + article_size <= self.MAX_TOTAL_CONTENT_CHARS:
                    kept_content.append(article)
                    running_size += article_size
                else:
                    log(f"        Dropped article: {article.get('url', 'unknown')[:60]}... ({article_size:,} chars)")
            
            extracted_content = kept_content
            log(f"   ✅ Kept {len(extracted_content)} articles, total: {running_size:,} chars")
            
            # Emit warning to UI
            if hasattr(self, 'event_callback') and self.event_callback:
                try:
                    await self.event_callback('warning', {
                        "message": "⚠️ Content size limit reached",
                        "details": f"Kept {len(extracted_content)} most relevant articles to prevent LLM overload",
                        "total_size": f"{running_size:,} chars"
                    })
                except Exception as e:
                    pass
        
        return {
            **state,
            "extracted_content": extracted_content
        }
    
    async def _extract_free_async(self, url: str) -> Optional[str]:
        """
        ⚡ OPTIMIZED: Async extraction with connection pooling (2-3x faster)
        Try multiple free extraction methods using httpx instead of requests
        """
        try:
            # Method 1: Jina AI Reader (most reliable, free)
            jina_url = f"https://r.jina.ai/{url}"
            
            try:
                jina_response = await self.http_client.get(jina_url, timeout=15)
                if jina_response.status_code == 200 and len(jina_response.text) > 500:
                    log(f"      ✅ Jina AI success")
                    return jina_response.text
            except Exception as e:
                log(f"      ⚠️  Jina AI failed: {str(e)[:30]}")
            
            # Method 2: Trafilatura (good for news articles)
            response = await self.http_client.get(url, timeout=10)
            
            if response.status_code == 200:
                # Try trafilatura
                content = trafilatura.extract(response.content)
                if content and len(content) > 500:
                    log(f"      ✅ Trafilatura success")
                    return content
                
                # Fallback: BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator='\n', strip=True)
                
                # Clean up
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                content = '\n'.join(lines)
                
                if len(content) > 500:
                    log(f"      ✅ BeautifulSoup success")
                    return content
            
            return None
            
        except Exception as e:
            log(f"      ⚠️  All extraction methods failed: {str(e)[:50]}")
            return None
    
    def _url_to_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    async def _store_in_local_rag(self, extracted_content: List[Dict], state: HypothesisState):
        """
        Store extracted articles in vector DB for local RAG queries (ASYNC)
        
        This enables the investigative journalist to query its own accumulated
        evidence using semantic search. Uses the same MongoDB handler as cognitive crawler.
        """
        import hashlib
        
        log(f"\n{'─'*80}")
        log(f"💾 LOCAL RAG STORAGE (ASYNC)")
        log(f"{'─'*80}")
        
        try:
            # Import mongodb handler from cognitive crawler
            import sys
            import os
            crawler_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '../cognitive_crawler/tools')
            )
            if crawler_dir not in sys.path:
                sys.path.insert(0, crawler_dir)
            
            from mongodb_handler import TenderMongoDBHandler
            
            log(f"   ✅ Using TenderMongoDBHandler (same as cognitive crawler)")
            
            db = TenderMongoDBHandler()
            
            # Prepare documents for storage
            documents = []
            for i, article in enumerate(extracted_content, 1):
                # Generate unique doc_id
                url = article.get("url", "")
                doc_id = hashlib.md5(f"{url}_{state['investigation_id']}".encode()).hexdigest()
                
                doc = {
                    "doc_id": doc_id,
                    "content": article["content"],
                    "metadata": {
                        "url": url,
                        "investigation_id": state["investigation_id"],
                        "query": state["initial_query"],
                        "iteration": state["iteration"],
                        "extraction_method": article.get("method", "unknown"),
                        "stored_at": datetime.now(timezone.utc).isoformat()
                    }
                }
                documents.append(doc)
                
                log(f"   [{i}] URL: {url[:60]}...")
                log(f"       doc_id: {doc_id[:16]}...")
                log(f"       content_length: {len(article['content'])} chars")
            
            # Store with investigation_id as thread_id for LOCAL RAG filtering
            log(f"   🔒 thread_id: {state['investigation_id'][:30]}...")
            log(f"   📦 Storing {len(documents)} documents...")
            
            await db.store_vectors(
                documents=documents,
                thread_id=state["investigation_id"]
            )
            
            log(f"   ✅ Storage complete - {len(documents)} articles now in LOCAL RAG")
            log(f"   🔍 Queryable from iteration 2+ using investigation_id filter")
            log(f"{'─'*80}\n")
            
            db.close()
            
        except Exception as e:
            log(f"   ❌ LOCAL RAG storage failed (non-critical): {e}")
            log(f"   🔍 Investigation will continue without RAG storage")
            log(f"{'─'*80}\n")
            import traceback
            traceback.print_exc()
            # Don't fail the investigation if RAG storage fails
    
    async def _query_local_rag(self, query: str, investigation_id: str, top_k: int = 10) -> Dict[str, Any]:
        """
        Query LOCAL RAG - only content from THIS investigation
        
        Args:
            query: Question to ask
            investigation_id: Current investigation ID
            top_k: Number of results to return
            
        Returns:
            Dict with answer, sources, chunks, scores
        """
        log(f"\n{'─'*80}")
        log(f"🔍 LOCAL RAG QUERY")
        log(f"{'─'*80}")
        log(f"   Query: {query}")
        log(f"   🔒 Filtering to investigation: {investigation_id[:30]}...")
        log(f"   📊 Requesting top_{top_k} results")
        
        try:
            from tools.rag_query import query_rag
            
            result = await query_rag(
                query=query,
                thread_id=investigation_id,  # Filter to this investigation only
                top_k=top_k,
                min_score=0.3,
                generate_answer=True
            )
            
            log(f"   ✅ Found {result['num_results']} relevant chunks")
            
            if result['num_results'] > 0:
                log(f"   📄 Sources:")
                for i, source in enumerate(result.get('sources', [])[:3], 1):
                    log(f"       [{i}] {source[:70]}...")
                log(f"   💡 Answer generated: {len(result.get('answer', ''))} chars")
            else:
                log(f"   ℹ️  No relevant content found in local knowledge base")
            
            log(f"{'─'*80}\n")
            
            return result
            
        except Exception as e:
            log(f"   ❌ Local RAG query failed: {e}")
            log(f"{'─'*80}\n")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "answer": "",
                "sources": [],
                "chunks": [],
                "num_results": 0,
                "error": str(e)
            }
    
    async def _query_global_rag(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        Query GLOBAL RAG - search all accumulated knowledge across investigations
        
        Args:
            query: Question to ask
            top_k: Number of results to return
            
        Returns:
            Dict with answer, sources, chunks, scores
        """
        try:
            from tools.rag_query import query_rag
            
            result = await query_rag(
                query=query,
                thread_id=None,  # No filter = search everything
                top_k=top_k,
                min_score=0.3,
                generate_answer=True
            )
            
            log(f"   🌐 Global RAG: Found {result['num_results']} relevant chunks across all investigations")
            return result
            
        except Exception as e:
            log(f"   ❌ Global RAG query failed: {e}")
            return {
                "success": False,
                "answer": "",
                "sources": [],
                "chunks": [],
                "num_results": 0,
                "error": str(e)
            }
    
    async def _analyzer_node(self, state: HypothesisState) -> HypothesisState:
        """
        Analyze extracted content for novel insights
        Focus on hypothesis testing and anomaly detection
        """
        extracted = state.get("extracted_content", [])
        
        log(f"\n{'='*80}")
        log(f"🔬 ANALYZER")
        log(f"{'='*80}")
        
        # Emit professional analysis start event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('thinking', {
                    "status": "Analyzing extracted content",
                    "details": "Identifying facts, entities, and patterns using AI analysis",
                    "action": "ai_analysis"
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        if not extracted:
            log("   ⚠️  No content to analyze")
            return state
        
        # Prepare content for analysis
        articles_text = ""
        for i, item in enumerate(extracted, 1):
            articles_text += f"\n\n--- ARTICLE {i} ---\n"
            articles_text += f"URL: {item['url']}\n"
            articles_text += f"CONTENT:\n{item['content'][:3000]}\n"  # Limit to 3000 chars per article
        
        analysis_prompt = f"""Analyze these articles for NOVEL insights and hypothesis testing.

INVESTIGATION: {state['initial_query']}

EXISTING HYPOTHESES:
{json.dumps(state['hypotheses'][:5], indent=2)}

EXISTING QUESTIONS (TO BE ANSWERED):
{json.dumps([dict(id=q["id"], hypothesis_id=q["hypothesis_id"], question=q["question"], status=q.get("status", "exploring")) for q in state.get("questions", []) if not q.get("answer")][:10], indent=2)}

EXISTING ENTITIES:
{json.dumps(list(state['entities'].keys())[:20], indent=2)}

ARTICLES:
{articles_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR ANALYSIS MISSION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **Answer unanswered questions**: For each question above, provide a DIRECT answer if found in the articles
2. **Extract NEW entities** (people, orgs, locations not yet identified)
3. **Test hypotheses**: Does this evidence support or refute existing hypotheses?
4. **Find connections**: Financial, political, personal relationships
5. **Detect anomalies**: What's suspicious? What's missing?
6. **Generate facts**: Specific, verifiable claims

CRITICAL FRAMEWORKS:
- **Temporal anomalies**: When did things happen? Any suspicious timing?
- **Financial anomalies**: Money flows, unusual transactions
- **Incentive misalignments**: Who benefits? Who's protecting whom?
- **Conspicuous absences**: What SHOULD be here but isn't?

⚡ **ANSWER QUESTIONS AGGRESSIVELY**: If article mentions the topic (even partially), provide an answer!
Don't wait for perfect certainty. Partial answers > no answers.

Return JSON:
{{
  "question_answers": [
    {{"question_id": "q_123", "answer": "Direct answer from article", "confidence": 0.0-1.0, "source_url": "article URL"}}
  ],
  "new_entities": [
    {{"name": "Entity name", "type": "person|org|location", "role": "Brief role", "significance": "Why important"}}
  ],
  "new_facts": ["Specific fact 1", "Specific fact 2"],
  "connections": [
    {{"from": "Entity A", "to": "Entity B", "type": "donated/appointed/owns/regulates", "evidence": "Source from article"}}
  ],
  "new_hypotheses": [
    {{"id": "h1", "statement": "Hypothesis statement", "status": "exploring", "confidence": 0.5, "evidence": []}}
  ],
  "hypothesis_updates": [
    {{"id": "h1", "status": "confirmed|refuted|exploring", "confidence": 0.0-1.0, "evidence": "What you found"}}
  ],
  "anomalies": ["What's unusual/suspicious/missing"],
  "novel_insights": ["NEW angle/pattern/connection others would miss"]
}}

IMPORTANT: In early iterations, focus on generating NEW hypotheses. In later iterations, focus on testing existing ones.
Focus on NOVELTY. What would an investigative journalist find interesting?
"""
        
        response = await self.llm.ainvoke([SystemMessage(content=analysis_prompt)])
        analysis = self._parse_json(response.content)
        
        # Track LLM cost
        self.costs["llm_calls"] += 1
        self.costs["total_cost"] += (self.COST_GPT4O_INPUT + self.COST_GPT4O_OUTPUT)
        
        # ✨ NEW: Store extracted content in RAG for local queries
        # Track documents stored in RAG BEFORE storage (important for state updates)
        documents_in_rag = state.get("documents_in_rag", 0)
        
        if extracted and state.get("investigation_id"):
            await self._store_in_local_rag(extracted, state)
            documents_in_rag += len(extracted)
            log(f"   💾 Documents in LOCAL RAG: {len(extracted)}")
        
        # Update state
        new_entities = state["entities"].copy()
        for entity in analysis.get("new_entities", []):
            new_entities[entity["name"]] = entity
        
        new_facts = state["facts"] + analysis.get("new_facts", [])
        new_connections = state["connections"] + analysis.get("connections", [])
        new_anomalies = state["anomalies"] + analysis.get("anomalies", [])
        
        # 🆕 Process question answers from analyzer
        question_answers = analysis.get("question_answers", [])
        questions_list = state.get("questions", []).copy()
        
        # 🐛 DEBUG: Log question tracking status
        unanswered_questions = [q for q in questions_list if not q.get("answer")]
        log(f"   🐛 DEBUG - Question Status:")
        log(f"      Total questions: {len(questions_list)}")
        log(f"      Unanswered: {len(unanswered_questions)}")
        log(f"      Answers from analyzer: {len(question_answers)}")
        
        if unanswered_questions:
            log(f"   📋 Unanswered questions (showing first 3):")
            for q in unanswered_questions[:3]:
                log(f"      - [{q.get('id')}] {q.get('question', '')[:80]}...")
        
        if question_answers:
            log(f"   💬 Processing {len(question_answers)} question answers from analyzer...")
            
            for qa in question_answers:
                question_id = qa.get("question_id")
                answer_text = qa.get("answer")
                source_url = qa.get("source_url")
                confidence = qa.get("confidence", 0.8)
                
                # Find and update the question
                question_found = False
                for q in questions_list:
                    if q.get("id") == question_id:
                        question_found = True
                        q["answer"] = answer_text
                        q["source"] = source_url
                        q["status"] = "answered"
                        q["iteration"] = state["iteration"]
                        
                        log(f"      ✅ Answered Q: {q.get('question', '')[:60]}...")
                        log(f"         A: {answer_text[:80]}...")
                        
                        # Emit question_answered event via WebSocket
                        if hasattr(self, 'event_callback') and self.event_callback:
                            try:
                                await self.event_callback('question_answered', {
                                    "question_id": question_id,
                                    "hypothesis_id": q.get("hypothesis_id"),
                                    "question": q.get("question"),
                                    "answer": answer_text,
                                    "source": source_url,
                                    "iteration": state["iteration"]
                                })
                            except Exception as e:
                                log(f"         ⚠️  WebSocket push failed: {e}")
                        break
                
                if not question_found:
                    log(f"      ⚠️  WARNING: Answer provided for unknown question_id: {question_id}")
                    log(f"         Available question IDs: {[q.get('id') for q in questions_list]}")
        else:
            if unanswered_questions:
                log(f"   ⚠️  WARNING: {len(unanswered_questions)} unanswered questions, but analyzer provided no answers!")
                log(f"      This may indicate the LLM didn't follow instructions to answer questions.")
        
        # Handle new hypotheses from analyzer
        existing_hypotheses = state["hypotheses"].copy()
        new_hypotheses_from_analysis = analysis.get("new_hypotheses", [])
        
        # Add IDs and defaults to new hypotheses if not present
        for hyp in new_hypotheses_from_analysis:
            if "id" not in hyp:
                hyp["id"] = f"h{len(existing_hypotheses) + 1}"
            if "status" not in hyp:
                hyp["status"] = "exploring"
            if "confidence" not in hyp:
                hyp["confidence"] = 0.5
            if "evidence" not in hyp:
                hyp["evidence"] = []
            if "priority" not in hyp:
                hyp["priority"] = 10  # Normal priority (user-driven get priority=0)
            if "questions" not in hyp:
                hyp["questions"] = []  # Initialize questions list
            existing_hypotheses.append(hyp)
            
            # Push to WebSocket in real-time if callback provided
            if hasattr(self, 'event_callback') and self.event_callback:
                try:
                    await self.event_callback('hypothesis_updated', hyp)
                except Exception as e:
                    log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Update existing hypotheses based on evidence
        updated_hypotheses = self._update_hypotheses(
            existing_hypotheses,
            analysis.get("hypothesis_updates", [])
        )
        
        # Nest questions inside their parent hypotheses (use updated questions_list with answers)
        for hyp in updated_hypotheses:
            # Find all questions for this hypothesis
            hyp_questions = [q for q in questions_list if q.get("hypothesis_id") == hyp.get("id")]
            # Ensure hypothesis has questions list
            if "questions" not in hyp:
                hyp["questions"] = []
            # Update with linked questions
            hyp["questions"] = hyp_questions
        
        # 🎯 SUMMARY LOG: Question answering status
        total_questions = len(questions_list)
        answered_questions = len([q for q in questions_list if q.get("answer")])
        unanswered_count = total_questions - answered_questions
        
        log(f"\n{'─'*80}")
        log(f"📊 ANALYZER SUMMARY (Iteration {state['iteration']}):")
        log(f"   Questions:")
        log(f"      Total: {total_questions}")
        log(f"      Answered: {answered_questions} ({'✅' if answered_questions > 0 else '⚠️'})")
        log(f"      Unanswered: {unanswered_count}")
        log(f"   Hypotheses with questions:")
        for hyp in updated_hypotheses:
            hyp_q_count = len(hyp.get("questions", []))
            hyp_answered = len([q for q in hyp.get("questions", []) if q.get("answer")])
            if hyp_q_count > 0:
                log(f"      [{hyp['id']}] {hyp_q_count} questions ({hyp_answered} answered)")
        log(f"{'─'*80}\n")
        
        log(f"   ✅ New entities: {len(analysis.get('new_entities', []))}")
        log(f"   ✅ New facts: {len(analysis.get('new_facts', []))}")
        log(f"   ✅ New connections: {len(analysis.get('connections', []))}")
        log(f"   ✅ Anomalies: {len(analysis.get('anomalies', []))}")
        log(f"   🔬 New hypotheses: {len(new_hypotheses_from_analysis)}")
        log(f"   💡 Novel insights: {len(analysis.get('novel_insights', []))}")
        log(f"   💾 Documents in LOCAL RAG: {documents_in_rag}")
        
        if analysis.get("novel_insights"):
            for insight in analysis["novel_insights"]:
                log(f"      🔥 {insight}")
        
        # Build updated state
        updated_state = {
            **state,  # Preserve all fields including investigation_id
            "entities": new_entities,
            "facts": new_facts,
            "connections": new_connections,
            "anomalies": new_anomalies,
            "hypotheses": updated_hypotheses,
            "documents_in_rag": documents_in_rag,  # Track for strategist
            "questions": questions_list,  # Use updated questions list with answers!
            "investigation_id": state.get("investigation_id"),  # Explicitly preserve investigation_id
            "user_instruction": None  # Clear after analyzer processes it (so next iteration doesn't see it)
        }
        
        # Log if we're clearing a user instruction
        if state.get("user_instruction"):
            log(f"   🔄 Clearing user_instruction after analysis: {state.get('user_instruction')[:60]}...")
        
        # Incremental save to MongoDB for real-time UI updates
        investigation_id = updated_state.get("investigation_id")  # Get from updated_state, not state
        log(f"   🔍 Checking incremental save: investigation_id={investigation_id}")
        if investigation_id:
            try:
                # Import using absolute path to avoid module conflicts
                import sys
                import os
                from pathlib import Path
                
                # Get the investigative_journalist directory
                current_dir = Path(__file__).parent
                tools_dir = current_dir / 'tools'
                
                # Add to sys.path if not already there
                if str(current_dir) not in sys.path:
                    sys.path.insert(0, str(current_dir))
                
                from tools.evidence_repository import save_investigation
                log(f"   💾 Saving iteration {updated_state['iteration']} to MongoDB...")
                await save_investigation({
                    **updated_state,
                    "cost_tracking": self.costs
                })
                log(f"   ✅ Saved iteration {updated_state['iteration']} to MongoDB")
                
                # Send state update via WebSocket
                if hasattr(self, 'event_callback') and self.event_callback:
                    try:
                        # Prepare clean state for frontend (V2 schema compatible)
                        frontend_state = {
                            "meta": {
                                "investigation_id": str(investigation_id) if investigation_id else None,
                                "iteration": int(updated_state.get("iteration", 0)),
                                "max_iterations": int(updated_state.get("max_iterations", 0)),
                                "phase": "exploration" if updated_state.get("iteration", 0) < updated_state.get("max_iterations", 0) else "synthesis",
                                "overall_confidence": float(sum(h.get("confidence", 0) for h in updated_state.get("hypotheses", [])) / max(len(updated_state.get("hypotheses", [])), 1))
                            },
                            "hypotheses": [
                                {
                                    "id": str(h.get("id", "")),
                                    "statement": str(h.get("statement", "")),
                                    "status": str(h.get("status", "exploring")),
                                    "confidence": float(h.get("confidence", 0.5)),
                                    "importance": float(h.get("importance", 0.5)),
                                    "priority": int(h.get("priority", 10)),
                                    "questions": [
                                        {
                                            "q": str(q.get("question", q.get("q", ""))),
                                            "a": str(q.get("answer", q.get("a", ""))) if (q.get("answer") or q.get("a")) else None,
                                            "src": str(q.get("source", q.get("src", ""))) if (q.get("source") or q.get("src")) else None,
                                            "status": str(q.get("status", "exploring")),
                                            "iteration": int(q.get("iteration", 0)) if q.get("iteration") else None
                                        }
                                        for q in (h.get("questions", []) or [])
                                    ]
                                }
                                for h in (updated_state.get("hypotheses", []) or [])
                            ],
                            "entities": [
                                {
                                    "name": str(name),
                                    "type": str(entity.get("type", "unknown")),
                                    "role": str(entity.get("role", "")),
                                    "importance": float(entity.get("importance", 0.5)),
                                    "investigated": bool(entity.get("investigated", False))
                                }
                                for name, entity in (updated_state.get("entities", {}) or {}).items()
                            ],
                            "facts": [str(f) for f in (updated_state.get("facts", []) or [])],
                            "anomalies": [str(a) for a in (updated_state.get("anomalies", []) or [])],
                            "connections": [
                                {
                                    "from": str(c.get("from", c.get("entity1", ""))),
                                    "to": str(c.get("to", c.get("entity2", ""))),
                                    "type": str(c.get("type", c.get("relationship", "")))
                                }
                                for c in (updated_state.get("connections", []) or [])
                                if (c.get("from") or c.get("entity1")) and (c.get("to") or c.get("entity2"))  # Filter out empty connections
                            ],
                            "costs": {
                                "tavily_searches": int(self.costs.get("tavily_searches", 0)),
                                "free_extractions": int(self.costs.get("free_extracts", 0)),
                                "tavily_extractions": int(self.costs.get("tavily_extracts", 0)),
                                "llm_calls": int(self.costs.get("llm_calls", 0)),
                                "total_cost": float(self.costs.get("total_cost", 0))
                            },
                            "cache": {
                                "seen_urls": len(updated_state.get("seen_urls", [])),
                                "previous_queries": len(updated_state.get("previous_queries", [])),
                                "documents_in_rag": int(updated_state.get("documents_in_rag", 0))
                            }
                        }
                        
                        await self.event_callback('state_update', frontend_state)
                        log(f"   📊 State update sent via WebSocket")
                    except Exception as e:
                        log(f"   ⚠️  State update WebSocket push failed: {e}")
                        import traceback
                        traceback.print_exc()
            except Exception as e:
                log(f"   ⚠️  Failed to save iteration: {e}")
                # Don't print full traceback, just continue
        else:
            log(f"   ⚠️  No investigation_id found, skipping incremental save")
        
        return updated_state
    
    def _update_hypotheses(self, existing: List[Dict], updates: List[Dict]) -> List[Dict]:
        """
        Update hypothesis status based on new evidence
        
        Rules:
        - confidence > 0.8: status = "confirmed"
        - confidence < 0.3: status = "refuted"
        - else: status = "exploring"
        - When a hypothesis is confirmed/refuted, automatically activate next "exploring" hypothesis
        """
        if not existing:
            return existing
        
        # Apply updates
        updated = existing.copy()
        for update in updates:
            hyp_id = update.get("id")
            for hyp in updated:
                if hyp.get("id") == hyp_id:
                    # Update confidence
                    if "confidence" in update:
                        hyp["confidence"] = update["confidence"]
                    
                    # Update status based on confidence
                    confidence = hyp.get("confidence", 0.5)
                    if confidence >= 0.8:
                        hyp["status"] = "confirmed"
                        log(f"      ✅ Hypothesis {hyp_id} CONFIRMED (confidence: {confidence:.2f})")
                    elif confidence <= 0.3:
                        hyp["status"] = "refuted"
                        log(f"      ❌ Hypothesis {hyp_id} REFUTED (confidence: {confidence:.2f})")
                    else:
                        hyp["status"] = "exploring"
                    
                    # Add evidence
                    if "evidence" in update:
                        if "evidence" not in hyp:
                            hyp["evidence"] = []
                        hyp["evidence"].append(update["evidence"])
                    
                    break
        
        # Auto-activate next hypothesis if current one is complete
        active_count = sum(1 for h in updated if h.get("status") == "exploring")
        if active_count == 0:
            # Find first hypothesis that's neither confirmed nor refuted
            for hyp in updated:
                if hyp.get("status") not in ["confirmed", "refuted"]:
                    hyp["status"] = "exploring"
                    log(f"      🎯 Activated next hypothesis: {hyp.get('id')} - {hyp.get('statement')}")
                    break
        
        return updated
    
    async def _synthesizer_node(self, state: HypothesisState) -> HypothesisState:
        """
        Generate final investigative report with NOVEL insights
        """
        log(f"\n{'='*80}")
        log(f"📝 SYNTHESIZER - Final Report")
        log(f"{'='*80}")
        
        # Collect all URLs from extracted content
        all_urls = []
        extracted_articles = state.get("extracted_content", [])
        for article in extracted_articles:
            url = article.get("url", "")
            if url:
                all_urls.append(url)
        
        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(all_urls))
        
        synthesis_prompt = f"""Write a comprehensive investigative journalism report.

INVESTIGATION: {state['initial_query']}
ITERATIONS: {state['iteration']}

KNOWLEDGE GATHERED:
- Entities: {len(state['entities'])}
- Facts: {len(state['facts'])}
- Connections: {len(state['connections'])}
- Hypotheses: {len(state['hypotheses'])}
- Anomalies: {len(state['anomalies'])}

KEY ENTITIES:
{json.dumps(dict(list(state['entities'].items())[:20]), indent=2)}

FACTS:
{json.dumps(state['facts'][:50], indent=2)}

CONNECTIONS:
{json.dumps(state['connections'][:20], indent=2)}

HYPOTHESES:
{json.dumps(state['hypotheses'], indent=2)}

ANOMALIES & SUSPICIOUS PATTERNS:
{json.dumps(state['anomalies'], indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVESTIGATIVE JOURNALISM REPORT STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write a professional investigative report following this EXACT structure:

## **HEADLINE**
[Clear, compelling headline]

---

## **EXECUTIVE SUMMARY**
[2-3 paragraph overview of the event and what happened]

---

## **KEY FINDINGS**
[Numbered list of the most important discoveries from the investigation]

1. **[Finding Title]**: [Detailed finding with specific facts, numbers, names]
2. **[Finding Title]**: [Detailed finding with specific facts, numbers, names]
3. **[Finding Title]**: [Detailed finding with specific facts, numbers, names]
[Continue with all major findings]

---

## **ANALYSIS & INSIGHTS**

### **Novel Insights**
[What did this investigation uncover that others missed?]

### **Alternative Hypotheses**
[Different possible explanations with supporting evidence]

### **Network of Actors**
[Who's involved and how they're connected]

### **Suspicious Patterns & Anomalies**
[What doesn't add up? What's missing?]

### **Timeline Analysis**
[What does the sequence of events reveal?]

---

## **UNANSWERED QUESTIONS**
[Critical questions that remain unresolved]

---

## **SOURCES**

This investigation analyzed the following sources:

{chr(10).join([f"{i}. {url}" for i, url in enumerate(unique_urls, 1)])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT GUIDELINES:
1. Start with EXECUTIVE SUMMARY explaining what happened
2. Then list KEY FINDINGS with specific evidence (names, numbers, quotes)
3. Then provide ANALYSIS & INSIGHTS with your conclusions
4. DO NOT add a SOURCES section - it's already included above
5. Use specific facts from the data above - cite entity names, numbers, dates
6. Be factual and evidence-based
7. Highlight what's novel or overlooked

Write the complete report now (without the SOURCES section, it's already added above).
"""
        
        response = await self.llm.ainvoke([SystemMessage(content=synthesis_prompt)])
        
        # Track LLM cost
        self.costs["llm_calls"] += 1
        self.costs["total_cost"] += (self.COST_GPT4O_INPUT + self.COST_GPT4O_OUTPUT)
        
        # Get report content (sources already embedded in prompt template)
        report_content = response.content
        
        log(f"\n{'='*80}")
        log(f"📄 FINAL REPORT")
        log(f"{'='*80}\n")
        log(report_content)
        log(f"\n{'='*80}\n")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SEND ARTICLE AS ARTIFACT (before other artifacts)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                investigation_id = state.get("investigation_id", "unknown")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                await self.event_callback('artifact', {
                    'artifact_id': f"article_{investigation_id}_{timestamp}",
                    'type': 'article',
                    'name': 'Investigation Report',
                    'article_text': report_content,
                    'timestamp': datetime.now().isoformat()
                })
                log(f"   ✅ Sent article artifact to frontend")
            except Exception as e:
                log(f"   ⚠️  Failed to send article artifact: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # GENERATE ARTIFACTS (Entity Network, Timeline, Evidence Chain)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Import artifact generator
        try:
            from tools.artifact_generator import generate_all_artifacts
            
            # Generate all 3 artifacts
            artifacts = await generate_all_artifacts(state, output_dir="artifacts")
            
            # Debug: Check callback availability
            has_attr = hasattr(self, 'event_callback')
            has_callback = self.event_callback if has_attr else None
            log(f"   🐛 DEBUG: hasattr(event_callback)={has_attr}, callback={has_callback is not None}, artifacts={len(artifacts) if artifacts else 0}")
            
            # Send artifacts to frontend (with fallback for local serving)
            if hasattr(self, 'event_callback') and self.event_callback and artifacts:
                log(f"   📦 Sending {len(artifacts)} artifacts to frontend...")
                
                # Try S3 upload first, fallback to local serving
                try:
                    import sys
                    from pathlib import Path
                    services_dir = Path(__file__).parent.parent.parent.parent / 'services'
                    if str(services_dir) not in sys.path:
                        sys.path.insert(0, str(services_dir))
                    
                    from s3_service import s3_service
                    use_s3 = s3_service is not None
                except Exception as e:
                    log(f"   ℹ️  S3 not available, using local serving: {e}")
                    use_s3 = False
                
                for artifact in artifacts:
                    try:
                        investigation_id = state.get("investigation_id", "unknown")
                        artifact_url = None
                        
                        # Try S3 upload if available
                        if use_s3:
                            try:
                                s3_key = await s3_service.upload_artifact(
                                    local_file_path=artifact["path"],
                                    artifact_id=investigation_id,
                                    artifact_type=artifact["name"].lower().replace(" ", "_")
                                )
                                
                                if s3_key:
                                    artifact_url = s3_service.get_presigned_url(s3_key, expiration=86400)
                                    log(f"   ✅ Uploaded to S3: {artifact['name']}")
                            except Exception as s3_error:
                                log(f"   ⚠️  S3 upload failed, using local: {s3_error}")
                                use_s3 = False  # Switch to local for remaining artifacts
                        
                        # Fallback: Use local file serving
                        if not artifact_url:
                            # Get relative path from backend root
                            from pathlib import Path
                            backend_root = Path(__file__).parent.parent.parent.parent
                            artifact_path = Path(artifact["path"])
                            
                            # Try to make relative to backend root
                            try:
                                rel_path = artifact_path.relative_to(backend_root)
                                artifact_url = f"http://localhost:8000/artifacts/{rel_path}"
                            except ValueError:
                                # If not relative, use absolute path construction
                                artifact_url = f"http://localhost:8000/artifacts/investigative_journalist/{artifact_path.name}"
                            
                            log(f"   📁 Using local file: {artifact['name']}")
                        
                        # Send artifact event to frontend
                        await self.event_callback('artifact', {
                            'type': artifact['type'],
                            'name': artifact['name'],
                            'url': artifact_url,
                            'artifact_id': investigation_id,
                            'timestamp': datetime.now().isoformat()
                        })
                        log(f"   ✅ Sent artifact to frontend: {artifact['name']}")
                        
                    except Exception as e:
                        log(f"   ❌ Failed to send artifact '{artifact['name']}': {e}")
                        import traceback
                        traceback.print_exc()
                        # Continue with other artifacts
                        
        except Exception as e:
            log(f"   ❌ Failed to generate artifacts: {e}")
            import traceback
            traceback.print_exc()
        
        return {
            **state,
            "final_report": report_content
        }
    
    def _parse_json(self, content: str) -> Dict:
        """Parse JSON from LLM response"""
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except Exception as e:
            log(f"   ⚠️  JSON parse error: {e}")
            return {}
    
    async def investigate(self, query: str, investigation_id: str = None, user_instruction: str = None, initial_state: Dict = None, event_callback: callable = None) -> Dict:
        """
        Run the investigation
        
        Args:
            query: Investigation query
            investigation_id: Optional investigation ID for incremental MongoDB saves
            user_instruction: Optional user instruction (e.g., "query local rag")
            initial_state: Optional loaded state to resume from
            event_callback: Optional async function for real-time events
        """
        # Store callback for use in nodes
        self.event_callback = event_callback
        
        # 🐛 FIX: Generate investigation_id if not provided (for fresh investigations)
        if not investigation_id:
            import hashlib
            import time
            investigation_id = f"inv_{hashlib.md5(f'{query}{time.time()}'.encode()).hexdigest()[:12]}"
            log(f"   🆕 Generated investigation_id: {investigation_id}")
        
        log(f"\n{'#'*80}")
        log(f"🔬 LEAN INVESTIGATOR")
        log(f"{'#'*80}")
        log(f"Query: {query}")
        log(f"Max Iterations: {self.max_iterations}")
        log(f"Investigation ID: {investigation_id} (incremental saves enabled)")
        if user_instruction:
            log(f"User Instruction: {user_instruction}")
        if event_callback:
            log(f"Event Callback: Enabled (real-time WebSocket events)")
        log(f"{'#'*80}\n")
        
        # Use loaded state or create fresh
        if initial_state:
            log(f"   ✅ Resuming from loaded state (iteration {initial_state.get('iteration')})")
            # Update with current parameters
            log(f"   🐛 DEBUG - Before setting: user_instruction in state = {initial_state.get('user_instruction')}")
            log(f"   🐛 DEBUG - user_instruction param = {user_instruction}")
            initial_state['user_instruction'] = user_instruction
            if user_instruction:
                log(f"   🔄 INJECTING user_instruction into state: {user_instruction[:80]}...")
            log(f"   🐛 DEBUG - After setting: user_instruction in state = {initial_state.get('user_instruction')}")
            state_to_use = initial_state
        else:
            log(f"   🆕 Starting fresh investigation")
            state_to_use: HypothesisState = {
                "initial_query": query,
                "iteration": 1,
                "max_iterations": self.max_iterations,
                "investigation_id": investigation_id,  # Store for incremental saves
                "user_instruction": user_instruction,  # User's latest instruction
                
                "entities": {},
                "facts": [],
                "hypotheses": [],
                "evidence": [],
                "connections": [],
                "anomalies": [],
                "questions": [],  # Question tree for UI
                
                "seen_urls": [],
                "extracted_cache": {},
                "previous_queries": [],
                "documents_in_rag": 0,  # ← FIX: Initialize RAG counter
                
                # Working variables
                "search_results": [],  # ⭐ CRITICAL: Initialize
                "extracted_content": [],  # ⭐ CRITICAL: Initialize
                
                "next_action": "search",
                "search_query": None,
                "investigation_complete": False,
                "final_report": None
            }
        
        final_state = await self.graph.ainvoke(
            state_to_use,
            config={"recursion_limit": self.max_iterations * 5}  # Increased from 3 to 5
        )
        
        log(f"\n{'#'*80}")
        log(f"✅ INVESTIGATION COMPLETE")
        log(f"{'#'*80}")
        log(f"Total iterations: {final_state['iteration']}")
        log(f"Entities discovered: {len(final_state['entities'])}")
        log(f"Facts collected: {len(final_state['facts'])}")
        log(f"Connections mapped: {len(final_state['connections'])}")
        log(f"Anomalies found: {len(final_state['anomalies'])}")
        log(f"{'#'*80}")
        log(f"\n💰 COST BREAKDOWN:")
        log(f"{'='*80}")
        log(f"Tavily Searches: {self.costs['tavily_searches']} × ${self.COST_TAVILY_SEARCH} = ${self.costs['tavily_searches'] * self.COST_TAVILY_SEARCH:.3f}")
        log(f"Tavily Extracts: {self.costs['tavily_extracts']} × ${self.COST_TAVILY_EXTRACT} = ${self.costs['tavily_extracts'] * self.COST_TAVILY_EXTRACT:.3f}")
        log(f"Free Extracts: {self.costs['free_extracts']} × $0.00 = $0.00 ✅")
        log(f"Cached Extracts: {self.costs['cached_extracts']} × $0.00 = $0.00 ✅")
        log(f"LLM Calls (GPT-4o): {self.costs['llm_calls']} × ${self.COST_GPT4O_INPUT + self.COST_GPT4O_OUTPUT:.4f} = ${self.costs['llm_calls'] * (self.COST_GPT4O_INPUT + self.COST_GPT4O_OUTPUT):.3f}")
        log(f"{'='*80}")
        log(f"TOTAL COST: ${self.costs['total_cost']:.3f}")
        log(f"{'='*80}")
        
        # Calculate savings
        if_all_tavily = (self.costs['free_extracts'] + self.costs['cached_extracts']) * self.COST_TAVILY_EXTRACT
        log(f"\n💡 SAVINGS:")
        log(f"If all extracts used Tavily: ${if_all_tavily:.3f}")
        log(f"Actual cost: ${self.costs['tavily_extracts'] * self.COST_TAVILY_EXTRACT:.3f}")
        log(f"Saved: ${if_all_tavily - (self.costs['tavily_extracts'] * self.COST_TAVILY_EXTRACT):.3f} ({100 * (1 - self.costs['tavily_extracts'] / max(self.costs['free_extracts'] + self.costs['cached_extracts'] + self.costs['tavily_extracts'], 1)):.0f}% reduction)")
        log(f"{'#'*80}\n")
        
        return {
            "query": query,
            "iterations": final_state["iteration"],
            "entities": final_state["entities"],
            "facts": final_state["facts"],
            "connections": final_state["connections"],
            "anomalies": final_state["anomalies"],
            "hypotheses": final_state["hypotheses"],
            "questions": final_state.get("questions", []),  # Add questions
            "report": final_state.get("final_report")
        }


# CLI interface
if __name__ == "__main__":
    async def main():
        query = input("Enter investigation query: ").strip() or "investigate root cause of recent deaths related to cough syrups in India"
        max_iter = input("Max iterations (default 100): ").strip()
        max_iter = int(max_iter) if max_iter.isdigit() else 100
        
        investigator = LeanInvestigator(max_iterations=max_iter)
        result = await investigator.investigate(query)
        
        print("\n" + "="*80)
        print("INVESTIGATION SUMMARY:")
        print("="*80)
        print(f"Entities discovered: {len(result['entities'])}")
        print(f"Facts collected: {len(result['facts'])}")
        print(f"Connections mapped: {len(result['connections'])}")
        print(f"Anomalies found: {len(result['anomalies'])}")
    
    asyncio.run(main())

