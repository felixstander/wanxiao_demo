---
name: wanxiao-sales-scenario
description: 万销客户阶段判断与需求分析技能。用于代理人输入“客户姓名”后，判断该客户当前所处销售阶段（高意向/中意向/低意向）以及下一步最需要的支持内容（出单推进、培育解释、知识教育、定期关怀）。当用户的问题核心是“这个客户现在处于什么阶段、他现在最需要什么”时使用。
---

# 万销销售场景（意向分流 + 工具编排 + 倒计时提醒）

本 Skill 用于执行销售指导手册：前端展示客户画像后，代理人点击客户，先判断意向，再按意向执行对应工具，并启动倒计时监控话术。

## 工作流

1. 从前端输入中提取客户姓名。
2. 调用 `intelligent_judgment` 获取 `intent_level`。
3. 按意向分流调用工具。
4. 返回结构化结果，包含意向、工具结果。

## 销售指导手册（执行规则）

### 客户意向判断

- 通过客户姓名，调用 `intelligent_judgment `获取客户完整信息后，得到客户购买意向。

### 意向分流

- **高意向**：调用 `issue_policy_tool`。
- **中意向**：调用 `claim_case_tool` 与 `personal_needs_analysis_tool`。
- **低意向**：调用 `product_knowledge_share_tool` 与 `periodic_care_tool`。


## 绑定mcp工具

- 编排脚本：`scripts/run_wanxiao_sales_flow.py`
- 涉及 MCP 工具：
  - `intelligent_judgment`
  - `issue_policy_tool`
  - `product_comparison_tool`
  - `claim_case_tool`
  - `personal_needs_analysis_tool`
  - `product_knowledge_share_tool`
  - `agent_ai_business_card_tool`
  - `periodic_care_tool`

### Basic Usage (沙箱环境)

沙箱环境中 skills 目录位于 `/home/daytona/skills/`，执行脚本时请务必使用该路径：

```bash
# 智能判断客户意向
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py intelligent_judgment --customer-name "张三" --base-url "http://127.0.0.1:8000"

# 出单工具
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py issue_policy_tool --customer-name "张三" --base-url "http://127.0.0.1:8000"

# 产品对比
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py product_comparison_tool --customer-name "张三" --base-url "http://127.0.0.1:8000"

# 理赔案例
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py claim_case_tool --customer-name "张三" --base-url "http://127.0.0.1:8000"

# 个人需求分析
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py personal_needs_analysis_tool --customer-name "张三" --base-url "http://127.0.0.1:8000"

# 产品知识分享
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py product_knowledge_share_tool --customer-name "张三" --base-url "http://127.0.0.1:8000"

# 代理人AI名片
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py agent_ai_business_card_tool --agent-name "金牌顾问小安" --specialty "医疗险+重疾险组合规划" --base-url "http://127.0.0.1:8000"

# 定期关怀
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py periodic_care_tool --customer-name "张三" --base-url "http://127.0.0.1:8000"

# 深度引导工具
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py deep_guidance_tools --customer-name "张三" --base-url "http://127.0.0.1:8000"
```

也可通过环境变量设置 MCP 服务地址：

```bash
export MCP_BASE_URL="http://127.0.0.1:8000"
python /home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py intelligent_judgment --customer-name "王五"
```


## 调用规则（强约束）

1. 必须先调用 `intelligent_judgment`，再按意向分流。

## 不要做的事

- 不要跳过意向判断直接调用出单/培育工具。
- 不要把中意向与低意向的触发话术混用。

## 输出规范

- 每个工具结果优先使用 `structuredContent`。
- 失败时返回 `status=error` 与明确错误信息（连接失败、参数缺失、调用超时）。

### 按意向分层的输出要求

#### 高意向（`issue_policy_tool`）
输出应聚焦促成转化：
- **保费金额**：明确展示 `annual_premium` / `monthly_premium`
- **行动催促**：加入紧迫感话术（如"限时优惠"、"早投保早保障"）
- **简化决策**：突出核心保障与一键投保入口

#### 中意向（`claim_case_tool`、`personal_needs_analysis_tool`）
输出应侧重价值论证：
- **分析结果**：清晰呈现需求分析结论、匹配案例数量
- **亮点内容**：强调产品 `highlights`、理赔速度、保障范围优势
- **对比优势**：如有产品对比，突出差异化价值点

#### 低意向（`product_knowledge_share_tool`、`periodic_care_tool`）
输出应采用教育+关怀策略：
- **知识科普**：解释保险概念、条款含义、常见误区
- **关怀形式**：结合节日/天气等场景给出温馨提示
- **软性引导**：不直接推销，而是建立信任与专业形象
- **留资钩子**：提供后续咨询入口，保持长期触达可能

