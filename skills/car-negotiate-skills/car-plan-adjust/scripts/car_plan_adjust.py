#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险方案调整工具

功能：根据客户需求调整保险方案并计算保费变化
调用方式：python car_plan_adjust.py --current_coverages "交强险,车损险,三者险(200万)" --action add --target "盗抢险"
"""

import argparse
import json


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


def adjust_plan(current_coverages: list, action: str, target: str, new_value: str = None) -> dict:
    current = [c.strip() for c in current_coverages.split(",")] if isinstance(current_coverages, str) else current_coverages
    new_coverages = current.copy()

    old_premium = sum(COVERAGE_PREMIUMS.get(c, 0) for c in current)

    if action == "add":
        if target not in new_coverages:
            new_coverages.append(target)
        else:
            return {"error": f"{target} 已在当前方案中"}
    elif action == "remove":
        if target in new_coverages:
            new_coverages.remove(target)
        else:
            return {"error": f"{target} 不在当前方案中"}
    elif action == "modify":
        if target in new_coverages:
            idx = new_coverages.index(target)
            new_coverages[idx] = new_value
        else:
            return {"error": f"{target} 不在当前方案中"}
    else:
        return {"error": f"未知操作类型: {action}"}

    new_premium = sum(COVERAGE_PREMIUMS.get(c, 0) for c in new_coverages)
    premium_change = round(new_premium - old_premium, 2)

    return {
        "old_coverages": current,
        "new_coverages": new_coverages,
        "old_premium": round(old_premium, 2),
        "new_premium": round(new_premium, 2),
        "premium_change": premium_change,
        "action": action,
        "target": target,
    }


def main():
    parser = argparse.ArgumentParser(description="车险方案调整工具")
    parser.add_argument("--current_coverages", required=True, help="当前险种列表，逗号分隔")
    parser.add_argument("--action", required=True, choices=["add", "remove", "modify"], help="变更类型")
    parser.add_argument("--target", required=True, help="目标险种")
    parser.add_argument("--new_value", default=None, help="新值（modify时使用）")

    args = parser.parse_args()
    result = adjust_plan(args.current_coverages, args.action, args.target, args.new_value)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
