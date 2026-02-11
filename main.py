import json
import os
import shutil
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Any, AsyncIterator, Iterator

import uvicorn
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MEMORIES_DIR = PROJECT_ROOT / "memories"
DAILY_DIR = MEMORIES_DIR / "daily"
LONG_TERM_FILE = MEMORIES_DIR / "MEMORY.md"

load_dotenv()

model_name = os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.7-flash")


def _ensure_memory_files(today: date) -> tuple[str, str]:
    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    today_name = today.strftime("%Y-%m-%d")
    today_file = DAILY_DIR / f"{today_name}.md"

    if not LONG_TERM_FILE.exists():
        LONG_TERM_FILE.write_text(
            "# 长期记忆\n\n"
            "## 用户偏好\n"
            "- 暂无\n\n"
            "## 重要决策\n"
            "- 暂无\n\n"
            "## 关键联系人\n"
            "- 暂无\n\n"
            "## 项目事实\n"
            "- 暂无\n",
            encoding="utf-8",
        )

    if not today_file.exists():
        today_file.write_text(
            f"# {today_name}\n\n"
            "## 09:00 - 会话初始化\n"
            "- 新的一天开始，按需记录重要事实、决策、偏好与待办。\n",
            encoding="utf-8",
        )

    return "/memories/MEMORY.md", f"/memories/daily/{today_name}.md"


def build_agent() -> Any:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Please set it in .env")

    os.environ["OPENAI_API_KEY"] = api_key

    llm = ChatOpenAI(
        model=model_name,
        base_url="https://openrouter.ai/api/v1",
        # temperature=0.2,
    )

    skills_dir = PROJECT_ROOT / "skills"
    today = date.today()
    yesterday = today - timedelta(days=1)
    long_term_path, today_path = _ensure_memory_files(today)
    yesterday_path = f"/memories/daily/{yesterday.strftime('%Y-%m-%d')}.md"

    system_prompt = (
        "你是一个通用 DeepAgent。你需要使用双层记忆系统，并把记忆写入本地 Markdown 文件。\n\n"
        "记忆目录结构：\n"
        "- 长期记忆：/memories/MEMORY.md\n"
        "- 每日日志：/memories/daily/YYYY-MM-DD.md\n\n"
        # "每次新会话开始时请先主动回忆：\n"
        # f"1) read_file {long_term_path}\n"
        # f"2) read_file {today_path}\n"
        f"3) 如果存在，再 read_file {yesterday_path}\n\n"
        "写入规范（参考双层记忆）：\n"
        "A. 每日日志（短期记忆）\n"
        "- 仅追加写入到当天文件 /memories/daily/YYYY-MM-DD.md。\n"
        "- 使用格式：\n"
        "  ## HH:MM - 事件标题\n"
        "  - 事实/结论1\n"
        "  - 事实/结论2\n"
        "- 适合记录：会话过程、临时上下文、待办进展、当天细节。\n\n"
        "B. 长期记忆\n"
        "- 维护 /memories/MEMORY.md 的结构化内容，优先保持以下章节：\n"
        "  ## 用户偏好\n"
        "  ## 重要决策\n"
        "  ## 关键联系人\n"
        "  ## 项目事实\n"
        "- 适合记录：跨天仍有效的信息（稳定偏好、关键决策、固定事实）。\n"
        "- 写入时去重、合并相同信息，避免重复条目。\n\n"
        "执行原则：\n"
        "- 当用户明确说‘记住这个’或出现重要信息时，优先写每日日志，并在必要时同步更新长期记忆。\n"
        "- 如果信息不确定，请标注‘待确认’，不要把猜测写成事实。\n"
        "- 回答用户问题时可结合记忆文件，但输出给用户时保持简洁准确。\n"
    )

    agent = create_deep_agent(
        model=llm,
        backend=FilesystemBackend(root_dir=str(PROJECT_ROOT), virtual_mode=True),
        skills=[str(skills_dir)],
        memory=[long_term_path, today_path],
        system_prompt=system_prompt,
    )
    return agent


