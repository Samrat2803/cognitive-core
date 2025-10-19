"""
Lean Investigator Agent
Optimized for 100+ iterations at minimal cost

Cost-saving strategies:
1. Tavily search only (no extract)
2. Free text extraction using Python libraries
3. Hypothesis-driven searching (not every iteration)
4. Smart caching
5. Incremental search frequency
"""

import asyncio
import sys
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, TypedDict
from pathlib import Path

import requests
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
        
        # Cost tracking
        self.costs = {
            "tavily_searches": 0,
            "tavily_extracts": 0,
            "free_extracts": 0,
            "cached_extracts": 0,
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
        workflow.add_edge("analyzer", "strategist")
        workflow.add_edge("synthesizer", END)
        
        # Compile without checkpointer (we use MongoDB directly)
        return workflow.compile()
    
    def _route_from_strategist(self, state: HypothesisState) -> str:
        """Route based on strategy decision"""
        if state["iteration"] > state["max_iterations"]:
            return "complete"
        if state.get("investigation_complete"):
            return "complete"
        
        action = state.get("next_action", "search")
        
        # Handle analyze_only (skip search)
        if action == "analyze_only":
            return "analyze"
        
        # Handle LOCAL RAG query
        if action == "query_local_rag":
            log(f"   🔀 Router: query_local_rag → local_rag_query node")
            return "query_local_rag"
        
        # Default: search
        log(f"   🔀 Router: {action} → searcher node")
        return "search"
    
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
        
        # Emit iteration start event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('log', {
                    "message": f"🔄 Iteration {iteration}/{state['max_iterations']}"
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        # Initialize questions list
        questions = state.get("questions", [])
        hypotheses = state.get("hypotheses", [])
        
        # Determine current phase
        if len(hypotheses) == 0:
            phase = "general_investigation"
            log("   📍 PHASE: General Investigation (no hypotheses yet)")
        else:
            # Find active hypothesis (status = "exploring")
            active_hypothesis = next((h for h in hypotheses if h.get("status") == "exploring"), None)
            
            if active_hypothesis:
                phase = "testing_hypothesis"
                log(f"   📍 PHASE: Testing Hypothesis {active_hypothesis.get('id')}")
                log(f"   📝 Hypothesis: {active_hypothesis.get('statement', 'N/A')}")
                log(f"   🎯 Confidence: {active_hypothesis.get('confidence', 0.0):.2f}")
            else:
                # All hypotheses are confirmed/refuted, generate new ones or complete
                completed_count = sum(1 for h in hypotheses if h.get("status") in ["confirmed", "refuted"])
                if completed_count == len(hypotheses) and iteration < state["max_iterations"] - 5:
                    phase = "generate_new_hypotheses"
                    log(f"   📍 PHASE: All {len(hypotheses)} hypotheses tested, need new ones")
                else:
                    phase = "complete"
                    log(f"   📍 PHASE: Investigation Complete ({completed_count}/{len(hypotheses)} hypotheses tested)")
        
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
            phase_instruction = """
**CURRENT PHASE: GENERAL INVESTIGATION**
Your goal: Conduct broad exploration to understand the landscape and identify potential hypotheses.
Focus on: Who, what, when, where, why questions to build foundational knowledge.
"""
        elif phase == "testing_hypothesis":
            active_hyp = next((h for h in hypotheses if h.get("status") == "exploring"), None)
            phase_instruction = f"""
**CURRENT PHASE: TESTING HYPOTHESIS**
Active Hypothesis: {active_hyp.get('statement', 'N/A')} (ID: {active_hyp.get('id', 'N/A')})
Current Confidence: {active_hyp.get('confidence', 0.0):.2f}
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
        user_instruction = state.get('user_instruction', '')
        force_local_rag = user_instruction and ('local' in user_instruction.lower() or 'knowledge base' in user_instruction.lower())
        
        # Log LOCAL RAG status
        log(f"\n{'─'*80}")
        log(f"💾 LOCAL RAG STATUS:")
        log(f"   Documents in RAG: {documents_in_rag}")
        log(f"   Has LOCAL RAG: {has_local_rag} (iteration >= 2 and docs > 0)")
        log(f"   User instruction: {user_instruction[:80] if user_instruction else 'None'}...")
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
        
        strategy_prompt = f"""You are an investigative strategist finding NOVEL angles others miss.

INVESTIGATION: {state['initial_query']}
ITERATION: {iteration}/{state['max_iterations']}
CURRENT DATE: {current_date}

{phase_instruction}

KNOWLEDGE GATHERED SO FAR:
- Entities identified: {len(state['entities'])}
- Facts collected: {len(state['facts'])}
- Hypotheses: {len(state['hypotheses'])}
- Connections mapped: {len(state['connections'])}
- Anomalies found: {len(state['anomalies'])}
{f"- Documents in LOCAL RAG: {documents_in_rag}" if has_local_rag else ""}

EXISTING HYPOTHESES:
{json.dumps(state['hypotheses'], indent=2)}

RECENT FACTS (Last 5):
{json.dumps(state['facts'][-5:], indent=2)}

KEY ANOMALIES (Top 5):
{json.dumps(state['anomalies'][-5:], indent=2)}

PREVIOUS SEARCH QUERIES (MUST NOT REPEAT):
{json.dumps(state.get('previous_queries', []), indent=2)}
{local_rag_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR MISSION: Find what others missed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 CRITICAL: Your query MUST be COMPLETELY DIFFERENT from all previous queries above!

CRITICAL THINKING FRAMEWORKS:

1. **The Dog That Didn't Bark**: What SHOULD have happened but didn't?
2. **Cui Bono**: Who benefits from the current narrative?
3. **Follow the Money**: Financial flows, donations, contracts
4. **Power Networks**: Who appointed whom? Conflicts of interest?
5. **Temporal Anomalies**: Why NOW? What changed 6 months ago?
6. **Comparative Baseline**: How does this compare to similar cases?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your task:
1. Review existing knowledge and hypotheses
2. Identify which hypothesis needs testing
3. Formulate a specific QUESTION to test that hypothesis
4. {"Decide: Query LOCAL RAG or search fresh web content" if has_local_rag else "Generate ONE specific search query to answer that question"}
5. Explain what NOVEL insight you're seeking

Return JSON:
{{
  "decision": {'query_local_rag OR search OR complete' if has_local_rag else 'search OR complete'},
  "hypothesis_id": "ID of hypothesis being tested (e.g., 'h1', 'h2') or 'general' for initial exploration",
  "question": "Specific question you're trying to answer (e.g., 'Who are the key people involved?', 'What regulatory actions were taken?')",
  {'rag_query OR search_query' if has_local_rag else 'search_query'}: "Natural language question for LOCAL RAG" {'OR Keywords for Tavily search' if has_local_rag else '(keywords, not questions)'},
  "hypothesis_being_tested": "Which hypothesis are you testing?",
  "novel_angle": "What new insight are you seeking that others missed?",
  "expected_evidence": "What would prove/disprove your hypothesis?",
  "completion_reason": "ONLY if decision='complete': Why investigation is complete"
}}

{"💡 If you choose 'query_local_rag', provide 'rag_query' with a natural language question." if has_local_rag else ""}
{"💡 If you choose 'search', provide 'search_query' with keywords for Tavily." if has_local_rag else ""}

Be specific. Be surgical. Find what others missed.
"""
        
        response = await self.llm.ainvoke([SystemMessage(content=strategy_prompt)])
        decision = self._parse_json(response.content)
        
        # Track LLM cost
        self.costs["llm_calls"] += 1
        self.costs["total_cost"] += (self.COST_GPT4O_INPUT + self.COST_GPT4O_OUTPUT)
        
        # ⭐ CRITICAL FIX: FORCE INITIAL SEARCH
        searches_done = len(state.get("previous_queries", []))
        if searches_done == 0:
            log("   🔒 FORCING INITIAL SEARCH (no searches yet)")
            decision["decision"] = "search"
            if not decision.get("search_query"):
                decision["search_query"] = state["initial_query"]
        
        # ⭐ CRITICAL FIX: PREVENT PREMATURE COMPLETION
        if decision.get("decision") == "complete":
            entities = len(state.get("entities", {}))
            facts = len(state.get("facts", []))
            if entities < 5 or facts < 10:
                log(f"   ⚠️  Rejecting premature completion (entities={entities}, facts={facts})")
                log(f"   🔄 Forcing continued investigation")
                decision["decision"] = "search"
                # Generate a fallback query
                if not decision.get("search_query"):
                    decision["search_query"] = f"{state['initial_query']} detailed investigation"
        
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
        if decision.get("question") and decision.get("decision") == "search":
            question_text = decision["question"]
            hypothesis_id = decision.get("hypothesis_id", "general")
            
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
        
        # Determine action based on decision
        action_type = decision.get("decision", "search")
        
        if action_type == "query_local_rag":
            log(f"   📝 Next action: QUERY LOCAL RAG")
            return {
                **state,
                "next_action": "query_local_rag",
                "rag_query": decision.get("rag_query", decision.get("search_query", "")),
                "questions": questions,
                "iteration": iteration + 1
            }
        else:
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
        Execute ONE targeted Tavily search
        """
        query = state.get("search_query", "")
        
        log(f"\n{'='*80}")
        log(f"🔍 SEARCHER")
        log(f"{'='*80}")
        log(f"Query: {query}")
        
        # Emit search event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('log', {
                    "message": f"🔍 Searching: {query}"
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
        
        # Emit articles found event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('log', {
                    "message": f"📰 Found {len(new_articles)} new articles to analyze"
                })
            except Exception as e:
                log(f"   ⚠️  WebSocket push failed: {e}")
        
        return {
            **state,
            "search_results": new_articles,
            "seen_urls": state["seen_urls"] + [a.get("url") for a in new_articles]
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
        
        # Emit extraction start event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('log', {
                    "message": f"📖 Extracting content from {min(len(articles), 2)} articles..."
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
            content = self._extract_free(url)
            
            if content and len(content) > 500:
                log(f"   [{i}] ✅ Free extraction: {len(content)} chars (Cost: $0.00)")
                self.costs["free_extracts"] += 1
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
                    tavily_result = await self.tavily.tavily_extract(urls=[url])
                    
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
        
        return {
            **state,
            "extracted_content": extracted_content
        }
    
    def _extract_free(self, url: str) -> Optional[str]:
        """
        Try multiple free extraction methods
        """
        try:
            # Method 1: Jina AI Reader (most reliable, free)
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            try:
                jina_response = requests.get(jina_url, headers=headers, timeout=15)
                if jina_response.status_code == 200 and len(jina_response.text) > 500:
                    log(f"      ✅ Jina AI success")
                    return jina_response.text
            except Exception as e:
                log(f"      ⚠️  Jina AI failed: {str(e)[:30]}")
            
            # Method 2: Trafilatura (good for news articles)
            response = requests.get(url, headers=headers, timeout=10)
            
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
        
        # Emit analysis start event
        if hasattr(self, 'event_callback') and self.event_callback:
            try:
                await self.event_callback('log', {
                    "message": f"🔬 Analyzing content for insights..."
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

EXISTING ENTITIES:
{json.dumps(list(state['entities'].keys())[:20], indent=2)}

ARTICLES:
{articles_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR ANALYSIS MISSION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **Extract NEW entities** (people, orgs, locations not yet identified)
2. **Test hypotheses**: Does this evidence support or refute existing hypotheses?
3. **Find connections**: Financial, political, personal relationships
4. **Detect anomalies**: What's suspicious? What's missing?
5. **Generate facts**: Specific, verifiable claims

CRITICAL FRAMEWORKS:
- **Temporal anomalies**: When did things happen? Any suspicious timing?
- **Financial anomalies**: Money flows, unusual transactions
- **Incentive misalignments**: Who benefits? Who's protecting whom?
- **Conspicuous absences**: What SHOULD be here but isn't?

Return JSON:
{{
  "new_entities": [
    {{"name": "Entity name", "type": "person|org|location", "role": "Brief role", "significance": "Why important"}}
  ],
  "new_facts": ["Specific fact 1", "Specific fact 2"],
  "connections": [
    {{"entity1": "A", "entity2": "B", "relationship": "donated/appointed/owns", "evidence": "From article"}}
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
        
        # Handle new hypotheses from analyzer
        existing_hypotheses = state["hypotheses"].copy()
        new_hypotheses_from_analysis = analysis.get("new_hypotheses", [])
        
        # Add IDs to new hypotheses if not present
        for hyp in new_hypotheses_from_analysis:
            if "id" not in hyp:
                hyp["id"] = f"h{len(existing_hypotheses) + 1}"
            if "status" not in hyp:
                hyp["status"] = "exploring"
            if "confidence" not in hyp:
                hyp["confidence"] = 0.5
            if "evidence" not in hyp:
                hyp["evidence"] = []
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
            "questions": state.get("questions", []),  # Preserve questions from strategist
            "investigation_id": state.get("investigation_id")  # Explicitly preserve investigation_id
        }
        
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT GUIDELINES:
1. Start with EXECUTIVE SUMMARY explaining what happened
2. Then list KEY FINDINGS with specific evidence (names, numbers, quotes)
3. Then provide ANALYSIS & INSIGHTS with your conclusions
4. Include all source URLs at the end
5. Use specific facts from the data above - cite entity names, numbers, dates
6. Be factual and evidence-based
7. Highlight what's novel or overlooked

Write the complete report now.
"""
        
        response = await self.llm.ainvoke([SystemMessage(content=synthesis_prompt)])
        
        # Track LLM cost
        self.costs["llm_calls"] += 1
        self.costs["total_cost"] += (self.COST_GPT4O_INPUT + self.COST_GPT4O_OUTPUT)
        
        # Get report content
        report_content = response.content
        
        # FIX: Don't append sources if LLM already included them
        # Check if report already has a SOURCES section (multiple variations)
        has_sources = (
            "## **SOURCES**" in report_content or 
            "## SOURCES" in report_content or
            "**Sources:**" in report_content or
            "**SOURCES:**" in report_content
        )
        
        if not has_sources:
            # Only append if missing
            if unique_urls:
                report_content += "\n\n---\n\n## **SOURCES**\n\n"
                report_content += "This investigation analyzed the following sources:\n\n"
                for i, url in enumerate(unique_urls, 1):
                    report_content += f"{i}. {url}\n"
        else:
            log(f"   ✓ Report already contains SOURCES section, skipping append")
        
        log(f"\n{'='*80}")
        log(f"📄 FINAL REPORT")
        log(f"{'='*80}\n")
        log(report_content)
        log(f"\n{'='*80}\n")
        
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
        
        log(f"\n{'#'*80}")
        log(f"🔬 LEAN INVESTIGATOR")
        log(f"{'#'*80}")
        log(f"Query: {query}")
        log(f"Max Iterations: {self.max_iterations}")
        if investigation_id:
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
            initial_state['user_instruction'] = user_instruction
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

