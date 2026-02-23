#!/usr/bin/env python3
"""通过 MCP SSE 调用倒计时工具并轮询获取结果。"""

import argparse
import json
import os
import queue
import threading
from time import monotonic
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def parse_args() -> argparse.Namespace:
    """解析倒计时 MCP 调用所需的命令行参数。

    参数:
        无。

    返回:
        argparse.Namespace: 包含工具入参、服务地址和超时配置的参数对象。
    """
    parser = argparse.ArgumentParser(description="Call diagnose_stuck_point through MCP SSE and poll result")
    parser.add_argument("tool_name", help="Tool label for countdown context, e.g. 出单工具")
    parser.add_argument("countdown_seconds", type=int, help="Countdown duration in seconds")
    parser.add_argument("timeout_script", help="Script text to trigger when countdown ends")
    parser.add_argument(
        "--base-url",
        default=os.getenv("MCP_BASE_URL", "http://127.0.0.1:8765"),
        help="MCP service base URL",
    )
    parser.add_argument(
        "--protocol-version",
        default=os.getenv("MCP_PROTOCOL_VERSION", "2025-03-26"),
        help="MCP protocol version used in initialize",
    )
    parser.add_argument(
        "--connect-timeout",
        type=float,
        default=15.0,
        help="Seconds to wait for SSE endpoint event",
    )
    parser.add_argument(
        "--poll-timeout",
        type=float,
        default=None,
        help="Seconds to wait for tools/call result; defaults to countdown_seconds + 30",
    )
    parser.add_argument(
        "--tick-seconds",
        type=int,
        default=1,
        help="tick_seconds argument for diagnose_stuck_point",
    )
    parser.add_argument(
        "--include-timeline",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Pass include_timeline to diagnose_stuck_point",
    )
    parser.add_argument(
        "--tool-api-name",
        default="diagnose_stuck_point",
        help="MCP tool API name to call",
    )
    return parser.parse_args()


def build_url(base_url: str, path_or_uri: str) -> str:
    """根据基础地址与相对路径拼接绝对 URL。

    参数:
        base_url: 服务基础地址，例如 http://127.0.0.1:8765。
        path_or_uri: SSE endpoint 事件返回的相对路径或 URI。

    返回:
        str: 绝对 URL。
    """
    normalized_base = base_url.rstrip("/") + "/"
    return urljoin(normalized_base, path_or_uri)


def post_json(url: str, payload: dict[str, Any], timeout_seconds: float) -> tuple[int, str]:
    """发送 JSON POST 请求并返回状态码和响应体。

    参数:
        url: 完整 HTTP 接口地址。
        payload: JSON 请求体字典。
        timeout_seconds: HTTP 请求超时时间（秒）。

    返回:
        tuple[int, str]: HTTP 状态码与响应文本。

    异常:
        RuntimeError: 当 HTTP 请求失败时抛出。
    """
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, body
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace") if hasattr(error, "read") else str(error)
        raise RuntimeError(f"HTTP {error.code} when posting {url}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Network error when posting {url}: {error}") from error


def sse_listener(
    sse_url: str,
    endpoint_queue: queue.Queue[str],
    message_queue: queue.Queue[dict[str, Any]],
    error_queue: queue.Queue[str],
    stop_event: threading.Event,
    socket_timeout_seconds: float,
) -> None:
    """监听 SSE 事件流并把 endpoint/message 事件分发到队列。

    参数:
        sse_url: SSE 接口地址。
        endpoint_queue: 接收 endpoint 事件 URI 的队列。
        message_queue: 接收 message 事件 JSON-RPC 数据的队列。
        error_queue: 接收监听异常信息的队列。
        stop_event: 外部停止监听的事件信号。
        socket_timeout_seconds: SSE 连接的套接字超时时间（秒）。

    返回:
        None: 结果通过传入队列返回。
    """
    request = Request(sse_url, headers={"Accept": "text/event-stream"})
    event_name = ""
    data_lines: list[str] = []

    try:
        with urlopen(request, timeout=socket_timeout_seconds) as response:
            while not stop_event.is_set():
                raw_line = response.readline()
                if not raw_line:
                    break

                line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")

                if not line:
                    if data_lines:
                        event_data = "\n".join(data_lines)
                        event_type = event_name or "message"
                        if event_type == "endpoint":
                            endpoint_queue.put(event_data)
                        elif event_type == "message":
                            try:
                                message_queue.put(json.loads(event_data))
                            except json.JSONDecodeError as error:
                                error_queue.put(f"Invalid JSON in message event: {error}")
                    event_name = ""
                    data_lines = []
                    continue

                if line.startswith(":"):
                    continue
                if line.startswith("event:"):
                    event_name = line[6:].strip()
                    continue
                if line.startswith("data:"):
                    data_lines.append(line[5:].lstrip())
    except Exception as error:
        error_queue.put(str(error))