def _sync_skills_to_project(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    if not source_dir.exists():
        return

    for root, dirs, files in os.walk(source_dir):
        rel_root = Path(root).relative_to(source_dir)

        dirs[:] = [d for d in dirs if d != "__pycache__"]
        if any(part == "__pycache__" for part in rel_root.parts):
            continue

        for file_name in files:
            src = Path(root) / file_name
            if src.suffix == ".pyc":
                continue

            dst = target_dir / rel_root / file_name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def _list_skill_packages(skills_dir: Path) -> list[dict[str, str]]:
    if not skills_dir.exists():
        return []

    seen: set[str] = set()
    packages: list[dict[str, str]] = []
    for skill_file in skills_dir.rglob("SKILL.md"):
        parent_dir = skill_file.parent
        try:
            rel = parent_dir.relative_to(skills_dir).as_posix()
        except ValueError:
            continue

        if rel in seen:
            continue

        seen.add(rel)
        packages.append({"name": parent_dir.name, "path": f"/skills/{rel}"})

    packages.sort(key=lambda item: (item["name"], item["path"]))
    return packages


def _frontend_asset_version() -> str:
    candidates = [
        FRONTEND_DIR / "index.html",
        FRONTEND_DIR / "style.css",
        FRONTEND_DIR / "script.js",
    ]
    latest_mtime = 0.0
    for path in candidates:
        if path.exists():
            latest_mtime = max(latest_mtime, path.stat().st_mtime)

    return str(int(latest_mtime)) if latest_mtime else "1"


def _latest_daily_memory_files(limit: int = 2) -> list[Path]:
    if not DAILY_DIR.exists():
        return []

    files = [p for p in DAILY_DIR.glob("*.md") if p.is_file()]
    files.sort(key=lambda p: p.name, reverse=True)
    return files[:limit]


def _read_text_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _memories_payload() -> dict[str, Any]:
    today = date.today()
    _ensure_memory_files(today)

    short_files = _latest_daily_memory_files(limit=2)
    short_term: list[dict[str, str]] = []
    max_mtime = LONG_TERM_FILE.stat().st_mtime if LONG_TERM_FILE.exists() else 0.0

    for file_path in short_files:
        short_term.append(
            {
                "date": file_path.stem,
                "path": f"/memories/daily/{file_path.name}",
                "content": _read_text_file(file_path),
            }
        )
        max_mtime = max(max_mtime, file_path.stat().st_mtime)

    long_term_content = _read_text_file(LONG_TERM_FILE)
    if LONG_TERM_FILE.exists():
        max_mtime = max(max_mtime, LONG_TERM_FILE.stat().st_mtime)

    return {
        "version": str(int(max_mtime)) if max_mtime else "1",
        "short_term": short_term,
        "long_term": {
            "path": "/memories/MEMORY.md",
            "content": long_term_content,
        },
    }


AGENT: Any | None = None


def get_agent() -> Any:
    global AGENT
    if AGENT is None:
        AGENT = build_agent()
    return AGENT


def _to_deepagent_messages(history: list[Any], user_text: str) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for item in history:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content", "")
            if role in {"user", "assistant"}:
                messages.append({"role": role, "content": str(content)})
            continue

        if isinstance(item, (list, tuple)) and len(item) == 2:
            user_msg, assistant_msg = item
            if user_msg:
                messages.append({"role": "user", "content": str(user_msg)})
            if assistant_msg:
                messages.append({"role": "assistant", "content": str(assistant_msg)})

    messages.append({"role": "user", "content": user_text})
    return messages


def chat_with_agent(
    message: str, history: list[Any], thread_id: str | None
) -> tuple[str, str, list[dict[str, str]]]:
    resolved_thread_id = thread_id or str(uuid.uuid4())
    normalized_messages = _to_deepagent_messages(history, message)

    result = get_agent().invoke(
        {"messages": normalized_messages},
        config={"configurable": {"thread_id": resolved_thread_id}},
    )

    assistant_text = ""
    for msg in reversed(result.get("messages", [])):
        if _get_msg_type(msg) == "ai":
            assistant_text = _message_content_to_text(_get_msg_content(msg))
            break

    updated_history = list(normalized_messages)
    updated_history.append({"role": "assistant", "content": assistant_text})
    return assistant_text, resolved_thread_id, updated_history


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
            elif hasattr(item, "text"):
                text = getattr(item, "text", "")
                if isinstance(text, str):
                    parts.append(text)
            elif hasattr(item, "content"):
                text = getattr(item, "content", "")
                if isinstance(text, str):
                    parts.append(text)
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts)

    return ""


def _get_msg_type(msg: Any) -> str:
    if isinstance(msg, dict):
        return str(msg.get("type", ""))
    return str(getattr(msg, "type", ""))


def _get_msg_content(msg: Any) -> Any:
    if isinstance(msg, dict):
        return msg.get("content", "")
    return getattr(msg, "content", "")


