---
name: insurance-product-recommend
description: 保险产品推荐（基于预算与需求/人群场景）。当用户想让你“推荐/选一款/哪款更适合/性价比”且尚未确定具体产品，并给出预算倾向（如“几百块/便宜点/不差钱”）和/或核心需求（如“看病报销/担心得癌症/意外防护/给孩子买/给老人买”）时使用；调用 insurance_product_recommend 返回推荐产品与理由。不用于出单/算保费，也不用于产品资料检索。
---

# 保险产品推荐（基于预算与需求）

本 Skill 用于在用户“想买保险但还没选定具体产品”时，根据预算描述与核心需求，筛选并输出推荐产品（默认返回前 2 个）。

## Common Workflow

1. 确认用户意图是“要推荐/要选择”而不是“查资料/要出单”。
2. 提取 `budget_desc` 与 `user_requirement`（缺一个就追问；都缺就先做需求澄清）。
3. 调用 `insurance_product_recommend` 获取推荐候选。
4. 将结果按“产品名 + 类型 + 推荐理由”整理输出。
5. 追问下一步：
   - 若用户已选定其中一款并要购买：补齐年龄/性别，转到出单。
   - 若用户仍不确定：继续澄清预算/保障重点/人群（少儿/老人/成人）再推荐。

## 绑定脚本与工具

- 脚本：`scripts/product_recommend.py`
- 工具名（LangChain Tool）：`insurance_product_recommend`
- 入参：
  - `budget_desc`：用户预算描述（自然语言），例如 `"几百块"`、`"便宜点"`、`"不差钱"`
  - `user_requirement`：用户核心需求（自然语言），例如 `"看病报销"`、`"担心得癌症"`、`"意外防护"`、`"给孩子买"`
- 返回：
  - 文本（包含推荐产品名称、类型、推荐理由）

### Basic Usage

**Note:** Always use the absolute path from your skills directory (shown in the system prompt above).

用于本地快速验证脚本是否可运行（参数：`<budget_desc> <user_requirement>`）。

If running deepagents from a virtual environment:
```bash
.venv/bin/python [YOUR_SKILLS_DIR]/保险产品推荐/scripts/product_recommend.py "几百块" "看病报销"
```

如果直接使用系统 Python：
```bash
python "$HOME/.deepagents/agent/skills/保险产品推荐/scripts/product_recommend.py" "几百块" "看病报销"
```

## 什么时候调用（强约束）

仅在满足以下条件时调用 `insurance_product_recommend`：

1. 用户明确希望“推荐/挑选/选一款更合适的保险”，且尚未选定具体产品。
2. 用户至少给出预算倾向或核心需求中的一个；如果两者都没有，先问清楚再推荐。

## 不要做的事（避免误用）

- 不要用于“已决定买某个具体产品”的场景（那属于出单/保费试算）。
- 不要用于“查询产品条款/标签/资料”的场景（那属于产品检索/答疑）。
- 不要把推荐当成最终结论：推荐结果是基于简化规则的筛选，应在推荐后继续引导用户确认保障点是否匹配。

## 参数提取与归一化建议

- `budget_desc`：尽量保留用户原话（工具内部会做简单映射）。如果用户给的是含糊区间（例如“差不多吧”），先追问可接受的大致年保费范围。
- `user_requirement`：同样尽量保留用户原话；若用户描述很长，抽取其中的核心诉求词（例如“住院报销/重疾确诊给付/意外医疗/孩子门诊”等）。

## 输出解读与对用户的输出规范

- 输出里会列出推荐产品及“类型/理由”。
- 若返回“暂时没有完美匹配”，优先做需求澄清（预算、年龄段、想保的风险类型），再尝试推荐或转产品查询。

## 示例（供 Agent 参考）

用户：
> 想买个医疗险，别太贵，几百块左右，有什么推荐？

调用：
```json
{"budget_desc":"几百块","user_requirement":"看病报销"}
```
