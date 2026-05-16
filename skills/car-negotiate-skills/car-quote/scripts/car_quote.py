#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险报价工具

功能：模拟车险报价系统，根据车辆信息和投保险种返回报价明细
调用方式：python car_quote.py --plate_number "京A12345" --vehicle_model "大众帕萨特" --ncd_years 3 --coverage_list "交强险,车损险,三者险(200万),座位险"
"""

import argparse
import json
import random


def quote_car_insurance(plate_number: str, vehicle_model: str, ncd_years: int, coverage_list: list) -> dict:
    """
    模拟车险报价系统
    """
    # 基础保费计算（模拟）
    base_premium = 3500.0
    if "大众" in vehicle_model or "丰田" in vehicle_model:
        base_premium = 3200.0
    elif "宝马" in vehicle_model or "奔驰" in vehicle_model:
        base_premium = 5500.0

    # NCD折扣系数
    ncd_discount = max(0.5, 1.0 - ncd_years * 0.1)

    # 各险种明细
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


def main():
    parser = argparse.ArgumentParser(description="车险报价工具")
    parser.add_argument("--plate_number", required=True, help="车牌号")
    parser.add_argument("--vehicle_model", required=True, help="车型")
    parser.add_argument("--ncd_years", type=int, default=0, help="无赔款年数")
    parser.add_argument("--coverage_list", default="交强险,车损险,三者险(200万),座位险", help="投保险种，逗号分隔")

    args = parser.parse_args()
    coverage_list = [x.strip() for x in args.coverage_list.split(",")]

    result = quote_car_insurance(args.plate_number, args.vehicle_model, args.ncd_years, coverage_list)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
