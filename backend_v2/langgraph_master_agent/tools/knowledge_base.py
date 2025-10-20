"""
Knowledge Base RAG Tool with Adaptive Retrieval

Implements query-adaptive RAG strategies:
1. Needle in Haystack - Precise information retrieval
2. Exhaustive Search - Comprehensive context retrieval

This is a TOOL, not a sub-agent - it's a simple stateless function.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


async def classify_query_scope(query: str) -> str:
    """
    Classify query into retrieval strategy
    
    Returns:
        "needle" - Specific, precise information
        "exhaustive" - Broad, comprehensive questions
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = f"""Classify this query's retrieval scope:

Query: "{query}"

Choose ONE:
- "needle" - Specific question needing precise answer from few chunks (e.g., "What is X?", "When did Y?", "Who is Z?")
- "exhaustive" - Broad question needing comprehensive context from many full documents (e.g., "All regulations", "Explain everything about...", "Overview of...")

Return ONLY the word "needle" or "exhaustive" - nothing else."""
    
    response = await llm.ainvoke([{"role": "user", "content": prompt}])
    scope = response.content.strip().lower()
    
    if "exhaustive" in scope:
        return "exhaustive"
    else:
        return "needle"


def deduplicate_by_url(results: List[Dict]) -> List[Dict]:
    """
    Deduplicate results by URL, keeping highest scoring chunk per URL
    
    Args:
        results: List of search results with 'metadata.url' and 'score'
        
    Returns:
        Deduplicated results (one per unique URL)
    """
    url_to_best = {}
    
    for result in results:
        url = result.get('metadata', {}).get('url', 'unknown')
        score = result.get('score', 0)
        
        if url not in url_to_best or score > url_to_best[url]['score']:
            url_to_best[url] = result
    
    # Return in score-descending order
    return sorted(url_to_best.values(), key=lambda x: x.get('score', 0), reverse=True)


