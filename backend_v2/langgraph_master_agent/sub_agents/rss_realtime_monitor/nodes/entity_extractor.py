"""
Entity Extractor Node

Extracts entities (people, organizations, locations, companies) from topics.
"""

import os
import sys
from typing import Dict, List
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from rss_realtime_monitor.state import RSSRealtimeMonitorState
from rss_realtime_monitor.config import MODEL, TEMPERATURE, MAX_ENTITIES_PER_TYPE

# Initialize OpenAI client
client = AsyncOpenAI()


async def extract_entities(state: RSSRealtimeMonitorState) -> RSSRealtimeMonitorState:
    """
    Extract entities from top topics using LLM
    
    Entities:
    - people: Key individuals mentioned
    - organizations: Organizations/governments
    - locations: Countries, cities, regions
    - companies: Companies/corporations
    """
    
    print("\n[6] Extracting entities from topics...")
    
    try:
        topics = state["explosive_topics"]
        
        if not topics:
            print("  ⚠️  No topics to extract entities from")
            return state
        
        # Extract entities from top 5 topics (to save API calls)
        top_topics = topics[:5]
        
        extracted_count = 0
        
        for topic in top_topics:
            headlines = topic.get("headlines", [])
            
            if not headlines:
                topic["entities"] = {
                    "people": [],
                    "organizations": [],
                    "locations": [],
                    "companies": []
                }
                continue
            
            # Combine headlines for context
            headlines_text = "\n".join([
                f"- {h['title']}" for h in headlines[:5]
            ])
            
            # Handle both 'label' (pre-transform) and 'topic' (post-transform) fields
            topic_name = topic.get('topic') or topic.get('label', 'Unknown Topic')
            
            prompt = f"""Extract key entities from these news headlines about: {topic_name}

Headlines:
{headlines_text}

Extract:
1. people: Key individuals mentioned (names only)
2. organizations: Organizations, governments, agencies
3. locations: Countries, cities, regions
4. companies: Companies, corporations

Return JSON with these 4 arrays. Max {MAX_ENTITIES_PER_TYPE} per type.
Only include entities that appear in the headlines."""
            
            try:
                response = await client.chat.completions.create(
                    model=MODEL,
                    temperature=TEMPERATURE,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                entities = json.loads(response.choices[0].message.content)
                
                # Ensure all fields exist and limit length
                topic["entities"] = {
                    "people": entities.get("people", [])[:MAX_ENTITIES_PER_TYPE],
                    "organizations": entities.get("organizations", [])[:MAX_ENTITIES_PER_TYPE],
                    "locations": entities.get("locations", [])[:MAX_ENTITIES_PER_TYPE],
                    "companies": entities.get("companies", [])[:MAX_ENTITIES_PER_TYPE]
                }
                
                extracted_count += 1
            
            except Exception as e:
                print(f"  ✗ Error extracting entities for topic {topic['rank']}: {e}")
                topic["entities"] = {
                    "people": [],
                    "organizations": [],
                    "locations": [],
                    "companies": []
                }
        
        print(f"  ✓ Extracted entities from {extracted_count}/{len(top_topics)} top topics")
        
        state["execution_log"].append(
            f"Extracted entities from {extracted_count} topics using {MODEL}"
        )
    
    except Exception as e:
        error_msg = f"Error extracting entities: {str(e)}"
        print(f"  ✗ {error_msg}")
        state["error_log"].append(error_msg)
    
    return state

