#!/bin/bash

# Setup script for API keys
echo "🔧 Setting up API keys for Web Research Agent"
echo "============================================="

ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating .env file from template..."
    cp backend/env.example .env
    echo "✅ .env file created"
else
    echo "📋 .env file already exists"
fi

echo ""
echo "ℹ️  To enable full functionality, you need to add your API keys to the .env file:"
echo ""
echo "1. Get a Tavily API key from: https://tavily.com/"
echo "2. Get an OpenAI API key from: https://platform.openai.com/api-keys"
echo "3. Edit .env file and replace the placeholder values:"
echo ""
echo "   TAVILY_API_KEY=your_actual_tavily_api_key_here"
echo "   OPENAI_API_KEY=your_actual_openai_api_key_here"
echo ""
echo "⚠️  Without API keys, the research functionality will show errors,"
echo "   but the UI tests will still pass to validate the interface."
echo ""
echo "🚀 After setting up keys, restart the backend server:"
echo "   ./scripts/start_backend.sh"
