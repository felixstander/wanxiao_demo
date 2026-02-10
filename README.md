#TODO:

1.skills还是没加载成功 
2.前端展示无回复，还是没有解决

# DeepAgents + OpenRouter + Vanilla Frontend Demo

## Features

- Uses LangChain DeepAgents (`create_deep_agent`) as the core agent runtime.
- Uses OpenRouter model via `langchain-openai` (`z-ai/glm-4.5-flash` by default).
- Loads skill files from `~/.deepagents/agent/skills` and mounts them into `/skills/*`.
- Uses local filesystem backend and stores memory in project `memories/` directory.
- Frontend framework replaced to vanilla `HTML + CSS + JavaScript` (based on target article style).
- Backend serves static frontend with FastAPI and exposes `/api/chat` for real agent calls.
- Frontend consumes `/api/chat/stream` for streaming model output.
- UI includes a right-side `思考过程` panel showing step events and tool-call/process traces from LangGraph stream events.

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Create env file:

```bash
cp .env.example .env
```

3. Fill in `.env`:

```env
OPENROUTER_API_KEY="your-openrouter-key"
OPENROUTER_MODEL="z-ai/glm-4.5-flash"
```

## Run

```bash
uv run python main.py
```

Open `http://localhost:7860` in your browser.

By default, auto-reload is enabled (code change -> process reload).

If you want to disable auto-reload:

```bash
AUTO_RELOAD=0 uv run python main.py
```

## Test

```bash
uv run python -m unittest tests/test_main.py
```

## Frontend Structure

```text
frontend/
├── index.html
├── style.css
└── script.js
```

- `index.html`: chat page structure (header/messages/suggested questions/input)
- `style.css`: modern chat layout + animation + responsive styles
- `script.js`: native DOM chat logic + `/api/chat` integration

## Skill Directory

The app reads all text files recursively under:

`~/.deepagents/agent/skills`

Each file is exposed to DeepAgents as a virtual file under `/skills/...` so the agent can load relevant skills on demand.

## Memory Directory (Two-layer Memory)

Memory is stored in local markdown files under project root:

```text
memories/
├── MEMORY.md
└── daily/
    └── YYYY-MM-DD.md
```

- `memories/daily/YYYY-MM-DD.md`: short-term daily logs (append-only event notes).
- `memories/MEMORY.md`: long-term curated memory (preferences, key decisions, contacts, project facts).

The agent system prompt instructs it to:

1. Read long-term memory and recent daily logs at session start.
2. Write short-term facts to daily log with `## HH:MM - title` format.
3. Promote stable cross-day knowledge into `MEMORY.md` with deduplication.
