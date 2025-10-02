"""
Quality Checker Node - Analyze bias and decide if iteration is needed
Adapted from POC agent_utils.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from collections import Counter
from state import SentimentAnalyzerState


def calculate_english_ratio(search_results: Dict[str, list]) -> float:
    """Calculate ratio of English language content (from POC logic)"""
    english_count = 0
    total_with_content = 0
    
    for country, results in search_results.items():
        for result in results:
            title = result.get('title', '')
            content = result.get('content', '')
            url = result.get('url', '').lower()
            
            # Check URL for non-English domains (positive signal)
            non_english_domains = ['presstv.ir', 'farsnews.ir', 'aljazeera.', 'xinhua', 'tass.', 'rt.com']
            has_non_english_domain = any(domain in url for domain in non_english_domains)
            
            combined = (title + ' ' + content).lower()
            
            if combined.strip():
                total_with_content += 1
                
                # If from known non-English source, don't count as English even if content is English
                if has_non_english_domain:
                    continue  # Don't count as English
                
                # Simple English detection (from POC)
                english_indicators = ["the", "and", "of", "to", "in", "is", "that", "for"]
                if any(word in combined for word in english_indicators):
                    english_count += 1
    
    return english_count / max(total_with_content, 1)


def has_non_english_countries(countries: list) -> bool:
    """Check if any countries primarily speak non-English languages"""
    non_english_countries = [
        "Iran", "Israel", "China", "Russia", "Japan", 
        "Saudi Arabia", "UAE", "Egypt", "Turkey", "Germany", "France"
    ]
    return any(country in non_english_countries for country in countries)


def analyze_source_diversity(search_results: Dict[str, list]) -> Dict[str, Any]:
    """Analyze source type diversity"""
    source_types = Counter()
    total_articles = 0
    
    for country, results in search_results.items():
        for result in results:
            total_articles += 1
            # Extract domain to classify source type
            url = result.get('url', '')
            if 'gov.' in url or '.gov' in url:
                source_types['government'] += 1
            elif 'edu' in url or 'academic' in url:
                source_types['academic'] += 1
            elif any(news in url for news in ['bbc', 'cnn', 'aljazeera', 'nytimes', 'reuters']):
                source_types['media'] += 1
            else:
                source_types['other'] += 1
    
    media_ratio = source_types.get('media', 0) / max(total_articles, 1)
    
    return {
        'source_distribution': dict(source_types),
        'media_ratio': media_ratio,
        'total_articles': total_articles,
        'source_diversity_score': len(source_types) / 4.0  # 4 possible types
    }


def generate_multilingual_search_params(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Generate search params with language diversification"""
    
    countries = state["countries"]
    query = state["query"]
    iteration = state.get("iteration", 0)
    
    # Country-specific search strategies with local media emphasis
    country_configs = {
        "Iran": {
            "queries": [
                f"{query} Iran PressTV",                   # Iranian state media
                f"{query} Iran Fars News",                 # Iranian news agency  
                f"{query} Iranian government statement"
            ],
            "include_domains": ["presstv.ir", "farsnews.ir", "aljazeera.com", "tasnimnews.com"]
        },
        "Israel": {
            "queries": [
                f"{query} Israel Jerusalem Post",
                f"{query} Israel Times of Israel",
                f"{query} Israeli government position"
            ],
            "include_domains": ["gov.il", "jpost.com", "timesofisrael.com", "i24news.tv"]
        },
        "US": {
            "queries": [
                f"{query} United States State Department",
                f"{query} US government policy",
                f"{query} American official position"
            ],
            "include_domains": ["state.gov", "whitehouse.gov", "defense.gov"]
        },
        "China": {
            "queries": [
                f"{query} China Xinhua",
                f"{query} Chinese government Beijing",
                f"{query} China CGTN"
            ],
            "include_domains": ["xinhuanet.com", "chinadaily.com.cn", "cgtn.com"]
        },
        "Russia": {
            "queries": [
                f"{query} Russia TASS",
                f"{query} Russia RT news",
                f"{query} Kremlin statement"
            ],
            "include_domains": ["tass.com", "rt.com", "sputniknews.com"]
        }
    }
    
    # Build params
    params = {}
    for country in countries:
        if country in country_configs:
            config = country_configs[country]
            # Rotate through queries based on iteration
            query_idx = iteration % len(config["queries"])
            params[country] = {
                "query": config["queries"][query_idx],
                "include_domains": config["include_domains"]
            }
        else:
            # Default fallback
            params[country] = {
                "query": f"{query} {country} public opinion",
                "include_domains": None
            }
    
    return params


