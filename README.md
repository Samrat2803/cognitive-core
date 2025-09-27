# Web Research Agent

A sophisticated web research agent built with LangGraph and Tavily, featuring a React TypeScript frontend and Python FastAPI backend.

## Project Structure

```
test_agents/
├── frontend/          # React TypeScript frontend
├── backend/           # Python FastAPI backend
│   ├── .env          # Environment variables (create this file)
│   ├── app.py        # FastAPI server
│   ├── research_agent.py
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   cp env.example .env
   ```

5. **Edit .env file with your API keys:**
   ```
   TAVILY_API_KEY=your_tavily_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   # Optional: ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

6. **Run the backend server:**
   ```bash
   python app.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   
   The frontend will be available at `http://localhost:3000`

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /research` - Perform web research
- `GET /config` - Get configuration info

## Environment Variables

Place your `.env` file in the **backend** folder with the following variables:

- `TAVILY_API_KEY` - Your Tavily API key (required)
- `OPENAI_API_KEY` - Your OpenAI API key (required for OpenAI models)
- `ANTHROPIC_API_KEY` - Your Anthropic API key (optional, for Claude models)

## Usage

1. Start the backend server first
2. Start the frontend development server
3. Open your browser to `http://localhost:3000`
4. Enter your research query and get comprehensive results
