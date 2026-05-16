#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险价格谈判工具

功能：根据客户异议类型返回谈判策略和话术建议
调用方式：python car_price_negotiate.py --objection_type "太贵"
"""

import argparse
import json


NEGOTIATION_STRATEGIES = {
    "太贵": {
        "strategy": "价值拆解+案例说服",
        "talking_points": [
            "张先生，我理解您的顾虑。这个保费折算下来每天不到X元，比一杯咖啡还便宜",
            "去年我们有一位客户，三者险买了200万，结果真的用上了，一次事故赔付了180万",
            "保险不是消费，是给自己和家人的一份保障",
            "现在投保还可以享受NCD无赔款优待，明年续保还能更便宜"
        ],
        "recommended_discount": "申请95折或赠送道路救援服务"
    },
    "比去年贵": {
        "strategy": "归因分析+价值重塑",
        "talking_points": [
            "今年保费调整主要是因为行业整体费率调整",
            "不过今年我们的保障范围也升级了，车损险现在包含了涉水、玻璃、自燃等保障",
            "虽然保费略有上涨，但保障更全面了",
            "而且您今年的NCD系数还是享受了优惠的"
        ],
        "recommended_discount": "解释清楚后申请小额优惠"
    },
    "要求优惠": {
        "strategy": "限时优惠+增值服务",
        "talking_points": [
            "正好这个月我们有转保客户专享活动",
            "现在投保可以享受道路救援全年不限次数服务",
            "还可以赠送一次免费代驾",
            "这个活动月底就结束了，我帮您锁定这个优惠"
        ],
        "recommended_discount": "赠送道路救援+代驾服务"
    },
    "再考虑": {
        "strategy": "紧迫感营造+最后机会",
        "talking_points": [
            "我理解您需要再考虑一下",
            "不过要提醒您，这个报价有效期只有7天",
            "而且月底活动就结束了，到时候可能就没有这些优惠了",
            "我可以先帮您预留这个优惠，您今天确定下来吗"
        ],
        "recommended_discount": "预留优惠+限时提醒"
    }
}


def get_negotiation_strategy(objection_type: str, customer_budget: str = None) -> dict:
    strategy = NEGOTIATION_STRATEGIES.get(objection_type, {
        "strategy": "通用价值说服",
        "talking_points": [
            "我们的方案性价比很高",
            "保障全面，理赔服务好"
        ],
        "recommended_discount": "申请标准优惠"
    })

    result = {
        "objection_type": objection_type,
        "strategy": strategy["strategy"],
        "talking_points": strategy["talking_points"],
        "recommended_discount": strategy["recommended_discount"]
    }

    if customer_budget:
        result["customer_budget"] = customer_budget

    return result


def main():
    parser = argparse.ArgumentParser(description="车险价格谈判工具")
    parser.add_argument("--objection_type", required=True, help="异议类型")
    parser.add_argument("--customer_budget", default=None, help="客户预算")
    args = parser.parse_args()
    result = get_negotiation_strategy(args.objection_type, args.customer_budget)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
