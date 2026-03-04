"""
LangChain Agent 和 Tools 注册模块
负责创建 LangChain Agent，注册 Sandbox 相关的 tools，并集成 VNC 可视化。
本模块使用 sandbox_manager.py 中封装的 SandboxManager 来管理 sandbox 生命周期。
"""

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 导入 sandbox 管理器
from sandbox_manager import SandboxManager

# 加载环境变量
load_dotenv()

# 全局 sandbox 管理器实例（单例模式）
_sandbox_manager: SandboxManager | None = None


def get_sandbox_manager() -> SandboxManager:
    """获取 sandbox 管理器实例（单例模式）"""
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = SandboxManager()
    return _sandbox_manager


# ============ LangChain Tools 定义 ============


@tool
def create_browser_sandbox(template_name: str = None, idle_timeout: int = 3000) -> str:
    """创建或获取一个浏览器 sandbox 实例。

    当需要访问网页、执行浏览器操作时，首先需要创建 sandbox。
    创建成功后，会返回 sandbox 信息，包括 VNC URL 用于可视化。

    Args:
        template_name: Sandbox 模板名称，如果不提供则从环境变量 BROWSER_TEMPLATE_NAME 读取
        idle_timeout: 空闲超时时间（秒），默认 3000 秒

    Returns:
        Sandbox 信息字符串，包括 ID、CDP URL、VNC URL
    """
    try:
        manager = get_sandbox_manager()

        # 如果 template_name 为空字符串，转换为 None 以便从环境变量读取
        if template_name == "":
            template_name = None

        info = manager.create(template_name=template_name, idle_timeout=idle_timeout)

        result = f"""✅ Sandbox 创建成功！

📋 Sandbox 信息:
- ID: {info['sandbox_id']}
- CDP URL: {info['cdp_url']}
"""
        vnc_url = info.get("vnc_url")
        if vnc_url:
            result += f"- VNC URL: {vnc_url}\n\n"
            result += (
                "提示: VNC 查看器应该已自动打开，您可以在浏览器中实时查看浏览器操作。"
            )
        else:
            result += "\n警告: 未获取到 VNC URL，可能无法使用可视化功能。"

        return result

    except Exception as e:
        return f"❌ 创建 Sandbox 失败: {str(e)}"


@tool
def get_sandbox_info() -> str:
    """获取当前 sandbox 的详细信息，包括 ID、CDP URL、VNC URL 等。

    当需要查看当前 sandbox 状态或获取 VNC 连接信息时使用此工具。

    Returns:
        Sandbox 信息字符串
    """
    try:
        manager = get_sandbox_manager()
        info = manager.get_info()

        result = f"""📋 当前 Sandbox 信息:
- Sandbox ID: {info['sandbox_id']}
- CDP URL: {info['cdp_url']}
"""
        if info.get("vnc_url"):
            result += f"- VNC URL: {info['vnc_url']}\n\n"
            result += "您可以使用 VNC URL 在浏览器中实时查看操作过程。\n"
            result += "   推荐使用 vnc.html 文件或 noVNC 客户端。"

        return result

    except RuntimeError as e:
        return f"⚠️ {str(e)}"
    except Exception as e:
        return f"❌ 获取 Sandbox 信息失败: {str(e)}"


class NavigateInput(BaseModel):
    """浏览器导航输入参数"""

    url: str = Field(description="要访问的网页 URL，必须以 http:// 或 https:// 开头")
    wait_until: str = Field(
        default="load",
        description="等待页面加载的状态: load, domcontentloaded, networkidle",
    )
    timeout: int = Field(default=30000, description="超时时间（毫秒），默认 30000")


@tool(args_schema=NavigateInput)
def navigate_to_url(url: str, wait_until: str = "load", timeout: int = 30000) -> str:
    """使用 sandbox 中的浏览器导航到指定 URL。

    当用户需要访问网页时使用此工具。导航后可以在 VNC 中实时查看页面。

    Args:
        url: 要访问的网页 URL
        wait_until: 等待页面加载的状态（load/domcontentloaded/networkidle）
        timeout: 超时时间（毫秒）

    Returns:
        导航结果描述
    """
    try:
        manager = get_sandbox_manager()

        if not manager.is_active():
            return "❌ 错误: 请先创建 sandbox"

        # 验证 URL
        if not url.startswith(("http://", "https://")):
            return f"❌ 错误: 无效的 URL 格式: {url}"

        cdp_url = manager.get_cdp_url()
        if not cdp_url:
            return "❌ 错误: 无法获取 CDP URL"

        # 使用 Playwright 连接浏览器并导航
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(cdp_url)
                pages = browser.contexts[0].pages if browser.contexts else []

                if pages:
                    page = pages[0]
                else:
                    page = browser.new_page()

                page.goto(url, wait_until=wait_until, timeout=timeout)
                title = page.title()

                return f"✅ 已成功导航到: {url}\n📄 页面标题: {title}\n💡 您可以在 VNC 中查看页面内容。"

        except ImportError:
            return f"✅ 导航指令已发送: {url}\n💡 提示: 安装 playwright 以启用实际导航功能 (pip install playwright)"
        except Exception as e:
            return f"❌ 导航失败: {str(e)}"

    except Exception as e:
        return f"❌ 操作失败: {str(e)}"


