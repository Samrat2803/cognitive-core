# Cognitive Core - 2-MVP Implementation Plan

Version: 2.0  
Status: Approved for Implementation  
Timebox: 2 weeks

## Objectives
- Transform chat into a true streaming experience (tokens over WebSocket).  
- Adopt a polished ChatGPT/Perplexity-like UI surface.  
- Add a branded homepage (“Cognitive Core”) with navigation to Chat/Results.  
- Introduce inline citations and a right-pane sources panel.  
- Maintain MVP simplicity (no auth, no Celery) and keep existing URLs.

## Scope (2-MVP)
- Backend: WebSocket token streaming protocol; completion with citations; optional non-stream fallback.
- Frontend: Streaming chat UI, citations UI, homepage, keyboard UX, responsive design.
- Tests: WS streaming smoke, citations rendering, homepage → chat flow, mobile layout.

## Deliverables
1) Streaming Chat surface with token-by-token rendering.  
2) Citation bar and side panel for sources.  
3) Homepage at `/` branded “Cognitive Core”.  
4) Documentation updates (API contracts section 2-MVP addendum).  

## Backend Work
### Changes
- `backend/app.py`: extend `/ws/{session_id}` to stream tokens and final frame.
- `backend/core/poc_integration_service.py`: produce token chunks (simulate by chunking sentences/words if needed); attach citations on final.
- `backend/models/analysis_models.py`: add `Citation` model (`id, url, title, domain, credibility, published_at`).
- Add tests: `tests/api/test_streaming_ws.py`, `tests/api/test_citations.py`.

### Streaming Protocol
- Token frame: `{ "type":"token", "content":"...", "index": n }`
- Heartbeat: `{ "type":"ping", "timestamp": ISO8601 }` every 30s; client responds `{ "type":"pong" }`
- Completion: `{ "type":"complete", "analysis_id":"...", "citations":[...], "usage": {"tokens": N} }`
- Error: `{ "type":"analysis_error", "error": {"code":"...","message":"...","recoverable":true} }`

### Acceptance
- First token < 600ms; smooth flow; final < 100ms after backend completes.  
- Completion includes 1+ citations for any non-empty result.  

## Frontend Work
### Changes
- Add `pages/Home.tsx`, `pages/Chat.tsx`; route `/` → Home, `/chat` → Chat.
- Add `components/chat2/*` (adopt from Chatbot UI style or similar) with streaming token rendering.
- Update `hooks/useWebSocket.ts` to accumulate token frames; handle `complete` and `error`.
- Add citations bar (inline numbered links) and `components/results/SourcesPanel.tsx`.
- Keyboard UX: Enter send, Shift+Enter newline; Cmd/Ctrl+K omnibar (Phase 2 optional if time remains).

### Acceptance
- Streaming UX: tokens display incrementally without layout jank.  
- Citations open side panel; clickable; keyboard accessible.  
- Homepage routes to chat via CTA and prompt chips.  

## Tests
- Playwright: `tests/e2e/streaming.spec.ts` (send message → see tokens), `tests/e2e/citations.spec.ts` (open/close panel), `tests/e2e/home-to-chat.spec.ts` (CTA flows), `tests/e2e/mobile-layout.spec.ts` (responsive snapshots).
- Backend: WS unit/integration tests for ping/pong, token frames, completion, error path.

## Timeline
- Week 1: Backend WS tokens + citations; Frontend streaming UI + homepage scaffold.  
- Week 2: Citations UI, keyboard UX, polish, tests.

## Risks & Mitigations
- WS instability → exponential backoff, heartbeat, fall back to non-stream on error.  
- Styling drift → adopt components wholesale first, then theme via CSS variables.  
- Performance → throttle appends, batch render with rAF.

## Non-Goals (2-MVP)
- Authentication, Celery/queues, exports engine changes.

## Handover
- Update API_CONTRACTS.md addendum with streaming message types and citations schema.  
- Update TEAM_STATUS_TRACKING.md with 2-MVP tasks and DoD.

