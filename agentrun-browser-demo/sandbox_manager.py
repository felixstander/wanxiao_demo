"""
Sandbox 生命周期管理模块
负责 AgentRun Browser Sandbox 的创建、管理和销毁。
提供统一的接口供 LangChain Agent 使用。
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class SandboxManager:
    """Sandbox 生命周期管理器"""
    
    def __init__(self):
        self._sandbox: Optional[Any] = None
        self._sandbox_id: Optional[str] = None
        self._cdp_url: Optional[str] = None
        self._vnc_url: Optional[str] = None
    
    def create(
        self,
        template_name: Optional[str] = None,
        idle_timeout: int = 3000
    ) -> Dict[str, Any]:
        """
        创建或获取一个浏览器 sandbox 实例
        
        Args:
            template_name: Sandbox 模板名称，如果为 None 则从环境变量读取
            idle_timeout: 空闲超时时间（秒），默认 3000 秒
            
        Returns:
            dict: 包含 sandbox_id, cdp_url, vnc_url 的字典
            
        Raises:
            RuntimeError: 创建失败时抛出异常
        """
        try:
            from agentrun.sandbox import Sandbox, TemplateType
            
            # 如果已有 sandbox，直接返回
            if self._sandbox is not None:
                return self.get_info()
            
            # 从环境变量获取模板名称
            if template_name is None:
                template_name = os.getenv(
                    "BROWSER_TEMPLATE_NAME",
                    "sandbox-browser-demo"
                )
            
            # 创建 sandbox
            self._sandbox = Sandbox.create(
                template_type=TemplateType.BROWSER,
                template_name=template_name,
                sandbox_idle_timeout_seconds=idle_timeout
            )
            
            self._sandbox_id = self._sandbox.sandbox_id
            self._cdp_url = self._get_cdp_url()
            self._vnc_url = self._get_vnc_url()
            
            return self.get_info()
            
        except ImportError as e:
            print(e)
            raise RuntimeError(
                "agentrun-sdk 未安装，请运行: pip install agentrun-sdk[playwright,server]"
            )
        except Exception as e:
            raise RuntimeError(f"创建 Sandbox 失败: {str(e)}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取当前 sandbox 的信息
        
        Returns:
            dict: 包含 sandbox_id, cdp_url, vnc_url 的字典
            
        Raises:
            RuntimeError: 如果没有活动的 sandbox
        """
        if self._sandbox is None:
            raise RuntimeError("没有活动的 sandbox，请先创建")
        
        return {
            "sandbox_id": self._sandbox_id,
            "cdp_url": self._cdp_url,
            "vnc_url": self._vnc_url,
        }
    
    def get_cdp_url(self) -> Optional[str]:
        """获取 CDP URL"""
        return self._sandbox.get_cdp_url()
    
    def _get_cdp_url(self) -> Optional[str]:
        """内部方法：获取 CDP URL"""
        if self._sandbox is None:
            return None
        return self._sandbox.get_cdp_url()
    
    def get_vnc_url(self) -> Optional[str]:
        """获取 VNC URL"""
        return self._sandbox.get_vnc_url()
    
    def _get_vnc_url(self) -> Optional[str]:
        """内部方法：获取 VNC URL"""
        if self._sandbox is None:
            return None
        return self._sandbox.get_vnc_url()
    
    def get_sandbox_id(self) -> Optional[str]:
        """获取 Sandbox ID"""
        return self._sandbox_id
    
    def destroy(self) -> str:
        """
        销毁当前的 sandbox 实例
        
        Returns:
            str: 操作结果描述
        """
        if self._sandbox is None:
            return "没有活动的 sandbox"
        
        try:
            sandbox_id = self._sandbox_id
            
            # 尝试销毁 sandbox
            if hasattr(self._sandbox, 'delete'):
                self._sandbox.delete()
            elif hasattr(self._sandbox, 'stop'):
                self._sandbox.stop()
            elif hasattr(self._sandbox, 'destroy'):
                self._sandbox.destroy()
            
            # 清理状态
            self._sandbox = None
            self._sandbox_id = None
            self._cdp_url = None
            self._vnc_url = None
            
            return f"Sandbox 已销毁: {sandbox_id}"
            
        except Exception as e:
            # 即使销毁失败，也清理本地状态
            self._sandbox = None
            self._sandbox_id = None
            self._cdp_url = None
            self._vnc_url = None
            return f"销毁 Sandbox 时出错: {str(e)}"
    
    def is_active(self) -> bool:
        """检查 sandbox 是否活跃"""
        return self._sandbox is not None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出，自动销毁"""
        self.destroy()
        return False


# 全局单例（可选，用于简单场景）
_global_manager: Optional[SandboxManager] = None


def get_global_manager() -> SandboxManager:
    """获取全局 SandboxManager 单例"""
    global _global_manager
    if _global_manager is None:
        _global_manager = SandboxManager()
    return _global_manager


def reset_global_manager():
    """重置全局 SandboxManager"""
    global _global_manager
    if _global_manager:
        _global_manager.destroy()
    _global_manager = None
