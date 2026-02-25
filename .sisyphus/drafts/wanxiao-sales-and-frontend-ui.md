# Draft: 万销销售场景技能包完善 + 前端 UI 调整

## 需求澄清与范围界定

### 需求 A：销售场景技能包完善
**状态**: SKILL.md 已存在，但缺少 Python 脚本

已发现的文件结构：
```
skills/万销销售场景/
├── SKILL.md                              # 已存在（完整）
├── references/任务倒计时SKILL.md          # 已存在
└── scripts/                              # 缺少 .py 文件！
    └── __pycache__/                      # 只有缓存
```

需要创建的工具脚本（共 8 个 MCP 工具调用）：
1. `intelligent_judgment` - 智能判断工具
2. `issue_policy_tool` - 出单工具
3. `product_comparison_tool` - 产品对比工具
4. `claim_case_tool` - 理赔案例工具
5. `personal_needs_analysis_tool` - 个人需求分析工具
6. `product_knowledge_share_tool` - 知识分享工具
7. `agent_ai_business_card_tool` - 代理人 AI 名片工具
8. `periodic_care_tool` - 定期关怀工具

以及主流程脚本：
- `run_wanxiao_sales_flow.py` - 完整的销售流程编排

### 需求 B：前端 UI 调整（两个独立需求）
**状态**: 需要新建实现

1. **加载指示器**: 在 `sendMessage()` 等待响应期间显示三点动画，而不是空白
2. **右侧面板比例**: 思考过程面板 2/3，Skills 技能包面板 1/3

---

## 技术发现

### 技能包模式（基于任务倒计时脚本）
- 使用 `argparse` 接收命令行参数
- 使用 SSE (Server-Sent Events) 与 MCP 服务通信
- 流程：建立 SSE 连接 → initialize → notifications/initialized → tools/call → 轮询结果
- 使用 `urllib` 进行 HTTP 请求
- 使用 `threading` + `queue` 处理异步 SSE 事件

### 前端技术栈
- 纯 HTML + CSS + JavaScript（无框架）
- 关键文件：`frontend/index.html`, `frontend/style.css`, `frontend/script.js`
- 流式响应：通过 `/api/chat/stream` SSE 端点

---

## 待澄清问题

### 问题 1：服务地址确认
SKILL.md 中提到的服务地址：
- 销售场景服务：`http://127.0.0.1:8000`
- 倒计时监控服务：`http://127.0.0.1:8001`

但参考的任务倒计时脚本使用：`http://127.0.0.1:8765`

**需要确认**：这些 MCP 工具的实际服务地址是什么？

### 问题 2：工具参数详情
每个 MCP 工具的入参需要通过接口/函数获取。但具体有哪些参数？

例如 `intelligent_judgment` 需要：
- customer_name
- age
- gender
- behavior
- 还有其他的吗？

### 问题 3：前端 UI 调整优先级
这是两个独立的工作：
- 后端技能包开发（复杂，涉及 9 个脚本）
- 前端 UI 调整（相对简单）

**建议**：分成两个工作计划并行执行，还是按顺序执行？

---

## 范围边界

### 包含在销售场景技能包中：
- 8 个独立的 MCP 工具调用脚本
- 1 个主流程编排脚本
- 所有脚本遵循任务倒计时的 SSE/MCP 调用模式
- 每个脚本都有命令行参数支持

### 包含在前端 UI 调整中：
- `frontend/script.js`: 在等待响应时显示加载动画
- `frontend/style.css`: 三点动画样式 + 右侧面板 2:1 比例

### 不包含：
- 后端 API 修改
- 技能包本身的业务逻辑修改（SKILL.md 已存在且完整）
- 其他前端功能修改

---

## 建议的工作计划拆分

**方案 1：两个独立计划（推荐）**
- Plan A: 万销销售场景技能包脚本完善（9 个脚本）
- Plan B: 前端加载指示器 + 面板比例调整

**方案 2：合并为一个大计划**
- 如果两个需求都很紧急且没有依赖关系，可以合并

---

## 下一步行动

等待用户确认：
1. MCP 服务地址
2. 各工具的详细入参
3. 工作计划拆分方式（分开还是合并）
