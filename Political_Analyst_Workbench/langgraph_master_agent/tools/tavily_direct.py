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
        country: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute Tavily search
        
        Tavily Search API Features (from POCs/tavily_api_features.md):
        - Real-time Web Search: Live retrieval of current information
        - Search Depth: basic and advanced modes
        - Auto-Parameters (Beta): Automatically tunes search settings
        - Country Parameter: Prioritizes results for specified country
        - Domain Targeting: Focus searches on specific domains
        - Include Media: Optionally include images and favicons
        
        Args:
            query: Search query
            search_depth: "basic" or "advanced"
            max_results: Number of results (1-20)
            country: Country filter (e.g., "India", "US")
        
        Returns:
            Formatted search results with citations
        """
        result = await self.client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=True,
            country=country
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
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Extract content from URLs
        
        Tavily Extract API Features:
        - Content Extraction: Fetches raw page content
        - Extraction Depth: basic and advanced options
        - Output Formats: markdown or text
        - Image/Favicon Inclusion: Optional metadata
        - Batch Extraction: Multiple URLs in single request
        
        Args:
            urls: List of URLs to extract
            format: "markdown" or "text"
        
        Returns:
            Extracted content for each URL
        """
        result = await self.client.extract(urls=urls, format=format)
        
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
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Crawl website for comprehensive content
        
        Tavily Crawl API Features:
        - Website Crawling: Follows internal links
        - Configurable Depth/Breadth: Control crawl scope
        - Integrated Extraction: Apply extract options during crawl
        - Filtering/Scoping: Restrict by path prefixes, file types
        
        Args:
            url: Starting URL
            max_depth: Crawl depth (1-3)
            format: "markdown" or "text"
        
        Returns:
            Crawled content from multiple pages
        """
        result = await self.client.crawl(
            url=url,
            max_depth=max_depth,
            format=format
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

