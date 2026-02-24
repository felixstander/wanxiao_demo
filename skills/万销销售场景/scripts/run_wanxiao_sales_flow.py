#!/usr/bin/env python3
"""执行万销销售场景的意向判断、工具分流与倒计时话术触发。"""

from __future__ import annotations

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


INTENT_COUNTDOWN_POLICY: dict[str, dict[str, Any]] = {
    "高意向": {
        "tool_name": "出单工具",
        "countdown_seconds": 10,
        "timeout_script": "您已经停留一段时间了，是否需要帮您解释保单的内容？",
    },
    "中意向": {
        "tool_name": "中意向培育工具",
        "countdown_seconds": 10,
        "timeout_script": "是否遇到理解困难？",
    },
    "低意向": {
        "tool_name": "低意向培育工具",
        "countdown_seconds": 10,
        "timeout_script": "内容是否符合您的要求？",
    },
}


def parse_args() -> argparse.Namespace:
    """解析万销销售场景脚本所需的命令行参数。

    参数:
        无。

    返回:
        argparse.Namespace: 包含客户信息、服务地址和调用控制参数。
    """
    parser = argparse.ArgumentParser(description="Run Wanxiao sales scenario workflow via MCP SSE")
    parser.add_argument("customer_name", help="客户姓名")
    parser.add_argument("--age", type=int, default=None, help="客户年龄")
    parser.add_argument("--gender", default="男", choices=["男", "女"], help="客户性别")
    parser.add_argument("--behavior", default=None, help="客户行为描述")
    parser.add_argument("--viewed-issue-link-count", type=int, default=None, help="出单链接查看次数")
    parser.add_argument("--claim-count", type=int, default=0, help="历史出险次数")
    parser.add_argument("--reimbursed-diseases", default="", help="历史报销疾病，逗号分隔")
    parser.add_argument("--annual-income", type=int, default=200000, help="客户年收入")
    parser.add_argument("--family-structure", default="单身", help="家庭结构")
    parser.add_argument("--existing-insurance-budget", type=int, default=0, help="已有保险预算")
    parser.add_argument("--viewed-products", default="", help="浏览过的产品，逗号分隔")
    parser.add_argument("--consulted-products", default="", help="咨询过的产品，逗号分隔")
    parser.add_argument("--city", default=None, help="客户城市")
    parser.add_argument("--upcoming-event", default=None, help="指定节日名称")
    parser.add_argument(
        "--include-product-comparison",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="中意向场景是否额外调用产品对比工具",
    )
    parser.add_argument(
        "--include-agent-card",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="低意向场景是否额外调用代理人 AI 名片工具",
    )
    parser.add_argument(
        "--skip-countdown",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="是否跳过倒计时监控工具调用",
    )
    parser.add_argument(
        "--sales-base-url",
        default=os.getenv("SALES_MCP_BASE_URL", "http://127.0.0.1:8765"),
        help="销售场景 MCP 服务地址",
    )
    parser.add_argument(
        "--monitor-base-url",
        default=os.getenv("MONITOR_MCP_BASE_URL", "http://127.0.0.1:8766"),
        help="倒计时监控 MCP 服务地址",
    )
    parser.add_argument(
        "--protocol-version",
        default=os.getenv("MCP_PROTOCOL_VERSION", "2025-03-26"),
        help="MCP 协议版本",
    )
    parser.add_argument("--connect-timeout", type=float, default=15.0, help="SSE 建连等待超时（秒）")
    parser.add_argument("--tool-timeout", type=float, default=60.0, help="单次工具调用等待超时（秒）")
    return parser.parse_args()


