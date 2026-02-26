#!/usr/bin/env python3
"""
Daytona Sandbox + DeepAgents 最小验证脚本（支持 ngrok IP 白名单）

功能:
1. 创建 Daytona 沙箱（支持 ngrok IP 白名单）
2. 上传 skills 文件夹到沙箱
3. 使用 DaytonaSandbox 作为 backend
4. 让 Deep Agent 通过沙箱执行代码和访问文件

环境变量:
    DAYTONA_API_KEY=your_daytona_api_key
    OPENROUTER_API_KEY=your_openrouter_key
    NGROK_URL=https://xxx.ngrok-free.dev  # 可选，用于配置白名单

获取 API Key:
    https://app.daytona.io/dashboard
"""

import json
import os
import subprocess
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
GLM_API_KEY = os.getenv("GLM_API_KEY")

if not DAYTONA_API_KEY:
    print("❌ 错误: 请设置 DAYTONA_API_KEY 环境变量")
    print("   获取地址: https://app.daytona.io/dashboard")
    sys.exit(1)

if not GLM_API_KEY:
    print("❌ 错误: 请设置 GLM_API_KEY 环境变量")
    print("   获取地址: https://open.bigmodel.cn/")
    sys.exit(1)

if not OPENROUTER_API_KEY:
    print("⚠️ 警告: 未设置 OPENROUTER_API_KEY 环境变量（当前未使用）")

# 导入 Daytona 和 DeepAgents
from daytona import CreateSandboxBaseParams, Daytona, FileUpload
from deepagents import create_deep_agent
from langchain_daytona import DaytonaSandbox

# 项目路径
PROJECT_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = PROJECT_ROOT / "skills"
MEMORIES_DIR = PROJECT_ROOT / "memories"
DAILY_DIR = MEMORIES_DIR / "daily"
LONG_TERM_FILE = MEMORIES_DIR / "MEMORY.md"

# 配置：ngrok URL（用于 Daytona 沙箱网络白名单）
# 设置此环境变量后，沙箱将被允许访问该 ngrok 地址
NGROK_URL = os.getenv("NGROK_URL", "")

# 确保目录存在
MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
DAILY_DIR.mkdir(parents=True, exist_ok=True)


