# API Contracts - 2-MVP Addendum (Streaming & Citations)

## WebSocket Streaming (Production: wss://)
- Path: `/ws/{session_id}`
- Frames:
```json
{ "type": "token", "content": "...", "index": 0 }
{ "type": "ping", "timestamp": "ISO8601" }
{ "type": "pong" }
{ "type": "complete", "analysis_id": "...", "citations": [ { "id": "c1", "url": "...", "title": "...", "domain": "...", "credibility": 0.8, "published_at": "2025-09-01" } ], "usage": { "tokens": 512 } }
{ "type": "analysis_error", "analysis_id": "...", "error": { "code": "...", "message": "...", "recoverable": true } }
```

## Citation Schema
```json
{ "id": "string", "url": "string", "title": "string", "domain": "string", "credibility": 0.0, "published_at": "string|null" }
```

## Non-stream Fallback (Optional)
- `POST /api/analysis/execute?stream=false` returns full text and citations in one payload for tests.

## Acceptance
- Token frames begin within 600ms; completion includes citations when sources exist.
