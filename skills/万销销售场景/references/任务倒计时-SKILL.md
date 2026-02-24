---
name: task-countdown-mcp
description: 任务倒计时与超时话术触发技能。用于用户要求按“工具名称 + 倒计时秒数 + 倒计时结束话术”调用销售倒计时 MCP 工具时；通过脚本建立 SSE 会话、发送 initialize 和 tools/call、并持续轮询事件流直到拿到工具结果。适用于演示倒计时监控、超时提醒和话术触发。
---

# 任务倒计时（MCP SSE 调用与结果轮询）

本 Skill 用于把 `tool_name`、`countdown_seconds`、`timeout_script` 作为入参，调用 `diagnose_stuck_point`，并轮询 MCP SSE 事件流拿回最终结果。

## Common Workflow

1. 从用户消息中提取三个核心参数：`tool_name`、`countdown_seconds`、`timeout_script`。
2. 校验参数：`countdown_seconds` 必须为正整数，话术不能为空。
3. 在终端执行脚本 `scripts/call_countdown_mcp.py` 发起调用。
4. 脚本自动完成：SSE 建连 -> initialize -> notifications/initialized -> tools/call。
5. 脚本持续轮询事件流，直到拿到指定请求 ID 的结果并输出 JSON。

## 绑定脚本与接口

- 脚本：`scripts/call_countdown_mcp.py`
- MCP 工具：`diagnose_stuck_point`
- 必填入参：
  - `tool_name`：被监控工具名（例如 `出单工具`）
  - `countdown_seconds`：倒计时秒数（正整数）
  - `timeout_script`：倒计时结束后触发的话术
- 默认连接地址：`http://127.0.0.1:8765`
- 默认协议版本：`2025-03-26`

### Basic Usage

If running deepagents from a virtual environment:
```bash
.venv/bin/python ./skills/任务倒计时/scripts/call_countdown_mcp.py "出单工具" 10 "您已经停留一段时间了，是否需要帮您解释保单的内容？"
```

如果直接使用系统 Python：
```bash
python ./skills/任务倒计时/scripts/call_countdown_mcp.py "出单工具" 10 "您已经停留一段时间了，是否需要帮您解释保单的内容？"
```

指定服务地址与轮询超时：
```bash
python ./skills/任务倒计时/scripts/call_countdown_mcp.py "出单工具" 10 "您已经停留一段时间了，是否需要帮您解释保单的内容？" --base-url "http://127.0.0.1:8765" --poll-timeout 45
```

## 调用规则（强约束）

1. 必须先确认服务已启动并可访问 `/sse`。
2. 必须走脚本，不要手动省略 initialize 流程。
3. 必须等待轮询结果返回后再向用户汇报，不可在倒计时过程中提前结束。
4. 如果脚本返回 `error`，要原样反馈失败原因并给出修复方向（地址、端口、服务状态、参数格式）。

## 不要做的事

- 不要把 `countdown_seconds` 传成非整数或小于等于 0。
- 不要遗漏 `timeout_script`，否则失去演示意义。
- 不要在同一步骤混用不一致的 `base_url`（例如建连和调用地址不同）。
- 不要把本技能用于产品推荐/出单本身，它只负责倒计时工具调用与结果回收。

## 输出规范

- 成功时返回脚本输出 JSON 中的核心字段：`status`、`trigger_action`、`timeout_script`、`elapsed_seconds`。
- 若存在 `structuredContent`，优先使用其中字段对外展示。
- 若失败，返回 `error` 内容并附上已使用的 `base_url` 以便排查。
