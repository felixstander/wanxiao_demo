#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
car_negotiate_tools.py

将车险谈判 skill 中的脚本封装为 LangChain 工具，
供 agent 直接调用，无需依赖 execute/sandbox。
"""

import json
import random
import sys
from pathlib import Path

# 添加 skills 路径以便导入 scripts
SKILLS_ROOT = Path(__file__).resolve().parent / "skills" / "car-negotiate-skills"

# 直接内联实现各工具函数，避免 import 路径问题


def _quote_car_insurance(plate_number: str, vehicle_model: str, ncd_years: int, coverage_list: list) -> dict:
    base_premium = 3500.0
    if "大众" in vehicle_model or "丰田" in vehicle_model:
        base_premium = 3200.0
    elif "宝马" in vehicle_model or "奔驰" in vehicle_model:
        base_premium = 5500.0

    ncd_discount = max(0.5, 1.0 - ncd_years * 0.1)
    breakdown = []

    if "交强险" in coverage_list:
        breakdown.append({"险种": "交强险", "保费": 950.0, "说明": "法定强制保险"})
    if "车船税" in coverage_list:
        breakdown.append({"险种": "车船税", "保费": 480.0, "说明": "按排量征收"})
    if "车损险" in coverage_list:
        premium = round(base_premium * 0.45 * ncd_discount, 2)
        breakdown.append({"险种": "机动车损失保险", "保费": premium, "说明": "保障车辆自身损失"})
    if "三者险(200万)" in coverage_list:
        premium = round(850.0 * ncd_discount, 2)
        breakdown.append({"险种": "第三者责任险(200万)", "保费": premium, "说明": "保障第三方人身财产损失"})
    if "三者险(300万)" in coverage_list:
        premium = round(1100.0 * ncd_discount, 2)
        breakdown.append({"险种": "第三者责任险(300万)", "保费": premium, "说明": "保障第三方人身财产损失"})
    if "座位险" in coverage_list:
        premium = round(150.0 * ncd_discount, 2)
        breakdown.append({"险种": "车上人员责任险", "保费": premium, "说明": "保障车上乘客和司机"})
    if "盗抢险" in coverage_list:
        premium = round(base_premium * 0.08 * ncd_discount, 2)
        breakdown.append({"险种": "全车盗抢保险", "保费": premium, "说明": "保障车辆被盗抢损失"})

    total_premium = round(sum(item["保费"] for item in breakdown), 2)
    return {
        "plate_number": plate_number,
        "vehicle_model": vehicle_model,
        "total_premium": total_premium,
        "breakdown": breakdown,
        "ncd_years": ncd_years,
        "ncd_discount": round(ncd_discount, 2),
        "quote_valid_until": "2026-05-23",
    }


PLAN_DETAILS = {
    "基础方案": [
        {"险种": "交强险", "类型": "必选", "保额": "死亡伤残18万/医疗1.8万/财产0.2万", "保障范围": "保障交通事故中第三方的人身伤亡和财产损失", "说明": "国家强制购买，未购买无法上路行驶"},
        {"险种": "第三者责任险(100万)", "类型": "强烈建议", "保额": "100万元", "保障范围": "保障交通事故中第三方的人身伤亡和财产损失，超出交强险部分", "说明": "建议保额至少100万，一线城市建议200万以上"},
    ],
    "全面方案": [
        {"险种": "交强险", "类型": "必选", "保额": "死亡伤残18万/医疗1.8万/财产0.2万", "保障范围": "保障交通事故中第三方的人身伤亡和财产损失", "说明": "国家强制购买"},
        {"险种": "机动车损失保险", "类型": "强烈建议", "保额": "按车辆实际价值", "保障范围": "保障车辆自身损失，包括碰撞、自然灾害、盗抢等", "说明": "建议购买，特别是新车或价值较高的车辆"},
        {"险种": "第三者责任险(200万)", "类型": "强烈建议", "保额": "200万元", "保障范围": "保障交通事故中第三方的人身伤亡和财产损失", "说明": "建议保额200万以上"},
        {"险种": "车上人员责任险", "类型": "建议购买", "保额": "每座1-10万元", "保障范围": "保障车上司机和乘客的人身伤亡", "说明": "经常载人的车辆建议购买"},
    ],
    "豪华方案": [
        {"险种": "交强险", "类型": "必选", "保额": "死亡伤残18万/医疗1.8万/财产0.2万", "保障范围": "保障交通事故中第三方的人身伤亡和财产损失", "说明": "国家强制购买"},
        {"险种": "机动车损失保险", "类型": "强烈建议", "保额": "按车辆实际价值", "保障范围": "保障车辆自身损失", "说明": "包含涉水、玻璃、自燃等保障"},
        {"险种": "第三者责任险(300万)", "类型": "强烈建议", "保额": "300万元", "保障范围": "保障第三方人身财产损失", "说明": "高保额，更安心"},
        {"险种": "车上人员责任险", "类型": "建议购买", "保额": "每座10万元", "保障范围": "保障车上人员", "说明": "高额保障"},
        {"险种": "全车盗抢险", "类型": "可选", "保额": "按车辆实际价值", "保障范围": "保障车辆被盗抢损失", "说明": "停车环境复杂建议购买"},
        {"险种": "玻璃单独破碎险", "类型": "可选", "保额": "按实际损失", "保障范围": "保障车辆玻璃单独破碎", "说明": "经常跑高速建议购买"},
    ],
}

COVERAGE_PREMIUMS = {
    "交强险": 950.0,
    "车船税": 480.0,
    "车损险": 1500.0,
    "三者险(100万)": 650.0,
    "三者险(200万)": 850.0,
    "三者险(300万)": 1100.0,
    "座位险": 150.0,
    "盗抢险": 380.0,
    "划痕险": 280.0,
    "玻璃险": 180.0,
}

NEGOTIATION_STRATEGIES = {
    "太贵": {"strategy": "价值拆解+案例说服", "talking_points": ["张先生，我理解您的顾虑。这个保费折算下来每天不到X元", "保险不是消费，是给自己和家人的一份保障", "现在投保还可以享受NCD无赔款优待，明年续保还能更便宜"], "recommended_discount": "申请95折或赠送道路救援服务"},
    "比去年贵": {"strategy": "归因分析+价值重塑", "talking_points": ["今年保费调整主要是因为行业整体费率调整", "不过今年我们的保障范围也升级了", "虽然保费略有上涨，但保障更全面了"], "recommended_discount": "解释清楚后申请小额优惠"},
    "要求优惠": {"strategy": "限时优惠+增值服务", "talking_points": ["正好这个月我们有转保客户专享活动", "现在投保可以享受道路救援全年不限次数服务", "还可以赠送一次免费代驾"], "recommended_discount": "赠送道路救援+代驾服务"},
}

GIFT_POOL = {
    "普通": [
        {"名称": "道路救援服务", "价值": 300, "说明": "全年不限次数道路救援", "有效期": "1年"},
        {"名称": "代驾服务1次", "价值": 150, "说明": "15公里内免费代驾", "有效期": "1年"},
        {"名称": "洗车券2张", "价值": 100, "说明": "合作门店通用", "有效期": "6个月"},
    ],
    "优质": [
        {"名称": "道路救援服务", "价值": 300, "说明": "全年不限次数道路救援", "有效期": "1年"},
        {"名称": "代驾服务3次", "价值": 450, "说明": "15公里内免费代驾", "有效期": "1年"},
        {"名称": "洗车券5张", "价值": 250, "说明": "合作门店通用", "有效期": "1年"},
        {"名称": "保养抵扣券", "价值": 200, "说明": "指定门店保养抵扣", "有效期": "1年"},
    ],
    "VIP": [
        {"名称": "道路救援服务", "价值": 300, "说明": "全年不限次数道路救援", "有效期": "1年"},
        {"名称": "代驾服务5次", "价值": 750, "说明": "15公里内免费代驾", "有效期": "1年"},
        {"名称": "洗车券10张", "价值": 500, "说明": "合作门店通用", "有效期": "1年"},
        {"名称": "保养抵扣券", "价值": 500, "说明": "指定门店保养抵扣", "有效期": "1年"},
        {"名称": "机场停车券", "价值": 300, "说明": "机场停车3天免费", "有效期": "1年"},
    ],
}

COMPETITOR_DATA = {
    "人保": {"价格": {"我方": "中等", "竞品": "较低", "说明": "人保价格通常略低，但保障范围可能不同"}, "服务": {"我方": "优秀", "竞品": "良好", "说明": "平安理赔速度更快，万元以下1天赔付"}, "保障": {"我方": "全面", "竞品": "全面", "说明": "主要险种保障范围相近"}, "网点": {"我方": "广泛", "竞品": "广泛", "说明": "两家网点都很多"}},
    "太平洋": {"价格": {"我方": "中等", "竞品": "中等", "说明": "价格水平相近"}, "服务": {"我方": "优秀", "竞品": "良好", "说明": "平安APP体验更好，线上服务更便捷"}, "保障": {"我方": "全面", "竞品": "全面", "说明": "主要险种保障范围相近"}, "网点": {"我方": "广泛", "竞品": "广泛", "说明": "两家网点都很多"}},
    "国寿": {"价格": {"我方": "中等", "竞品": "较高", "说明": "国寿价格通常略高"}, "服务": {"我方": "优秀", "竞品": "良好", "说明": "平安理赔速度更快"}, "保障": {"我方": "全面", "竞品": "全面", "说明": "主要险种保障范围相近"}, "网点": {"我方": "广泛", "竞品": "较多", "说明": "平安网点覆盖更广"}},
}

PROMOTION_STRATEGIES = {
    "问付款": {"promotion_strategy": "直接促成", "talking_points": ["您可以直接通过平安APP支付，也可以微信/支付宝", "支付完成后保单立即生效", "我现在就帮您生成支付链接"], "urgency": "低", "next_step": "引导支付"},
    "问生效": {"promotion_strategy": "确认需求+促成", "talking_points": ["保单支付成功后立即生效", "您希望什么时候生效？今天还是明天？", "我帮您设置为明天零时生效"], "urgency": "中", "next_step": "确认生效时间并促成"},
    "犹豫": {"promotion_strategy": "限时优惠+紧迫感", "talking_points": ["这个优惠价格今天截止，明天就恢复原价了", "现在投保还送道路救援全年服务", "您看这样，我先帮您预留这个优惠"], "urgency": "高", "next_step": "确认优惠预留并促成"},
}

CLAIM_PROCESS = {
    "报案": {"步骤": "拨打95511或通过平安APP报案", "时效": "7x24小时", "说明": "随时随地可报案，APP一键报案更便捷"},
    "查勘": {"步骤": "查勘员联系客户，确认事故情况", "时效": "市区30分钟到达", "说明": "专业查勘员快速响应"},
    "定损": {"步骤": "确定损失金额", "时效": "简单案件现场定损", "说明": "合作修理厂可直接定损"},
    "赔付": {"步骤": "审核通过后赔付", "时效": "万元以下1天赔付", "说明": "快速到账，无需等待"},
}


# LangChain Tools
from langchain_core.tools import tool


@tool
def car_quote(plate_number: str, vehicle_model: str, ncd_years: int, coverage_list: list) -> str:
    """车险报价工具。根据车辆信息和投保险种返回报价明细。
    
    Args:
        plate_number: 车牌号，如 "京A12345"
        vehicle_model: 车型，如 "大众帕萨特 2023款"
        ncd_years: 无赔款年数，如 3
        coverage_list: 投保险种列表，如 ["交强险", "车损险", "三者险(200万)", "座位险"]
    """
    result = _quote_car_insurance(plate_number, vehicle_model, ncd_years, coverage_list)
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def car_plan_explain(plan_type: str) -> str:
    """车险方案讲解工具。返回不同方案类型的险种详细说明。
    
    Args:
        plan_type: 方案类型，如 "基础方案"、"全面方案"、"豪华方案"
    """
    coverages = PLAN_DETAILS.get(plan_type, [])
    return json.dumps({"plan_type": plan_type, "coverages": coverages}, ensure_ascii=False, indent=2)


@tool
def car_plan_adjust(current_coverages: list, action: str, target: str, new_value: str = "") -> str:
    """车险方案调整工具。根据客户需求调整保险方案并计算保费变化。
    
    Args:
        current_coverages: 当前险种列表，如 ["交强险", "车损险", "三者险(200万)"]
        action: 变更类型，"add"/"remove"/"modify"
        target: 目标险种
        new_value: 新值（如保额），可选
    """
    if isinstance(current_coverages, str):
        current = [c.strip() for c in current_coverages.split(",")]
    else:
        current = list(current_coverages)
    
    new_coverages = current.copy()
    old_premium = sum(COVERAGE_PREMIUMS.get(c, 0) for c in current)

    if action == "add":
        if target not in new_coverages:
            new_coverages.append(target)
        else:
            return json.dumps({"error": f"{target} 已在当前方案中"}, ensure_ascii=False)
    elif action == "remove":
        if target in new_coverages:
            new_coverages.remove(target)
        else:
            return json.dumps({"error": f"{target} 不在当前方案中"}, ensure_ascii=False)
    elif action == "modify":
        if target in new_coverages:
            idx = new_coverages.index(target)
            new_coverages[idx] = new_value or target

    new_premium = sum(COVERAGE_PREMIUMS.get(c, 0) for c in new_coverages)
    return json.dumps({
        "old_coverages": current,
        "new_coverages": new_coverages,
        "old_premium": old_premium,
        "new_premium": new_premium,
        "premium_change": round(new_premium - old_premium, 2),
    }, ensure_ascii=False, indent=2)


@tool
def car_price_negotiate(objection_type: str, customer_budget: str = "") -> str:
    """车险价格谈判工具。根据客户异议类型返回谈判策略和话术建议。
    
    Args:
        objection_type: 异议类型，如 "太贵"、"比去年贵"、"要求优惠"
        customer_budget: 客户预算（可选）
    """
    strategy = NEGOTIATION_STRATEGIES.get(objection_type, {
        "strategy": "通用谈判策略",
        "talking_points": ["我理解您的顾虑", "让我为您分析一下", "我们有一些增值服务可以为您提供"],
        "recommended_discount": "申请小额优惠或赠送服务",
    })
    result = dict(strategy)
    if customer_budget:
        result["customer_budget"] = customer_budget
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def car_price_diff(plate_number: str, last_year_premium: float, current_premium: float) -> str:
    """车险价格差异解释工具。分析车险价格变化原因。
    
    Args:
        plate_number: 车牌号
        last_year_premium: 去年保费
        current_premium: 今年保费
    """
    diff_amount = round(current_premium - last_year_premium, 2)
    diff_percent = round(diff_amount / last_year_premium * 100, 1) if last_year_premium else 0
    
    reasons = []
    if random.random() > 0.3:
        ncd_change = round(random.uniform(-0.1, 0.15), 2)
        reasons.append({"原因": "NCD系数变化", "说明": f"NCD系数调整", "影响金额": round(last_year_premium * ncd_change, 2), "类型": "涨价" if ncd_change > 0 else "降价"})
    if random.random() > 0.5:
        reasons.append({"原因": "保障范围调整", "说明": "今年车损险包含涉水、玻璃、自燃等保障", "影响金额": round(random.uniform(50, 200), 2), "类型": "涨价"})
    if random.random() > 0.5:
        reasons.append({"原因": "市场费率调整", "说明": "行业整体费率上调", "影响金额": round(random.uniform(30, 150), 2), "类型": "涨价"})
    if random.random() > 0.7:
        reasons.append({"原因": "出险记录影响", "说明": "去年有出险记录导致系数上浮", "影响金额": round(random.uniform(100, 300), 2), "类型": "涨价"})

    return json.dumps({
        "plate_number": plate_number,
        "last_year_premium": last_year_premium,
        "current_premium": current_premium,
        "diff_amount": diff_amount,
        "diff_percent": diff_percent,
        "reasons": reasons,
        "summary": f"今年保费较去年{'上涨' if diff_amount > 0 else '下降'}{abs(diff_amount)}元，主要受NCD系数、保障范围调整和市场费率影响。",
    }, ensure_ascii=False, indent=2)


@tool
def car_service_card(customer_level: str, vehicle_type: str) -> str:
    """车险服务卡券工具。查询可用赠品/卡券资源。
    
    Args:
        customer_level: 客户等级，如 "普通"、"优质"、"VIP"
        vehicle_type: 车型，如 "轿车"、"SUV"
    """
    gifts = GIFT_POOL.get(customer_level, GIFT_POOL["普通"])
    total_value = sum(g["价值"] for g in gifts)
    return json.dumps({
        "customer_level": customer_level,
        "vehicle_type": vehicle_type,
        "available_gifts": gifts,
        "total_value": total_value,
        "note": f"您当前是{customer_level}客户，可享受总价值{total_value}元的增值服务礼包。",
    }, ensure_ascii=False, indent=2)


@tool
def car_competitor_compare(competitor: str, compare_dimension: str) -> str:
    """车险竞品对比工具。获取竞品对比数据。
    
    Args:
        competitor: 竞品公司，如 "人保"、"太平洋"、"国寿"
        compare_dimension: 对比维度，如 "价格"、"服务"、"保障"
    """
    data = COMPETITOR_DATA.get(competitor)
    if not data:
        return json.dumps({"error": f"暂无{competitor}的对比数据"}, ensure_ascii=False)
    
    if compare_dimension in data:
        return json.dumps({"competitor": competitor, "dimension": compare_dimension, "comparison": data[compare_dimension]}, ensure_ascii=False, indent=2)
    
    return json.dumps({"competitor": competitor, "full_comparison": data}, ensure_ascii=False, indent=2)


@tool
def car_promotion(customer_signal: str) -> str:
    """车险促单工具。根据客户信号返回促单策略和话术。
    
    Args:
        customer_signal: 客户信号，如 "问付款"、"问生效"、"犹豫"
    """
    strategy = PROMOTION_STRATEGIES.get(customer_signal, {
        "promotion_strategy": "通用促单策略",
        "talking_points": ["现在投保享受最优费率", "保障从明天开始生效", "有任何问题随时联系我"],
        "urgency": "中",
        "next_step": "确认购买意向",
    })
    return json.dumps(strategy, ensure_ascii=False, indent=2)


@tool
def car_claim_service(concern_type: str) -> str:
    """车险理赔服务工具。返回理赔流程和服务优势说明。
    
    Args:
        concern_type: 顾虑类型，如 "速度"、"便捷"、"赔付比例"
    """
    advantages = {
        "速度": ["万元以下案件1天赔付", "线上理赔，不用跑网点", "审核通过后快速到账"],
        "便捷": ["APP一键报案", "合作修理厂直接定损", "7x24小时服务"],
        "赔付比例": ["定损金额=实际维修金额", "无隐形扣减", "全额赔付"],
    }
    return json.dumps({
        "concern_type": concern_type,
        "claim_process": CLAIM_PROCESS,
        "advantages": advantages.get(concern_type, advantages["速度"]),
        "summary": "平安理赔服务专业、快速、便捷，万元以下1天赔付，让您无后顾之忧。",
    }, ensure_ascii=False, indent=2)


@tool
def car_payment(plate_number: str, total_premium: float, payment_method: str) -> str:
    """车险投保支付工具。生成支付链接和订单。
    
    Args:
        plate_number: 车牌号
        total_premium: 总保费金额
        payment_method: 支付方式，如 "微信支付"、"支付宝"、"银行卡"
    """
    import time
    timestamp = int(time.time())
    order_id = f"PA{timestamp}{random.randint(1000, 9999)}"
    payment_url = f"https://payment.pingan.com/order/{order_id}"
    
    return json.dumps({
        "plate_number": plate_number,
        "total_premium": total_premium,
        "payment_method": payment_method,
        "order_id": order_id,
        "payment_url": payment_url,
        "status": "待支付",
        "expire_time": "30分钟内有效",
        "instructions": [
            "1. 点击支付链接或扫描二维码",
            f"2. 确认支付金额：{total_premium}元",
            "3. 完成支付验证",
            "4. 等待支付结果确认",
        ],
        "support_hotline": "95511",
    }, ensure_ascii=False, indent=2)


# 工具列表
CAR_NEGOTIATE_TOOLS = [
    car_quote,
    car_plan_explain,
    car_plan_adjust,
    car_price_negotiate,
    car_price_diff,
    car_service_card,
    car_competitor_compare,
    car_promotion,
    car_claim_service,
    car_payment,
]
