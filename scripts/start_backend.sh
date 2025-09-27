#!/bin/bash

# Start Backend Server
echo "🚀 Starting Web Research Agent Backend..."

cd backend

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "TAVILY_API_KEY=your_tavily_api_key_here"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    echo ""
    echo "Copy env.example to .env and fill in your keys:"
    echo "cp env.example .env"
    exit 1
fi

# Start the server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API documentation available at http://localhost:8000/docs"
echo ""
python app.py
