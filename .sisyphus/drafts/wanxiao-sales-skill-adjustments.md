# Draft: 万销销售场景 Skill 细节修订

## Requirements (confirmed)
- 在工作流第 4 步中，直接指导读取 `references/任务倒计时SKILL.md`，而不是后文再补充参考说明。
- `Basic Usage` 不再使用 Python 脚本调用，改为 `curl` 接口调用形式。
- `curl` 入参设置参考 `mcp_tool/sales_mcp_mock.py` 中各 MCP tool 的入参定义。

## Technical Decisions
- 主要修订目标文件：`skills/万销销售场景/SKILL.md`。
- 工作流与调用示例需要保持一致：流程描述、工具顺序、示例参数来源统一。
- 保留现有技能定位（意向分流 + 工具编排 + 倒计时提醒），仅修正文档执行细节。

## Research Findings
- 现状：`skills/万销销售场景/SKILL.md` 的第 4 步仅写“调用倒计时监控：diagnose_stuck_point”，未在该步骤直接提示读取倒计时参考。
- 现状：文档后部已有“按需读取倒计时参考”段落，路径写为 `references/任务倒计时-SKILL.md`（带连字符）。
- 现状：`Basic Usage` 仍是 `run_wanxiao_sales_flow.py` 的 Python 命令示例。
- 依据：`mcp_tool/sales_mcp_mock.py` 中核心工具入参以 `customer_name` 为主，部分工具另有可选参数（如 `agent_ai_business_card_tool` 的 `agent_name`、`specialty`）。

## Open Questions
- `Basic Usage` 是否需要展示完整 MCP SSE 流程（`/sse` + `initialize` + `tools/call`），还是仅展示直观的 `tools/call` 片段？
- 倒计时参考路径是否统一为 `references/任务倒计时SKILL.md`（无连字符）作为唯一标准路径？

## Scope Boundaries
- INCLUDE: 工作流步骤描述、参考路径提示、Basic Usage 调用方式与入参示例。
- EXCLUDE: 修改 Python 服务实现、MCP tool 业务逻辑、非本 Skill 文档内容。
