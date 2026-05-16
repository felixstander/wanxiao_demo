#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险促单工具

功能：根据客户信号返回促单策略和话术
调用方式：python car_promotion.py --customer_signal "问付款"
"""

import argparse
import json


PROMOTION_STRATEGIES = {
    "问付款": {
        "promotion_strategy": "直接促成",
        "talking_points": [
            "您可以直接通过平安APP支付，也可以微信/支付宝",
            "支付完成后保单立即生效",
            "我现在就帮您生成支付链接"
        ],
        "urgency": "低",
        "next_step": "引导支付"
    },
    "问生效": {
        "promotion_strategy": "确认需求+促成",
        "talking_points": [
            "保单支付成功后立即生效",
            "您希望什么时候生效？今天还是明天？",
            "我帮您设置为明天零时生效，这样今天还能享受旧保单保障"
        ],
        "urgency": "中",
        "next_step": "确认生效时间并促成"
    },
    "犹豫": {
        "promotion_strategy": "限时优惠+紧迫感",
        "talking_points": [
            "这个优惠价格今天截止，明天就恢复原价了",
            "现在投保还送道路救援全年服务",
            "您看这样，我先帮您预留这个优惠，您今天确定下来就行"
        ],
        "urgency": "高",
        "next_step": "预留优惠并确认"
    },
    "反复询问": {
        "promotion_strategy": "总结确认+直接促成",
        "talking_points": [
            "我来帮您总结一下：您投保的是全面方案，总保费XXX元",
            "保障包括交强险、车损险、三者险200万、座位险",
            "您看没问题的话，我现在就帮您办理"
        ],
        "urgency": "中",
        "next_step": "总结方案并促成"
    },
    "要和家人商量": {
        "promotion_strategy": "预留优惠+限时",
        "talking_points": [
            "理解，买保险确实要和家里商量一下",
            "不过这个价格今天是最后一天了",
            "我先帮您预留，您今天之内确认就行"
        ],
        "urgency": "高",
        "next_step": "预留优惠"
    }
}


def get_promotion_strategy(customer_signal: str) -> dict:
    strategy = PROMOTION_STRATEGIES.get(customer_signal, {
        "promotion_strategy": "通用促成",
        "talking_points": [
            "这个方案性价比很高",
            "保障全面，服务也好"
        ],
        "urgency": "中",
        "next_step": "确认意向"
    })

    return {
        "customer_signal": customer_signal,
        **strategy
    }


def main():
    parser = argparse.ArgumentParser(description="车险促单工具")
    parser.add_argument("--customer_signal", required=True, help="客户信号")
    args = parser.parse_args()
    result = get_promotion_strategy(args.customer_signal)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
