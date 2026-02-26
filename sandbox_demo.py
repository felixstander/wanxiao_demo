#!/usr/bin/env python3
"""
使用 Daytona SDK 沙箱上传并执行 Python 脚本。

功能:
1. 创建 Daytona 沙箱
2. 上传本地文件到沙箱
3. 通过 shell 执行命令
4. 获取执行结果

安装依赖:
    uv add daytona python-dotenv

环境变量:
    DAYTONA_API_KEY=your_api_key
    DAYTONA_SERVER_URL=https://app.daytona.io/api  (可选)
    DAYTONA_TARGET=us  (可选，默认为 us)

获取 API Key:
    https://app.daytona.io/dashboard
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查必要的环境变量
DAYTONA_API_KEY = os.getenv("DAYTONA_API_KEY")
if not DAYTONA_API_KEY:
    print("错误: 请设置 DAYTONA_API_KEY 环境变量")
    print("获取 API Key: https://app.daytona.io/dashboard")
    sys.exit(1)

# 导入 Daytona SDK
from daytona import Daytona, DaytonaConfig, CreateSandboxBaseParams, FileUpload

# 文件路径配置
LOCAL_FILE_PATH = "./skills/万销销售场景/scripts/call_sales_mcp.py"
REMOTE_FILE_PATH = "/home/daytona/call_sales_mcp.py"


def upload_and_execute():
    """上传文件到 Daytona 沙箱并执行 shell 命令。"""
    
    print("🚀 初始化 Daytona SDK...")
    
    # 初始化 Daytona（从环境变量读取配置）
    # 环境变量: DAYTONA_API_KEY, DAYTONA_SERVER_URL, DAYTONA_TARGET
    daytona = Daytona()
    
    # 或者使用显式配置
    # config = DaytonaConfig(
    #     api_key=DAYTONA_API_KEY,
    #     server_url=os.getenv("DAYTONA_SERVER_URL", "https://app.daytona.io/api"),
    #     target=os.getenv("DAYTONA_TARGET", "us"),
    # )
    # daytona = Daytona(config)
    
    print("📦 创建沙箱...")
    
    # 创建沙箱（使用默认 Python 环境）
    sandbox = daytona.create()
    
    # 或者使用自定义参数
    # params = CreateSandboxBaseParams(
    #     language="python",
    #     env_vars={"PYTHONUNBUFFERED": "1"},
    #     auto_stop_interval=30,  # 30分钟后自动停止
    # )
    # sandbox = daytona.create(params)
    
    print(f"✅ 沙箱创建成功: {sandbox.id}")
    
    try:
        # 检查本地文件是否存在
        local_path = Path(LOCAL_FILE_PATH)
        if not local_path.exists():
            print(f"❌ 本地文件不存在: {LOCAL_FILE_PATH}")
            sys.exit(1)
        
        print(f"\n📁 本地文件: {local_path.absolute()}")
        print(f"📊 文件大小: {local_path.stat().st_size} bytes")
        
        # 1. 上传文件到沙箱
        print(f"\n📤 正在上传文件到沙箱...")
        
        # 读取文件内容
        with open(local_path, "rb") as f:
            file_content = f.read()
        
        # 使用 FileUpload 上传文件
        upload_file = FileUpload(
            source=file_content,
            destination=REMOTE_FILE_PATH
        )
        sandbox.fs.upload_files([upload_file])
        
        print(f"✅ 文件上传成功: {REMOTE_FILE_PATH}")
        
        # 2. 验证文件是否上传成功
        print("\n🔍 验证文件是否存在...")
        ls_result = sandbox.process.exec("ls -la /home/daytona/")
        print(f"沙箱目录内容:\n{ls_result.result}")
        
        # 3. 安装必要的依赖
        print("\n📦 检查并安装必要的依赖...")
        install_result = sandbox.process.exec(
            "pip install urllib3 --quiet 2>&1 || echo '依赖安装完成或已存在'"
        )
        print(f"依赖安装结果:\n{install_result.result}")
        
        # 4. 执行 Python 脚本（显示帮助）
        print(f"\n▶️  正在执行脚本（显示帮助信息）...")
        print("=" * 60)
        
        help_result = sandbox.process.exec(f"python3 {REMOTE_FILE_PATH} --help")
        print(help_result.result)
        
        if help_result.exit_code != 0:
            print(f"⚠️  退出码: {help_result.exit_code}")
        
        print("=" * 60)
        
        # 5. 尝试执行实际工具调用（需要 MCP 服务）
        print("\n📝 尝试执行工具调用（需要 MCP 服务）...")
        tool_call_result = sandbox.process.exec(
            f"timeout 10 python3 {REMOTE_FILE_PATH} intelligent_judgment --customer-name 张三 2>&1 || echo '执行超时或失败（可能是 MCP 服务未运行）'"
        )
        print(f"结果:\n{tool_call_result.result}")
        
        # 6. 检查生成的文件
        print("\n📥 检查生成的文件...")
        find_result = sandbox.process.exec(
            r"find /home/daytona -type f \( -name '*.json' -o -name '*.txt' -o -name '*.log' \) 2>/dev/null"
        )
        if find_result.result.strip():
            print(f"发现的文件:\n{find_result.result}")
        else:
            print("没有生成额外的文件")
        
        print("\n✅ 所有操作完成!")
        
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # 关闭沙箱
        print("\n🧹 正在清理沙箱...")
        daytona.delete(sandbox)
        print("✅ 沙箱已关闭")


def demo_code_execution():
    """演示直接执行 Python 代码。"""
    
    print("\n" + "=" * 60)
    print("演示: 直接执行 Python 代码")
    print("=" * 60)
    
    daytona = Daytona()
    sandbox = daytona.create()
    
    print(f"✅ 沙箱创建成功: {sandbox.id}")
    
    try:
        # 执行 Python 代码
        python_code = '''
import sys
print("Hello from Daytona sandbox!")
print(f"Python version: {sys.version}")
result = 42 * 2
print(f"计算结果: {result}")
'''
        
        print("\n▶️  执行 Python 代码...")
        
        # 使用 process.code_run 执行 Python 代码
        code_result = sandbox.process.code_run(python_code)
        
        print(f"\n执行结果:")
        print(f"  stdout: {code_result.result}")
        print(f"  artifacts: {code_result.artifacts}")
        
        # 也可以获取更详细的输出
        if hasattr(code_result, 'stdout'):
            print(f"  详细输出: {code_result.stdout}")
        
    finally:
        print("\n🧹 正在清理沙箱...")
        daytona.delete(sandbox)
        print("✅ 沙箱已关闭")


def demo_with_charts():
    """演示生成图表。"""
    
    print("\n" + "=" * 60)
    print("演示: 生成图表")
    print("=" * 60)
    
    daytona = Daytona()
    sandbox = daytona.create()
    
    print(f"✅ 沙箱创建成功: {sandbox.id}")
    
    try:
        python_code = '''
import matplotlib.pyplot as plt
import numpy as np

# 生成数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 创建图表
plt.figure(figsize=(8, 4))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave Example')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("图表生成完成!")
'''
        
        print("\n▶️  执行 Python 代码（生成图表）...")
        code_result = sandbox.process.code_run(python_code)
        
        print(f"\n执行结果:")
        print(f"  result: {code_result.result}")
        print(f"  artifacts: {code_result.artifacts}")
        
        # 处理图表
        if code_result.artifacts and code_result.artifacts.charts:
            for i, chart in enumerate(code_result.artifacts.charts):
                print(f"  Chart {i}: {chart}")
        
    finally:
        print("\n🧹 正在清理沙箱...")
        daytona.delete(sandbox)
        print("✅ 沙箱已关闭")


def main():
    """主函数入口。"""
    print("=" * 60)
    print("Daytona SDK Demo")
    print("=" * 60)
    print()
    
    # 1. 基础功能演示
    upload_and_execute()
    
    # 2. 代码执行演示
    print("\n")
    demo_code_execution()
    
    # 3. 图表生成演示
    print("\n")
    demo_with_charts()


if __name__ == "__main__":
    main()
