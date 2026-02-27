# TODO LIST

1. - [ ] skills 仍未成功加载
2. - [ ] 记忆模块完善
    1. - [ ] Milvus Lite 记忆检索脚本尝试
    2. - [x] 记忆子Agent从主 Agent解耦出来
    3. - [ ] 画记忆模块的架构图
    4. - [ ] 长期记忆的提示词需要进行解耦，要记录的内容现在太杂太多，应该解耦成用户偏好/代理人偏好/已咨询保险等
    5. - [x] 系统提示词里 memory.md 需要修改，不应该让他再去 read file的，因为记忆已经自动载入到<agent_memory> 里，这样会浪费一次大模型的调用。可以指明 edit file 的记忆路径


# DeepAgents + OpenRouter + 原生前端 Demo

## 功能说明

- 使用 LangChain DeepAgents（`create_deep_agent`）作为核心 Agent 运行时。
- 通过 `langchain-openai` 接入 OpenRouter 模型（默认 `z-ai/glm-4.7-flash`）。
- 从 `~/.deepagents/agent/skills` 加载技能文件，并映射到 `/skills/*`。
- 使用本地文件系统后端，记忆数据存储在项目内的 `memories/` 目录。
- 前端使用原生 `HTML + CSS + JavaScript`。
- 后端使用 FastAPI 提供静态页面与接口（如 `/api/chat`、`/api/chat/stream`）。
- 前端通过 `/api/chat/stream` 消费流式输出。
- 界面右侧提供“思考过程”面板，展示 LangGraph 事件、工具调用与阶段信息。

## 环境准备

1. 安装依赖：

```bash
uv sync
```

2. 创建环境变量文件：

```bash
cp .env.example .env
```

3. 编辑 `.env`：

```env
OPENROUTER_API_KEY="your-openrouter-key"
OPENROUTER_MODEL="z-ai/glm-4.5-flash"
OPENROUTER_MEMORY_MODEL="z-ai/glm-4.7-flash"
MEMORY_AGENT_ENABLED="1"
OUTPUT_SANITIZE_ENABLED="1"
```

## 启动项目

```bash
uv run python main.py
```

浏览器访问：`http://localhost:7860`

默认开启自动重载（代码变更后进程自动重启）。

如果要关闭自动重载：

```bash
AUTO_RELOAD=0 uv run python main.py
```

## 运行测试

```bash
uv run python -m unittest tests/test_main.py
```

或运行全部测试：

```bash
uv run python -m unittest discover -s tests
```

## 前端目录结构

```text
frontend/
├── index.html
├── style.css
└── script.js
```

- `index.html`：聊天页面结构（头部、消息区、技能区、输入区）
- `style.css`：页面布局、动画、响应式样式
- `script.js`：前端交互逻辑与接口调用

## 技能目录说明

应用会递归读取以下目录中的技能文本文件：

`~/.deepagents/agent/skills`

这些文件会被映射为 DeepAgents 可访问的虚拟路径 `/skills/...`，供 Agent 按需加载。

## 记忆目录说明（双层记忆）

记忆以 Markdown 形式保存在项目根目录下：

```text
memories/
├── MEMORY.md
└── daily/
    └── YYYY-MM-DD.md
```

- `memories/daily/YYYY-MM-DD.md`：短期记忆（按天记录的追加日志）
- `memories/MEMORY.md`：长期记忆（用户偏好、关键决策、联系人、项目事实）

系统提示会引导 Agent：

1. 会话开始时读取长期记忆与最近日记。
2. 将短期信息按 `## HH:MM - 标题` 写入当日日志。
3. 将跨天稳定信息去重后沉淀到 `MEMORY.md`。

## Prompt 配置化

- 所有主/子 Agent 提示词已从 `main.py` 抽离到配置与模板文件：

```text
config/prompts.yaml
prompts/main_system/SOUL.md
prompts/main_system/INDENTITY.md
prompts/main_system/MEMORY.md
prompts/memory_agent.md
```

- `config/prompts.yaml` 负责：
  - prompt 文件路由
  - 主模型与 memory_agent 模型配置（含 env 键与默认值）

## Memory Agent（异步记忆提炼）

- 新增 `memory_agent` 子 Agent：每轮用户-助手对话结束后异步执行，不阻塞主回复。
- 模型默认使用 `z-ai/glm-4.7-flash`（可通过 `OPENROUTER_MEMORY_MODEL` 覆盖）。
- 输出为结构化 JSON，自动落盘到：
  - 每日短期记忆：`memories/daily/YYYY-MM-DD.md`
  - 长期记忆：`memories/MEMORY.md`
- 可通过 `MEMORY_AGENT_ENABLED=0` 关闭该异步记忆提炼流程。

## 输出净化规则配置

- 配置文件：`config/output_sanitize.yaml`
- 可配置项：
  - `enabled`：是否启用净化
  - `literals`：命中即过滤的关键词
  - `regex`：正则过滤规则
- 运行时总开关：`OUTPUT_SANITIZE_ENABLED=0/1`

## 文件自动同步（Daytona 沙箱）
应用支持将本地 `skills/`、`data/`、`memories/` 文件夹的变更**自动同步**到 Daytona 沙箱，无需重启应用。

### 工作原理

- **自动监听**：应用启动后，使用 `watchdog` 库监视三个文件夹的变更
- **防抖机制**：变更发生后等待 2 秒（可配置），期间如有新变更则重置计时器
- **增量同步**：只上传变更的文件，保留沙箱中其他文件
- **自动清理**：应用退出时自动停止监听器

### 环境变量配置

```bash
# 禁用文件监听（默认启用）
FILE_WATCH_ENABLED=0 uv run python main.py

# 调整防抖时间（默认 2.0 秒）
FILE_WATCH_DEBOUNCE=5.0 uv run python main.py
```

### 手动同步 API

如需手动触发同步（例如临时禁用自动监听时）：

```bash
# 触发同步
curl -X POST http://localhost:7860/api/sync

# 返回示例
{
  "status": "success",
  "message": "文件夹同步完成",
  "synced_folders": ["skills", "data", "memories"]
}
```

### 工作流程

```
修改本地文件（skills/data/memories）
           ↓
    文件监听器检测到变更
           ↓
    防抖等待 2 秒（可配置）
           ↓
    自动同步到 Daytona 沙箱
           ↓
    Agent 立即使用最新文件
```

### 注意事项

- 首次启动时会自动安装 `watchdog` 依赖（已添加到 `pyproject.toml`）
- 隐藏文件（以 `.` 开头）、临时文件、`__pycache__` 等会被自动忽略
- 如果沙箱未初始化（如启动失败），自动监听将不会启动
## Milvus Lite 记忆检索脚本
新增脚本：`src/milvus_mem_search.py`

- 数据源目录：`memories/daily/*.md`（仅匹配 `YYYY-MM-DD.md`）
- 向量库：Milvus Lite 本地文件 `/.memories/milvus_memories.db`
- 向量模型：`sentence-transformers` 的 `all-MiniLM-L6-v2`

常用命令：

```bash
# 首次或增量索引 daily 记忆
uv run python src/milvus_mem_search.py index

# 全量重建索引（drop + rebuild）
uv run python src/milvus_mem_search.py rebuild

# 语义检索
uv run python src/milvus_mem_search.py search "今天提过哪些客户需求" --top-k 5

# 查看 collection 统计
uv run python src/milvus_mem_search.py stats
```
