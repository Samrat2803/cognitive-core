"""
Deep Investigative Reporter Agent

A persistent investigative agent that follows entities recursively, traces funding,
identifies hidden connections, and generates visual artifacts (causal diagrams and network graphs).
"""

from langgraph.graph import StateGraph, END
from .state import InvestigativeState
from .nodes import (
    query_analyzer,
    event_mapper,
    entity_investigator,
    strategic_intelligence_analyzer,
    funding_tracer,
    report_generator
)


def should_continue_investigating(state: InvestigativeState) -> str:
    """
    Decision point: Continue investigating or generate report?
    
    Stop conditions:
    1. Reached max depth
    2. High overall confidence
    3. No more entities to investigate
    4. Manual stop signal
    """
    # Manual stop
    if not state.get("should_continue", True):
        return "generate_report"
    
    # Reached max depth
    if state.get("investigation_depth", 0) >= state.get("max_depth", 5):
        print("\n⚠️  Reached maximum investigation depth")
        return "generate_report"
    
    # No more entities to investigate
    if len(state.get("entity_queue", [])) == 0:
        print("\n✓ No more entities to investigate")
        return "generate_report"
    
    # High confidence achieved
    if state.get("overall_confidence", 0) >= 0.85:
        print("\n✓ High confidence achieved")
        return "generate_report"
    
    # Continue investigating
    return "continue"


def build_investigation_graph() -> StateGraph:
    """
    Build the investigation workflow graph.
    
    Flow:
    1. Parse query
    2. Map timeline
    3. LOOP:
       - Strategic Intelligence Analyzer (THE BRAIN)
       - Investigate entities
       - Trace funding
       - Back to Strategic Analyzer
    4. Generate report
    """
    workflow = StateGraph(InvestigativeState)
    
    # Add nodes
    workflow.add_node("query_analyzer", query_analyzer)
    workflow.add_node("event_mapper", event_mapper)
    workflow.add_node("strategic_intelligence_analyzer", strategic_intelligence_analyzer)
    workflow.add_node("entity_investigator", entity_investigator)
    workflow.add_node("funding_tracer", funding_tracer)
    workflow.add_node("report_generator", report_generator)
    
    # Entry point
    workflow.set_entry_point("query_analyzer")
    
    # Initial discovery flow
    workflow.add_edge("query_analyzer", "event_mapper")
    
    # First strategic analysis
    workflow.add_edge("event_mapper", "strategic_intelligence_analyzer")
    
    # INVESTIGATION LOOP
    # Strategic Analyzer decides what to investigate next
    workflow.add_conditional_edges(
        "strategic_intelligence_analyzer",
        should_continue_investigating,
        {
            "continue": "entity_investigator",
            "generate_report": "report_generator"
        }
    )
    
    # After investigating entity, trace funding
    workflow.add_edge("entity_investigator", "funding_tracer")
    
    # After tracing funding, go back to Strategic Analyzer (THE BRAIN)
    # This creates the recursive intelligence loop
    workflow.add_edge("funding_tracer", "strategic_intelligence_analyzer")
    
    # End after report
    workflow.add_edge("report_generator", END)
    
    return workflow.compile()


# Create compiled graph
investigation_agent = build_investigation_graph()


async def investigate(query: str, cutoff_date: str = None, max_depth: int = 5) -> dict:
    """
    Run deep investigation on a query.
    
    Args:
        query: Investigation question (e.g., "Why did Nepal revolution happen?")
        cutoff_date: Only use information before this date
        max_depth: Maximum investigation depth (default: 5)
    
    Returns:
        dict with artifacts (network graph, causal diagram, HTML report)
    """
    initial_state = {
        "query": query,
        "cutoff_date": cutoff_date,
        "max_depth": max_depth,
        "messages": []
    }
    
    print("\n" + "="*80)
    print(f"🕵️  DEEP INVESTIGATIVE REPORTER")
    print(f"Query: {query}")
    print(f"Max Depth: {max_depth}")
    print("="*80)
    
    # Run investigation
    final_state = await investigation_agent.ainvoke(initial_state)
    
    print("\n" + "="*80)
    print("✅ INVESTIGATION COMPLETE")
    print("="*80)
    
    return {
        "artifacts": final_state.get("artifacts", []),
        "summary": final_state.get("artifacts", [])[-1]["data"] if final_state.get("artifacts") else {},
        "investigation_depth": final_state.get("investigation_depth", 0),
        "total_entities": len(final_state.get("entities", {})),
        "funding_network": final_state.get("funding_network", {}),
        "hypotheses": final_state.get("investigation_hypotheses", [])
    }


# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        result = await investigate(
            query="Why did Nepal revolution happen in 2025?",
            max_depth=3
        )
        
        print("\n📊 ARTIFACTS GENERATED:")
        for artifact in result["artifacts"]:
            print(f"  - {artifact['title']} ({artifact['format']})")
        
        print(f"\n✓ Investigated {result['total_entities']} entities")
        print(f"✓ Investigation depth: {result['investigation_depth']}")
        print(f"✓ Funding network size: {len(result['funding_network'])}")
    
    asyncio.run(test())


