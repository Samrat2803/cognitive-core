# Frontend Guide - 2-MVP (Streaming Chat UI & Homepage)

Version: 2.0  
Status: Ready for Implementation  
Owner: Frontend Lead

## Goals
- Provide ChatGPT/Perplexity-like streaming chat experience
- Add "Cognitive Core" homepage and navigation
- Show inline citations and a right-side sources panel

## Scope
- Streaming tokens over WebSocket; accumulate and render incrementally
- Inline citation superscripts (e.g., [1], [2]) and Sources panel
- Homepage with CTA, prompt chips, and route to /chat

## Tasks
1) Routing & Pages
   - Add `src/pages/Home.tsx` with hero, CTA "Start Analysis", prompt chips
   - Add `src/pages/Chat.tsx` hosting the new chat surface
   - Wire routes (keep existing AnalysisResults page)
2) Chat UI
   - Create `src/components/chat2/MessageList.tsx`, `MessageBubble.tsx`, `ChatInput.tsx`
   - Token rendering: append as `{type:'token'}` frames arrive; finalize on `{type:'complete'}`
   - Loading skeletons; aria-live region for streaming text
3) Citations
   - Inline superscripts linked to `SourcesPanel` (right drawer)
   - `src/components/results/SourcesPanel.tsx` with list of normalized citations
4) WebSocket Hook
   - Extend `hooks/useWebSocket.ts` to handle token accumulation, ping/pong, errors, completion
   - Reconnect with exponential backoff; `wss://` in production
5) Keyboard UX
   - Enter send; Shift+Enter newline; focus management for accessibility

## File Changes
- `src/pages/Home.tsx`, `src/pages/Chat.tsx`
- `src/components/chat2/*` (new chat components)
- `src/components/results/SourcesPanel.tsx`
- `src/hooks/useWebSocket.ts` (streaming support)
- `src/App.tsx` or router file (routes)

## Commands
```bash
cd frontend
npm install
npm start
```

## Acceptance Criteria
- First token visible < 600ms; continuous streaming without layout jank
- Citations open/close via keyboard and mouse; links open in new tab
- Homepage CTA navigates to /chat and pre-fills selected prompt chip
- Mobile layout responsive (≥ 375px width)

## Notes
- Keep environment-driven API/WS URLs per 1-MVP config
- Use existing color palette and typography (Linear/GitHub-inspired)