async def quality_checker(state: SentimentAnalyzerState) -> Dict[str, Any]:
    """Check quality and decide if iteration is needed"""
    
    iteration = state.get("iteration", 0)
    search_results = state.get("search_results", {})
    countries = state["countries"]
    
    print(f"\n🔍 Quality Checker: Analyzing iteration {iteration + 1}...")
    
    # Max iterations check
    MAX_ITERATIONS = 2  # Allow up to 2 iterations (3 total searches)
    if iteration >= MAX_ITERATIONS:
        print(f"   ⏹️  Max iterations reached ({MAX_ITERATIONS + 1} total searches)")
        return {
            "iteration": iteration + 1,  # Increment for final state
            "should_iterate": False,
            "iteration_reason": "max_iterations_reached",
            "quality_metrics": {},
            "execution_log": state.get("execution_log", []) + [{
                "step": "quality_checker",
                "action": f"Stopped: Max iterations ({MAX_ITERATIONS + 1} total searches) reached"
            }]
        }
    
    if not search_results:
        print(f"   ⚠️  No search results to analyze")
        return {
            "iteration": iteration + 1,
            "should_iterate": False,
            "iteration_reason": "no_results",
            "quality_metrics": {},
            "execution_log": state.get("execution_log", []) + [{
                "step": "quality_checker",
                "action": "Stopped: No search results"
            }]
        }
    
    # Calculate quality metrics
    english_ratio = calculate_english_ratio(search_results)
    source_metrics = analyze_source_diversity(search_results)
    has_non_english = has_non_english_countries(countries)
    
    quality_metrics = {
        "english_ratio": english_ratio,
        "source_diversity": source_metrics['source_diversity_score'],
        "media_ratio": source_metrics['media_ratio'],
        "total_articles": source_metrics['total_articles'],
        "source_distribution": source_metrics['source_distribution']
    }
    
    print(f"   📊 Quality Metrics:")
    print(f"      English ratio: {english_ratio:.1%}")
    print(f"      Source diversity: {source_metrics['source_diversity_score']:.1%}")
    print(f"      Media ratio: {source_metrics['media_ratio']:.1%}")
    print(f"      Total articles: {source_metrics['total_articles']}")
    
    # Decision logic (from POC)
    gaps = []
    
    # Language diversity gap
    if english_ratio > 0.8 and has_non_english:
        gaps.append("language_diversity_gap")
        print(f"   🚨 Language bias detected: {english_ratio:.1%} English")
    
    # Source type homogeneity
    if source_metrics['media_ratio'] > 0.85:
        gaps.append("source_type_homogeneity")
        print(f"   🚨 Source bias detected: {source_metrics['media_ratio']:.1%} media")
    
    # Good stopping conditions - RELAXED (domain filtering works even with English content)
    if (english_ratio < 0.7 and 
        source_metrics['source_diversity_score'] >= 0.5 and
        source_metrics['total_articles'] >= 5):
        print(f"   ✅ Quality acceptable: Good language and source diversity")
        return {
            "iteration": iteration + 1,
            "should_iterate": False,
            "iteration_reason": "quality_acceptable",
            "quality_metrics": quality_metrics,
            "execution_log": state.get("execution_log", []) + [{
                "step": "quality_checker",
                "action": f"Stopped: Quality acceptable (diversity: {source_metrics['source_diversity_score']:.1%})"
            }]
        }
    
    # If iteration >= 1 and we have diverse sources, stop (domain filtering likely working)
    if (iteration >= 1 and 
        source_metrics['source_diversity_score'] >= 0.5 and
        source_metrics['total_articles'] >= 8):
        print(f"   ✅ Stopping after iteration {iteration + 1}: Source diversity improved")
        return {
            "iteration": iteration + 1,
            "should_iterate": False,
            "iteration_reason": "source_diversity_improved",
            "quality_metrics": quality_metrics,
            "execution_log": state.get("execution_log", []) + [{
                "step": "quality_checker",
                "action": f"Stopped: Source diversity improved to {source_metrics['source_diversity_score']:.1%}"
            }]
        }
    
    # If iteration < MAX and gaps found, iterate (only on first iteration)
    if iteration == 0 and gaps:
        print(f"   🔄 Gaps found: {', '.join(gaps)} - will iterate")
        new_params = generate_multilingual_search_params(state)
        return {
            "iteration": iteration + 1,  # Increment for next iteration
            "should_iterate": True,
            "iteration_reason": f"bias_detected: {', '.join(gaps)}",
            "quality_metrics": quality_metrics,
            "search_params": new_params,
            "execution_log": state.get("execution_log", []) + [{
                "step": "quality_checker",
                "action": f"Continuing to iteration {iteration + 2}: Detected {len(gaps)} gaps - {', '.join(gaps)}"
            }]
        }
    
    # Stop if no major improvements expected
    print(f"   ⏹️  Stopping: Iteration {iteration + 1} complete")
    return {
        "iteration": iteration + 1,
        "should_iterate": False,
        "iteration_reason": "no_improvement_expected",
        "quality_metrics": quality_metrics,
        "execution_log": state.get("execution_log", []) + [{
            "step": "quality_checker",
            "action": f"Stopped: No significant improvement expected"
        }]
    }