def _get_tool_calls(msg: Any) -> list[Any]:
    if isinstance(msg, dict):
        tool_calls = msg.get("tool_calls")
        return tool_calls if isinstance(tool_calls, list) else []
    tool_calls = getattr(msg, "tool_calls", None)
    return tool_calls if isinstance(tool_calls, list) else []


def _extract_ai_text_from_updates(update_chunk: Any) -> str:
    data = update_chunk
    if (
        isinstance(update_chunk, (tuple, list))
        and len(update_chunk) == 2
        and isinstance(update_chunk[1], dict)
    ):
        data = update_chunk[1]

    if not isinstance(data, dict):
        return ""

    candidates: list[str] = []
    for node_update in data.values():
        if not isinstance(node_update, dict):
            continue
        messages = node_update.get("messages")
        if not isinstance(messages, list):
            continue
        for msg in messages:
            if _get_msg_type(msg) == "ai":
                text = _message_content_to_text(_get_msg_content(msg))
                if text:
                    candidates.append(text)

    return candidates[-1] if candidates else ""


def _extract_ai_text_from_output(output: Any) -> str:
    if not isinstance(output, dict):
        return ""

    messages = output.get("messages")
    if not isinstance(messages, list):
        return ""

    for msg in reversed(messages):
        if _get_msg_type(msg) == "ai":
            text = _message_content_to_text(_get_msg_content(msg))
            if text:
                return text
    return ""


def _extract_event_chunk_text(chunk: Any) -> str:
    if chunk is None:
        return ""

    if hasattr(chunk, "content"):
        return _message_content_to_text(getattr(chunk, "content"))

    if isinstance(chunk, dict) and "content" in chunk:
        return _message_content_to_text(chunk.get("content"))

    return _message_content_to_text(chunk)


def _preview_output(value: Any, limit: int = 120) -> str:
    text = _message_content_to_text(value)
    if not text:
        text = str(value)
    text = text.replace("\n", " ").strip()
    if len(text) > limit:
        return f"{text[:limit]}..."
    return text


def _extract_stream_text(chunk: Any) -> str:
    candidate = chunk
    if isinstance(chunk, (tuple, list)) and chunk:
        candidate = chunk[0]

    if hasattr(candidate, "content"):
        return _message_content_to_text(getattr(candidate, "content"))

    if isinstance(candidate, dict):
        if "content" in candidate:
            return _message_content_to_text(candidate.get("content"))
    return ""


def _extract_message_and_metadata(chunk: Any) -> tuple[Any, dict[str, Any]]:
    if isinstance(chunk, (tuple, list)) and len(chunk) >= 2:
        maybe_metadata = chunk[1]
        metadata = maybe_metadata if isinstance(maybe_metadata, dict) else {}
        return chunk[0], metadata
    return chunk, {}


def _iter_update_descriptions(update_chunk: Any) -> list[str]:
    namespace: tuple[Any, ...] = ()
    data = update_chunk

    if (
        isinstance(update_chunk, (tuple, list))
        and len(update_chunk) == 2
        and isinstance(update_chunk[1], dict)
    ):
        namespace = tuple(update_chunk[0]) if isinstance(update_chunk[0], tuple) else ()
        data = update_chunk[1]

    lines: list[str] = []
    if namespace:
        lines.append(f"子图: {' > '.join(str(x) for x in namespace)}")

    if not isinstance(data, dict):
        return lines

    for node_name, node_update in data.items():
        lines.append(f"步骤: {node_name}")

        if isinstance(node_update, dict):
            messages = node_update.get("messages")
            if isinstance(messages, list):
                for msg in messages:
                    tool_calls = _get_tool_calls(msg)
                    if tool_calls:
                        for tc in tool_calls:
                            if isinstance(tc, dict):
                                tool_name = tc.get("name") or tc.get("id") or "unknown"
                                lines.append(f"调用工具: {tool_name}")

                    msg_type = _get_msg_type(msg)
                    if msg_type == "tool":
                        tool_name = (
                            msg.get("name", "unknown")
                            if isinstance(msg, dict)
                            else getattr(msg, "name", "unknown")
                        )
                        lines.append(f"工具返回: {tool_name}")

    return lines


