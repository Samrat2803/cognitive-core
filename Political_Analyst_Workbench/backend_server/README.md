# Political Analyst Backend Server

FastAPI backend server for the Political Analyst Workbench using LangGraph Master Agent architecture.

## Features

- **🎯 Master Agent Architecture**: Multi-node LangGraph workflow for intelligent analysis
- **🔍 Real-time Web Search**: Tavily API integration for current data
- **📊 Auto Artifact Generation**: Charts, graphs, and visualizations
- **⚡ WebSocket Support**: Real-time streaming updates
- **🔐 Production Ready**: CORS, health checks, error handling
- **📦 Easy Deployment**: AWS Elastic Beanstalk compatible

## Quick Start

### 1. Install Dependencies

```bash
cd backend_server
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required keys:
- `OPENAI_API_KEY`: For LLM inference
- `TAVILY_API_KEY`: For web search

### 3. Run Server

**Development:**
```bash
python app.py
```

**Production:**
```bash
uvicorn application:application --host 0.0.0.0 --port 8000
```

**With Gunicorn:**
```bash
gunicorn application:application -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

### Health Check

```bash
GET /
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "agent_status": "ready",
  "timestamp": "2025-10-01T12:00:00Z"
}
```

### Analysis (POST)

```bash
POST /api/analyze

Request:
{
  "query": "Create a trend chart of India's GDP growth rate over 2020-2025",
  "user_session": "optional_session_id"
}

Response:
{
  "success": true,
  "session_id": "session_123",
  "query": "Create a trend chart...",
  "response": "### India's GDP Growth Rate...",
  "citations": [...],
  "confidence": 0.85,
  "tools_used": ["tavily_search"],
  "iterations": 1,
  "execution_log": [...],
  "artifact": {
    "artifact_id": "line_abc123",
    "type": "line_chart",
    "html_path": "artifacts/line_abc123.html",
    "png_path": "artifacts/line_abc123.png"
  },
  "processing_time_ms": 5230
}
```

### Get Artifact

```bash
GET /api/artifacts/{artifact_id}.html
GET /api/artifacts/{artifact_id}.png
```

### WebSocket (Streaming)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analyze');

// Send query
ws.send(JSON.stringify({
  query: "Analyze climate policy trends"
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'started') {
    console.log('Analysis started');
  } else if (data.type === 'step') {
    console.log('Step:', data.step, data.action);
  } else if (data.type === 'complete') {
    console.log('Result:', data.result);
  }
};
```

## Deployment

### AWS Elastic Beanstalk

1. Initialize EB:
```bash
eb init -p python-3.11 political-analyst
```

2. Create environment:
```bash
eb create political-analyst-prod
```

3. Set environment variables:
```bash
eb setenv OPENAI_API_KEY=xxx TAVILY_API_KEY=xxx
```

4. Deploy:
```bash
eb deploy
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "application:application", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t political-analyst-backend .
docker run -p 8000:8000 --env-file .env political-analyst-backend
```

## Architecture

```
User Request
     ↓
FastAPI Endpoint (/api/analyze)
     ↓
Master Political Analyst
     ↓
┌─────────────────────────────┐
│  LangGraph Workflow         │
├─────────────────────────────┤
│  1. Conversation Manager    │
│  2. Strategic Planner       │
│  3. Tool Executor           │
│     - Tavily Search         │
│     - Tavily Extract        │
│     - Sub-agents (future)   │
│  4. Decision Gate           │
│  5. Response Synthesizer    │
│  6. Artifact Decision       │
│  7. Artifact Creator        │
└─────────────────────────────┘
     ↓
JSON Response + Artifacts
```

## Configuration

See `config_server.py` for all configuration options:

- `DEFAULT_MODEL`: LLM model (default: "gpt-4o-mini")
- `TEMPERATURE`: Always 0 for consistency
- `MAX_QUERY_LENGTH`: Maximum query length (2000 chars)
- `CORS_ORIGINS`: Allowed frontend origins
- `ARTIFACT_DIR`: Where to save generated artifacts

## Error Handling

The server includes comprehensive error handling:

- `400`: Bad request (empty/too long query)
- `404`: Artifact not found
- `500`: Internal server error
- `503`: Service unavailable (agent not initialized)

All errors return:
```json
{
  "detail": "Error message here"
}
```

## Monitoring

### Health Checks

AWS/Load balancers can use `/health` endpoint.

### Logging

All requests and errors are logged to stdout:
```
🚀 Starting Political Analyst Workbench Backend...
✅ Political Analyst Agent initialized successfully
🎯 Backend server ready!
```

### LangSmith Integration

Set `LANGSMITH_API_KEY` to enable tracing and monitoring.

## Testing

Run tests:
```bash
pytest tests/
```

Test specific endpoint:
```bash
pytest tests/test_api.py::test_analyze_endpoint
```

## Performance

- Typical response time: 3-8 seconds
- Artifact generation: +1-2 seconds
- Concurrent requests: Supported via async
- WebSocket connections: Unlimited

## Troubleshooting

**Agent not initializing:**
- Check API keys in .env
- Verify network connectivity
- Check logs for import errors

**Artifacts not found:**
- Ensure `../artifacts/` directory exists
- Check file permissions
- Verify artifact_id in response

**CORS errors:**
- Add frontend URL to `CORS_ORIGINS`
- Restart server after changes

## License

MIT License - See LICENSE file

## Support

For issues or questions, please open a GitHub issue or contact the development team.

