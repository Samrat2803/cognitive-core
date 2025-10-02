"""
Explosiveness Scorer Node - Calculates composite explosiveness score using 4 signals
"""

from datetime import datetime
from state import LiveMonitorState
from config import (
    SIGNAL_WEIGHTS,
    CLASSIFICATION_THRESHOLDS,
    CRISIS_KEYWORDS,
    MAX_TOPICS_RETURNED
)


def calculate_signal_scores(topic_data: dict, relevant_articles: list, keywords: list) -> dict:
    """
    Calculate all signal scores for a topic
    
    4 Signals:
    1. LLM Explosiveness (0-30 points)
    2. Frequency (0-25 points)
    3. Source Diversity (0-20 points)
    4. Urgency Keywords (0-15 points)
    5. Recency Bonus (0-10 points - fixed for now)
    """
    
    signals = {}
    
    # Signal 1: LLM Explosiveness (0-30 points)
    llm_rating = topic_data.get('explosiveness', 5)  # 1-10 scale
    signals['llm_explosiveness'] = llm_rating * 3  # Convert to 0-30
    
    # Signal 2: Frequency - how many articles mention this topic (0-25 points)
    frequency = topic_data.get('frequency', 1)
    signals['frequency'] = min(frequency * 5, 25)
    
    # Signal 3: Source Diversity - unique sources across ALL articles (0-20 points)
    domains = []
    for article in relevant_articles:
        url = article.get('url', '')
        if url:
            try:
                domain = url.split('/')[2]
                domains.append(domain)
            except:
                pass
    
    unique_sources = len(set(domains))
    signals['source_diversity'] = min(unique_sources * 2, 20)
    
    # Signal 4: Urgency Keywords in topic name (0-15 points)
    topic_name = topic_data.get('topic', '').lower()
    urgency_count = sum(1 for kw in CRISIS_KEYWORDS if kw in topic_name)
    signals['urgency_keywords'] = min(urgency_count * 5, 15)
    
    # Signal 5: Recency Bonus (fixed for now, can be dynamic later)
    signals['recency_bonus'] = 5  # Default bonus
    
    return signals


def classify_topic(total_score: int) -> tuple:
    """
    Classify topic based on score
    
    Returns: (emoji_classification, priority_number)
    """
    
    if total_score >= CLASSIFICATION_THRESHOLDS['CRITICAL']:
        return "🔴 CRITICAL", 1
    elif total_score >= CLASSIFICATION_THRESHOLDS['EXPLOSIVE']:
        return "🟠 EXPLOSIVE", 2
    elif total_score >= CLASSIFICATION_THRESHOLDS['TRENDING']:
        return "🟡 TRENDING", 3
    else:
        return "🟢 EMERGING", 4


def get_topic_image(topic_index: int, fetched_images: list) -> str:
    """
    Get a representative image for a topic from fetched images
    
    Strategy:
    - Distribute images across topics (round-robin style)
    - Each topic gets a unique image if possible
    - Returns empty string if no images available
    """
    if not fetched_images:
        return ""
    
    # Use modulo to distribute images across topics
    # This ensures each topic gets a different image
    image_index = topic_index % len(fetched_images)
    return fetched_images[image_index]


async def calculate_explosiveness(state: LiveMonitorState) -> LiveMonitorState:
    """
    Calculate explosiveness scores for all extracted topics
    """
    
    print("\n💥 Calculating explosiveness scores...")
    
    extracted_topics = state['extracted_topics']
    relevant_articles = state['relevant_articles']
    keywords = state['keywords']
    fetched_images = state.get('fetched_images', [])  # Images from Tavily
    
    if not extracted_topics:
        print("   ⚠ No topics to score")
        execution_log = state.get('execution_log', [])
        execution_log.append({
            "step": "calculate_explosiveness",
            "timestamp": datetime.now().isoformat(),
            "status": "skipped",
            "reason": "no_topics"
        })
        
        return {
            **state,
            "scored_topics": [],
            "explosive_topics": [],
            "execution_log": execution_log
        }
    
    scored_topics = []
    
    for topic_index, topic_data in enumerate(extracted_topics):
        topic_name = topic_data.get('topic', 'Unknown')
        
        print(f"\n   Scoring: {topic_name}")
        
        # Calculate all signal scores
        signals = calculate_signal_scores(topic_data, relevant_articles, keywords)
        
        # Print breakdown
        print(f"      • LLM explosiveness: {signals['llm_explosiveness']}/30")
        print(f"      • Frequency: {signals['frequency']}/25")
        print(f"      • Source diversity: {signals['source_diversity']}/20")
        print(f"      • Urgency keywords: {signals['urgency_keywords']}/15")
        print(f"      • Recency bonus: {signals['recency_bonus']}/10")
        
        # Calculate total score
        total_score = sum(signals.values())
        
        # Classify
        classification, priority = classify_topic(total_score)
        
        print(f"      ━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"      🎯 TOTAL: {total_score}/100")
        print(f"      🏷️  {classification}")
        
        # Get image for this topic
        topic_image = get_topic_image(topic_index, fetched_images)
        if topic_image:
            print(f"      🖼️  Image found")
        
        # Compile scored topic
        scored_topic = {
            "rank": 0,  # Will be set after sorting
            "topic": topic_name,
            "explosiveness_score": total_score,
            "classification": classification,
            "priority": priority,
            "signal_breakdown": signals,
            "frequency": topic_data.get('frequency', 0),
            "llm_rating": topic_data.get('explosiveness', 0),
            "entities": topic_data.get('entities', {}),
            "reasoning": topic_data.get('reasoning', ''),
            "image_url": topic_image,  # NEW: Image from news source
            "sources": []  # Will be populated with article sources
        }
        
        scored_topics.append(scored_topic)
    
    # Sort by score (descending)
    scored_topics.sort(key=lambda x: x['explosiveness_score'], reverse=True)
    
    # Assign ranks
    for i, topic in enumerate(scored_topics, 1):
        topic['rank'] = i
    
    # Get top N topics
    top_topics = scored_topics[:MAX_TOPICS_RETURNED]
    
    print(f"\n   ✓ Scored {len(scored_topics)} topics")
    print(f"   ✓ Returning top {len(top_topics)} explosive topics")
    
    # Add to execution log
    execution_log = state.get('execution_log', [])
    execution_log.append({
        "step": "calculate_explosiveness",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "topics_scored": len(scored_topics),
        "top_topics_returned": len(top_topics)
    })
    
    return {
        **state,
        "scored_topics": scored_topics,
        "explosive_topics": top_topics,
        "execution_log": execution_log
    }

