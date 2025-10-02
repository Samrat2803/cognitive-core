# Political Analyst Workbench

A sophisticated AI agent powered by **LangGraph** and **Tavily** for comprehensive political analysis and research.

## Features

- 🤖 **LangGraph Agent**: Intelligent workflow management with conditional tool usage
- 🔍 **Tavily Integration**: Real-time web search and information gathering with enhanced documentation
- 🏛️ **Political Analysis**: Specialized for political research, policy analysis, and current events
- 💬 **Interactive Interface**: Command-line chat interface for natural conversations
- 🔴 **Live Streaming UI**: Real-time Streamlit interface with live agent reasoning updates
- 🎨 **Enhanced Real-time UI**: Beautiful web interface showing agent working step-by-step
- 🧠 **Reasoning Transparency**: Full visibility into agent decision-making process with progress tracking
- 🔧 **Async Processing**: Efficient handling of multiple API calls

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp env.example .env
```

Edit `.env` file:
```
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Agent

**🔴 Real-time Streaming UI (Recommended):**
```bash
./start_realtime_ui.sh
# Or manually: streamlit run realtime_streaming_ui.py --server.port 8502
```

**🎨 Basic Real-time UI:**
```bash
./start_ui.sh
# Or manually: streamlit run realtime_ui.py
```

**💬 Interactive CLI Mode:**
```bash
python main.py
```

**⚡ Single Query Mode:**
```bash
python main.py "What are the latest developments in US foreign policy?"
```

**🧪 Simple Test Agent:**
```bash
python simple_agent.py
```

## Usage Examples

### Political Research Queries
- "What is the current status of the Ukraine conflict?"
- "Analyze the latest polling data for the 2024 US presidential election"
- "What are the key policy differences between major political parties on climate change?"

### Current Events Analysis
- "What happened in today's UN Security Council meeting?"
- "Summarize the latest developments in Middle East diplomacy"
- "What are the economic implications of recent trade policy changes?"

### Policy Research
- "Compare healthcare policies across different countries"
- "What are the main arguments for and against carbon taxation?"
- "Analyze the effectiveness of recent immigration reforms"

## Architecture

### Core Components

1. **PoliticalAnalystAgent**: Main agent class that orchestrates the workflow
2. **LangGraph Workflow**: 
   - **Agent Node**: Processes queries with GPT-4o-mini
   - **Tools Node**: Executes Tavily searches when needed
   - **Conditional Logic**: Determines when to use tools vs. provide direct responses

3. **Tavily Integration**: 
   - Advanced search depth for comprehensive results
   - Real-time web information retrieval
   - Structured data extraction

### Workflow

```
User Query → Agent Node → [Tool Usage?] → Tavily Search → Agent Node → Response
```

## Configuration

### LLM Settings
- **Model**: GPT-4o-mini (cost-effective, high performance)
- **Temperature**: 0 (deterministic responses)
- **Tool Binding**: Automatic tool selection based on query needs

### Tavily Settings
- **Max Results**: 10 per search
- **Search Depth**: Advanced (comprehensive coverage)
- **Include Answer**: Yes (direct answers when available)
- **Content Type**: Text only (no images/raw content)

## Package Requirements

```
langgraph          # Workflow orchestration
langchain_openai   # OpenAI integration
langchain_community # Community tools (Tavily)
tavily-python      # Tavily search API
python-dotenv      # Environment variable management
```

## API Keys Required

1. **Tavily API Key**: Get from [tavily.com](https://tavily.com)
2. **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com)

## Development

### Project Structure
```
Political_Analyst_Workbench/
├── political_agent.py         # Enhanced LangGraph agent implementation
├── simple_agent.py            # Simple working agent for testing
├── streaming_agent.py         # Real-time streaming agent with live updates
├── main.py                    # Interactive CLI runner
├── realtime_ui.py             # Basic Streamlit real-time UI
├── realtime_streaming_ui.py   # Advanced streaming UI with live updates
├── start_ui.sh               # Basic UI startup script
├── start_realtime_ui.sh      # Real-time streaming UI startup script
├── requirements.txt           # Package dependencies
├── env.example               # Environment template
├── AGENT_ARCHITECTURE.md      # Detailed agent documentation
└── README.md                 # This file
```

### Extending the Agent

To add new tools or capabilities:

1. **Add New Tools**: Import and initialize additional LangChain tools
2. **Update Tool Binding**: Add tools to the `self.tools` list
3. **Modify Workflow**: Extend the LangGraph workflow as needed

### Error Handling

The agent includes comprehensive error handling for:
- Missing API keys
- Network connectivity issues
- Tool execution failures
- Invalid user inputs

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure `.env` file exists with valid keys
2. **Import Errors**: Run `uv pip install -r requirements.txt`
3. **Network Issues**: Check internet connectivity for Tavily searches
4. **Rate Limits**: Tavily and OpenAI have usage limits - check your quotas

### Debug Mode

For detailed logging, modify the agent initialization:
```python
agent = PoliticalAnalystAgent()
# Add logging configuration as needed
```

## License

This project is part of the Tavily Agent experimental framework.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This is a basic configuration. For production use, consider adding:
- Conversation memory/history
- Advanced error recovery
- Custom tool implementations
- Performance monitoring
- Security enhancements
