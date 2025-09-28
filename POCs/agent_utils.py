"""Utility functions for geopolitical sentiment analysis agent"""

import json
from typing import Dict, List, Any, Tuple
from collections import Counter


def analyze_bias_and_gaps(results_json: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze bias and gaps in sentiment analysis results"""
    
    articles = results_json.get("articles", [])
    countries = results_json.get("countries", [])
    query = results_json.get("query", "")
    
    if not articles:
        return {"has_gaps": True, "reason": "No articles found"}
    
    # Language analysis (basic heuristic)
    english_count = 0
    total_with_content = 0
    
    # Source type distribution
    source_types = Counter()
    
    # Credibility distribution
    credibility_scores = []
    
    # Sentiment distribution
    sentiment_scores = []
    
    # Bias analysis (methodological issues)
    bias_types = Counter()
    bias_severities = []
    
    # Date analysis
    recent_dates = 0  # Articles from 2023+
    unknown_dates = 0
    
    for article in articles:
        if article.get("sentiment") is not None:
            sentiment_scores.append(article["sentiment"])
        
        if article.get("source_type"):
            source_types[article["source_type"]] += 1
            
        if article.get("credibility_score") is not None:
            credibility_scores.append(article["credibility_score"])
            
        # Bias analysis (methodological issues)
        if article.get("bias_type"):
            bias_list = article["bias_type"] if isinstance(article["bias_type"], list) else []
            for bias in bias_list:
                bias_types[bias] += 1
                
        if article.get("bias_severity") is not None:
            bias_severities.append(article["bias_severity"])
            
        # Basic language detection (very simple heuristic)
        reasoning = article.get("reasoning") or ""
        title = article.get("title") or ""
        content = reasoning + title
        if content:
            total_with_content += 1
            # Simple check for English (presence of common English words)
            english_indicators = ["the", "and", "of", "to", "in", "is", "that", "for"]
            if any(word in content.lower() for word in english_indicators):
                english_count += 1
                
        # Date analysis
        date_pub = article.get("date_published")
        if date_pub and date_pub != "unknown":
            if "2023" in date_pub or "2024" in date_pub or "2025" in date_pub:
                recent_dates += 1
        else:
            unknown_dates += 1
    
    # Calculate metrics
    english_ratio = english_count / max(total_with_content, 1)
    avg_sentiment = sum(sentiment_scores) / max(len(sentiment_scores), 1)
    avg_credibility = sum(credibility_scores) / max(len(credibility_scores), 1)
    avg_bias_severity = sum(bias_severities) / max(len(bias_severities), 1)
    
    # Detect methodological biases and gaps
    gaps = []
    suggestions = []
    
    # Language diversity gap (methodological issue)
    if english_ratio > 0.8:
        gaps.append("language_diversity_gap")
        suggestions.append({
            "type": "language_diversification",
            "action": "search_non_english",
            "details": f"Language homogeneity ({english_ratio:.1%} English). Try Arabic/Farsi terms for cultural context."
        })
    
    # Source type diversity gap (methodological issue)
    media_ratio = source_types.get("media", 0) / max(len(articles), 1)
    if media_ratio > 0.85:
        gaps.append("source_type_homogeneity")
        suggestions.append({
            "type": "source_diversification", 
            "action": "include_domains",
            "details": f"Source homogeneity ({media_ratio:.1%} media). Include govt/academic domains for perspective diversity."
        })
    
    # High methodological bias severity
    if avg_bias_severity > 0.6:
        gaps.append("high_methodological_bias")
        # Find most common bias types
        top_bias = bias_types.most_common(2)
        bias_details = ", ".join([f"{bias}: {count}" for bias, count in top_bias])
        suggestions.append({
            "type": "bias_mitigation",
            "action": "adjust_search_strategy",
            "details": f"High bias severity ({avg_bias_severity:.2f}). Top issues: {bias_details}. Consider different domains/terms."
        })
    
    # Citation bias - if too many articles have citation_bias
    citation_bias_count = bias_types.get("citation_bias", 0)
    if citation_bias_count > len(articles) * 0.3:
        gaps.append("citation_bias_pattern")
        suggestions.append({
            "type": "citation_diversification",
            "action": "search_different_sources",
            "details": f"Citation bias in {citation_bias_count} articles. Search government/academic sources for primary perspectives."
        })
    
    # Temporal coverage gap (methodological issue)
    recent_ratio = recent_dates / max(len(articles), 1)
    if recent_ratio < 0.3:
        gaps.append("temporal_coverage_gap")
        suggestions.append({
            "type": "time_filtering",
            "action": "add_time_filter", 
            "details": f"Poor temporal coverage ({recent_ratio:.1%} recent). Add days=30 filter for current context."
        })
    
    return {
        "has_gaps": len(gaps) > 0,
        "gaps": gaps,
        "suggestions": suggestions,
        "metrics": {
            "english_ratio": english_ratio,
            "avg_sentiment": avg_sentiment,
            "avg_credibility": avg_credibility,
            "avg_bias_severity": avg_bias_severity,
            "source_distribution": dict(source_types),
            "bias_distribution": dict(bias_types),
            "recent_ratio": recent_ratio,
            "total_articles": len(articles)
        }
    }


def generate_search_params(analysis: Dict[str, Any], iteration: int) -> Dict[str, Any]:
    """Generate next search parameters based on bias analysis"""
    
    suggestions = analysis.get("suggestions", [])
    
    # Default params
    params = {
        "query_term": "Hamas",  # Default fallback
        "countries": ["United States", "Iran", "Israel"],
        "include_domains": None,
        "exclude_domains": None,
        "days": None
    }
    
    # Apply suggestions
    for suggestion in suggestions:
        if suggestion["type"] == "language_diversification":
            # Try Arabic/Farsi terms
            arabic_terms = ["حماس", "Hamas resistance", "Hamas martyrs"]
            params["query_term"] = arabic_terms[iteration % len(arabic_terms)]
            
        elif suggestion["type"] == "source_diversification":
            # Include government and academic domains
            params["include_domains"] = [
                "gov.ir", "gov.il", "state.gov", "whitehouse.gov",
                "aljazeera.com", "presstv.ir", "jpost.com"
            ]
            
        elif suggestion["type"] == "bias_mitigation":
            # Try different search strategies to reduce methodological bias
            alternative_terms = ["Hamas governance", "Palestinian movement", "Gaza politics"]
            params["query_term"] = alternative_terms[iteration % len(alternative_terms)]
            
        elif suggestion["type"] == "citation_diversification":
            # Focus on primary sources
            params["include_domains"] = [
                "gov.ir", "gov.il", "state.gov", "un.org", 
                "whitehouse.gov", "knesset.gov.il"
            ]
            
        elif suggestion["type"] == "time_filtering":
            # Add recency filter
            params["days"] = 30
    
    return params


def should_stop_iteration(analysis: Dict[str, Any], iteration: int, max_iterations: int = 3) -> bool:
    """Determine if agent should stop iterating"""
    
    if iteration >= max_iterations:
        return True
        
    if not analysis.get("has_gaps", True):
        return True
        
    # Stop if we have good coverage
    metrics = analysis.get("metrics", {})
    
    # Good stopping conditions
    if (metrics.get("english_ratio", 1.0) < 0.7 and  # Language diversity
        metrics.get("recent_ratio", 0.0) > 0.4 and   # Recent content
        len(metrics.get("source_distribution", {})) >= 3):  # Source diversity
        return True
        
    return False
