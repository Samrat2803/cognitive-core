"""
Entity extraction utilities using GPT-5 for intelligent extraction.

Extract people, organizations, events, and claims from text using LLM reasoning.
"""

import re
from typing import Dict, List, Any
from datetime import datetime
from shared.llm_factory import LLMFactory


# Create LLM instance for entity extraction
_llm = None

def get_llm():
    """Get or create LLM instance"""
    global _llm
    if _llm is None:
        _llm = LLMFactory.create_llm(
            model="gpt-5",
            max_tokens=1000,
            reasoning_effort="low",
            verbosity="low"
        )
    return _llm


def extract_entities_from_text(text: str, content_type: str = "general") -> List[Dict[str, str]]:
    """
    Extract named entities from text using GPT-5 reasoning.
    
    Uses the same investigative approach as manual curl investigation.
    Returns list of entities with name and type.
    """
    # Limit text length
    text = text[:2000] if len(text) > 2000 else text
    
    # Use GPT-5 to extract entities with context awareness
    prompt = f"""You are an investigative journalist analyzing Nepal Gen Z protests (September 2025).

From this text, extract ONLY the most relevant entities:

TEXT: {text}

Extract and list:
1. KEY ORGANIZATIONS (NGOs, media companies, protest organizers) - especially those organizing or funding protests
2. KEY PEOPLE (leaders, organizers, officials) - only those with significant roles
3. FUNDERS (who provides money/support)

Format each as: TYPE | NAME
Examples:
organization | Hami Nepal
person | Sudan Gurung
funder | NED

Only extract entities DIRECTLY related to Nepal protests. Skip generic names, article titles, or irrelevant mentions.
Be concise. List 5-10 max."""

    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        
        # Parse LLM response (GPT-5 returns list of dicts with 'text' key)
        entities = []
        
        # Extract text from GPT-5 response
        if hasattr(response, 'content'):
            content = response.content
            # GPT-5 format: [{'type': 'text', 'text': '...', 'annotations': []}]
            if isinstance(content, list) and len(content) > 0:
                content = content[0].get('text', '')
            else:
                content = str(content)
        else:
            content = str(response)
        
        # Parse entities from text
        for line in content.split('\n'):
            line = line.strip()
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    entity_type = parts[0].strip().lower()
                    entity_name = parts[1].strip()
                    
                    # Validate type
                    if entity_type in ['organization', 'person', 'funder', 'event']:
                        entities.append({
                            "name": entity_name,
                            "type": entity_type
                        })
        
        return entities[:10]  # Limit to top 10
        
    except Exception as e:
        print(f"  ⚠️  Entity extraction error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to simple keyword extraction
        return extract_entities_fallback(text)


def extract_entities_fallback(text: str) -> List[Dict[str, str]]:
    """Fallback: Simple keyword extraction if LLM fails"""
    entities = []
    
    # Key organizations known from manual investigation
    key_orgs = ["Hami Nepal", "Pavilion Media", "NED", "USAID"]
    for org in key_orgs:
        if org.lower() in text.lower():
            entities.append({"name": org, "type": "organization" if org not in ["NED", "USAID"] else "funder"})
    
    # Key people
    key_people = ["Sudan Gurung", "Deepak Bhatta", "K.P. Sharma Oli"]
    for person in key_people:
        if person.lower() in text.lower():
            entities.append({"name": person, "type": "person"})
    
    return entities


def extract_facts_from_results(results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extract factual statements from search results.
    
    Returns list of facts with source URLs.
    """
    facts = []
    
    for result in results:
        content = result.get("content", "")
        url = result.get("url", "")
        
        # Extract sentences with factual indicators
        sentences = content.split(". ")
        
        for sentence in sentences:
            # Fact indicators
            if any(indicator in sentence.lower() for indicator in [
                "registered", "founded", "established", "appointed", "arrested",
                "charged", "funded", "donated", "received", "granted",
                "billion", "million", "percent", "chairman", "ceo", "director"
            ]):
                facts.append({
                    "fact": sentence.strip(),
                    "source": url,
                    "extracted_at": datetime.utcnow().isoformat()
                })
    
    return facts


def create_entity_record(name: str, entity_type: str = "unknown", 
                        importance: float = 0.5) -> Dict[str, Any]:
    """
    Create a new entity record with default values.
    """
    return {
        "name": name,
        "type": entity_type,
        "importance": importance,
        "investigated": False,
        "confidence": 0.0,
        "facts": [],
        "claims": [],
        "connections": [],
        "sources": [],
        "investigation_attempts": 0,
        "blocked_methods": [],
        "background": "",
        "current_role": "",
        "funders": [],
        "funding_traced": False,
        "corruption_charges": False,
        "arms_dealer": False
    }


def extract_funding_entities(results: List[Dict[str, Any]]) -> List[str]:
    """
    Extract names of funding organizations from search results.
    """
    funders = []
    
    funding_keywords = [
        "funded by", "funding from", "sponsored by", "grants from",
        "donated by", "supported by", "financial support from"
    ]
    
    for result in results:
        content = result.get("content", "")
        
        for keyword in funding_keywords:
            if keyword in content.lower():
                # Extract entity name after keyword
                pattern = rf"{keyword}\s+([A-Z][a-zA-Z\s&,]+?)(?:\.|,|;|\s+and|\s+or)"
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    funder_name = match.group(1).strip()
                    if len(funder_name) > 3:  # Filter out short matches
                        funders.append(funder_name)
    
    return list(set(funders))


def extract_timeline_events(results: List[Dict[str, Any]], cutoff_date: str = None) -> List[Dict[str, Any]]:
    """
    Extract events with dates from search results.
    
    Returns chronologically sorted list of events.
    """
    events = []
    
    # Date patterns
    date_patterns = [
        r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
        r'(\d{4}-\d{2}-\d{2})'
    ]
    
    for result in results:
        content = result.get("content", "")
        url = result.get("url", "")
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0)
                # Get surrounding text as event description
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]
                
                events.append({
                    "date": date_str,
                    "description": context.strip(),
                    "sources": [url],
                    "major_event": False,
                    "cause_identified": False
                })
    
    # Sort by date (simplified)
    events.sort(key=lambda x: x["date"])
    
    return events

