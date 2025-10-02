"""
Shared Tavily Client Wrapper
"""

import os
import httpx
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class TavilyClient:
    """Unified Tavily API client for all agents"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found")
        
        self.base_url = "https://api.tavily.com"
    
    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 8,
        include_answer: bool = True,
        include_images: bool = False,
        country: Optional[str] = None,
        domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Tavily Search API
        
        Args:
            query: Search query
            search_depth: "basic" or "advanced"
            max_results: Number of results (1-20)
            include_answer: Include AI-generated answer
            include_images: Include image URLs
            country: Prioritize country (e.g., "India", "US")
            domains: List of domains to focus on
        
        Returns:
            Search results with answer, results, images
        """
        async with httpx.AsyncClient(timeout=30) as client:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": search_depth,
                "include_images": include_images,
                "include_answer": include_answer,
                "max_results": max_results,
                "include_raw_content": False
            }
            
            if country:
                payload["country"] = country
            
            if domains:
                payload["include_domains"] = domains
            
            try:
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 432:
                    return {"error": "Rate limit exceeded", "results": []}
                else:
                    return {"error": f"API error {response.status_code}", "results": []}
            
            except Exception as e:
                return {"error": f"Request failed: {str(e)}", "results": []}
    
    async def extract(
        self,
        urls: List[str],
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Tavily Extract API
        
        Args:
            urls: List of URLs to extract
            format: "markdown" or "text"
        
        Returns:
            Extracted content for each URL
        """
        async with httpx.AsyncClient(timeout=60) as client:
            payload = {
                "api_key": self.api_key,
                "urls": urls,
                "format": format
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/extract",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"API error {response.status_code}", "results": []}
            
            except Exception as e:
                return {"error": f"Request failed: {str(e)}", "results": []}
    
    async def crawl(
        self,
        url: str,
        max_depth: int = 2,
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Tavily Crawl API
        
        Args:
            url: Starting URL
            max_depth: Crawl depth (1-3)
            format: "markdown" or "text"
        
        Returns:
            Crawled content from multiple pages
        """
        async with httpx.AsyncClient(timeout=120) as client:
            payload = {
                "api_key": self.api_key,
                "url": url,
                "max_depth": max_depth,
                "format": format
            }
            
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