def parse_csv_list(value: str) -> list[str]:
    """把逗号分隔字符串解析为列表。

    参数:
        value: 原始字符串。

    返回:
        list[str]: 去空白且去空元素后的字符串列表。
    """
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def build_url(base_url: str, path_or_uri: str) -> str:
    """根据基础地址和相对路径拼接绝对 URL。

    参数:
        base_url: 服务基础地址。
        path_or_uri: 相对路径或 URI。

    返回:
        str: 绝对 URL。
    """
    normalized_base = base_url.rstrip("/") + "/"
    return urljoin(normalized_base, path_or_uri)


def post_json(url: str, payload: dict[str, Any], timeout_seconds: float) -> tuple[int, str]:
    """发送 JSON POST 请求并返回状态码与响应体。

    参数:
        url: 接口地址。
        payload: JSON 请求体。
        timeout_seconds: HTTP 请求超时秒数。

    返回:
        tuple[int, str]: 状态码与响应体文本。

    异常:
        RuntimeError: 网络异常或 HTTP 状态异常时抛出。
    """
    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace") if hasattr(error, "read") else str(error)
        raise RuntimeError(f"HTTP {error.code} when posting {url}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Network error when posting {url}: {error}") from error


def extract_structured_content(tool_response: dict[str, Any]) -> dict[str, Any]:
    """从 tools/call 响应中提取 structuredContent。

    参数:
        tool_response: JSON-RPC tools/call 响应对象。

    返回:
        dict[str, Any]: structuredContent；若不存在则尝试从文本 JSON 解析。
    """
    result = tool_response.get("result")
    if not isinstance(result, dict):
        return {}

    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured

    content = result.get("content")
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                try:
                    parsed = json.loads(item["text"])
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, dict):
                    return parsed

    return {}


