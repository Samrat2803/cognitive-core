"""
Tender Parser Node - Parse structured tender data from crawled content
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from state import CognitiveCrawlerState
from tools.tender_utils import parse_tender_content
from tools.mongodb_handler import TenderMongoDBHandler


async def tender_parser(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Parse tender data from crawled content and store in MongoDB
    
    Extracts:
    - Tender ID
    - Title
    - Organization
    - Dates (published, closing, opening)
    - Value (if available)
    - Location
    - Category
    """
    
    crawl_results = state.get("crawl_results", [])
    
    print(f"\n📝 Tender Parser: Parsing {len(crawl_results)} crawled pages...")
    
    state["execution_log"].append({
        "step": "tender_parser",
        "action": f"Parsing tenders from {len(crawl_results)} pages"
    })
    
    all_tenders = []
    
    try:
        for result in crawl_results:
            if not result.get("success", False):
                continue
            
            content = result.get("content", "")
            url = result.get("url", "")
            
            # Parse tenders from content
            tenders = parse_tender_content(content, url)
            all_tenders.extend(tenders)
        
        print(f"   📊 Parsed {len(all_tenders)} tenders")
        
        # Store in MongoDB
        if all_tenders:
            db_handler = TenderMongoDBHandler()
            db_handler.store_tenders(all_tenders)
            print(f"   ✅ Stored {len(all_tenders)} tenders in MongoDB")
        
        state["tenders_parsed"] = all_tenders
        state["tenders_stored"] = len(all_tenders)
        
    except Exception as e:
        error_msg = f"tender_parser error: {str(e)}"
        print(f"   ❌ {error_msg}")
        state["error_log"].append(error_msg)
        state["tenders_parsed"] = []
        state["tenders_stored"] = 0
    
    return state

