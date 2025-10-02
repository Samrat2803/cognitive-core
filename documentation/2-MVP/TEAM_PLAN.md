# Team Plan - 2-MVP (Streaming, UI, Homepage)

## Cross-Team Objectives
- Ship streaming chat, citations, and homepage in 2 weeks
- Maintain 1-MVP infra and URLs

## Backend Tasks
- WS token frames & completion (with citations)
- Citation model + normalization
- Tests: streaming, completion, error frames

## Frontend Tasks
- Integrate streaming chat surface
- Inline citations + SourcesPanel
- Homepage + routing + prompt chips
- Streaming hook: ping/pong, reconnect

## Acceptance Criteria (Shared)
- First token < 600ms; smooth stream
- Completion contains citations; UI shows sources panel
- Homepage CTA to /chat works; mobile layout OK

## Timeline
- Week 1: WS tokens/citations + chat streaming + homepage
- Week 2: Citations UI polish, keyboard UX, tests, visual pass

## Risks
- WS stability → heartbeat/reconnect
- Styling drift → adopt components wholesale first
- Performance → throttle renders
