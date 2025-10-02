# Master Political Analyst Agent

LangGraph-based master agent for the Political Analyst Workbench.

## Architecture

```
START
  ↓
Conversation Manager  (Initialize context, manage history)
  ↓
Strategic Planner     (Analyze query, plan tool usage)
  ↓
Tool Executor         (Execute Tavily tools, call sub-agents)
  ↓
Decision Gate         (Check if more data needed)
  ↓ [loop if needed]
  ↓ [continue if ready]
Response Synthesizer  (Compile final response)
  ↓
END
```

## Nodes

### 1. **Conversation Manager**
- Manages conversation history
- Initializes session context
- Tracks conversation state

### 2. **Strategic Planner**
- Analyzes user query intent
- Determines which tools to use
- Plans execution strategy
- Uses GPT-4o-mini for planning

### 3. **Tool Executor**
- Executes Tavily tools:
  - **Search**: Real-time web search
  - **Extract**: Content extraction from URLs
  - **Crawl**: Deep website crawling
- Calls sub-agents:
  - **Sentiment Analyzer**: Multi-country sentiment analysis
  - Future: Fact checker, source credibility, etc.

### 4. **Decision Gate**
- Evaluates if sufficient information gathered
- Routes to retry tools or proceed to synthesis
- Enforces iteration limits (max 3)

### 5. **Response Synthesizer**
- Compiles results from all sources
- Formats user-friendly response
- Adds citations and sources
- Uses GPT-4o-mini for synthesis

## Tools Available

### Direct Tavily Tools
- `tavily_search`: Real-time web search
- `tavily_extract`: Extract content from URLs
- `tavily_crawl`: Deep crawl websites

### Sub-Agents
- `sentiment_analysis_agent`: Comprehensive geopolitical sentiment analysis (to be implemented)
- `fact_checker_agent`: Claim verification (future)
- `source_credibility_agent`: Source reliability assessment (future)

## Usage

### Basic Usage

```python
from langgraph_master_agent.main import MasterPoliticalAnalyst

# Initialize
agent = MasterPoliticalAnalyst()

# Process query
result = agent.process_query_sync("What's happening in Gaza?")

print(result["response"])
print(f"Confidence: {result['confidence']}")
print(f"Citations: {len(result['citations'])}")
```

### Async Usage

```python
import asyncio
from langgraph_master_agent.main import MasterPoliticalAnalyst

async def main():
    agent = MasterPoliticalAnalyst()
    result = await agent.process_query("Analyze US-China relations")
    print(result["response"])

asyncio.run(main())
```

### With Real-time Callbacks

```python
def update_ui(result):
    print(f"Tools used: {result['tools_used']}")
    print(f"Progress: {result['iterations']}")

agent = MasterPoliticalAnalyst(update_callback=update_ui)
result = agent.process_query_sync("Latest climate policy updates")
```

## Running Tests

```bash
cd Political_Analyst_Workbench

# Activate venv if available
source .venv/bin/activate

# Run master agent
python langgraph_master_agent/main.py
```

## Configuration

Edit `config.py` to customize:
- LLM model and temperature
- Max iterations
- Tavily search settings
- Tool registry

## State Schema

The agent maintains comprehensive state through `MasterAgentState`:

```python
{
    "conversation_history": [...],
    "current_message": "user query",
    "task_plan": "planned actions",
    "tools_to_use": ["tavily_search"],
    "tool_results": {...},
    "sub_agent_results": {...},
    "final_response": "formatted response",
    "citations": [...],
    "confidence_score": 0.85,
    "execution_log": [...],
    "metadata": {...}
}
```

## LangFuse Observability

All nodes are decorated with `@observe` for LangFuse tracing:
- Track execution flow
- Monitor LLM calls
- Debug issues
- Analyze performance

View traces at: `http://localhost:3761`

## Next Steps

1. ✅ Master agent infrastructure complete
2. 📝 Implement sentiment analyzer sub-agent
3. 🔗 Connect sub-agent to master
4. 🎨 Build UI for visualization
5. 🧪 Add comprehensive tests

## File Structure

```
langgraph_master_agent/
├── __init__.py
├── README.md
├── state.py              # State schema
├── config.py             # Configuration
├── graph.py              # Graph definition
├── main.py               # Entry point
├── nodes/
│   ├── conversation_manager.py
│   ├── strategic_planner.py
│   ├── tool_executor.py
│   ├── decision_gate.py
│   └── response_synthesizer.py
└── tools/
    ├── tavily_direct.py
    └── sub_agent_caller.py
```

## Dependencies

See `../requirements.txt` for full dependencies:
- langgraph
- langchain-openai
- httpx
- python-dotenv
- langfuse (optional, for observability)

