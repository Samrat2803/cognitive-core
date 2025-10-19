"""
Label Generator Node

Generates descriptive labels for topics using TF-IDF keyword extraction.
"""

import os
import sys
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from rss_realtime_monitor.state import RSSRealtimeMonitorState


def generate_labels(state: RSSRealtimeMonitorState) -> RSSRealtimeMonitorState:
    """
    Generate topic labels using TF-IDF keyword extraction
    
    Strategy:
    1. Combine all titles in each topic
    2. Extract top keywords using TF-IDF
    3. Create concise label (max 3-4 words)
    """
    
    print("\n[4] Generating topic labels...")
    
    try:
        topics = state["topics"]
        
        if not topics:
            print("  ⚠️  No topics to label")
            return state
        
        labeled_count = 0
        
        for topic in topics:
            articles = topic["articles"]
            
            if not articles:
                topic["label"] = "Unknown Topic"
                continue
            
            # Combine all titles
            titles = [a.get("title", "") for a in articles]
            all_text = " ".join(titles)
            
            # Extract keywords using TF-IDF
            try:
                vectorizer = TfidfVectorizer(
                    max_features=10,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                
                tfidf_matrix = vectorizer.fit_transform([all_text])
                feature_names = vectorizer.get_feature_names_out()
                
                # Get top 3 terms
                scores = tfidf_matrix.toarray()[0]
                top_indices = scores.argsort()[-3:][::-1]
                top_terms = [feature_names[i] for i in top_indices if scores[i] > 0]
                
                # Create label
                if top_terms:
                    label = " | ".join(top_terms[:3]).title()
                else:
                    # Fallback: use first title words
                    label = " ".join(titles[0].split()[:4])
                
                topic["label"] = label
                labeled_count += 1
            
            except Exception as e:
                # Fallback: use first title
                topic["label"] = titles[0][:50] if titles else "Unknown Topic"
                labeled_count += 1
        
        print(f"  ✓ Generated {labeled_count} topic labels")
        
        state["execution_log"].append(
            f"Generated labels for {labeled_count} topics using TF-IDF"
        )
    
    except Exception as e:
        error_msg = f"Error generating labels: {str(e)}"
        print(f"  ✗ {error_msg}")
        state["error_log"].append(error_msg)
    
    return state