class McpSseClient:
    """基于 SSE 的 MCP 客户端，封装 initialize 和 tools/call 调用。"""

    def __init__(
        self,
        base_url: str,
        protocol_version: str,
        connect_timeout: float,
        socket_timeout: float,
    ) -> None:
        """初始化 MCP SSE 客户端。

        参数:
            base_url: MCP 服务基础地址。
            protocol_version: 协议版本。
            connect_timeout: 等待 endpoint 事件超时（秒）。
            socket_timeout: SSE socket 超时（秒）。

        返回:
            None。
        """
        self.base_url = base_url
        self.protocol_version = protocol_version
        self.connect_timeout = connect_timeout
        self.socket_timeout = socket_timeout
        self.sse_url = build_url(base_url, "/sse")
        self.message_url: str | None = None
        self.endpoint_queue: queue.Queue[str] = queue.Queue()
        self.message_queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self.error_queue: queue.Queue[str] = queue.Queue()
        self.stop_event = threading.Event()
        self.listener_thread: threading.Thread | None = None
        self.request_id = 0

    def connect(self) -> dict[str, Any]:
        """建立 SSE 会话并完成 initialize 握手。

        参数:
            无。

        返回:
            dict[str, Any]: initialize 响应对象。
        """
        self.listener_thread = threading.Thread(
            target=self._listener_loop,
            daemon=True,
        )
        self.listener_thread.start()

        endpoint_uri = self._wait_for_endpoint(self.connect_timeout)
        self.message_url = build_url(self.base_url, endpoint_uri)

        init_id = self._next_request_id()
        init_payload = {
            "jsonrpc": "2.0",
            "id": init_id,
            "method": "initialize",
            "params": {
                "protocolVersion": self.protocol_version,
                "capabilities": {},
                "clientInfo": {"name": "wanxiao-sales-skill", "version": "1.0.0"},
            },
        }
        post_json(self.message_url, init_payload, timeout_seconds=15)
        init_response = self._wait_for_response(init_id, timeout_seconds=15)

        initialized_payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        post_json(self.message_url, initialized_payload, timeout_seconds=15)
        return init_response

    def call_tool(self, tool_name: str, arguments: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
        """调用指定 MCP 工具并等待返回。

        参数:
            tool_name: 工具名。
            arguments: 工具入参字典。
            timeout_seconds: 等待响应超时（秒）。

        返回:
            dict[str, Any]: JSON-RPC 响应对象。
        """
        if not self.message_url:
            raise RuntimeError("MCP client is not connected")

        request_id = self._next_request_id()
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }
        post_json(self.message_url, payload, timeout_seconds=15)
        return self._wait_for_response(request_id, timeout_seconds)

    def close(self) -> None:
        """关闭 SSE 监听线程。

        参数:
            无。

        返回:
            None。
        """
        self.stop_event.set()
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1)

    def _next_request_id(self) -> int:
        """生成递增的请求 ID。

        参数:
            无。

        返回:
            int: 新请求 ID。
        """
        self.request_id += 1
        return self.request_id

    def _listener_loop(self) -> None:
        """监听 SSE 事件并写入 endpoint 与消息队列。

        参数:
            无。

        返回:
            None。
        """
        request = Request(self.sse_url, headers={"Accept": "text/event-stream"})
        event_name = ""
        data_lines: list[str] = []

        try:
            with urlopen(request, timeout=self.socket_timeout) as response:
                while not self.stop_event.is_set():
                    raw_line = response.readline()
                    if not raw_line:
                        break

                    line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if not line:
                        if data_lines:
                            event_data = "\n".join(data_lines)
                            event_type = event_name or "message"
                            if event_type == "endpoint":
                                self.endpoint_queue.put(event_data)
                            elif event_type == "message":
                                try:
                                    self.message_queue.put(json.loads(event_data))
                                except json.JSONDecodeError as error:
                                    self.error_queue.put(f"Invalid JSON in message event: {error}")
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
            self.error_queue.put(str(error))

    def _wait_for_endpoint(self, timeout_seconds: float) -> str:
        """等待 endpoint 事件并返回消息接口 URI。

        参数:
            timeout_seconds: 超时秒数。

        返回:
            str: endpoint 事件返回的 URI。
        """
        deadline = monotonic() + timeout_seconds
        while monotonic() < deadline:
            if not self.error_queue.empty():
                raise RuntimeError(f"SSE listener failed: {self.error_queue.get()}")

            remaining = max(deadline - monotonic(), 0.0)
            try:
                return self.endpoint_queue.get(timeout=min(0.5, remaining))
            except queue.Empty:
                continue

        raise RuntimeError(f"Timed out waiting for SSE endpoint event after {timeout_seconds} seconds")

    def _wait_for_response(self, request_id: int, timeout_seconds: float) -> dict[str, Any]:
        """轮询消息队列并等待匹配请求 ID 的响应。

        参数:
            request_id: 请求 ID。
            timeout_seconds: 超时秒数。

        返回:
            dict[str, Any]: 匹配到的 JSON-RPC 响应。
        """
        deadline = monotonic() + timeout_seconds
        target_id = str(request_id)

        while monotonic() < deadline:
            if not self.error_queue.empty():
                raise RuntimeError(f"SSE listener failed: {self.error_queue.get()}")

            remaining = max(deadline - monotonic(), 0.0)
            try:
                message = self.message_queue.get(timeout=min(0.5, remaining))
            except queue.Empty:
                continue

            message_id = message.get("id")
            if message_id is None:
                continue
            if str(message_id) == target_id:
                return message

        raise RuntimeError(f"Timed out waiting for response id={request_id} after {timeout_seconds} seconds")


