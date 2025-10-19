"""
RSS Realtime Monitor - Standalone Test Runner

Usage:
    python main.py                                    # Default keywords
    python main.py "TikTok, ban, ByteDance"          # Custom keywords
    python main.py "AI" --regions "United States"    # With region filter
"""

import asyncio
import sys
import json
import os
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rss_realtime_monitor.graph import create_rss_realtime_monitor_graph
from rss_realtime_monitor.state import RSSRealtimeMonitorState
from rss_realtime_monitor.config import DEFAULT_MAX_TOPICS


async def run_rss_monitor(
    keywords: list,
    regions: list = None,
    categories: list = None,
    max_topics: int = DEFAULT_MAX_TOPICS
):
    """
    Run the RSS Realtime Monitor agent
    
    Args:
        keywords: List of keywords to search for
        regions: Optional list of regions to filter
        categories: Optional list of categories to filter
        max_topics: Max topics to return
    
    Returns:
        Agent result state
    """
    
    print("=" * 80)
    print("🔥 RSS REALTIME MONITOR - Explosive Topic Detection")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Keywords: {', '.join(keywords)}")
    if regions:
        print(f"Regions: {', '.join(regions)}")
    if categories:
        print(f"Categories: {', '.join(categories)}")
    print(f"Max Topics: {max_topics}")
    print("=" * 80)
    
    start_time = datetime.now()
    
    # Create graph
    graph = create_rss_realtime_monitor_graph()
    
    # Initialize state
    initial_state: RSSRealtimeMonitorState = {
        "keywords": keywords,
        "regions": regions,
        "categories": categories,
        "max_topics": max_topics,
        "all_cached_articles": [],
        "filtered_articles": [],
        "embeddings": {},
        "clusters": [],
        "topics": [],
        "explosive_topics": [],
        "total_articles_cached": 0,
        "articles_analyzed": 0,
        "topics_found": 0,
        "processing_time_seconds": 0.0,
        "execution_log": [],
        "error_log": []
    }
    
    # Run graph
    try:
        result = await graph.ainvoke(initial_state)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        result['processing_time_seconds'] = processing_time
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 RESULTS SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ Processing:")
        print(f"   • Total articles in cache: {result['total_articles_cached']}")
        print(f"   • Articles analyzed: {result['articles_analyzed']}")
        print(f"   • Topics found: {result['topics_found']}")
        print(f"   • Processing time: {processing_time:.1f}s")
        
        if result['error_log']:
            print(f"\n⚠️  Errors encountered: {len(result['error_log'])}")
            for error in result['error_log']:
                print(f"   • {error}")
        
        print(f"\n🔥 TOP EXPLOSIVE TOPICS:")
        print("=" * 80)
        
        explosive_topics = result['explosive_topics']
        
        if not explosive_topics:
            print("\n   ⚠️  No topics found for these keywords.")
            print("   Try different keywords or run RSS collector first.")
        else:
            for topic in explosive_topics:
                rank = topic['rank']
                label = topic['label']
                score = topic['explosiveness_score']
                count = topic['article_count']
                velocity = topic['velocity']
                age = topic['avg_age_hours']
                
                # Status indicator
                if velocity > 1.0:
                    status = "🔥 BREAKING"
                elif age < 6:
                    status = "🆕 NEW"
                elif count >= 10:
                    status = "📈 MAJOR"
                else:
                    status = "📰 DEVELOPING"
                
                print(f"\n#{rank}. {status} | {label}")
                print(f"   Score: {score}/100 | Articles: {count} | Velocity: {velocity:.2f}/hr | Age: {age:.1f}h")
                
                # Show score breakdown
                breakdown = topic['score_breakdown']
                print(f"   Breakdown: Velocity={breakdown['velocity']:.0f}, "
                      f"Recency={breakdown['recency']:.0f}, "
                      f"Diversity={breakdown['diversity']:.0f}, "
                      f"Geo={breakdown['geographic']:.0f}, "
                      f"Relevance={breakdown['relevance']:.0f}")
                
                # Show sources
                sources = topic['sources'][:5]
                print(f"   Sources ({topic['source_diversity']}): {', '.join(sources)}")
                
                # Show entities
                entities = topic.get('entities', {})
                if entities:
                    entity_parts = []
                    if entities.get('people'):
                        entity_parts.append(f"People: {', '.join(entities['people'][:3])}")
                    if entities.get('companies'):
                        entity_parts.append(f"Companies: {', '.join(entities['companies'][:3])}")
                    if entities.get('locations'):
                        entity_parts.append(f"Locations: {', '.join(entities['locations'][:3])}")
                    
                    if entity_parts:
                        print(f"   Entities: {' | '.join(entity_parts)}")
                
                # Show top headlines
                print(f"   Headlines:")
                for i, headline in enumerate(topic['headlines'][:3], 1):
                    age_marker = "🔴" if headline['age_hours'] < 3 else "🟡" if headline['age_hours'] < 12 else "⚪"
                    print(f"     {i}. {age_marker} {headline['title'][:70]}...")
                    print(f"        {headline['source']} · {headline['age_hours']:.1f}h ago")
                
                # Tavily readiness
                if topic['ready_for_tavily']:
                    print(f"   ✅ Ready for Tavily deep dive (score > 70)")
        
        # Save results
        output_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'test_output_{timestamp}.json')
        
        # Prepare output data (remove embeddings - too large)
        output_data = dict(result)
        output_data.pop('embeddings', None)
        output_data.pop('all_cached_articles', None)
        output_data.pop('filtered_articles', None)
        
        # Convert numpy types to Python types for JSON serialization
        def convert_numpy(obj):
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        output_data = convert_numpy(output_data)
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return result
    
    except Exception as e:
        print(f"\n❌ ERROR: Agent execution failed")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='RSS Realtime Monitor')
    parser.add_argument('keywords', nargs='?', default=None,
                       help='Comma-separated keywords (e.g., "AI, regulation, policy")')
    parser.add_argument('--regions', default=None,
                       help='Comma-separated regions (e.g., "United States, Europe")')
    parser.add_argument('--categories', default=None,
                       help='Comma-separated categories (e.g., "technology, business")')
    parser.add_argument('--max-topics', type=int, default=DEFAULT_MAX_TOPICS,
                       help='Maximum topics to return')
    
    args = parser.parse_args()
    
    # Parse keywords
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]
    else:
        # Default keywords
        keywords = ["artificial intelligence", "technology", "regulation"]
        print(f"Using default keywords: {', '.join(keywords)}")
        print(f"(Provide custom keywords: python main.py \"keyword1, keyword2\")\n")
    
    # Parse regions
    regions = None
    if args.regions:
        regions = [r.strip() for r in args.regions.split(',')]
    
    # Parse categories
    categories = None
    if args.categories:
        categories = [c.strip() for c in args.categories.split(',')]
    
    # Run agent
    asyncio.run(run_rss_monitor(
        keywords=keywords,
        regions=regions,
        categories=categories,
        max_topics=args.max_topics
    ))


if __name__ == "__main__":
    main()

