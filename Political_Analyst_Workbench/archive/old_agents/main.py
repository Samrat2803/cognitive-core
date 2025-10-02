"""
Political Analyst Workbench - Interactive Main Runner
"""

import asyncio
from political_agent import PoliticalAnalystAgent


async def main():
    """Main interactive loop for the Political Analyst Workbench"""
    
    print("🏛️  Political Analyst Workbench")
    print("=" * 50)
    print("An AI agent powered by LangGraph and Tavily for political analysis")
    print("Type 'exit', 'quit', or 'q' to end the session")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("🔧 Initializing agent...")
        agent = PoliticalAnalystAgent()
        print("✅ Agent ready!")
        print()
        
        # Interactive loop
        while True:
            try:
                # Get user input
                user_input = input("🗣️  You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process the query
                print("🤔 Thinking...")
                response = await agent.process_query(user_input)
                
                # Display response
                print(f"🤖 Agent: {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                print("Please try again or type 'exit' to quit.")
                print()
                
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        print("Please check your API keys in the .env file.")
        return


def run_single_query(query: str) -> str:
    """Run a single query (useful for testing)"""
    
    try:
        agent = PoliticalAnalystAgent()
        return agent.process_query_sync(query)
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Check if we're running a single query or interactive mode
    import sys
    
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}")
        print("=" * 50)
        response = run_single_query(query)
        print(f"Response: {response}")
    else:
        # Interactive mode
        asyncio.run(main())