@tool("browser_screenshot", description="在浏览器 sandbox 中截取当前页面截图")
def take_screenshot(filename: str = "screenshot.png") -> str:
    """截取浏览器当前页面的截图。

    Args:
        filename: 截图文件名，默认 "screenshot.png"

    Returns:
        操作结果
    """
    try:
        manager = get_sandbox_manager()

        if not manager.is_active():
            return "❌ 错误: 请先创建 sandbox"

        cdp_url = manager.get_cdp_url()
        if not cdp_url:
            return "❌ 错误: 无法获取 CDP URL"

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(cdp_url)
                pages = browser.contexts[0].pages if browser.contexts else []

                if pages:
                    page = pages[0]
                else:
                    return "❌ 错误: 没有打开的页面"

                page.screenshot(path=filename)
                return f"✅ 截图已保存: {filename}"

        except ImportError:
            return "❌ 错误: 需要安装 playwright (pip install playwright)"
        except Exception as e:
            return f"❌ 截图失败: {str(e)}"

    except Exception as e:
        return f"❌ 操作失败: {str(e)}"


@tool(
    "destroy_sandbox",
    description="销毁当前的 sandbox 实例，释放资源。注意：仅在程序退出或明确需要释放资源时使用，不要在一轮对话后销毁。",
)
def destroy_sandbox() -> str:
    """销毁当前的 sandbox 实例。

    重要提示：此工具应该仅在以下情况使用：
    - 程序即将退出
    - 明确需要释放资源
    - 用户明确要求销毁

    不要在一轮对话完成后就销毁 sandbox，因为 sandbox 可以在多轮对话中复用。

    Returns:
        操作结果
    """
    try:
        manager = get_sandbox_manager()
        result = manager.destroy()
        return result
    except Exception as e:
        return f"❌ 销毁失败: {str(e)}"


# ============ Agent 创建 ============


def create_browser_agent(system_prompt: str = None):
    """
    创建带有 sandbox 工具的 LangChain Agent

    Args:
        system_prompt: 自定义系统提示词，如果为 None 则使用默认提示词

    Returns:
        LangChain Agent 实例
    """
    # 配置 OpenRouter API（与 main.py 一致）
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("请设置环境变量 OPENROUTER_API_KEY")

    # 设置 API key 到环境变量（OpenAI SDK 兼容模式需要）
    os.environ["OPENAI_API_KEY"] = api_key

    base_url = "https://openrouter.ai/api/v1"
    model_name = os.getenv("MODEL_NAME", "z-ai/glm-4.7-flash")

    # 创建 LLM
    model = ChatOpenAI(
        model=model_name,
        base_url=base_url,
        temperature=0.1,
    )
    # 创建工具列表
    tools = [
        create_browser_sandbox,
        get_sandbox_info,
        navigate_to_url,
        take_screenshot,
        destroy_sandbox,
    ]

    # 默认系统提示词
    if system_prompt is None:
        system_prompt = """你是一个浏览器自动化助手，可以使用 sandbox 来访问和操作网页。

当用户需要访问网页时，请按以下步骤操作：
1. 首先创建或获取 sandbox（如果还没有）
2. 使用 navigate_to_url 导航到目标网页
3. 执行用户请求的操作
4. 如果需要，可以截取截图

重要提示：
- 创建 sandbox 后，会返回 VNC URL，用户可以使用它实时查看浏览器操作
- 所有操作都会在 VNC 中实时显示，方便调试和监控
- sandbox 可以在多轮对话中复用，不要在一轮对话完成后就销毁
- 只有在用户明确要求销毁时才使用 destroy_sandbox 工具
- 不要主动建议用户销毁 sandbox，除非用户明确要求
- 请始终用中文回复，确保操作准确、高效。"""

    # 创建 Agent
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
    )

    return agent


def get_available_tools():
    """获取所有可用的工具列表"""
    return [
        create_browser_sandbox,
        get_sandbox_info,
        navigate_to_url,
        take_screenshot,
        destroy_sandbox,
    ]
