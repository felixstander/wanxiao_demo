---
name: read-and-create-skill
description: |
  基于用户提供的 Excel/CSV 表格自动创建 Agent 技能包。

  **使用场景：**
  - 用户说"我有个叫 xxx 的表格，帮我生成技能"
  - 用户需要将填好的表格转换为可用的 skill 技能包
  - 用户提及表格文件名并要求创建/生成技能

  **触发关键词：**
  - "表格" + "生成技能" / "创建技能"
  - "csv" + "技能"
  - "有个叫 xxx 的表格"
  - "基于表格创建技能"

  **务必使用此技能：** 当用户提及他们有表格文件并希望基于该表格创建 Agent 技能时，无论用户是否明确说出"创建技能"这几个字，都应该使用此技能处理。
---

# read_and_create_skill

## 说明

本技能用于基于用户提供的 Excel/CSV 表格自动创建 Agent 技能包。用户将填好的表格放在 `data/` 文件夹中，提供表格文件名后，本技能会读取表格内容并生成完整的 skill 技能包。

表格可以包含多个 Sheet：
- **Sheet1**: 主技能定义（必须）
- **Sheet2-N**: 子场景定义（可选），每个子场景会生成独立的参考文档

## 使用流程

### 1. 表格文件准备

用户需将填好的表格文件（.csv 或 .xlsx 格式）放置在 `read_and_create_skill/data/` 目录下。

**表格结构要求：**
- Sheet1：主技能信息（使用场景、SOP、接口定义等）
- Sheet2-N：子场景信息（如"保单导出"、"理赔查询"等）

### 2. 用户输入格式

用户会以如下形式提供表格名称：
- "我有个叫 xxx 的表格"
- "帮我基于 xxx 表格生成技能"
- "用 xxx.xlsx 创建一个新技能"

**你需要从用户输入中提取表格文件名**（不带后缀）。

### 3. 读取表格内容

使用 `scripts/csv_to_prompt.py` 脚本读取表格内容：

```bash
python read_and_create_skill/scripts/csv_to_prompt.py <表格文件名>
```

**注意**：
- 只需提供文件名，不需要 `.csv` 或者 `.xlsx` 后缀
- 脚本会自动在 `data/` 目录下查找对应文件
- 脚本会读取所有 Sheet，并按 Sheet 分组显示内容

### 4. 解析表格字段

每个 Sheet 都包含以下字段：

#### 产品/业务提供的字段

| 字段名 | 说明 | 对应代码变量 |
|--------|------|-------------|
| SKILL名称 | 生成的 skill 文件夹名称（建议英文，小写，用连字符分隔） | - |
| description | 使用场景描述 | `description` |
| steps | SOP流程(业务/产品提供) | `steps` |
| judege_logic | 步骤分流逻辑(业务/产品提供) | `judege_logic` |
| is_inverse | 需用户反馈内容(业务/产品提供) | `is_inverse` |
| inverse_content | 反馈内容缺失是否反问(业务/产品提供) | `inverse_content` |
| related_question | 建议关联问(业务/产品提供) | `related_question` |

#### 开发提供的字段

| 字段名 | 说明 | 对应代码变量 |
|--------|------|-------------|
| tool_method | 接口工具（开发提供） | `tool_method` |
| tool_input | 接口入参（开发提供） | `tool_input` |
| tool_output | 接口出参（开发提供） | `tool_output` |

**字段含义详解：**

- **description**: 使用场景描述，说明何时触发此技能，包含触发关键词和条件
- **steps**: SOP流程，业务执行的标准操作流程步骤
- **judege_logic**: 步骤分流逻辑，不同场景下的分支判断规则
- **is_inverse**: 需用户反馈内容，执行任务所需的必填信息列表
- **inverse_content**: 反馈内容缺失是否反问，true/false，缺失时是否主动反问用户
- **related_question**: 建议关联问，业务/产品建议的关联问题
- **tool_method**: 接口工具，API 接口的调用方式（curl 示例）
- **tool_input**: 接口入参，API 请求的参数说明（JSON 格式）
- **tool_output**: 接口出参，API 返回的数据格式说明

### 5. 创建技能包

根据表格内容，在指定目录（默认为 `workspace/skills/`）创建技能包。

#### 5.1 目录结构

```
skills/
└── {SKILL名称}/
    ├── SKILL.md              # 技能主文件（基于 Sheet1）
    └── references/
        ├── tool.md           # 工具定义（开发提供的字段）
        ├── sub-scene-1.md    # 子场景1指引（Sheet2）
        ├── sub-scene-2.md    # 子场景2指引（Sheet3）
        └── ...
```

#### 5.2 生成 references/tool.md

将 Sheet1 中的开发字段写入此文件：
- tool_method（接口工具）
- tool_input（接口入参）
- tool_output（接口出参）

**此文件是接口调用的权威参考，当工具调用出错时，必须优先读取此文件排查问题。**

```markdown
# 工具定义

## 接口方法

\`\`\`bash
{tool_method}
\`\`\`

## 接口入参

\`\`\`json
{tool_input}
\`\`\`

## 接口出参

\`\`\`json
{tool_output}
\`\`\`
```

