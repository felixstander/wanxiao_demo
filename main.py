import json
import os
import shutil
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterator

import uvicorn
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MEMORIES_DIR = PROJECT_ROOT / "memories"
DAILY_DIR = MEMORIES_DIR / "daily"
LONG_TERM_FILE = MEMORIES_DIR / "MEMORY.md"

load_dotenv()

model_name = os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.5-flash")


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
        temperature=0.2,
    )

    external_skills_dir = Path.home() / ".deepagents" / "agent" / "skills"
    mirrored_skills_dir = PROJECT_ROOT / "skills"
    _sync_skills_to_project(external_skills_dir, mirrored_skills_dir)
    today = date.today()
    yesterday = today - timedelta(days=1)
    long_term_path, today_path = _ensure_memory_files(today)
    yesterday_path = f"/memories/daily/{yesterday.strftime('%Y-%m-%d')}.md"

    system_prompt = (
        "你是一个通用 DeepAgent。你需要使用双层记忆系统，并把记忆写入本地 Markdown 文件。\n\n"
        "记忆目录结构：\n"
        "- 长期记忆：/memories/MEMORY.md\n"
        "- 每日日志：/memories/daily/YYYY-MM-DD.md\n\n"
        "每次新会话开始时请先主动回忆：\n"
        f"1) read_file {long_term_path}\n"
        f"2) read_file {today_path}\n"
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
        skills=[str(mirrored_skills_dir)],
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


def stream_chat_with_agent(
    message: str, history: list[Any], thread_id: str | None
) -> Iterator[dict[str, Any]]:
    resolved_thread_id = thread_id or str(uuid.uuid4())
    normalized_messages = _to_deepagent_messages(history, message)

    assistant_full_text = ""
    got_stream_tokens = False
    last_node = ""
    fallback_ai_text_from_updates = ""

    yield {"event": "start", "thread_id": resolved_thread_id}

    try:
        stream_iter = get_agent().stream(
            {"messages": normalized_messages},
            config={"configurable": {"thread_id": resolved_thread_id}},
            stream_mode=["messages", "updates"],
            subgraphs=True,
        )

        for item in stream_iter:
            if (
                isinstance(item, (tuple, list))
                and len(item) == 2
                and item[0] in {"messages", "updates"}
            ):
                mode = item[0]
                chunk = item[1]
            else:
                mode = "messages"
                chunk = item

            if mode == "updates":
                for line in _iter_update_descriptions(chunk):
                    yield {"event": "process", "text": line}

                update_ai_text = _extract_ai_text_from_updates(chunk)
                if update_ai_text:
                    fallback_ai_text_from_updates = update_ai_text
                continue

            message_chunk, metadata = _extract_message_and_metadata(chunk)
            current_node = metadata.get("langgraph_node", "")
            if current_node and current_node != last_node:
                last_node = current_node
                yield {"event": "process", "text": f"LLM 节点: {current_node}"}

            delta = _extract_stream_text(message_chunk)
            if delta:
                got_stream_tokens = True
                assistant_full_text += delta
                yield {"event": "delta", "text": delta}

        if not assistant_full_text and fallback_ai_text_from_updates:
            assistant_full_text = fallback_ai_text_from_updates
            yield {"event": "delta", "text": assistant_full_text}
    except Exception as exc:
        if got_stream_tokens:
            yield {"event": "error", "detail": f"stream interrupted: {exc}"}
        else:
            answer, _, _ = chat_with_agent(
                message=message,
                history=history,
                thread_id=resolved_thread_id,
            )
            assistant_full_text = answer
            yield {"event": "delta", "text": answer}

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

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(str(FRONTEND_DIR / "index.html"))

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
    def chat_stream(payload: ChatRequest) -> StreamingResponse:
        if not payload.message.strip():
            raise HTTPException(status_code=400, detail="message cannot be empty")

        def event_generator() -> Iterator[str]:
            for event in stream_chat_with_agent(
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
