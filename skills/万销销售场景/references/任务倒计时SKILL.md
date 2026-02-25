---
name: task-countdown-mcp
description: 异步任务倒计时与超时话术触发技能。用于展示工具结果后启动倒计时，倒计时结束后自动展示话术。采用异步非阻塞模式，立即返回 task_id，前端通过轮询查询状态。
---

# 任务倒计时（异步非阻塞模式）

本 Skill 提供异步倒计时功能，用于在展示工具结果后启动倒计时监控，如果用户在倒计时期间没有交互，则自动展示对应话术。

## 核心特点

- **异步非阻塞**：调用后立即返回，不占用请求
- **前端轮询**：前端通过 HTTP 接口查询倒计时状态
- **自动话术展示**：倒计时结束后自动展示预设话术

## 涉及 MCP 工具

1. `start_countdown_async` - 启动异步倒计时
2. `get_countdown_status` - 查询倒计时状态

## 工具详情

### start_countdown_async

启动异步倒计时，立即返回 task_id，后台执行倒计时。

**入参：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tool_name | string | 是 | 被监控工具名（如 `issue_policy_tool`） |
| countdown_seconds | int | 是 | 倒计时秒数（建议 10 秒） |
| timeout_script | string | 是 | 倒计时结束后展示的话术 |

**返回值：**

```json
{
  "task_id": "uuid-string",
  "status": "started",
  "countdown_seconds": 10,
  "tool_name": "issue_policy_tool"
}
```

### get_countdown_status

查询倒计时任务状态。

**入参：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | string | 是 | 倒计时任务 ID |

**返回值 - running 状态：**

```json
{
  "status": "running",
  "task_id": "uuid-string",
  "elapsed_seconds": 3,
  "remaining_seconds": 7,
  "timeout_script": "话术内容"
}
```

**返回值 - completed 状态：**

```json
{
  "status": "completed",
  "task_id": "uuid-string",
  "timeout_script": "话术内容",
  "elapsed_seconds": 10
}
```

**返回值 - not_found：**

```json
{
  "status": "not_found",
  "task_id": "uuid-string"
}
```

## 使用流程

### 1. 启动倒计时

展示工具结果后，调用 `start_countdown_async`：

```bash
MESSAGE_URL="http://127.0.0.1:8765/messages/?session_id=xxxx"

curl -sS -X POST "$MESSAGE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":3,
    "method":"tools/call",
    "params":{
      "name":"start_countdown_async",
      "arguments":{
        "tool_name":"issue_policy_tool",
        "countdown_seconds":10,
        "timeout_script":"您已经停留一段时间了，是否需要帮您解释保单的内容？"
      }
    }
  }'
```

### 2. 前端接收 countdown_started 事件

主站 SSE 流会推送 `countdown_started` 事件：

```json
{
  "event": "countdown_started",
  "task_id": "uuid-string",
  "countdown_seconds": 10
}
```

### 3. 前端轮询查询状态

前端每秒轮询 `/api/countdown/{task_id}`：

```javascript
const interval = setInterval(async () => {
  const res = await fetch(`/api/countdown/${taskId}`);
  const data = await res.json();
  
  if (data.status === 'completed') {
    clearInterval(interval);
    showTimeoutScript(data.timeout_script);  // 展示话术
  }
}, 1000);
```

### 4. 倒计时完成，展示话术

倒计时结束后，前端以 assistant 消息形式展示 `timeout_script`。

### 5. 用户交互取消倒计时

用户发送新消息时，视为"点击/交互"，前端取消所有活跃倒计时。

## 完整调用示例（高意向客户）

```bash
# 1. 先建立 SSE 连接获取 session_id
curl -N "http://127.0.0.1:8765/sse"

# 2. 初始化 MCP 会话
MESSAGE_URL="http://127.0.0.1:8765/messages/?session_id=xxxx"

curl -sS -X POST "$MESSAGE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"initialize",
    "params":{
      "protocolVersion":"2025-03-26",
      "capabilities":{},
      "clientInfo":{"name":"countdown-client","version":"1.0.0"}
    }
  }'

curl -sS -X POST "$MESSAGE_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# 3. 调用 start_countdown_async 启动倒计时
curl -sS -X POST "$MESSAGE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"tools/call",
    "params":{
      "name":"start_countdown_async",
      "arguments":{
        "tool_name":"issue_policy_tool",
        "countdown_seconds":10,
        "timeout_script":"您已经停留一段时间了，是否需要帮您解释保单的内容？"
      }
    }
  }'

# 返回：{"task_id": "xxx", "status": "started", ...}

# 4. 查询倒计时状态
curl -sS "http://127.0.0.1:7860/api/countdown/{task_id}"

# 返回：{"status": "running", "elapsed_seconds": 3, ...}
# 或：{"status": "completed", "timeout_script": "..."}
```

## 服务地址

- MCP 服务：`http://127.0.0.1:8765`
- 主站代理接口：`http://127.0.0.1:7860/api/countdown/{task_id}`

## 调用规则（强约束）

1. 必须先调用业务工具展示结果，再启动倒计时。
2. `countdown_seconds` 必须为正整数。
3. `timeout_script` 不能为空，需根据业务场景预设。
4. 启动倒计时后，主站会通过 SSE 推送 `countdown_started` 事件给前端。
5. 前端负责轮询状态，倒计时结束后自动展示话术。

## 不要做的事

- 不要把 `countdown_seconds` 传成非整数或小于等于 0。
- 不要遗漏 `timeout_script`，否则倒计时完成后无内容可展示。
- 不要在前端轮询频率过高（建议每秒 1 次）。
- 不要把本技能用于产品推荐/出单本身，它只负责倒计时监控与话术触发。

## 输出规范

- 成功时返回核心字段：`task_id`、`status`、`countdown_seconds`。
- 倒计时完成后，前端展示 `timeout_script` 内容。
- 若失败，返回 `error` 内容并附上排查方向。
