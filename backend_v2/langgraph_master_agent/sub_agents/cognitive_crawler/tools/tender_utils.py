"""
Content Parsing Utilities - Extract structured data from web pages
"""

import re
from typing import List, Dict
from datetime import datetime
from urllib.parse import urlparse


def parse_tender_content(content: str, url: str) -> List[Dict]:
    """
    Parse content from crawled web page
    
    Generic parsing that works for any content, not just tenders
    
    Args:
        content: Text content from crawled page
        url: Source URL
        
    Returns:
        List of content dictionaries (usually just one for generic crawling)
    """
    
    # For generic crawling, just return the content as-is
    # The content_processor node will handle chunking
    parsed = [{
        'url': url,
        'domain': extract_domain_from_url(url),
        'title': extract_title_from_content(content),
        'organization': extract_org_from_url(url),
        'crawled_at': datetime.now().isoformat(),
        'content': content
    }]
    
    return parsed


def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url: Web page URL
        
    Returns:
        Domain name (e.g., "docs.python.org")
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return "unknown"


def extract_title_from_content(content: str) -> str:
    """
    Try to extract a title from content
    
    Args:
        content: Page content
        
    Returns:
        Extracted or generated title
    """
    # Try to find <title> tag if HTML
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if title_match:
        return title_match.group(1).strip()
    
    # Try to find first heading
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    if h1_match:
        # Remove HTML tags
        title = re.sub(r'<[^>]+>', '', h1_match.group(1))
        return title.strip()
    
    # Fall back to first line or first few words
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) > 10:  # Meaningful line
            return line[:100]  # First 100 chars
    
    return "Untitled"


def extract_org_from_url(url: str) -> str:
    """
    Extract organization/site name from URL
    
    Args:
        url: Web page URL
        
    Returns:
        Organization name
    """
    
    domain = extract_domain_from_url(url)
    
    # Known mappings for common sites
    org_mapping = {
        'docs.python.org': 'Python Documentation',
        'github.com': 'GitHub',
        'stackoverflow.com': 'Stack Overflow',
        'wikipedia.org': 'Wikipedia',
        'medium.com': 'Medium',
        'dev.to': 'DEV Community',
        'eprocure.gov.in': 'Government eProcurement',
        'defproc.gov.in': 'Defence Procurement',
        'gov.in': 'Government of India',
        'nic.in': 'National Informatics Centre'
    }
    
    # Check for exact match
    if domain in org_mapping:
        return org_mapping[domain]
    
    # Check for partial match
    for key, org_name in org_mapping.items():
        if key in domain:
            return org_name
    
    # Extract from domain
    # e.g., "docs.python.org" -> "Python"
    parts = domain.split('.')
    if len(parts) >= 2:
        # Get the main part (before .com/.org/etc)
        main_part = parts[-2]
        return main_part.capitalize()
    
    return domain


def clean_tender_data(tender: Dict) -> Dict:
    """
    Clean and normalize content data
    
    Args:
        tender: Raw content dictionary
        
    Returns:
        Cleaned content dictionary
    """
    
    # Clean up the content
    if 'content' in tender:
        content = tender['content']
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        tender['content'] = content.strip()
    
    return tender


def categorize_tender(tender: Dict) -> str:
    """
    Categorize content based on title and domain
    
    Args:
        tender: Content dictionary
        
    Returns:
        Category string
    """
    
    title = tender.get('title', '').lower()
    domain = tender.get('domain', '').lower()
    
    # Programming/Tech
    if any(word in title or word in domain for word in ['python', 'javascript', 'programming', 'code', 'tutorial', 'docs', 'documentation']):
        return "Programming"
    
    # Government/Procurement
    elif any(word in domain for word in ['gov.in', 'nic.in', 'eprocure', 'tender']):
        return "Government"
    
    # Education
    elif any(word in title or word in domain for word in ['tutorial', 'course', 'learning', 'education']):
        return "Education"
    
    # News/Blog
    elif any(word in domain for word in ['medium', 'blog', 'news']):
        return "Content"
    
    else:
        return "General"


