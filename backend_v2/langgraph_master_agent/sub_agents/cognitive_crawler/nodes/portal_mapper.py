"""
Portal Mapper Node - Intelligent mapping with domain classification
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any, List
from urllib.parse import urlparse
from state import CognitiveCrawlerState
from tools.tavily_discovery import map_portal_structure_with_instructions
from tools.domain_classifier import DomainClassifier
from config import MAX_PAGES_TO_MAP


def extract_root_domain(url: str) -> str:
    """
    Extract root domain from any URL
    Example: https://mod.gov.in/en/press-releases/article123 → https://mod.gov.in
    """
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except:
        return url


async def portal_mapper(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Intelligent portal mapping with domain classification
    
    Three-layer intelligence:
    1. Analyze user intent from query (override classifier if needed)
    2. Classify domains (AUTHORITY vs NEWS vs UNKNOWN) - ADVISORY only
    3. Preserve original discovered URLs (highest priority)
    4. Use instructions to get relevant URLs from domains
    
    Strategy (FLEXIBLE based on user intent):
    - If user says "crawl all [domain]" → Map entire domain regardless of type
    - If user says "find articles about X" → Smart classification applies
    - NEWS sites: Only specific article by default, unless intent suggests otherwise
    - AUTHORITY sites: Map entire domain with keyword-based instructions
    - UNKNOWN sites: Only specific URL by default
    """
    
    portals = state.get("portals_discovered", [])
    query = state.get("query", "")
    
    print(f"\n🧠 Intelligent Portal Mapper: Processing {len(portals)} discovered URLs...")
    print(f"   Query: {query[:80]}...")
    
    state["execution_log"].append({
        "step": "portal_mapper",
        "action": f"Intelligent mapping with domain classification for {len(portals)} URLs"
    })
    
    # Step 0: Detect user intent (override classifier)
    intent = detect_crawl_intent(query)
    print(f"\n   🎯 STEP 0: Intent Detection")
    print(f"      Intent: {intent['type']}")
    print(f"      Reason: {intent['reason']}")
    
    # Step 1: Classify each discovered URL
    print(f"\n   📊 STEP 1: Domain Classification (Advisory)")
    
    classified_urls = []
    for portal in portals[:MAX_PAGES_TO_MAP]:
        url = portal.get("url")
        if not url:
            continue
        
        classification = DomainClassifier.classify_domain(url)
        
        # Override classification based on intent
        if intent['type'] == 'CRAWL_ENTIRE_SITE':
            classification['strategy'] = 'FULL_DOMAIN'
            classification['reason'] = f"User intent override: {intent['reason']}"
        elif intent['type'] == 'CRAWL_SPECIFIC_DOMAIN':
            # Check if this URL's domain matches intent
            if any(domain.lower() in url.lower() for domain in intent.get('target_domains', [])):
                classification['strategy'] = 'FULL_DOMAIN'
                classification['reason'] = f"User requested this domain: {intent['reason']}"
        
        classified_urls.append({
            "url": url,
            "title": portal.get("title", ""),
            "content": portal.get("content", ""),
            "classification": classification,
            "priority": 100  # Original discovered URLs get highest priority
        })
    
    # Group by strategy
    urls_to_crawl_directly = []  # High priority - crawl these specific URLs
    domains_to_map = {}  # Map these domains comprehensively
    
    for item in classified_urls:
        url = item["url"]
        strategy = item["classification"]["strategy"]
        domain_type = item["classification"]["type"]
        
        if strategy == "FULL_DOMAIN":
            # Map the entire domain (AUTHORITY/RESEARCH or user intent override)
            root = extract_root_domain(url)
            if root not in domains_to_map:
                domains_to_map[root] = {
                    "root": root,
                    "type": domain_type,
                    "original_urls": [],
                    "reason": item["classification"]["reason"]
                }
            domains_to_map[root]["original_urls"].append(url)
        else:
            # Only crawl this specific URL (NEWS/UNKNOWN without override)
            urls_to_crawl_directly.append(item)
    
    print(f"      ✅ {len(urls_to_crawl_directly)} specific URLs to crawl")
    print(f"      ✅ {len(domains_to_map)} domains to map comprehensively")
    
    # Step 2: Add specific URLs to crawl list (highest priority)
    all_pages = []
    
    if urls_to_crawl_directly:
        print(f"\n   📍 STEP 2: Adding Specific URLs (Priority 100)")
        for item in urls_to_crawl_directly:
            all_pages.append({
                "url": item["url"],
                "priority": item["priority"],
                "source": "ORIGINAL_DISCOVERY",
                "type": item["classification"]["type"]
            })
            print(f"      + {item['url'][:70]}... [{item['classification']['type']}]")
    
    # Step 3: Map domains with keyword-based instructions
    if domains_to_map:
        print(f"\n   🗺️  STEP 3: Mapping Domains with Instructions")
        
        for i, (root, info) in enumerate(domains_to_map.items(), 1):
            print(f"\n      Domain {i}/{len(domains_to_map)}: {root}")
            print(f"      Type: {info['type']}")
            print(f"      Reason: {info['reason']}")
            
            # Add original URLs first (priority 100)
            for orig_url in info["original_urls"]:
                all_pages.append({
                    "url": orig_url,
                    "priority": 100,
                    "source": "ORIGINAL_DISCOVERY",
                    "type": info['type']
                })
            
            try:
                # Create smart instructions based on query keywords
                instructions = f"Find pages related to: {query}. Prioritize relevant content pages over navigation."
                
                # Map the domain with instructions
                structure = await map_portal_structure_with_instructions(
                    url=root,
                    instructions=instructions
                )
                discovered_pages = structure.get("results", [])
                
                print(f"      🔍 Tavily found {len(discovered_pages)} pages with instructions")
                
                # Filter and prioritize
                for page_url in discovered_pages:
                    # Skip if already added as original
                    if page_url in [orig_url for orig_url in info["original_urls"]]:
                        continue
                    
                    # Basic filtering
                    if all([
                        '#' not in page_url,
                        'javascript' not in page_url.lower(),
                        page_url.startswith('http'),
                        not page_url.endswith(('.pdf', '.jpg', '.png', '.zip', '.doc', '.xls'))
                    ]):
                        # Score relevance based on URL keywords
                        relevance_score = score_url_relevance(page_url, query)
                        
                        all_pages.append({
                            "url": page_url,
                            "priority": relevance_score,
                            "source": "DOMAIN_MAP",
                            "type": info['type']
                        })
                
                print(f"      ✅ Added {len(discovered_pages)} pages from domain")
                
            except Exception as e:
                print(f"      ⚠️  Error mapping: {e}")
                # Still keep the original URLs
    
    # Step 4: Remove duplicates and sort by priority
    seen_urls = set()
    unique_pages = []
    
    # Sort by priority (highest first)
    all_pages.sort(key=lambda x: x['priority'], reverse=True)
    
    for page in all_pages:
        url = page['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_pages.append(page)
    
    # Step 5: Output summary
    print(f"\n   📊 FINAL RESULTS:")
    print(f"      Total unique URLs: {len(unique_pages)}")
    
    original_count = len([p for p in unique_pages if p['source'] == 'ORIGINAL_DISCOVERY'])
    mapped_count = len([p for p in unique_pages if p['source'] == 'DOMAIN_MAP'])
    
    print(f"      - Original discoveries: {original_count} (Priority 100)")
    print(f"      - Domain mapped: {mapped_count} (Prioritized by relevance)")
    
    if unique_pages:
        print(f"\n   🎯 Top 10 URLs by Priority:")
        for i, page in enumerate(unique_pages[:10], 1):
            print(f"      {i}. [{page['priority']}] {page['url'][:60]}... [{page['type']}]")
    
    # Store URLs only (remove metadata for crawler)
    state["listing_pages"] = [page['url'] for page in unique_pages]
    
    state["execution_log"].append({
        "step": "portal_mapper",
        "result": f"Mapped {len(unique_pages)} URLs with intelligent prioritization"
    })
    
    return state


def detect_crawl_intent(query: str) -> Dict[str, Any]:
    """
    Detect user's crawling intent from query
    This OVERRIDES domain classification when user is explicit
    
    Returns:
        {
            "type": "CRAWL_ENTIRE_SITE" | "CRAWL_SPECIFIC_DOMAIN" | "DISCOVER_AND_FILTER",
            "reason": "explanation",
            "target_domains": ["example.com"] if applicable
        }
    """
    query_lower = query.lower()
    
    # Detect "crawl all X" or "scrape all X" intent
    crawl_all_keywords = [
        'crawl all', 'scrape all', 'get all', 'fetch all',
        'crawl entire', 'scrape entire', 'map entire',
        'all articles from', 'all pages from', 'all content from'
    ]
    
    for keyword in crawl_all_keywords:
        if keyword in query_lower:
            # Extract target domain if mentioned
            target_domains = []
            
            # Common domain patterns
            domain_patterns = [
                'times of india', 'timesofindia', 'hindustantimes', 
                'reuters', 'bbc', 'bloomberg', 'npr',
                'cdsco', 'mohfw', 'dcgi', 'fda', 'nih'
            ]
            
            for pattern in domain_patterns:
                if pattern in query_lower:
                    target_domains.append(pattern)
            
            if target_domains:
                return {
                    "type": "CRAWL_SPECIFIC_DOMAIN",
                    "reason": f"User explicitly requested to crawl: {', '.join(target_domains)}",
                    "target_domains": target_domains
                }
            else:
                return {
                    "type": "CRAWL_ENTIRE_SITE",
                    "reason": "User requested comprehensive crawl ('crawl all', 'scrape all', etc.)",
                    "target_domains": []
                }
    
    # Detect "find portals/websites about X" - discovery mode
    discovery_keywords = [
        'find portals', 'find websites', 'discover sites',
        'search for portals', 'locate websites'
    ]
    
    for keyword in discovery_keywords:
        if keyword in query_lower:
            return {
                "type": "DISCOVER_AND_FILTER",
                "reason": "User wants to discover relevant portals (smart filtering applies)",
                "target_domains": []
            }
    
    # Default: smart filtering based on domain classification
    return {
        "type": "DISCOVER_AND_FILTER",
        "reason": "Default mode: discover relevant content with smart classification",
        "target_domains": []
    }


def score_url_relevance(url: str, query: str) -> int:
    """
    Score URL relevance based on query keywords
    Returns: 0-99 (100 reserved for original discoveries)
    """
    url_lower = url.lower()
    query_words = query.lower().split()
    
    score = 50  # Base score for mapped URLs
    
    # Boost for query keywords in URL
    keyword_matches = sum(1 for word in query_words if len(word) > 3 and word in url_lower)
    score += keyword_matches * 10
    
    # Penalize for common navigation URLs
    navigation_indicators = [
        '/about', '/contact', '/privacy', '/terms', '/careers', 
        '/support', '/help', '/faq', '/login', '/signup',
        '/home', '/index', '/sitemap', '/search'
    ]
    
    for indicator in navigation_indicators:
        if indicator in url_lower:
            score -= 20
            break
    
    # Boost for content indicators
    content_indicators = [
        '/article', '/news', '/press', '/release', '/report',
        '/research', '/publication', '/document', '/regulation',
        '/policy', '/guideline', '/announcement'
    ]
    
    for indicator in content_indicators:
        if indicator in url_lower:
            score += 15
            break
    
    # Ensure score is in valid range
    return max(10, min(99, score))

