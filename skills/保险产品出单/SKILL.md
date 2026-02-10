---
name: insurance-issuance
description: 保险产品出单/保费试算与投保信息生成。当用户已明确“就买这款/帮我出单/投保/算保费”，并指向某个具体产品且提供投保人年龄与性别时使用；调用 insurance_get_quote 计算最终保费并返回出单结果（含保单号）。不用于产品推荐、产品资料检索或泛问答。
---

# 保险产品出单（保费试算/投保信息生成）

本 Skill 用于在“用户已选定具体产品并明确要购买/出单”后，计算最终保费并生成出单结果（包含保单号）。

## Common Workflow

1. 确认用户意图是“购买/投保/出单/算最终保费”，且已锁定具体产品。
2. 采集并归一化必要参数：`product_keyword`、`age`（整数）、`gender`（男/女）。
3. 调用 `insurance_get_quote` 获取最终保费与 `policy_id`。
4. 将结果以 JSON（或关键信息摘要）反馈给用户，并说明当前为模拟结果/无真实支付链接。
5. 若失败：提示用户提供更精确的产品关键词，或先转到产品查询工具确认产品名称。

## 绑定脚本与工具

- 脚本：`scripts/product_get_quote.py`
- 工具名（LangChain Tool）：`insurance_get_quote`
- 入参：
  - `product_keyword`：产品名称关键词（建议取产品名里有辨识度的一段）
  - `age`：投保人年龄（整数）
  - `gender`：投保人性别，只接受 `男` 或 `女`
- 返回：
  - 成功：JSON 字符串（字段包含 `success`、`product_name`、`input_age`、`input_gender`、`final_price`、`policy_id`）
  - 失败：以自然语言返回错误（例如 `出单失败: ...`）

### Basic Usage

**Note:** Always use the absolute path from your skills directory (shown in the system prompt above).

用于本地快速验证脚本是否可运行（参数：`<product_keyword> <age> <gender>`；其中 `gender` 仅支持 `男`/`女`）。

If running deepagents from a virtual environment:
```bash
.venv/bin/python [YOUR_SKILLS_DIR]/保险产品出单/scripts/product_get_quote.py "医疗" 30 "男"
```

如果直接使用系统 Python：
```bash
python "$HOME/.deepagents/agent/skills/保险产品出单/scripts/product_get_quote.py" "医疗" 30 "男"
```

## 什么时候调用（强约束）

仅在满足以下条件时调用 `insurance_get_quote`：

1. 用户明确表达“要买/要出单/就买这个”，并指向某个具体产品（已完成推荐或已完成产品查询确认）。
2. 用户已提供投保人 `age` 和 `gender`（或能从上下文无歧义抽取）。

不满足条件时：先补齐信息或澄清意图，不要抢跑出单。

## 不要做的事（避免误用）

- 不要用它做产品推荐、对比或科普答疑（这些属于“推荐/查询”类工具）。
- 不要在用户仍处于“问问看/先了解/随便看看”的阶段就调用。
- 不要编造投保链接：当前出单结果仅返回 `policy_id`，没有真实支付/投保链接。
- 不要主动收集不必要的敏感信息（身份证号、手机号、地址等）。本工具只需要年龄和性别。

## 调用前检查清单（调用前必须过一遍）

1. **确认购买意图**：用户是否已明确“就买 X”？
2. **确认产品唯一性**：`product_keyword` 是否足以在产品名中定位到唯一产品？
3. **确认字段合法**：
   - `age` 必须是整数
   - `gender` 必须归一到 `男`/`女`（如用户说“男性/女/女生/男生”，先转换；不确定就问）

## 参数提取与归一化建议

- `product_keyword`：优先使用用户给出的完整产品名；否则从产品名中截取一段高辨识度关键词（例如 `尊享e生`、`超级玛丽`、`达尔文`）。
- `age`：如果用户给的是区间/大概（例如“30多”），先追问具体年龄。
- `gender`：
  - “男性/男士/男生” -> `男`
  - “女性/女士/女生” -> `女`

## 结果解读与对用户的输出规范

当工具返回成功 JSON 时：

- 明确告知：已完成保费试算/模拟出单。
- 重点展示：`product_name`、`final_price`、`policy_id`。
- 提醒下一步：如果需要“真实投保/支付链接”，需要接入真实业务系统；当前仅提供模拟结果。

当工具返回失败时：

- 原样传达失败原因。
- 给出最小化纠正路径：
  1) 让用户确认产品全称/更具体关键词；或
  2) 建议先用产品查询工具定位产品名称，再回到出单。

## 示例（供 Agent 参考）

用户：
> 我就买“尊享e生百万医疗险2024”，30岁，男，帮我出单。

调用：
```json
{"product_keyword":"尊享e生","age":30,"gender":"男"}
```

成功返回（示意）：
```json
{
  "success": true,
  "product_name": "尊享e生百万医疗险2024",
  "input_age": 30,
  "input_gender": "男",
  "final_price": 330.0,
  "policy_id": "POL_123456"
}
```
