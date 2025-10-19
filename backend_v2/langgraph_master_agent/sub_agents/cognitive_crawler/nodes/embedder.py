"""
Embedder Node - Generate and store vector embeddings with proper chunking
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any, List
from state import CognitiveCrawlerState
from tools.mongodb_handler import TenderMongoDBHandler
from langchain.text_splitter import RecursiveCharacterTextSplitter


async def embedder(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Generate OpenAI embeddings with proper chunking
    
    Uses RecursiveCharacterTextSplitter for intelligent chunking:
    - Splits at natural boundaries (paragraphs, sentences)
    - Maintains overlap between chunks for context
    - Multiple embeddings per document for better retrieval
    """
    
    tenders = state.get("tenders_parsed", [])
    thread_id = state.get("thread_id", "default_session")
    
    print(f"\n🧬 Embedder: Generating embeddings for {len(tenders)} documents...")
    
    state["execution_log"].append({
        "step": "embedder",
        "action": f"Generating embeddings with chunking for {len(tenders)} documents"
    })
    
    try:
        if not tenders:
            print("   ⚠️  No documents to embed")
            state["embeddings_generated"] = 0
            return state
        
        # Initialize text splitter with LARGER chunks for better context
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,          # 3000 chars (3x larger) to preserve context
            chunk_overlap=400,         # 400 overlap for continuity
            separators=["\n\n", "\n", ". ", " ", ""],  # Try natural boundaries first
            length_function=len
        )
        
        # Create chunked documents for embedding
        all_chunks = []
        total_chunks = 0
        
        for doc in tenders:
            content = doc.get('content', '')
            
            if len(content) < 100:
                # Skip very short content (likely just metadata/navigation)
                print(f"   ⚠️  Skipping short content from {doc.get('url', 'unknown')}")
                continue
            
            # Split into chunks
            chunks = text_splitter.split_text(content)
            
            # Create a document for each chunk
            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    'doc_id': f"{doc.get('doc_id')}_chunk_{i}",
                    'content': chunk,
                    'metadata': {
                        'url': doc.get('url'),
                        'domain': doc.get('domain'),
                        'relevance_score': doc.get('relevance_score'),
                        'query_keywords': doc.get('query_keywords'),
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'original_doc_id': doc.get('doc_id')
                    }
                }
                all_chunks.append(chunk_doc)
                total_chunks += 1
        
        print(f"   📄 Split {len(tenders)} documents into {total_chunks} chunks")
        print(f"   📊 Average: {total_chunks / len(tenders) if tenders else 0:.1f} chunks per document")
        
        # Generate and store embeddings for all chunks
        if all_chunks:
            db_handler = TenderMongoDBHandler()
            await db_handler.store_vectors(all_chunks, thread_id)
            
            state["embeddings_generated"] = len(all_chunks)
            print(f"   ✅ Generated and stored {len(all_chunks)} embeddings")
        else:
            print("   ⚠️  No valid chunks to embed (all content too short)")
            state["embeddings_generated"] = 0
        
    except Exception as e:
        error_msg = f"embedder error: {str(e)}"
        print(f"   ❌ {error_msg}")
        import traceback
        traceback.print_exc()
        state["error_log"].append(error_msg)
        state["embeddings_generated"] = 0
    
    return state

