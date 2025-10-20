"""
Content Processor Node - Generic content processing for any use case
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any, List
from state import CognitiveCrawlerState
from tools.mongodb_handler import TenderMongoDBHandler
from datetime import datetime


async def content_processor(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Process crawled content and prepare for storage
    
    Generic processor that works for ANY content type:
    - Press releases
    - Policy documents
    - Reports
    - Announcements
    - ANY government information
    
    Takes keywords from query to identify relevant sections
    """
    
    crawl_results = state.get("crawl_results", [])
    query = state.get("query", "")
    
    print(f"\n📝 Content Processor: Processing {len(crawl_results)} documents...")
    
    state["execution_log"].append({
        "step": "content_processor",
        "action": f"Processing {len(crawl_results)} crawled documents"
    })
    
    # Extract keywords from query for relevance scoring
    query_keywords = extract_keywords(query)
    print(f"   🔑 Query keywords: {', '.join(query_keywords[:5])}")
    
    processed_documents = []
    
    try:
        for i, result in enumerate(crawl_results, 1):
            if not result.get("success") or not result.get("content"):
                continue
            
            url = result.get("url", "")
            content = result.get("content", "")
            
            # Create document with metadata
            document = {
                "doc_id": f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                "url": url,
                "content": content,
                "content_length": len(content),
                "query_keywords": query_keywords,
                "crawled_at": datetime.now().isoformat(),
                "thread_id": state.get("thread_id"),
                # Extract domain for categorization
                "domain": extract_domain(url),
                # Calculate relevance score based on keyword matches
                "relevance_score": calculate_relevance(content, query_keywords)
            }
            
            processed_documents.append(document)
            
            # Log each processed document
            state["execution_log"].append({
                "step": "content_processor",
                "action": f"Processed: {extract_domain(url)} ({len(content):,} chars)"
            })
        
        print(f"   ✅ Processed {len(processed_documents)} documents")
        
        # Store in MongoDB
        if processed_documents:
            mongodb = TenderMongoDBHandler()
            await mongodb.store_documents(processed_documents)
            print(f"   💾 Stored {len(processed_documents)} documents in MongoDB")
        
        state["tenders_parsed"] = processed_documents  # Reusing field name
        state["tenders_stored"] = len(processed_documents)
        
    except Exception as e:
        error_msg = f"content_processor error: {str(e)}"
        print(f"   ❌ {error_msg}")
        state["error_log"].append(error_msg)
        state["tenders_parsed"] = []
        state["tenders_stored"] = 0
    
    return state


def extract_keywords(query: str) -> List[str]:
    """
    Extract meaningful keywords from user query
    Filters out common words
    """
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                    'of', 'with', 'by', 'from', 'all', 'find', 'get', 'show', 'about'}
    
    words = query.lower().split()
    keywords = [w for w in words if w not in common_words and len(w) > 3]
    
    return keywords


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return "unknown"


def calculate_relevance(content: str, keywords: List[str]) -> float:
    """
    Calculate relevance score based on keyword frequency
    Returns score between 0 and 1
    """
    if not keywords or not content:
        return 0.0
    
    content_lower = content.lower()
    matches = sum(1 for keyword in keywords if keyword in content_lower)
    
    return min(1.0, matches / len(keywords))

