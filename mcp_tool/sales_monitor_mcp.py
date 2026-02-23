import argparse
import asyncio
import os
from time import monotonic
from typing import Any

from mcp.server.fastmcp import FastMCP
import uvicorn


mcp = FastMCP("SalesActivityMonitor")


@mcp.tool()
async def diagnose_stuck_point(
    tool_name: str,
    countdown_seconds: int,
    timeout_script: str,
    tick_seconds: int = 1,
    include_timeline: bool = True,
) -> dict[str, Any]:
    """异步监控指定工具的倒计时并在超时后返回预设话术。

    参数:
        tool_name: 当前被监控的工具名称，用于标识倒计时归属。
        countdown_seconds: 倒计时时长（秒）。函数会在服务端异步等待该时长结束。
        timeout_script: 倒计时结束后需要触发/展示的话术内容。
        tick_seconds: 倒计时轮询步长（秒），每个步长记录一次剩余时间；默认 1 秒。
        include_timeline: 是否返回完整监控轨迹（tick + timeout 事件）；默认返回。

    返回:
        dict[str, Any]:
            - 参数非法时返回错误结构：
              {"status": "error", "message": str, "data": None}
            - 倒计时完成时返回触发结果，包含：
              status/tool_name/countdown_seconds/elapsed_seconds/
              trigger_action/timeout_script/timeline。
    """
    if countdown_seconds <= 0:
        return {
            "status": "error",
            "message": "countdown_seconds 必须大于 0",
            "data": None,
        }

    if tick_seconds <= 0:
        return {
            "status": "error",
            "message": "tick_seconds 必须大于 0",
            "data": None,
        }

    timeline: list[dict[str, Any]] = []
    started_at = monotonic()
    elapsed_seconds = 0

    while elapsed_seconds < countdown_seconds:
        remaining_seconds = countdown_seconds - elapsed_seconds
        if include_timeline:
            timeline.append(
                {
                    "event": "tick",
                    "tool_name": tool_name,
                    "remaining_seconds": remaining_seconds,
                }
            )

        sleep_for = min(tick_seconds, max(remaining_seconds, 0))
        await asyncio.sleep(sleep_for)
        elapsed_seconds = int(monotonic() - started_at)

    total_elapsed = round(monotonic() - started_at, 3)

    if include_timeline:
        timeline.append(
            {
                "event": "timeout",
                "tool_name": tool_name,
                "remaining_seconds": 0,
                "script": timeout_script,
            }
        )

    return {
        "status": "timeout_triggered",
        "tool_name": tool_name,
        "countdown_seconds": countdown_seconds,
        "elapsed_seconds": total_elapsed,
        "trigger_action": "show_timeout_script",
        "timeout_script": timeout_script,
        "timeline": timeline,
    }


def create_sse_app(mount_path: str) -> Any:
    """创建用于 SSE 传输的 MCP ASGI 应用。

    参数:
        mount_path: SSE 路由挂载前缀。传入 "/" 时对外暴露 `/sse` 和 `/messages/`。

    返回:
        Any: 可直接交给 uvicorn 运行的 ASGI 应用对象。
    """
    return mcp.sse_app(mount_path=mount_path)


def parse_cli_args() -> argparse.Namespace:
    """解析终端启动参数，用于配置 IP、端口与路由前缀。

    参数:
        无。

    返回:
        argparse.Namespace: 包含 host、port、mount_path、log_level 四个字段。
    """
    parser = argparse.ArgumentParser(description="Run SalesActivityMonitor MCP server with SSE via uvicorn")
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", "127.0.0.1"),
        help="监听 IP 地址，默认 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8000")),
        help="监听端口，默认 8000",
    )
    parser.add_argument(
        "--mount-path",
        default=os.getenv("MCP_MOUNT_PATH", "/"),
        help="SSE 路由挂载路径，默认 '/'",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("MCP_LOG_LEVEL", "info"),
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="uvicorn 日志级别",
    )
    return parser.parse_args()


def run_sse_server_with_uvicorn(
    host: str,
    port: int,
    mount_path: str,
    log_level: str,
) -> None:
    """使用 uvicorn 启动基于 SSE 传输的 MCP 服务。

    参数:
        host: 服务监听 IP。
        port: 服务监听端口。
        mount_path: SSE 路由挂载前缀。
        log_level: uvicorn 日志级别。

    返回:
        None: 函数会阻塞运行，直到服务退出。
    """
    app = create_sse_app(mount_path=mount_path)
    uvicorn.run(app, host=host, port=port, log_level=log_level)


app = create_sse_app(mount_path=os.getenv("MCP_MOUNT_PATH", "/"))


if __name__ == "__main__":
    args = parse_cli_args()
    print(
        "Starting SalesActivityMonitor MCP Server via uvicorn "
        f"(transport=sse, host={args.host}, port={args.port}, mount_path={args.mount_path})..."
    )
    run_sse_server_with_uvicorn(
        host=args.host,
        port=args.port,
        mount_path=args.mount_path,
        log_level=args.log_level,
    )
