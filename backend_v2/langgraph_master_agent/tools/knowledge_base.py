"""
Knowledge Base RAG Tool

Provides semantic search over accumulated crawled content.
This is a TOOL, not a sub-agent - it's a simple stateless function.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


@observe(name="query_knowledge_base_tool")
async def query_knowledge_base(
    query: str, 
    top_k: int = 30,  # Increased from 10 to 30 for more comprehensive answers
    min_score: float = 0.3,
    generate_answer: bool = True
) -> Dict[str, Any]:
    """
    Query the accumulated knowledge base using RAG
    
    This tool searches all crawled content using semantic similarity
    and optionally generates an LLM answer based on the results.
    
    Args:
        query: Natural language question
        top_k: Number of results to return
        min_score: Minimum cosine similarity score (0-1)
        generate_answer: Whether to generate LLM answer (default: True)
        
    Returns:
        {
            "answer": "LLM-generated answer" (if generate_answer=True),
            "sources": [list of source URLs],
            "chunks": [list of relevant content chunks],
            "scores": [similarity scores],
            "num_results": int
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
    
    # Search vectors
    db = TenderMongoDBHandler()
    try:
        results = await db.search_vectors(query, top_k=top_k)
        
        # Filter by minimum score
        filtered = [r for r in results if r.get('score', 0) >= min_score]
        
        print(f"   ✅ Found {len(filtered)} results (min_score={min_score})")
        
        if len(filtered) == 0:
            return {
                "answer": "No relevant information found in the knowledge base.",
                "sources": [],
                "chunks": [],
                "scores": [],
                "num_results": 0
            }
        
        # Extract sources
        sources = []
        for r in filtered:
            url = r.get('metadata', {}).get('url', 'Unknown')
            if url not in sources:
                sources.append(url)
        
        # Generate answer if requested
        answer = ""
        if generate_answer:
            print(f"   🤖 Generating LLM answer from {len(filtered[:10])} top results...")
            
            # Build context from top 10 results (out of 30 retrieved)
            context_parts = []
            for i, r in enumerate(filtered[:10], 1):
                url = r.get('metadata', {}).get('url', 'Unknown')
                content = r.get('content', '')[:1000]  # Limit per chunk (increased from 800)
                score = r.get('score', 0)
                
                context_parts.append(
                    f"[Source {i}] (Relevance: {score:.2f})\n"
                    f"URL: {url}\n"
                    f"Content: {content}\n"
                )
            
            context = "\n---\n\n".join(context_parts)
            
            # Generate answer
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            rag_prompt = f"""You are a helpful assistant that answers questions based on provided context.

Question: {query}

Context from knowledge base:
{context}

Instructions:
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain enough information, say so
3. Cite sources by mentioning the source numbers [Source 1], [Source 2], etc.
4. Be concise but comprehensive
5. If multiple sources say different things, mention the differences

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
            "error": str(e)
        }
    
    finally:
        db.close()


if __name__ == "__main__":
    """Test the knowledge base tool"""
    import asyncio
    
    async def test():
        print("\n" + "="*80)
        print("🧪 TESTING KNOWLEDGE BASE TOOL")
        print("="*80)
        
        # Test query
        result = await query_knowledge_base(
            query="What caused the cough syrup deaths in India?",
            top_k=5,
            min_score=0.3
        )
        
        print("\n" + "="*80)
        print("📊 RESULTS")
        print("="*80)
        print(f"\n✅ Found {result['num_results']} relevant results")
        print(f"\n📝 Answer:\n{result['answer']}")
        print(f"\n🔗 Sources:")
        for i, source in enumerate(result['sources'], 1):
            print(f"   {i}. {source}")
        print("\n" + "="*80)
    
    asyncio.run(test())

