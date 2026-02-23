from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional

# 初始化 FastMCP 服务器
mcp = FastMCP("SalesActivityMonitor")


class AgentActivityMetrics(BaseModel):
    idle_seconds: int = Field(default=0, description="工具未操作的静止时间（秒）")
    page_stay_seconds: int = Field(default=0, description="当前页面停留的总时长（秒）")
    repeated_view_count: int = Field(
        default=0, description="针对同一信息的反复查看次数"
    )
    unreplied_seconds: int = Field(
        default=0, description="客户提问后未回复的时长（秒）"
    )


@mcp.tool()
def diagnose_stuck_point(
    idle_seconds: int,
    page_stay_seconds: int,
    repeated_view_count: int,
    unreplied_seconds: int,
) -> dict:
    """
    智能诊断卡点工具。
    输入代理人当前的操作监控数据，输出是否卡住的判定、诊断原因以及推荐的辅助话术。
    """

    # 按照业务逻辑表的优先级进行判断（通常客户提问未回复的优先级最高）

    # 1. 客户提问未回复 > 1分钟 (60秒)
    if unreplied_seconds > 60:
        return {
            "status": "Stuck",
            "reason": "话术缺失/回复迟缓",
            "action_type": "Recommend_Script",
            "suggested_prompt": "需要话术支持吗？",
            "next_flow": "进入培育流程/推荐对应过程工具",
        }

    # 2. 工具未操作 > 30秒
    if idle_seconds > 30:
        return {
            "status": "Stuck",
            "reason": "操作迟疑",
            "action_type": "Provide_Guidance",
            "suggested_prompt": "需要帮您解释如何操作吗？",
            "next_flow": "智能诊断卡点 -> 推进对应过程工具",
        }

    # 3. 页面停留过长 > 2分钟 (120秒)
    if page_stay_seconds > 120:
        return {
            "status": "Stuck",
            "reason": "理解困难",
            "action_type": "Simplify_Info",
            "suggested_prompt": "是否遇到理解困难？",
            "next_flow": "智能诊断卡点 -> 推进对应过程工具",
        }

    # 4. 反复查看同信息 >= 3次
    if repeated_view_count >= 3:
        return {
            "status": "Stuck",
            "reason": "关键信息确认中",
            "action_type": "Clarify_Value",
            "suggested_prompt": "对这个部分有疑问？",
            "next_flow": "智能诊断卡点 -> 推进对应过程工具",
        }

    # 5. 如果都没有触发阈值，则判定为正常推进
    return {
        "status": "Progress",
        "reason": "操作正常",
        "action_type": "Continue",
        "suggested_prompt": None,
        "next_flow": "推进到下一步",
    }


if __name__ == "__main__":
    # 启动 MCP 服务器，默认通过 stdio 与大模型客户端进行通信
    print("Starting SalesActivityMonitor MCP Server...")
    mcp.run()
