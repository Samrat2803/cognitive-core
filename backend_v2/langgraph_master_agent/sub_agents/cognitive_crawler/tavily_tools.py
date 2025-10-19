"""
Comprehensive Tavily Tools for LangGraph Agent
Implements all 4 Tavily API endpoints with detailed parameter documentation
"""

import os
import json
from typing import Dict, List, Optional, Any, Literal, Union
from datetime import datetime
import httpx
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_BASE_URL = "https://api.tavily.com"


class TavilyTools:
    """Comprehensive Tavily API tools with detailed documentation for LLM agents"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or TAVILY_API_KEY
        if not self.api_key:
            raise ValueError("Tavily API key is required. Set TAVILY_API_KEY environment variable.")
    
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make async HTTP request to Tavily API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TAVILY_BASE_URL}/{endpoint}",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    async def tavily_search(
        self,
        query: str,
        auto_parameters: bool = False,
        topic: Literal["general", "news", "finance"] = "general",
        search_depth: Literal["basic", "advanced"] = "basic",
        chunks_per_source: Optional[int] = None,
        max_results: int = 5,
        time_range: Optional[Literal["day", "week", "month", "year", "d", "w", "m", "y"]] = None,
        days: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_answer: Union[bool, Literal["basic", "advanced"]] = False,
        include_raw_content: Union[bool, Literal["markdown", "text"]] = False,
        include_images: bool = False,
        include_image_descriptions: bool = False,
        include_favicon: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        country: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a comprehensive web search using Tavily Search API.
        
        This is the primary tool for finding current information on the internet.
        Use this when you need to answer questions about current events, facts, or any
        information that requires real-time web search.
        
        Parameters:
        -----------
        query : str (REQUIRED)
            The search query to execute. Be specific and clear.
            Examples: 
            - "What are the latest advancements in AI in 2024?"
            - "Tesla stock price today"
            - "Best practices for Python async programming"
        
        auto_parameters : bool (default: False)
            When True, Tavily automatically optimizes search parameters based on query intent.
            Useful when you're unsure about optimal settings.
            Note: May set search_depth to 'advanced' (2 credits) if likely to improve results.
        
        topic : "general" | "news" | "finance" (default: "general")
            The category of search:
            - "general": Broad search across all sources
            - "news": Real-time news from mainstream media (use for current events, politics, sports)
            - "finance": Financial data and market information
        
        search_depth : "basic" | "advanced" (default: "basic")
            Depth of search:
            - "basic": 1 API credit, returns generic content snippets
            - "advanced": 2 API credits, returns most relevant sources and content snippets
            Use "advanced" when accuracy and relevance are critical.
        
        chunks_per_source : int, 1-3 (optional, only with advanced search)
            Maximum number of content chunks (max 500 chars each) per source.
            Higher values provide more context but longer responses.
            Only available when search_depth is "advanced".
        
        max_results : int, 0-20 (default: 5)
            Maximum number of search results to return.
            More results = more comprehensive but longer processing time.
            Typical usage: 5-10 results for most queries.
        
        time_range : "day" | "week" | "month" | "year" | "d" | "w" | "m" | "y" (optional)
            Filter results by publish date.
            Use for time-sensitive queries:
            - "day"/"d": Last 24 hours
            - "week"/"w": Last 7 days
            - "month"/"m": Last 30 days
            - "year"/"y": Last 365 days
        
        days : int >= 1 (optional, only with topic="news", default: 7)
            Number of days back from current date to include.
            Only applicable when topic is "news".
        
        start_date : str (optional, format: YYYY-MM-DD)
            Include only results published after this date.
            Example: "2024-01-01"
        
        end_date : str (optional, format: YYYY-MM-DD)
            Include only results published before this date.
            Example: "2024-12-31"
        
        include_answer : bool | "basic" | "advanced" (default: False)
            Include an LLM-generated answer to the query:
            - False: No answer
            - True/"basic": Quick summary answer
            - "advanced": Detailed, comprehensive answer
            Use when you need a direct answer along with sources.
        
        include_raw_content : bool | "markdown" | "text" (default: False)
            Include the cleaned HTML content of each result:
            - False: No raw content
            - True/"markdown": Content in markdown format
            - "text": Plain text content (may increase latency)
            Use when you need full article/page content for analysis.
        
        include_images : bool (default: False)
            Perform an image search and include relevant images in results.
            Useful for visual content queries.
        
        include_image_descriptions : bool (default: False)
            When include_images is True, add descriptive text for each image.
            Helps understand image content without viewing.
        
        include_favicon : bool (default: False)
            Include the favicon URL for each result.
            Useful for displaying source branding.
        
        include_domains : List[str] (optional, max 300 domains)
            Specifically include results from these domains.
            Example: ["wikipedia.org", "nature.com", "arxiv.org"]
            Use to focus on authoritative/specific sources.
        
        exclude_domains : List[str] (optional, max 150 domains)
            Exclude results from these domains.
            Example: ["example.com", "spam-site.com"]
            Use to filter out unreliable or irrelevant sources.
        
        country : str (optional, only with topic="general")
            Boost results from a specific country (170+ countries supported).
            Examples: "united states", "united kingdom", "japan", "germany"
            Use when seeking region-specific information.
        
        Returns:
        --------
        Dict containing:
            - query: The executed search query
            - answer: LLM-generated answer (if requested)
            - results: List of search results with title, url, content, score
            - images: List of relevant images (if requested)
            - response_time: Time taken to complete request
            - request_id: Unique identifier for the request
        
        Examples:
        ---------
        1. Basic search:
           tavily_search(query="What is quantum computing?")
        
        2. Advanced news search with answer:
           tavily_search(
               query="Latest AI breakthroughs 2024",
               topic="news",
               search_depth="advanced",
               include_answer="advanced",
               time_range="month"
           )
        
        3. Academic research with domain filtering:
           tavily_search(
               query="Machine learning optimization techniques",
               include_domains=["arxiv.org", "scholar.google.com"],
               max_results=10,
               include_raw_content="markdown"
           )
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "auto_parameters": auto_parameters,
            "topic": topic,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "include_images": include_images,
            "include_image_descriptions": include_image_descriptions,
            "include_favicon": include_favicon
        }
        
        # Add optional parameters only if provided
        if chunks_per_source is not None:
            payload["chunks_per_source"] = chunks_per_source
        if time_range:
            payload["time_range"] = time_range
        if days is not None:
            payload["days"] = days
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["end_date"] = end_date
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        if country:
            payload["country"] = country
        
        return await self._make_request("search", payload)
    
    async def tavily_extract(
        self,
        urls: List[str]
    ) -> Dict[str, Any]:
        """
        Extract clean, structured content from specific web pages.
        
        Use this tool when you have specific URLs and need to extract their content.
        Perfect for reading articles, documentation, blog posts, or any web page content
        after you've found relevant URLs through search or other means.
        
        Parameters:
        -----------
        urls : List[str] (REQUIRED)
            List of URLs to extract content from.
            Supports multiple URLs in a single request for efficiency.
            Examples:
            - ["https://en.wikipedia.org/wiki/Artificial_intelligence"]
            - ["https://example.com/article1", "https://example.com/article2"]
            
            Best Practices:
            - Use valid, accessible URLs
            - Batch multiple URLs from the same source for efficiency
            - Maximum recommended: 10-20 URLs per request
            - Ensure URLs are publicly accessible (no login required)
        
        Returns:
        --------
        Dict containing:
            - results: List of extracted content for each URL
                - url: The source URL
                - raw_content: Cleaned and parsed content
                - success: Whether extraction was successful
            - failed_results: List of URLs that failed to extract (if any)
        
        Examples:
        ---------
        1. Extract single article:
           tavily_extract(urls=["https://example.com/article"])
        
        2. Extract multiple related pages:
           tavily_extract(urls=[
               "https://docs.python.org/3/library/asyncio.html",
               "https://docs.python.org/3/library/asyncio-task.html"
           ])
        
        3. Extract content after search:
           # First search, then extract from top results
           search_results = await tavily_search("Python async tutorial")
           urls = [result['url'] for result in search_results['results'][:3]]
           content = await tavily_extract(urls=urls)
        
        Use Cases:
        ----------
        - Reading full article content after finding it through search
        - Extracting documentation pages for detailed analysis
        - Gathering content from multiple pages of the same topic
        - Getting clean text content without HTML/ads/navigation
        - Building a knowledge base from specific sources
        """
        payload = {
            "api_key": self.api_key,
            "urls": urls
        }
        
        return await self._make_request("extract", payload)
    
    async def tavily_crawl(
        self,
        base_url: str,
        instructions: str,
        max_depth: Optional[int] = None,
        max_breadth: Optional[int] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Intelligently crawl a website based on natural language instructions.
        
        This is a powerful tool for navigating complex websites and extracting specific
        information across multiple pages. The crawler follows your instructions to find
        and extract relevant content automatically.
        
        Parameters:
        -----------
        base_url : str (REQUIRED)
            The starting URL for the crawl.
            This is where the crawler begins its navigation.
            Examples:
            - "https://docs.python.org/3/"
            - "https://example.com/blog"
            - "https://company.com/products"
            
            Best Practices:
            - Use a relevant starting point close to your target content
            - Ensure the URL is accessible and doesn't require authentication
            - Start from a page with good navigation/links to target content
        
        instructions : str (REQUIRED)
            Natural language instructions telling the crawler what to find.
            Be specific about what content you want and how to identify it.
            
            Examples:
            - "Find all tutorial pages about asyncio and extract the code examples"
            - "Navigate to the pricing page and extract all plan details"
            - "Find all blog posts about machine learning from 2024"
            - "Look for documentation pages about API authentication"
            - "Extract all product descriptions from the catalog"
            
            Tips for effective instructions:
            - Be specific about what content to look for
            - Mention keywords or identifiers (headings, sections, etc.)
            - Specify what to extract (text, links, tables, etc.)
            - Include constraints (dates, categories, etc.)
        
        max_depth : int (optional)
            Maximum depth to traverse from the base URL.
            Depth = number of clicks/links away from base_url
            - Depth 1: Only direct links from base_url
            - Depth 2: Links from base_url and links from those pages
            - Depth 3: Three levels deep, etc.
            
            Recommendations:
            - Small sites: 2-3
            - Medium sites: 3-5
            - Large sites: 5-10
            - Default: Usually 3-5 if not specified
        
        max_breadth : int (optional)
            Maximum number of links to follow per level.
            Controls how many pages at each depth level to explore.
            
            Recommendations:
            - Focused crawl: 5-10
            - Moderate crawl: 10-20
            - Broad crawl: 20-50
            - Helps limit API usage and processing time
        
        limit : int (optional)
            Total number of pages to process before stopping.
            Hard limit on total pages crawled regardless of depth/breadth.
            
            Use this to:
            - Control API costs
            - Limit processing time
            - Prevent excessive crawling
            
            Typical values: 10-100 pages
        
        Returns:
        --------
        Dict containing:
            - results: List of extracted content matching your instructions
                - url: Page URL
                - content: Extracted content based on instructions
                - depth: How far from base_url this page is
            - pages_crawled: Total number of pages processed
            - pages_matched: Number of pages matching instructions
            - crawl_time: Time taken for the crawl
        
        Examples:
        ---------
        1. Find specific documentation:
           tavily_crawl(
               base_url="https://docs.python.org/3/",
               instructions="Find all pages about asyncio and extract the main concepts and code examples",
               max_depth=3,
               limit=20
           )
        
        2. Extract blog posts:
           tavily_crawl(
               base_url="https://example.com/blog",
               instructions="Find all blog posts from 2024 about AI and extract titles, dates, and summaries",
               max_depth=2,
               max_breadth=10
           )
        
        3. Product catalog extraction:
           tavily_crawl(
               base_url="https://shop.example.com/products",
               instructions="Extract product names, prices, and descriptions from all product pages",
               max_depth=2,
               limit=50
           )
        
        Use Cases:
        ----------
        - Extracting structured data from documentation sites
        - Gathering articles/posts from blogs
        - Collecting product information from e-commerce sites
        - Building datasets from specific website sections
        - Research and competitive analysis
        - Content aggregation and monitoring
        """
        payload = {
            "api_key": self.api_key,
            "base_url": base_url,
            "instructions": instructions
        }
        
        if max_depth is not None:
            payload["max_depth"] = max_depth
        if max_breadth is not None:
            payload["max_breadth"] = max_breadth
        if limit is not None:
            payload["limit"] = limit
        
        return await self._make_request("crawl", payload)
    
    async def tavily_map(
        self,
        url: str,
        instructions: Optional[str] = None,
        max_depth: Optional[int] = None,
        max_breadth: Optional[int] = None,
        limit: Optional[int] = None,
        select_paths: Optional[List[str]] = None,
        select_domains: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        allow_external: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive site map by traversing a website like a graph.
        
        Use this tool to discover and map the structure of a website. Perfect for
        understanding site architecture, finding all pages, or discovering hidden content.
        
        Parameters:
        -----------
        url : str (REQUIRED)
            The root URL to begin mapping.
            This is the starting point for site map generation.
            Examples:
            - "https://example.com"
            - "https://docs.project.org"
            - "https://blog.company.com"
        
        instructions : str (optional)
            Natural language instructions to guide the mapping process.
            Use to focus the map on specific types of pages or sections.
            
            Examples:
            - "Map all documentation pages"
            - "Find all pages in the blog section"
            - "Discover all product pages"
            - "Map the entire site structure"
        
        max_depth : int (optional)
            Maximum depth to traverse from the root URL.
            Controls how deep into the site hierarchy to explore.
            
            Recommendations:
            - Quick map: 1-2
            - Standard map: 3-5
            - Deep map: 5-10
            - Full site: 10+
        
        max_breadth : int (optional)
            Maximum number of links to follow per level.
            Controls horizontal exploration at each depth.
            
            Recommendations:
            - Focused: 10-20
            - Moderate: 20-50
            - Comprehensive: 50-100+
        
        limit : int (optional)
            Total number of links to process before stopping.
            Hard cap on total URLs mapped.
            
            Use to control scope and costs.
            Typical values: 50-500 URLs
        
        select_paths : List[str] (optional)
            Regex patterns to select specific URL paths.
            Only URLs matching these patterns will be included.
            
            Examples:
            - ["^/blog/.*"] : Only blog pages
            - ["^/docs/.*", "^/api/.*"] : Only docs and API pages
            - ["^/products/category-.*"] : Specific product categories
            
            Regex tips:
            - ^ = start of path
            - $ = end of path
            - .* = any characters
            - [0-9]+ = one or more digits
        
        select_domains : List[str] (optional)
            Regex patterns to select specific domains or subdomains.
            
            Examples:
            - ["^docs\\.example\\.com$"] : Only docs subdomain
            - ["^.*\\.example\\.com$"] : All subdomains
        
        exclude_paths : List[str] (optional)
            Regex patterns to exclude specific URL paths.
            URLs matching these patterns will be skipped.
            
            Common exclusions:
            - ["^/admin/.*"] : Skip admin pages
            - ["^/login.*", "^/signup.*"] : Skip auth pages
            - ["^/tag/.*", "^/category/.*"] : Skip tag/category pages
            - [".*/page/[0-9]+.*"] : Skip pagination
        
        exclude_domains : List[str] (optional)
            Regex patterns to exclude specific domains.
            
            Examples:
            - ["^external\\.com$"] : Exclude specific external domain
            - ["^ad\\..*"] : Exclude ad-related domains
        
        allow_external : bool (default: False)
            Whether to include external domain links in results.
            
            - False: Only map URLs on the same domain
            - True: Include links to external sites
            
            Use True when:
            - Analyzing site's external link profile
            - Finding all linked resources
            - Building comprehensive link map
        
        Returns:
        --------
        Dict containing:
            - results: List of all discovered URLs
                - url: The discovered URL
                - depth: Distance from root URL
                - links_from: URLs that link to this page
                - links_to: URLs this page links to
            - total_urls: Total number of URLs discovered
            - max_depth_reached: Deepest level explored
            - map_time: Time taken to generate map
        
        Examples:
        ---------
        1. Basic site map:
           tavily_map(url="https://example.com")
        
        2. Map documentation only:
           tavily_map(
               url="https://docs.example.com",
               select_paths=["^/docs/.*"],
               max_depth=5,
               limit=100
           )
        
        3. Map blog excluding tags:
           tavily_map(
               url="https://blog.example.com",
               exclude_paths=["^/tag/.*", "^/author/.*"],
               max_depth=3
           )
        
        4. Comprehensive site map with external links:
           tavily_map(
               url="https://example.com",
               allow_external=True,
               max_depth=10,
               limit=500
           )
        
        5. Map specific subdomain:
           tavily_map(
               url="https://example.com",
               select_domains=["^api\\.example\\.com$"],
               instructions="Map all API documentation pages"
           )
        
        Use Cases:
        ----------
        - Site structure analysis and visualization
        - SEO audits and broken link detection
        - Content inventory and discovery
        - Competitive analysis
        - Finding orphaned or hidden pages
        - Understanding site navigation patterns
        - Building comprehensive URL lists for testing
        """
        payload = {
            "api_key": self.api_key,
            "url": url,
            "allow_external": allow_external
        }
        
        if instructions:
            payload["instructions"] = instructions
        if max_depth is not None:
            payload["max_depth"] = max_depth
        if max_breadth is not None:
            payload["max_breadth"] = max_breadth
        if limit is not None:
            payload["limit"] = limit
        if select_paths:
            payload["select_paths"] = select_paths
        if select_domains:
            payload["select_domains"] = select_domains
        if exclude_paths:
            payload["exclude_paths"] = exclude_paths
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        
        return await self._make_request("map", payload)


# Tool schemas for OpenAI function calling
TAVILY_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": """Search the web for current information, news, facts, or any real-time data. 
            
This is the PRIMARY tool for finding information on the internet. Use it for:
- Current events and news
- Facts and statistics
- Research questions
- Product information
- Technical documentation
- Any question requiring up-to-date information

BEST PRACTICES:
1. Query Formulation: Use specific, clear search terms. Add context words like "2024", "latest", "current" for time-sensitive queries.
2. Topic Selection: Use 'news' for breaking news/current events, 'finance' for stocks/markets, 'general' for everything else.
3. Search Depth: Start with 'basic' (1 credit). Only use 'advanced' (2 credits) when high accuracy is critical or basic results are insufficient.
4. Results Count: Use 3-5 results for quick answers, 5-10 for comprehensive research, 10+ only for in-depth analysis.
5. Include Answer: Set to 'true' or 'basic' when user needs a direct summary. Use 'advanced' for complex questions requiring detailed analysis.
6. Time Filtering: Always use 'time_range' for queries about "recent", "latest", "today", or specific time periods. Use 'day' for breaking news, 'week' for recent updates, 'month' for current trends.
7. Domain Filtering: Use 'include_domains' for authoritative sources (e.g., ['wikipedia.org', 'nature.com', 'arxiv.org'] for research). Use 'exclude_domains' to filter unreliable sources.
8. Raw Content: Only set 'include_raw_content' to 'markdown' or 'text' if you need full article text for detailed analysis. This increases response time and size.
9. Country Filtering: Use 'country' parameter when query is region-specific (e.g., "Japan news", "UK weather").
10. Cost Optimization: Basic search is sufficient for 80% of queries. Reserve advanced search for critical research.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query. Be specific and clear. Examples: 'latest AI breakthroughs 2024', 'Python asyncio best practices', 'current Bitcoin price'"
                    },
                    "topic": {
                        "type": "string",
                        "enum": ["general", "news", "finance"],
                        "description": "Search category: 'general' for broad searches, 'news' for current events from mainstream media, 'finance' for financial data",
                        "default": "general"
                    },
                    "search_depth": {
                        "type": "string",
                        "enum": ["basic", "advanced"],
                        "description": "Search depth: 'basic' (1 credit, faster) for general queries, 'advanced' (2 credits) for detailed research requiring high accuracy",
                        "default": "basic"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return (0-20). Use 5-10 for most queries, more for comprehensive research",
                        "minimum": 0,
                        "maximum": 20,
                        "default": 5
                    },
                    "include_answer": {
                        "type": "string",
                        "enum": ["false", "true", "basic", "advanced"],
                        "description": "Include LLM-generated answer: 'false' for no answer, 'true'/'basic' for quick summary, 'advanced' for detailed answer",
                        "default": "false"
                    },
                    "time_range": {
                        "type": "string",
                        "enum": ["day", "week", "month", "year"],
                        "description": "Filter by publish date. Use for time-sensitive queries: 'day' for last 24h, 'week' for 7 days, 'month' for 30 days, 'year' for 365 days"
                    },
                    "include_raw_content": {
                        "type": "string",
                        "enum": ["false", "true", "markdown", "text"],
                        "description": "Include full page content: 'false' for no content, 'true'/'markdown' for formatted content, 'text' for plain text"
                    },
                    "include_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Only include results from these domains. Example: ['wikipedia.org', 'nature.com'] for authoritative sources"
                    },
                    "exclude_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Exclude results from these domains. Example: ['example.com'] to filter out specific sites"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tavily_extract",
            "description": """Extract clean, structured content from specific web pages.

Use this tool when you:
- Have specific URLs and need their content
- Want to read full articles or documentation
- Need to extract text from multiple pages
- Want clean content without HTML/ads/navigation

This is ideal AFTER searching to get full content from relevant pages.

BEST PRACTICES:
1. URL Validation: Ensure URLs are valid, publicly accessible, and don't require authentication/login.
2. Batch Processing: Extract multiple related URLs in a single call for efficiency (e.g., all results from a search).
3. Optimal Batch Size: 3-5 URLs per request for balance between speed and comprehensiveness. Avoid exceeding 10-20 URLs.
4. Sequential Workflow: Typically use tavily_search first to find URLs, then tavily_extract to get full content.
5. URL Selection: Prioritize high-relevance URLs (higher scores from search results) to avoid unnecessary extractions.
6. Error Handling: Some URLs may fail to extract (paywalls, dynamic content, etc.). Always check the response for failed_results.
7. Content Size: Extracted content can be large. Only extract when you need the full text, not just snippets.
8. Use Case Matching: Use for articles, blogs, documentation, and static content. Not ideal for dynamic SPAs or JavaScript-heavy sites.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to extract content from. Can extract multiple URLs in one request. Example: ['https://example.com/article1', 'https://example.com/article2']"
                    }
                },
                "required": ["urls"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tavily_crawl",
            "description": """Intelligently crawl a website based on natural language instructions.

