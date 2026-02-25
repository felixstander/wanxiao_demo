import argparse
import asyncio
import os
import uuid
from time import monotonic
from typing import Any

import uvicorn
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SalesActivityMonitor")

# 全局内存存储：管理倒计时任务状态
_countdown_tasks: dict[str, dict] = {}
_countdown_lock = asyncio.Lock()


@mcp.tool()
async def start_countdown_async(
    tool_name: str,
    countdown_seconds: int,
    timeout_script: str,
) -> dict[str, Any]:
    """启动异步非阻塞倒计时，立即返回 task_id，后台执行倒计时。

    参数:
        tool_name: 当前被监控的工具名称，用于标识倒计时归属。
        countdown_seconds: 倒计时时长（秒）。
        timeout_script: 倒计时结束后需要触发/展示的话术内容。

    返回:
        dict[str, Any]:
            - task_id: 倒计时任务唯一标识
            - status: "started"
            - countdown_seconds: 倒计时总时长
            - tool_name: 工具名称
    """
    task_id = str(uuid.uuid4())

    async def countdown_task() -> None:
        """后台倒计时任务"""
        started_at = asyncio.get_event_loop().time()
        async with _countdown_lock:
            _countdown_tasks[task_id] = {
                "task_id": task_id,
                "tool_name": tool_name,
                "countdown_seconds": countdown_seconds,
                "timeout_script": timeout_script,
                "started_at": started_at,
                "status": "running",
                "elapsed_seconds": 0,
            }

        # 执行倒计时
        await asyncio.sleep(countdown_seconds)

        # 倒计时完成，更新状态
        async with _countdown_lock:
            if task_id in _countdown_tasks:
                _countdown_tasks[task_id]["status"] = "completed"
                _countdown_tasks[task_id]["elapsed_seconds"] = countdown_seconds

    # 启动后台任务
    asyncio.create_task(countdown_task())

    return {
        "task_id": task_id,
        "status": "started",
        "countdown_seconds": countdown_seconds,
        "tool_name": tool_name,
    }


@mcp.tool()
async def get_countdown_status(task_id: str) -> dict[str, Any]:
    """查询倒计时任务状态。

    参数:
        task_id: 倒计时任务唯一标识。

    返回:
        dict[str, Any]:
            - status: "running" | "completed" | "not_found"
            - task_id: 任务ID
            - elapsed_seconds: 已过去秒数（running时实时计算）
            - remaining_seconds: 剩余秒数（仅running时）
            - timeout_script: 倒计时结束后的话术（completed时返回）
    """
    async with _countdown_lock:
        task = _countdown_tasks.get(task_id)
        if not task:
            return {
                "status": "not_found",
                "task_id": task_id,
            }

        if task["status"] == "running":
            elapsed = int(asyncio.get_event_loop().time() - task["started_at"])
            remaining = max(0, task["countdown_seconds"] - elapsed)
            return {
                "status": "running",
                "task_id": task_id,
                "elapsed_seconds": elapsed,
                "remaining_seconds": remaining,
                "timeout_script": task["timeout_script"],
            }
        else:
            # completed
            return {
                "status": "completed",
                "task_id": task_id,
                "timeout_script": task["timeout_script"],
                "elapsed_seconds": task["countdown_seconds"],
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
    parser = argparse.ArgumentParser(
        description="Run SalesActivityMonitor MCP server with SSE via uvicorn"
    )
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
