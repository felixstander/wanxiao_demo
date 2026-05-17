#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
car_negotiate_server.py

车险谈判中间件 FastAPI 服务。

API:
- POST /api/chat          - 聊天（支持启用/禁用 middleware）
- POST /api/chat/stream   - 流式聊天
- GET  /api/negotiation_state?user_id=xxx  - 查询用户谈判状态（DB 事实）
- GET  /api/strategy?user_id=xxx           - 查询当前策略推荐
- GET  /api/skills        - 技能列表
- GET  /api/health        - 健康检查

前端展示：
- 左侧：谈判状态面板（替代短期/长期记忆）
  - 上半：当前事实（轮次、阶段、价格轨迹、预算、险种等）
  - 下半：策略推荐（局势分析 + 主策略）
"""

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, AsyncIterator

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from car_negotiate_demo import build_car_negotiate_agent
from car_negotiate_middleware import FactStore
from car_negotiate_tools import CAR_NEGOTIATE_TOOLS

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SKILLS_DIR = PROJECT_ROOT / "skills" / "car-negotiate-skills"
DB_PATH = PROJECT_ROOT / "car_negotiate.db"

# 全局 Agent 实例
AGENT_WITH_MW: Any | None = None
AGENT_WITHOUT_MW: Any | None = None
MIDDLEWARE_INSTANCE: Any | None = None


def init_agents():
    """预加载两个 Agent 实例。"""
    global AGENT_WITH_MW, AGENT_WITHOUT_MW, MIDDLEWARE_INSTANCE

    print("=" * 60)
    print("🚀 预加载 Agents...")
    print("=" * 60)

    # 带中间件的 Agent
    print("\n[1/2] 初始化 Agent（启用中间件）...")
    AGENT_WITH_MW, MIDDLEWARE_INSTANCE = build_car_negotiate_agent(
        use_middleware=True, user_id="web-user"
    )
    print("✅ Agent（启用中间件）初始化完成")

    # 不带中间件的 Agent（用于对比）
    print("\n[2/2] 初始化 Agent（禁用中间件）...")
    AGENT_WITHOUT_MW, _ = build_car_negotiate_agent(
        use_middleware=False, user_id="web-user-no-mw"
    )
    print("✅ Agent（禁用中间件）初始化完成")

    print("\n" + "=" * 60)
    print("✅ 所有 Agents 预加载完成！")
    print("=" * 60 + "\n")


def get_agent(use_middleware: bool = True):
    """获取 Agent 实例。"""
    if use_middleware:
        if AGENT_WITH_MW is None:
            raise RuntimeError("Agent（启用中间件）尚未初始化")
        return AGENT_WITH_MW
    else:
        if AGENT_WITHOUT_MW is None:
            raise RuntimeError("Agent（禁用中间件）尚未初始化")
        return AGENT_WITHOUT_MW


def get_middleware():
    """获取中间件实例。"""
    return MIDDLEWARE_INSTANCE


# ── Pydantic Models ────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    history: list[Any] = Field(default_factory=list)
    thread_id: str | None = None
    use_middleware: bool = Field(default=True, description="是否启用中间件")


class StrategyRequest(BaseModel):
    user_id: str = Field(default="web-user")
    current_input: str = Field(default="")


# ── FastAPI App ────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(title="车险谈判中间件演示平台", version="1.0.0")
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    print("🚀 预加载 Agents...")
    init_agents()
    print("✅ Agents 预加载完成\n")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "car-negotiate"}

    @app.get("/api/skills")
    def skills() -> dict[str, Any]:
        """返回可用的 skill 列表。"""
        skill_list = []
        if SKILLS_DIR.exists():
            for skill_dir in sorted(SKILLS_DIR.iterdir()):
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    skill_list.append({
                        "name": skill_dir.name,
                        "path": f"/skills/{skill_dir.name}",
                    })
        return {"skills": skill_list}

    @app.get("/api/negotiation_state")
    def negotiation_state(user_id: str = Query(default="web-user")) -> dict[str, Any]:
        """查询用户在 DB 中的谈判事实。"""
        store = FactStore(str(DB_PATH))
        facts = store.get_facts(user_id)
        return {
            "user_id": user_id,
            "facts": facts,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

    @app.post("/api/strategy")
    def strategy_recommendation(payload: StrategyRequest) -> dict[str, Any]:
        """基于当前事实和输入，生成策略推荐。"""
        middleware = get_middleware()
        if middleware is None:
            return {
                "error": "中间件未初始化",
                "user_id": payload.user_id,
            }

        store = FactStore(str(DB_PATH))
        facts = store.get_facts(payload.user_id)

        # 构建可选策略池
        from car_negotiate_middleware import OPTIONAL_STRATEGIES
        stage = facts.get("stage", "初始")
        stage_module_map = {
            "初始": ["M1", "M2"],
            "质疑": ["M4", "M5", "M7"],
            "调整": ["M3"],
            "谈判": ["M4", "M6", "M7", "M8"],
            "成交": ["M8", "M9", "M10"],
        }
        relevant_modules = stage_module_map.get(stage, ["M1", "M2"])
        all_relevant = set(relevant_modules)
        for m in relevant_modules:
            num = int(m[1:]) if len(m) > 1 and m[1:].isdigit() else 0
            for offset in [-1, 1]:
                neighbor = f"M{num + offset}"
                if any(s["模块"] == neighbor for s in OPTIONAL_STRATEGIES):
                    all_relevant.add(neighbor)
        relevant_strategies = [s for s in OPTIONAL_STRATEGIES if s["模块"] in all_relevant]

        # 调用 LLM 推荐策略
        strategy_result = middleware._recommend_strategy(
            facts, payload.current_input, relevant_strategies
        )

        return {
            "user_id": payload.user_id,
            "facts": facts,
            "strategy": strategy_result,
            "available_strategies": relevant_strategies,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

    @app.post("/api/chat")
    def chat(payload: ChatRequest) -> dict[str, Any]:
        if not payload.message.strip():
            raise HTTPException(status_code=400, detail="message cannot be empty")

        try:
            agent = get_agent(use_middleware=payload.use_middleware)
            resolved_thread_id = payload.thread_id or __import__("uuid").uuid4().hex

            result = agent.invoke(
                {"messages": [{"role": "user", "content": payload.message}]},
                config={"configurable": {"thread_id": resolved_thread_id}},
            )

            # 提取 AI 回复
            ai_text = ""
            for msg in reversed(result.get("messages", [])):
                msg_type = ""
                content = ""
                if isinstance(msg, dict):
                    msg_type = msg.get("type", "") or msg.get("role", "")
                    content = msg.get("content", "")
                else:
                    msg_type = getattr(msg, "type", "")
                    content = getattr(msg, "content", "")
                if msg_type in ("ai", "assistant", "AIMessage"):
                    ai_text = content if isinstance(content, str) else str(content)
                    break

            return {
                "reply": ai_text,
                "thread_id": resolved_thread_id,
                "use_middleware": payload.use_middleware,
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"chat failed: {exc}") from exc

    @app.post("/api/chat/stream")
    async def chat_stream(payload: ChatRequest) -> StreamingResponse:
        if not payload.message.strip():
            raise HTTPException(status_code=400, detail="message cannot be empty")

        async def event_generator() -> AsyncIterator[str]:
            agent = get_agent(use_middleware=payload.use_middleware)
            resolved_thread_id = payload.thread_id or __import__("uuid").uuid4().hex

            yield _to_sse({"event": "start", "thread_id": resolved_thread_id})

            try:
                event_iter = agent.astream_events(
                    {"messages": [{"role": "user", "content": payload.message}]},
                    config={"configurable": {"thread_id": resolved_thread_id}},
                    version="v2",
                )

                async for event in event_iter:
                    kind = str(event.get("event", ""))
                    name = str(event.get("name", ""))
                    data = event.get("data") if isinstance(event.get("data"), dict) else {}

                    if kind == "on_chat_model_stream":
                        chunk = data.get("chunk")
                        delta = _extract_event_chunk_text(chunk)
                        if delta:
                            yield _to_sse({"event": "delta", "text": delta})
                        continue

                    if kind == "on_tool_start":
                        yield _to_sse({"event": "process", "text": f"调用工具: {name}"})
                        continue

                    if kind == "on_tool_end":
                        yield _to_sse({"event": "process", "text": f"工具完成: {name}"})
                        continue

                    if kind == "on_chain_start":
                        if name and name != "agent":
                            yield _to_sse({"event": "process", "text": f"进入阶段: {name}"})
                        continue

            except Exception as exc:
                yield _to_sse({"event": "error", "detail": f"stream failed: {exc}"})

            yield _to_sse({
                "event": "done",
                "reply": "",
                "thread_id": resolved_thread_id,
            })

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.get("/")
    def index() -> HTMLResponse:
        html = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
        version = str(int(__import__("time").time()))
        rendered = html.replace("__ASSET_VERSION__", version)
        return HTMLResponse(rendered)

    return app


def _to_sse(event: dict[str, Any]) -> str:
    payload = json.dumps(event, ensure_ascii=False)
    return f"data: {payload}\n\n"


def _extract_event_chunk_text(chunk: Any) -> str:
    if chunk is None:
        return ""
    if hasattr(chunk, "content"):
        content = getattr(chunk, "content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str):
                        parts.append(text)
                elif isinstance(item, str):
                    parts.append(item)
            return "".join(parts)
        return str(content)
    if isinstance(chunk, dict) and "content" in chunk:
        return str(chunk.get("content", ""))
    return str(chunk)


app: FastAPI | None = None
if __name__ != "__main__":
    app = create_app()


def main():
    port = int(os.getenv("PORT", "8006"))
    local_app = create_app()
    uvicorn.run(local_app, host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
