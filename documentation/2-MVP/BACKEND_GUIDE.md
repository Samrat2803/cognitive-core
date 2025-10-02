# Backend Guide - 2-MVP (Streaming & Citations)

Version: 2.0  
Status: Ready for Implementation  
Owner: Backend Lead

## Goals
- Add true token streaming over WebSocket to feel like a live chatbot
- Include citations in final completion frame for Perplexity-like UX
- Keep MVP simplicity: no auth, no Celery/queues, no exports changes

## Scope
- Extend existing `/ws/{session_id}` to emit token frames and a final completion frame
- Simulate tokenization if underlying POC returns a whole response (chunk by words/sentences)
- Add `Citation` schema and include citations in completion
- Maintain existing REST endpoints; add optional `?stream=false` non-stream fallback if needed for tests

## Protocol (2-MVP)
- Token frame:
```json
{ "type": "token", "content": "partial text", "index": 0 }
```
- Heartbeat (every 30s):
```json
{ "type": "ping", "timestamp": "2025-09-28T12:00:00Z" }
```
- Client shall respond with:
```json
{ "type": "pong" }
```
- Completion frame:
```json
{
  "type": "complete",
  "analysis_id": "analysis_123",
  "citations": [
    { "id": "c1", "url": "https://...", "title": "...", "domain": "example.com", "credibility": 0.82, "published_at": "2025-09-01" }
  ],
  "usage": { "tokens": 512 }
}
```
- Error frame:
```json
{
  "type": "analysis_error",
  "analysis_id": "analysis_123",
  "error": { "code": "EXTERNAL_API_FAILURE", "message": "...", "recoverable": true }
}
```

## File Changes
- `backend/app.py`
  - Extend `/ws/{session_id}`: accept connection, handle ping/pong, forward token frames from service, send completion/error
- `backend/core/poc_integration_service.py`
  - Implement `async stream_analysis(params, session_id)` that yields token frames (chunked) and a final completion
  - Add minimal citation extraction/normalization (from existing sources list)
- `backend/models/analysis_models.py`
  - Add `Citation` Pydantic model: `{ id: str, url: str, title: str, domain: str, credibility: float, published_at: str|null }`
- `backend/tests/api/test_streaming_ws.py`
  - Connect WS, send a trigger, assert receipt of token frames, heartbeat, and completion
- `backend/tests/api/test_citations.py`
  - Assert completion frame includes normalized citations array

## Step-by-step
1) WS plumbing in `app.py`
   - Accept, register session, start a background task that iterates over `stream_analysis`
   - Relay frames to the specific session
2) Service streaming in `poc_integration_service.py`
   - Run existing analysis (or staged steps) and incrementally yield tokens (split on whitespace or sentence boundaries)
   - Collect citations from POC results and normalize (url, title, domain)
   - Yield completion with `citations` and `usage`
3) Models
   - Add `Citation` model to `analysis_models.py`
4) Tests
   - WS token streaming: expect first token within reasonable time
   - Completion contains `citations`

## Commands
```bash
# Backend dev
cd backend
source .venv/bin/activate
pytest tests/api/test_streaming_ws.py -q
pytest tests/api/test_citations.py -q
```

## Acceptance Criteria
- First token visible < 600ms from stream start (local)
- Smooth token delivery (no buffer dump at end)
- Completion includes >= 1 citation when sources exist
- Heartbeat every 30s; client ping/pong path verified in test

## Notes
- Keep `/research` unchanged for backward compatibility
- Keep existing URLs/WSS and environment setup as in 1-MVP