Use this tool to:
- Navigate complex websites automatically
- Extract specific information across multiple pages
- Follow links based on your instructions
- Gather structured data from websites

Perfect for extracting content from documentation, blogs, or product catalogs when you know the starting point.

BEST PRACTICES:
1. Clear Instructions: Be very specific about what to find. Include keywords, section names, or identifiers. Bad: "find info". Good: "find all tutorial pages about asyncio and extract code examples".
2. Starting Point: Choose a base_url close to your target content. Start from category/section pages, not the homepage.
3. Scope Control: Always set 'limit' to prevent excessive crawling. Start with 10-20 pages for focused tasks, 50-100 for broader tasks.
4. Depth Strategy: Use depth 2-3 for focused crawls, 3-5 for moderate exploration. Deeper = more pages = higher cost.
5. Breadth Management: Set max_breadth (10-20) to limit links per level. Prevents following every single link on large pages.
6. Instruction Specificity: Include what to extract (titles, descriptions, code, etc.) and how to identify it (URLs containing X, pages with heading Y).
7. Cost Awareness: Crawling can consume many API credits. Start small, check results, then expand if needed.
8. Use Case Selection: Use for structured content extraction, not general exploration. For site structure, use tavily_map instead.
9. Time Constraints: Mention date ranges or version numbers in instructions if relevant (e.g., "articles from 2024").
10. Validation: Review crawl results to ensure instructions were interpreted correctly before using for analysis.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_url": {
                        "type": "string",
                        "description": "Starting URL for the crawl. Example: 'https://docs.python.org/3/'"
                    },
                    "instructions": {
                        "type": "string",
                        "description": "Natural language instructions for what to find and extract. Be specific. Example: 'Find all tutorial pages about asyncio and extract code examples'"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth from base URL (number of clicks away). Recommended: 2-5 for focused crawls"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum total pages to process. Recommended: 10-50 to control costs"
                    }
                },
                "required": ["base_url", "instructions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tavily_map",
            "description": """Generate a comprehensive site map by discovering all pages on a website.

Use this tool to:
- Understand website structure
- Discover all pages on a site
- Find hidden or hard-to-reach pages
- Analyze site organization
- Build comprehensive URL lists

Great for site analysis, SEO audits, or when you need to know what pages exist on a domain.

BEST PRACTICES:
1. Purpose Clarity: Use for site STRUCTURE discovery, not content extraction. For content, use tavily_crawl instead.
2. Root URL Selection: Start from the domain root or main section (e.g., 'https://example.com' or 'https://docs.example.com').
3. Limit Setting: ALWAYS set a 'limit' to control scope and costs. Use 50-100 for small sites, 100-500 for medium, 500+ for large sites.
4. Depth Planning: Use depth 2-3 for quick overview, 5-7 for comprehensive mapping, 10+ for complete site architecture.
5. Path Filtering: Use 'select_paths' to focus on specific sections. Example: ['^/docs/.*'] for documentation only. This dramatically reduces unnecessary crawling.
6. Exclusion Strategy: Always exclude admin, login, tag, category, and pagination URLs using 'exclude_paths': ['^/admin/.*', '^/login.*', '.*/page/[0-9]+.*', '^/tag/.*'].
7. Domain Control: Set 'allow_external' to false (default) to stay on the same domain. Only use true for external link analysis.
8. Regex Patterns: Use proper regex. '^' = start, '$' = end, '.*' = any chars, '[0-9]+' = numbers. Test patterns before use.
9. Instruction Guidance: Use 'instructions' to guide what types of pages to prioritize or focus on.
10. Incremental Approach: Start with small limit and focused paths. Expand based on initial results. Large maps can be expensive.
11. Performance Consideration: Mapping is slower than other operations. Set reasonable expectations and limits.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Root URL to begin mapping. Example: 'https://example.com'"
                    },
                    "instructions": {
                        "type": "string",
                        "description": "Optional instructions to guide the mapping. Example: 'Map all documentation pages'"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth to explore. Recommended: 3-5 for standard maps, 10+ for comprehensive"
                    },
                    "select_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Regex patterns to include only specific paths. Example: ['^/blog/.*'] for blog pages only"
                    },
                    "exclude_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Regex patterns to exclude paths. Example: ['^/admin/.*', '^/login.*'] to skip admin/login pages"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum URLs to map. Recommended: 50-500 depending on site size"
                    },
                    "allow_external": {
                        "type": "boolean",
                        "description": "Include external domain links. Set true for external link analysis",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        }
    }
]


if __name__ == "__main__":
    import asyncio
    
    async def test_tools():
        """Test Tavily tools"""
        tools = TavilyTools()
        
        print("Testing Tavily Search...")
        result = await tools.tavily_search(
            query="What is LangGraph?",
            max_results=3,
            include_answer=True
        )
        print(f"Search completed: {len(result.get('results', []))} results")
        if result.get('answer'):
            print(f"Answer: {result['answer'][:200]}...")
        
        print("\n" + "="*50 + "\n")
        
        print("Testing Tavily Extract...")
        if result.get('results'):
            first_url = result['results'][0]['url']
            extract_result = await tools.tavily_extract(urls=[first_url])
            print(f"Extracted content from: {first_url}")
            print(f"Content length: {len(str(extract_result))}")
        
        print("\nAll tests completed!")
    
    asyncio.run(test_tools())

