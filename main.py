import csv
import json
import os
import re
import threading
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, AsyncIterator

import uvicorn
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field

from src.output_sanitize_config import load_output_sanitize_config
from src.prompt_config import PromptConfig

# 倒计时 MCP 服务配置
COUNTDOWN_MCP_URL = os.getenv("COUNTDOWN_MCP_URL", "http://127.0.0.1:8765")

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MEMORIES_DIR = PROJECT_ROOT / "memories"
DAILY_DIR = MEMORIES_DIR / "daily"
LONG_TERM_FILE = MEMORIES_DIR / "MEMORY.md"

load_dotenv()
PROMPTS = PromptConfig(PROJECT_ROOT)
OUTPUT_SANITIZE_CONFIG = load_output_sanitize_config(
    PROJECT_ROOT / "config" / "output_sanitize.yaml"
)

model_name = PROMPTS.get_model_name("main")
memory_model_name = PROMPTS.get_model_name("memory_agent")
MEMORY_WRITE_LOCK = threading.Lock()


def _env_flag(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


MEMORY_AGENT_ENABLED = _env_flag("MEMORY_AGENT_ENABLED", default=True)
OUTPUT_SANITIZE_ENABLED = _env_flag("OUTPUT_SANITIZE_ENABLED", default=True)
CHECKPOINTER = MemorySaver()


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

    return (
        "/memories/MEMORY.md",
        f"/memories/daily/{today_name}.md",
    )


def build_agent() -> Any:
    # api_key = os.getenv("OPENROUTER_API_KEY")
    api_key = os.getenv("GLM_API_KEY")
    # if not api_key:
    #     raise RuntimeError("OPENROUTER_API_KEY is missing. Please set it in .env")
    #
    if not api_key:
        raise RuntimeError("GLM_API_KEY is missing. Please set it in .env")

    os.environ["OPENAI_API_KEY"] = api_key

    # llm = ChatOpenAI(
    #     model=model_name,
    #     base_url="https://openrouter.ai/api/v1",
    #     # temperature=0.2,
    # )
    llm = ChatOpenAI(
        model=model_name,
        base_url="https://open.bigmodel.cn/api/paas/v4",
        temperature=0.1,
    )

    skills_dir = PROJECT_ROOT / "skills"
    today = date.today()
    yesterday = today - timedelta(days=1)
    long_term_path, today_path = _ensure_memory_files(today)
    yesterday_path = f"/memories/daily/{yesterday.strftime('%Y-%m-%d')}.md"

    system_prompt = PROMPTS.render_prompt(
        "main_system",
        {
            "long_term_path": str(long_term_path),
            "today_path": str(today_path),
            "yesterday_path": str(yesterday_path),
        },
    )

    def _make_backend(runtime):
        return CompositeBackend(
            default=StateBackend(runtime),  # Ephemeral storage
            routes={
                "/memories/": FilesystemBackend(root_dir=str(MEMORIES_DIR)),
                "/skills/": FilesystemBackend(root_dir=str(PROJECT_ROOT)),
            },  # Persistent storage
        )

    agent = create_deep_agent(
        model=llm,
        store=InMemoryStore(),
        backend=FilesystemBackend(root_dir=str(PROJECT_ROOT)),
        skills=[str(skills_dir)],
        memory=[long_term_path, today_path, yesterday_path],
        checkpointer=CHECKPOINTER,
        system_prompt=system_prompt,
    )
    return agent


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


def _customers_payload(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists() or not csv_path.is_file():
        return []

    customers: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not isinstance(row, dict):
                continue

            name = str(row.get("name", "")).strip()
            age = str(row.get("age", "")).strip()
            gender = str(row.get("gender", "")).strip()
            behavior = str(row.get("behaviors", "")).strip()
            if not name:
                continue

            customers.append(
                {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "behavior": behavior,
                }
            )

    return customers


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
    return path.read_text(encoding="utf-8", errors="replace")


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
MEMORY_AGENT: Any | None = None


def get_agent() -> Any:
    global AGENT
    if AGENT is None:
        AGENT = build_agent()
    return AGENT


def build_memory_agent() -> Any:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Please set it in .env")

    os.environ["OPENAI_API_KEY"] = api_key
    llm = ChatOpenAI(
        model=memory_model_name,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1,
    )

    system_prompt = PROMPTS.render_prompt("memory_agent")
    agent = create_deep_agent(
        model=llm,
        backend=FilesystemBackend(root_dir=str(PROJECT_ROOT), virtual_mode=True),
        system_prompt=system_prompt,
    )
    return agent


def get_memory_agent() -> Any:
    global MEMORY_AGENT
    if MEMORY_AGENT is None:
        MEMORY_AGENT = build_memory_agent()
    return MEMORY_AGENT


def _now_hhmm() -> str:
    return datetime.now().strftime("%H:%M")


def _append_daily_memory(title: str, bullets: list[str], today_path: Path) -> None:
    cleaned_title = title.strip() or "会话记录"
    cleaned_bullets = [x.strip() for x in bullets if x and x.strip()]
    if not cleaned_bullets:
        return

    block_lines = [f"## {_now_hhmm()} - {cleaned_title}"]
    for line in cleaned_bullets:
        block_lines.append(f"- {line}")
    block = "\n" + "\n".join(block_lines) + "\n"

    current = _read_text_file(today_path)
    today_path.write_text(current + block, encoding="utf-8")


def _parse_long_term_sections(content: str) -> dict[str, list[str]]:
    section_names = ["用户偏好", "重要决策", "关键联系人", "项目事实"]
    sections: dict[str, list[str]] = {name: [] for name in section_names}
    current_section = ""

    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            name = line[3:].strip()
            current_section = name if name in sections else ""
            continue
        if current_section and line.startswith("-"):
            item = line[1:].strip()
            if item and item != "暂无":
                sections[current_section].append(item)

    return sections


def _render_long_term_sections(sections: dict[str, list[str]]) -> str:
    ordered_names = ["用户偏好", "重要决策", "关键联系人", "项目事实"]
    lines = ["# 长期记忆", ""]
    for name in ordered_names:
        lines.append(f"## {name}")
        items = []
        seen: set[str] = set()
        for text in sections.get(name, []):
            normalized = text.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            items.append(normalized)
        if not items:
            lines.append("- 暂无")
        else:
            for item in items:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _merge_long_term_memory(
    updates: dict[str, list[str]], long_term_path: Path
) -> None:
    current = _read_text_file(long_term_path)
    sections = _parse_long_term_sections(current)

    for key, values in updates.items():
        if key not in sections or not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, str) and value.strip():
                sections[key].append(value.strip())

    long_term_path.write_text(_render_long_term_sections(sections), encoding="utf-8")


def _safe_json_loads(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _strip_markdown_syntax(text: str) -> str:
    if not text:
        return ""

    value = text
    value = re.sub(r"```[\w-]*\n?", "", value)
    value = value.replace("```", "")
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"==([^=]+)==", r"\1", value)
    return value


def _is_internal_leak_line(line: str) -> bool:
    if not OUTPUT_SANITIZE_ENABLED or not OUTPUT_SANITIZE_CONFIG.enabled:
        return False

    s = line.strip()
    if not s:
        return False

    if any(token in s for token in OUTPUT_SANITIZE_CONFIG.literals):
        return True

    return any(pattern.search(s) for pattern in OUTPUT_SANITIZE_CONFIG.regex_patterns)


def _sanitize_user_facing_text(text: str) -> str:
    raw = _strip_markdown_syntax(text)
    lines = raw.splitlines()
    kept = [line for line in lines if not _is_internal_leak_line(line)]
    cleaned = "\n".join(kept).strip()
    return cleaned


def _consume_stream_buffer(buffer: str) -> tuple[str, str]:
    if "\n" not in buffer:
        return "", buffer

    parts = buffer.split("\n")
    remain = parts.pop() if parts else ""
    output_parts: list[str] = []
    for raw_line in parts:
        clean_line = _strip_markdown_syntax(raw_line)
        if _is_internal_leak_line(clean_line):
            continue
        output_parts.append(clean_line)

    flushed = "\n".join(output_parts)
    if flushed:
        flushed += "\n"
    return flushed, remain


def _run_memory_agent_sync(user_message: str, assistant_message: str) -> None:
    if not user_message.strip() or not assistant_message.strip():
        return

    with MEMORY_WRITE_LOCK:
        today = date.today()
        _, today_virtual_path = _ensure_memory_files(today)
        today_path = PROJECT_ROOT / today_virtual_path.lstrip("/")
        yesterday = today - timedelta(days=1)
        yesterday_virtual_path = f"/memories/daily/{yesterday.strftime('%Y-%m-%d')}.md"
        yesterday_path = PROJECT_ROOT / yesterday_virtual_path.lstrip("/")

        long_term_path = LONG_TERM_FILE
        today_log_content = _read_text_file(today_path)
        yesterday_log_content = _read_text_file(yesterday_path)
        long_term_content = _read_text_file(long_term_path)

        memory_task = (
            "请基于以下本轮会话更新记忆文件，并直接使用文件工具落盘。\n\n"
            f"用户消息:\n{user_message}\n\n"
            f"助手回复:\n{assistant_message}\n\n"
            f"今日日志路径: {today_virtual_path}\n"
            f"昨日日志路径: {yesterday_virtual_path}\n"
            "长期记忆路径: /memories/MEMORY.md\n\n"
            "今天日志当前内容:\n"
            f"{today_log_content or '(空)'}\n\n"
            "昨天日志当前内容:\n"
            f"{yesterday_log_content or '(空)'}\n\n"
            "长期记忆当前内容:\n"
            f"{long_term_content or '(空)'}\n"
        )

        get_memory_agent().invoke(
            {"messages": [{"role": "user", "content": memory_task}]},
            config={
                "configurable": {"thread_id": f"memory-{today.strftime('%Y-%m-%d')}"}
            },
        )


def _dispatch_memory_agent(user_message: str, assistant_message: str) -> None:
    if not MEMORY_AGENT_ENABLED:
        return

    worker = threading.Thread(
        target=_run_memory_agent_sync,
        args=(user_message, assistant_message),
        daemon=True,
    )
    worker.start()


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
    input_messages = [{"role": "user", "content": message}]

    result = get_agent().invoke(
        {"messages": input_messages},
        config={"configurable": {"thread_id": resolved_thread_id}},
    )

    assistant_text = ""
    for msg in reversed(result.get("messages", [])):
        if _get_msg_type(msg) == "ai":
            assistant_text = _message_content_to_text(_get_msg_content(msg))
            break

    assistant_text = _sanitize_user_facing_text(assistant_text)

    updated_history = _to_deepagent_messages(history, message)
    updated_history.append({"role": "assistant", "content": assistant_text})
    _dispatch_memory_agent(user_message=message, assistant_message=assistant_text)
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


async def stream_chat_with_agent(
    message: str, history: list[Any], thread_id: str | None
) -> AsyncIterator[dict[str, Any]]:
    resolved_thread_id = thread_id or str(uuid.uuid4())
    input_messages = [{"role": "user", "content": message}]

    assistant_full_text = ""
    started_nodes: set[str] = set()
    completed_nodes: set[str] = set()
    fallback_ai_text = ""
    stream_buffer = ""

    yield {"event": "start", "thread_id": resolved_thread_id}

    try:
        event_iter = get_agent().astream_events(
            {"messages": input_messages},
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
                    stream_buffer += delta
                    flushed, stream_buffer = _consume_stream_buffer(stream_buffer)
                    if flushed:
                        assistant_full_text += flushed
                        yield {"event": "delta", "text": flushed}
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
                tool_result_preview = ""
                if tool_output is not None:
                    tool_result_preview = _preview_output(tool_output)

                # 检测 start_countdown_async 工具完成，发送 countdown_started 事件
                if name == "start_countdown_async" and tool_output:
                    task_id = tool_output.get("task_id")
                    countdown_seconds = tool_output.get("countdown_seconds", 10)
                    if task_id:
                        yield {
                            "event": "countdown_started",
                            "task_id": task_id,
                            "countdown_seconds": countdown_seconds,
                        }

                yield {"event": "process", "text": f"工具完成: {name}"}
                if tool_result_preview:
                    yield {
                        "event": "process",
                        "text": f"工具结果: {tool_result_preview}",
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

    if stream_buffer:
        tail = _strip_markdown_syntax(stream_buffer)
        if not _is_internal_leak_line(tail):
            assistant_full_text += tail
            yield {"event": "delta", "text": tail}

    if not assistant_full_text and fallback_ai_text:
        assistant_full_text = _sanitize_user_facing_text(fallback_ai_text)
        if assistant_full_text:
            yield {"event": "delta", "text": assistant_full_text}

    assistant_full_text = _sanitize_user_facing_text(assistant_full_text)

    updated_history = _to_deepagent_messages(history, message)
    updated_history.append({"role": "assistant", "content": assistant_full_text})
    _dispatch_memory_agent(user_message=message, assistant_message=assistant_full_text)
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

    @app.get("/api/customers")
    def customers() -> dict[str, Any]:
        return {
            "customers": _customers_payload(PROJECT_ROOT / "data" / "customer_db.csv")
        }

    @app.get("/api/memories")
    def memories() -> dict[str, Any]:
        return _memories_payload()

    @app.get("/api/countdown/{task_id}")
    async def get_countdown_status_api(task_id: str) -> dict[str, Any]:
        """代理查询 MCP 服务的倒计时状态"""
        import urllib.error
        import urllib.request

        try:
            # 调用 MCP 服务的 get_countdown_status 工具
            # MCP 通过 /messages/ 端点接收 JSON-RPC 请求
            request_body = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "get_countdown_status",
                        "arguments": {"task_id": task_id},
                    },
                }
            ).encode("utf-8")

            req = urllib.request.Request(
                f"{COUNTDOWN_MCP_URL}/messages/",
                data=request_body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=5) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                # 解析 MCP 响应
                if "result" in response_data:
                    result = response_data["result"]
                    if isinstance(result, dict) and "content" in result:
                        content = result["content"]
                        if isinstance(content, list) and len(content) > 0:
                            text_item = content[0]
                            if isinstance(text_item, dict) and "text" in text_item:
                                data = json.loads(text_item["text"])
                                return data

                # 如果无法解析，返回错误
                return {"status": "error", "message": "无法解析 MCP 响应"}

        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"status": "not_found", "task_id": task_id}
            return {"status": "error", "message": f"MCP 服务错误: {e.code}"}
        except Exception as e:
            return {"status": "error", "message": f"查询失败: {str(e)}"}

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