def get_ngrok_ip(ngrok_url: str) -> str | None:
    """解析 ngrok 域名对应的 IP 地址。"""
    import socket
    from urllib.parse import urlparse

    try:
        parsed = urlparse(ngrok_url)
        hostname = parsed.hostname

        if not hostname:
            print(f"❌ 无法解析 URL: {ngrok_url}")
            return None

        ip_address = socket.gethostbyname(hostname)
        print(f"✅ {hostname} -> {ip_address}")
        return ip_address

    except socket.gaierror as e:
        print(f"❌ DNS 解析失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


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


def create_daytona_backend_with_skills(ngrok_url: str | None = None):
    """创建 Daytona Sandbox，上传 skills，并返回 backend。

    参数:
        ngrok_url: ngrok URL，用于获取 IP 白名单。如果提供，将允许沙箱访问该 IP。
                 例如: https://nell-pluteal-doria.ngrok-free.dev

    返回:
        tuple: (backend, daytona, sandbox)
    """
    print("🚀 创建 Daytona 沙箱...")

    # 初始化 Daytona
    daytona = Daytona()

    # 准备网络白名单
    network_allow_list = None
    if ngrok_url:
        print(f"🔍 获取 ngrok IP 地址: {ngrok_url}")
        ngrok_ip = get_ngrok_ip(ngrok_url)
        if ngrok_ip:
            # 使用 /32 表示单个 IP
            # 注意：Daytona 最多支持 5 个 CIDR
            network_allow_list = f"{ngrok_ip}/32"
            print(f"✅ 将允许沙箱访问: {network_allow_list}")
        else:
            print("⚠️  无法获取 ngrok IP，继续创建沙箱（可能无法访问 MCP 服务）")

    # 创建沙箱（使用 ngrok IP 白名单）
    if network_allow_list:
        params = CreateSandboxBaseParams(network_allow_list=network_allow_list)
        sandbox = daytona.create(params)
    else:
        sandbox = daytona.create()

    print(f"✅ 沙箱创建成功: {sandbox.id}")

    # 诊断网络访问
    print("\n🔍 诊断沙箱网络访问...")
    if ngrok_url:
        print(f"   预期可访问 ngrok: {ngrok_url}")
    print()

    try:
        # 测试1: ping Google DNS
        ping_result = sandbox.process.exec("ping -c 1 8.8.8.8", timeout=10)
        print(
            f"  ✓ Ping 8.8.8.8: {ping_result.result.strip() if ping_result.result else '成功'}"
        )
    except Exception as e:
        print(f"  ✗ Ping 8.8.8.8 失败: {e}")

    try:
        # 测试2: curl 外部 HTTP
        curl_result = sandbox.process.exec(
            "curl -s -o /dev/null -w '%{http_code}' https://www.google.com", timeout=15
        )
        if curl_result.result and curl_result.result.strip() == "200":
            print(f"  ✓ HTTPS 访问 google.com: 成功")
        else:
            print(f"  ✗ HTTPS 访问 google.com: 返回状态 {curl_result.result}")
    except Exception as e:
        print(f"  ✗ HTTPS 访问 google.com 失败: {e}")

    if ngrok_url:
        try:
            # 测试3: 尝试访问 ngrok 地址
            print(f"  🔄 测试访问 ngrok: {ngrok_url}/sse")
            ngrok_result = sandbox.process.exec(
                f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 10 {ngrok_url}/sse",
                timeout=20,
            )
            if ngrok_result.result and ngrok_result.result.strip() == "200":
                print(f"  ✓ ngrok 访问: 成功 (HTTP 200)")
            else:
                status = (
                    ngrok_result.result.strip() if ngrok_result.result else "无响应"
                )
                print(f"  ⚠ ngrok 访问: HTTP {status} (可能需要检查 MCP 服务状态)")
        except Exception as e:
            print(f"  ✗ ngrok 访问失败: {e}")

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


def build_agent_with_daytona(ngrok_url: str | None = None) -> tuple[Any, Daytona, Any]:
    """构建使用 Daytona backend 的 Deep Agent。

    参数:
        ngrok_url: ngrok URL，用于配置沙箱网络白名单。例如: https://xxx.ngrok-free.dev

    返回:
        tuple: (agent, daytona, sandbox)
    """
    # 创建 Daytona backend（包含上传 skills）
    backend, daytona, sandbox = create_daytona_backend_with_skills(ngrok_url=ngrok_url)

    # 配置 LLM
    os.environ["OPENAI_API_KEY"] = GLM_API_KEY
    llm = ChatOpenAI(model="glm-5", base_url="https://open.bigmodel.cn/api/paas/v4")

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


def demo_read_sales_script(
    agent: Any, use_ngrok: bool = False, ngrok_url: str | None = None
):
    """演示读取销售脚本内容。

    参数:
        agent: Deep Agent 实例
        use_ngrok: 是否使用 ngrok 在沙箱内执行（需要 ngrok_url）
        ngrok_url: ngrok URL，例如 https://xxx.ngrok-free.dev

    说明:
        - use_ngrok=False (默认): 在宿主机执行，使用 localhost:8000
        - use_ngrok=True: 在沙箱内执行，使用 ngrok URL
    """
    print("\n" + "=" * 60)
    print("演示 2: 调用销售 MCP 工具")
    print("=" * 60)

    script_path = (
        PROJECT_ROOT / "skills" / "万销销售场景" / "scripts" / "call_sales_mcp.py"
    )

    # 确定 base_url
    if use_ngrok and ngrok_url:
        base_url = ngrok_url
        print(f"🌐 使用 ngrok 执行: {base_url}")
        print("   （沙箱内通过 ngrok 访问 MCP）")
    else:
        base_url = "http://127.0.0.1:8000"
        print(f"💻 使用本地地址: {base_url}")
        print("   （在宿主机执行，绕过沙箱网络限制）")

    # 执行脚本
    cmd = [
        "uv",
        "run",
        "python",
        str(script_path),
        "intelligent_judgment",
        "--customer-name",
        "张三",
        "--base-url",
        base_url,
    ]

    print(f"\n📞 执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT)
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            print("\n✅ MCP 调用成功:")
            print(json.dumps(output, ensure_ascii=False, indent=2))

            # 让 agent 分析结果
            agent_result = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"MCP 工具返回结果如下，请分析并总结:\n```json\n{json.dumps(output, ensure_ascii=False)}\n```",
                        }
                    ]
                },
                config={"configurable": {"thread_id": "demo-read"}},
            )

            print("\n📝 Agent 分析:")
            for msg in agent_result.get("messages", []):
                content = (
                    msg.get("content", "")
                    if isinstance(msg, dict)
                    else getattr(msg, "content", "")
                )
                if content:
                    print(f"  {content}")
        else:
            print(f"\n❌ MCP 调用失败:")
            print(f"  返回码: {result.returncode}")
            print(f"  错误输出: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("\n❌ MCP 调用超时（30秒）")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback

        traceback.print_exc()


def main():
    """主函数。"""
    print("=" * 60)
    print("Daytona + DeepAgents 最小验证脚本（支持 ngrok 白名单）")
    print("=" * 60)
    print()

    agent = None
    daytona = None
    sandbox = None

    try:
        # 构建 Agent（传入 ngrok URL 以配置网络白名单）
        ngrok_url = NGROK_URL if NGROK_URL else None
        if ngrok_url:
            print(f"🌐 将配置 ngrok 白名单: {ngrok_url}")
        agent, daytona, sandbox = build_agent_with_daytona(ngrok_url=ngrok_url)

        # 运行演示
        demo_list_skills(agent)

        # 根据是否配置了 NGROK_URL 决定演示方式
        if ngrok_url:
            print("\n🌐 使用 ngrok 方案：沙箱通过 ngrok 访问 MCP")
            demo_read_sales_script(agent, use_ngrok=True, ngrok_url=ngrok_url)
        else:
            print("\n💻 使用本地方案：在宿主机执行 MCP 调用")
            demo_read_sales_script(agent, use_ngrok=False)

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
