#!/bin/bash

# Political Analyst Workbench - Real-time Streaming UI Startup Script

echo "🏛️  Starting Political Analyst Workbench - Real-time Streaming UI..."
echo "=================================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy env.example to .env and add your API keys:"
    echo "  cp env.example .env"
    echo "  # Then edit .env with your TAVILY_API_KEY and OPENAI_API_KEY"
    exit 1
fi

# Check if required packages are installed
echo "🔧 Checking dependencies..."
python -c "import streamlit, langchain_community, tavily" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip install -r requirements.txt
fi

echo "🚀 Starting Real-time Streaming UI..."
echo "📱 The UI will open in your browser at http://localhost:8502"
echo "🔴 LIVE UPDATES: Watch agent reasoning in real-time!"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start Streamlit with real-time streaming UI
streamlit run realtime_streaming_ui.py --server.port 8502 --server.address localhost

