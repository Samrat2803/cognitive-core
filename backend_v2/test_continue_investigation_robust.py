#!/usr/bin/env python3
"""
ROBUST Test Suite for Continue Investigation Feature
Tests all aspects of the continue investigation functionality
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

# Test configuration
TEST_QUERY = "Recent developments in quantum computing"
INITIAL_ITERATIONS = 2
CONTINUE_ITERATIONS = 2
TOTAL_EXPECTED_ITERATIONS = INITIAL_ITERATIONS + CONTINUE_ITERATIONS

# Tracking data
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


class InvestigationTracker:
    """Track investigation progress across both runs"""
    
    def __init__(self):
        self.initial_run = {
            "hypotheses": [],
            "questions": [],
            "entities": [],
            "facts": [],
            "iterations": 0,
            "start_time": None,
            "end_time": None
        }
        self.continued_run = {
            "hypotheses": [],
            "questions": [],
            "entities": [],
            "facts": [],
            "iterations": 0,
            "start_time": None,
            "end_time": None
        }
        self.websocket_events = []
    
    def track_event(self, event_type: str, data: Dict[str, Any], phase: str):
        """Track WebSocket event"""
        self.websocket_events.append({
            "type": event_type,
            "data": data,
            "phase": phase,
            "timestamp": datetime.now().isoformat()
        })


tracker = InvestigationTracker()


async def run_investigation_phase(investigation_id: str, phase: str, timeout: int = 180):
    """
    Run investigation phase via WebSocket
    
    Args:
        investigation_id: Investigation ID
        phase: "initial" or "continued"
        timeout: Max wait time in seconds
    """
    global tracker
    
    uri = f"{WS_URL}/ws/investigations/{investigation_id}"
    
    print(f"🔌 Connecting to WebSocket: {uri}")
    print(f"   Phase: {phase}")
    print(f"   Timeout: {timeout}s")
    
    phase_data = tracker.initial_run if phase == "initial" else tracker.continued_run
    phase_data["start_time"] = datetime.now()
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send start message
            await websocket.send(json.dumps({"type": "start"}))
            print("✅ Sent start message")
            
            # Listen for messages
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                    data = json.loads(message)
                    
                    msg_type = data.get("type")
                    msg_data = data.get("data", {})
                    
                    # Track event
                    tracker.track_event(msg_type, msg_data, phase)
                    
                    # Process specific event types
                    if msg_type == "hypothesis_updated":
                        hyp = msg_data
                        phase_data["hypotheses"].append(hyp)
                        hyp_statement = hyp.get("statement", "")[:60]
                        print(f"💡 [{phase.upper()}] Hypothesis: {hyp_statement}...")
                        print(f"   Status: {hyp.get('status')}, Confidence: {hyp.get('confidence', 0.0):.2f}")
                    
                    elif msg_type == "question_discovered":
                        q = msg_data
                        phase_data["questions"].append(q)
                        question = q.get("question", "")[:60]
                        print(f"❓ [{phase.upper()}] Question: {question}...")
                        print(f"   Hypothesis ID: {q.get('hypothesis_id')}, Iteration: {q.get('iteration')}")
                    
                    elif msg_type == "entity_discovered":
                        entity = msg_data
                        phase_data["entities"].append(entity)
                        print(f"👤 [{phase.upper()}] Entity: {entity.get('name', 'N/A')} ({entity.get('type', 'N/A')})")
                    
                    elif msg_type == "fact_recorded":
                        fact = msg_data
                        phase_data["facts"].append(fact)
                        fact_content = fact.get("content", "")[:50]
                        print(f"📌 [{phase.upper()}] Fact: {fact_content}...")
                    
                    elif msg_type == "iteration_start":
                        iteration = msg_data.get("iteration")
                        print(f"🔄 [{phase.upper()}] Iteration {iteration} started")
                    
                    elif msg_type == "iteration_complete":
                        iteration = msg_data.get("iteration")
                        cost = msg_data.get("cost", 0.0)
                        print(f"✅ [{phase.upper()}] Iteration {iteration} complete (Cost: ${cost:.3f})")
                        phase_data["iterations"] = iteration
                    
                    elif msg_type == "investigation_complete":
                        print(f"✅ [{phase.upper()}] Investigation complete!")
                        phase_data["end_time"] = datetime.now()
                        break
                    
                    elif msg_type == "error":
                        error_msg = msg_data.get("message", "Unknown error")
                        print(f"❌ [{phase.upper()}] Error: {error_msg}")
                        test_results["failed"].append(f"WebSocket error in {phase}: {error_msg}")
                        break
                    
                except asyncio.TimeoutError:
                    print(f"⏱️  [{phase.upper()}] Timeout after {timeout}s")
                    test_results["warnings"].append(f"Timeout in {phase} phase after {timeout}s")
                    break
                except Exception as e:
                    print(f"❌ [{phase.upper()}] Error: {e}")
                    test_results["failed"].append(f"Error in {phase}: {str(e)}")
                    break
    
    except Exception as e:
        print(f"❌ Failed to connect WebSocket: {e}")
        test_results["failed"].append(f"WebSocket connection failed: {str(e)}")


def verify_mongodb_state(investigation_id: str, expected_iterations: int, phase: str) -> Dict[str, Any]:
    """Verify MongoDB state matches expectations"""
    
    print(f"\n📚 Verifying MongoDB state ({phase})...")
    
    response = requests.get(f"{BASE_URL}/api/investigations/{investigation_id}")
    
    if not response.ok:
        test_results["failed"].append(f"Failed to fetch MongoDB state in {phase}: {response.status_code}")
        return {}
    
    data = response.json()["data"]
    
    # Extract data
    db_hypotheses = data.get("hypotheses", [])
    db_questions = data.get("questions", [])
    db_entities = data.get("entities", {})
    db_facts = data.get("facts", [])
    db_connections = data.get("connections", [])
    db_anomalies = data.get("anomalies", [])
    db_iterations = data.get("current_iteration", 0)
    db_max_iterations = data.get("max_iterations", 0)
    db_status = data.get("status", "unknown")
    db_article = data.get("article", "")
    
    # Print state
    print(f"   Hypotheses: {len(db_hypotheses)}")
    print(f"   Questions: {len(db_questions)}")
    print(f"   Entities: {len(db_entities)}")
    print(f"   Facts: {len(db_facts)}")
    print(f"   Connections: {len(db_connections)}")
    print(f"   Anomalies: {len(db_anomalies)}")
    print(f"   Iterations: {db_iterations}/{db_max_iterations}")
    print(f"   Status: {db_status}")
    print(f"   Article: {len(db_article)} chars")
    
    # Verify iterations
    if db_iterations == expected_iterations:
        test_results["passed"].append(f"✅ {phase}: Iterations correct ({db_iterations}/{expected_iterations})")
    else:
        test_results["failed"].append(f"❌ {phase}: Iterations incorrect ({db_iterations}/{expected_iterations})")
    
    # Verify status
    expected_status = "completed" if phase == "final" else "active"
    if db_status == expected_status:
        test_results["passed"].append(f"✅ {phase}: Status correct ({db_status})")
    else:
        test_results["warnings"].append(f"⚠️  {phase}: Status unexpected ({db_status}, expected {expected_status})")
    
    # Verify data presence
    if len(db_hypotheses) > 0:
        test_results["passed"].append(f"✅ {phase}: Hypotheses present ({len(db_hypotheses)})")
    else:
        test_results["warnings"].append(f"⚠️  {phase}: No hypotheses found")
    
    if len(db_questions) > 0:
        test_results["passed"].append(f"✅ {phase}: Questions present ({len(db_questions)})")
    else:
        test_results["warnings"].append(f"⚠️  {phase}: No questions found")
    
    if len(db_entities) > 0:
        test_results["passed"].append(f"✅ {phase}: Entities present ({len(db_entities)})")
    else:
        test_results["warnings"].append(f"⚠️  {phase}: No entities found")
    
    return data


def verify_accumulation(initial_data: Dict, final_data: Dict):
    """Verify data accumulated correctly between runs"""
    
    print("\n🔍 Verifying data accumulation...")
    
    initial_hypotheses = len(initial_data.get("hypotheses", []))
    final_hypotheses = len(final_data.get("hypotheses", []))
    
    initial_questions = len(initial_data.get("questions", []))
    final_questions = len(final_data.get("questions", []))
    
    initial_entities = len(initial_data.get("entities", {}))
    final_entities = len(final_data.get("entities", {}))
    
    initial_facts = len(initial_data.get("facts", []))
    final_facts = len(final_data.get("facts", []))
    
    # Test accumulation
    if final_hypotheses >= initial_hypotheses:
        test_results["passed"].append(f"✅ Hypotheses accumulated ({initial_hypotheses} → {final_hypotheses})")
    else:
        test_results["failed"].append(f"❌ Hypotheses lost ({initial_hypotheses} → {final_hypotheses})")
    
    if final_questions >= initial_questions:
        test_results["passed"].append(f"✅ Questions accumulated ({initial_questions} → {final_questions})")
    else:
        test_results["failed"].append(f"❌ Questions lost ({initial_questions} → {final_questions})")
    
    if final_entities >= initial_entities:
        test_results["passed"].append(f"✅ Entities accumulated ({initial_entities} → {final_entities})")
    else:
        test_results["failed"].append(f"❌ Entities lost ({initial_entities} → {final_entities})")
    
    if final_facts >= initial_facts:
        test_results["passed"].append(f"✅ Facts accumulated ({initial_facts} → {final_facts})")
    else:
        test_results["failed"].append(f"❌ Facts lost ({initial_facts} → {final_facts})")


def verify_websocket_events():
    """Verify WebSocket events were received correctly"""
    
    print("\n🔌 Verifying WebSocket events...")
    
    initial_events = [e for e in tracker.websocket_events if e["phase"] == "initial"]
    continued_events = [e for e in tracker.websocket_events if e["phase"] == "continued"]
    
    print(f"   Initial phase events: {len(initial_events)}")
    print(f"   Continued phase events: {len(continued_events)}")
    
    # Count event types
    event_types = {}
    for event in tracker.websocket_events:
        event_type = event["type"]
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print(f"\n   Event type breakdown:")
    for event_type, count in sorted(event_types.items()):
        print(f"      {event_type}: {count}")
    
    # Verify critical events
    if event_types.get("hypothesis_updated", 0) > 0:
        test_results["passed"].append(f"✅ Hypothesis events received ({event_types['hypothesis_updated']})")
    else:
        test_results["warnings"].append("⚠️  No hypothesis events received")
    
    if event_types.get("question_discovered", 0) > 0:
        test_results["passed"].append(f"✅ Question events received ({event_types['question_discovered']})")
    else:
        test_results["warnings"].append("⚠️  No question events received")
    
    if event_types.get("investigation_complete", 0) == 2:
        test_results["passed"].append("✅ Both phases completed")
    else:
        test_results["failed"].append(f"❌ Expected 2 completion events, got {event_types.get('investigation_complete', 0)}")


def print_test_summary():
    """Print final test summary"""
    
    print("\n" + "="*80)
    print("🎯 TEST SUMMARY")
    print("="*80)
    
    total_tests = len(test_results["passed"]) + len(test_results["failed"]) + len(test_results["warnings"])
    passed_count = len(test_results["passed"])
    failed_count = len(test_results["failed"])
    warning_count = len(test_results["warnings"])
    
    print(f"\n📊 Results: {passed_count}/{total_tests} passed")
    print(f"   ✅ Passed: {passed_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   ⚠️  Warnings: {warning_count}")
    
    if test_results["passed"]:
        print(f"\n✅ Passed Tests:")
        for test in test_results["passed"]:
            print(f"   {test}")
    
    if test_results["failed"]:
        print(f"\n❌ Failed Tests:")
        for test in test_results["failed"]:
            print(f"   {test}")
    
    if test_results["warnings"]:
        print(f"\n⚠️  Warnings:")
        for warning in test_results["warnings"]:
            print(f"   {warning}")
    
    # Final verdict
    print("\n" + "="*80)
    if failed_count == 0:
        print("✅ ALL TESTS PASSED!")
        if warning_count > 0:
            print(f"⚠️  But {warning_count} warnings detected")
    else:
        print(f"❌ {failed_count} TESTS FAILED")
    print("="*80 + "\n")
    
    return failed_count == 0


def main():
    """Main test execution"""
    
    print("\n" + "="*80)
    print("🧪 ROBUST CONTINUE INVESTIGATION TEST SUITE")
    print("="*80)
    print(f"\nTest Configuration:")
    print(f"   Query: {TEST_QUERY}")
    print(f"   Initial iterations: {INITIAL_ITERATIONS}")
    print(f"   Continue iterations: {CONTINUE_ITERATIONS}")
    print(f"   Total expected: {TOTAL_EXPECTED_ITERATIONS}")
    print()
    
    # Step 1: Create investigation
    print("\n" + "="*80)
    print("📝 STEP 1: Create Investigation")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/api/investigations",
        json={
            "query": TEST_QUERY,
            "title": "Continue Investigation Test - Robust",
            "max_iterations": INITIAL_ITERATIONS
        }
    )
    
    if not response.ok:
        print(f"❌ Failed to create investigation: {response.status_code}")
        print(f"   Response: {response.text}")
        test_results["failed"].append("Failed to create investigation")
        print_test_summary()
        return False
    
    investigation_id = response.json()["investigation_id"]
    print(f"✅ Created investigation: {investigation_id}")
    test_results["passed"].append("✅ Investigation created successfully")
    
    # Step 2: Run initial investigation
    print("\n" + "="*80)
    print(f"🚀 STEP 2: Run Initial Investigation ({INITIAL_ITERATIONS} iterations)")
    print("="*80)
    
    asyncio.run(run_investigation_phase(investigation_id, "initial", timeout=300))
    
    # Step 3: Verify MongoDB state after initial run
    print("\n" + "="*80)
    print("📚 STEP 3: Verify MongoDB State (After Initial Run)")
    print("="*80)
    
    initial_data = verify_mongodb_state(investigation_id, INITIAL_ITERATIONS, "initial")
    
    # Step 4: Continue investigation
    print("\n" + "="*80)
    print(f"🔄 STEP 4: Continue Investigation (+{CONTINUE_ITERATIONS} iterations)")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/api/investigations/{investigation_id}/continue",
        json={"additional_iterations": CONTINUE_ITERATIONS}
    )
    
    if not response.ok:
        print(f"❌ Failed to continue investigation: {response.status_code}")
        test_results["failed"].append("Failed to continue investigation")
    else:
        print(f"✅ Continue request accepted")
        test_results["passed"].append("✅ Continue request accepted")
    
    # Step 5: Run continued investigation
    print("\n" + "="*80)
    print(f"🚀 STEP 5: Run Continued Investigation (+{CONTINUE_ITERATIONS} iterations)")
    print("="*80)
    
    asyncio.run(run_investigation_phase(investigation_id, "continued", timeout=300))
    
    # Step 6: Verify MongoDB state after continuation
    print("\n" + "="*80)
    print("📚 STEP 6: Verify MongoDB State (After Continuation)")
    print("="*80)
    
    final_data = verify_mongodb_state(investigation_id, TOTAL_EXPECTED_ITERATIONS, "final")
    
    # Step 7: Verify data accumulation
    print("\n" + "="*80)
    print("🔍 STEP 7: Verify Data Accumulation")
    print("="*80)
    
    verify_accumulation(initial_data, final_data)
    
    # Step 8: Verify WebSocket events
    print("\n" + "="*80)
    print("🔌 STEP 8: Verify WebSocket Events")
    print("="*80)
    
    verify_websocket_events()
    
    # Step 9: Print test summary
    success = print_test_summary()
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

