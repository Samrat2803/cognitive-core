"""
Evidence Repository Service - MongoDB Integration
Saves and loads investigation evidence for resumption capability
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../../.env'))

# Import mongo service
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
from services.mongo_service import mongo_service


async def save_investigation(state: Dict[str, Any], session_id: Optional[str] = None) -> str:
    """
    Save investigation evidence repository to MongoDB
    
    Args:
        state: Investigation state with all evidence
        session_id: Optional master agent session ID
        
    Returns:
        investigation_id: UUID for this investigation
    """
    await mongo_service.connect()
    
    investigation_id = state.get("investigation_id") or f"inv_{uuid.uuid4().hex[:12]}"
    
    # Calculate cost summary
    cost_tracking = state.get("cost_tracking", {})
    
    doc = {
        "investigation_id": investigation_id,
        "session_id": session_id or state.get("session_id"),
        "query": state["initial_query"],
        "title": state.get("title", state["initial_query"][:100]),
        "status": "completed" if state.get("investigation_complete") else "active",
        "created_at": datetime.utcnow() if "created_at" not in state else state.get("created_at"),
        "updated_at": datetime.utcnow(),
        "completed_at": datetime.utcnow() if state.get("investigation_complete") else None,
        
        # Progress tracking (using Investigation model fields)
        "current_iteration": state["iteration"] - 1,  # Subtract 1 since we increment before work
        "max_iterations": state["max_iterations"],
        "phase": state.get("phase", "synthesis"),
        
        # Evidence database
        "entities": state.get("entities", {}),
        "facts": state.get("facts", []),
        "connections": state.get("connections", []),
        "anomalies": state.get("anomalies", []),
        "hypotheses": state.get("hypotheses", []),
        "questions": state.get("questions", []),  # Add questions
        
        # Extracted articles with full content
        "extracted_articles": [
            {
                "url": article.get("url"),
                "content": article.get("content"),
                "method": article.get("method"),
                "word_count": len(article.get("content", "").split()),
                "char_count": len(article.get("content", ""))
            }
            for article in state.get("extracted_content", [])
        ],
        
        # Search history for transparency
        "search_queries": state.get("previous_queries", []),
        "seen_urls": state.get("seen_urls", []),
        
        # Final outputs
        "article": state.get("final_report", ""),
        "article_draft": state.get("article_draft", ""),
        
        # Execution tracking
        "execution_log": state.get("execution_log", []),
        "cost_usd": cost_tracking.get("total_cost", 0.0),
        
        # User info
        "user_session": state.get("user_session"),
        "thread_id": state.get("thread_id")
    }
    
    # Upsert (update if exists, insert if new)
    await mongo_service.db.investigations.update_one(
        {"investigation_id": investigation_id},
        {"$set": doc},
        upsert=True
    )
    
    print(f"✅ Saved investigation to MongoDB: {investigation_id}")
    print(f"   Status: {doc['status']}")
    print(f"   Progress: {doc['current_iteration']}/{doc['max_iterations']} iterations")
    print(f"   Evidence: {len(doc['entities'])} entities, {len(doc['facts'])} facts, {len(doc.get('questions', []))} questions")
    print(f"   Cost: ${doc['cost_usd']:.3f}")
    
    return investigation_id


async def load_investigation(investigation_id: str) -> Optional[Dict[str, Any]]:
    """
    Load investigation from MongoDB to resume
    
    Args:
        investigation_id: Investigation UUID to load
        
    Returns:
        State dict ready to resume, or None if not found
    """
    await mongo_service.connect()
    
    doc = await mongo_service.db.investigations.find_one(
        {"investigation_id": investigation_id}
    )
    
    if not doc:
        print(f"❌ Investigation not found: {investigation_id}")
        return None
    
    print(f"✅ Loaded investigation from MongoDB: {investigation_id}")
    print(f"   Query: {doc['query']}")
    print(f"   Status: {doc['status']}")
    
    # Check if this investigation can be resumed (must have been run before)
    current_iter = doc.get('current_iteration', 0)
    if current_iter == 0:
        print(f"   📝 Fresh investigation (not yet run) - starting from scratch")
        return None  # Return None so it starts fresh
    
    print(f"   Progress: {current_iter}/{doc.get('max_iterations', 20)} iterations")
    print(f"   Evidence: {len(doc.get('entities', {}))} entities, {len(doc.get('facts', []))} facts")
    
    # Convert MongoDB doc back to state format
    state = {
        "investigation_id": doc["investigation_id"],
        "session_id": doc.get("session_id"),
        "initial_query": doc["query"],
        "iteration": current_iter + 1,  # Start from next iteration
        "max_iterations": doc.get("max_iterations", 20),
        
        # Restore evidence
        "entities": doc.get("entities", {}),
        "facts": doc.get("facts", []),
        "connections": doc.get("connections", []),
        "anomalies": doc.get("anomalies", []),
        "hypotheses": doc.get("hypotheses", []),
        "questions": doc.get("questions", []),
        "evidence": [],
        
        # Restore search history
        "seen_urls": doc.get("seen_urls", []),
        "previous_queries": doc.get("search_queries", []),
        "extracted_cache": {},  # Don't restore cache, will rebuild if needed
        
        # Working variables (start fresh each session)
        "search_results": [],
        "extracted_content": [],
        
        # Control
        "next_action": "search",
        "search_query": None,
        "investigation_complete": False,
        "final_report": doc.get("article", ""),  # Previous report if exists
        
        # Metadata
        "execution_log": doc.get("execution_log", []),
        "error_log": [],
        "artifacts": [],
        "cost_tracking": {
            "total_cost": doc.get("cost_usd", 0.0)
        },
        
        # Preserve creation timestamp
        "created_at": doc.get("created_at")
    }
    
    return state


async def get_investigation_summary(investigation_id: str) -> Optional[Dict[str, Any]]:
    """
    Get summary of investigation without loading full state
    
    Returns:
        Summary dict with key metrics, or None if not found
    """
    await mongo_service.connect()
    
    doc = await mongo_service.db.investigations.find_one(
        {"investigation_id": investigation_id},
        {
            "investigation_id": 1,
            "query": 1,
            "status": 1,
            "progress": 1,
            "created_at": 1,
            "updated_at": 1,
            "_id": 0
        }
    )
    
    return doc


async def list_investigations(limit: int = 20, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List recent investigations
    
    Args:
        limit: Maximum number to return
        status: Optional filter by status ("in_progress", "completed", "paused")
        
    Returns:
        List of investigation summaries
    """
    await mongo_service.connect()
    
    query = {}
    if status:
        query["status"] = status
    
    cursor = mongo_service.db.investigations.find(
        query,
        {
            "investigation_id": 1,
            "query": 1,
            "status": 1,
            "progress": 1,
            "created_at": 1,
            "updated_at": 1,
            "_id": 0
        }
    ).sort("updated_at", -1).limit(limit)
    
    return await cursor.to_list(length=limit)


