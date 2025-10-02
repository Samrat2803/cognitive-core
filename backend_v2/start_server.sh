#!/bin/bash

# Startup script for Political Analyst Backend Server
# Usage: ./start_server.sh [development|production]

MODE=${1:-development}

echo "========================================"
echo "🚀 Political Analyst Backend Server"
echo "========================================"
echo "Mode: $MODE"
echo ""

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "⚠️  Warning: ../.env file not found"
    echo "   Copy .env.example to .env and configure API keys"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "../.venv_studio" ]; then
    echo "📦 Activating virtual environment..."
    source ../.venv_studio/bin/activate
elif [ -d "../.venv" ]; then
    echo "📦 Activating virtual environment..."
    source ../.venv/bin/activate
fi

# Check required packages
echo "🔍 Checking dependencies..."
python -c "import fastapi, uvicorn, langgraph" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

echo ""
echo "========================================"

if [ "$MODE" = "production" ]; then
    echo "🎯 Starting in PRODUCTION mode..."
    echo "   Using Gunicorn with 4 workers"
    echo "========================================"
    gunicorn application:application \
        -w 4 \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --timeout 120 \
        --log-level info
else
    echo "🔧 Starting in DEVELOPMENT mode..."
    echo "   Hot reload enabled"
    echo "   Access at: http://localhost:8000"
    echo "   Docs at: http://localhost:8000/docs"
    echo "========================================"
    python app.py
fi

