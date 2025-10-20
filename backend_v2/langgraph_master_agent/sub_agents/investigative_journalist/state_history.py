"""
State History Manager for Investigative Journalist V2

This module manages historical state snapshots for investigations,
allowing users to view the investigation's evolution over time and
potentially resume from any previous iteration.

Key Features:
- Stores state snapshot after each iteration
- Retrieves full history or specific iteration
- Supports state compression to manage storage
- Enables investigation replay and analysis
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class StateHistoryManager:
    """Manages historical state snapshots for investigations."""
    
    def __init__(self):
        """Initialize the state history manager with MongoDB connection."""
        self.mongo_uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_CONNECTION_STRING")
        if not self.mongo_uri:
            raise ValueError("MONGODB_URI or MONGODB_CONNECTION_STRING not found in environment variables")
        
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection_name = "investigation_state_history"
    
    async def _ensure_connection(self):
        """Ensure MongoDB connection is established."""
        if self.client is None:
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client.tavily_investigation_db
            
            # Create indexes for efficient queries
            collection = self.db[self.collection_name]
            await collection.create_index([("investigation_id", 1), ("iteration", 1)], unique=True)
            await collection.create_index([("investigation_id", 1), ("timestamp", -1)])
            await collection.create_index("investigation_id")
    
    async def save_state_snapshot(
        self,
        investigation_id: str,
        iteration: int,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a state snapshot for a specific iteration.
        
        Args:
            investigation_id: Unique investigation identifier
            iteration: Current iteration number
            state: Complete state dictionary
            metadata: Optional metadata (e.g., node that generated this state)
        
        Returns:
            True if saved successfully, False otherwise
        """
        await self._ensure_connection()
        
        try:
            document = {
                "investigation_id": investigation_id,
                "iteration": iteration,
                "state": state,
                "timestamp": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            # Use upsert to handle potential duplicates
            await self.db[self.collection_name].update_one(
                {
                    "investigation_id": investigation_id,
                    "iteration": iteration
                },
                {"$set": document},
                upsert=True
            )
            
            return True
        except Exception as e:
            print(f"Error saving state snapshot: {e}")
            return False
    
    async def get_state_snapshot(
        self,
        investigation_id: str,
        iteration: int
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific state snapshot.
        
        Args:
            investigation_id: Unique investigation identifier
            iteration: Iteration number to retrieve
        
        Returns:
            State dictionary if found, None otherwise
        """
        await self._ensure_connection()
        
        try:
            document = await self.db[self.collection_name].find_one({
                "investigation_id": investigation_id,
                "iteration": iteration
            })
            
            if document:
                return document.get("state")
            return None
        except Exception as e:
            print(f"Error retrieving state snapshot: {e}")
            return None
    
    async def get_latest_state(
        self,
        investigation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent state for an investigation.
        
        Args:
            investigation_id: Unique investigation identifier
        
        Returns:
            Latest state dictionary if found, None otherwise
        """
        await self._ensure_connection()
        
        try:
            document = await self.db[self.collection_name].find_one(
                {"investigation_id": investigation_id},
                sort=[("iteration", -1)]
            )
            
            if document:
                return document.get("state")
            return None
        except Exception as e:
            print(f"Error retrieving latest state: {e}")
            return None
    
    async def get_state_history(
        self,
        investigation_id: str,
        include_full_state: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get the complete history of state snapshots for an investigation.
        
        Args:
            investigation_id: Unique investigation identifier
            include_full_state: If True, include full state; if False, only metadata
        
        Returns:
            List of state snapshots ordered by iteration
        """
        await self._ensure_connection()
        
        try:
            cursor = self.db[self.collection_name].find(
                {"investigation_id": investigation_id}
            ).sort("iteration", 1)
            
            snapshots = []
            async for document in cursor:
                if include_full_state:
                    snapshots.append({
                        "iteration": document["iteration"],
                        "timestamp": document["timestamp"],
                        "state": document["state"],
                        "metadata": document.get("metadata", {})
                    })
                else:
                    # Summary only (for UI list view)
                    state = document["state"]
                    snapshots.append({
                        "iteration": document["iteration"],
                        "timestamp": document["timestamp"],
                        "summary": {
                            "phase": state.get("meta", {}).get("phase"),
                            "confidence": state.get("meta", {}).get("overall_confidence"),
                            "hypotheses_count": len(state.get("hypotheses", [])),
                            "facts_count": len(state.get("facts", [])),
                            "entities_count": len(state.get("entities", [])),
                        },
                        "metadata": document.get("metadata", {})
                    })
            
            return snapshots
        except Exception as e:
            print(f"Error retrieving state history: {e}")
            return []
    
    async def get_iteration_count(
        self,
        investigation_id: str
    ) -> int:
        """
        Get the number of iterations stored for an investigation.
        
        Args:
            investigation_id: Unique investigation identifier
        
        Returns:
            Number of stored iterations
        """
        await self._ensure_connection()
        
        try:
            count = await self.db[self.collection_name].count_documents({
                "investigation_id": investigation_id
            })
            return count
        except Exception as e:
            print(f"Error counting iterations: {e}")
            return 0
    
    async def delete_investigation_history(
        self,
        investigation_id: str
    ) -> bool:
        """
        Delete all state history for an investigation.
        
        Args:
            investigation_id: Unique investigation identifier
        
        Returns:
            True if deleted successfully, False otherwise
        """
        await self._ensure_connection()
        
        try:
            result = await self.db[self.collection_name].delete_many({
                "investigation_id": investigation_id
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting investigation history: {e}")
            return False
    
    async def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None


# Global instance for easy access
_history_manager: Optional[StateHistoryManager] = None

def get_history_manager() -> StateHistoryManager:
    """Get or create the global state history manager instance."""
    global _history_manager
    if _history_manager is None:
        _history_manager = StateHistoryManager()
    return _history_manager


# ============================================
# Utility Functions
# ============================================

async def save_state(
    investigation_id: str,
    iteration: int,
    state: Dict[str, Any],
    node_name: Optional[str] = None
) -> bool:
    """
    Convenience function to save a state snapshot.
    
    Args:
        investigation_id: Unique investigation identifier
        iteration: Current iteration number
        state: Complete state dictionary
        node_name: Optional name of the node that generated this state
    
    Returns:
        True if saved successfully, False otherwise
    """
    manager = get_history_manager()
    metadata = {"node": node_name} if node_name else None
    return await manager.save_state_snapshot(investigation_id, iteration, state, metadata)


async def get_state(
    investigation_id: str,
    iteration: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to retrieve a state snapshot.
    
    Args:
        investigation_id: Unique investigation identifier
        iteration: Iteration to retrieve (if None, gets latest)
    
    Returns:
        State dictionary if found, None otherwise
    """
    manager = get_history_manager()
    
    if iteration is None:
        return await manager.get_latest_state(investigation_id)
    else:
        return await manager.get_state_snapshot(investigation_id, iteration)


async def get_history_summary(
    investigation_id: str
) -> List[Dict[str, Any]]:
    """
    Get a summary of all iterations for an investigation.
    
    Args:
        investigation_id: Unique investigation identifier
    
    Returns:
        List of iteration summaries
    """
    manager = get_history_manager()
    return await manager.get_state_history(investigation_id, include_full_state=False)


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    async def test_history_manager():
        """Test the state history manager."""
        manager = StateHistoryManager()
        
        # Test data
        test_id = "test_inv_12345"
        
        # Save multiple iterations
        for i in range(1, 4):
            test_state = {
                "meta": {
                    "iteration": i,
                    "phase": "explore" if i < 3 else "deep_dive",
                    "overall_confidence": i * 0.3
                },
                "hypotheses": [{"id": f"H{i}", "statement": f"Test hypothesis {i}"}],
                "facts": [f"Fact {i}.1", f"Fact {i}.2"],
                "entities": []
            }
            
            success = await manager.save_state_snapshot(
                test_id, i, test_state, {"node": f"node_{i}"}
            )
            print(f"Saved iteration {i}: {success}")
        
        # Retrieve specific iteration
        state_2 = await manager.get_state_snapshot(test_id, 2)
        print(f"\nIteration 2 state: {state_2 is not None}")
        
        # Get latest state
        latest = await manager.get_latest_state(test_id)
        print(f"Latest iteration: {latest.get('meta', {}).get('iteration') if latest else None}")
        
        # Get history summary
        history = await manager.get_state_history(test_id, include_full_state=False)
        print(f"\nHistory summary ({len(history)} iterations):")
        for snapshot in history:
            print(f"  Iteration {snapshot['iteration']}: {snapshot['summary']}")
        
        # Cleanup
        deleted = await manager.delete_investigation_history(test_id)
        print(f"\nDeleted test data: {deleted}")
        
        await manager.close()
    
    # Run test
    asyncio.run(test_history_manager())

