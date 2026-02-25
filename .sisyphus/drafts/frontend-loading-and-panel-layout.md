# Draft: Frontend Loading and Panel Layout

## Requirements (confirmed)
- Loading feedback: During answer generation, frontend should show an obvious in-progress indicator (three-dot loading style) instead of blank area.
- Right-side layout ratio: Increase thinking-process pane height/space and reduce skills pane proportion to 2/3 vs 1/3.

## Technical Decisions
- Frontend stack: Plain `HTML + CSS + JavaScript` (no frontend framework package detected).
- Waiting state insertion point: `frontend/script.js` in `sendMessage()` via `addBotMessage("")` then `updateBotMessage(...)` on stream deltas.
- Right panel layout control: `frontend/style.css` via `.side-column` (`display: flex; flex-direction: column`) with `.process-panel` and `.skills-section` sizing.
- Ratio target interpretation (working assumption): vertical split in right sidebar (process:skills = 2/3:1/3).

## Research Findings
- Message waiting behavior:
  - `frontend/script.js:384` creates empty bot bubble: `const botMessageEl = this.addBotMessage("");`
  - If stream has no delta, fallback only at end: `frontend/script.js:456-458` sets `(空回复)`.
  - Result: waiting phase can appear visually empty.
- Stream lifecycle source:
  - Frontend consumes `/api/chat/stream` in `frontend/script.js:391`.
  - Backend emits `start/delta/process/done/error` events in `main.py:721-821`.
- Right-side structure:
  - DOM sections in `frontend/index.html:65-77` (`process-panel`, `skills-section`).
  - Desktop sizing currently implicit (`.process-panel { flex: 1; }` + `.skills-section { min-height: 210px; }`) at `frontend/style.css:108-116` and `frontend/style.css:207-216`.
  - Mobile uses fixed heights `34vh` vs `26vh` (not 2:1) in `frontend/style.css:551-557`.
- Existing loading-style reuse:
  - Text placeholders exist (`加载中...`) in multiple cards, but no animated dots class currently defined.
  - Existing animation utility is only `@keyframes fadeIn` for message appearance (`frontend/style.css:506-515`).

## Open Questions
- Loading indicator style preference: only animated three dots, or text + animated dots (e.g., “思考中...”)?
- Ratio scope: apply 2/3:1/3 only on desktop, or keep same ratio logic on mobile too?

## Scope Boundaries
- INCLUDE: Waiting-state UI feedback and right-panel proportion adjustment.
- EXCLUDE: Unrelated redesign, data-flow refactors, backend changes.

## Test Strategy Decision
- Infrastructure exists: YES (Python unittest for backend), NO dedicated frontend automated UI test setup.
- Proposed for this UI tweak: Automated tests = NO; verification by agent-executed UI QA scenarios (Playwright/manual scripted browser checks in execution phase).
