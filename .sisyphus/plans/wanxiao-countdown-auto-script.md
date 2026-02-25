# 万销销售场景倒计时自动话术展示实现计划

## TL;DR

> **目标**: 实现销售场景展示工具结果后自动启动10秒倒计时，倒计时结束后如果用户未点击，自动展示对应话术。
>
> **实现方式**: 修改 `diagnose_stuck_point` MCP 工具支持异步非阻塞模式，添加状态查询接口，前端轮询获取倒计时状态并在完成后展示话术。
>
> **核心改动**:
> - `sales_monitor_mcp.py`: 新增 `start_countdown` 和 `get_countdown_status` 工具
> - `SKILL.md`: 更新倒计时调用流程说明
> - `frontend/script.js`: 添加倒计时状态轮询和话术展示逻辑
>
> **并行度**: Wave 1 → Wave 2 → Wave 3（部分可并行）
> **预估工作量**: 中等（Medium）

---

## Context

### 原始需求
用户在万销销售场景中，需要实现以下功能：
1. 根据客户意向调用对应工具（出单、理赔案例、知识分享等）
2. 展示工具结果后，**立即启动10秒倒计时**
3. 倒计时期间静默进行（无需视觉提示）
4. 倒计时结束后，如果用户没有点击，**自动展示对应话术**

### 当前现状分析

**现有实现** (`sales_monitor_mcp.py`):
```python
async def diagnose_stuck_point(
    tool_name: str,
    countdown_seconds: int,
    timeout_script: str,
    ...
):
    # 同步等待，阻塞直到倒计时结束
    while elapsed_seconds < countdown_seconds:
        await asyncio.sleep(sleep_for)
    return {...}
```

**问题**:
1. `diagnose_stuck_point` 是**同步阻塞**的，会占用整个请求直到10秒结束
2. 前端在等待期间无法做其他操作
3. 无法实现"展示工具结果后再等待10秒"的流程

**用户选择的技术方案**:
- 后端控制倒计时
- 通过**前端轮询**查询倒计时状态
- 倒计时**静默进行**（无视觉提示）
- 修改 `diagnose_stuck_point` 工具

---

## Work Objectives

### Core Objective
将现有的同步阻塞式倒计时改造为**异步非阻塞模式**，支持前端轮询查询状态，并在倒计时完成后展示话术。

### Concrete Deliverables
1. **后端**: `sales_monitor_mcp.py` 新增 `start_countdown` 和 `get_countdown_status` 工具
2. **后端**: 倒计时任务存储（支持查询状态）
3. **文档**: 更新 `skills/万销销售场景/SKILL.md` 倒计时调用流程
4. **前端**: `frontend/script.js` 添加轮询逻辑和话术展示
5. **整合**: 销售流程端到端测试通过

### Definition of Done
- [ ] 调用 `start_countdown` 后立即可返回，不阻塞
- [ ] 前端可以通过轮询 `get_countdown_status` 查询倒计时状态
- [ ] 倒计时结束后，话术自动展示在聊天窗口
- [ ] 高/中/低意向客户对应不同的话术（按SKILL.md定义）
- [ ] 端到端流程完整测试通过

### Must Have
- [x] 异步非阻塞倒计时启动
- [x] 倒计时状态可查询
- [x] 话术按意向等级区分（高/中/低）
- [x] 前端自动轮询机制
- [x] 向后兼容（不破坏现有 `diagnose_stuck_point`）

### Must NOT Have (Guardrails)
- 不使用 WebSocket（使用轮询方式）
- 倒计时期间不添加视觉提示（静默进行）
- 不引入外部存储（Redis等），使用内存存储

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO（无测试框架）
- **Automated tests**: NO
- **Agent-Executed QA**: YES（主要验证手段）

### QA Policy
所有任务必须通过Agent-Executed QA验证，证据保存到 `.sisyphus/evidence/`。

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (后端核心 - 可立即启动):
├── Task 1: sales_monitor_mcp.py 新增 start_countdown 工具 [quick]
├── Task 2: sales_monitor_mcp.py 新增 get_countdown_status 工具 [quick]
└── Task 3: 倒计时状态存储与管理（内存字典） [quick]

Wave 2 (文档与前端):
├── Task 4: 更新 skills/万销销售场景/SKILL.md 倒计时调用流程 [unspecified-low]
├── Task 5: frontend/script.js 添加倒计时启动和轮询逻辑 [unspecified-high]
└── Task 6: frontend/script.js 添加话术展示逻辑 [quick]