def call_intelligent_judgment_tool(
    client: McpSseClient,
    customer_name: str,
    age: int | None,
    behavior: str | None,
    viewed_issue_link_count: int | None,
    timeout_seconds: float,
) -> dict[str, Any]:
    """调用 intelligent_judgment 工具。

    参数:
        client: 销售场景 MCP 客户端。
        customer_name: 客户姓名。
        age: 客户年龄，可选。
        behavior: 客户行为，可选。
        viewed_issue_link_count: 出单链接查看次数，可选。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    arguments: dict[str, Any] = {"customer_name": customer_name}
    if age is not None:
        arguments["age"] = age
    if behavior:
        arguments["behavior"] = behavior
    if viewed_issue_link_count is not None:
        arguments["viewed_issue_link_count"] = viewed_issue_link_count
    return client.call_tool("intelligent_judgment", arguments, timeout_seconds)


def call_issue_policy_tool(
    client: McpSseClient,
    customer_name: str,
    age: int,
    gender: str,
    claim_count: int,
    reimbursed_diseases: list[str],
    timeout_seconds: float,
) -> dict[str, Any]:
    """调用 issue_policy_tool 工具。

    参数:
        client: 销售场景 MCP 客户端。
        customer_name: 客户姓名。
        age: 客户年龄。
        gender: 客户性别。
        claim_count: 出险次数。
        reimbursed_diseases: 报销疾病列表。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    return client.call_tool(
        "issue_policy_tool",
        {
            "customer_name": customer_name,
            "age": age,
            "gender": gender,
            "claim_count": claim_count,
            "reimbursed_diseases": reimbursed_diseases,
        },
        timeout_seconds,
    )


def call_product_comparison_tool(
    client: McpSseClient,
    customer_name: str,
    viewed_products: list[str],
    timeout_seconds: float,
) -> dict[str, Any]:
    """调用 product_comparison_tool 工具。

    参数:
        client: 销售场景 MCP 客户端。
        customer_name: 客户姓名。
        viewed_products: 浏览产品列表。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    arguments: dict[str, Any] = {"customer_name": customer_name}
    if viewed_products:
        arguments["viewed_products"] = viewed_products
    return client.call_tool("product_comparison_tool", arguments, timeout_seconds)


def call_claim_case_tool(
    client: McpSseClient,
    customer_name: str,
    age: int,
    reimbursed_diseases: list[str],
    timeout_seconds: float,
) -> dict[str, Any]:
    """调用 claim_case_tool 工具。

    参数:
        client: 销售场景 MCP 客户端。
        customer_name: 客户姓名。
        age: 客户年龄。
        reimbursed_diseases: 报销疾病列表。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    return client.call_tool(
        "claim_case_tool",
        {
            "customer_name": customer_name,
            "age": age,
            "reimbursed_diseases": reimbursed_diseases,
        },
        timeout_seconds,
    )


def call_personal_needs_analysis_tool(
    client: McpSseClient,
    customer_name: str,
    age: int,
    annual_income: int,
    family_structure: str,
    existing_insurance_budget: int,
    timeout_seconds: float,
) -> dict[str, Any]:
    """调用 personal_needs_analysis_tool 工具。

    参数:
        client: 销售场景 MCP 客户端。
        customer_name: 客户姓名。
        age: 客户年龄。
        annual_income: 年收入。
        family_structure: 家庭结构。
        existing_insurance_budget: 已有保险预算。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    return client.call_tool(
        "personal_needs_analysis_tool",
        {
            "customer_name": customer_name,
            "age": age,
            "annual_income": annual_income,
            "family_structure": family_structure,
            "existing_insurance_budget": existing_insurance_budget,
        },
        timeout_seconds,
    )


def call_product_knowledge_share_tool(
    client: McpSseClient,
    customer_name: str,
    consulted_products: list[str],
    timeout_seconds: float,
) -> dict[str, Any]:
    """调用 product_knowledge_share_tool 工具。

    参数:
        client: 销售场景 MCP 客户端。
        customer_name: 客户姓名。
        consulted_products: 咨询产品列表。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    arguments: dict[str, Any] = {"customer_name": customer_name}
    if consulted_products:
        arguments["consulted_products"] = consulted_products
    return client.call_tool("product_knowledge_share_tool", arguments, timeout_seconds)


