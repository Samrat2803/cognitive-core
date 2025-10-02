"""Extract all sources with metadata from agent analysis results for review"""

import json
import pandas as pd
from typing import List, Dict, Any


def extract_all_sources(agent_results_path: str) -> List[Dict[str, Any]]:
    """Extract all articles from all iterations with metadata"""
    
    with open(agent_results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    all_sources = []
    
    # Extract from all iterations
    for iteration_idx, iteration_data in enumerate(results.get("all_results", [])):
        query = iteration_data.get("query", f"iteration_{iteration_idx}")
        
        for article in iteration_data.get("articles", []):
            source_entry = {
                # Iteration info
                "iteration": iteration_idx + 1,
                "query_term": query,
                
                # Basic info
                "country": article.get("country", ""),
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                
                # GPT-4o Analysis
                "sentiment_score": article.get("sentiment"),
                "reasoning": article.get("reasoning", ""),
                "source_type": article.get("source_type", ""),
                "date_published": article.get("date_published"),
                "credibility_score": article.get("credibility_score"),
                
                # Bias Analysis
                "bias_type": article.get("bias_type", []),
                "bias_severity": article.get("bias_severity"),
                "bias_notes": article.get("bias_notes", ""),
                
                # Additional metadata
                "has_sentiment": article.get("sentiment") is not None,
                "has_reasoning": bool(article.get("reasoning", "")),
                "is_recent": bool(article.get("date_published") and 
                                any(year in str(article.get("date_published", "")) 
                                    for year in ["2023", "2024", "2025"])),
                
                # URL domain for analysis
                "domain": extract_domain(article.get("url", "")),
            }
            
            all_sources.append(source_entry)
    
    return all_sources


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    if not url:
        return ""
    
    try:
        # Remove protocol
        if "://" in url:
            url = url.split("://")[1]
        
        # Get domain part
        domain = url.split("/")[0]
        
        # Remove www
        if domain.startswith("www."):
            domain = domain[4:]
            
        return domain
    except:
        return ""


def create_summary_stats(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create summary statistics"""
    
    total_sources = len(sources)
    
    # Count by iteration
    iteration_counts = {}
    for source in sources:
        iter_num = source["iteration"]
        iteration_counts[iter_num] = iteration_counts.get(iter_num, 0) + 1
    
    # Count by country
    country_counts = {}
    for source in sources:
        country = source["country"]
        country_counts[country] = country_counts.get(country, 0) + 1
    
    # Count by source type
    source_type_counts = {}
    for source in sources:
        stype = source["source_type"]
        if stype:
            source_type_counts[stype] = source_type_counts.get(stype, 0) + 1
    
    # Count by domain
    domain_counts = {}
    for source in sources:
        domain = source["domain"]
        if domain:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Sentiment analysis
    sentiments = [s["sentiment_score"] for s in sources if s["sentiment_score"] is not None]
    
    # Recent articles
    recent_count = sum(1 for s in sources if s["is_recent"])
    
    # Bias analysis
    bias_severities = [s["bias_severity"] for s in sources if s["bias_severity"] is not None]
    
    # Count bias types
    bias_type_counts = {}
    for source in sources:
        bias_types = source.get("bias_type", [])
        if isinstance(bias_types, list):
            for bias_type in bias_types:
                bias_type_counts[bias_type] = bias_type_counts.get(bias_type, 0) + 1
    
    return {
        "total_sources": total_sources,
        "sources_with_sentiment": len(sentiments),
        "sources_with_reasoning": sum(1 for s in sources if s["has_reasoning"]),
        "recent_articles": recent_count,
        "recent_percentage": (recent_count / total_sources * 100) if total_sources > 0 else 0,
        
        "sentiment_stats": {
            "count": len(sentiments),
            "avg": sum(sentiments) / len(sentiments) if sentiments else 0,
            "min": min(sentiments) if sentiments else None,
            "max": max(sentiments) if sentiments else None,
        },
        
        "bias_stats": {
            "sources_with_bias_analysis": len(bias_severities),
            "avg_bias_severity": sum(bias_severities) / len(bias_severities) if bias_severities else 0,
            "bias_type_breakdown": dict(sorted(bias_type_counts.items(), key=lambda x: x[1], reverse=True)),
        },
        
        "iteration_breakdown": iteration_counts,
        "country_breakdown": country_counts,
        "source_type_breakdown": source_type_counts,
        "top_domains": dict(sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
    }


def main():
    """Main function to create sources review files"""
    
    print("🔍 Extracting sources from agent analysis results...")
    
    # Extract all sources
    sources = extract_all_sources("POCs/agent_analysis_results.json")
    
    print(f"📊 Found {len(sources)} total sources across all iterations")
    
    # Create summary stats
    stats = create_summary_stats(sources)
    
    # Save detailed sources as CSV (convert bias_type list to string for CSV)
    df = pd.DataFrame(sources)
    df['bias_type_str'] = df['bias_type'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x) if x else '')
    df.to_csv("POCs/all_sources_detailed.csv", index=False)
    print(f"💾 Saved detailed sources to POCs/all_sources_detailed.csv")
    
    # Save sources as JSON for programmatic access
    with open("POCs/all_sources_detailed.json", "w", encoding="utf-8") as f:
        json.dump(sources, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved detailed sources to POCs/all_sources_detailed.json")
    
    # Save summary statistics
    with open("POCs/sources_summary_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"📈 Saved summary statistics to POCs/sources_summary_stats.json")
    
    # Create a focused review CSV with key columns
    review_columns = [
        "iteration", "query_term", "country", "title", "domain", 
        "sentiment_score", "source_type", "credibility_score", 
        "date_published", "is_recent", "bias_type_str", "bias_severity", 
        "bias_notes", "reasoning"
    ]
    
    review_df = df[review_columns].copy()
    review_df.to_csv("POCs/sources_for_review.csv", index=False)
    print(f"📋 Saved review-focused CSV to POCs/sources_for_review.csv")
    
    # Print summary
    print("\n📊 Summary Statistics:")
    print(f"   Total Sources: {stats['total_sources']}")
    print(f"   With Sentiment: {stats['sources_with_sentiment']}")
    print(f"   With Reasoning: {stats['sources_with_reasoning']}")
    print(f"   Recent Articles: {stats['recent_articles']} ({stats['recent_percentage']:.1f}%)")
    print(f"   Avg Sentiment: {stats['sentiment_stats']['avg']:.3f}")
    
    print(f"\n🔄 By Iteration:")
    for iter_num, count in sorted(stats['iteration_breakdown'].items()):
        print(f"   Iteration {iter_num}: {count} sources")
    
    print(f"\n🌍 By Country:")
    for country, count in sorted(stats['country_breakdown'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {country}: {count} sources")
    
    print(f"\n📰 By Source Type:")
    for stype, count in sorted(stats['source_type_breakdown'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {stype}: {count} sources")
    
    print(f"\n⚠️  Bias Analysis:")
    print(f"   Sources with bias analysis: {stats['bias_stats']['sources_with_bias_analysis']}")
    print(f"   Avg bias severity: {stats['bias_stats']['avg_bias_severity']:.3f}")
    print(f"   Top bias types:")
    for bias_type, count in list(stats['bias_stats']['bias_type_breakdown'].items())[:5]:
        print(f"     {bias_type}: {count} sources")
    
    print(f"\n🌐 Top Domains:")
    for domain, count in list(stats['top_domains'].items())[:5]:
        print(f"   {domain}: {count} sources")
    
    print(f"\n✅ All files created successfully!")
    return stats


if __name__ == "__main__":
    main()
