#!/usr/bin/env python3
"""
Daytona Sandbox + DeepAgents 最小验证脚本

功能:
1. 创建 Daytona 沙箱
2. 上传 skills 文件夹到沙箱
3. 使用 DaytonaSandbox 作为 backend
4. 让 Deep Agent 通过沙箱执行代码和访问文件

环境变量:
    DAYTONA_API_KEY=your_daytona_api_key
    OPENROUTER_API_KEY=your_openrouter_key

获取 API Key:
    https://app.daytona.io/dashboard

安装依赖:
    uv add daytona langchain-daytona deepagents langchain-openai python-dotenv
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

# 加载环境变量
load_dotenv()

# 检查必要的环境变量
DAYTONA_API_KEY = os.getenv("DAYTONA_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not DAYTONA_API_KEY:
    print("❌ 错误: 请设置 DAYTONA_API_KEY 环境变量")
    print("   获取地址: https://app.daytona.io/dashboard")
    sys.exit(1)

if not OPENROUTER_API_KEY:
    print("❌ 错误: 请设置 OPENROUTER_API_KEY 环境变量")
    sys.exit(1)

# 导入 Daytona 和 DeepAgents
from daytona import Daytona, FileUpload
from langchain_daytona import DaytonaSandbox
from deepagents import create_deep_agent

# 项目路径
PROJECT_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = PROJECT_ROOT / "skills"
MEMORIES_DIR = PROJECT_ROOT / "memories"
DAILY_DIR = MEMORIES_DIR / "daily"
LONG_TERM_FILE = MEMORIES_DIR / "MEMORY.md"

# 确保目录存在
MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
DAILY_DIR.mkdir(parents=True, exist_ok=True)


def ensure_memory_files(today: date) -> tuple[str, str, str]:
    """确保记忆文件存在。"""
    today_name = today.strftime("%Y-%m-%d")
    today_file = DAILY_DIR / f"{today_name}.md"

    if not LONG_TERM_FILE.exists():
        LONG_TERM_FILE.write_text(
            "# 长期记忆\n\n"
            "## 用户偏好\n- 暂无\n\n"
            "## 重要决策\n- 暂无\n\n"
            "## 关键联系人\n- 暂无\n\n"
            "## 项目事实\n- 暂无\n",
            encoding="utf-8",
        )

    if not today_file.exists():
        today_file.write_text(
            f"# {today_name}\n\n"
            "## 09:00 - 会话初始化\n"
            "- 新的一天开始，按需记录重要事实、决策、偏好与待办。\n",
            encoding="utf-8",
        )

    yesterday = today - timedelta(days=1)
    yesterday_path = f"/memories/daily/{yesterday.strftime('%Y-%m-%d')}.md"

    return (
        "/memories/MEMORY.md",
        f"/memories/daily/{today_name}.md",
        yesterday_path,
    )


def upload_skills_to_sandbox(
    sandbox, local_skills_dir: Path, remote_base: str = "/home/daytona/skills"
):
    """将 skills 文件夹上传到沙箱。"""
    print(f"\n📤 正在上传 skills 文件夹到沙箱 {remote_base}...")

    upload_files = []

    if not local_skills_dir.exists():
        print(f"⚠️  本地 skills 目录不存在: {local_skills_dir}")
        return

    # 遍历 skills 目录下的所有文件
    for file_path in local_skills_dir.rglob("*"):
        if file_path.is_file():
            # 计算相对路径
            rel_path = file_path.relative_to(local_skills_dir)
            remote_path = f"{remote_base}/{rel_path}"

            # 读取文件内容
            try:
                with open(file_path, "rb") as f:
                    content = f.read()

                upload_files.append(FileUpload(source=content, destination=remote_path))
            except Exception as e:
                print(f"⚠️  读取文件失败 {file_path}: {e}")

    if upload_files:
        # 批量上传文件
        sandbox.fs.upload_files(upload_files)
        print(f"✅ 已上传 {len(upload_files)} 个文件到沙箱")
    else:
        print("⚠️  没有文件需要上传")


def create_daytona_backend_with_skills():
    """创建 Daytona Sandbox，上传 skills，并返回 backend。"""
    print("🚀 创建 Daytona 沙箱...")

    # 初始化 Daytona
    daytona = Daytona()

    # 创建沙箱
    sandbox = daytona.create()
    print(f"✅ 沙箱创建成功: {sandbox.id}")

    # 上传 skills 文件夹
    upload_skills_to_sandbox(sandbox, SKILLS_DIR, "/home/daytona/skills")

    # 验证上传
    print("\n🔍 验证 skills 上传...")
    ls_result = sandbox.process.exec("find /home/daytona/skills -type f | head -10")
    print(f"沙箱中的 skills 文件:\n{ls_result.result}")

    # 使用 DaytonaSandbox 作为 backend
    backend = DaytonaSandbox(sandbox=sandbox)
    print("✅ DaytonaSandbox backend 创建成功")

    return backend, daytona, sandbox


def build_agent_with_daytona() -> tuple[Any, Daytona, Any]:
    """构建使用 Daytona backend 的 Deep Agent。"""

    # 创建 Daytona backend（包含上传 skills）
    backend, daytona, sandbox = create_daytona_backend_with_skills()

    # 配置 LLM (使用 OpenRouter)
    os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
    llm = ChatOpenAI(
        model="z-ai/glm-4.7-flash",
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
    )

    # 准备记忆文件路径（虚拟路径，agent 通过 backend 访问）
    today = date.today()
    long_term_path, today_path, yesterday_path = ensure_memory_files(today)

    # 构建 system prompt
    system_prompt = f"""你是一个智能助手，可以使用工具执行任务。

