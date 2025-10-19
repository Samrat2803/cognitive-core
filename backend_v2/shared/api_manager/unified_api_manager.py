"""
Unified API Manager - Central management for all external API calls

This module consolidates:
1. Tavily API (search, extract, QnA, crawl)
2. OpenAI API (LLM, embeddings)
3. MongoDB caching layer
4. Cost tracking and analytics

All API calls go through this manager for:
- Automatic caching
- Cost tracking
- Rate limit handling
- Error handling
- Logging
"""

import os
import asyncio
from typing import Dict, List, Optional, Any, Literal, Union
from datetime import datetime
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class UnifiedAPIManager:
    """
    Single source of truth for all external API calls
    
    Features:
    - Automatic caching (Tavily: 24h/7d, OpenAI: configurable)
    - Cost tracking per API call
    - Rate limit handling
    - Fallback strategies
    - Unified error handling
    """
    
    # Cost constants (per call/token)
    COST_TAVILY_SEARCH = 0.01
    COST_TAVILY_EXTRACT = 0.05
    COST_OPENAI_GPT4O_INPUT = 2.50 / 1_000_000  # per token
    COST_OPENAI_GPT4O_OUTPUT = 10.00 / 1_000_000  # per token
    COST_OPENAI_EMBEDDING = 0.02 / 1_000_000  # per token
    
    def __init__(self, enable_caching: bool = True):
        """
        Initialize unified API manager
        
        Args:
            enable_caching: Enable MongoDB caching for all APIs
        """
        self.enable_caching = enable_caching
        
        # Initialize API clients
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.tavily_api_key:
            print("⚠️  TAVILY_API_KEY not found")
        if not self.openai_api_key:
            print("⚠️  OPENAI_API_KEY not found")
        
        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        
        # Initialize cache
        self.cache = None
        if enable_caching:
            try:
                from ..tavily_cache import get_tavily_cache
                self.cache = get_tavily_cache()
                print("✅ Unified API Manager initialized with caching")
            except Exception as e:
                print(f"⚠️  Caching initialization failed: {e}")
                self.enable_caching = False
        else:
            print("✅ Unified API Manager initialized (caching disabled)")
        
        # Cost tracking
        self.costs = {
            "tavily_search": 0,
            "tavily_extract": 0,
            "openai_llm": 0,
            "openai_embedding": 0,
            "total": 0
        }
        
        # Call statistics
        self.stats = {
            "tavily_search_calls": 0,
            "tavily_extract_calls": 0,
            "openai_llm_calls": 0,
            "openai_embedding_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    # ============================================================================
    # TAVILY API METHODS
    # ============================================================================
    
    async def tavily_search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 5,
        topic: str = "general",
        include_answer: bool = False,
        include_images: bool = False,
        include_raw_content: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tavily search with automatic caching
        
        Args:
            query: Search query
            search_depth: "basic" (1 credit) or "advanced" (2 credits)
            max_results: Number of results (0-20)
            topic: "general", "news", or "finance"
            include_answer: Include LLM-generated answer
            include_images: Include relevant images
            include_raw_content: Include full article content
            **kwargs: Additional Tavily parameters
        
        Returns:
            Search results dict
        """
        self.stats["tavily_search_calls"] += 1
        
        # Check cache first
        if self.enable_caching and self.cache:
            cached_result = await self.cache.get_cached_search(query, search_depth, max_results)
            if cached_result:
                self.stats["cache_hits"] += 1
                print(f"💰 CACHE HIT - Search: '{query[:50]}...'")
                return cached_result
        
        self.stats["cache_misses"] += 1
        
        # Make API call
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": max_results,
                    "topic": topic,
                    "include_answer": include_answer,
                    "include_images": include_images,
                    "include_raw_content": include_raw_content,
                    **kwargs
                }
                
                response = await client.post(
                    "https://api.tavily.com/search",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Track cost
                    cost = self.COST_TAVILY_SEARCH * (2 if search_depth == "advanced" else 1)
                    self.costs["tavily_search"] += cost
                    self.costs["total"] += cost
                    
                    # Cache result
                    if self.enable_caching and self.cache:
                        await self.cache.cache_search(query, result, search_depth, max_results)
                    
                    return result
                elif response.status_code == 432:
                    return {"error": "Rate limit exceeded", "results": []}
                else:
                    return {"error": f"API error {response.status_code}", "results": []}
        
        except Exception as e:
            return {"error": f"Request failed: {str(e)}", "results": []}
    
    async def tavily_extract(
        self,
        urls: List[str],
        format: str = "markdown",
        extract_depth: str = "basic"
    ) -> Dict[str, Any]:
        """
        Tavily extract with automatic caching
        
        Args:
            urls: List of URLs to extract
            format: "markdown" or "text"
            extract_depth: "basic" or "advanced"
        
        Returns:
            Extraction results dict
        """
        self.stats["tavily_extract_calls"] += 1
        
        # Check cache for all URLs
        urls_to_fetch = urls
        cached_results = {}
        
        if self.enable_caching and self.cache:
            cached_results = await self.cache.get_multiple_cached_extracts(urls)
            urls_to_fetch = [url for url in urls if url not in cached_results]
            
            if cached_results:
                self.stats["cache_hits"] += len(cached_results)
                print(f"💰 CACHE HIT - {len(cached_results)}/{len(urls)} extracts")
        
        # Fetch uncached URLs
        if not urls_to_fetch:
            return {
                "results": [
                    {"url": url, "raw_content": content, "method": "cache"}
                    for url, content in cached_results.items()
                ]
            }
        
        self.stats["cache_misses"] += len(urls_to_fetch)
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                payload = {
                    "api_key": self.tavily_api_key,
                    "urls": urls_to_fetch
                }
                
                response = await client.post(
                    "https://api.tavily.com/extract",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    fresh_results = result.get("results", [])
                    
                    # Track cost
                    cost = self.COST_TAVILY_EXTRACT * len(urls_to_fetch)
                    self.costs["tavily_extract"] += cost
                    self.costs["total"] += cost
                    
                    # Cache and store vectors
                    if self.enable_caching and self.cache:
                        for item in fresh_results:
                            url = item.get("url")
                            content = item.get("raw_content", "")
                            if url and content:
                                await self.cache.cache_extract(
                                    url=url,
                                    content=content,
                                    method="tavily",
                                    store_vector=True
                                )
                    
                    # Combine cached and fresh results
                    all_results = [
                        {"url": url, "raw_content": content, "method": "cache"}
                        for url, content in cached_results.items()
                    ] + fresh_results
                    
                    return {"results": all_results}
                
                else:
                    # Return cached results even if API fails
                    if cached_results:
                        return {
                            "results": [
                                {"url": url, "raw_content": content, "method": "cache"}
                                for url, content in cached_results.items()
                            ],
                            "error": f"API error {response.status_code}, returning {len(cached_results)} cached results"
                        }
                    return {"error": f"API error {response.status_code}", "results": []}
        
        except Exception as e:
            # Return cached results even if exception
            if cached_results:
                return {
                    "results": [
                        {"url": url, "raw_content": content, "method": "cache"}
                        for url, content in cached_results.items()
                    ],
                    "error": f"Request failed: {str(e)}, returning {len(cached_results)} cached results"
                }
            return {"error": f"Request failed: {str(e)}", "results": []}
    
    # ============================================================================
    # OPENAI API METHODS
    # ============================================================================
    
    async def llm_complete(
        self,
        prompt: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        cache_key: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        OpenAI LLM completion with optional caching
        
        Args:
            prompt: User prompt
            model: OpenAI model name
            temperature: 0-2
            max_tokens: Max response tokens
            cache_key: Optional key for caching (e.g., "sentiment_analysis_prompt")
            system_prompt: Optional system prompt
        
        Returns:
            Dict with 'content', 'tokens_used', 'cost'
        """
        if not self.openai_client:
            return {"error": "OpenAI client not initialized", "content": ""}
        
        self.stats["openai_llm_calls"] += 1
        
        # Check cache if cache_key provided
        if cache_key and self.enable_caching and self.cache:
            # TODO: Implement LLM response caching
            pass
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # Calculate cost
            cost = (
                input_tokens * self.COST_OPENAI_GPT4O_INPUT +
                output_tokens * self.COST_OPENAI_GPT4O_OUTPUT
            )
            
            self.costs["openai_llm"] += cost
            self.costs["total"] += cost
            
            return {
                "content": content,
                "tokens_used": input_tokens + output_tokens,
                "cost": cost,
                "model": model
            }
        
        except Exception as e:
            return {"error": str(e), "content": ""}
    
    async def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> Optional[List[float]]:
        """
        Create OpenAI embedding
        
        Args:
            text: Text to embed
            model: Embedding model
        
        Returns:
            Embedding vector or None
        """
        if not self.openai_client:
            return None
        
        self.stats["openai_embedding_calls"] += 1
        
        try:
            # Truncate to ~8000 chars
            truncated_text = text[:8000] if len(text) > 8000 else text
            
            response = await self.openai_client.embeddings.create(
                model=model,
                input=truncated_text
            )
            
            embedding = response.data[0].embedding
            
            # Calculate cost
            tokens_used = len(truncated_text) // 4  # Rough estimate
            cost = tokens_used * self.COST_OPENAI_EMBEDDING
            
            self.costs["openai_embedding"] += cost
            self.costs["total"] += cost
            
            return embedding
        
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return None
    
    # ============================================================================
    # COST TRACKING & STATISTICS
    # ============================================================================
    
    def get_cost_stats(self) -> Dict[str, Any]:
        """Get comprehensive cost and usage statistics"""
        return {
            "costs": {
                **self.costs,
                "breakdown": {
                    "tavily": self.costs["tavily_search"] + self.costs["tavily_extract"],
                    "openai": self.costs["openai_llm"] + self.costs["openai_embedding"]
                }
            },
            "calls": {
                "tavily_search": self.stats["tavily_search_calls"],
                "tavily_extract": self.stats["tavily_extract_calls"],
                "openai_llm": self.stats["openai_llm_calls"],
                "openai_embedding": self.stats["openai_embedding_calls"],
                "total": sum([
                    self.stats["tavily_search_calls"],
                    self.stats["tavily_extract_calls"],
                    self.stats["openai_llm_calls"],
                    self.stats["openai_embedding_calls"]
                ])
            },
            "cache": {
                "hits": self.stats["cache_hits"],
                "misses": self.stats["cache_misses"],
                "hit_rate": (
                    self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"])
                    if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 else 0
                )
            },
            "cache_stats": self.cache.get_stats() if self.cache else {}
        }
    
    def reset_stats(self):
        """Reset all cost and usage statistics"""
        self.costs = {
            "tavily_search": 0,
            "tavily_extract": 0,
            "openai_llm": 0,
            "openai_embedding": 0,
            "total": 0
        }
        self.stats = {
            "tavily_search_calls": 0,
            "tavily_extract_calls": 0,
            "openai_llm_calls": 0,
            "openai_embedding_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_api_manager_instance: Optional[UnifiedAPIManager] = None

def get_api_manager(enable_caching: bool = True) -> UnifiedAPIManager:
    """Get singleton instance of UnifiedAPIManager"""
    global _api_manager_instance
    
    if _api_manager_instance is None:
        _api_manager_instance = UnifiedAPIManager(enable_caching=enable_caching)
    
    return _api_manager_instance


