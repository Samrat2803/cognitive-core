"""
General RAG Query Tool - Usable by ALL sub-agents

Supports:
- LOCAL RAG: Filter to specific thread_id (investigation, session, etc.)
- GLOBAL RAG: Search all accumulated knowledge

This tool wraps the MongoDB vector search functionality and makes it
available to any sub-agent that needs RAG capabilities.
"""

import sys
import os

# Import mongodb handler from cognitive crawler
crawler_tools_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../sub_agents/cognitive_crawler/tools')
)
crawler_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../sub_agents/cognitive_crawler')
)

# Add both paths for imports
if crawler_tools_dir not in sys.path:
    sys.path.insert(0, crawler_tools_dir)
if crawler_dir not in sys.path:
    sys.path.insert(0, crawler_dir)

from mongodb_handler import TenderMongoDBHandler

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


@observe(name="rag_query_tool")
async def query_rag(
    query: str,
    thread_id: Optional[str] = None,
    top_k: int = 10,
    min_score: float = 0.3,
    generate_answer: bool = True
) -> Dict[str, Any]:
    """
    Universal RAG query tool for all sub-agents
    
    This tool allows any sub-agent to query accumulated knowledge stored
    in the vector database. Supports both LOCAL (filtered) and GLOBAL search.
    
    Args:
        query: Natural language question
        thread_id: 
            - None = GLOBAL RAG (search all data)
            - "inv_abc123" = LOCAL RAG (filter to specific investigation)
            - "session_xyz" = LOCAL RAG (filter to specific crawler session)
        top_k: Number of results to return (default: 10)
        min_score: Minimum similarity score 0-1 (default: 0.3)
        generate_answer: Generate LLM answer from results (default: True)
        
    Returns:
        {
            "answer": "Generated answer based on context",
            "sources": ["url1", "url2", ...],  # Unique source URLs
            "chunks": [full chunk data with metadata],
            "scores": [0.95, 0.87, ...],  # Similarity scores
            "num_results": int,
            "mode": "local" | "global"
        }
    
    Examples:
        # Global RAG - search everything
        result = await query_rag("What regulatory failures have occurred?")
        
        # Local RAG - specific investigation only
        result = await query_rag(
            query="What have we learned about the company?",
            thread_id="inv_abc123"
        )
        
        # Without answer generation (just retrieval)
        result = await query_rag(
            query="Find documents about FDA",
            generate_answer=False
        )
    """
    
    mode = "local" if thread_id else "global"
    print(f"\n🔍 RAG Query ({mode.upper()}): {query}")
    if thread_id:
        print(f"   🔒 Filtering to: {thread_id[:30]}...")
    
    db = None
    try:
        db = TenderMongoDBHandler()
        
        # Vector search with optional thread_id filtering
        results = await db.search_vectors(
            query=query,
            thread_id=thread_id,
            top_k=top_k
        )
        
        # Filter by minimum score
        filtered = [r for r in results if r.get('score', 0) >= min_score]
        
        print(f"   ✅ Found {len(filtered)} results (min_score={min_score})")
        
        if len(filtered) == 0:
            return {
                "answer": "No relevant information found in the knowledge base.",
                "sources": [],
                "chunks": [],
                "scores": [],
                "num_results": 0,
                "mode": mode
            }
        
        # Extract unique sources
        sources = []
        for r in filtered:
            url = r.get('metadata', {}).get('url', 'Unknown')
            if url and url not in sources and url != 'Unknown':
                sources.append(url)
        
        # Generate answer if requested
        answer = ""
        if generate_answer:
            print(f"   🤖 Generating answer from top {min(len(filtered), 10)} results...")
            
            # Build context from top results
            context_parts = []
            for i, r in enumerate(filtered[:10], 1):
                url = r.get('metadata', {}).get('url', 'Unknown')
                content = r.get('content', '')[:800]  # Limit per chunk
                score = r.get('score', 0)
                
                context_parts.append(
                    f"[Source {i}] (Relevance: {score:.2f})\n"
                    f"URL: {url}\n"
                    f"Content: {content}\n"
                )
            
            context = "\n---\n\n".join(context_parts)
            
            # Generate with LLM
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            rag_prompt = f"""Answer the question based ONLY on the provided context.

Question: {query}

Context from knowledge base:
{context}

Instructions:
1. Answer using ONLY the information in the context above
2. Cite sources by mentioning [Source 1], [Source 2], etc.
3. If the context doesn't contain enough information, say so clearly
4. Be concise but comprehensive
5. If multiple sources say different things, mention both perspectives

Answer:"""
            
            response = await llm.ainvoke([
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": rag_prompt}
            ])
            
            answer = response.content
            print(f"   ✅ Answer generated ({len(answer)} chars)")
        
        return {
            "answer": answer,
            "sources": sources,
            "chunks": filtered,
            "scores": [r.get('score', 0) for r in filtered],
            "num_results": len(filtered),
            "mode": mode,
            "query": query
        }
        
    except Exception as e:
        print(f"   ❌ RAG query error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "answer": f"Error querying knowledge base: {str(e)}",
            "sources": [],
            "chunks": [],
            "scores": [],
            "num_results": 0,
            "mode": mode,
            "error": str(e)
        }
    
    finally:
        if db:
            db.close()


# Convenience wrappers for common use cases
async def query_local_rag(query: str, thread_id: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Convenience function: Query LOCAL RAG (specific thread only)
    
    Args:
        query: Question to ask
        thread_id: Investigation/session ID to filter to
        top_k: Number of results
        
    Returns:
        RAG query results filtered to specific thread
    """
    return await query_rag(query=query, thread_id=thread_id, top_k=top_k)


async def query_global_rag(query: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Convenience function: Query GLOBAL RAG (all data)
    
    Args:
        query: Question to ask
        top_k: Number of results
        
    Returns:
        RAG query results across all stored knowledge
    """
    return await query_rag(query=query, thread_id=None, top_k=top_k)


if __name__ == "__main__":
    """Test the RAG query tool"""
    import asyncio
    
    async def test():
        print("\n" + "="*80)
        print("🧪 TESTING GENERAL RAG QUERY TOOL")
        print("="*80)
        
        # Test global RAG
        print("\n📊 TEST 1: Global RAG (search all data)")
        result = await query_global_rag(
            query="What are the main topics in the knowledge base?",
            top_k=5
        )
        
        print("\n" + "="*80)
        print("📊 RESULTS")
        print("="*80)
        print(f"\n✅ Found {result['num_results']} relevant results")
        print(f"📝 Mode: {result['mode']}")
        print(f"\n💬 Answer:\n{result['answer']}")
        print(f"\n🔗 Sources ({len(result['sources'])}):")
        for i, source in enumerate(result['sources'], 1):
            print(f"   {i}. {source}")
        
        print("\n" + "="*80)
        print("✅ Test complete!")
        print("="*80)
    
    asyncio.run(test())

