"""
LangChain + AgentRun Browser Sandbox 集成示例
主入口文件，演示如何使用 LangChain Agent 与 AgentRun Browser Sandbox 集成。
"""

import sys
import signal
import webbrowser
import urllib.parse
import threading
import http.server
import socketserver
from pathlib import Path
from dotenv import load_dotenv
from langchain_agent import create_browser_agent, get_sandbox_manager

# 加载环境变量
load_dotenv()

# 全局 HTTP 服务器实例
_http_server = None
_http_port = 8080

# 全局清理标志，用于防止重复清理
_cleanup_done = False


def start_http_server():
    """启动一个简单的 HTTP 服务器来提供 vnc.html"""
    global _http_server

    if _http_server is not None:
        return _http_port

    try:
        current_dir = Path(__file__).parent.absolute()

        class VNCRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(current_dir), **kwargs)

            def log_message(self, format, *args):
                # 静默日志，避免输出过多信息
                pass

        # 尝试启动服务器
        for port in range(_http_port, _http_port + 10):
            try:
                server = socketserver.TCPServer(("", port), VNCRequestHandler)
                server.allow_reuse_address = True

                # 在后台线程中运行服务器
                def run_server():
                    server.serve_forever()

                thread = threading.Thread(target=run_server, daemon=True)
                thread.start()

                _http_server = server
                return port

            except OSError:
                continue

        return None

    except Exception as e:
        print(f"启动 HTTP 服务器失败: {str(e)}")
        return None


def open_vnc_viewer(vnc_url: str):
    """
    自动打开 VNC 查看器并设置 VNC URL

    Args:
        vnc_url: VNC WebSocket URL
    """
    if not vnc_url:
        return

    try:
        # 获取当前文件所在目录
        current_dir = Path(__file__).parent.absolute()
        vnc_html_path = current_dir / "vnc.html"

        # 检查文件是否存在
        if not vnc_html_path.exists():
            print(f"警告: vnc.html 文件不存在: {vnc_html_path}")
            print_vnc_info(vnc_url)
            return

        # 启动 HTTP 服务器
        port = start_http_server()

        if port:
            # 编码 VNC URL 作为 URL 参数
            encoded_url = urllib.parse.quote(vnc_url, safe="")

            # 构建 HTTP URL
            http_url = f"http://localhost:{port}/vnc.html?url={encoded_url}"

            # 打开浏览器
            print(f"\n正在打开 VNC 查看器...")
            print(f"HTTP 服务器运行在: http://localhost:{port}")
            print(f"VNC URL: {vnc_url[:80]}...")
            print(f"完整 URL: {http_url[:100]}...")

            webbrowser.open(http_url)
            print(f"VNC 查看器已打开")
            print(f"VNC URL 已通过 URL 参数自动设置，页面加载后会自动连接")
        else:
            # 如果 HTTP 服务器启动失败，尝试使用 file:// 协议
            print(f"HTTP 服务器启动失败，尝试使用文件协议...")
            encoded_url = urllib.parse.quote(vnc_url, safe="")
            file_url = f"file://{vnc_html_path}?url={encoded_url}"
            webbrowser.open(file_url)
            print(f"VNC 查看器已打开（使用文件协议）")
            print(f"提示: 如果无法自动连接，请手动复制 VNC URL 到输入框")

    except Exception as e:
        print(f"自动打开 VNC 查看器失败: {str(e)}")
        print_vnc_info(vnc_url)


def print_vnc_info(vnc_url: str):
    """打印 VNC 连接信息"""
    if not vnc_url:
        return

    print("\n" + "=" * 60)
    print("VNC 可视化连接信息")
    print("=" * 60)
    print(f"\nVNC URL: {vnc_url}")
    print("\n使用方式:")
    print("   1. 使用 noVNC 客户端连接")
    print("   2. 或在浏览器中访问 VNC 查看器页面")
    print("   3. 实时查看浏览器操作过程")
    print("\n" + "=" * 60 + "\n")


def cleanup_sandbox():
    """
    清理 sandbox 资源
    这个函数可以被信号处理器、异常处理器和正常退出流程调用
    """
    global _cleanup_done

    # 防止重复清理
    if _cleanup_done:
        return

    _cleanup_done = True

    try:
        manager = get_sandbox_manager()
        if manager.is_active():
            print("\n" + "=" * 60)
            print("正在清理 sandbox...")
            print("=" * 60)
            result = manager.destroy()
            print(f"清理结果: {result}\n")
        else:
            print("\n没有活动的 sandbox 需要清理\n")
    except Exception as e:
        print(f"\n清理 sandbox 时出错: {str(e)}\n")


def signal_handler(signum, frame):
    """
    信号处理器，处理 Ctrl+C (SIGINT) 和其他信号

    Args:
        signum: 信号编号
        frame: 当前堆栈帧
    """
    print("\n\n收到中断信号，正在清理资源...")
    cleanup_sandbox()
    print("清理完成")
    sys.exit(0)


