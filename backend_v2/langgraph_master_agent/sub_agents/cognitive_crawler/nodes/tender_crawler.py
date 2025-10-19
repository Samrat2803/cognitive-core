"""
Tender Crawler Node - Uses Crawl4AI with Tavily Extract fallback
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from state import CognitiveCrawlerState
from tools.crawl4ai_wrapper import crawl_multiple_pages
from tools.tavily_fallback import extract_with_tavily
from config import MAX_PAGES_TO_CRAWL


async def tender_crawler(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Crawl pages using:
    1. Check for existing URLs in database (skip duplicates)
    2. Crawl4AI (FREE, fast) - tries first
    3. Tavily Extract (PAID, reliable) - fallback if Crawl4AI fails
    """
    
    from tools.mongodb_handler import TenderMongoDBHandler
    
    # Get URLs to crawl
    listing_pages = state.get("listing_pages", [])
    
    # If no listing pages from discovery, use default current working URLs
    if not listing_pages:
        listing_pages = [
            "https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page",
            "https://defproc.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
        ]
    
    # Limit pages to crawl
    urls_to_crawl = listing_pages[:MAX_PAGES_TO_CRAWL]
    
    print(f"\n🕷️  Crawler: Checking {len(urls_to_crawl)} pages...")
    
    state["execution_log"].append({
        "step": "tender_crawler",
        "action": f"Crawling {len(urls_to_crawl)} pages"
    })
    
    try:
        # STEP 0: Check for existing URLs in database (DEDUPLICATION)
        db_handler = TenderMongoDBHandler()
        existing_urls = await db_handler.get_existing_urls(urls_to_crawl)
        
        # Filter out already-crawled URLs
        new_urls = [url for url in urls_to_crawl if url not in existing_urls]
        skipped_count = len(urls_to_crawl) - len(new_urls)
        
        if skipped_count > 0:
            print(f"   ♻️  Skipping {skipped_count} already-crawled URLs")
        
        if not new_urls:
            print(f"   ✅ All URLs already in database - nothing to crawl!")
            state["crawl_results"] = []
            return state
        
        print(f"   🆕 Crawling {len(new_urls)} new URLs...")
        print(f"   Strategy: Crawl4AI first, Tavily Extract fallback")
        
        # Step 1: Try Crawl4AI first (FREE)
        print(f"   🤖 Attempting with Crawl4AI...")
        crawl_results = await crawl_multiple_pages(new_urls)
        
        # Check if Crawl4AI got meaningful content
        successful_crawls = []
        failed_urls = []
        
        for result in crawl_results:
            if result.get("success") and len(result.get("content", "")) > 5000:
                # Content looks substantial
                successful_crawls.append(result)
            else:
                # Too short or failed - might be CAPTCHA/blocked
                failed_urls.append(result.get("url"))
        
        print(f"   ✅ Crawl4AI successful: {len(successful_crawls)}/{len(crawl_results)} pages")
        
        # Step 2: Fallback to Tavily Extract for failed URLs
        if failed_urls:
            print(f"   🔄 Falling back to Tavily Extract for {len(failed_urls)} failed pages...")
            
            tavily_results = await extract_with_tavily(failed_urls)
            
            # Add successful tavily extracts to results
            for tavily_result in tavily_results:
                if tavily_result.get("success"):
                    successful_crawls.append(tavily_result)
            
            print(f"   ✅ Tavily Extract recovered: {len(tavily_results)} pages")
        
        state["crawl_results"] = successful_crawls
        print(f"   📊 Total successful: {len(successful_crawls)}/{len(urls_to_crawl)} pages")
        
    except Exception as e:
        error_msg = f"tender_crawler error: {str(e)}"
        print(f"   ❌ {error_msg}")
        state["error_log"].append(error_msg)
        state["crawl_results"] = []
    
    return state

