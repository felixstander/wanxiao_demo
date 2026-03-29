# Insurance QA Skill

保险与通用知识问答 Skill，用于处理用户的保险产品问答和通用性知识问答（如天气、新闻等）。

## 功能特性

- **保险问答**：通过内部工具查询保险产品条款、费率、理赔规则等官方信息
- **通用搜索**：通过外部搜索工具获取实时新闻、政策、天气等外部信息
- **智能规划**：自动拆分复杂问题为可独立执行的子问题序列
- **答案验证**：多维度验证答案质量（完整性、准确性、相关性、一致性）
- **错误处理**：优雅处理工具调用失败、信息冲突等异常情况
- **来源标注**：清晰区分内部资料和外部信息，标注信息边界

## 文件结构

```
insurance-qa-skill/
├── SKILL.md                      # 主入口：触发条件、硬规则、总体流程
├── README.md                     # 本文件：项目说明和结构概览
├── references/                   # 参考文档：详细策略和规范
│   ├── plan.md                   # 计划模块：问题拆分策略
│   ├── tool.md                   # 工具规范：脚本调用方式和参数详解
│   ├── validation.md             # 验证模块：答案质量检查标准
│   ├── error.md                  # 错误处理：异常处理和冲突解决
│   └── gotchas.md                # 陷阱清单：保险场景特有风险
├── scripts/                      # 可执行脚本
│   ├── product_answer.py         # 内部保险问答工具
│   └── web_search.py             # 外部网页搜索工具
├── assets/                       # 资源文件
│   ├── format.md                 # 输出格式规范
│   ├── insurance-templates/      # 保险产品专用模板（待扩展）
│   └── search-templates/         # 通用搜索模板（待扩展）
└── examples/                     # 示例文档
    ├── tool-usage-example.md     # 工具调用示例（待扩展）
    └── error-recovery-example.md # 错误恢复示例（待扩展）
```

## 快速开始

### 1. 安装依赖

```bash
# 两个脚本仅依赖Python标准库，无需额外安装
python --version  # 需要 Python 3.7+
```

### 2. 使用内部保险问答工具

```bash
python scripts/product_answer.py --question "重疾险等待期是多少天"
python scripts/product_answer.py --question "30岁男性重疾险50万保额年缴保费"
```

**参数说明：**
- `--question` (必填): 标准化的保险问题描述
- `--format` (可选): 输出格式，`text` 或 `json`，默认 `text`
- `--version` (可选): 指定条款版本，如 `2024版`

**输出字段：**
- `answer` (str): 关于保险问题的文本答案

### 3. 使用外部网页搜索工具

```bash
python scripts/web_search.py --question "2025年3月保险监管新政策"
python scripts/web_search.py --question "北京今天天气"
```

**参数说明：**
- `--question` (必填): 搜索查询词
- `--format` (可选): 输出格式，`json` 或 `text`，默认 `json`
- `--num-results` (可选): 返回结果数量，默认 `3`

**输出字段：**
- `web_detail` (List[str]): 前3个相关网页的详细内容
- `web_sumn` (str): 基于搜索结果的总结

### 4. 混合查询示例

```bash
# 步骤1：查询内部保险产品信息
python scripts/product_answer.py --question "XX重疾险产品条款简介"

# 步骤2：搜索相关外部政策新闻
python scripts/web_search.py --question "2025年3月 XX重疾险 监管政策 新规"
```

## 核心流程

```
用户问题 → 计划模块（plan.md）→ 生成执行计划
   ↓
确定工具类型 → 调用对应脚本
   ↓
验证模块（validation.md）检查返回数据
   ↓
通过？ → 是：继续下一子问题或进入格式化
   ↓
否 → 错误模块（error.md）处理 → 重试/调整/报错
   ↓
格式模块（format.md）组装输出（标注数据来源）
```

## 硬规则

1. **问题拆分强制检查**：所有问题必须先经过计划模块评估是否需要拆分
2. **工具调用规范**：保险问题必须用 `product_answer.py`，实时信息必须用 `web_search.py`
3. **工具选择优先级**：保险相关问题优先使用内部工具
4. **验证强制**：每个工具返回结果必须经过验证模块检查
5. **输出规范**：必须按照 format.md 规范标注信息来源
6. **脚本执行安全**：只允许调用 `scripts/` 目录下的两个脚本

## 文档说明

### SKILL.md
主入口文件，包含：
- 触发条件：何时激活该 Skill
- 任务目标：核心服务质量要求
- 硬规则：不可违反的执行规则
- 执行流程：完整的工具调用流程
- 工具调用速查表

### references/plan.md
问题拆分与执行策略：
- 多意图问题拆分（含"和"、"以及"等连接词）
- 对比类问题拆分（含"对比"、"哪个更好"等关键词）
- 混合信息问题拆分（保险+外部信息）
- 条件依赖问题串行执行
- 执行计划格式（YAML 规范）
- 工具选择决策树

### references/tool.md
工具调用规范：
- `product_answer.py` 调用方式和参数说明
- `web_search.py` 调用方式和参数说明
- 输出格式详解（`answer`, `web_detail`, `web_sumn`）
- 返回值解析规范
- 来源可信度评估标准
- 工具调用组合示例
- 错误处理规范

### references/validation.md
答案质量检查：
- 完整性检查（Completeness）
- 准确性检查（Accuracy）
- 相关性检查（Relevance）
- 一致性检查（Consistency）
- 验证流程和失败类型处理
- 验证输出格式（YAML）

### references/error.md
错误处理策略：
- 工具调用失败（Technical Errors）
- 数据缺失（Data Missing）
- 信息冲突（Conflicts）
- 逻辑不一致（Logical Inconsistency）
- 错误恢复策略矩阵

### references/gotchas.md
关键陷阱清单：
- 🚨 高风险：条款版本混淆、地域限定遗漏、营销话术当条款
- ⚠️ 中风险：费率表误解、保障期限表述、等待期计算
- 通用问答陷阱：过时信息、AI幻觉
- 流程陷阱：错误链式反应、隐私泄露、循环调用

### assets/format.md
输出格式规范：
- 信息来源标记（【内部资料】/【网络信息】）
- 时间戳标注要求
- 纯保险产品问答格式
- 纯通用知识问答格式
- 混合问答格式和信息边界标注
- 信息边界硬规则
- 特殊场景处理话术

## 安全注意事项

1. **参数清理**：两个脚本都实现了输入清理，移除危险字符防止注入攻击
2. **隐私保护**：`web_search.py` 会自动脱敏敏感信息（保单号、身份证号、手机号）
3. **来源验证**：外部搜索结果会标注可信度级别（高/中/低）
4. **重试限制**：工具调用失败时有重试次数限制，避免无限循环

## 扩展开发

### 添加新的保险产品

编辑 `scripts/product_answer.py` 中的 `InsuranceDatabase` 类，添加新的产品数据。

### 接入真实搜索API

编辑 `scripts/web_search.py` 中的 `WebSearchAPI` 类，替换 `search` 方法为真实的搜索API调用（如 Google Custom Search API、Bing Search API 等）。

### 添加新的输出模板

在 `assets/insurance-templates/` 或 `assets/search-templates/` 目录下添加新的 Markdown 模板文件。

## 许可证

MIT License

## 维护者

- 创建日期：2025-03-29
- 版本：v1.0.0

## 参考

- [渐进式披露设计模式](https://mp.weixin.qq.com/s/c42XqFaEeNEhh6DtQgajFw)
- OpenCode Skill 框架规范