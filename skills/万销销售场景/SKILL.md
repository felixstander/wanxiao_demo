---
name: wanxiao-sales-scenario
description: 万销销售场景编排技能。用于代理人在前端点击客户后，按“智能判断、意向分流、工具执行、倒计时话术提醒”执行完整销售动作。会调用 SalesScenarioMockTools 的 intelligent_judgment、issue_policy_tool、claim_case_tool、personal_needs_analysis_tool、product_knowledge_share_tool、periodic_care_tool 等工具，并在末尾调用 SalesActivityMonitor 的 diagnose_stuck_point。适用于保险销售演示、客户意向分层和跟进话术触发。
---

# 万销销售场景（意向分流 + 工具编排 + 倒计时提醒）

本 Skill 用于执行销售指导手册：前端展示客户画像后，代理人点击客户，先判断意向，再按意向执行对应工具，并启动倒计时监控话术。

## Common Workflow

1. 从前端输入中提取客户信息：`customer_name`、`age`、`gender`、`behavior`。
2. 调用 `intelligent_judgment` 获取 `intent_level`。
3. 按意向分流调用工具：
   - 高意向：`issue_policy_tool`
   - 中意向：`claim_case_tool` + `personal_needs_analysis_tool`
   - 低意向：`product_knowledge_share_tool` + `periodic_care_tool`
4. 展示对应工具结果后，调用倒计时监控：`diagnose_stuck_point`。
5. 返回结构化结果，包含意向、工具结果、倒计时话术触发结果。

## 销售指导手册（执行规则）

### 前端输入

- 客户基础信息：姓名、年龄、性别、行为。

### 意向分流

- **高意向**：调用 `issue_policy_tool`。
- **中意向**：调用 `claim_case_tool` 与 `personal_needs_analysis_tool`。
- **低意向**：调用 `product_knowledge_share_tool` 与 `periodic_care_tool`。

### 倒计时策略

- **高意向**：10 秒，话术：`您已经停留一段时间了，是否需要帮您解释保单的内容？`
- **中意向**：10 秒，话术：`是否遇到理解困难？`
- **低意向**：10 秒，话术：`内容是否符合您的要求？`

## 绑定脚本与工具

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
  - `diagnose_stuck_point`
- 默认服务地址：
  - 销售场景服务：`http://127.0.0.1:8765`
  - 倒计时监控服务：`http://127.0.0.1:8766`

### Basic Usage

If running deepagents from a virtual environment:
```bash
.venv/bin/python ./skills/万销销售场景/scripts/run_wanxiao_sales_flow.py "张三" --age 35 --gender 男 --behavior "多次查看出单链接" --claim-count 1 --reimbursed-diseases "甲状腺结节" --family-structure "已婚一孩" --annual-income 280000 --sales-base-url "http://127.0.0.1:8765" --monitor-base-url "http://127.0.0.1:8766"
```

如果直接使用系统 Python：
```bash
python ./skills/万销销售场景/scripts/run_wanxiao_sales_flow.py "李四" --age 42 --gender 女 --behavior "浏览产品对比页" --claim-count 2 --reimbursed-diseases "乳腺结节,胆囊炎" --family-structure "已婚二孩" --annual-income 360000 --sales-base-url "http://127.0.0.1:8765" --monitor-base-url "http://127.0.0.1:8766"
```

低意向示例：
```bash
python ./skills/万销销售场景/scripts/run_wanxiao_sales_flow.py "王五" --age 28 --gender 男 --behavior "第一次点击咨询" --consulted-products "轻松医疗基础版" --city "南京" --sales-base-url "http://127.0.0.1:8765" --monitor-base-url "http://127.0.0.1:8766"
```

## 按需读取倒计时参考

- 当需要了解倒计时技能的完整调用规范时，读取：`references/任务倒计时-SKILL.md`
- 该参考文件来自“任务倒计时”技能，包含 SSE 建连、initialize、tools/call、轮询结果的细化流程。

## 调用规则（强约束）

1. 必须先调用 `intelligent_judgment`，再按意向分流。
2. 必须按手册执行倒计时策略，倒计时统一为 10 秒。
3. 需要监控结果时，必须调用 `diagnose_stuck_point`，不得只做本地等待。
4. 若某些字段缺失，优先使用前端提供值；缺失时再用脚本默认值。

## 不要做的事

- 不要跳过意向判断直接调用出单/培育工具。
- 不要把中意向与低意向的触发话术混用。
- 不要把 `sales-base-url` 与 `monitor-base-url` 写错为同一个不可用服务。

## 输出规范

- 输出必须包含：`intent_level`、`route_tools`、`countdown`。
- 每个工具结果优先使用 `structuredContent`。
- 失败时返回 `status=error` 与明确错误信息（连接失败、参数缺失、调用超时）。
