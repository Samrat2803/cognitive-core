#!/bin/bash

# Political Analyst Workbench - Phoenix Real-time Observability UI

echo "🔥 Starting Phoenix Real-time Observability for Political Analyst Workbench"
echo "=========================================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy env.example to .env and add your API keys"
    exit 1
fi

# Install Phoenix if not available
echo "📦 Checking Phoenix installation..."
python -c "import phoenix" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Phoenix (Arize AI)..."
    pip install arize-phoenix
fi

echo "🚀 Starting Phoenix Observable Agent..."
echo "🔥 Phoenix UI will launch at: http://localhost:6006"
echo "📊 Real-time traces will appear as the agent runs"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run the Phoenix observable agent
python phoenix_observability.py