async def stream_chat_with_agent(
    message: str, history: list[Any], thread_id: str | None
) -> AsyncIterator[dict[str, Any]]:
    resolved_thread_id = thread_id or str(uuid.uuid4())
    normalized_messages = _to_deepagent_messages(history, message)

    assistant_full_text = ""
    started_nodes: set[str] = set()
    completed_nodes: set[str] = set()
    fallback_ai_text = ""

    yield {"event": "start", "thread_id": resolved_thread_id}

    try:
        event_iter = get_agent().astream_events(
            {"messages": normalized_messages},
            config={"configurable": {"thread_id": resolved_thread_id}},
            version="v2",
        )

        async for event in event_iter:
            kind = str(event.get("event", ""))
            name = str(event.get("name", ""))
            data = event.get("data") if isinstance(event.get("data"), dict) else {}
            metadata = (
                event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
            )
            node_name = str(metadata.get("langgraph_node") or name or "")

            if kind == "on_chat_model_stream":
                chunk = data.get("chunk")
                delta = _extract_event_chunk_text(chunk)
                if delta:
                    assistant_full_text += delta
                    yield {"event": "delta", "text": delta}
                continue

            if kind == "on_chain_start":
                if (
                    node_name
                    and node_name not in started_nodes
                    and node_name != "agent"
                ):
                    started_nodes.add(node_name)
                    yield {"event": "process", "text": f"进入阶段: {node_name}"}
                continue

            if kind == "on_tool_start":
                tool_input = data.get("input")
                yield {"event": "process", "text": f"调用工具: {name}"}
                if tool_input is not None:
                    yield {
                        "event": "process",
                        "text": f"工具参数: {_preview_output(tool_input)}",
                    }
                continue

            if kind == "on_tool_end":
                tool_output = data.get("output")
                yield {"event": "process", "text": f"工具完成: {name}"}
                if tool_output is not None:
                    yield {
                        "event": "process",
                        "text": f"工具结果: {_preview_output(tool_output)}",
                    }
                continue

            if kind == "on_chain_end":
                if (
                    node_name
                    and node_name not in completed_nodes
                    and node_name != "agent"
                ):
                    completed_nodes.add(node_name)
                    yield {"event": "process", "text": f"阶段完成: {node_name}"}

                output = data.get("output")
                if not assistant_full_text and output is not None:
                    fallback = _extract_ai_text_from_output(output)
                    if fallback:
                        fallback_ai_text = fallback
    except Exception as exc:
        if assistant_full_text:
            yield {"event": "error", "detail": f"stream interrupted: {exc}"}
        else:
            yield {"event": "error", "detail": f"stream failed: {exc}"}

    if not assistant_full_text and fallback_ai_text:
        assistant_full_text = fallback_ai_text
        yield {"event": "delta", "text": assistant_full_text}

    updated_history = list(normalized_messages)
    updated_history.append({"role": "assistant", "content": assistant_full_text})
    yield {
        "event": "done",
        "reply": assistant_full_text,
        "thread_id": resolved_thread_id,
        "history": updated_history,
    }


class ChatRequest(BaseModel):
    message: str
    history: list[Any] = Field(default_factory=list)
    thread_id: str | None = None


def _to_sse(event: dict[str, Any]) -> str:
    payload = json.dumps(event, ensure_ascii=False)
    return f"data: {payload}\n\n"


def create_app() -> FastAPI:
    app = FastAPI(title="AI Chat Platform", version="1.0.0")
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "model": model_name}

    @app.get("/api/skills")
    def skills() -> dict[str, Any]:
        return {"skills": _list_skill_packages(PROJECT_ROOT / "skills")}

    @app.get("/api/memories")
    def memories() -> dict[str, Any]:
        return _memories_payload()

    @app.get("/")
    def index() -> HTMLResponse:
        html = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
        version = _frontend_asset_version()
        rendered = html.replace("__ASSET_VERSION__", version)
        return HTMLResponse(rendered)

    @app.post("/api/chat")
    def chat(payload: ChatRequest) -> dict[str, Any]:
        if not payload.message.strip():
            raise HTTPException(status_code=400, detail="message cannot be empty")

        try:
            answer, thread_id, history = chat_with_agent(
                message=payload.message,
                history=payload.history,
                thread_id=payload.thread_id,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"chat failed: {exc}") from exc

        return {
            "reply": answer,
            "thread_id": thread_id,
            "history": history,
        }

    @app.post("/api/chat/stream")
    async def chat_stream(payload: ChatRequest) -> StreamingResponse:
        if not payload.message.strip():
            raise HTTPException(status_code=400, detail="message cannot be empty")

        async def event_generator() -> AsyncIterator[str]:
            async for event in stream_chat_with_agent(
                message=payload.message,
                history=payload.history,
                thread_id=payload.thread_id,
            ):
                yield _to_sse(event)

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return app


app = create_app()


def main() -> None:
    auto_reload = os.getenv("AUTO_RELOAD", "1") == "1"
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=auto_reload)


if __name__ == "__main__":
    main()