if __name__ == "__main__":
    import asyncio
    
    async def test():
        """Test evidence repository"""
        
        # Test save
        test_state = {
            "initial_query": "Test investigation",
            "iteration": 5,
            "max_iterations": 20,
            "entities": {"TestEntity": {"type": "person", "role": "test"}},
            "facts": ["Fact 1", "Fact 2"],
            "connections": [],
            "anomalies": [],
            "hypotheses": [],
            "evidence": [],
            "seen_urls": ["https://example.com"],
            "previous_queries": ["query 1", "query 2"],
            "search_results": [],
            "extracted_content": [],
            "investigation_complete": False,
            "cost_tracking": {
                "tavily_searches": 2,
                "free_extracts": 3,
                "total_cost": 0.05
            }
        }
        
        inv_id = await save_investigation(test_state)
        print(f"\n✅ Saved test investigation: {inv_id}")
        
        # Test load
        loaded = await load_investigation(inv_id)
        if loaded:
            print(f"\n✅ Loaded investigation successfully")
            print(f"   Query: {loaded['initial_query']}")
            print(f"   Entities: {len(loaded['entities'])}")
            
        # Test list
        investigations = await list_investigations(limit=5)
        print(f"\n✅ Found {len(investigations)} investigations")
        for inv in investigations:
            print(f"   - {inv['investigation_id']}: {inv['query']} ({inv['status']})")
    
    asyncio.run(test())