Wave 3 (整合测试 - 顺序执行):
├── Task 7: 启动销售MCP服务和监控MCP服务 [quick]
├── Task 8: 端到端测试：高意向客户流程 [unspecified-high]
├── Task 9: 端到端测试：中/低意向客户流程 [unspecified-high]
└── Task 10: 验证向后兼容性（diagnose_stuck_point） [quick]
```

### Dependency Matrix
- **1-3**: — — 4, 5, 6, 1
- **4**: — — 7, 2
- **5-6**: — — 7, 2
- **7**: 1-6 — 8, 9, 10, 3
- **8-10**: 7 — 完成, 4

### Agent Dispatch Summary
- **Wave 1**: 3 tasks → `quick` (T1), `quick` (T2), `quick` (T3)
- **Wave 2**: 3 tasks → `unspecified-low` (T4), `unspecified-high` (T5), `quick` (T6)
- **Wave 3**: 4 tasks → `quick` (T7), `unspecified-high` (T8, T9), `quick` (T10)

---

## TODOs



### Wave 1: 后端 MCP 改造

#### Task 1: sales_monitor_mcp.py 新增内存存储结构
**Scope**: `mcp_tool/sales_monitor_mcp.py`

**Goal**: 添加全局内存存储，用于管理倒计时任务状态。

**Implementation Notes**:
- 添加全局字典 `_countdown_tasks: dict[str, dict]`
- 每个 task 存储: `task_id`, `tool_name`, `countdown_seconds`, `timeout_script`, `started_at`, `status` (running/completed/cancelled), `elapsed_seconds`
- 使用 `asyncio.Lock` 保护并发访问

**Acceptance Criteria**:
- [ ] 字典结构定义清晰，包含所有必要字段
- [ ] 有线程/协程安全保护

---

#### Task 2: sales_monitor_mcp.py 新增 start_countdown_async 工具
**Scope**: `mcp_tool/sales_monitor_mcp.py`

**Goal**: 创建非阻塞倒计时启动工具，立即返回 task_id。

**Implementation Notes**:
```python
@mcp.tool()
async def start_countdown_async(
    tool_name: str,
    countdown_seconds: int,
    timeout_script: str,
    tick_seconds: int = 1,
) -> dict[str, Any]:
    # 生成 task_id (uuid)
    # 创建后台 asyncio.Task 执行倒计时
    # 立即返回 {"task_id": "...", "status": "started", ...}
```
- 倒计时完成后更新 `_countdown_tasks[task_id]["status"]` = "completed"
- 同时存储 `result` 包含 `timeout_script`

**Acceptance Criteria**:
- [ ] 调用后立即返回，不阻塞
- [ ] 返回包含 task_id
- [ ] 后台任务正确执行倒计时

---

#### Task 3: sales_monitor_mcp.py 新增 get_countdown_status 工具
**Scope**: `mcp_tool/sales_monitor_mcp.py`

**Goal**: 创建倒计时状态查询工具。

**Implementation Notes**:
```python
@mcp.tool()
async def get_countdown_status(task_id: str) -> dict[str, Any]:
    # 从 _countdown_tasks 查询
    # 返回 {"task_id": "...", "status": "running|completed|not_found", 
    #       "elapsed_seconds": ..., "remaining_seconds": ..., 
    #       "timeout_script": ...} (如果已完成)
```

**Acceptance Criteria**:
- [ ] 能正确查询到 running 状态
- [ ] 倒计时结束后返回 completed 和 timeout_script
- [ ] task_id 不存在返回 not_found

---

### Wave 2: 后端 API 与文档

#### Task 4: main.py 新增 /api/countdown/{task_id} 查询接口
**Scope**: `main.py` (FastAPI app)

**Goal**: 提供主站 API 供前端查询倒计时状态。

**Implementation Notes**:
由于前端不直接连接 MCP，主站需要代理或复用存储逻辑。

**方案 A（推荐）**: 主站直接查询 MCP
```python
@app.get("/api/countdown/{task_id}")
async def get_countdown_status_api(task_id: str) -> dict[str, Any]:
    # 通过 MCP SSE 调用 get_countdown_status
    # 或直接 HTTP 调用（如果 MCP 暴露了 HTTP API）
