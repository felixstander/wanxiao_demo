# LangChain + AgentRun Browser Sandbox 集成示例

基于博客文章《快速上手：LangChain + AgentRun 浏览器沙箱极简集成指南》的完整实现。

## 🌟 功能特性

- 🤖 **LangChain Agent**: 使用 `create_agent` 智能编排浏览器操作
- 🌐 **Browser Sandbox**: 基于 AgentRun 的沙箱浏览器环境
- 🛠️ **丰富的工具**: 支持创建沙箱、导航网页、截图等操作
- 👁️ **VNC 可视化**: 实时查看浏览器操作过程
- 🔒 **安全可靠**: 浏览器运行在隔离的沙箱环境中
- 💬 **多轮对话**: 支持交互式对话，复用 Sandbox 实例

## 📋 前置要求

1. **Python 3.10+**
2. **阿里云账号** 和 **AgentRun 服务访问权限**
3. **在 AgentRun 控制台创建的资源**:
   - 一个 Browser 类型的沙箱模板

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写你的配置
```

环境变量说明：

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API Key |
| `ALIBABA_CLOUD_ACCESS_KEY_ID` | ✅ | 阿里云 Access Key ID |
| `ALIBABA_CLOUD_ACCESS_KEY_SECRET` | ✅ | 阿里云 Access Key Secret |
| `ALIBABA_CLOUD_ACCOUNT_ID` | ✅ | 阿里云账号 ID |
| `ALIBABA_CLOUD_REGION` | ❌ | 区域（默认: cn-hangzhou） |
| `BROWSER_TEMPLATE_NAME` | ✅ | Browser 沙箱模板名称 |
| `AGENTRUN_CONTROL_ENDPOINT` | ❌ | AgentRun 控制面端点 |
| `AGENTRUN_DATA_ENDPOINT` | ❌ | AgentRun 数据面端点 |
| `MODEL_NAME` | ❌ | 模型名称（默认: z-ai/glm-4.5-flash） |

### 3. 在 AgentRun 控制台创建沙箱模板

访问 [AgentRun 控制台](https://functionai.console.aliyun.com/cn-hangzhou/agent/runtime/sandbox) 并创建:

1. 点击"创建沙箱模板"
2. 选择"浏览器"类型
3. 填写模板名称，记录为 `BROWSER_TEMPLATE_NAME`
4. 等待模板就绪

### 4. 运行 Demo

```bash
python main.py
```

程序会自动：
1. 创建 Browser Sandbox
2. 打开 VNC 查看器（实时查看浏览器操作）
3. 执行预设查询
4. 进入交互模式

## 📁 项目结构

```
agentrun-browser-demo/
├── main.py                 # 主入口文件
├── langchain_agent.py      # LangChain Agent 和 Tools
├── sandbox_manager.py      # Sandbox 生命周期管理
├── vnc.html                # VNC 查看器页面
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
└── README.md               # 本文件
```

## 🔧 核心模块说明

### 1. sandbox_manager.py

负责 Sandbox 的创建、管理和销毁：

- **SandboxManager 类**: 管理单个 Sandbox 实例
- **单例模式**: 确保整个会话只有一个 Sandbox
- **上下文管理器**: 支持 `with` 语句自动清理
- **全局管理器**: 提供 `get_global_manager()` 方便访问

核心方法：
- `create()`: 创建 Sandbox
- `get_info()`: 获取 Sandbox 信息（CDP URL、VNC URL）
- `destroy()`: 销毁 Sandbox
- `is_active()`: 检查 Sandbox 是否活跃

### 2. langchain_agent.py

定义 LangChain Tools 和创建 Agent：

**Tools 列表：**

| 工具名 | 功能 |
|--------|------|
| `create_browser_sandbox` | 创建浏览器沙箱 |
| `get_sandbox_info` | 获取沙箱信息 |
| `navigate_to_url` | 导航到指定 URL |
| `take_screenshot` | 截取页面截图 |
| `destroy_sandbox` | 销毁沙箱（谨慎使用） |

**创建 Agent:**

```python
from langchain_agent import create_browser_agent

agent = create_browser_agent()

# 执行查询
result = agent.invoke({
    "messages": [{"role": "user", "content": "访问 https://www.example.com"}]
})
```

### 3. main.py

主入口文件，演示完整流程：

- **VNC 自动打开**: 创建 Sandbox 后自动打开 VNC 查看器
- **信号处理**: 捕获 Ctrl+C，确保资源正确清理
- **交互模式**: 支持持续对话，复用 Sandbox 实例

### 4. vnc.html

VNC 可视化查看器页面：

- **noVNC 集成**: 使用 noVNC 库连接 VNC 服务器
- **自动连接**: 从 URL 参数读取 VNC URL 并自动连接
- **缩放控制**: 支持调整显示比例
- **状态显示**: 实时显示连接状态

## 💡 使用示例

### 基础网页访问

```
你: 创建一个浏览器 sandbox
Agent: ✅ Sandbox 创建成功！
       📋 Sandbox 信息:
       - ID: sandbox-xxxxx
       - CDP URL: wss://...
       - VNC URL: wss://...

你: 导航到 https://www.aliyun.com
Agent: ✅ 已成功导航到: https://www.aliyun.com
       📄 页面标题: 阿里云-计算，为了无法计算的价值
       💡 您可以在 VNC 中查看页面内容。

你: 截取当前页面截图
Agent: ✅ 截图已保存: screenshot.png
```

### VNC 可视化

创建 Sandbox 后，会自动打开 VNC 查看器：

1. **自动打开**: 浏览器会自动打开 `vnc.html`
2. **自动连接**: VNC URL 通过 URL 参数传递
3. **实时查看**: 所有浏览器操作实时显示
4. **交互操作**: 支持在 VNC 中直接操作浏览器

## 🔐 安全说明

1. **环境变量**: 敏感信息（API Key、AK/SK）存储在 `.env` 文件，不要提交到代码仓库
2. **Sandbox 隔离**: 每个 Sandbox 运行在独立容器中，完全隔离
3. **自动清理**: 程序退出时自动销毁 Sandbox，避免资源浪费
4. **超时控制**: Sandbox 空闲超时会自动销毁

## 🐛 故障排除

### 问题：运行时报错 "请设置环境变量 OPENROUTER_API_KEY"

**解决**: 在 `.env` 文件中设置 `OPENROUTER_API_KEY`，可以从 [OpenRouter 控制台](https://openrouter.ai/keys) 获取。

### 问题：VNC 查看器无法自动打开

**解决**: 
- 手动打开 `vnc.html` 文件
- 从 Agent 输出中复制 VNC URL
- 粘贴到 VNC 查看器的输入框中

### 问题：Sandbox 创建失败

**解决**: 
- 检查阿里云 Access Key 是否正确
- 检查 `BROWSER_TEMPLATE_NAME` 是否已在控制台创建
- 检查网络连接

### 问题：浏览器操作无响应

**解决**:
- 检查 VNC 中浏览器是否正常显示
- 等待页面完全加载后再执行操作
- 检查 CDP URL 是否有效

## 📚 相关链接

- [博客原文](https://www.cnblogs.com/alisystemsoftware/p/19518369)
- [AgentRun SDK 文档](https://docs.agent.run)
- [AgentRun Python SDK GitHub](https://github.com/Serverless-Devs/agentrun-sdk-python)
- [LangChain 文档](https://python.langchain.com/)
- [AgentRun 控制台](https://functionai.console.aliyun.com/)
- [OpenRouter](https://openrouter.ai/)

## 📄 License

MIT License
