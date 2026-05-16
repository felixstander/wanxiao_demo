#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Car_Negotiate_Middleware

车险谈判中间件，用于在 agent 执行前后注入和收集信息，
以提升 agent 的 skill 选择准确性和对话效果。

- before_agent: 分析用户意图，注入 skill 选择指导
- after_agent: 抽取对话关键信息，用于效果评估和优化
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    after_agent,
    before_agent,
)
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

# 用户意图 -> 推荐 Skill 的映射
INTENT_SKILL_MAP = {
    # M1 报价模块
    "报个价": "car-quote",
    "报一下价": "car-quote",
    "询价": "car-quote",
    "报价": "car-quote",
    "多少钱": "car-quote",
    "保费多少": "car-quote",
    "保费": "car-quote",
    "转保": "car-quote",
    
    # M2 方案讲解模块
    "保什么": "car-plan-explain",
    "保障范围": "car-plan-explain",
    "险种": "car-plan-explain",
    "讲解": "car-plan-explain",
    "什么意思": "car-plan-explain",
    "详细介绍": "car-plan-explain",
    
    # M3 方案调整模块
    "加保": "car-plan-adjust",
    "加一个": "car-plan-adjust",
    "加一个险": "car-plan-adjust",
    "减保": "car-plan-adjust",
    "不要了": "car-plan-adjust",
    "去掉": "car-plan-adjust",
    "更换": "car-plan-adjust",
    "调整": "car-plan-adjust",
    "升到": "car-plan-adjust",
    "降到": "car-plan-adjust",
    
    # M4 价格谈判模块
    "太贵": "car-price-negotiate",
    "有点贵": "car-price-negotiate",
    "便宜": "car-price-negotiate",
    "能不能便宜": "car-price-negotiate",
    "便宜点": "car-price-negotiate",
    "优惠": "car-price-negotiate",
    "折扣": "car-price-negotiate",
    "嫌贵": "car-price-negotiate",
    "价格有点高": "car-price-negotiate",
    
    # M5 价格差异解释模块
    "比去年贵": "car-price-diff-explain",
    "涨价": "car-price-diff-explain",
    "贵了好多": "car-price-diff-explain",
    "怎么贵了": "car-price-diff-explain",
    "贵这么多": "car-price-diff-explain",
    
    # M6 服务卡券模块
    "赠品": "car-service-card",
    "礼品": "car-service-card",
    "卡券": "car-service-card",
    "有什么送": "car-service-card",
    "送什么": "car-service-card",
    "增值服务": "car-service-card",
    
    # M7 竞品对比模块
    "人保": "car-competitor-compare",
    "太平洋": "car-competitor-compare",
    "国寿": "car-competitor-compare",
    "对比": "car-competitor-compare",
    "别家": "car-competitor-compare",
    "其他公司": "car-competitor-compare",
    
    # M8 促单模块
    "考虑": "car-promotion",
    "犹豫": "car-promotion",
    "再想想": "car-promotion",
    "促单": "car-promotion",
    "再考虑一下": "car-promotion",
    "再问问": "car-promotion",
    
    # M9 理赔服务模块
    "理赔": "car-claim-service",
    "出险": "car-claim-service",
    "赔付": "car-claim-service",
    "快吗": "car-claim-service",
    
    # M10 投保支付模块
    "付款": "car-payment",
    "支付": "car-payment",
    "购买": "car-payment",
    "办理": "car-payment",
    "确定": "car-payment",
    "就这个了": "car-payment",
    "确定了": "car-payment",
    "现在就办": "car-payment",
}

SKILL_GUIDANCE = {
    "car-quote": "当前用户意图为【询价/报价】，请优先使用 car-quote skill 获取并播报车险报价。",
    "car-plan-explain": "当前用户意图为【了解保障详情】，请优先使用 car-plan-explain skill 讲解险种和保障范围。",
    "car-plan-adjust": "当前用户意图为【调整方案】，请优先使用 car-plan-adjust skill 修改保险方案并重新报价。",
    "car-price-negotiate": "当前用户意图为【价格异议】，请优先使用 car-price-negotiate skill 运用谈判策略争取成交。",
    "car-price-diff-explain": "当前用户意图为【质疑价格变化】，请优先使用 car-price-diff-explain skill 归因分析并解释。",
    "car-service-card": "当前用户意图为【询问优惠/赠品】，请优先使用 car-service-card skill 查询并推荐可用赠品。",
    "car-competitor-compare": "当前用户意图为【竞品对比】，请优先使用 car-competitor-compare skill 进行结构化对比。",
    "car-promotion": "当前用户意图为【犹豫/考虑中】，请优先使用 car-promotion skill 运用促单策略推动决策。",
    "car-claim-service": "当前用户意图为【理赔咨询】，请优先使用 car-claim-service skill 介绍理赔流程和优势。",
    "car-payment": "当前用户意图为【确认购买/支付】，请优先使用 car-payment skill 引导完成投保支付。",
}