@observe(name="query_knowledge_base_tool")
async def query_knowledge_base(
    query: str, 
    top_k: int = 30,
    min_score: float = 0.3,
    generate_answer: bool = True,
    force_scope: str = None,  # Optional: "needle" or "exhaustive" to override classification
    progress_callback = None,  # Optional: callback for real-time progress updates
    stream_callback = None  # NEW: For streaming response tokens
) -> Dict[str, Any]:
    """
    Query the accumulated knowledge base using ADAPTIVE RAG
    
    Automatically selects retrieval strategy based on query:
    - Needle in Haystack: Precise, focused retrieval
    - Exhaustive Search: Broad, comprehensive retrieval
    
    Args:
        query: Natural language question
        top_k: Number of results to return (default 30)
        min_score: Minimum cosine similarity score (0-1)
        generate_answer: Whether to generate LLM answer (default: True)
        force_scope: Override automatic classification ("needle" or "exhaustive")
        
    Returns:
        {
            "answer": "LLM-generated answer" (if generate_answer=True),
            "sources": [list of source URLs],
            "chunks": [list of relevant content chunks],
            "scores": [similarity scores],
            "num_results": int,
            "strategy": "needle" or "exhaustive",
            "unique_documents": int
        }
    """
    # Import here to avoid circular dependencies
    import sys
    import os
    
    # Add cognitive_crawler paths for imports
    crawler_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../sub_agents/cognitive_crawler')
    )
    crawler_tools = os.path.join(crawler_dir, 'tools')
    
    if crawler_dir not in sys.path:
        sys.path.insert(0, crawler_dir)
    if crawler_tools not in sys.path:
        sys.path.insert(0, crawler_tools)
    
    from tools.mongodb_handler import TenderMongoDBHandler
    
    print(f"\n🔍 Knowledge Base Query: {query}")
    
    # Progress update helper
    async def send_progress(step: str, message: str):
        if progress_callback:
            await progress_callback(step, message)
        print(f"   {message}")
    
    # Step 1: Classify query scope
    await send_progress("classify", "🤔 Analyzing query type...")
    
    if force_scope:
        scope = force_scope
        await send_progress("classify", f"🎯 Using forced scope: {scope}")
    else:
        scope = await classify_query_scope(query)
        scope_emoji = "🎯" if scope == "needle" else "📚"
        scope_label = "NEEDLE IN HAYSTACK" if scope == "needle" else "EXHAUSTIVE SEARCH"
        await send_progress("classify", f"{scope_emoji} Detected: {scope_label}")
    
    # Step 2: Adaptive retrieval based on scope
    db = TenderMongoDBHandler()
    
    try:
        if scope == "exhaustive":
            # EXHAUSTIVE SEARCH: Broad questions
            await send_progress("retrieve", "📚 Using EXHAUSTIVE strategy (broad query)")
            await send_progress("retrieve", "🔍 Searching vector database for diverse documents...")
            
            # Retrieve 3x more to get diverse documents
            results = await db.search_vectors(query, top_k=top_k * 3)
            
            await send_progress("filter", f"📊 Retrieved {len(results)} chunks from vector DB")
            
            # Filter by minimum score
            filtered = [r for r in results if r.get('score', 0) >= min_score]
            await send_progress("filter", f"✂️ Filtered to {len(filtered)} relevant chunks (score ≥ {min_score})")
            
            # Deduplicate by URL - keep best chunk per document
            await send_progress("deduplicate", "🔄 Deduplicating by URL...")
            unique_docs = deduplicate_by_url(filtered)
            
            await send_progress("deduplicate", f"✅ Found {len(unique_docs)} unique documents")
            
            # Take top_k unique documents
            final_results = unique_docs[:top_k]
            
        else:
            # NEEDLE IN HAYSTACK: Specific questions
            await send_progress("retrieve", "🎯 Using NEEDLE strategy (specific query)")
            await send_progress("retrieve", "🔍 Searching vector database for precise match...")
            
            # Standard retrieval
            results = await db.search_vectors(query, top_k=top_k * 2)  # Retrieve 2x for dedup buffer
            
            await send_progress("filter", f"📊 Retrieved {len(results)} chunks from vector DB")
            
            # Filter by minimum score
            filtered = [r for r in results if r.get('score', 0) >= min_score]
            await send_progress("filter", f"✂️ Filtered to {len(filtered)} relevant chunks (score ≥ {min_score})")
            
            # Deduplicate by URL
            await send_progress("deduplicate", "🔄 Deduplicating by URL...")
            unique_docs = deduplicate_by_url(filtered)
            
            await send_progress("deduplicate", f"✅ Found {len(unique_docs)} unique documents")
            
            # Take top_k unique documents
            final_results = unique_docs[:top_k]
        
        if len(final_results) == 0:
            return {
                "answer": "No relevant information found in the knowledge base.",
                "sources": [],
                "chunks": [],
                "scores": [],
                "num_results": 0,
                "strategy": scope,
                "unique_documents": 0
            }
        
        # Extract unique sources
        sources = []
        for r in final_results:
            url = r.get('metadata', {}).get('url', 'Unknown')
            if url not in sources:
                sources.append(url)
        
        await send_progress("sources", f"📄 Using {len(sources)} unique sources for answer")
        
        # Generate answer if requested
        answer = ""
        if generate_answer:
            # For exhaustive: use more context, for needle: use less
            context_limit = 15 if scope == "exhaustive" else 10
            
            await send_progress("generate", f"🤖 Generating {'comprehensive' if scope == 'exhaustive' else 'precise'} answer...")
            await send_progress("generate", f"📝 Using top {min(context_limit, len(final_results))} documents for context")
            
            # Build context from results
            context_parts = []
            for i, r in enumerate(final_results[:context_limit], 1):
                url = r.get('metadata', {}).get('url', 'Unknown')
                content = r.get('content', '')[:1500 if scope == "exhaustive" else 1000]
                score = r.get('score', 0)
                
                context_parts.append(
                    f"[Source {i}] (Relevance: {score:.2f})\n"
                    f"URL: {url}\n"
                    f"Content: {content}\n"
                )
            
            context = "\n---\n\n".join(context_parts)
            
            # Generate answer
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            if scope == "exhaustive":
                rag_prompt = f"""You are a helpful assistant that provides COMPREHENSIVE answers based on provided context.

Question: {query}

Context from knowledge base ({len(sources)} unique sources):
{context}

Instructions:
1. Provide a THOROUGH, COMPREHENSIVE answer covering all relevant information
2. Organize information by themes/categories if applicable
3. Include details from multiple sources when available
4. Cite sources using [Source N] notation
5. If sources conflict, mention the different perspectives
6. Be detailed but well-structured

Answer:"""
            else:
                rag_prompt = f"""You are a helpful assistant that provides PRECISE answers based on provided context.

Question: {query}

Context from knowledge base:
{context}

Instructions:
1. Answer the question PRECISELY and CONCISELY
2. Focus on the specific information requested
3. Cite sources using [Source N] notation
4. If context doesn't contain the exact answer, say so
5. Be direct and to-the-point

Answer:"""


            # STREAMING support
            if stream_callback:
                # Stream the response token by token
                await send_progress("generate_stream", "🌊 Streaming answer...")
                accumulated_content = ""
                
                async for chunk in llm.astream([
                    {"role": "system", "content": "You are a helpful research assistant."},
                    {"role": "user", "content": rag_prompt}
                ]):
                    if hasattr(chunk, 'content') and chunk.content:
                        accumulated_content += chunk.content
                        # Call the callback with each chunk
                        await stream_callback(chunk.content)
                
                answer = accumulated_content
                await send_progress("complete", f"✅ Streaming complete ({len(answer)} chars, {len(sources)} sources)")
            else:
                # Non-streaming: original behavior
                response = await llm.ainvoke([
                    {"role": "system", "content": "You are a helpful research assistant."},
                    {"role": "user", "content": rag_prompt}
                ])
                
                answer = response.content
                await send_progress("complete", f"✅ Answer ready ({len(answer)} chars, {len(sources)} sources)")
        
        return {
            "answer": answer,
            "sources": sources,
            "chunks": final_results,
            "scores": [r.get('score', 0) for r in final_results],
            "num_results": len(final_results),
            "strategy": scope,
            "unique_documents": len(sources),
            "query": query
        }
        
    except Exception as e:
        print(f"   ❌ Knowledge base query error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "answer": f"Error querying knowledge base: {str(e)}",
            "sources": [],
            "chunks": [],
            "scores": [],
            "num_results": 0,
            "strategy": "error",
            "unique_documents": 0,
            "error": str(e)
        }
    
    finally:
        db.close()