def call_agent_ai_business_card_tool(
    client: McpSseClient,
    timeout_seconds: float,
) -> dict[str, Any]:
    """调用 agent_ai_business_card_tool 工具。

    参数:
        client: 销售场景 MCP 客户端。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    return client.call_tool("agent_ai_business_card_tool", {}, timeout_seconds)


def call_periodic_care_tool(
    client: McpSseClient,
    customer_name: str,
    city: str | None,
    upcoming_event: str | None,
    timeout_seconds: float,
) -> dict[str, Any]:
    """调用 periodic_care_tool 工具。

    参数:
        client: 销售场景 MCP 客户端。
        customer_name: 客户姓名。
        city: 城市信息，可选。
        upcoming_event: 节日信息，可选。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    arguments: dict[str, Any] = {"customer_name": customer_name}
    if city:
        arguments["city"] = city
    if upcoming_event:
        arguments["upcoming_event"] = upcoming_event
    return client.call_tool("periodic_care_tool", arguments, timeout_seconds)


def call_countdown_tool(
    monitor_client: McpSseClient,
    intent_level: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    """根据意向等级调用倒计时监控工具。

    参数:
        monitor_client: 倒计时监控 MCP 客户端。
        intent_level: 意向等级。
        timeout_seconds: 等待超时秒数。

    返回:
        dict[str, Any]: JSON-RPC 响应。
    """
    policy = INTENT_COUNTDOWN_POLICY[intent_level]
    return monitor_client.call_tool(
        "diagnose_stuck_point",
        {
            "tool_name": policy["tool_name"],
            "countdown_seconds": policy["countdown_seconds"],
            "timeout_script": policy["timeout_script"],
        },
        timeout_seconds,
    )


def format_tool_record(tool_name: str, raw_response: dict[str, Any]) -> dict[str, Any]:
    """把工具调用结果格式化为统一输出记录。

    参数:
        tool_name: 工具名。
        raw_response: JSON-RPC 原始响应。

    返回:
        dict[str, Any]: 包含工具名、structuredContent 和原始响应。
    """
    return {
        "tool_name": tool_name,
        "structured_content": extract_structured_content(raw_response),
        "raw_response": raw_response,
    }


def run_sales_workflow(args: argparse.Namespace) -> dict[str, Any]:
    """执行万销销售场景完整流程。

    参数:
        args: 命令行参数对象。

    返回:
        dict[str, Any]: 全流程输出，包含意向判断、分流工具和倒计时结果。
    """
    reimbursed_diseases = parse_csv_list(args.reimbursed_diseases)
    viewed_products = parse_csv_list(args.viewed_products)
    consulted_products = parse_csv_list(args.consulted_products)

    sales_client = McpSseClient(
        base_url=args.sales_base_url,
        protocol_version=args.protocol_version,
        connect_timeout=args.connect_timeout,
        socket_timeout=args.tool_timeout + 30,
    )
    monitor_client = McpSseClient(
        base_url=args.monitor_base_url,
        protocol_version=args.protocol_version,
        connect_timeout=args.connect_timeout,
        socket_timeout=args.tool_timeout + 30,
    )

    monitor_initialize: dict[str, Any] | None = None
    route_records: list[dict[str, Any]] = []

    try:
        sales_initialize = sales_client.connect()

        intelligent_response = call_intelligent_judgment_tool(
            sales_client,
            customer_name=args.customer_name,
            age=args.age,
            behavior=args.behavior,
            viewed_issue_link_count=args.viewed_issue_link_count,
            timeout_seconds=args.tool_timeout,
        )
        intelligent_structured = extract_structured_content(intelligent_response)
        intelligent_data = intelligent_structured.get("data") if isinstance(intelligent_structured, dict) else {}
        if not isinstance(intelligent_data, dict):
            intelligent_data = {}

        if intelligent_structured.get("status") == "error":
            raise RuntimeError(str(intelligent_structured.get("message", "intelligent_judgment 调用失败")))

        intent_level = intelligent_data.get("intent_level")

        if intent_level not in INTENT_COUNTDOWN_POLICY:
            raise RuntimeError(f"无法识别意向等级: {intent_level}")

        age_for_route = args.age if args.age is not None else int(intelligent_data.get("age", 30))

        if intent_level == "高意向":
            issue_response = call_issue_policy_tool(
                sales_client,
                customer_name=args.customer_name,
                age=age_for_route,
                gender=args.gender,
                claim_count=args.claim_count,
                reimbursed_diseases=reimbursed_diseases,
                timeout_seconds=args.tool_timeout,
            )
            route_records.append(format_tool_record("issue_policy_tool", issue_response))

        elif intent_level == "中意向":
            if args.include_product_comparison:
                comparison_response = call_product_comparison_tool(
                    sales_client,
                    customer_name=args.customer_name,
                    viewed_products=viewed_products,
                    timeout_seconds=args.tool_timeout,
                )
                route_records.append(format_tool_record("product_comparison_tool", comparison_response))

            claim_response = call_claim_case_tool(
                sales_client,
                customer_name=args.customer_name,
                age=age_for_route,
                reimbursed_diseases=reimbursed_diseases,
                timeout_seconds=args.tool_timeout,
            )
            route_records.append(format_tool_record("claim_case_tool", claim_response))

            needs_response = call_personal_needs_analysis_tool(
                sales_client,
                customer_name=args.customer_name,
                age=age_for_route,
                annual_income=args.annual_income,
                family_structure=args.family_structure,
                existing_insurance_budget=args.existing_insurance_budget,
                timeout_seconds=args.tool_timeout,
            )
            route_records.append(format_tool_record("personal_needs_analysis_tool", needs_response))

        elif intent_level == "低意向":
            knowledge_response = call_product_knowledge_share_tool(
                sales_client,
                customer_name=args.customer_name,
                consulted_products=consulted_products,
                timeout_seconds=args.tool_timeout,
            )
            route_records.append(format_tool_record("product_knowledge_share_tool", knowledge_response))

            if args.include_agent_card:
                card_response = call_agent_ai_business_card_tool(sales_client, timeout_seconds=args.tool_timeout)
                route_records.append(format_tool_record("agent_ai_business_card_tool", card_response))

            care_response = call_periodic_care_tool(
                sales_client,
                customer_name=args.customer_name,
                city=args.city,
                upcoming_event=args.upcoming_event,
                timeout_seconds=args.tool_timeout,
            )
            route_records.append(format_tool_record("periodic_care_tool", care_response))

        if args.skip_countdown:
            countdown_record = {
                "status": "skipped",
                "reason": "skip_countdown=true",
                "policy": INTENT_COUNTDOWN_POLICY[intent_level],
            }
        else:
            monitor_initialize = monitor_client.connect()
            countdown_response = call_countdown_tool(
                monitor_client,
                intent_level=intent_level,
                timeout_seconds=max(args.tool_timeout, 30),
            )
            countdown_record = {
                "tool_name": "diagnose_stuck_point",
                "structured_content": extract_structured_content(countdown_response),
                "raw_response": countdown_response,
            }

        return {
            "status": "success",
            "customer_name": args.customer_name,
            "intent_level": intent_level,
            "sales_initialize": sales_initialize,
            "monitor_initialize": monitor_initialize,
            "intelligent_judgment": {
                "tool_name": "intelligent_judgment",
                "structured_content": intelligent_structured,
                "raw_response": intelligent_response,
            },
            "route_tools": route_records,
            "countdown": countdown_record,
        }
    finally:
        sales_client.close()
        monitor_client.close()


def main() -> None:
    """终端入口函数，打印流程执行结果。

    参数:
        无。

    返回:
        None: 输出 JSON 并按状态码退出。
    """
    args = parse_args()
    try:
        result = run_sales_workflow(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as error:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": str(error),
                    "customer_name": args.customer_name,
                    "sales_base_url": args.sales_base_url,
                    "monitor_base_url": args.monitor_base_url,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
