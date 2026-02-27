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
- **中意向**：调用 `claim_case_tool` 与 `issue_policy_tool`。
- **低意向**：调用 `agent_ai_business_card_tool` 与 `periodic_care_tool`。


## 绑定mcp工具

- 编排脚本：`scripts/run_wanxiao_sales_flow.py`
- 涉及 MCP 工具：
  - `intelligent_judgment`（智能意向判断）
  - `issue_policy_tool`（出单工具）
  - `product_comparison_tool`（产品对比工具）
  - `claim_case_tool`（理赔案例工具）
  - `personal_needs_analysis_tool`（个人需求分析工具）
  - `product_knowledge_share_tool`（产品知识分享工具）
  - `agent_ai_business_card_tool`（代理人AI名片工具）
  - `periodic_care_tool`（定期关怀工具）

### Basic Usage (沙箱环境)

沙箱环境中 skills 目录位于 `/home/daytona/skills/`，执行脚本时请务必使用该路径：

```bash
# 智能判断客户意向
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py intelligent_judgment --customer-name "张三" 

# 出单工具
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py issue_policy_tool --customer-name "张三" 

# 产品对比
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py product_comparison_tool --customer-name "张三" 

# 理赔案例
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py claim_case_tool --customer-name "张三" 

# 个人需求分析
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py personal_needs_analysis_tool --customer-name "张三" 

# 产品知识分享
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py product_knowledge_share_tool --customer-name "张三" 

# 代理人AI名片
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py agent_ai_business_card_tool --agent-name "金牌顾问小安" --specialty "医疗险+重疾险组合规划" 

# 定期关怀
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py periodic_care_tool --customer-name "张三" 

# 深度引导工具
python /home/daytona/skills/万销销售场景/scripts/sales_cli.py deep_guidance_tools --customer-name "张三" 
```



## 调用规则（强约束）

1. 必须先调用 `intelligent_judgment`，再按意向分流。

## 不要做的事

- 不要跳过意向判断直接调用出单/培育工具。


## 输出规范

- 每个工具结果优先使用 `structuredContent`。
- 失败时返回 `status=error` 与明确错误信息（连接失败、参数缺失、调用超时）。
- `intelligent_judgment`工具的结果不需要输出,只需要说明客户为高/中/低意向。

### 按工具结果的输出要求

#### `issue_policy_tool`（出单工具）
必须以下列表格格式输出：

| 项目 | 内容 |
|------|------|
| 月保费 | ¥{monthly_premium} |
| 年保费 | ¥{annual_premium} |
| 客户年龄 | {input_features.age} |
| 客户性别 | {input_features.gender} |
| 历史理赔次数 | {input_features.claim_count} |

#### `product_comparison_tool`（产品对比工具）
必须以下列表格格式输出：

| 产品名称 | 类型 | 价格档位 | 保额上限 | 等待期 | 核心亮点 | 注意事项 |
|---------|------|---------|---------|--------|---------|---------|
| {comparison_table[0].product} | {comparison_table[0].type} | {comparison_table[0].price_band} | {comparison_table[0].coverage_limit} | {comparison_table[0].waiting_period} | {comparison_table[0].highlights} | {comparison_table[0].limitations} |
| {comparison_table[1].product} | ... | ... | ... | ... | ... | ... |

#### `claim_case_tool`（理赔案例工具）
必须以下列表格格式输出：

| 案例ID | 疾病 | 匹配产品 | 理赔金额 | 审批天数 | 关键要点 |
|--------|------|---------|---------|---------|---------|
| {cases[0].case_id} | {cases[0].disease} | {cases[0].matched_product} | ¥{cases[0].claim_amount} | {cases[0].approval_days}天 | {cases[0].key_point} |
| {cases[1].case_id} | ... | ... | ... | ... | ... |

#### `personal_needs_analysis_tool`（个人需求分析工具）
必须以下列表格格式输出：

| 项目 | 内容 |
|------|------|
| 年收入 | ¥{analysis.annual_income} |
| 家庭结构 | {analysis.family_structure} |
| 客户年龄 | {analysis.age} |
| 推荐年预算 | ¥{analysis.recommended_annual_budget} |
| 推荐月预算 | ¥{analysis.recommended_monthly_budget} |
| 保障重点 | {analysis.demand_focus} |

**保障组合建议**：

| 产品 | 配置比例 | 预估预算 | 保障范围 |
|------|---------|---------|---------|
| {analysis.recommended_portfolio[0].product} | {analysis.recommended_portfolio[0].allocation_ratio} | ¥{analysis.recommended_portfolio[0].estimated_budget} | {analysis.recommended_portfolio[0].coverage_scope} |
| {analysis.recommended_portfolio[1].product} | ... | ... | ... |

#### `product_knowledge_share_tool`（产品知识分享工具）
必须以下列表格格式输出：

**知识卡片**：

| 产品 | 可保疾病 | 赔付范围 | 保额上限 | 简单解释 |
|------|---------|---------|---------|---------|
| {knowledge_cards[0].product} | {knowledge_cards[0].insurable_diseases} | {knowledge_cards[0].payout_scope} | {knowledge_cards[0].coverage_limit} | {knowledge_cards[0].easy_explain} |
| {knowledge_cards[1].product} | ... | ... | ... | ... |

**分享素材**：
- 文章标题：{share_material.article_title}
- 海报链接：{share_material.poster_url}

#### `agent_ai_business_card_tool`（代理人AI名片工具）
必须以下列表格格式输出：

| 项目 | 内容 |
|------|------|
| 职称 | {card.title} |
| 专业领域 | {card.specialty} |
| 服务标签 | {card.service_tags} |
| 分享链接 | {card.share_link} |

#### `periodic_care_tool`（定期关怀工具）
必须以下列表格格式输出：

| 项目 | 内容 |
|------|------|
| 城市 | {city} |
| 节日/事件 | {event} |
| 关怀话术 | {care_message} |
| 关联产品 | {linked_products} |
| 下次触达建议 | {schedule_suggestion.next_touchpoint} |
| 触达渠道 | {schedule_suggestion.channel} |


