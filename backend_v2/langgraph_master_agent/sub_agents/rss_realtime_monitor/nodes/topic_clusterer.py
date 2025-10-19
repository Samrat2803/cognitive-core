"""
Topic Clusterer Node

Clusters articles into topics using DBSCAN and creates embeddings on-demand.
"""

import os
import sys
from typing import Dict
import numpy as np
from dotenv import load_dotenv
from sklearn.cluster import DBSCAN
from collections import defaultdict

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.rss_embedder import RSSEmbedder
from rss_realtime_monitor.state import RSSRealtimeMonitorState
from rss_realtime_monitor.config import DBSCAN_EPS, DBSCAN_MIN_SAMPLES


async def cluster_topics(state: RSSRealtimeMonitorState) -> RSSRealtimeMonitorState:
    """
    Cluster articles into topics using DBSCAN
    
    Steps:
    1. Get/create embeddings for filtered articles (on-demand)
    2. Run DBSCAN clustering
    3. Group articles by cluster
    4. Create topic metadata
    """
    
    print("\n[3] Clustering articles into topics...")
    
    try:
        articles = state["filtered_articles"]
        
        if not articles:
            print("  ⚠️  No articles to cluster")
            state["clusters"] = []
            state["topics"] = []
            state["topics_found"] = 0
            return state
        
        if len(articles) < 2:
            print("  ⚠️  Need at least 2 articles to cluster")
            # Create single topic with all articles
            state["clusters"] = [0]
            state["topics"] = [{
                "cluster_id": 0,
                "articles": articles,
                "article_count": len(articles)
            }]
            state["topics_found"] = 1
            return state
        
        print(f"  Clustering {len(articles)} articles...")
        
        # Get or create embeddings
        embedder = RSSEmbedder()
        article_urls = [a["url"] for a in articles]
        
        embeddings_dict = await embedder.get_or_create_embeddings(
            article_urls,
            show_progress=False
        )
        
        # Convert to ordered array
        embeddings_list = []
        url_to_idx = {}
        
        for idx, url in enumerate(article_urls):
            if url in embeddings_dict:
                embeddings_list.append(embeddings_dict[url])
                url_to_idx[url] = idx
        
        if len(embeddings_list) < 2:
            print("  ⚠️  Not enough embeddings created")
            state["clusters"] = [0] * len(articles)
            state["topics"] = [{
                "cluster_id": 0,
                "articles": articles,
                "article_count": len(articles)
            }]
            state["topics_found"] = 1
            return state
        
        embeddings_array = np.array(embeddings_list)
        
        # Run DBSCAN clustering
        clustering = DBSCAN(
            eps=DBSCAN_EPS,
            min_samples=DBSCAN_MIN_SAMPLES,
            metric='cosine'
        )
        
        cluster_labels = clustering.fit_predict(embeddings_array)
        
        # Count clusters
        unique_clusters = set(cluster_labels)
        n_noise = sum(1 for c in cluster_labels if c == -1)
        n_clusters = len(unique_clusters) - (1 if -1 in unique_clusters else 0)
        
        print(f"  ✓ Found {n_clusters} clusters ({n_noise} unclustered articles)")
        
        # Group articles by cluster
        cluster_articles = defaultdict(list)
        
        for idx, cluster_id in enumerate(cluster_labels):
            url = article_urls[idx]
            article = next((a for a in articles if a["url"] == url), None)
            if article:
                cluster_articles[cluster_id].append(article)
        
        # Create topic metadata
        topics = []
        
        for cluster_id, cluster_arts in cluster_articles.items():
            if cluster_id == -1:
                continue  # Skip noise for now
            
            topics.append({
                "cluster_id": cluster_id,
                "articles": cluster_arts,
                "article_count": len(cluster_arts)
            })
        
        # Store in state
        state["clusters"] = cluster_labels.tolist()
        state["topics"] = topics
        state["topics_found"] = len(topics)
        state["embeddings"] = embeddings_dict
        
        state["execution_log"].append(
            f"Clustered into {len(topics)} topics using DBSCAN"
        )
    
    except Exception as e:
        error_msg = f"Error clustering topics: {str(e)}"
        print(f"  ✗ {error_msg}")
        state["error_log"].append(error_msg)
        # Fallback: create single topic
        state["clusters"] = [0] * len(state["filtered_articles"])
        state["topics"] = [{
            "cluster_id": 0,
            "articles": state["filtered_articles"],
            "article_count": len(state["filtered_articles"])
        }]
        state["topics_found"] = 1
    
    return state

