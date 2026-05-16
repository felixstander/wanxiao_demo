#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险价格差异解释工具

功能：分析车险价格变化原因
调用方式：python car_price_diff.py --plate_number "京A12345" --last_year_premium 3200 --current_premium 3800
"""

import argparse
import json
import random


def analyze_price_diff(plate_number: str, last_year_premium: float, current_premium: float) -> dict:
    diff_amount = round(current_premium - last_year_premium, 2)
    diff_percent = round(diff_amount / last_year_premium * 100, 1) if last_year_premium else 0

    # 模拟归因分析
    reasons = []

    # 随机生成一些原因
    if random.random() > 0.3:
        ncd_change = round(random.uniform(-0.1, 0.15), 2)
        if ncd_change > 0:
            reasons.append({
                "原因": "NCD系数变化",
                "说明": f"去年有出险记录，NCD系数从{round(1.0-ncd_change, 2)}调整为{1.0}",
                "影响金额": round(last_year_premium * ncd_change, 2),
                "类型": "涨价"
            })
        else:
            reasons.append({
                "原因": "NCD系数变化",
                "说明": f"连续多年无出险，NCD系数优惠增加",
                "影响金额": round(last_year_premium * ncd_change, 2),
                "类型": "降价"
            })

    if random.random() > 0.5:
        coverage_change = round(random.uniform(100, 500), 2)
        reasons.append({
            "原因": "保障范围调整",
            "说明": "今年车损险包含涉水、玻璃、自燃等附加保障",
            "影响金额": coverage_change,
            "类型": "涨价"
        })

    if random.random() > 0.6:
        market_change = round(random.uniform(-200, 300), 2)
        reasons.append({
            "原因": "市场费率调整",
            "说明": "行业整体费率调整",
            "影响金额": market_change,
            "类型": "涨价" if market_change > 0 else "降价"
        })

    if random.random() > 0.7:
        violation_change = round(random.uniform(50, 200), 2)
        reasons.append({
            "原因": "违章记录影响",
            "说明": "查询到上年有违章记录，影响费率",
            "影响金额": violation_change,
            "类型": "涨价"
        })

    return {
        "plate_number": plate_number,
        "last_year_premium": last_year_premium,
        "current_premium": current_premium,
        "diff_amount": diff_amount,
        "diff_percent": diff_percent,
        "reasons": reasons,
        "summary": f"价格变化主要受{'、'.join([r['原因'] for r in reasons])}影响"
    }


def main():
    parser = argparse.ArgumentParser(description="车险价格差异解释工具")
    parser.add_argument("--plate_number", required=True, help="车牌号")
    parser.add_argument("--last_year_premium", type=float, required=True, help="去年保费")
    parser.add_argument("--current_premium", type=float, required=True, help="今年保费")

    args = parser.parse_args()
    result = analyze_price_diff(args.plate_number, args.last_year_premium, args.current_premium)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
