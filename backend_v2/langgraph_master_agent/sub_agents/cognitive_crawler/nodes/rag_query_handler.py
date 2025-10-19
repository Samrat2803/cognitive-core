"""
RAG Query Handler Node - Uses general RAG tool
"""

import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.abspath(os.path.join(current_dir, '../../..', 'tools'))
crawler_dir = os.path.abspath(os.path.join(current_dir, '..'))

if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
if crawler_dir not in sys.path:
    sys.path.insert(0, crawler_dir)

from typing import Dict, Any
from state import CognitiveCrawlerState
from rag_query import query_rag
from config import TOP_K_RESULTS


async def rag_query_handler(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Handle RAG query using general RAG tool
    
    Uses thread_id from state for session-specific RAG.
    If thread_id is None or not provided, searches globally.
    """
    
    query = state["query"]
    thread_id = state.get("thread_id")  # Optional: filter to this session
    
    print(f"\n🔎 RAG Query Handler")
    print(f"   Query: {query}")
    print(f"   Thread ID: {thread_id if thread_id else 'None (global search)'}")
    
    state["execution_log"].append({
        "step": "rag_query_handler",
        "action": f"RAG search: {query[:50]}..."
    })
    
    try:
        # Use general RAG tool (supports both local and global)
        result = await query_rag(
            query=query,
            thread_id=thread_id,  # Will filter if provided, else searches globally
            top_k=TOP_K_RESULTS,
            min_score=0.3,
            generate_answer=True
        )
        
        # Convert to cognitive crawler state format
        relevant_tenders = []
        similarity_scores = []
        
        for chunk in result.get('chunks', []):
            relevant_tenders.append({
                'doc_id': chunk.get('doc_id', 'unknown'),
                'content': chunk.get('content', ''),
                'metadata': chunk.get('metadata', {}),
                'url': chunk.get('metadata', {}).get('url', 'N/A'),
                'domain': chunk.get('metadata', {}).get('domain', 'N/A'),
                'relevance_score': chunk.get('metadata', {}).get('relevance_score', 0),
                'score': chunk.get('score', 0)
            })
            similarity_scores.append(chunk.get('score', 0))
        
        state["relevant_tenders"] = relevant_tenders
        state["similarity_scores"] = similarity_scores
        state["answer"] = result.get('answer', '')
        state["sources"] = result.get('sources', [])
        
        print(f"   ✅ Found {len(relevant_tenders)} relevant documents")
        
        if relevant_tenders:
            print("\n   Top 3 matches:")
            for i, (tender, score) in enumerate(zip(relevant_tenders[:3], similarity_scores[:3]), 1):
                print(f"   {i}. {tender.get('url', 'Unknown')} (score: {score:.3f})")
                print(f"      Domain: {tender.get('domain', 'N/A')}")
        
    except Exception as e:
        error_msg = f"rag_query_handler error: {str(e)}"
        print(f"   ❌ {error_msg}")
        state["error_log"].append(error_msg)
        state["relevant_tenders"] = []
        state["similarity_scores"] = []
        state["answer"] = f"Error: {str(e)}"
        state["sources"] = []
    
    return state

