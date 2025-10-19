"""
Create MongoDB Atlas Vector Search Index using Python

This script creates a vector search index on the tender_vectors collection
for fast semantic search (10-50ms instead of seconds).

Requirements:
- MONGO_DB_URI must be set in .env
- MongoDB Atlas cluster must be M10 or higher (vector search not available on free tier M0)
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

load_dotenv()

def create_vector_search_index():
    """
    Create Atlas Vector Search index using the createSearchIndexes command
    """
    
    # Get connection URI
    uri = os.getenv('MONGODB_CONNECTION_STRING') or os.getenv('MONGO_DB_URI')
    if not uri:
        print("❌ MONGODB_CONNECTION_STRING not found in .env")
        sys.exit(1)
    
    print("🔗 Connecting to MongoDB Atlas...")
    client = MongoClient(uri)
    
    # Get database and collection (use the actual database where vectors are stored)
    db = client['political_analyst_db']  # This is where the vectors are!
    collection = db['tender_vectors']
    
    print(f"📊 Collection: political_analyst_db.tender_vectors")
    
    # Check if collection exists (by checking document count)
    try:
        doc_count = collection.count_documents({})
        print(f"   Documents in collection: {doc_count}")
        
        if doc_count == 0:
            print(f"\n⚠️  Collection is empty!")
            print(f"   You need to crawl some data first before creating the index.")
            print(f"   Run a crawl operation, then come back and run this script.")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n⚠️  Collection may not exist or is empty")
        print(f"   Error: {e}")
        print(f"\n   You need to crawl some data first!")
        sys.exit(1)
    
    # Check if index already exists
    try:
        existing_indexes = list(collection.list_search_indexes())
        print(f"\n📋 Existing search indexes: {len(existing_indexes)}")
        
        for idx in existing_indexes:
            print(f"   - {idx.get('name', 'unnamed')} (status: {idx.get('status', 'unknown')})")
        
        # Check if vector_index already exists
        if any(idx.get('name') == 'vector_index' for idx in existing_indexes):
            print("\n⚠️  Index 'vector_index' already exists!")
            response = input("Do you want to recreate it? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
            
            # Drop existing index
            print("\n🗑️  Dropping existing index...")
            collection.drop_search_index('vector_index')
            print("✅ Dropped")
    
    except Exception as e:
        print(f"⚠️  Could not list existing indexes: {e}")
        print("   (This is OK if no indexes exist yet)")
    
    # Define vector search index
    index_definition = {
        "name": "vector_index",
        "definition": {
            "mappings": {
                "dynamic": False,
                "fields": {
                    "embedding": {
                        "type": "knnVector",
                        "dimensions": 1536,
                        "similarity": "cosine"
                    },
                    "thread_id": {
                        "type": "token"
                    },
                    "created_at": {
                        "type": "date"
                    }
                }
            }
        }
    }
    
    print(f"\n🔨 Creating vector search index 'vector_index'...")
    print(f"   - Field: embedding (1536 dimensions, cosine similarity)")
    print(f"   - Filters: thread_id, created_at")
    
    try:
        # Create the index
        result = collection.create_search_index(index_definition)
        
        print(f"\n✅ Index creation initiated!")
        print(f"   Index name: vector_index")
        print(f"   Result: {result}")
        print(f"\n⏳ Index is building... This may take 2-5 minutes.")
        print(f"   Check status in Atlas UI or run this script again to verify.")
        
    except Exception as e:
        error_msg = str(e)
        
        if "Atlas search index" in error_msg or "search is not enabled" in error_msg.lower():
            print(f"\n❌ Atlas Search is not enabled on your cluster!")
            print(f"\n💡 Solutions:")
            print(f"   1. Upgrade to M10+ cluster (search requires dedicated cluster)")
            print(f"   2. Enable Atlas Search in Atlas UI: Cluster → ... → Edit → Enable Atlas Search")
            print(f"   3. Create new M10+ cluster with Search enabled")
        else:
            print(f"\n❌ Error creating index: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 MongoDB Atlas Vector Search Index Creator")
    print("=" * 80)
    print()
    
    create_vector_search_index()
    
    print()
    print("=" * 80)
    print("✨ Done!")
    print("=" * 80)

