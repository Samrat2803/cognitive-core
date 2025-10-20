"""
MongoDB Handler - Store and search tenders with vector embeddings
Uses AsyncIOMotorClient for proper async support in LangGraph nodes
NOW USES LangChain's MongoDBAtlasVectorSearch for proper RAG!
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient  # Synchronous client for LangChain
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
from datetime import datetime

# Import from config.py to ensure consistency
from config import (
    MONGODB_URI,
    DATABASE_NAME,
    PORTALS_COLLECTION,
    TENDERS_COLLECTION,
    VECTORS_COLLECTION,
    EMBEDDING_MODEL,
    OPENAI_API_KEY
)


class TenderMongoDBHandler:
    """Handle MongoDB operations for tender storage and vector search - ASYNC + LangChain RAG"""
    
    def __init__(self):
        """Initialize MongoDB async client, embeddings, and LangChain vector store"""
        # Async client for database operations
        self.client = AsyncIOMotorClient(MONGODB_URI)
        self.db = self.client[DATABASE_NAME]
        
        # Synchronous client for LangChain (it doesn't support async yet)
        self.sync_client = MongoClient(MONGODB_URI)
        self.sync_db = self.sync_client[DATABASE_NAME]
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Initialize LangChain's MongoDBAtlasVectorSearch with synchronous client
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.sync_db[VECTORS_COLLECTION],
            embedding=self.embeddings,
            index_name="vector_index",  # Must match the index name you create in Atlas UI
            text_key="content",
            embedding_key="embedding"
        )
    
    async def store_portals(self, portals: List[Dict]):
        """
        Store discovered portal information
        
        Args:
            portals: List of portal dictionaries
        """
        collection = self.db[PORTALS_COLLECTION]
        
        for portal in portals:
            portal['discovered_at'] = datetime.now()
            portal['last_updated'] = datetime.now()
        
        if portals:
            await collection.insert_many(portals)
    
    async def store_documents(self, documents: List[Dict]):
        """
        Store generic documents (press releases, policies, reports, etc.)
        
        Args:
            documents: List of document dictionaries
        """
        collection = self.db[TENDERS_COLLECTION]  # Reusing collection
        
        for doc in documents:
            doc['stored_at'] = datetime.now()
            # Ensure required fields for compatibility
            if 'tender_id' not in doc:
                doc['tender_id'] = doc.get('doc_id', f"doc_{datetime.now().timestamp()}")
            if 'domain' not in doc:
                doc['domain'] = 'unknown'
            if 'title' not in doc:
                doc['title'] = doc.get('content', '')[:100]
            if 'organization' not in doc:
                doc['organization'] = doc.get('domain', 'unknown')
        
        if documents:
            await collection.insert_many(documents)
    
    async def get_existing_urls(self, urls: List[str]) -> set:
        """
        Check which URLs are already in the database
        
        Args:
            urls: List of URLs to check
            
        Returns:
            Set of URLs that already exist in the database
        """
        collection = self.db[TENDERS_COLLECTION]
        
        # Query for documents with these URLs
        cursor = collection.find(
            {'url': {'$in': urls}},
            {'url': 1, '_id': 0}
        )
        
        existing_docs = await cursor.to_list(length=None)
        existing_urls = {doc['url'] for doc in existing_docs if 'url' in doc}
        
        return existing_urls
    
    async def store_tenders(self, tenders: List[Dict]):
        """
        Store structured tender data (kept for backwards compatibility)
        
        Args:
            tenders: List of tender dictionaries
        """
        collection = self.db[TENDERS_COLLECTION]
        
        for tender in tenders:
            tender['stored_at'] = datetime.now()
        
        if tenders:
            # Use upsert to avoid duplicates based on tender_id
            for tender in tenders:
                await collection.update_one(
                    {'tender_id': tender.get('tender_id')},
                    {'$set': tender},
                    upsert=True
                )
    
    async def store_vectors(self, documents: List[Dict], thread_id: str):
        """
        Generate embeddings and store using LangChain's vector store
        
        Args:
            documents: List of documents with 'content', 'doc_id', 'metadata'
            thread_id: Session ID for this crawl
        """
        print(f"   📦 Storing {len(documents)} documents in vector store...")
        
        # Convert to LangChain Document format
        langchain_docs = []
        for doc in documents:
            langchain_doc = Document(
                page_content=doc['content'],
                metadata={
                    **doc.get('metadata', {}),
                    'doc_id': doc['doc_id'],
                    'thread_id': thread_id,
                    'created_at': str(datetime.now())
                }
            )
            langchain_docs.append(langchain_doc)
        
        # Use LangChain's add_documents (handles embedding + storage)
        # Note: This is synchronous in LangChain, but fast enough
        try:
            ids = self.vector_store.add_documents(langchain_docs)
            print(f"   ✅ Stored {len(ids)} vectors using LangChain MongoDBAtlasVectorSearch")
        except Exception as e:
            print(f"   ⚠️  LangChain vector store failed: {e}")
            print(f"   🔄 Falling back to manual storage...")
            
            # Fallback: manual storage (for backwards compatibility)
            collection = self.db[VECTORS_COLLECTION]
            texts = [doc['content'] for doc in documents]
            embeddings = self.embeddings.embed_documents(texts)
            
            for i, doc in enumerate(documents):
                vector_doc = {
                    'doc_id': doc['doc_id'],
                    'content': doc['content'],
                    'embedding': embeddings[i],
                    'metadata': doc.get('metadata', {}),
                    'thread_id': thread_id,
                    'created_at': datetime.now()
                }
                await collection.insert_one(vector_doc)
            print(f"   ✅ Fallback storage complete")
    
    async def search_vectors(self, query: str, thread_id: str = None, top_k: int = 30) -> List[Dict]:
        """
        Perform vector similarity search using MongoDB Atlas Vector Search
        
        FAST: Uses Atlas's native vector search with HNSW indexing (10-50ms)
        
        Args:
            query: Search query
            thread_id: Filter to specific session/investigation (None = search all data)
            top_k: Number of results to return (default 30)
            
        Returns:
            List of matching documents with scores
        """
        collection = self.db[VECTORS_COLLECTION]
        total_vectors = await collection.count_documents({})
        
        print(f"   🚀 Atlas Vector Search: {total_vectors} vectors indexed")
        if thread_id:
            print(f"   🔒 Filtering to thread_id: {thread_id[:30]}...")
        
        try:
            # METHOD 1: Use LangChain's Atlas Vector Search (FAST!)
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Use Atlas Vector Search aggregation pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",  # Must match your Atlas index name
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": top_k * 10,  # Oversample for better recall
                        "limit": top_k * 3 if thread_id else top_k  # Get extra for filtering
                    }
                }
            ]
            
            # Add thread_id filter if provided (LOCAL RAG)
            if thread_id:
                pipeline.append({
                    "$match": {
                        "thread_id": thread_id
                    }
                })
            
            # Apply final limit after filtering
            if thread_id:
                pipeline.append({
                    "$limit": top_k
                })
            
            pipeline.append({
                "$project": {
                    "content": 1,
                    # LangChain stores metadata fields at root level, not in 'metadata' subdoc
                    "url": 1,
                    "domain": 1,
                    "relevance_score": 1,
                    "query_keywords": 1,
                    "chunk_index": 1,
                    "total_chunks": 1,
                    "original_doc_id": 1,
                    "doc_id": 1,
                    "thread_id": 1,
                    "created_at": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            })
            
            # Execute search (async)
            cursor = collection.aggregate(pipeline)
            results_raw = await cursor.to_list(length=top_k)
            
            # Reformat to have metadata as a nested object (for consistency with knowledge_base.py)
            results = []
            for doc in results_raw:
                result = {
                    'content': doc.get('content', ''),
                    'metadata': {
                        'url': doc.get('url', 'Unknown'),
                        'domain': doc.get('domain', 'unknown'),
                        'relevance_score': doc.get('relevance_score', 0),
                        'query_keywords': doc.get('query_keywords', []),
                        'chunk_index': doc.get('chunk_index', 0),
                        'total_chunks': doc.get('total_chunks', 1),
                        'original_doc_id': doc.get('original_doc_id', ''),
                    },
                    'doc_id': doc.get('doc_id', 'unknown'),
                    'thread_id': doc.get('thread_id', 'unknown'),
                    'score': doc.get('score', 0)
                }
                results.append(result)
            
            print(f"   ✅ Atlas Vector Search found {len(results)} results")
            
            if results:
                print(f"   📊 Top 3 matches:")
                for i, result in enumerate(results[:3], 1):
                    url = result.get('metadata', {}).get('url', 'Unknown')
                    score = result.get('score', 0)
                    print(f"   {i}. {url} (score: {score:.3f})")
            
            return results
            
        except Exception as e:
            print(f"   ⚠️  Atlas Vector Search error: {e}")
            print(f"   🔄 Falling back to in-memory cosine similarity...")
            
            # FALLBACK: In-memory cosine similarity (slow but reliable)
            return await self._fallback_cosine_search(query, top_k)
    
    async def _fallback_cosine_search(self, query: str, top_k: int) -> List[Dict]:
        """
        Fallback method using in-memory cosine similarity
        Used when Atlas Vector Search index is not configured
        """
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        collection = self.db[VECTORS_COLLECTION]
        
        print(f"   🐢 Using slow in-memory search (configure Atlas index for 100x speedup!)")
        
        try:
            # Only fetch embeddings first (not full content)
            cursor = collection.find({}, {'embedding': 1, 'doc_id': 1})
            all_docs = await cursor.to_list(length=None)
            
            if len(all_docs) == 0:
                return []
            
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            query_vector = np.array(query_embedding).reshape(1, -1)
            
            # Extract embeddings
            doc_embeddings = []
            doc_ids = []
            
            for doc in all_docs:
                if 'embedding' in doc and doc['embedding']:
                    doc_embeddings.append(doc['embedding'])
                    doc_ids.append(doc['doc_id'])
            
            if len(doc_embeddings) == 0:
                return []
            
            # Compute cosine similarity
            doc_vectors = np.array(doc_embeddings)
            similarities = cosine_similarity(query_vector, doc_vectors)[0]
            
            # Get top k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Fetch full documents for top k
            top_doc_ids = [doc_ids[idx] for idx in top_indices]
            cursor = collection.find({'doc_id': {'$in': top_doc_ids}})
            full_docs = await cursor.to_list(length=top_k)
            
            # Create results with scores
            results = []
            doc_id_to_doc = {doc['doc_id']: doc for doc in full_docs}
            
            for idx in top_indices:
                doc_id = doc_ids[idx]
                doc = doc_id_to_doc.get(doc_id)
                if doc:
                    score = float(similarities[idx])
                    
                    result = {
                        'content': doc.get('content', ''),
                        'metadata': doc.get('metadata', {}),
                        'doc_id': doc.get('doc_id', 'unknown'),
                        'thread_id': doc.get('thread_id', 'unknown'),
                        'score': score
                    }
                    results.append(result)
            
            print(f"   ✅ Fallback found {len(results)} results")
            
            if results:
                print(f"   📊 Top 3 matches:")
                for i, result in enumerate(results[:3], 1):
                    url = result.get('metadata', {}).get('url', 'Unknown')
                    score = result.get('score', 0)
                    print(f"   {i}. {url} (score: {score:.3f})")
            
            return results
            
        except Exception as e:
            print(f"   ❌ Fallback search also failed: {e}")
            
            # LAST RESORT: Return recent documents
            print(f"   📄 Final fallback: returning recent documents")
            cursor = collection.find({}).sort("created_at", -1).limit(top_k)
            results = await cursor.to_list(length=top_k)
            return [{**doc, 'score': 0.5} for doc in results]
    
    async def get_all_tenders(self, filters: Dict = None) -> List[Dict]:
        """
        Get all tenders matching filters
        
        Args:
            filters: MongoDB query filters
            
        Returns:
            List of tender documents
        """
        collection = self.db[TENDERS_COLLECTION]
        
        if filters:
            cursor = collection.find(filters)
        else:
            cursor = collection.find()
        
        return await cursor.to_list(length=None)
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()

