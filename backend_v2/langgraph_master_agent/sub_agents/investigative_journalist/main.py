"""
Investigative Journalist - Standalone Test Runner

Run without master agent for testing
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')

# Import the investigator (we'll refactor to use lean_investigator for now)
sys.path.insert(0, '/Users/kiransah/Desktop/code/tavily_assignment/exp_3')
from lean_investigator import LeanInvestigator


async def test_standalone(query: str = "India cough syrup deaths", max_iterations: int = 5):
    """
    Test investigative journalist in standalone mode
    
    Args:
        query: Investigation query
        max_iterations: Maximum iterations to run
    """
    print(f"\n{'='*80}")
    print(f"🚀 INVESTIGATIVE JOURNALIST - STANDALONE TEST")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print(f"Max Iterations: {max_iterations}")
    print(f"{'='*80}\n")
    
    # Create investigator
    investigator = LeanInvestigator(max_iterations=max_iterations)
    
    # Run investigation
    result = await investigator.investigate(query)
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETE")
    print(f"{'='*80}")
    print(f"Entities: {len(result['entities'])}")
    print(f"Facts: {len(result['facts'])}")
    print(f"Connections: {len(result['connections'])}")
    print(f"Anomalies: {len(result['anomalies'])}")
    print(f"Cost: ${investigator.costs['total_cost']:.3f}")
    print(f"{'='*80}\n")
    
    return result


if __name__ == "__main__":
    import sys
    
    # Parse command line args (optional)
    query = sys.argv[1] if len(sys.argv) > 1 else "India cough syrup deaths"
    max_iter = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Run test
    asyncio.run(test_standalone(query, max_iter))

