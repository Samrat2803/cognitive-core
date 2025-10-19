"""
Standalone Runner for Tender Intelligence Agent

⚠️ IMPORTANT: This file allows testing the agent WITHOUT the master agent
DO NOT import anything from master agent except shared utilities
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add paths for standalone execution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# Import from current directory (simple imports like POCs)
from graph import create_tender_intelligence_graph
from state import TenderIntelligenceState

# Test queries - showcasing GENERAL PURPOSE capabilities
TEST_QUERIES = [
    {
        "query": "Defense ministry cloud computing tenders India",
        "action": "discover",
        "sources": [],  # No domain restrictions - search entire web
        "description": "Test 1: Government tenders (India)"
    },
    {
        "query": "Microsoft Azure procurement opportunities",
        "action": "discover",
        "sources": [],  # Will find Microsoft's procurement portal
        "description": "Test 2: Private company RFPs"
    },
    {
        "query": "Amazon AWS tender submissions",
        "action": "discover",
        "sources": ["amazon.com", "aws.amazon.com"],  # Optional: focus on Amazon domains
        "description": "Test 3: Company procurement with suggested domains"
    },
    {
        "query": "United Nations procurement opportunities",
        "action": "discover",
        "sources": [],
        "description": "Test 4: International organization tenders"
    },
    {
        "query": "UK government digital services tenders",
        "action": "discover",
        "sources": ["gov.uk"],  # Optional: focus on UK government
        "description": "Test 5: International government tenders"
    }
]


async def run_standalone_test(query_config: dict):
    """
    Run agent in complete isolation
    
    Args:
        query_config: Dict with query, action, ministries, etc.
    """
    
    print("\n" + "="*70)
    print(f"🚀 STANDALONE TEST: {query_config['description']}")
    print("="*70)
    
    # Create graph
    graph = create_tender_intelligence_graph()
    
    # Initialize state
    initial_state: TenderIntelligenceState = {
        "query": query_config["query"],
        "action": query_config["action"],
        "sources": query_config.get("sources", []),  # Optional suggested domains
        "categories": None,
        "location": None,
        "value_range": None,
        "date_range": None,
        "portals_discovered": [],
        "listing_pages": [],
        "crawl_results": [],
        "tenders_parsed": [],
        "tenders_stored": 0,
        "embeddings_generated": 0,
        "relevant_tenders": [],
        "similarity_scores": [],
        "summary": "",
        "key_findings": [],
        "recommendations": [],
        "confidence": 0.0,
        "artifacts": [],
        "execution_log": [],
        "error_log": [],
        "thread_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "execution_time": 0.0
    }
    
    print(f"📝 Query: {query_config['query']}")
    print(f"🎯 Action: {query_config['action']}")
    if query_config.get("sources"):
        print(f"📍 Suggested sources: {', '.join(query_config['sources'])}")
    else:
        print(f"🌐 Searching entire web (no restrictions)")
    print("\n⏳ Processing...")
    
    start_time = datetime.now()
    
    try:
        # Run agent
        result = await graph.ainvoke(initial_state)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        result["execution_time"] = duration
        
        # Display results
        print(f"\n✅ SUCCESS (completed in {duration:.2f}s)")
        print("\n" + "-"*70)
        print("📊 RESULTS:")
        print("-"*70)
        
        # Action-specific results
        action = query_config["action"]
        
        if action == "discover":
            print(f"\n🔍 Portals Discovered: {len(result['portals_discovered'])}")
            for i, portal in enumerate(result['portals_discovered'][:5], 1):
                print(f"   {i}. {portal.get('title', 'Unknown')}")
                print(f"      {portal.get('url', 'N/A')}")
            
            print(f"\n📄 Listing Pages Found: {len(result['listing_pages'])}")
            for i, page in enumerate(result['listing_pages'][:3], 1):
                print(f"   {i}. {page}")
        
        elif action == "crawl":
            print(f"\n📊 Tenders Parsed: {len(result['tenders_parsed'])}")
            print(f"💾 Tenders Stored: {result['tenders_stored']}")
            print(f"🧬 Embeddings Generated: {result['embeddings_generated']}")
            
            if result['tenders_parsed']:
                print("\n   Sample tenders:")
                for i, tender in enumerate(result['tenders_parsed'][:3], 1):
                    print(f"   {i}. {tender.get('title', 'Unknown')}")
                    print(f"      ID: {tender.get('tender_id', 'N/A')}")
                    print(f"      Org: {tender.get('organization', 'N/A')}")
        
        else:  # query
            print(f"\n🔎 Relevant Tenders Found: {len(result['relevant_tenders'])}")
            
            for i, tender in enumerate(result['relevant_tenders'][:5], 1):
                metadata = tender.get('metadata', {})
                score = tender.get('score', 0)
                print(f"   {i}. {metadata.get('title', 'Unknown')} (score: {score:.3f})")
                print(f"      Org: {metadata.get('organization', 'N/A')}")
        
        # Common outputs
        print(f"\n📝 Summary:")
        print(f"   {result['summary']}")
        
        print(f"\n🔍 Key Findings ({len(result['key_findings'])}):")
        for i, finding in enumerate(result['key_findings'][:5], 1):
            print(f"   {i}. {finding}")
        
        print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n📈 Confidence: {result['confidence']:.2%}")
        
        # Execution log
        print(f"\n📋 Execution Log ({len(result['execution_log'])} steps):")
        for log_entry in result["execution_log"]:
            print(f"   [{log_entry['step']}] {log_entry['action']}")
        
        # Errors (if any)
        if result["error_log"]:
            print(f"\n⚠️  Errors Encountered ({len(result['error_log'])}):")
            for error in result["error_log"]:
                print(f"   - {error}")
        
        # Save result to file
        output_dir = "examples"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(
            output_dir, 
            f"test_{query_config['action']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_file, 'w') as f:
            # Remove non-serializable fields for JSON
            json_result = {
                "query": result.get("query"),
                "action": result.get("action"),
                "portals_discovered": result.get("portals_discovered", []),
                "listing_pages": result.get("listing_pages", []),
                "tenders_stored": result.get("tenders_stored", 0),
                "embeddings_generated": result.get("embeddings_generated", 0),
                "summary": result.get("summary"),
                "key_findings": result.get("key_findings"),
                "recommendations": result.get("recommendations"),
                "confidence": result.get("confidence"),
                "execution_log": result.get("execution_log"),
                "error_log": result.get("error_log"),
                "execution_time": duration
            }
            json.dump(json_result, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        print("\n" + "="*70)
        
        return result
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n❌ FAILED (after {duration:.2f}s)")
        print(f"Error: {str(e)}")
        print("\n" + "="*70)
        
        import traceback
        traceback.print_exc()
        
        return None


async def run_all_tests():
    """Run all test queries"""
    
    print("\n" + "🎯 "*35)
    print("TENDER INTELLIGENCE - STANDALONE TEST SUITE")
    print("🎯 "*35)
    print(f"\nTotal Tests: {len(TEST_QUERIES)}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for i, query_config in enumerate(TEST_QUERIES, 1):
        print(f"\n\n{'='*70}")
        print(f"TEST {i}/{len(TEST_QUERIES)}")
        print(f"{'='*70}")
        
        result = await run_standalone_test(query_config)
        results.append({
            "test_number": i,
            "query": query_config["query"],
            "action": query_config["action"],
            "success": result is not None,
            "result": result
        })
        
        # Pause between tests
        if i < len(TEST_QUERIES):
            print("\n⏸️  Pausing 3 seconds before next test...")
            await asyncio.sleep(3)
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {successful/len(results):.1%}")
    
    print("\nTest Results:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"   {status} Test {r['test_number']}: {r['action']} - {r['query']}")
    
    print("\n" + "="*70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    return results


def main():
    """Main entry point"""
    
    # Check if specific test query provided
    if len(sys.argv) > 1:
        # Custom query from command line
        action = sys.argv[1] if len(sys.argv) > 1 else "query"
        query_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Find defense tenders"
        
        custom_query = {
            "query": query_text,
            "action": action,
            "ministries": ["Defense"],
            "description": f"Custom {action} query"
        }
        asyncio.run(run_standalone_test(custom_query))
    else:
        # Run all test queries
        asyncio.run(run_all_tests())


if __name__ == "__main__":
    print("\n" + "🔬 "*35)
    print("TENDER INTELLIGENCE AGENT - STANDALONE MODE")
    print("This tests the agent WITHOUT the master agent")
    print("🔬 "*35)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