def main():
    """主函数"""
    global _cleanup_done

    # 重置清理标志
    _cleanup_done = False

    # 注册信号处理器，处理 Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, signal_handler)

    # 在 Windows 上，SIGBREAK 也可以处理
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal_handler)

    print("=" * 60)
    print("LangChain + AgentRun Browser Sandbox 集成示例")
    print("=" * 60)
    print()

    try:
        # 创建 Agent
        print("正在初始化 LangChain Agent...")
        agent = create_browser_agent()
        print("Agent 初始化完成\n")

        # 示例查询
        queries = [
            "创建一个浏览器 sandbox",
            "获取当前 sandbox 的信息，包括 VNC URL",
            "导航到 https://www.aliyun.com",
            "截取当前页面截图",
        ]

        # 执行查询
        for i, query in enumerate(queries, 1):
            print(f"\n{'=' * 60}")
            print(f"查询 {i}: {query}")
            print(f"{'=' * 60}\n")

            try:
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": query}]}
                )

                # 提取最后一条消息的内容
                output = (
                    result.get("messages", [])[-1].content
                    if isinstance(result.get("messages"), list)
                    else result.get("output", str(result))
                )

                print(f"\n结果:\n{output}\n")

                # 如果是创建 sandbox，自动打开 VNC 查看器
                if i == 1:
                    try:
                        # 等待一下确保 sandbox 完全创建
                        import time

                        time.sleep(1)

                        manager = get_sandbox_manager()
                        if manager.is_active():
                            info = manager.get_info()
                            vnc_url = info.get("vnc_url")

                            if vnc_url:
                                print(f"\n检测到 VNC URL: {vnc_url[:80]}...")
                                open_vnc_viewer(vnc_url)
                                print_vnc_info(vnc_url)
                            else:
                                print(
                                    "\n警告: 未获取到 VNC URL，请检查 sandbox 创建是否成功"
                                )
                    except Exception as e:
                        print(f"打开 VNC 查看器时出错: {str(e)}")
                        import traceback

                        traceback.print_exc()

                # 如果是获取信息，显示 VNC 信息
                elif i == 2:
                    try:
                        manager = get_sandbox_manager()
                        if manager.is_active():
                            info = manager.get_info()
                            if info.get("vnc_url"):
                                print_vnc_info(info["vnc_url"])
                    except:
                        pass

            except Exception as e:
                print(f"查询失败: {str(e)}\n")
                import traceback

                traceback.print_exc()

        # 交互式查询
        print("\n" + "=" * 60)
        print("进入交互模式（输入 'quit' 或 'exit' 退出，Ctrl+C 或 Ctrl+D 中断）")
        print("=" * 60 + "\n")

        while True:
            try:
                user_input = input("请输入您的查询: ").strip()
            except EOFError:
                # 处理 Ctrl+D (EOF)
                print("\n\n检测到输入结束 (Ctrl+D)，正在清理资源...")
                cleanup_sandbox()
                print("清理完成")
                break
            except KeyboardInterrupt:
                # 处理 Ctrl+C (在 input 调用期间)
                print("\n\n检测到中断信号 (Ctrl+C)，正在清理资源...")
                cleanup_sandbox()
                print("清理完成")
                break

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "退出"]:
                print("\nBye")
                # 退出前清理 sandbox
                cleanup_sandbox()
                break

            try:
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": user_input}]}
                )

                output = (
                    result.get("messages", [])[-1].content
                    if isinstance(result.get("messages"), list)
                    else result.get("output", str(result))
                )

                print(f"\n结果:\n{output}\n")

                # 检查是否需要打开或显示 VNC 信息
                user_input_lower = user_input.lower()
                if "创建" in user_input_lower and "sandbox" in user_input_lower:
                    # 如果是创建 sandbox，自动打开 VNC 查看器
                    try:
                        # 等待一下确保 sandbox 完全创建
                        import time

                        time.sleep(1)

                        manager = get_sandbox_manager()
                        if manager.is_active():
                            info = manager.get_info()
                            vnc_url = info.get("vnc_url")

                            if vnc_url:
                                print(f"\n检测到 VNC URL: {vnc_url[:80]}...")
                                open_vnc_viewer(vnc_url)
                                print_vnc_info(vnc_url)
                            else:
                                print(
                                    "\n警告: 未获取到 VNC URL，请检查 sandbox 创建是否成功"
                                )
                    except Exception as e:
                        print(f"打开 VNC 查看器时出错: {str(e)}")
                        import traceback

                        traceback.print_exc()

                elif "sandbox" in user_input_lower or "vnc" in user_input_lower:
                    # 其他情况只显示信息
                    try:
                        manager = get_sandbox_manager()
                        if manager.is_active():
                            info = manager.get_info()
                            if info.get("vnc_url"):
                                print_vnc_info(info["vnc_url"])
                    except:
                        pass

            except Exception as e:
                print(f"查询失败: {str(e)}\n")
                import traceback

                traceback.print_exc()

        # 清理资源（仅在程序正常退出时）
        cleanup_sandbox()

    except KeyboardInterrupt:
        # 处理顶层 KeyboardInterrupt (Ctrl+C)
        print("\n\n检测到中断信号 (Ctrl+C)，正在清理资源...")
        cleanup_sandbox()
        print("清理完成")
        sys.exit(0)

    except EOFError:
        # 处理顶层 EOFError (Ctrl+D)
        print("\n\n检测到输入结束 (Ctrl+D)，正在清理资源...")
        cleanup_sandbox()
        print("清理完成")
        sys.exit(0)

    except ValueError as e:
        print(f"配置错误: {str(e)}")
        print("\n提示: 请确保已设置以下环境变量:")
        print("   - OPENROUTER_API_KEY: OpenRouter API Key (用于调用大模型)")
        print("   - ALIBABA_CLOUD_ACCOUNT_ID: 阿里云账号 ID")
        print("   - ALIBABA_CLOUD_ACCESS_KEY_ID: 访问密钥 ID")
        print("   - ALIBABA_CLOUD_ACCESS_KEY_SECRET: 访问密钥 Secret")
        print("   - MODEL_NAME: 模型名称（默认: z-ai/glm-4.5-flash）")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback

        traceback.print_exc()
        # 发生错误时也尝试清理
        cleanup_sandbox()


if __name__ == "__main__":
    main()
