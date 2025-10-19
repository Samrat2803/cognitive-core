"""
Shared Tavily Client Wrapper with Integrated Caching
"""

import os
import httpx
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Try to import caching (optional dependency)
try:
    from shared.tavily_cache import get_tavily_cache
    CACHING_AVAILABLE = True
except ImportError:
    try:
        # Try relative import
        from .tavily_cache import get_tavily_cache
        CACHING_AVAILABLE = True
    except ImportError:
        CACHING_AVAILABLE = False
        print("⚠️  Tavily caching not available (tavily_cache.py not found)")


class TavilyClient:
    """Unified Tavily API client for all agents with integrated caching"""
    
    def __init__(self, api_key: Optional[str] = None, enable_caching: bool = True):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found")
        
        self.base_url = "https://api.tavily.com"
        
        # Initialize caching
        self.caching_enabled = enable_caching and CACHING_AVAILABLE
        self.cache = get_tavily_cache() if self.caching_enabled else None
        
        if self.caching_enabled:
            print("✅ Tavily client initialized with caching enabled")
        else:
            print("⚠️  Tavily client initialized WITHOUT caching")
    
    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 8,
        include_answer: bool = True,
        include_images: bool = False,
        include_raw_content: bool = False,
        country: Optional[str] = None,
        days: Optional[int] = None,
        topic: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        auto_parameters: bool = False
    ) -> Dict[str, Any]:
        """
        Tavily Search API - Enhanced with full parameter support + CACHING
        
        Args:
            query: Search query
            search_depth: "basic" or "advanced" (advanced provides 3x more content)
            max_results: Number of results (1-20)
            include_answer: Include AI-generated answer
            include_images: Include image URLs in results
            include_raw_content: Include full article text (10x more content than snippets)
            country: Prioritize results from country (e.g., "US", "UK", "India")
            days: Limit results to last N days (e.g., 7 for last week)
            topic: "general" or "news" (use "news" for political/current events)
            include_domains: List of domains to focus on (e.g., ["bbc.com", "reuters.com"])
            exclude_domains: List of domains to exclude (e.g., ["rt.com"] for propaganda)
            auto_parameters: Let Tavily auto-tune search settings based on query
        
        Returns:
            Search results with answer, results array, images (if requested)
        """
        # Check cache first
        if self.caching_enabled:
            cached_result = await self.cache.get_cached_search(query, search_depth, max_results)
            if cached_result:
                print(f"💾 CACHE HIT - Tavily Search: {query[:60]}... (saved $0.01)")
                return cached_result
            else:
                print(f"🔍 CACHE MISS - Tavily Search: {query[:60]}... (calling API)")
        
        # Cache miss or caching disabled - call Tavily API
        async with httpx.AsyncClient(timeout=30) as client:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": search_depth,
                "include_images": include_images,
                "include_answer": include_answer,
                "max_results": max_results,
                "include_raw_content": include_raw_content
            }
            
            # Optional parameters
            if country:
                payload["country"] = country
            
            if days is not None:
                payload["days"] = days
            
            if topic:
                payload["topic"] = topic
            
            if include_domains:
                payload["include_domains"] = include_domains
            
            if exclude_domains:
                payload["exclude_domains"] = exclude_domains
            
            if auto_parameters:
                payload["auto_parameters"] = True
            
            try:
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Cache the successful result
                    if self.caching_enabled:
                        await self.cache.cache_search(query, result, search_depth, max_results)
                        print(f"💾 CACHED - Tavily Search: {query[:60]}... (24h TTL)")
                    
                    return result
                elif response.status_code == 432:
                    return {"error": "Rate limit exceeded", "results": []}
                else:
                    return {"error": f"API error {response.status_code}", "results": []}
            
            except Exception as e:
                return {"error": f"Request failed: {str(e)}", "results": []}
    
    async def extract(
        self,
        urls: List[str],
        format: str = "markdown",
        extract_depth: str = "basic",
        include_images: bool = False
    ) -> Dict[str, Any]:
        """
        Tavily Extract API - Enhanced with full parameter support + CACHING
        
        Args:
            urls: List of URLs to extract (max 10)
            format: "markdown" (structured) or "text" (plain)
            extract_depth: "basic" (main content) or "advanced" (includes tables, metadata)
            include_images: Include image URLs from articles
        
        Returns:
            Extracted content for each URL with raw_content, images, url
        """
        # Check cache for each URL
        cached_extracts = {}
        urls_to_fetch = []
        
        if self.caching_enabled:
            cached_extracts = await self.cache.get_multiple_cached_extracts(urls)
            urls_to_fetch = [url for url in urls if url not in cached_extracts]
            
            # Log cache hits
            if cached_extracts:
                print(f"💾 CACHE HIT - {len(cached_extracts)} Tavily Extracts (saved ${len(cached_extracts) * 0.05:.2f})")
            if urls_to_fetch:
                print(f"🔍 CACHE MISS - {len(urls_to_fetch)} Tavily Extracts (calling API)")
        else:
            urls_to_fetch = urls
        
        # If all URLs are cached, return immediately
        if not urls_to_fetch:
            print(f"✅ ALL {len(cached_extracts)} EXTRACTS FROM CACHE")
            return {
                "results": [
                    {"url": url, "raw_content": content, "method": "cache"}
                    for url, content in cached_extracts.items()
                ]
            }
        
        # Fetch uncached URLs from Tavily
        async with httpx.AsyncClient(timeout=60) as client:
            payload = {
                "api_key": self.api_key,
                "urls": urls_to_fetch,  # Only fetch uncached URLs
                "format": format,
                "extract_depth": extract_depth,
                "include_images": include_images
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/extract",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    fresh_results = result.get("results", [])
                    
                    # Cache each extracted result
                    if self.caching_enabled:
                        cached_count = 0
                        for item in fresh_results:
                            url = item.get("url")
                            content = item.get("raw_content", "")
                            if url and content:
                                await self.cache.cache_extract(
                                    url=url,
                                    content=content,
                                    method="tavily",
                                    metadata={"format": format, "depth": extract_depth},
                                    store_vector=True
                                )
                                cached_count += 1
                        if cached_count > 0:
                            print(f"💾 CACHED - {cached_count} Tavily Extracts (7d TTL)")
                    
                    # Combine cached + fresh results
                    all_results = [
                        {"url": url, "raw_content": content, "method": "cache"}
                        for url, content in cached_extracts.items()
                    ] + fresh_results
                    
                    return {"results": all_results}
                else:
                    # On error, return what we have from cache
                    if cached_extracts:
                        return {
                            "results": [
                                {"url": url, "raw_content": content, "method": "cache"}
                                for url, content in cached_extracts.items()
                            ],
                            "error": f"API error {response.status_code} (partial results from cache)"
                        }
                    return {"error": f"API error {response.status_code}", "results": []}
            
            except Exception as e:
                # On error, return what we have from cache
                if cached_extracts:
                    return {
                        "results": [
                            {"url": url, "raw_content": content, "method": "cache"}
                            for url, content in cached_extracts.items()
                        ],
                        "error": f"Request failed: {str(e)} (partial results from cache)"
                    }
                return {"error": f"Request failed: {str(e)}", "results": []}
    
    async def crawl(
        self,
        url: str,
        max_depth: int = 2,
        max_breadth: Optional[int] = None,
        limit: Optional[int] = None,
        format: str = "markdown",
        extract_depth: str = "basic",
        select_paths: Optional[List[str]] = None,
        select_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Tavily Crawl API - Enhanced with full parameter support
        
        Args:
            url: Starting URL to begin crawl
            max_depth: How many link levels to follow (1-3)
            max_breadth: How many links to follow per page
            limit: Maximum total pages to crawl (prevents runaway crawls)
            format: "markdown" (structured) or "text" (plain)
            extract_depth: "basic" or "advanced" (includes tables, metadata)
            select_paths: Regex patterns to focus crawl (e.g., ["/policies/", "/research/"])
            select_domains: Regex patterns for allowed domains
        
        Returns:
            Crawled content from multiple pages with raw_content, url, depth_level
        """
        async with httpx.AsyncClient(timeout=120) as client:
            payload = {
                "api_key": self.api_key,
                "url": url,
                "max_depth": max_depth,
                "format": format,
                "extract_depth": extract_depth
            }
            
            # Optional parameters
            if max_breadth is not None:
                payload["max_breadth"] = max_breadth
            
            if limit is not None:
                payload["limit"] = limit
            
            if select_paths:
                payload["select_paths"] = select_paths
            
            if select_domains:
                payload["select_domains"] = select_domains
            
            try:
                response = await client.post(
                    f"{self.base_url}/crawl",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"API error {response.status_code}", "results": []}
            
            except Exception as e:
                return {"error": f"Request failed: {str(e)}", "results": []}
    
    async def map(
        self,
        url: str,
        instructions: Optional[str] = None,
        max_depth: int = 1,
        max_breadth: int = 20,
        limit: int = 50,
        select_paths: Optional[List[str]] = None,
        select_domains: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        allow_external: bool = True
    ) -> Dict[str, Any]:
        """
        Tavily Map API - Website sitemap generation (Beta)
        
        Traverses websites like a graph to discover all URLs and generate comprehensive site maps.
        Explores hundreds of paths in parallel with intelligent discovery.
        
        Args:
            url: Root URL to begin mapping (e.g., "docs.tavily.com")
            instructions: Natural language instructions for crawler (increases cost to 2 credits per 10 pages)
            max_depth: How far from base URL to explore (default: 1)
            max_breadth: Max links to follow per page (default: 20)
            limit: Total links to process before stopping (default: 50)
            select_paths: Regex patterns to include specific paths (e.g., ["/docs/.*"])
            select_domains: Regex patterns for specific domains (e.g., ["^docs\\.example\\.com$"])
            exclude_paths: Regex patterns to exclude paths (e.g., ["/private/.*"])
            exclude_domains: Regex patterns to exclude domains
            allow_external: Include external domain links (default: True)
        
        Returns:
            Sitemap with base_url, results (list of discovered URLs), response_time
        """
        async with httpx.AsyncClient(timeout=120) as client:
            payload = {
                "api_key": self.api_key,
                "url": url,
                "max_depth": max_depth,
                "max_breadth": max_breadth,
                "limit": limit,
                "allow_external": allow_external
            }
            
            # Optional parameters
            if instructions:
                payload["instructions"] = instructions
            
            if select_paths:
                payload["select_paths"] = select_paths
            
            if select_domains:
                payload["select_domains"] = select_domains
            
            if exclude_paths:
                payload["exclude_paths"] = exclude_paths
            
            if exclude_domains:
                payload["exclude_domains"] = exclude_domains
            
            try:
                response = await client.post(
                    f"{self.base_url}/map",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"API error {response.status_code}", "results": []}
            
            except Exception as e:
                return {"error": f"Request failed: {str(e)}", "results": []}

