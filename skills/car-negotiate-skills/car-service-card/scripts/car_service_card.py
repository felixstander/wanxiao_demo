#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险服务卡券工具

功能：查询可用赠品/卡券资源
调用方式：python car_service_card.py --customer_level "优质" --vehicle_type "轿车"
"""

import argparse
import json


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
    ]
}


def query_gifts(customer_level: str, vehicle_type: str) -> dict:
    gifts = GIFT_POOL.get(customer_level, GIFT_POOL["普通"])
    total_value = sum(g["价值"] for g in gifts)

    return {
        "customer_level": customer_level,
        "vehicle_type": vehicle_type,
        "available_gifts": gifts,
        "total_gift_value": total_value,
        "recommendation": f"根据您的{customer_level}客户等级，推荐以下赠品，总价值{total_value}元"
    }


def main():
    parser = argparse.ArgumentParser(description="车险服务卡券工具")
    parser.add_argument("--customer_level", default="普通", help="客户等级")
    parser.add_argument("--vehicle_type", default="轿车", help="车型")
    args = parser.parse_args()
    result = query_gifts(args.customer_level, args.vehicle_type)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