#### 5.3 生成子场景文档（Sheet2-N）

对于每个子场景 Sheet（Sheet1 除外），创建一个独立的参考文档：

- **文件名转换规则**：
  - 中文 Sheet 名需转换为英文（如"保单导出" → `policy-export.md`）
  - 使用小写字母，空格用连字符替换
  - 可以使用简单的映射规则，如：
    - 保单导出 → `policy-export`
    - 理赔查询 → `claim-query`
    - 续费提醒 → `renewal-reminder`

- **文件内容结构**：

```markdown
# {Sheet 名称}

## 说明

{description}

## 执行步骤

{steps}

## 分流逻辑

{judege_logic}

## 需收集的信息

{is_inverse}

## 建议关联问

{related_question}
```

**按需加载**：在 SKILL.md 中根据场景需要引用这些子场景文档。

#### 5.4 生成 SKILL.md（主技能文件）

基于 Sheet1 内容生成技能主文件：

```markdown
---
name: {SKILL名称}
description: |
  {使用场景描述摘要}
  
  **触发条件：**
  - {触发条件1}
  - {触发条件2}
---

# {SKILL名称}

## 说明

{description}

## 使用时机

{从使用场景描述中提取触发条件和关键词}

## 执行步骤

{steps}

## 分流逻辑

{judege_logic}

## 子场景

根据对话上下文，按需加载对应的子场景文档：

- 保单导出场景：`references/policy-export.md`
- 理赔查询场景：`references/claim-query.md`
- ...

## 需收集的信息

{is_inverse}

{如果 inverse_content 为 true，添加：缺失时主动反问用户以获取信息}

## 工具调用

- 工具定义：`references/tool.md`
- **当工具调用出错时，优先读取 `references/tool.md` 排查问题**

## 响应示例

{根据 tool_output 格式，提供自然的响应话术示例}
```

## 完整执行示例

假设用户说："我有个叫 policy_search 的表格，帮我生成技能"

执行步骤：

1. **提取文件名**：`policy_search`

2. **读取表格**：
   ```bash
   python3 read_and_create_skill/scripts/csv_to_prompt.py policy_search
   ```

3. **解析输出**：脚本会返回所有 Sheet 的内容，例如：
   - Sheet 1: policy-search（主技能）
   - Sheet 2: 保单导出（子场景）
   - Sheet 3: 理赔查询（子场景）

4. **创建目录结构**：
   ```
   skills/
   └── policy-search/
       ├── SKILL.md
       └── references/
           ├── tool.md
           ├── policy-export.md
           └── claim-query.md
   ```

5. **生成文件**：
   - `tool.md`：写入 Sheet1 的开发字段
   - `policy-export.md`基于 Sheet2 生成子场景文档
   - `claim-query.md`基于 Sheet3 生成子场景文档
   - `SKILL.md`：基于 Sheet1 生成主技能文档，包含子场景引用

## 错误处理

执行过程中可能遇到以下情况：

1. **表格文件不存在**：提示用户检查 `read_and_create_skill/data/` 目录下是否有该文件
2. **格式错误**：确保文件使用 UTF-8 编码，Excel 文件需安装 openpyxl（`pip install openpyxl`）
3. **字段缺失**：如果表格缺少必要字段（如 SKILL名称、description），需提示用户补充
4. **脚本执行失败**：检查 Python 环境是否正常，脚本路径是否正确

## 注意事项

1. **文件名处理**：
   - 从用户输入提取的文件名可能包含或不含后缀，需统一处理
   - SKILL名称建议转为小写，空格替换为连字符（如 `Policy Search` → `policy-search`）

2. **子场景文件名**：
   - 中文 Sheet 名需要转换为英文文件名
   - 可以使用拼音、意译或简写，保持简洁易读
   - 例如："保单导出" → `policy-export.md`，"理赔进度查询" → `claim-status.md`

3. **工具定义**：`references/tool.md` 必须包含完整的接口信息，作为排错第一参考

4. **按需加载**：子场景文档不应在 SKILL.md 中全部展开，而是根据上下文按需引用

5. **重复生成**：如果目标技能目录已存在，询问用户是覆盖还是增量更新

## 输出要求

生成的技能包必须满足：

1. **结构完整**：
   - `SKILL.md`（主技能文件）
   - `references/tool.md`（工具定义）
   - `references/{子场景}.md`（每个子场景一个文件）

2. **SKILL.md 格式**：
   - 必须包含 YAML frontmatter（name 和 description）
   - description 需说明触发条件和关键特征
   - 正文包含说明、使用时机、执行步骤、子场景引用、工具调用等章节
   - **必须明确告知：工具调用出错时优先读取 `references/tool.md`**

3. **tool.md 格式**：
   - 使用 Markdown 代码块展示接口调用示例
   - 入参和出参使用 JSON 格式说明
   - 添加注释解释关键字段含义

4. **子场景文档格式**：
   - 文件名为英文（中文 Sheet 名需转换）
   - 包含该场景的执行步骤和分流逻辑
   - 可在 SKILL.md 中通过相对路径引用
