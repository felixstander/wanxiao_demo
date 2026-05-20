#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Car_Negotiate_Middleware

车险谈判中间件，基于 SQLite 实现状态持久化与策略推荐。

功能：
- before_agent: 从 SQLite 读取历史事实，结合可选策略池，让 LLM 推荐策略并注入
- after_agent: 分析完整对话历史，抽取结构化事实，存入 SQLite
"""

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    after_agent,
    before_agent,
)
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

# ── 可选策略池（基于 M1-M10 标准子步骤） ──────────────────────
OPTIONAL_STRATEGIES = [
    # M1 报价
    {"编码": "M1.1", "名称": "确认车辆信息", "模块": "M1", "动作": "核对车牌、车型、车架号、使用性质、出险记录", "触发条件": "报价前必须确认"},
    {"编码": "M1.2", "名称": "调用报价系统", "模块": "M1", "动作": "调用 car_quote 获取报价", "触发条件": "车辆信息已确认"},
    {"编码": "M1.3", "名称": "播报报价金额", "模块": "M1", "动作": "清晰播报总保费，分项说明", "触发条件": "报价已生成"},
    {"编码": "M1.4", "名称": "解释价格构成", "模块": "M1", "动作": "解释各险种作用和 NCD 影响", "触发条件": "客户对价格有疑问"},
    {"编码": "M1.5", "名称": "询问客户意见", "模块": "M1", "动作": "询问客户对报价的接受程度", "触发条件": "报价播报后"},
    # M2 方案讲解
    {"编码": "M2.1", "名称": "说明方案包含哪些险种", "模块": "M2", "动作": "列出所有险种名称和基本作用", "触发条件": "客户询问保障细节"},
    {"编码": "M2.2", "名称": "解释各险种保障范围和保额", "模块": "M2", "动作": "详细解释保障内容和赔付方式", "触发条件": "客户对险种不了解"},
    {"编码": "M2.3", "名称": "区分必选/可选", "模块": "M2", "动作": "说明法定必买和建议购买的险种", "触发条件": "客户不清楚该买什么"},
    {"编码": "M2.4", "名称": "询问客户是否需要调整", "模块": "M2", "动作": "询问是否有想增减的险种", "触发条件": "方案讲解后"},
    # M3 方案调整
    {"编码": "M3.1", "名称": "确认客户变更需求", "模块": "M3", "动作": "明确客户要增减或修改的险种", "触发条件": "客户提出加保/减保/更换"},
    {"编码": "M3.2", "名称": "调用方案配置系统修改", "模块": "M3", "动作": "调用 car_plan_adjust 调整方案", "触发条件": "变更需求已确认"},
    {"编码": "M3.3", "名称": "重新调用报价系统", "模块": "M3", "动作": "基于新方案重新计算保费", "触发条件": "方案已调整"},
    {"编码": "M3.4", "名称": "播报新报价", "模块": "M3", "动作": "播报调整后总保费和价格变化", "触发条件": "新报价已生成"},
    {"编码": "M3.5", "名称": "确认客户是否接受", "模块": "M3", "动作": "询问客户对新方案的接受程度", "触发条件": "新报价播报后"},
    # M4 价格谈判
    {"编码": "M4.1", "名称": "倾听并认同客户感受", "模块": "M4", "动作": "表示理解客户顾虑，不否定", "触发条件": "客户表达价格不满"},
    {"编码": "M4.2", "名称": "探寻价格异议原因", "模块": "M4", "动作": "询问具体原因、预算、对比参照物", "触发条件": "客户嫌贵/要求优惠"},
    {"编码": "M4.3", "名称": "运用谈判策略", "模块": "M4", "动作": "价值拆解/案例说服/紧迫感营造", "触发条件": "已了解异议原因"},
    {"编码": "M4.4", "名称": "询问是否接受", "模块": "M4", "动作": "给出方案后询问客户意见", "触发条件": "谈判策略使用后"},
    {"编码": "M4.5", "名称": "申请优惠/赠送", "模块": "M4", "动作": "向上级申请额外优惠或增值服务", "触发条件": "客户仍不满意"},
    # M5 价格差异解释
    {"编码": "M5.1", "名称": "共情客户质疑", "模块": "M5", "动作": "表示理解客户对价格变化的关注", "触发条件": "客户质疑比去年贵"},
    {"编码": "M5.2", "名称": "查询出险/违章/历史保单", "模块": "M5", "动作": "调用 car_price_diff 查询变化原因", "触发条件": "客户对比往年保费"},
    {"编码": "M5.3", "名称": "归因分析", "模块": "M5", "动作": "分析 NCD/出险/保障/市场/折扣变化", "触发条件": "已查询历史数据"},
    {"编码": "M5.4", "名称": "向客户解释归因结果", "模块": "M5", "动作": "用通俗语言解释价格变化原因", "触发条件": "归因分析完成"},
    {"编码": "M5.5", "名称": "引导回当前方案价值", "模块": "M5", "动作": "将注意力引回保障价值", "触发条件": "解释后客户仍关注价格"},
    # M6 服务卡券
    {"编码": "M6.1", "名称": "查询资源池可用赠品/卡券", "模块": "M6", "动作": "调用 car_service_card 查询赠品", "触发条件": "客户询问优惠/促单阶段"},
    {"编码": "M6.2", "名称": "推荐匹配赠品", "模块": "M6", "动作": "根据客户偏好推荐最适合赠品", "触发条件": "已查询可用赠品"},
    {"编码": "M6.3", "名称": "说明赠送规则和限制", "模块": "M6", "动作": "说明赠品使用条件和有效期", "触发条件": "推荐赠品后"},
    {"编码": "M6.4", "名称": "将赠品价值与保费挂钩", "模块": "M6", "动作": "计算赠品实际价值相当于折扣", "触发条件": "客户对赠品感兴趣"},
    {"编码": "M6.5", "名称": "引导确认是否接受", "模块": "M6", "动作": "询问客户对赠品的满意度", "触发条件": "赠品价值说明后"},
    # M7 竞品对比
    {"编码": "M7.1", "名称": "认同客户比价行为", "模块": "M7", "动作": "表示理解货比三家", "触发条件": "客户提及竞品"},
    {"编码": "M7.2", "名称": "获取竞品信息", "模块": "M7", "动作": "询问并调用 car_competitor_compare", "触发条件": "客户主动对比"},
    {"编码": "M7.3", "名称": "结构化对比", "模块": "M7", "动作": "从保障/价格/服务三维度对比", "触发条件": "已获取竞品信息"},
    {"编码": "M7.4", "名称": "突出我方差异化优势", "模块": "M7", "动作": "强调平安理赔速度/网点/APP优势", "触发条件": "对比后"},
    {"编码": "M7.5", "名称": "引导客户综合评估", "模块": "M7", "动作": "引导不仅看价格还要看服务", "触发条件": "客户犹豫选择"},
    # M8 促单
    {"编码": "M8.1", "名称": "识别成交信号", "模块": "M8", "动作": "识别问付款/问生效/反复询问细节", "触发条件": "客户意向明确但犹豫"},
    {"编码": "M8.2", "名称": "运用促单策略", "模块": "M8", "动作": "限时优惠/赠品激励/紧迫感/案例说服", "触发条件": "识别到成交信号"},
    {"编码": "M8.3", "名称": "确认购买意向", "模块": "M8", "动作": "直接询问是否确定购买", "触发条件": "促单策略使用后"},
    {"编码": "M8.4", "名称": "引导进入支付环节", "模块": "M8", "动作": "引导客户进入支付流程", "触发条件": "客户确认购买"},
    # M9 理赔服务
    {"编码": "M9.1", "名称": "了解客户关注点", "模块": "M9", "动作": "询问关心理赔的哪个方面", "触发条件": "客户询问理赔"},
    {"编码": "M9.2", "名称": "介绍理赔流程", "模块": "M9", "动作": "介绍报案→查勘→定损→赔付", "触发条件": "客户对理赔流程不清楚"},
    {"编码": "M9.3", "名称": "展示服务优势", "模块": "M9", "动作": "万元以下1天赔付/线上理赔", "触发条件": "客户关心理赔速度"},
    {"编码": "M9.4", "名称": "消除客户顾虑", "模块": "M9", "动作": "解答具体顾虑并强调口碑", "触发条件": "客户仍有顾虑"},
    # M10 投保支付
    {"编码": "M10.1", "名称": "确认最终方案和报价", "模块": "M10", "动作": "再次确认险种/保额/保费/生效时间", "触发条件": "客户确认购买"},
    {"编码": "M10.2", "名称": "引导支付方式选择", "模块": "M10", "动作": "介绍平安APP/微信/支付宝/银行卡", "触发条件": "客户同意支付"},
    {"编码": "M10.3", "名称": "引导完成支付操作", "模块": "M10", "动作": "指导支付步骤并提醒安全", "触发条件": "客户选定支付方式"},
    {"编码": "M10.4", "名称": "确认支付成功", "模块": "M10", "动作": "确认保单生成并告知保单号", "触发条件": "支付完成"},
    {"编码": "M10.5", "名称": "引导查看电子保单", "模块": "M10", "动作": "指导在平安APP查看电子保单", "触发条件": "支付成功确认后"},
]


# ── 辅助函数：消息提取 ─────────────────────────────────────────
def _extract_all_messages(state: AgentState) -> list[dict[str, str]]:
    """从 state 中提取所有用户/AI 消息对。"""
    messages = state.get("messages", [])
    history: list[dict[str, str]] = []
    for msg in messages:
        role, content = "", ""
        if isinstance(msg, dict):
            role = msg.get("role") or msg.get("type", "")
            content = msg.get("content", "")
        else:
            role = getattr(msg, "type", "")
            content = getattr(msg, "content", "")
        if role in ("user", "human", "HumanMessage") and isinstance(content, str) and content.strip():
            history.append({"role": "user", "content": content.strip()})
        elif role in ("assistant", "ai", "AIMessage") and isinstance(content, str) and content.strip():
            history.append({"role": "assistant", "content": content.strip()})
    return history


def _extract_last_user_message(state: AgentState) -> str:
    """提取最后一条用户消息。"""
    msgs = _extract_all_messages(state)
    for m in reversed(msgs):
        if m["role"] == "user":
            return m["content"]
    return ""


def _extract_last_ai_message(state: AgentState) -> str:
    """提取最后一条 AI 消息。"""
    msgs = _extract_all_messages(state)
    for m in reversed(msgs):
        if m["role"] == "assistant":
            return m["content"]
    return ""


def _get_user_id(state: AgentState, runtime: Any, middleware: Any = None) -> str:
    """尝试从 runtime.config 或 fallback 获取 user_id。"""
    # 0. 如果中间件手动设置了 user_id，优先使用
    if middleware is not None and getattr(middleware, "_current_user_id", None):
        return str(middleware._current_user_id)
    # 1. 探测 runtime 的所有属性，寻找 thread_id
    try:
        # 尝试直接访问常见属性
        for attr_name in ["config", "metadata", "state", "thread_id", "run_id"]:
            val = getattr(runtime, attr_name, None)
            if val is not None:
                if attr_name == "thread_id" and val:
                    return str(val)
                # 如果是 dict，递归查找 thread_id
                if isinstance(val, dict):
                    for key in ["thread_id", "run_id", "user_id"]:
                        if key in val and val[key]:
                            return str(val[key])
                    if "configurable" in val and isinstance(val["configurable"], dict):
                        for key in ["thread_id", "run_id", "user_id"]:
                            if key in val["configurable"] and val["configurable"][key]:
                                return str(val["configurable"][key])
                # 如果有 __dict__，遍历它
                if hasattr(val, "__dict__"):
                    d = val.__dict__
                    for key in ["thread_id", "run_id", "user_id"]:
                        if key in d and d[key]:
                            return str(d[key])
    except Exception:
        pass
    # 2. fallback：尝试从 state 中的 metadata 获取
    try:
        metadata = state.get("metadata", {})
        if isinstance(metadata, dict):
            tid = metadata.get("thread_id")
            if tid:
                return str(tid)
    except Exception:
        pass
    # 3. fallback：用当前时间戳
    return f"anonymous_{datetime.now().strftime('%Y%m%d%H%M%S')}"


# ── SQLite DB 管理 ──────────────────────────────────────────────
class FactStore:
    """基于 SQLite 的事实存储。"""

    def __init__(self, db_path: str | Path = "./car_negotiate.db"):
        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS negotiation_facts (
                    user_id TEXT PRIMARY KEY,
                    round_count INTEGER DEFAULT 0,
                    stage TEXT DEFAULT '初始',
                    price_trajectory TEXT DEFAULT '[]',
                    budget_value REAL,
                    budget_basis TEXT,
                    deleted_coverages TEXT DEFAULT '[]',
                    current_coverages TEXT DEFAULT '[]',
                    recent_strategy_code TEXT,
                    recent_customer_reaction TEXT,
                    recent_strategy_result TEXT,
                    core_concern TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()

    def get_facts(self, user_id: str) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM negotiation_facts WHERE user_id = ?", (user_id,)
            )
            row = cursor.fetchone()
            cols = [d[0] for d in cursor.description]
        if not row:
            return {
                "user_id": user_id,
                "round_count": 0,
                "stage": "初始",
                "price_trajectory": [],
                "budget": {"值": None, "依据": ""},
                "已删险种": [],
                "当前险种": [],
                "最近策略": {"编码": "", "客户反应": "", "结果": ""},
                "核心顾虑": "",
            }
        facts = dict(zip(cols, row))
        return {
            "user_id": facts.get("user_id", user_id),
            "round_count": facts.get("round_count", 0),
            "stage": facts.get("stage", "初始"),
            "price_trajectory": json.loads(facts.get("price_trajectory", "[]")),
            "budget": {
                "值": facts.get("budget_value"),
                "依据": facts.get("budget_basis", ""),
            },
            "已删险种": json.loads(facts.get("deleted_coverages", "[]")),
            "当前险种": json.loads(facts.get("current_coverages", "[]")),
            "最近策略": {
                "编码": facts.get("recent_strategy_code", ""),
                "客户反应": facts.get("recent_customer_reaction", ""),
                "结果": facts.get("recent_strategy_result", ""),
            },
            "核心顾虑": facts.get("core_concern", ""),
        }

    def save_facts(self, user_id: str, facts: dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO negotiation_facts (
                    user_id, round_count, stage, price_trajectory,
                    budget_value, budget_basis, deleted_coverages, current_coverages,
                    recent_strategy_code, recent_customer_reaction, recent_strategy_result,
                    core_concern, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    round_count=excluded.round_count,
                    stage=excluded.stage,
                    price_trajectory=excluded.price_trajectory,
                    budget_value=excluded.budget_value,
                    budget_basis=excluded.budget_basis,
                    deleted_coverages=excluded.deleted_coverages,
                    current_coverages=excluded.current_coverages,
                    recent_strategy_code=excluded.recent_strategy_code,
                    recent_customer_reaction=excluded.recent_customer_reaction,
                    recent_strategy_result=excluded.recent_strategy_result,
                    core_concern=excluded.core_concern,
                    updated_at=excluded.updated_at
                """,
                (
                    user_id,
                    facts.get("round_count", 0),
                    facts.get("stage", "初始"),
                    json.dumps(facts.get("price_trajectory", []), ensure_ascii=False),
                    facts.get("budget", {}).get("值"),
                    facts.get("budget", {}).get("依据", ""),
                    json.dumps(facts.get("已删险种", []), ensure_ascii=False),
                    json.dumps(facts.get("当前险种", []), ensure_ascii=False),
                    facts.get("最近策略", {}).get("编码", ""),
                    facts.get("最近策略", {}).get("客户反应", ""),
                    facts.get("最近策略", {}).get("结果", ""),
                    facts.get("核心顾虑", ""),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()


# ── 中间件 ─────────────────────────────────────────────────────
class CarNegotiateMiddleware(AgentMiddleware):
    """车险谈判中间件。

    before_agent: 从 DB 读取历史事实 → LLM 策略推荐 → 注入 system message
    after_agent:  分析完整对话 → LLM 抽取事实 → 存入 SQLite
    """

    def __init__(
        self,
        extraction_llm: ChatOpenAI | None = None,
        strategy_llm: ChatOpenAI | None = None,
        db_path: str | Path = "./car_negotiate.db",
        output_dir: str | Path = "./middleware_logs",
    ):
        super().__init__()
        self.extraction_llm = extraction_llm
        self.strategy_llm = strategy_llm or extraction_llm
        self.store = FactStore(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._current_user_id: str | None = None

    def set_user_id(self, user_id: str) -> None:
        """手动设置当前 user_id（用于从外部传入 thread_id）。"""
        self._current_user_id = user_id

    # ── before_agent ───────────────────────────────────────────
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        user_id = _get_user_id(state, runtime, self)
        user_text = _extract_last_user_message(state)
        if not user_text:
            return None

        # 1. 读取历史事实
        facts = self.store.get_facts(user_id)
        facts["轮次"] = facts.get("round_count", 0) + 1

        # 2. 构建可选策略池（根据当前阶段过滤相关策略，减少 prompt 长度）
        stage = facts.get("stage", "初始")
        stage_module_map = {
            "初始": ["M1", "M2"],
            "质疑": ["M4", "M5", "M7"],
            "调整": ["M3"],
            "谈判": ["M4", "M6", "M7", "M8"],
            "成交": ["M8", "M9", "M10"],
        }
        relevant_modules = stage_module_map.get(stage, ["M1", "M2"])
        # 同时保留相邻模块（增加灵活性）
        all_relevant = set(relevant_modules)
        for m in relevant_modules:
            num = int(m[1:]) if len(m) > 1 and m[1:].isdigit() else 0
            for offset in [-1, 1]:
                neighbor = f"M{num + offset}"
                if any(s["模块"] == neighbor for s in OPTIONAL_STRATEGIES):
                    all_relevant.add(neighbor)
        relevant_strategies = [s for s in OPTIONAL_STRATEGIES if s["模块"] in all_relevant]

        # 3. 让 LLM 推荐策略（仅在非第一轮且配置了 LLM 时调用，避免超时）
        if facts.get("round_count", 0) == 0:
            # 第一轮：使用默认策略，不调用 LLM
            strategy_result = {
                "局势分析": "首次接触，处于初始阶段，需要收集车辆信息并报价。",
                "主策略": {"编码": "M1.1", "名称": "确认车辆信息", "模块": "M1", "动作": "核对车牌、车型、出险记录", "理由": "首次对话，必须先确认车辆信息才能报价"},
            }
        else:
            strategy_result = self._recommend_strategy(facts, user_text, relevant_strategies)

        # 4. 打印日志
        print(f"\n[CarNegotiateMiddleware] user_id={user_id} | 轮次={facts['轮次']} | 阶段={stage}")
        print(f"  策略推荐: {strategy_result.get('主策略', {}).get('编码', 'N/A')} | {strategy_result.get('主策略', {}).get('名称', 'N/A')}")
        print(f"  局势分析: {strategy_result.get('局势分析', 'N/A')}")

        # 5. 构建注入消息
        main_strategy = strategy_result.get("主策略", {})
        guidance_parts = [
            "【中间件策略推荐】",
            f"局势分析: {strategy_result.get('局势分析', '')}",
            f"推荐策略: {main_strategy.get('编码', '')} - {main_strategy.get('名称', '')}",
            f"所属模块: {main_strategy.get('模块', '')}",
            f"建议动作: {main_strategy.get('动作', '')}",
            f"推荐理由: {main_strategy.get('理由', '')}",
            "",
            "【当前事实背景】",
            f"轮次: {facts['轮次']} | 阶段: {stage}",
            f"价格轨迹: {facts.get('price_trajectory', [])}",
            f"预算: {facts.get('budget', {}).get('值', '未提及')} ({facts.get('budget', {}).get('依据', '')})",
            f"已删险种: {facts.get('已删险种', [])}",
            f"当前险种: {facts.get('当前险种', [])}",
            f"最近策略: {facts.get('最近策略', {}).get('编码', '无')} → 客户反应: {facts.get('最近策略', {}).get('客户反应', '无')} → 结果: {facts.get('最近策略', {}).get('结果', '无')}",
            f"核心顾虑: {facts.get('核心顾虑', '无')}",
            "",
            "注意：以上仅为策略推荐，请根据实际对话灵活执行。",
        ]
        guidance_text = "\n".join(guidance_parts)

        # 6. 将指导信息作为 system message 插入
        messages = state.get("messages", [])
        if isinstance(messages, list):
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
            messages.insert(insert_idx, SystemMessage(content=guidance_text))

        return None

    def _recommend_strategy(
        self,
        facts: dict[str, Any],
        user_text: str,
        strategy_pool: list[dict[str, str]],
    ) -> dict[str, Any]:
        """使用 LLM 基于事实和当前输入推荐策略。"""
        if self.strategy_llm is None:
            return {
                "局势分析": "未配置 strategy_llm",
                "主策略": {"编码": "", "名称": "", "模块": "", "动作": "", "理由": ""},
            }

        prompt = f"""你是一个专业的车险销售策略分析师。基于以下事实和当前输入，分析局势并推荐唯一策略。

【事实】
- 轮次: {facts.get('轮次', 0)} | 阶段: {facts.get('stage', '初始')} | 价格轨迹: {facts.get('price_trajectory', [])}
- 预算: {facts.get('budget', {}).get('值', 'null')} ({facts.get('budget', {}).get('依据', '')})
- 已删: {facts.get('已删险种', [])} | 当前: {facts.get('当前险种', [])}
- 最近策略: {facts.get('最近策略', {}).get('编码', '')} → 客户反应: {facts.get('最近策略', {}).get('客户反应', '')} → 结果: {facts.get('最近策略', {}).get('结果', '')}
- 核心顾虑: {facts.get('核心顾虑', '')}

【当前输入】
{user_text}

【可选策略池】（仅从以下策略中选择）
{json.dumps(strategy_pool, ensure_ascii=False, indent=2)}

【严格要求】
1. 必须从可选策略池中选择一个策略
2. 只返回纯 JSON，不要 markdown 代码块标记，不要任何解释性文字
3. 理由字段要具体引用事实

【输出格式】
{{
  "局势分析": "1-2句话，包含局势判断+耐心判断+风险判断",
  "主策略": {{
    "编码": "Mx.y",
    "名称": "策略名称",
    "模块": "Mx",
    "动作": "具体动作",
    "理由": "为什么选这个（引用事实）+ 预期反应 + 若失败怎么办"
  }}
}}"""

        max_retries = 2
        last_raw = ""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                response = self.strategy_llm.invoke(prompt)
                raw = response.content if hasattr(response, "content") else str(response)
                last_raw = str(raw)
                content = _clean_llm_output(raw)
                result = json.loads(content)
                
                # 验证结果结构
                if "主策略" in result and "编码" in result["主策略"]:
                    return result
                else:
                    raise ValueError("返回的 JSON 缺少必要的字段")
                    
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    print(f"[CarNegotiateMiddleware] 策略推荐解析失败（第{attempt+1}次尝试）: {e}")
                    # 在 prompt 中添加错误信息，要求重新生成
                    prompt += f"\n\n【错误】之前返回的内容解析失败: {str(e)[:100]}。请确保只返回纯 JSON，不要包含任何其他文字。"
                else:
                    print(f"[CarNegotiateMiddleware] 策略推荐最终失败: {e}")
                    if last_raw:
                        print(f"[CarNegotiateMiddleware] 原始响应前500字符: {last_raw[:500]}")
        
        # 如果所有重试都失败了
        return {
            "局势分析": f"策略推荐失败（已重试{max_retries}次）: {last_error}",
            "主策略": {"编码": "", "名称": "", "模块": "", "动作": "", "理由": ""},
        }

    # ── after_agent ────────────────────────────────────────────
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        user_id = _get_user_id(state, runtime, self)
        user_text = _extract_last_user_message(state)
        ai_text = _extract_last_ai_message(state)
        if not user_text or not ai_text:
            return None

        print(f"\n[CarNegotiateMiddleware] user_id={user_id} | after_agent 抽取事实...")

        # 1. 获取完整对话历史
        full_history = _extract_all_messages(state)
        conversation_text = "\n".join(
            f"{'用户' if m['role'] == 'user' else '坐席'}: {m['content']}" for m in full_history
        )

        # 2. 读取当前事实（用于增量更新）
        old_facts = self.store.get_facts(user_id)
        current_round = old_facts.get("round_count", 0) + 1

        # 3. LLM 抽取结构化事实
        extracted = self._extract_facts_with_llm(conversation_text, user_text, current_round)

        # 4. 合并事实
        new_facts = self._merge_facts(old_facts, extracted, current_round)

        # 5. 存入 SQLite
        self.store.save_facts(user_id, new_facts)

        # 6. 打印日志
        print(f"[CarNegotiateMiddleware] 事实抽取完成并已入库")
        print(f"  轮次: {new_facts['round_count']} | 阶段: {new_facts['stage']}")
        print(f"  价格轨迹: {new_facts.get('price_trajectory', [])}")
        print(f"  预算: {new_facts.get('budget', {}).get('值')} ({new_facts.get('budget', {}).get('依据')})")
        print(f"  当前险种: {new_facts.get('当前险种', [])}")
        print(f"  最近策略: {new_facts.get('最近策略', {}).get('编码')} → 结果: {new_facts.get('最近策略', {}).get('结果')}")
        print(f"  核心顾虑: {new_facts.get('核心顾虑', '')}")

        # 7. 保存到 JSON 日志（方便查看）
        self._save_json_log(user_id, new_facts, conversation_text)

        return None

    def _extract_facts_with_llm(
        self, conversation_text: str, current_input: str, round_count: int
    ) -> dict[str, Any]:
        """使用 LLM 从完整对话中抽取结构化事实。"""
        if self.extraction_llm is None:
            return {}

        prompt = f"""从以下车险销售对话记录中提取事实，输出 JSON。

对话记录：
{conversation_text}

当前输入：{current_input}

请严格返回以下 JSON（不要遗漏字段）：
{{
  "轮次": {round_count},
  "阶段": "初始/质疑/调整/谈判/成交",
  "价格轨迹": [金额1, 金额2],
  "预算": {{"值": 数字或null, "依据": "客户原话"}},
  "已删险种": ["名称"],
  "当前险种": ["名称"],
  "最近策略": {{"编码": "Mx.y", "客户反应": "原话", "结果": "成功/失败/不明确"}},
  "核心顾虑": "保费太高/保障不够/比去年贵/别家更便宜/其他"
}}

提取规则：
1. 阶段：根据对话整体氛围判断，只能是"初始/质疑/调整/谈判/成交"之一
2. 价格轨迹：提取所有出现过的保费金额（数字），按时间顺序排列
3. 预算：如果客户提到预算上限或期望价格，记录数值和原话
4. 已删险种：客户明确表示不要了的险种
5. 当前险种：当前方案中包含的险种列表
6. 最近策略：上一轮使用的策略编码（从坐席话术推断）、客户的直接反应、结果判断
7. 核心顾虑：客户最核心的顾虑，只能是给定选项之一

只返回 JSON，不要其他内容。"""

        try:
            response = self.extraction_llm.invoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            content = _clean_llm_output(raw)
            return json.loads(content)
        except Exception as e:
            print(f"[CarNegotiateMiddleware] 事实抽取失败: {e}")
            return {}

    def _merge_facts(self, old: dict[str, Any], new: dict[str, Any], new_round_count: int) -> dict[str, Any]:
        """合并新旧事实（增量更新）。"""
        merged = dict(old)

        # 轮次：使用计算后的新轮次
        merged["round_count"] = new_round_count

        # 阶段、核心顾虑：直接覆盖
        for key in ["stage", "核心顾虑"]:
            if key in new and new[key]:
                merged[key] = new[key]

        # 价格轨迹：合并并去重
        old_prices = merged.get("price_trajectory", [])
        new_prices = new.get("价格轨迹", [])
        if new_prices:
            # 简单合并，保留时间顺序
            merged["price_trajectory"] = old_prices + [p for p in new_prices if p not in old_prices]

        # 预算：如果新值不为空则覆盖
        new_budget = new.get("预算", {})
        if new_budget and (new_budget.get("值") is not None or new_budget.get("依据")):
            merged["budget"] = new_budget

        # 已删险种：合并
        old_deleted = set(merged.get("已删险种", []))
        new_deleted = set(new.get("已删险种", []))
        merged["已删险种"] = sorted(old_deleted | new_deleted)

        # 当前险种：直接覆盖（最新为准）
        if new.get("当前险种"):
            merged["当前险种"] = new["当前险种"]

        # 最近策略：直接覆盖（最新一轮为准）
        new_strategy = new.get("最近策略", {})
        if new_strategy and new_strategy.get("编码"):
            merged["最近策略"] = new_strategy

        return merged

    def _save_json_log(self, user_id: str, facts: dict[str, Any], conversation_text: str) -> None:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.output_dir / f"fact_{user_id}_{timestamp}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "user_id": user_id,
                        "timestamp": datetime.now().isoformat(),
                        "facts": facts,
                        "conversation": conversation_text,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            print(f"[CarNegotiateMiddleware] JSON 日志保存失败: {e}")


# ── 辅助函数 ───────────────────────────────────────────────────
def _clean_llm_output(raw: Any) -> str:
    """清理 LLM 输出，提取 JSON 内容。"""
    import re
    
    if isinstance(raw, list):
        text = "\n".join(
            str(item) if not isinstance(item, dict) else str(item.get("text", item))
            for item in raw
        )
    else:
        text = str(raw)
    text = text.strip()
    
    # 尝试提取 markdown 代码块中的内容
    # 匹配 ```json ... ``` 或 ``` ... ```
    # 使用非贪婪匹配，允许代码块内部有多行
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if code_block_match:
        candidate = code_block_match.group(1).strip()
        # 验证是否是有效的 JSON
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass
    
    # 尝试找到第一个 { 到最后一个 }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace:last_brace + 1]
        # 验证是否是有效的 JSON
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass
    
    # 如果都没找到，返回原始文本（让调用者处理错误）
    return text


# ── 兼容旧接口的装饰器版本 ─────────────────────────────────────
@before_agent
def car_negotiate_before(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """简化版 before_agent hook（无 DB/LLM，仅做关键词意图检测）。"""
    user_text = _extract_last_user_message(state)
    if not user_text:
        return None

    # 简单关键词匹配
    intent_map = {
        "报个价": "car-quote", "多少钱": "car-quote",
        "保什么": "car-plan-explain", "保障范围": "car-plan-explain",
        "加保": "car-plan-adjust", "减保": "car-plan-adjust", "去掉": "car-plan-adjust",
        "太贵": "car-price-negotiate", "便宜": "car-price-negotiate", "优惠": "car-price-negotiate",
        "比去年贵": "car-price-diff-explain",
        "赠品": "car-service-card", "礼品": "car-service-card",
        "人保": "car-competitor-compare", "太平洋": "car-competitor-compare",
        "考虑": "car-promotion", "犹豫": "car-promotion",
        "理赔": "car-claim-service", "出险": "car-claim-service",
        "付款": "car-payment", "支付": "car-payment", "确定": "car-payment",
    }
    matched = ""
    for kw, skill in intent_map.items():
        if kw in user_text:
            matched = skill
            break

    guidance = f"【中间件意图分析】用户输入: {user_text}\n检测到意图: {matched or '未知'}\n"
    if matched:
        guidance += f"推荐优先调用 skill: {matched}"
    return {"messages": [SystemMessage(content=guidance)]}