def _detect_intent(user_text: str) -> tuple[str, str]:
    """基于关键词检测用户意图和推荐 skill。
    
    Returns:
        (intent, recommended_skill)
    """
    user_text_lower = user_text.lower()
    for keyword, skill in INTENT_SKILL_MAP.items():
        if keyword in user_text_lower:
            return keyword, skill
    return "未知", ""


def _extract_user_message(state: AgentState) -> str:
    """从 state 中提取最后一条用户消息。"""
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, dict):
            if msg.get("role") == "user" or msg.get("type") == "human":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content
        else:
            # langchain message object
            role = getattr(msg, "type", "")
            if role in ("human", "HumanMessage"):
                content = getattr(msg, "content", "")
                if isinstance(content, str):
                    return content
    return ""


def _extract_ai_message(state: AgentState) -> str:
    """从 state 中提取最后一条 AI 消息。"""
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, dict):
            if msg.get("role") == "assistant" or msg.get("type") == "ai":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content
        else:
            role = getattr(msg, "type", "")
            if role in ("ai", "AIMessage"):
                content = getattr(msg, "content", "")
                if isinstance(content, str):
                    return content
    return ""


class CarNegotiateMiddleware(AgentMiddleware):
    """车险谈判中间件。
    
    在 before_agent 阶段分析用户意图并注入 skill 选择指导，
    在 after_agent 阶段使用大模型抽取对话关键信息。
    """

    def __init__(
        self,
        extraction_llm: ChatOpenAI | None = None,
        output_dir: str | Path = "./middleware_logs",
    ):
        super().__init__()
        self.extraction_llm = extraction_llm
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._session_data: list[dict[str, Any]] = []

    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """在 agent 执行前分析用户意图，注入 skill 选择指导。"""
        user_text = _extract_user_message(state)
        if not user_text:
            return None

        intent, recommended_skill = _detect_intent(user_text)
        
        # 记录检测到的意图
        print(f"\n[CarNegotiateMiddleware] 用户意图检测: '{intent}' -> 推荐 skill: {recommended_skill or '无'}")

        # 构建注入消息
        guidance_parts = [
            "【中间件意图分析】",
            f"用户输入: {user_text}",
            f"检测到意图: {intent}",
        ]
        
        if recommended_skill and recommended_skill in SKILL_GUIDANCE:
            guidance_parts.append(SKILL_GUIDANCE[recommended_skill])
            guidance_parts.append(
                "注意：以上仅为推荐，如用户问题涉及多个模块，请按需调用相应 skill。"
            )
        else:
            guidance_parts.append(
                "未检测到明确意图，请根据用户问题自主选择最合适的 skill。"
            )
        
        guidance_text = "\n".join(guidance_parts)
        
        # 将指导信息作为 system message 插入到 messages 开头
        # 由于 state["messages"] 是列表，我们可以直接修改
        messages = state.get("messages", [])
        if isinstance(messages, list):
            # 找到第一个非 system 消息的位置，在其前面插入
            insert_idx = 0
            for i, msg in enumerate(messages):
                msg_type = ""
                if isinstance(msg, dict):
                    msg_type = msg.get("type", "") or msg.get("role", "")
                else:
                    msg_type = getattr(msg, "type", "")
                if msg_type not in ("system", "SystemMessage"):
                    insert_idx = i
                    break
                insert_idx = i + 1
            
            # 创建 SystemMessage
            sys_msg = SystemMessage(content=guidance_text)
            messages.insert(insert_idx, sys_msg)
            
            # 直接修改 state，不需要返回 messages（因为我们已经插入了）
            # 但为了安全，返回 None 表示没有额外的 state 更新
        
        return None

    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """在 agent 执行后抽取对话关键信息。"""
        user_text = _extract_user_message(state)
        ai_text = _extract_ai_message(state)
        
        if not user_text or not ai_text:
            return None

        print(f"\n[CarNegotiateMiddleware] 开始抽取对话关键信息...")

        # 使用 LLM 抽取关键信息
        extracted = self._extract_with_llm(user_text, ai_text)
        
        # 保存到会话数据
        record = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_text,
            "ai_message": ai_text[:500] if len(ai_text) > 500 else ai_text,
            "extracted": extracted,
        }
        self._session_data.append(record)
        
        # 保存到文件
        self._save_session_data()
        
        print(f"[CarNegotiateMiddleware] 关键信息抽取完成，已保存到 {self.output_dir}")
        print(f"  - 客户意向: {extracted.get('customer_intent', 'N/A')}")
        print(f"  - 异议类型: {extracted.get('objection_type', 'N/A')}")
        print(f"  - 成交信号: {extracted.get('deal_signal', 'N/A')}")
        
        return None

    def _extract_with_llm(self, user_text: str, ai_text: str) -> dict[str, Any]:
        """使用大模型抽取对话关键信息。"""
        if self.extraction_llm is None:
            return {"error": "未配置 extraction_llm"}
        
        prompt = f"""请分析以下车险销售对话，抽取关键信息并返回 JSON 格式：

【用户消息】
{user_text}

【坐席回复】
{ai_text}

请返回以下字段的 JSON：
{{
    "customer_intent": "客户当前意图（如：询价、了解保障、价格异议、确认购买等）",
    "objection_type": "客户异议类型（如：价格太贵、比去年贵、考虑中、无）",
    "deal_signal": "成交信号强度（强/中/弱/无），并说明原因",
    "customer_emotion": "客户情绪（积极/中性/消极/焦虑）",
    "mentioned_skills": "对话中涉及的技能模块列表（如：car-quote, car-price-negotiate）",
    "next_step_suggestion": "下一步建议（如：继续谈判、促单、讲解保障、引导支付等）",
    "key_entities": "对话中提到的关键实体（如车牌号、车型、保费金额、竞品公司等）"
}}

只返回 JSON，不要其他内容。"""

        try:
            response = self.extraction_llm.invoke(prompt)
            raw_content = response.content if hasattr(response, "content") else str(response)
            
            # 处理 content 可能是 list 的情况
            if isinstance(raw_content, list):
                content = "\n".join(
                    str(item) if not isinstance(item, dict) else str(item.get("text", item))
                    for item in raw_content
                )
            else:
                content = str(raw_content)
            
            # 尝试解析 JSON
            # 先清理可能的 markdown 代码块
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"[CarNegotiateMiddleware] LLM 抽取失败: {e}")
            return {
                "customer_intent": "解析失败",
                "objection_type": "解析失败",
                "deal_signal": "解析失败",
                "error": str(e),
            }

    def _save_session_data(self) -> None:
        """保存会话数据到文件。"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.output_dir / f"car_negotiate_session_{timestamp}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self._session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[CarNegotiateMiddleware] 保存会话数据失败: {e}")


# 为了方便使用 decorator 方式创建，也提供函数版本
@before_agent
def car_negotiate_before(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """before_agent hook：注入意图分析和 skill 选择指导。"""
    user_text = _extract_user_message(state)
    if not user_text:
        return None

    intent, recommended_skill = _detect_intent(user_text)
    print(f"\n[CarNegotiateBefore] 用户意图检测: '{intent}' -> 推荐 skill: {recommended_skill or '无'}")

    guidance_parts = [
        "【中间件意图分析】",
        f"用户输入: {user_text}",
        f"检测到意图: {intent}",
    ]
    
    if recommended_skill and recommended_skill in SKILL_GUIDANCE:
        guidance_parts.append(SKILL_GUIDANCE[recommended_skill])
    else:
        guidance_parts.append("未检测到明确意图，请根据用户问题自主选择最合适的 skill。")
    
    guidance_text = "\n".join(guidance_parts)
    
    # 返回 messages 更新，add_messages 会追加
    return {"messages": [SystemMessage(content=guidance_text)]}


# after_agent hook 需要 LLM，所以用类方式更方便
# 如果需要使用 decorator，可以先创建 LLM 实例然后封装