你有以下能力：
1. 通过 Python 代码执行数据分析和计算
2. 使用 shell 命令操作文件系统
3. 调用 skills 文件夹下的各种工具

重要提示：
- 所有 skills 文件都位于沙箱的 /home/daytona/skills/ 目录下
- 执行 Python 脚本时，请使用沙箱中的路径
- 你可以使用 shell 命令查看和操作文件

记忆文件位置：
- 长期记忆: {long_term_path}
- 今日记录: {today_path}
- 昨日记录: {yesterday_path}

当前日期: {today.isoformat()}

请在 sandbox 环境中安全地执行代码，并返回执行结果给用户。
"""

    # 技能目录（沙箱中的路径）
    skills = ["/home/daytona/skills"]
    print(f"📦 加载技能目录: {skills}")

    # 创建 Deep Agent
    print("🤖 创建 Deep Agent...")
    agent = create_deep_agent(
        model=llm,
        store=InMemoryStore(),
        backend=backend,
        skills=skills,
        memory=[long_term_path, today_path, yesterday_path],
        checkpointer=MemorySaver(),
        system_prompt=system_prompt,
    )
    print("✅ Deep Agent 创建成功")

    return agent, daytona, sandbox


def demo_list_skills(agent: Any):
    """演示列出沙箱中的 skills 文件。"""
    print("\n" + "=" * 60)
    print("演示 1: 列出沙箱中的 skills 文件")
    print("=" * 60)

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请执行 shell 命令 'find /home/daytona/skills -type f | head -20'，列出沙箱中的技能文件",
                }
            ]
        },
        config={"configurable": {"thread_id": "demo-list"}},
    )

    print("\n📝 Agent 响应:")
    for msg in result.get("messages", []):
        content = (
            msg.get("content", "")
            if isinstance(msg, dict)
            else getattr(msg, "content", "")
        )
        if content:
            print(f"  {content}")


def demo_read_sales_script(agent: Any):
    """演示读取销售脚本。"""
    print("\n" + "=" * 60)
    print("演示 2: 读取销售脚本内容")
    print("=" * 60)

    sales_script_path = "/home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py"
    sales_script_path = 'python home/daytona/skills/万销销售场景/scripts/call_sales_mcp.py intelligent_judgment --customer-name "张三" --base-url "http://127.0.0.1:8000"'

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"请使用 shell 命令执行'{sales_script_path}' ,并告诉我工具输出的内容",
                }
            ]
        },
        config={"configurable": {"thread_id": "demo-read"}},
    )

    print("\n📝 Agent 响应:")
    for msg in result.get("messages", []):
        content = (
            msg.get("content", "")
            if isinstance(msg, dict)
            else getattr(msg, "content", "")
        )
        if content:
            print(f"  {content}")


def demo_python_execution(agent: Any):
    """演示通过沙箱执行 Python 代码。"""
    print("\n" + "=" * 60)
    print("演示 3: 执行 Python 代码")
    print("=" * 60)

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请执行 Python 代码计算 42 * 42，并告诉我结果",
                }
            ]
        },
        config={"configurable": {"thread_id": "demo-python"}},
    )

    print("\n📝 Agent 响应:")
    for msg in result.get("messages", []):
        content = (
            msg.get("content", "")
            if isinstance(msg, dict)
            else getattr(msg, "content", "")
        )
        if content:
            print(f"  {content}")


def main():
    """主函数。"""
    print("=" * 60)
    print("Daytona + DeepAgents 最小验证脚本")
    print("=" * 60)
    print()

    agent = None
    daytona = None
    sandbox = None

    try:
        # 构建 Agent
        agent, daytona, sandbox = build_agent_with_daytona()

        # 运行演示
        demo_list_skills(agent)
        demo_read_sales_script(agent)
        demo_python_execution(agent)

        print("\n" + "=" * 60)
        print("✅ 所有演示完成!")
        print("=" * 60)

        # 交互模式

        while True:
            user_input = input("\n用户: ").strip()
            if user_input.lower() in ("exit", "quit", "退出"):
                break

            if not user_input:
                continue

            print("🤖 Agent 思考中...")
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config={"configurable": {"thread_id": "demo-interactive"}},
            )

            print("\n📝 Agent 响应:")
            for msg in result.get("messages", []):
                content = (
                    msg.get("content", "")
                    if isinstance(msg, dict)
                    else getattr(msg, "content", "")
                )
                if content:
                    print(f"  {content}")

    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # 清理沙箱
        if daytona and sandbox:
            print("\n🧹 清理沙箱...")
            try:
                daytona.delete(sandbox)
                print("✅ 沙箱已删除")
            except Exception as e:
                print(f"⚠️  删除沙箱时出错: {e}")


if __name__ == "__main__":
    main()
