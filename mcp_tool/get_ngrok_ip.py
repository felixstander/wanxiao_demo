#!/usr/bin/env python3
"""获取 ngrok 域名的 IP 地址，用于 Daytona sandbox 白名单配置。"""

import socket
import sys
from urllib.parse import urlparse


def get_ngrok_ip(ngrok_url: str) -> str | None:
    """解析 ngrok 域名对应的 IP 地址。
    
    参数:
        ngrok_url: ngrok URL，例如 https://nell-pluteal-doria.ngrok-free.dev
        
    返回:
        str: IP 地址，例如 203.168.241.43
        None: 解析失败
    """
    try:
        # 解析域名
        parsed = urlparse(ngrok_url)
        hostname = parsed.hostname
        
        if not hostname:
            print(f"❌ 无法解析 URL: {ngrok_url}")
            return None
        
        # 获取 IP 地址
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ {hostname} -> {ip_address}")
        return ip_address
        
    except socket.gaierror as e:
        print(f"❌ DNS 解析失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def main():
    """命令行入口。"""
    # 默认的 ngrok URL（可以从命令行参数覆盖）
    default_url = "https://nell-pluteal-doria.ngrok-free.dev"
    
    # 获取命令行参数
    ngrok_url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    print(f"🔍 解析 ngrok 域名: {ngrok_url}")
    ip = get_ngrok_ip(ngrok_url)
    
    if ip:
        print(f"\n📋 在 Daytona 中使用:")
        print(f'   network_allow_list="{ip}/32"')
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
