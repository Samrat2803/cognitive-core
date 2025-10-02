"""
Topic Extractor Node - Uses LLM to extract main political topics from articles
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../../.env'))

from openai import AsyncOpenAI
from state import LiveMonitorState
from config import MODEL, TEMPERATURE

client = AsyncOpenAI()


async def extract_topics(state: LiveMonitorState) -> LiveMonitorState:
    """
    Extract main political topics from relevant articles using LLM
    
    Returns topics with:
    - Specific topic name
    - Frequency (how many articles mention it)
    - Explosiveness rating (1-10)
    - Key entities (people, countries, organizations)
    """
    
    print("\n🧠 Extracting topics with LLM...")
    
    relevant_articles = state['relevant_articles']
    keywords = state['keywords']
    
    if not relevant_articles:
        print("   ⚠ No relevant articles to extract topics from")
        execution_log = state.get('execution_log', [])
        execution_log.append({
            "step": "extract_topics",
            "timestamp": datetime.now().isoformat(),
            "status": "skipped",
            "reason": "no_relevant_articles"
        })
        
        return {
            **state,
            "extracted_topics": [],
            "execution_log": execution_log
        }
    
    # Prepare article summaries for LLM (limit to 25 for token efficiency)
    article_summaries = []
    for i, article in enumerate(relevant_articles[:25], 1):
        title = article.get('title', 'No title')
        content = article.get('content', '')[:200]  # First 200 chars
        relevance = article.get('relevance_score', 0)
        article_summaries.append(f"{i}. [{relevance} pts] {title}\n   {content}")
    
    print(f"   Processing {len(article_summaries)} articles...")
    
    prompt = f"""Analyze these political news articles related to: {', '.join(keywords)}

Extract the main political topics/events. For each topic:
1. Give it a SPECIFIC name (not generic - be specific like "CBI raids 15 Bihar offices" not just "corruption")
2. Count how many articles mention it
3. Rate its EXPLOSIVENESS (1-10):
   - 9-10: Major crisis, war, coup, assassination, emergency
   - 7-8: Significant unexpected development, breaking news
   - 5-6: Notable event but somewhat expected
   - 3-4: Routine political development
   - 1-2: Minor or scheduled news
4. List key entities (people, countries, organizations)
5. Provide brief reasoning for the explosiveness rating

Articles:
{chr(10).join(article_summaries)}

Return JSON in this exact format:
{{
    "topics": [
        {{
            "topic": "specific topic name",
            "frequency": number of articles mentioning it,
            "explosiveness": 1-10 rating,
            "entities": {{"people": ["name"], "countries": ["country"], "organizations": ["org"]}},
            "reasoning": "why this explosiveness rating"
        }}
    ]
}}

Focus on the top 5-7 most significant topics."""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        topics = result.get('topics', [])
        
        print(f"   ✓ Extracted {len(topics)} topics")
        
        for i, topic in enumerate(topics, 1):
            name = topic.get('topic', 'Unknown')
            exp = topic.get('explosiveness', 0)
            freq = topic.get('frequency', 0)
            print(f"      {i}. {name}")
            print(f"         Explosiveness: {exp}/10 | Articles: {freq}")
        
        # Add to execution log
        execution_log = state.get('execution_log', [])
        execution_log.append({
            "step": "extract_topics",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "topics_extracted": len(topics)
        })
        
        return {
            **state,
            "extracted_topics": topics,
            "execution_log": execution_log
        }
        
    except Exception as e:
        print(f"   ✗ Topic extraction failed: {e}")
        
        error_log = state.get('error_log', [])
        error_log.append(f"Topic extraction error: {str(e)}")
        
        execution_log = state.get('execution_log', [])
        execution_log.append({
            "step": "extract_topics",
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        })
        
        return {
            **state,
            "extracted_topics": [],
            "execution_log": execution_log,
            "error_log": error_log
        }

