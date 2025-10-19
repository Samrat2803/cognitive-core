#!/usr/bin/env python3
"""
Script to delete all investigations from MongoDB
Use this to clean up test data
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add path for imports
sys.path.append(os.path.dirname(__file__))

from services.mongo_service import mongo_service


async def cleanup_investigations():
    """Delete all investigations from MongoDB"""
    
    print("\n" + "="*80)
    print("🧹 CLEANUP INVESTIGATIONS")
    print("="*80)
    
    try:
        # Connect to MongoDB
        await mongo_service.connect()
        print("✅ Connected to MongoDB")
        
        # Count existing investigations
        count = await mongo_service.db.investigations.count_documents({})
        print(f"\n📊 Found {count} investigations in database")
        
        if count == 0:
            print("✅ Database already clean!")
            return
        
        # List investigations before deletion
        print("\n📋 Investigations to delete:")
        cursor = mongo_service.db.investigations.find(
            {},
            {
                "investigation_id": 1,
                "query": 1,
                "status": 1,
                "current_iteration": 1,
                "created_at": 1,
                "_id": 0
            }
        ).limit(10)
        
        investigations = await cursor.to_list(length=10)
        for inv in investigations:
            print(f"   • {inv.get('investigation_id')}: {inv.get('query', 'N/A')[:50]}...")
            print(f"     Status: {inv.get('status')}, Iterations: {inv.get('current_iteration', 0)}")
        
        if count > 10:
            print(f"   ... and {count - 10} more")
        
        # Confirm deletion
        print(f"\n⚠️  This will DELETE ALL {count} investigations!")
        response = input("Type 'DELETE' to confirm: ")
        
        if response.strip().upper() != "DELETE":
            print("❌ Cleanup cancelled")
            return
        
        # Delete all investigations
        print("\n🗑️  Deleting investigations...")
        result = await mongo_service.db.investigations.delete_many({})
        
        print(f"✅ Deleted {result.deleted_count} investigations")
        
        # Verify cleanup
        final_count = await mongo_service.db.investigations.count_documents({})
        print(f"📊 Remaining investigations: {final_count}")
        
        if final_count == 0:
            print("\n✅ Cleanup complete!")
        else:
            print(f"\n⚠️  Warning: {final_count} investigations still remain")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*80 + "\n")


async def list_investigations():
    """List all investigations (for verification)"""
    
    print("\n" + "="*80)
    print("📋 LIST ALL INVESTIGATIONS")
    print("="*80)
    
    try:
        # Connect to MongoDB
        await mongo_service.connect()
        
        # Count investigations
        count = await mongo_service.db.investigations.count_documents({})
        print(f"\n📊 Total investigations: {count}")
        
        if count == 0:
            print("✅ No investigations found")
            return
        
        # List all investigations
        cursor = mongo_service.db.investigations.find(
            {},
            {
                "investigation_id": 1,
                "query": 1,
                "status": 1,
                "current_iteration": 1,
                "max_iterations": 1,
                "created_at": 1,
                "_id": 0
            }
        ).sort("created_at", -1)
        
        investigations = await cursor.to_list(length=100)
        
        for i, inv in enumerate(investigations, 1):
            print(f"\n{i}. {inv.get('investigation_id')}")
            print(f"   Query: {inv.get('query', 'N/A')}")
            print(f"   Status: {inv.get('status')}")
            print(f"   Progress: {inv.get('current_iteration', 0)}/{inv.get('max_iterations', 'N/A')}")
            print(f"   Created: {inv.get('created_at', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error listing investigations: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage investigations in MongoDB")
    parser.add_argument("action", choices=["cleanup", "list"], 
                       help="Action to perform: cleanup (delete all) or list (view all)")
    
    args = parser.parse_args()
    
    if args.action == "cleanup":
        asyncio.run(cleanup_investigations())
    elif args.action == "list":
        asyncio.run(list_investigations())