```

**方案 B**: 主站维护倒计时存储
- MCP 只负责启动倒计时
- 主站维护 `_countdown_tasks` 字典
- 前端只查询主站

**Acceptance Criteria**:
- [ ] API 返回正确的倒计时状态
- [ ] 支持 CORS（同域不需要额外配置）
- [ ] 有适当的错误处理

---

#### Task 5: 更新 skills/万销销售场景/SKILL.md 倒计时流程
**Scope**: `skills/万销销售场景/SKILL.md`

**Goal**: 更新文档，描述新的异步倒计时调用流程。

**Implementation Notes**:
- 在 "工作流" 步骤 4 中更新倒计时调用说明
- 新增说明：调用 `start_countdown_async` 获取 task_id
- 新增说明：前端通过 `/api/countdown/{task_id}` 轮询状态
- 更新话术映射（高/中/低意向）

**Acceptance Criteria**:
- [ ] 文档描述与实际代码一致
- [ ] 包含新的 API 调用示例
- [ ] 清晰说明前端轮询流程

---

### Wave 3: 前端实现

#### Task 6: frontend/script.js 新增倒计时状态管理
**Scope**: `frontend/script.js`

**Goal**: 在 ChatApp 类中添加倒计时相关状态和方法。

**Implementation Notes**:
```javascript
class ChatApp {
  constructor() {
    // ... existing code ...
    this.activeCountdowns = new Map(); // task_id -> {status, script, timer}
  }
  
  startCountdown(taskId, timeoutScript) {
    // 存储到 activeCountdowns
    // 启动轮询
  }
  
