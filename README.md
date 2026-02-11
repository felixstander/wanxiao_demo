# TODO LIST

1. - [] skills 仍未成功加载
2. - [] 记忆模块完善
    1. - [] Milvus Lite 记忆检索脚本尝试
    2. - [] 记忆子Agent从主 Agent解耦出来
    3. - [] 画记忆模块的架构图


# DeepAgents + OpenRouter + 原生前端 Demo

## 功能说明

- 使用 LangChain DeepAgents（`create_deep_agent`）作为核心 Agent 运行时。
- 通过 `langchain-openai` 接入 OpenRouter 模型（默认 `z-ai/glm-4.5-flash`）。
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
