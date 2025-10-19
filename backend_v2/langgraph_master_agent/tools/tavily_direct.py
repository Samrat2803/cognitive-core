"""
Direct Tavily Tools for Master Agent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import Dict, Any, List, Optional
from shared.tavily_client import TavilyClient
from shared.observability import ObservabilityManager

observe = ObservabilityManager.get_observe_decorator()


class TavilyDirectTools:
    """Direct Tavily API tools for master agent"""
    
    def __init__(self):
        self.client = TavilyClient()
    
    @observe(name="tavily_search_tool")
    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 8,
        days: Optional[int] = None,
        topic: Optional[str] = None,
        country: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        include_images: bool = False,
        include_raw_content: bool = False,
        auto_parameters: bool = False
    ) -> Dict[str, Any]:
        """
        Execute Tavily search with full parameter support
        
        Real-time web search for political intelligence and news.
        
        Args:
            query: Search term/question (e.g., "Hamas ceasefire negotiations 2024")
            search_depth: "basic" (faster, generic snippets) or "advanced" (detailed content, 3x more data)
            max_results: Number of results to return (1-20). Use 15+ for comprehensive analysis.
            days: Limit results to last N days (e.g., 7 for last week). Essential for "recent" queries.
            topic: "general" (broad) or "news" (mainstream media). Use "news" for political analysis.
            country: Prioritize results from country (e.g., "US", "UK", "India")
            include_domains: List of trusted domains (e.g., ["bbc.com", "reuters.com", "apnews.com"])
            exclude_domains: List of domains to avoid (e.g., ["rt.com"] for state propaganda)
            include_images: Include image URLs for visual context
            include_raw_content: Include full article text (10x more content than snippets)
            auto_parameters: Let Tavily auto-tune search settings
        
        Returns:
            Formatted search results with answer, results array, and citations
        """
        result = await self.client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=True,
            days=days,
            topic=topic,
            country=country,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_images=include_images,
            include_raw_content=include_raw_content,
            auto_parameters=auto_parameters
        )
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"],
                "results": []
            }
        
        # Format results
        formatted_results = []
        answer = result.get("answer", "")
        
        for item in result.get("results", []):
            formatted_results.append({
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "url": item.get("url", ""),
                "score": item.get("score", 0),
                "published_date": item.get("published_date", "")
            })
        
        return {
            "success": True,
            "answer": answer,
            "results": formatted_results,
            "query": query,
            "result_count": len(formatted_results)
        }
    
    @observe(name="tavily_extract_tool")
    async def extract(
        self,
        urls: List[str],
        format: str = "markdown",
        extract_depth: str = "basic",
        include_images: bool = False
    ) -> Dict[str, Any]:
        """
        Extract full structured content from specific URLs
        
        Use when you have URLs and need complete article text for deep analysis.
        
        Args:
            urls: List of URLs to extract (max 10). e.g., ["https://bbc.com/article1", "https://reuters.com/article2"]
            format: "markdown" (structured, preserves formatting) or "text" (plain). Prefer markdown.
            extract_depth: "basic" (main content only) or "advanced" (includes tables, embedded content, metadata)
            include_images: Include all image URLs from the articles
        
        Best Practice: Use after tavily_search to get full content (search gives snippets, extract gives complete articles)
        
        Returns:
            Extracted content for each URL with raw_content (full article text), images, and url
        """
        result = await self.client.extract(
            urls=urls,
            format=format,
            extract_depth=extract_depth,
            include_images=include_images
        )
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"],
                "extracts": []
            }
        
        return {
            "success": True,
            "extracts": result.get("results", []),
            "url_count": len(urls)
        }
    
    @observe(name="tavily_crawl_tool")
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
        Systematically explore and extract content from entire websites
        
        Use when you need comprehensive coverage of a website section (e.g., policy pages, research repositories).
        
        Args:
            url: Starting URL to begin crawl (e.g., "https://whitehouse.gov/policies/foreign-policy")
            max_depth: How many link levels to follow (1-3). Default: 2. Use 3 for comprehensive crawls.
            max_breadth: How many links to follow per page (e.g., 50). Controls crawl width.
            limit: Maximum total pages to crawl (e.g., 100). Prevents runaway crawls.
            format: "markdown" (structured) or "text" (plain). Prefer markdown.
            extract_depth: "basic" or "advanced" (includes tables, metadata)
            select_paths: Regex patterns to focus crawl (e.g., ["/policies/", "/statements/"])
            select_domains: Regex patterns for allowed domains (e.g., ["whitehouse.gov"])
        
        Best Practice: Start with max_depth=2, increase to 3 only if needed. Use select_paths to focus crawl.
        Always set limit to prevent excessive crawling.
        
        Note: Time-intensive (2-5 minutes for large crawls). Max depth 3.
        
        Returns:
            Crawled content from multiple pages with raw_content, url, and depth_level
        """
        result = await self.client.crawl(
            url=url,
            max_depth=max_depth,
            max_breadth=max_breadth,
            limit=limit,
            format=format,
            extract_depth=extract_depth,
            select_paths=select_paths,
            select_domains=select_domains
        )
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"],
                "pages": []
            }
        
        return {
            "success": True,
            "pages": result.get("results", []),
            "page_count": len(result.get("results", []))
        }
    
    @observe(name="tavily_map_tool")
    async def map(
        self,
        url: str,
        instructions: Optional[str] = None,
        max_depth: int = 1,
        max_breadth: int = 20,
        limit: int = 50,
        select_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive website sitemap
        
        Traverses websites like a graph to discover all URLs. Explores hundreds of paths in parallel.
        
        Args:
            url: Root URL to map (e.g., "docs.tavily.com", "whitehouse.gov")
            instructions: Natural language instructions for intelligent discovery (e.g., "Find all policy pages")
            max_depth: How far from root to explore (1-5). Default: 1
            max_breadth: Max links per page (default: 20)
            limit: Total URLs to discover before stopping (default: 50)
            select_paths: Include only paths matching patterns (e.g., ["/docs/.*", "/api/.*"])
            exclude_paths: Exclude paths matching patterns (e.g., ["/private/.*", "/admin/.*"])
        
        Use Cases:
        - Discover all pages on a government website for comprehensive policy analysis
        - Map think tank research pages
        - Find all documentation pages
        - Discover hidden/linked content not easily found via search
        
        Examples:
        - "Map UN website for humanitarian reports" → url="un.org", instructions="Find humanitarian reports"
        - "Discover all WHO COVID pages" → url="who.int", select_paths=["/covid/.*"]
        
        Returns:
            Sitemap with base_url, results (list of discovered URLs), and response_time
        """
        result = await self.client.map(
            url=url,
            instructions=instructions,
            max_depth=max_depth,
            max_breadth=max_breadth,
            limit=limit,
            select_paths=select_paths,
            exclude_paths=exclude_paths
        )
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"],
                "urls": []
            }
        
        return {
            "success": True,
            "base_url": result.get("base_url", ""),
            "urls": result.get("results", []),
            "url_count": len(result.get("results", [])),
            "response_time": result.get("response_time", 0)
        }

