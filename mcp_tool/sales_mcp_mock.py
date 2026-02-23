from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict

# 初始化 MCP 服务器
mcp = FastMCP("SalesScenarioMockTools")

# ==========================================
# Mock 数据区
# ==========================================

# 1. 客户特征与意愿映射 Mock 数据
MOCK_CUSTOMER_DB = {
    "张三": {
        "age": 35,
        "behavior": "多次查看出单链接",
        "intent_level": "高意向",
        "scene_type": "简单场景",
        "tag": "价格敏感型",
    },
    "李四": {
        "age": 42,
        "behavior": "浏览了产品对比页但未点击购买",
        "intent_level": "中意向",
        "scene_type": "需要培育",
        "tag": "注重保障全面性",
    },
    "王五": {
        "age": 28,
        "behavior": "第一次点击咨询，询问基础概念",
        "intent_level": "低意向",
        "scene_type": "复杂场景",
        "tag": "小白客户",
    },
}

# ==========================================
# 工具定义区 (MCP Tools)
# ==========================================


@mcp.tool()
def intelligent_judgment(customer_name: str) -> dict:
    """
    1. 智能判断工具：根据客户姓名，映射并返回客户的意愿和特征。
    """
    if customer_name in MOCK_CUSTOMER_DB:
        customer_info = MOCK_CUSTOMER_DB[customer_name]
        return {
            "status": "success",
            "message": f"成功匹配客户：{customer_name}",
            "data": customer_info,
        }
    return {"status": "error", "message": "未找到该客户的特征数据", "data": None}


@mcp.tool()
def issue_policy_tool(customer_name: str, age: int, intent_level: str) -> dict:
    """
    2. 出单工具：输入客户信息，带出报价页面配置。
    """
    # Mock 报价数据
    base_price = 300 if age < 30 else (500 if age < 40 else 800)
    return {
        "tool_name": "直接出单工具",
        "action": "render_quote_page",
        "page_url": f"https://mock-insurance.com/quote?user={customer_name}&price={base_price}",
        "ui_elements": [
            "产品方案摘要",
            f"动态测算保费: {base_price}元",
            "一键投保按钮",
        ],
    }


@mcp.tool()
def nurturing_process_tools() -> dict:
    """
    3. 过程工具组合：返回用于中意向客户培育的三个工具组合，供前端演示替换与组合。
    """
    return {
        "tool_name": "过程工具组合",
        "available_tools": [
            {
                "id": "t_compare",
                "name": "产品对比",
                "desc": "生成多款产品优劣势对比表格",
            },
            {
                "id": "t_claims",
                "name": "理赔案例",
                "desc": "推送真实理赔成功案例，建立信任",
            },
            {
                "id": "t_needs",
                "name": "个人客户需求分析",
                "desc": "雷达图展示客户在重疾、医疗、意外的缺口",
            },
        ],
        "suggested_action": "display_tool_carousel",  # 建议前端以轮播或列表展示
    }


@mcp.tool()
def deep_guidance_tools() -> dict:
    """
    4. 深度引导流程工具：针对低意向/复杂场景的长线跟进工具。
    """
    return {
        "tool_name": "深度引导流程工具",
        "available_tools": [
            {
                "id": "d_knowledge",
                "name": "产品知识分享",
                "type": "资讯/海报",
                "desc": "软性科普文章与早安海报",
            },
            {
                "id": "d_marketing",
                "name": "内容营销素材库",
                "type": "代理人AI名片",
                "desc": "带有追踪功能的专业名片分享",
            },
            {
                "id": "d_care",
                "name": "定期关怀",
                "type": "日程提醒",
                "desc": "自动设置生日、节日问候提醒",
            },
        ],
    }


@mcp.tool()
def diagnose_stuck_status(
    current_tool_id: str, elapsed_seconds: int, customer_intent: str
) -> dict:
    """
    5 & 6. 智能判断卡点工具 (作为 Skill 封装在 Tool 内)
    根据前端触发的时间（倒计时工具产生的结果）、当前停留的工具页面、客户意愿，
    内置逻辑判断，决定下一步推送什么话术或卡片。
    """
    # 逻辑 6.1：出单场景，30秒未操作
    if current_tool_id == "issue_policy" and elapsed_seconds >= 30:
        return {
            "diagnosis": "出单卡顿",
            "trigger_action": "show_assist_card",
            "message": "出单工具未操作 | 30秒 | 需要帮您解释吗？",
            "next_step": "等待代理人点击'需要'，跳转操作指引",
        }

    # 逻辑 6.2：任意页面停留，2分钟 (120秒)
    if elapsed_seconds >= 120:
        return {
            "diagnosis": "理解困难/阅读时间过长",
            "trigger_action": "show_assist_card",
            "message": f"页面停留过长 | {elapsed_seconds//60}分钟 | 是否遇到理解困难？",
            "next_step": "弹出简版说明或核心卖点提炼工具",
        }

    # 扩展逻辑：如果是中低意向客户，卡顿时的干预可以不同
    if customer_intent in ["中意向", "低意向"] and elapsed_seconds >= 60:
        return {
            "diagnosis": "培育期犹豫",
            "trigger_action": "recommend_tool",
            "message": "客户可能还在犹豫，建议发送【理赔案例】促单",
            "next_step": "调用 nurturing_process_tools 的 t_claims",
        }

    # 未触发任何卡点
    return {"diagnosis": "正常操作中", "trigger_action": "none", "message": "继续监控"}


if __name__ == "__main__":
    print("Starting Sales Mock Tools MCP Server...")
    mcp.run()
