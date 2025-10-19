"""
Smart Domain Classifier - Decides crawling strategy per domain
"""

from typing import Dict, Literal
from urllib.parse import urlparse


class DomainClassifier:
    """
    Classify domains to determine crawling strategy
    
    Categories:
    - AUTHORITY: Government/official sites → Crawl entire domain
    - NEWS: News/media sites → Crawl only specific articles
    - ORGANIZATION: Companies/NGOs → Crawl entire domain
    - UNKNOWN: Other sites → Crawl specific pages only
    """
    
    # Authority indicators (crawl entire domain)
    AUTHORITY_INDICATORS = [
        'gov.in', 'nic.in', 'gov.uk', 'gov.au', '.gov',
        'who.int', 'fda.gov', 'ema.europa.eu',
        'cdsco.gov.in', 'dcgi.gov.in', 'mohfw.gov.in',
        'nppa.gov.in', 'icmr.gov.in', 'dbtindia.gov.in'
    ]
    
    # News sites (crawl specific articles only)
    NEWS_INDICATORS = [
        'bbc.com', 'bbc.co.uk', 'cnn.com', 'reuters.com', 
        'bloomberg.com', 'npr.org', 'nytimes.com', 'theguardian.com',
        'timesofindia.com', 'hindustantimes.com', 'indianexpress.com',
        'thehindu.com', 'ndtv.com', 'news18.com',
        '/news/', '/article/', '/story/', '/press-release/'
    ]
    
    # Research/Academic (crawl entire domain)
    RESEARCH_INDICATORS = [
        '.edu', '.ac.uk', '.ac.in',
        'nih.gov', 'pubmed', 'scholar.google',
        'researchgate.net', 'arxiv.org'
    ]
    
    @classmethod
    def classify_domain(cls, url: str) -> Dict[str, any]:
        """
        Classify a URL and determine crawling strategy
        
        Returns:
            {
                "domain": "example.com",
                "type": "AUTHORITY" | "NEWS" | "ORGANIZATION" | "UNKNOWN",
                "strategy": "FULL_DOMAIN" | "SPECIFIC_URL",
                "confidence": 0.0-1.0,
                "reason": "explanation"
            }
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            full_url = url.lower()
            
            # Check for authority domains
            for indicator in cls.AUTHORITY_INDICATORS:
                if indicator in domain:
                    return {
                        "domain": domain,
                        "type": "AUTHORITY",
                        "strategy": "FULL_DOMAIN",
                        "confidence": 0.95,
                        "reason": f"Government/official domain: {indicator}"
                    }
            
            # Check for research/academic
            for indicator in cls.RESEARCH_INDICATORS:
                if indicator in domain:
                    return {
                        "domain": domain,
                        "type": "RESEARCH",
                        "strategy": "FULL_DOMAIN",
                        "confidence": 0.90,
                        "reason": f"Research/academic domain: {indicator}"
                    }
            
            # Check for news sites
            for indicator in cls.NEWS_INDICATORS:
                if indicator in domain or indicator in path or indicator in full_url:
                    return {
                        "domain": domain,
                        "type": "NEWS",
                        "strategy": "SPECIFIC_URL",
                        "confidence": 0.85,
                        "reason": f"News/media site: {indicator}"
                    }
            
            # Default: specific URL only for unknown domains
            return {
                "domain": domain,
                "type": "UNKNOWN",
                "strategy": "SPECIFIC_URL",
                "confidence": 0.50,
                "reason": "Unknown domain type - crawl specific URL only"
            }
            
        except Exception as e:
            return {
                "domain": url,
                "type": "UNKNOWN",
                "strategy": "SPECIFIC_URL",
                "confidence": 0.0,
                "reason": f"Error parsing URL: {e}"
            }
    
    @classmethod
    def should_map_domain(cls, url: str) -> bool:
        """Quick check: should we map the entire domain?"""
        classification = cls.classify_domain(url)
        return classification["strategy"] == "FULL_DOMAIN"


if __name__ == "__main__":
    # Test cases
    test_urls = [
        "https://cdsco.gov.in/regulations/drug-approval",
        "https://www.reuters.com/business/healthcare-pharmaceuticals/cough-syrup-crisis",
        "https://timesofindia.indiatimes.com/india/drug-contamination-news/articleshow/12345.cms",
        "https://mohfw.gov.in/",
        "https://www.bbc.com/news/world-asia-india-12345678",
        "https://www.nih.gov/research",
        "https://example-pharma-company.com/products"
    ]
    
    print("🧠 DOMAIN CLASSIFICATION TEST")
    print("=" * 80)
    
    for url in test_urls:
        result = DomainClassifier.classify_domain(url)
        print(f"\n📍 {url}")
        print(f"   Type: {result['type']}")
        print(f"   Strategy: {result['strategy']}")
        print(f"   Confidence: {result['confidence']:.0%}")
        print(f"   Reason: {result['reason']}")