if __name__ == "__main__":
    """Test the knowledge base tool"""
    import asyncio
    
    async def test():
        print("\n" + "="*80)
        print("🧪 TESTING ADAPTIVE RAG")
        print("="*80)
        
        # Test 1: Needle in Haystack
        print("\n" + "="*80)
        print("TEST 1: NEEDLE IN HAYSTACK")
        print("="*80)
        result1 = await query_knowledge_base(
            query="What is the Drugs and Cosmetics Act?",
            top_k=10,
            min_score=0.3
        )
        
        print(f"\n✅ Strategy: {result1['strategy']}")
        print(f"✅ Found {result1['num_results']} results from {result1['unique_documents']} documents")
        print(f"\n📝 Answer:\n{result1['answer'][:300]}...")
        
        # Test 2: Exhaustive Search
        print("\n\n" + "="*80)
        print("TEST 2: EXHAUSTIVE SEARCH")
        print("="*80)
        result2 = await query_knowledge_base(
            query="Tell me everything about drug regulations in India",
            top_k=10,
            min_score=0.3
        )
        
        print(f"\n✅ Strategy: {result2['strategy']}")
        print(f"✅ Found {result2['num_results']} results from {result2['unique_documents']} documents")
        print(f"\n📝 Answer:\n{result2['answer'][:300]}...")
        
        print("\n" + "="*80)
    
    asyncio.run(test())
