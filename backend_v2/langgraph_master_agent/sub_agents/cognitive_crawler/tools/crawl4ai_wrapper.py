"""
Crawl4AI Wrapper - Browser-based crawling with anti-scraping bypass
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import List, Dict
from config import CRAWL_TIMEOUT
from bs4 import BeautifulSoup
import httpx

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
    print("✅ Crawl4AI available - using browser emulation")
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("⚠️  Crawl4AI not found - using httpx fallback")


def extract_clean_text_from_html(html: str) -> str:
    """
    Extract clean text from HTML, removing navigation/UI noise
    
    Uses BeautifulSoup to:
    1. Find main content area (article, main, etc.)
    2. Remove script, style, nav, footer, etc.
    3. Extract and clean text
    
    Returns:
        Clean text content without UI noise
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to find main content area (common HTML5 tags)
    main_content = None
    for selector in ['article', 'main', '[role="main"]', '.article-content', '.post-content', '.content']:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    if not main_content:
        # Fallback to body if no specific content tag found
        main_content = soup.body or soup
    
    # Remove unwanted elements (navigation, UI, scripts, etc.)
    for element in main_content([
        'script', 'style', 'nav', 'footer', 'header', 'aside', 
        'iframe', 'button', 'form', 'noscript', 'svg'
    ]):
        element.decompose()
    
    # Get text
    text = main_content.get_text(separator='\n', strip=True)
    
    # Clean up extra whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = '\n'.join(lines)
    
    return clean_text


async def fast_httpx_crawl(url: str, timeout: int = 10) -> Dict:
    """
    FAST crawling using httpx (2-3 seconds per URL)
    
    Use this first before falling back to Crawl4AI.
    Works for most static/simple sites.
    
    Returns:
        Dict with 'url', 'success', 'content', 'html', 'fast_method': True
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                html = response.text
                clean_content = extract_clean_text_from_html(html)
                
                # Check if we got meaningful content (not just error page)
                if len(clean_content) > 500:  # At least 500 chars
                    return {
                        'url': url,
                        'success': True,
                        'content': clean_content,
                        'html': html,
                        'status_code': 200,
                        'fast_method': True
                    }
            
            # If we get here, it failed or content too short
            return {
                'url': url,
                'success': False,
                'content': '',
                'error': f'HTTP {response.status_code} or insufficient content',
                'fast_method': True
            }
            
    except Exception as e:
        return {
            'url': url,
            'success': False,
            'content': '',
            'error': str(e),
            'fast_method': True
        }


async def crawl_single_page(url: str) -> Dict:
    """
    Crawl a single page with intelligent fallback strategy:
    1. Try fast httpx (2-3s) - works for most sites
    2. Fall back to Crawl4AI (10-15s) - for JavaScript-heavy sites
    """
    
    print(f"      Crawling: {url}")
    
    # STEP 1: Try fast httpx first
    result = await fast_httpx_crawl(url, timeout=5)
    
    if result['success']:
        print(f"         ⚡ Fast httpx success!")
        return result
    
    # STEP 2: Fall back to Crawl4AI for JavaScript-heavy sites
    print(f"         🔄 Trying Crawl4AI (JS-heavy site)...")
    
    if CRAWL4AI_AVAILABLE:
        try:
            # Configure browser for stealth mode
            browser_config = BrowserConfig(
                browser_type="chromium",
                headless=True,
                verbose=False
            )
            
            # Configure crawler - wait longer for JavaScript content to load
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                page_timeout=CRAWL_TIMEOUT * 1000,  # Convert to ms
                # Wait longer for JavaScript/AJAX content
                delay_before_return_html=8.0,  # Wait 8 seconds for dynamic content
                js_code="""
                    // Scroll to trigger lazy loading
                    window.scrollTo(0, document.body.scrollHeight);
                    // Wait a bit more
                    await new Promise(r => setTimeout(r, 2000));
                """
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=crawler_config)
                
                # Extract clean text from HTML (not markdown, which is broken)
                clean_content = extract_clean_text_from_html(result.html) if result.html else ""
                
                return {
                    'url': url,
                    'success': result.success,
                    'content': clean_content,  # Clean text without UI noise
                    'html': result.html,
                    'status_code': 200 if result.success else None
                }
                
        except Exception as e:
            print(f"      ❌ Crawl4AI error: {e}")
            return {
                'url': url,
                'success': False,
                'content': '',
                'error': str(e)
            }
    
    # If Crawl4AI not available, return the failed fast_httpx result
    return result


async def crawl_multiple_pages(urls: List[str], parallel: bool = True) -> List[Dict]:
    """
    Crawl multiple pages with PARALLEL execution
    
    Args:
        urls: List of URLs to crawl
        parallel: If True, crawl all URLs concurrently (much faster!)
                 If False, crawl sequentially with rate limiting
    
    Returns:
        List of crawl results
    """
    import asyncio
    
    if parallel:
        # PARALLEL: Crawl all URLs at once! 🚀
        print(f"   🚀 Parallel crawling {len(urls)} URLs...")
        results = await asyncio.gather(*[crawl_single_page(url) for url in urls])
        return list(results)
    else:
        # SEQUENTIAL: One at a time (old behavior)
        results = []
        for i, url in enumerate(urls, 1):
            print(f"   Crawling page {i}/{len(urls)}")
            result = await crawl_single_page(url)
            results.append(result)
            
            # Rate limiting
            if i < len(urls):
                await asyncio.sleep(2)
        
        return results

