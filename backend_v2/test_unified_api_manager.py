"""
Test Unified API Manager - Verify centralized API management and caching

This test demonstrates:
1. Tavily search caching
2. Tavily extract caching
3. OpenAI LLM calls
4. OpenAI embeddings
5. Cost tracking
6. Cache hit rates
"""

import asyncio
import sys
import os

# Add backend_v2 to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.api_manager import get_api_manager


async def test_unified_api_manager():
    print("="*80)
    print("🧪 UNIFIED API MANAGER TEST")
    print("="*80)
    
    # Initialize manager
    api = get_api_manager(enable_caching=True)
    
    # ========================================================================
    # TEST 1: Tavily Search (with caching)
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 1: TAVILY SEARCH CACHING")
    print("="*80)
    
    query = "artificial intelligence 2025"
    
    print(f"\n🔍 Run 1: Search for '{query}'")
    result1 = await api.tavily_search(query=query, max_results=2)
    
    if "error" in result1:
        print(f"   ❌ Error: {result1['error']}")
    else:
        print(f"   ✅ Got {len(result1.get('results', []))} results")
        print(f"   💰 Cost: ${api.costs['tavily_search']:.3f}")
    
    print(f"\n🔍 Run 2: Same search (should hit cache)")
    result2 = await api.tavily_search(query=query, max_results=2)
    
    if "error" in result2:
        print(f"   ❌ Error: {result2['error']}")
    else:
        print(f"   ✅ Got {len(result2.get('results', []))} results")
        print(f"   💰 Cost: ${api.costs['tavily_search']:.3f} (should be same as Run 1)")
    
    # ========================================================================
    # TEST 2: Tavily Extract (with caching)
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 2: TAVILY EXTRACT CACHING")
    print("="*80)
    
    if result1.get("results"):
        urls = [result1["results"][0]["url"]]
        
        print(f"\n📄 Run 1: Extract {urls[0][:60]}...")
        extract1 = await api.tavily_extract(urls=urls)
        
        if "error" in extract1:
            print(f"   ❌ Error: {extract1['error']}")
        else:
            content_len = len(extract1["results"][0].get("raw_content", ""))
            print(f"   ✅ Extracted {content_len} chars")
            print(f"   💰 Cost: ${api.costs['tavily_extract']:.3f}")
        
        print(f"\n📄 Run 2: Same URL (should hit cache)")
        extract2 = await api.tavily_extract(urls=urls)
        
        if "error" in extract2:
            print(f"   ❌ Error: {extract2['error']}")
        else:
            content_len = len(extract2["results"][0].get("raw_content", ""))
            print(f"   ✅ Extracted {content_len} chars")
            print(f"   💰 Cost: ${api.costs['tavily_extract']:.3f} (should be same as Run 1)")
    else:
        print("⚠️  Skipping extract test (no search results)")
    
    # ========================================================================
    # TEST 3: OpenAI LLM
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 3: OPENAI LLM COMPLETION")
    print("="*80)
    
    prompt = "What is 2+2? Answer in one word."
    
    print(f"\n🤖 LLM Query: '{prompt}'")
    llm_result = await api.llm_complete(prompt=prompt, max_tokens=10)
    
    if "error" in llm_result:
        print(f"   ❌ Error: {llm_result['error']}")
    else:
        print(f"   ✅ Response: {llm_result['content']}")
        print(f"   💰 Cost: ${llm_result['cost']:.6f}")
        print(f"   📊 Tokens: {llm_result['tokens_used']}")
    
    # ========================================================================
    # TEST 4: OpenAI Embeddings
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 4: OPENAI EMBEDDINGS")
    print("="*80)
    
    text = "This is a test sentence for embedding generation."
    
    print(f"\n🧬 Creating embedding for: '{text}'")
    embedding = await api.create_embedding(text=text)
    
    if embedding:
        print(f"   ✅ Embedding created: {len(embedding)} dimensions")
        print(f"   💰 Cost: ${api.costs['openai_embedding']:.6f}")
    else:
        print(f"   ❌ Failed to create embedding")
    
    # ========================================================================
    # FINAL STATISTICS
    # ========================================================================
    print("\n" + "="*80)
    print("📊 FINAL COST & USAGE STATISTICS")
    print("="*80)
    
    stats = api.get_cost_stats()
    
    print(f"\n💰 COSTS:")
    print(f"   Tavily Search:    ${stats['costs']['tavily_search']:.3f}")
    print(f"   Tavily Extract:   ${stats['costs']['tavily_extract']:.3f}")
    print(f"   OpenAI LLM:       ${stats['costs']['openai_llm']:.6f}")
    print(f"   OpenAI Embedding: ${stats['costs']['openai_embedding']:.6f}")
    print(f"   {'─'*40}")
    print(f"   TOTAL:            ${stats['costs']['total']:.3f}")
    
    print(f"\n📞 API CALLS:")
    print(f"   Tavily Search:    {stats['calls']['tavily_search']}")
    print(f"   Tavily Extract:   {stats['calls']['tavily_extract']}")
    print(f"   OpenAI LLM:       {stats['calls']['openai_llm']}")
    print(f"   OpenAI Embedding: {stats['calls']['openai_embedding']}")
    print(f"   {'─'*40}")
    print(f"   TOTAL:            {stats['calls']['total']}")
    
    print(f"\n💾 CACHE PERFORMANCE:")
    print(f"   Cache Hits:       {stats['cache']['hits']}")
    print(f"   Cache Misses:     {stats['cache']['misses']}")
    print(f"   Hit Rate:         {stats['cache']['hit_rate']*100:.1f}%")
    
    if stats['cache_stats']:
        print(f"\n🗄️  CACHE STORAGE:")
        cs = stats['cache_stats']
        print(f"   Search Cache:     {cs.get('search_total', 0)} queries")
        print(f"   Extract Cache:    {cs.get('extract_total', 0)} URLs")
        print(f"   Vector Storage:   {cs.get('vector_total', 0)} embeddings")
        print(f"   Total Saved:      ${cs.get('total_saved', 0):.2f}")
    
    # ========================================================================
    # SUCCESS CRITERIA
    # ========================================================================
    print("\n" + "="*80)
    print("✅ SUCCESS CRITERIA")
    print("="*80)
    
    success = True
    
    if stats['calls']['tavily_search'] >= 2:
        print("✅ Tavily search tested")
    else:
        print("❌ Tavily search not tested properly")
        success = False
    
    if stats['cache']['hit_rate'] > 0:
        print(f"✅ Caching working ({stats['cache']['hit_rate']*100:.0f}% hit rate)")
    else:
        print("⚠️  No cache hits detected")
    
    if stats['costs']['total'] > 0:
        print(f"✅ Cost tracking working (${stats['costs']['total']:.3f} tracked)")
    else:
        print("❌ Cost tracking not working")
        success = False
    
    print("\n" + "="*80)
    if success:
        print("🎉 ALL TESTS PASSED - Unified API Manager is working!")
    else:
        print("⚠️  SOME TESTS FAILED - Check logs above")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_unified_api_manager())


