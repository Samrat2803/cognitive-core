"""
Standalone Test Runner for Live Political Monitor Agent

Usage:
    python main.py                           # Use default keywords
    python main.py "Ukraine, war, Russia"    # Custom keywords
"""

import asyncio
import sys
import json
import os
from datetime import datetime
from graph import create_live_monitor_graph
from state import LiveMonitorState
from config import DEFAULT_KEYWORDS, DEFAULT_CACHE_HOURS, MAX_TOPICS_RETURNED


async def run_live_monitor(keywords: list, cache_hours: int = 3, max_results: int = 10):
    """
    Run the Live Political Monitor agent
    
    Args:
        keywords: List of keywords to focus on
        cache_hours: Cache duration (not used in standalone, for future)
        max_results: Max topics to return
    """
    
    print("=" * 80)
    print("🔥 LIVE POLITICAL MONITOR - Explosive Topic Detection")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Max Results: {max_results}")
    print("=" * 80)
    
    start_time = datetime.now()
    
    # Create graph
    graph = create_live_monitor_graph()
    
    # Initialize state
    initial_state: LiveMonitorState = {
        "keywords": keywords,
        "cache_hours": cache_hours,
        "max_results": max_results,
        "generated_queries": [],
        "raw_articles": [],
        "relevant_articles": [],
        "irrelevant_articles": [],
        "extracted_topics": [],
        "scored_topics": [],
        "explosive_topics": [],
        "total_articles_analyzed": 0,
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
        print(f"   • Total articles analyzed: {result['total_articles_analyzed']}")
        print(f"   • Relevant articles: {len(result['relevant_articles'])}")
        print(f"   • Topics extracted: {len(result['extracted_topics'])}")
        print(f"   • Processing time: {processing_time:.1f}s")
        
        if result['error_log']:
            print(f"\n⚠️  Errors encountered: {len(result['error_log'])}")
            for error in result['error_log']:
                print(f"   • {error}")
        
        print(f"\n🔥 TOP EXPLOSIVE TOPICS:")
        print("=" * 80)
        
        explosive_topics = result['explosive_topics']
        
        if not explosive_topics:
            print("\n   ⚠️  No explosive topics found for these keywords.")
            print("   Try different keywords or check if there's breaking news.")
        else:
            for topic in explosive_topics:
                rank = topic['rank']
                classification = topic['classification']
                name = topic['topic']
                score = topic['explosiveness_score']
                freq = topic['frequency']
                
                print(f"\n{rank}. {classification} - {name}")
                print(f"   Score: {score}/100 | Articles: {freq}")
                
                # Show signal breakdown
                signals = topic['signal_breakdown']
                print(f"   Signals: LLM={signals['llm_explosiveness']}, "
                      f"Freq={signals['frequency']}, "
                      f"Sources={signals['source_diversity']}, "
                      f"Urgency={signals['urgency_keywords']}")
                
                # Show entities
                entities = topic.get('entities', {})
                if entities:
                    people = entities.get('people', [])
                    countries = entities.get('countries', [])
                    orgs = entities.get('organizations', [])
                    
                    entity_parts = []
                    if people:
                        entity_parts.append(f"People: {', '.join(people[:3])}")
                    if countries:
                        entity_parts.append(f"Countries: {', '.join(countries[:3])}")
                    if orgs:
                        entity_parts.append(f"Orgs: {', '.join(orgs[:3])}")
                    
                    if entity_parts:
                        print(f"   Entities: {' | '.join(entity_parts)}")
                
                # Show reasoning
                reasoning = topic.get('reasoning', '')
                if reasoning:
                    print(f"   Reasoning: {reasoning[:150]}...")
        
        # Save results to file
        output_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'test_output_{timestamp}.json')
        
        # Prepare output data
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "keywords": keywords,
            "processing_time_seconds": processing_time,
            "total_articles_analyzed": result['total_articles_analyzed'],
            "relevant_articles_count": len(result['relevant_articles']),
            "topics_extracted": len(result['extracted_topics']),
            "explosive_topics": explosive_topics,
            "execution_log": result['execution_log'],
            "error_log": result['error_log']
        }
        
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
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        # Custom keywords from command line
        keywords_str = sys.argv[1]
        keywords = [k.strip() for k in keywords_str.split(',')]
    else:
        # Use default keywords
        keywords = DEFAULT_KEYWORDS
        print(f"Using default keywords: {', '.join(keywords)}")
        print(f"(You can provide custom keywords as argument: python main.py \"keyword1, keyword2\")\n")
    
    # Run agent
    asyncio.run(run_live_monitor(keywords))


if __name__ == "__main__":
    main()