  cancelCountdown(taskId) {
    // 取消轮询，从 activeCountdowns 删除
  }
}
```

**Acceptance Criteria**:
- [ ] 有状态存储结构
- [ ] 能正确启动和取消倒计时

---

#### Task 7: frontend/script.js 新增轮询逻辑
**Scope**: `frontend/script.js`

**Goal**: 实现轮询 `/api/countdown/{task_id}` 获取状态。

**Implementation Notes**:
```javascript
async function pollCountdown(taskId, timeoutScript) {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/countdown/${taskId}`);
    const data = await response.json();
    
    if (data.status === 'completed') {
      clearInterval(interval);
      showTimeoutScript(data.timeout_script);
    } else if (data.status === 'not_found') {
      clearInterval(interval);
    }
  }, 1000); // 每秒轮询
}
```

**Acceptance Criteria**:
- [ ] 每秒轮询一次
- [ ] 倒计时完成后停止轮询
- [ ] 有错误处理（如 404）

---

#### Task 8: frontend/script.js 新增话术展示逻辑
**Scope**: `frontend/script.js`

**Goal**: 倒计时完成后以 assistant 消息形式展示话术。

**Implementation Notes**:
```javascript
showTimeoutScript(script) {
  // 创建 assistant 消息气泡
  // 显示话术内容
  // 添加到聊天记录
}
```

**Acceptance Criteria**:
- [ ] 话术以 assistant 消息展示
- [ ] 样式与正常回复一致
- [ ] 用户发送新消息可中断/忽略话术

---

### Wave 4: 整合测试

#### Task 9: 启动销售MCP服务和监控MCP服务
**Scope**: 终端命令

**Goal**: 确保所有服务正常运行。

**Implementation Notes**:
```bash
# 终端 1: 启动销售 MCP 服务（端口 8000）
uv run python mcp_tool/sales_mcp_mock.py --port 8000

# 终端 2: 启动监控 MCP 服务（端口 8765）
uv run python mcp_tool/sales_monitor_mcp.py --port 8765

# 终端 3: 启动主服务（端口 7860）
uv run python main.py
```

**Acceptance Criteria**:
- [ ] 所有服务正常启动，无报错
- [ ] 服务间网络连通

---

#### Task 10: 端到端测试 - 高意向客户流程
**Scope**: 完整流程

**Goal**: 验证高意向客户的倒计时和话术展示。

**Test Scenario**:
1. 用户选择高意向客户（如张三）
2. Agent 调用 `intelligent_judgment` 返回高意向
3. Agent 调用 `issue_policy_tool` 展示出单结果
4. Agent 调用 `start_countdown_async`（10秒，话术："您已经停留一段时间了，是否需要帮您解释保单的内容？"）
5. 前端轮询状态
6. 10秒后自动展示话术

**Acceptance Criteria**:
- [ ] 工具结果正常展示
- [ ] 倒计时正确启动
- [ ] 10秒后话术自动展示

---

#### Task 11: 端到端测试 - 中意向客户流程
**Scope**: 完整流程

**Goal**: 验证中意向客户的倒计时和话术展示。

**Test Scenario**:
- 话术："是否遇到理解困难？"
- 流程类似 Task 10

**Acceptance Criteria**:
- [ ] 话术正确展示

---

#### Task 12: 端到端测试 - 低意向客户流程
**Scope**: 完整流程

**Goal**: 验证低意向客户的倒计时和话术展示。

**Test Scenario**:
- 话术："内容是否符合您的要求？"
- 流程类似 Task 10

**Acceptance Criteria**:
- [ ] 话术正确展示

---

#### Task 13: 验证向后兼容性
**Scope**: `mcp_tool/sales_monitor_mcp.py`

**Goal**: 确保原 `diagnose_stuck_point` 工具仍然可用。

**Test Scenario**:
```bash
curl -N "http://127.0.0.1:8765/sse"
# ... 获取 session_id ...
curl -X POST ... -d '{"method":"tools/call","params":{"name":"diagnose_stuck_point",...}}'
```

**Acceptance Criteria**:
- [ ] 原工具仍能正常工作
- [ ] 返回值格式不变

---

## High-Level Architecture

### 数据流图

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Frontend  │────▶│  main.py     │────▶│ MCP Monitor     │
│  (script.js)│     │  FastAPI     │     │ (8765)          │
│             │◀────│  /api/chat   │     │                 │
│             │     │  /api/countdown│   │ start_countdown_│
│             │◀────│              │     │ async()         │
└─────────────┘     └──────────────┘     └─────────────────┘
       │                      │                    │
       │ 1. send message      │                    │
       │──────────────────────▶                    │
       │                      │                    │
       │ 2. SSE: tool result  │                    │
       │◀─────────────────────│                    │
       │                      │ 3. call MCP        │
       │                      │─────────────────────▶
       │                      │                    │
       │                      │ 4. return task_id  │
       │                      │◀─────────────────────
       │ 5. SSE: countdown    │                    │
       │    started (task_id) │                    │
       │◀─────────────────────│                    │
       │                      │                    │
       │ 6. poll /api/countdown/{task_id}
       │──────────────────────▶                    │
       │                      │ 7. query status    │
       │                      │─────────────────────▶
       │                      │                    │
       │                      │ 8. return status   │
       │                      │◀─────────────────────
       │                      │                    │
       │ 9. return status     │                    │
       │◀─────────────────────│                    │
       │                      │                    │
       │ ... (repeat 6-9) ... │                    │
       │                      │                    │
       │ 10. countdown        │                    │
       │     completed        │                    │
       │◀─────────────────────│                    │
       │                      │                    │
       │ 11. show timeout     │                    │
       │     script in chat   │                    │
       │                      │                    │
```

### 关键设计决策

**1. 状态存储位置**: 
- **方案**: 在 `sales_monitor_mcp.py` 中维护内存存储
- **理由**: 避免引入 Redis，符合用户选择；MCP 服务作为倒计时中心

**2. 前端轮询 vs WebSocket**:
- **方案**: 前端轮询 `/api/countdown/{task_id}`
- **理由**: 符合用户选择，实现简单

**3. 话术展示时机**:
- **方案**: 倒计时完成后以 assistant 消息展示
- **理由**: 与现有聊天界面一致，用户体验好

**4. 用户点击定义**:
- **方案**: 用户发送任何新消息视为"点击/交互"
- **理由**: 简化实现，语义清晰
- **实现**: 前端在发送新消息时取消所有活跃倒计时

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP 服务重启导致倒计时状态丢失 | 中 | 中 | 使用内存存储是设计选择；可接受状态丢失 |
| 前端轮询频率过高 | 低 | 低 | 设置 1 秒轮询间隔；合理 |
| 用户同时触发多个倒计时 | 中 | 低 | 前端管理多个 countdown，各自独立 |
| 话术重复展示 | 低 | 中 | 前端标记已展示的话术，避免重复 |

---

## Appendix

### 话术映射表（来自 SKILL.md）

| 意向等级 | 触发的工具 | 倒计时话术 |
|----------|-----------|-----------|
| 高意向 | `issue_policy_tool` | "您已经停留一段时间了，是否需要帮您解释保单的内容？" |
| 中意向 | `claim_case_tool` + `personal_needs_analysis_tool` | "是否遇到理解困难？" |
| 低意向 | `product_knowledge_share_tool` + `periodic_care_tool` | "内容是否符合您的要求？" |

### 相关文件

- `mcp_tool/sales_monitor_mcp.py` - 监控 MCP 服务，需新增工具
- `mcp_tool/sales_mcp_mock.py` - 销售 MCP 服务（不需要修改）
- `skills/万销销售场景/SKILL.md` - 技能文档，需更新
- `main.py` - 主 FastAPI 服务，需新增 API
- `frontend/script.js` - 前端逻辑，需新增倒计时处理

### 服务端口

- 主站: `http://127.0.0.1:7860`
- 销售 MCP: `http://127.0.0.1:8000`
- 监控 MCP: `http://127.0.0.1:8765`

---

*Plan created by Prometheus*
*Date: 2026-02-25*
