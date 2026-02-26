import argparse
import csv
import os
from datetime import date
from pathlib import Path
from typing import Any

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(
    "SalesScenarioMockTools",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)



CUSTOMER_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "customer_db.csv"
LIST_FIELDS = {
    "behaviors",
    "viewed_products",
    "consulted_products",
    "reimbursed_diseases",
}
INT_FIELDS = {"age", "viewed_issue_link_count", "claim_count", "annual_income"}


def _parse_list_field(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split("|") if item.strip()]


def _load_customer_db_from_csv(csv_path: Path) -> dict[str, dict[str, Any]]:
    customer_db: dict[str, dict[str, Any]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            customer_name = (row.get("name") or "").strip()
            if not customer_name:
                continue

            customer_profile: dict[str, Any] = {}
            for field_name, value in row.items():
                if field_name == "name":
                    continue
                raw_value = (value or "").strip()
                if field_name in LIST_FIELDS:
                    customer_profile[field_name] = _parse_list_field(raw_value)
                elif field_name in INT_FIELDS:
                    customer_profile[field_name] = int(raw_value) if raw_value else 0
                else:
                    customer_profile[field_name] = raw_value

            customer_db[customer_name] = customer_profile

    return customer_db


CUSTOMER_DB: dict[str, dict[str, Any]] = _load_customer_db_from_csv(CUSTOMER_CSV_PATH)


PRODUCT_CATALOG: dict[str, dict[str, Any]] = {
    "守护重疾Pro": {
        "type": "重疾险",
        "price_band": "中高",
        "annual_base_premium": 2200,
        "coverage_scope": ["恶性肿瘤", "心脑血管重疾", "器官功能障碍"],
        "coverage_limit": "50万-80万",
        "waiting_period": "90天",
        "highlights": ["重疾多次赔", "特定疾病额外赔付"],
        "limitations": ["既往重大疾病除外", "等待期内不赔"],
    },
    "全家医疗Plus": {
        "type": "医疗险",
        "price_band": "中",
        "annual_base_premium": 1600,
        "coverage_scope": ["住院医疗", "门诊手术", "重大疾病住院"],
        "coverage_limit": "300万",
        "waiting_period": "30天",
        "highlights": ["可附加家庭共保", "特药直付"],
        "limitations": ["部分慢病免责", "特需部需附加"],
    },
    "安心意外Max": {
        "type": "意外险",
        "price_band": "低",
        "annual_base_premium": 680,
        "coverage_scope": ["交通意外", "意外医疗", "伤残保障"],
        "coverage_limit": "100万",
        "waiting_period": "次日生效",
        "highlights": ["交通意外高额赔", "含意外住院津贴"],
        "limitations": ["高危运动部分免责"],
    },
    "臻选医疗VIP": {
        "type": "高端医疗险",
        "price_band": "高",
        "annual_base_premium": 3800,
        "coverage_scope": ["全球医疗网络", "先进疗法", "重大疾病二诊"],
        "coverage_limit": "800万",
        "waiting_period": "30天",
        "highlights": ["公立特需可报", "国际就医支持"],
        "limitations": ["首年已有疾病责任受限"],
    },
    "轻松医疗基础版": {
        "type": "医疗险",
        "price_band": "低",
        "annual_base_premium": 980,
        "coverage_scope": ["住院医疗", "重大疾病住院"],
        "coverage_limit": "200万",
        "waiting_period": "30天",
        "highlights": ["保费友好", "投保门槛低"],
        "limitations": ["报销范围较基础"],
    },
}


CLAIM_CASE_DB: list[dict[str, Any]] = [
    {
        "case_id": "CASE-001",
        "disease": "乳腺结节",
        "age_min": 35,
        "age_max": 50,
        "product": "守护重疾Pro",
        "claim_amount": 320000,
        "approval_days": 5,
        "key_point": "体检发现后尽快规范复查，按条款完成材料提交",
    },
    {
        "case_id": "CASE-002",
        "disease": "甲状腺结节",
        "age_min": 25,
        "age_max": 45,
        "product": "全家医疗Plus",
        "claim_amount": 86000,
        "approval_days": 3,
        "key_point": "门诊+住院链路齐全，报销比例高",
    },
    {
        "case_id": "CASE-003",
        "disease": "心脑血管疾病",
        "age_min": 35,
        "age_max": 60,
        "product": "守护重疾Pro",
        "claim_amount": 500000,
        "approval_days": 7,
        "key_point": "符合重疾定义后快速给付，缓解治疗现金压力",
    },
]


FESTIVAL_CALENDAR: list[dict[str, Any]] = [
    {"name": "清明", "month": 4, "day": 4, "travel_risk": "短途自驾增多"},
    {"name": "劳动节", "month": 5, "day": 1, "travel_risk": "景区拥挤+交通高峰"},
    {"name": "端午", "month": 6, "day": 10, "travel_risk": "周边游和水上活动增加"},
    {"name": "中秋", "month": 9, "day": 17, "travel_risk": "返乡车流集中"},
    {"name": "国庆", "month": 10, "day": 1, "travel_risk": "跨省出行高峰"},
]


CITY_CARE_HINTS: dict[str, str] = {
    "上海": "近期昼夜温差较大，注意呼吸道与慢病管理",
    "杭州": "梅雨季节注意出行路滑和车险联动保障",
    "南京": "换季过敏高发，建议关注门急诊和住院保障",
}


def _behavior_score(behaviors: list[str], viewed_issue_link_count: int) -> int:
    """根据客户行为与链接查看次数计算意愿分数。

    参数:
        behaviors: 客户行为文本列表。
        viewed_issue_link_count: 出单链接查看次数。

    返回:
        int: 行为得分，分数越高表示意愿越强。
    """
    score = 0
    behavior_text = "|".join(behaviors)
    if "多次查看出单链接" in behavior_text:
        score += 45
    if "浏览产品对比页" in behavior_text:
        score += 20
    if "理赔案例" in behavior_text:
        score += 15
    if "第一次点击咨询" in behavior_text or "询问基础概念" in behavior_text:
        score += 8
    score += min(viewed_issue_link_count * 8, 24)
    return score


def _intent_level_from_score(score: int) -> str:
    """根据意愿分数映射高/中/低意向。

    参数:
        score: 客户意愿评分。

    返回:
        str: 意向等级（高意向、中意向、低意向）。
    """
    if score >= 60:
        return "高意向"
    if score >= 40:
        return "中意向"
    return "低意向"


def _resolve_customer(name: str) -> dict[str, Any] | None:
    """按姓名从客户数据库中查询客户信息。

    参数:
        name: 客户姓名。

    返回:
        dict[str, Any] | None: 命中时返回客户画像，未命中返回 None。
    """
    return CUSTOMER_DB.get(name)


def _disease_risk_factor(diseases: list[str]) -> float:
    """根据历史报销疾病列表计算疾病风险系数。

    参数:
        diseases: 历史报销疾病名称列表。

    返回:
        float: 疾病风险系数，用于保费测算。
    """
    high_risk = {"恶性肿瘤", "心脑血管疾病", "慢性肾病"}
    mid_risk = {"乳腺结节", "甲状腺结节", "高血压", "糖尿病"}
    factor = 1.0
    for disease in diseases:
        if disease in high_risk:
            factor += 0.12
        elif disease in mid_risk:
            factor += 0.06
        else:
            factor += 0.03
    return min(factor, 1.55)


def _age_factor(age: int) -> float:
    """根据年龄返回年龄风险系数。

    参数:
        age: 客户年龄。

    返回:
        float: 年龄风险系数。
    """
    if age < 30:
        return 0.88
    if age < 40:
        return 1.0
    if age < 50:
        return 1.22
    return 1.48


def _gender_factor(gender: str) -> float:
    """根据性别返回保费调节系数。

    参数:
        gender: 客户性别（男/女）。

    返回:
        float: 性别调节系数。
    """
    return 1.08 if gender == "男" else 1.0


def _intent_adjustment(intent_level: str) -> float:
    """根据客户意愿等级返回保费微调系数。

    参数:
        intent_level: 客户意愿等级。

    返回:
        float: 意愿调节系数。
    """
    if intent_level == "高意向":
        return 0.96
    if intent_level == "低意向":
        return 1.05
    return 1.0


def _recommend_products_by_age(age: int) -> list[str]:
    """根据年龄返回推荐产品列表。

    参数:
        age: 客户年龄。

    返回:
        list[str]: 推荐产品名称列表。
    """
    if age < 30:
        return ["轻松医疗基础版", "安心意外Max"]
    if age < 40:
        return ["全家医疗Plus", "守护重疾Pro"]
    return ["守护重疾Pro", "臻选医疗VIP"]


def _nearest_festival(today: date) -> dict[str, Any]:
    """计算距离当前日期最近的节日信息。

    参数:
        today: 当前日期。

    返回:
        dict[str, Any]: 最近节日的名称、日期与出行风险信息。
    """
    current_year = today.year
    candidates: list[tuple[int, dict[str, Any]]] = []
    for item in FESTIVAL_CALENDAR:
        festival_date = date(current_year, item["month"], item["day"])
        if festival_date < today:
            festival_date = date(current_year + 1, item["month"], item["day"])
        diff_days = (festival_date - today).days
        candidates.append((diff_days, item))
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


@mcp.tool()
def intelligent_judgment(
    customer_name: str,
) -> dict[str, Any]:
    """根据客户基础信息与行为数据判断当前销售意愿等级。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含判断状态、意愿分数、意向等级与推荐下一步工具。
    """
    customer = _resolve_customer(customer_name)
    if customer is None:
        return {
            "status": "error",
            "message": "未找到客户，请先在 data/customer_db.csv 中维护该客户后再调用",
            "data": None,
        }

    behaviors = list(customer["behaviors"])
    viewed_count = customer["viewed_issue_link_count"]
    inferred_age = customer["age"]

    score = _behavior_score(behaviors, viewed_count)
    if inferred_age >= 40:
        score += 6

    intent_level = _intent_level_from_score(score)
    scene_type = (
        "简单场景"
        if intent_level == "高意向"
        else ("需要培育" if intent_level == "中意向" else "深度引导")
    )

    next_tool = {
        "高意向": "issue_policy_tool",
        "中意向": "product_comparison_tool",
        "低意向": "product_knowledge_share_tool",
    }[intent_level]

    return {
        "status": "success",
        "message": f"已完成客户 {customer_name} 的意愿判断",
        "data": {
            "customer_name": customer_name,
            "age": inferred_age,
            "behaviors": behaviors,
            "viewed_issue_link_count": viewed_count,
            "intent_score": score,
            "intent_level": intent_level,
            "scene_type": scene_type,
            "next_recommended_tool": next_tool,
        },
    }


@mcp.tool()
def issue_policy_tool(
    customer_name: str,
) -> dict[str, Any]:
    """基于客户画像与风险因子生成报价结果并返回出单页面配置。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含保费测算结果、保费拆解、推荐产品与页面元素。
    """
    customer = _resolve_customer(customer_name)
    if customer is None:
        return {
            "status": "error",
            "message": "未找到客户，请先在 data/customer_db.csv 中维护该客户后再调用",
            "data": None,
        }

    resolved_age = customer.get("age")
    resolved_gender = customer.get("gender")
    resolved_claim_count = customer.get("claim_count")
    resolved_reimbursed_diseases = customer.get("reimbursed_diseases")

    if resolved_age is None or resolved_gender is None or resolved_claim_count is None:
        return {
            "status": "error",
            "message": "客户画像缺少出单所需字段（age/gender/claim_count）",
            "data": None,
        }

    if resolved_gender not in {"男", "女"}:
        return {
            "status": "error",
            "message": "gender 仅支持 '男' 或 '女'",
            "data": None,
        }

    resolved_diseases = (
        resolved_reimbursed_diseases
        if isinstance(resolved_reimbursed_diseases, list)
        else []
    )

    judgment = intelligent_judgment(customer_name)
    intent_level = "中意向"
    if judgment["status"] == "success":
        intent_level = judgment["data"]["intent_level"]

    base_premium = 1200
    age_factor = _age_factor(int(resolved_age))
    gender_factor = _gender_factor(str(resolved_gender))
    claims_factor = min(1.0 + int(resolved_claim_count) * 0.09, 1.45)
    disease_factor = _disease_risk_factor(resolved_diseases)
    intent_factor = _intent_adjustment(intent_level)

    annual_premium = round(
        base_premium
        * age_factor
        * gender_factor
        * claims_factor
        * disease_factor
        * intent_factor,
        2,
    )

    monthly_premium = round(annual_premium / 12, 2)
    recommended_products = _recommend_products_by_age(int(resolved_age))
    quote_products = [
        {
            "name": name,
            "type": PRODUCT_CATALOG[name]["type"],
            "coverage_limit": PRODUCT_CATALOG[name]["coverage_limit"],
            "annual_base_premium": PRODUCT_CATALOG[name]["annual_base_premium"],
        }
        for name in recommended_products
    ]

    return {
        "status": "success",
        "tool_name": "issue_policy_tool",
        "action": "render_quote_page",
        "page_url": (
            "https://mock-insurance.com/quote"
            f"?user={customer_name}&age={resolved_age}&gender={resolved_gender}&annual_premium={annual_premium}"
        ),
        "quote": {
            "customer_name": customer_name,
            "intent_level": intent_level,
            "annual_premium": annual_premium,
            "monthly_premium": monthly_premium,
            "premium_breakdown": {
                "base_premium": base_premium,
                "age_factor": age_factor,
                "gender_factor": gender_factor,
                "claims_factor": claims_factor,
                "disease_factor": disease_factor,
                "intent_factor": intent_factor,
            },
            "input_features": {
                "age": resolved_age,
                "gender": resolved_gender,
                "claim_count": resolved_claim_count,
                "reimbursed_diseases": resolved_diseases,
            },
            "recommended_products": quote_products,
        },
        "ui_elements": ["产品方案摘要", "动态测算保费", "一键投保按钮", "核保须知"],
    }


@mcp.tool()
def product_comparison_tool(
    customer_name: str,
) -> dict[str, Any]:
    """根据客户浏览记录输出产品对比结果。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含产品对比表与推荐沟通话术。
    """
    customer = _resolve_customer(customer_name)
    if customer is None:
        return {
            "status": "error",
            "message": "未找到客户，请先在 data/customer_db.csv 中维护该客户后再调用",
            "data": None,
        }

    products = customer["viewed_products"]
    if len(products) < 2:
        products = ["全家医疗Plus", "守护重疾Pro"]

    comparison_rows = []
    for product_name in products:
        detail = PRODUCT_CATALOG.get(product_name)
        if not detail:
            continue
        comparison_rows.append(
            {
                "product": product_name,
                "type": detail["type"],
                "price_band": detail["price_band"],
                "coverage_limit": detail["coverage_limit"],
                "waiting_period": detail["waiting_period"],
                "highlights": detail["highlights"],
                "limitations": detail["limitations"],
            }
        )

    return {
        "status": "success",
        "tool_name": "product_comparison_tool",
        "customer_name": customer_name,
        "comparison_table": comparison_rows,
        "suggested_talk_track": "可先从保额和等待期解释差异，再强调理赔体验。",
    }


@mcp.tool()
def claim_case_tool(
    customer_name: str,
) -> dict[str, Any]:
    """基于年龄和疾病信息匹配理赔案例并返回展示数据。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含匹配案例数量、案例详情与沟通建议。
    """
    customer = _resolve_customer(customer_name)
    if customer is None:
        return {
            "status": "error",
            "message": "未找到客户，请先在 data/customer_db.csv 中维护该客户后再调用",
            "data": None,
        }

    resolved_age = customer.get("age")
    resolved_reimbursed_diseases = customer.get("reimbursed_diseases")

    if resolved_age is None:
        return {
            "status": "error",
            "message": "客户画像缺少理赔案例匹配所需字段（age）",
            "data": None,
        }

    diseases = (
        resolved_reimbursed_diseases
        if isinstance(resolved_reimbursed_diseases, list)
        else []
    )

    matched_cases: list[dict[str, Any]] = []
    for item in CLAIM_CASE_DB:
        disease_hit = item["disease"] in diseases
        age_hit = item["age_min"] <= int(resolved_age) <= item["age_max"]
        if disease_hit or age_hit:
            matched_cases.append(item)

    if not matched_cases:
        matched_cases = CLAIM_CASE_DB[:2]

    output_cases = [
        {
            "case_id": case["case_id"],
            "disease": case["disease"],
            "matched_product": case["product"],
            "claim_amount": case["claim_amount"],
            "approval_days": case["approval_days"],
            "key_point": case["key_point"],
        }
        for case in matched_cases[:3]
    ]

    return {
        "status": "success",
        "tool_name": "claim_case_tool",
        "customer_name": customer_name,
        "matched_case_count": len(output_cases),
        "cases": output_cases,
        "suggested_talk_track": "这些案例和您的年龄/疾病背景相近，可参考理赔速度与赔付金额。",
    }


@mcp.tool()
def personal_needs_analysis_tool(
    customer_name: str,
) -> dict[str, Any]:
    """根据家庭结构和收入水平输出个人保障需求分析。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含推荐预算、保障重点与产品组合建议。
    """
    customer = _resolve_customer(customer_name)
    if customer is None:
        return {
            "status": "error",
            "message": "未找到客户，请先在 data/customer_db.csv 中维护该客户后再调用",
            "data": None,
        }

    resolved_age = customer.get("age")
    resolved_annual_income = customer.get("annual_income")
    resolved_family_structure = customer.get("family_structure")

    if (
        resolved_age is None
        or resolved_annual_income is None
        or resolved_family_structure is None
    ):
        return {
            "status": "error",
            "message": "客户画像缺少需求分析所需字段（age/annual_income/family_structure）",
            "data": None,
        }

    gross_budget = int(int(resolved_annual_income) * 0.1)
    existing_insurance_budget = 0
    recommended_budget = max(gross_budget - existing_insurance_budget, 1200)
    budget_monthly = round(recommended_budget / 12, 2)

    has_children = "孩" in str(resolved_family_structure)
    has_spouse = "已婚" in str(resolved_family_structure)

    demand_focus = ["医疗保障", "重大疾病保障"]
    if has_children:
        demand_focus.append("家庭责任保障")
    if int(resolved_age) >= 40:
        demand_focus.append("心脑血管风险保障")
    if not has_spouse and not has_children:
        demand_focus.append("高杠杆意外保障")

    recommended_products = _recommend_products_by_age(int(resolved_age))
    portfolio = [
        {
            "product": p,
            "allocation_ratio": 0.5 if idx == 0 else 0.3 if idx == 1 else 0.2,
            "estimated_budget": round(
                recommended_budget * (0.5 if idx == 0 else 0.3 if idx == 1 else 0.2),
                2,
            ),
            "coverage_scope": PRODUCT_CATALOG[p]["coverage_scope"],
        }
        for idx, p in enumerate(recommended_products)
    ]

    return {
        "status": "success",
        "tool_name": "personal_needs_analysis_tool",
        "customer_name": customer_name,
        "analysis": {
            "annual_income": resolved_annual_income,
            "family_structure": resolved_family_structure,
            "age": resolved_age,
            "recommended_annual_budget": recommended_budget,
            "recommended_monthly_budget": budget_monthly,
            "demand_focus": demand_focus,
            "recommended_portfolio": portfolio,
        },
    }


@mcp.tool()
def nurturing_process_tools(customer_name: str) -> dict[str, Any]:
    """返回中意向客户培育阶段的过程工具清单。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含可编排的过程工具列表。
    """
    return {
        "status": "success",
        "tool_name": "nurturing_process_tools",
        "customer_name": customer_name,
        "available_tools": [
            {
                "id": "product_comparison_tool",
                "name": "产品对比",
                "desc": "基于客户浏览产品生成差异化对比",
            },
            {
                "id": "claim_case_tool",
                "name": "理赔案例",
                "desc": "基于年龄和疾病给出相似理赔案例",
            },
            {
                "id": "personal_needs_analysis_tool",
                "name": "个人客户需求分析",
                "desc": "输出预算、险种组合、保障范围",
            },
        ],
    }


@mcp.tool()
def product_knowledge_share_tool(
    customer_name: str,
) -> dict[str, Any]:
    """根据客户历史咨询产品生成科普知识卡片。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含知识卡片、文章标题与海报素材地址。
    """
    customer = _resolve_customer(customer_name)
    if customer is None:
        return {
            "status": "error",
            "message": "未找到客户，请先在 data/customer_db.csv 中维护该客户后再调用",
            "data": None,
        }

    products = customer["consulted_products"]
    if not products:
        products = ["全家医疗Plus"]

    knowledge_cards = []
    for name in products:
        item = PRODUCT_CATALOG.get(name)
        if not item:
            continue
        knowledge_cards.append(
            {
                "product": name,
                "insurable_diseases": item["coverage_scope"],
                "payout_scope": item["highlights"],
                "coverage_limit": item["coverage_limit"],
                "easy_explain": f"{name} 适合先解决 {item['type']} 的核心保障缺口。",
            }
        )

    return {
        "status": "success",
        "tool_name": "product_knowledge_share_tool",
        "customer_name": customer_name,
        "knowledge_cards": knowledge_cards,
        "share_material": {
            "article_title": "3分钟读懂医疗+重疾如何搭配",
            "poster_url": "https://mock-insurance.com/materials/knowledge-poster-01.png",
        },
    }


@mcp.tool()
def agent_ai_business_card_tool(
    agent_name: str = "金牌顾问小安",
    specialty: str = "医疗险+重疾险组合规划",
) -> dict[str, Any]:
    """生成可分享可追踪的代理人 AI 名片素材。

    参数:
        agent_name: 代理人名称。
        specialty: 代理人擅长领域描述。

    返回:
        dict[str, Any]: 包含名片信息、分享链接与追踪编码。
    """
    return {
        "status": "success",
        "tool_name": "agent_ai_business_card_tool",
        "card": {
            "agent_name": agent_name,
            "title": "家庭保障规划顾问",
            "specialty": specialty,
            "service_tags": ["保费优化", "家庭保障配置", "理赔协助"],
            "share_link": "https://mock-insurance.com/agent-card/AI-001",
            "track_code": "track_ai_card_001",
        },
    }


@mcp.tool()
def periodic_care_tool(
    customer_name: str,
) -> dict[str, Any]:
    """基于节日与城市信息生成定期关怀文案和保障建议。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含关怀文案、关联产品与下次触达建议。
    """
    customer = _resolve_customer(customer_name)
    if customer is None:
        return {
            "status": "error",
            "message": "未找到客户，请先在 data/customer_db.csv 中维护该客户后再调用",
            "data": None,
        }

    city_name = customer["city"]
    festival = _nearest_festival(date.today())

    care_hint = CITY_CARE_HINTS.get(
        city_name, "近期注意出行安全与天气变化，建议完善意外与医疗保障。"
    )
    event_name = festival["name"]
    travel_risk = festival.get("travel_risk", "节假日出行与天气变化风险增加")

    return {
        "status": "success",
        "tool_name": "periodic_care_tool",
        "customer_name": customer_name,
        "city": city_name,
        "event": event_name,
        "care_message": (
            f"{event_name}将近，{care_hint}。{travel_risk}，"
            "建议提前配置意外医疗与交通意外保障。"
        ),
        "linked_products": ["安心意外Max", "全家医疗Plus"],
        "schedule_suggestion": {
            "next_touchpoint": "3天后回访",
            "channel": "企业微信",
        },
    }


@mcp.tool()
def deep_guidance_tools(customer_name: str) -> dict[str, Any]:
    """返回低意向或复杂场景下的深度引导工具清单。

    参数:
        customer_name: 客户姓名。

    返回:
        dict[str, Any]: 包含可编排的深度引导工具列表。
    """
    return {
        "status": "success",
        "tool_name": "deep_guidance_tools",
        "customer_name": customer_name,
        "available_tools": [
            {
                "id": "product_knowledge_share_tool",
                "name": "产品知识分享",
                "desc": "基于客户咨询过的产品输出可保疾病、赔付范围、保额科普",
            },
            {
                "id": "agent_ai_business_card_tool",
                "name": "内容营销素材库（代理人AI名片）",
                "desc": "生成可追踪分享的代理人专业名片",
            },
            {
                "id": "periodic_care_tool",
                "name": "定期关怀",
                "desc": "基于节日/天气给出问候文案并关联保障卖点",
            },
        ],
    }


def create_sse_app(mount_path: str) -> Any:
    """创建用于 SSE 传输的 MCP ASGI 应用。

    参数:
        mount_path: SSE 路由挂载前缀。传入 "/" 时对外暴露 `/sse` 和 `/messages/`。

    返回:
        Any: 可直接交给 uvicorn 运行的 ASGI 应用对象。
    """
    return mcp.sse_app(mount_path=mount_path)


def parse_cli_args() -> argparse.Namespace:
    """解析命令行参数，用于配置服务监听地址与端口。

    参数:
        无。

    返回:
        argparse.Namespace: 包含 host、port、mount_path、log_level 四个字段。
    """
    parser = argparse.ArgumentParser(
        description="Run SalesScenarioMockTools MCP server with SSE via uvicorn"
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", "127.0.0.1"),
        help="监听 IP 地址，默认 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8000")),
        help="监听端口，默认 8000",
    )
    parser.add_argument(
        "--mount-path",
        default=os.getenv("MCP_MOUNT_PATH", "/"),
        help="SSE 路由挂载路径，默认 '/'",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("MCP_LOG_LEVEL", "info"),
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="uvicorn 日志级别",
    )
    return parser.parse_args()


def run_sse_server_with_uvicorn(
    host: str,
    port: int,
    mount_path: str,
    log_level: str,
) -> None:
    """使用 uvicorn 启动基于 SSE 传输的 Sales Mock MCP 服务。

    参数:
        host: 服务监听 IP。
        port: 服务监听端口。
        mount_path: SSE 路由挂载前缀。
        log_level: uvicorn 日志级别。

    返回:
        None: 函数会阻塞运行，直到服务退出。
    """
    app_instance = create_sse_app(mount_path=mount_path)
    uvicorn.run(app_instance, host=host, port=port, log_level=log_level)


app = create_sse_app(mount_path=os.getenv("MCP_MOUNT_PATH", "/"))


if __name__ == "__main__":
    args = parse_cli_args()
    print(
        "Starting SalesScenarioMockTools MCP Server via uvicorn "
        f"(transport=sse, host={args.host}, port={args.port}, mount_path={args.mount_path})..."
    )
    run_sse_server_with_uvicorn(
        host=args.host,
        port=args.port,
        mount_path=args.mount_path,
        log_level=args.log_level,
    )