def wait_for_endpoint(
    endpoint_queue: queue.Queue[str],
    error_queue: queue.Queue[str],
    timeout_seconds: float,
) -> str:
    """等待 SSE 流返回 endpoint 事件。

    参数:
        endpoint_queue: 存放 endpoint URI 的队列。
        error_queue: 存放监听错误的队列。
        timeout_seconds: 最长等待时间（秒）。

    返回:
        str: 服务端返回的 endpoint URI。

    异常:
        RuntimeError: 超时或监听器报错时抛出。
    """
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        if not error_queue.empty():
            raise RuntimeError(f"SSE listener failed: {error_queue.get()}")
        remaining = max(deadline - monotonic(), 0.0)
        try:
            return endpoint_queue.get(timeout=min(0.5, remaining))
        except queue.Empty:
            continue
    raise RuntimeError(f"Timed out waiting for SSE endpoint event after {timeout_seconds} seconds")


def wait_for_response(
    message_queue: queue.Queue[dict[str, Any]],
    error_queue: queue.Queue[str],
    request_id: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    """轮询消息队列直到拿到指定 request_id 的 JSON-RPC 响应。

    参数:
        message_queue: 存放 SSE message 事件 JSON-RPC 数据的队列。
        error_queue: 存放监听错误的队列。
        request_id: 目标 JSON-RPC 请求 ID。
        timeout_seconds: 最长等待时间（秒）。

    返回:
        dict[str, Any]: 匹配 request_id 的 JSON-RPC 响应对象。

    异常:
        RuntimeError: 超时或监听器报错时抛出。
    """
    deadline = monotonic() + timeout_seconds
    target = str(request_id)

    while monotonic() < deadline:
        if not error_queue.empty():
            raise RuntimeError(f"SSE listener failed: {error_queue.get()}")

        remaining = max(deadline - monotonic(), 0.0)
        try:
            message = message_queue.get(timeout=min(0.5, remaining))
        except queue.Empty:
            continue

        message_id = message.get("id")
        if message_id is None:
            continue

        if str(message_id) == target:
            return message

    raise RuntimeError(f"Timed out waiting for response id={request_id} after {timeout_seconds} seconds")


def run_countdown_call(args: argparse.Namespace) -> dict[str, Any]:
    """执行完整 MCP SSE 调用流程并返回 tools/call 响应。

    参数:
        args: 解析后的命令行参数对象。

    返回:
        dict[str, Any]: 聚合结果，包含 initialize 与 tools/call 的原始响应。
    """
    if args.countdown_seconds <= 0:
        raise RuntimeError("countdown_seconds must be a positive integer")

    if args.tick_seconds <= 0:
        raise RuntimeError("tick_seconds must be a positive integer")

    poll_timeout = args.poll_timeout if args.poll_timeout is not None else float(args.countdown_seconds + 30)
    sse_url = build_url(args.base_url, "/sse")

    endpoint_queue: queue.Queue[str] = queue.Queue()
    message_queue: queue.Queue[dict[str, Any]] = queue.Queue()
    error_queue: queue.Queue[str] = queue.Queue()
    stop_event = threading.Event()

    listener = threading.Thread(
        target=sse_listener,
        args=(
            sse_url,
            endpoint_queue,
            message_queue,
            error_queue,
            stop_event,
            poll_timeout + 30,
        ),
        daemon=True,
    )
    listener.start()

    try:
        endpoint_uri = wait_for_endpoint(endpoint_queue, error_queue, args.connect_timeout)
        message_url = build_url(args.base_url, endpoint_uri)

        initialize_id = 1
        init_payload = {
            "jsonrpc": "2.0",
            "id": initialize_id,
            "method": "initialize",
            "params": {
                "protocolVersion": args.protocol_version,
                "capabilities": {},
                "clientInfo": {"name": "countdown-skill-script", "version": "1.0.0"},
            },
        }
        post_json(message_url, init_payload, timeout_seconds=15)
        init_response = wait_for_response(message_queue, error_queue, initialize_id, timeout_seconds=15)

        initialized_payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        post_json(message_url, initialized_payload, timeout_seconds=15)

        tool_call_id = 2
        tool_payload = {
            "jsonrpc": "2.0",
            "id": tool_call_id,
            "method": "tools/call",
            "params": {
                "name": args.tool_api_name,
                "arguments": {
                    "tool_name": args.tool_name,
                    "countdown_seconds": args.countdown_seconds,
                    "timeout_script": args.timeout_script,
                    "tick_seconds": args.tick_seconds,
                    "include_timeline": args.include_timeline,
                },
            },
        }
        post_json(message_url, tool_payload, timeout_seconds=15)
        tool_response = wait_for_response(message_queue, error_queue, tool_call_id, timeout_seconds=poll_timeout)

        return {
            "status": "success",
            "base_url": args.base_url,
            "sse_url": sse_url,
            "message_url": message_url,
            "initialize_response": init_response,
            "tool_call_response": tool_response,
        }
    finally:
        stop_event.set()


def main() -> None:
    """终端入口函数。

    参数:
        无。

    返回:
        None: 将结果打印为 JSON，并按执行状态退出。
    """
    args = parse_args()
    try:
        result = run_countdown_call(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as error:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": str(error),
                    "base_url": args.base_url,
                    "tool_name": args.tool_name,
                    "countdown_seconds": args.countdown_seconds,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
