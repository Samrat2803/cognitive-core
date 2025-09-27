"""
Main script to run the Web Research Agent
"""

import asyncio
import os
from dotenv import load_dotenv
from research_agent import WebResearchAgent

# Load environment variables
load_dotenv()

async def main():
    """Main function to run the research agent"""
    
    # Check if API keys are set
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ TAVILY_API_KEY not found in environment variables")
        print("Please set your Tavily API key in the .env file")
        return
    
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ No LLM API key found")
        print("Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY in the .env file")
        return
    
    # Initialize the agent
    llm_provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
    model = "gpt-4o-mini" if llm_provider == "openai" else "claude-3-haiku-20240307"
    
    print(f"🚀 Initializing Web Research Agent with {llm_provider} ({model})")
    agent = WebResearchAgent(llm_provider=llm_provider, model=model)
    
    # Interactive mode
    print("\n" + "="*60)
    print("🔍 Web Research Agent - Interactive Mode")
    print("="*60)
    print("Enter your research queries (type 'quit' to exit)")
    print("="*60)
    
    while True:
        try:
            query = input("\n📝 Enter your research query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                print("❌ Please enter a valid query")
                continue
            
            print(f"\n🔍 Researching: {query}")
            print("⏳ This may take a few moments...")
            
            # Perform research
            result = await agent.research(query)
            
            if result.get("error"):
                print(f"❌ Error: {result['error']}")
                continue
            
            # Display results
            print(f"\n✅ Research completed!")
            print(f"🔍 Search terms used: {', '.join(result['search_terms'])}")
            print(f"📚 Sources found: {len(result['sources'])}")
            print(f"\n📋 Final Answer:")
            print("-" * 50)
            print(result['final_answer'])
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

def run_sync_example():
    """Run a synchronous example"""
    print("🚀 Running synchronous example...")
    
    agent = WebResearchAgent(llm_provider="openai", model="gpt-4o-mini")
    
    query = "What are the latest developments in artificial intelligence?"
    print(f"🔍 Researching: {query}")
    
    result = agent.research_sync(query)
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Research completed!")
        print(f"🔍 Search terms: {', '.join(result['search_terms'])}")
        print(f"📚 Sources: {len(result['sources'])}")
        print(f"\n📋 Answer:\n{result['final_answer']}")

if __name__ == "__main__":
    # Check if running in interactive mode or example mode
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--example":
        run_sync_example()
    else:
        asyncio.run(main())
