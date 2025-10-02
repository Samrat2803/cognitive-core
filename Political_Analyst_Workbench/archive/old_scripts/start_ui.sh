#!/bin/bash

# Political Analyst Workbench - UI Startup Script

echo "🏛️  Starting Political Analyst Workbench UI..."
echo "=" * 50

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

echo "🚀 Starting Streamlit UI..."
echo "📱 The UI will open in your browser at http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start Streamlit
streamlit run realtime_ui.py --server.port 8501 --server.address localhost
