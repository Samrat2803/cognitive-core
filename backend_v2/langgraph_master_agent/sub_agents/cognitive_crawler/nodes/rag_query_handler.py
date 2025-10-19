"""
RAG Query Handler Node - Search tenders using vector similarity
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from state import CognitiveCrawlerState
from tools.mongodb_handler import TenderMongoDBHandler
from config import TOP_K_RESULTS


async def rag_query_handler(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Handle RAG query - search for relevant tenders using vector similarity
    
    ALWAYS searches globally across all data for simplicity
    """
    
    query = state["query"]
    
    print(f"\n🔎 RAG Query Handler: Searching for relevant content...")
    print(f"   Query: {query}")
    print(f"   Mode: GLOBAL (searching all crawled data)")
    
    state["execution_log"].append({
        "step": "rag_query_handler",
        "action": f"Global vector search for: {query[:50]}..."
    })
    
    try:
        db_handler = TenderMongoDBHandler()
        # thread_id is ignored - always searches globally
        results = await db_handler.search_vectors(query, thread_id=None, top_k=TOP_K_RESULTS)
        
        # Extract tenders and similarity scores
        relevant_tenders = []
        similarity_scores = []
        
        for result in results:
            # MongoDB Atlas Vector Search returns documents with scores
            relevant_tenders.append({
                'doc_id': result.get('doc_id'),
                'content': result.get('content'),
                'metadata': result.get('metadata', {}),
                'url': result.get('metadata', {}).get('url', 'N/A'),
                'domain': result.get('metadata', {}).get('domain', 'N/A'),
                'relevance_score': result.get('metadata', {}).get('relevance_score', 0),
                'score': result.get('score', 0)
            })
            similarity_scores.append(result.get('score', 0))
        
        state["relevant_tenders"] = relevant_tenders
        state["similarity_scores"] = similarity_scores
        
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
    
    return state

