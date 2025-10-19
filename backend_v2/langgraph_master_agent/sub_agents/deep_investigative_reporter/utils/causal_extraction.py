"""Causal relationship extraction using GPT-5 reasoning"""

from typing import Dict, List, Any
import re
from shared.llm_factory import LLMFactory


# LLM instance for causal analysis
_llm = None

def get_llm():
    """Get or create LLM instance"""
    global _llm
    if _llm is None:
        _llm = LLMFactory.create_llm(
            model="gpt-5",
            max_tokens=800,
            reasoning_effort="low",
            verbosity="low"
        )
    return _llm


def extract_causal_relationships(results: List[Dict[str, Any]], event: Dict[str, str]) -> List[Dict]:
    """
    Extract causal relationships using GPT-5 reasoning.
    
    Asks "why did this event happen?" like a real investigative journalist.
    """
    if not results:
        return []
    
    # Combine content from results
    combined_content = "\n\n".join([
        f"Source: {r.get('title', '')} - {r.get('content', '')[:500]}"
        for r in results[:5]  # Top 5 results
    ])
    
    event_desc = event.get("description", "")
    
    # Use GPT-5 to identify causes
    prompt = f"""You are an investigative journalist analyzing Nepal Gen Z protests.

EVENT: {event_desc}

AVAILABLE INFORMATION:
{combined_content}

Question: What CAUSED this event? What are the underlying reasons and triggers?

List causes in this format:
CAUSE | cause description
CAUSE | another cause

Example:
CAUSE | Social media ban on September 4
CAUSE | Viral nepo kid campaign exposing politicians' children
CAUSE | 20% youth unemployment and economic desperation

Be specific and factual. List 3-5 key causes."""

    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        
        # Parse causes (handle GPT-5 response format)
        relationships = []
        
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
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('CAUSE |') or line.startswith('cause |'):
                cause = line.split('|', 1)[1].strip() if '|' in line else line.replace('CAUSE', '').replace('cause', '').strip()
                
                relationships.append({
                    "cause": cause,
                    "effect": event_desc[:100],
                    "sources": [r.get("url", "") for r in results[:3]],
                    "confidence": 0.8  # High confidence from GPT-5 reasoning
                })
        
        return relationships
        
    except Exception as e:
        print(f"  ⚠️  Causal extraction error: {e}")
        return []


def build_causal_chains(causal_links: List[Dict]) -> List[List[Dict]]:
    """
    Build complete causal chains from individual links.
    
    Example: A → B, B → C  =>  [A, B, C]
    """
    # Build adjacency map
    graph = {}
    for link in causal_links:
        cause = link["cause"]
        effect = link["effect"]
        
        if cause not in graph:
            graph[cause] = []
        graph[cause].append({
            "effect": effect,
            "confidence": link["confidence"],
            "evidence": link.get("evidence", [])
        })
    
    # Find root causes (no incoming edges)
    all_effects = set(link["effect"] for link in causal_links)
    all_causes = set(link["cause"] for link in causal_links)
    root_causes = all_causes - all_effects
    
    # Build chains from roots
    chains = []
    
    def build_chain(node, current_chain, visited):
        """DFS to build chain"""
        if node in visited:
            return
        
        visited.add(node)
        current_chain.append(node)
        
        # If node has effects, continue chain
        if node in graph:
            for next_node in graph[node]:
                build_chain(next_node["effect"], current_chain.copy(), visited)
        else:
            # End of chain
            if len(current_chain) > 1:
                chains.append(current_chain)
    
    for root in root_causes:
        build_chain(root, [], set())
    
    return chains


def identify_root_causes(entities: Dict[str, Any], timeline: List[Dict]) -> List[str]:
    """
    Identify root causes (underlying conditions that enabled the event).
    
    Look for:
    - Economic conditions
    - Political structure issues
    - Historical grievances
    """
    root_causes = []
    
    # Economic indicators
    economic_keywords = ["unemployment", "poverty", "inequality", "economic", "recession"]
    # Political indicators
    political_keywords = ["corruption", "authoritarian", "nepotism", "elite", "ruling class"]
    # Historical indicators
    historical_keywords = ["years of", "decades of", "long history", "systematic"]
    
    for entity_name, entity in entities.items():
        facts = entity.get("facts", [])
        
        for fact in facts:
            fact_text = fact.get("fact", "").lower()
            
            # Check for root cause indicators
            if any(keyword in fact_text for keyword in economic_keywords + political_keywords + historical_keywords):
                root_causes.append(fact_text)
    
    return list(set(root_causes))  # Deduplicate


def calculate_causal_confidence(cause: str, effect: str, evidence: List[str]) -> float:
    """
    Calculate confidence score for a causal relationship.
    
    Factors:
    - Number of sources (more = higher confidence)
    - Quality of sources (.gov, .edu = higher)
    - Temporal proximity (closer in time = higher)
    """
    confidence = 0.3  # Base confidence
    
    # Factor 1: Number of evidence sources
    if len(evidence) >= 3:
        confidence += 0.3
    elif len(evidence) == 2:
        confidence += 0.2
    elif len(evidence) == 1:
        confidence += 0.1
    
    # Factor 2: Source quality
    high_quality_domains = [".gov", ".edu", ".org"]
    quality_sources = sum(1 for url in evidence if any(domain in url for domain in high_quality_domains))
    confidence += min(quality_sources * 0.1, 0.2)
    
    # Factor 3: Direct causal language
    causal_indicators = ["caused", "led to", "resulted in", "triggered"]
    if any(indicator in cause.lower() or indicator in effect.lower() for indicator in causal_indicators):
        confidence += 0.1
    
    return min(confidence, 1.0)  # Cap at 1.0

