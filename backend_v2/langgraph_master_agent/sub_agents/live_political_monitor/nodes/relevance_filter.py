"""
Relevance Filter Node - Filters articles by user keywords
"""

from datetime import datetime
from state import LiveMonitorState
from config import MIN_RELEVANCE_SCORE, KEYWORD_MATCH_WEIGHT, CRISIS_KEYWORD_WEIGHT, CRISIS_KEYWORDS


def calculate_relevance_score(article: dict, keywords: list) -> int:
    """
    Calculate how relevant an article is to the user's keywords
    
    Scoring:
    - Each keyword match in title/content: +20 points
    - Each crisis keyword match: +10 points
    - Negative keywords: -50 points (future feature)
    
    Returns: Score (0-100+)
    """
    
    title = article.get('title', '').lower()
    content = article.get('content', '').lower()
    article_text = title + ' ' + content
    
    score = 0
    matches_found = []
    
    # Check user keywords
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in article_text:
            score += KEYWORD_MATCH_WEIGHT
            matches_found.append(keyword)
    
    # Check crisis keywords (bonus for urgency)
    crisis_matches = []
    for crisis_kw in CRISIS_KEYWORDS:
        if crisis_kw in article_text:
            score += CRISIS_KEYWORD_WEIGHT
            crisis_matches.append(crisis_kw)
    
    return score, matches_found, crisis_matches


async def filter_by_relevance(state: LiveMonitorState) -> LiveMonitorState:
    """
    Filter articles to keep only those relevant to user keywords
    """
    
    print("\n🔍 Filtering articles by relevance...")
    
    raw_articles = state['raw_articles']
    keywords = state['keywords']
    
    print(f"   Analyzing {len(raw_articles)} articles against keywords: {', '.join(keywords)}")
    
    relevant_articles = []
    irrelevant_articles = []
    
    for article in raw_articles:
        relevance_score, matches, crisis_kw = calculate_relevance_score(article, keywords)
        
        # Add metadata to article
        article['relevance_score'] = relevance_score
        article['keyword_matches'] = matches
        article['crisis_keywords'] = crisis_kw
        
        if relevance_score >= MIN_RELEVANCE_SCORE:
            relevant_articles.append(article)
        else:
            irrelevant_articles.append(article)
    
    print(f"   ✓ Relevant articles: {len(relevant_articles)}")
    print(f"   ✗ Filtered out: {len(irrelevant_articles)}")
    
    if relevant_articles:
        # Show sample of top relevant articles
        top_3 = sorted(relevant_articles, key=lambda x: x['relevance_score'], reverse=True)[:3]
        print(f"\n   Top 3 most relevant:")
        for i, article in enumerate(top_3, 1):
            title = article.get('title', 'No title')[:80]
            score = article['relevance_score']
            matches = article['keyword_matches']
            print(f"      {i}. [{score} pts] {title}")
            print(f"         Matches: {', '.join(matches)}")
    
    # Add to execution log
    execution_log = state.get('execution_log', [])
    execution_log.append({
        "step": "filter_by_relevance",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "relevant_count": len(relevant_articles),
        "irrelevant_count": len(irrelevant_articles)
    })
    
    return {
        **state,
        "relevant_articles": relevant_articles,
        "irrelevant_articles": irrelevant_articles,
        "execution_log": execution_log
    }

