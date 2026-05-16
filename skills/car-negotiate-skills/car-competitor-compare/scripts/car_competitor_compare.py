#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险竞品对比工具

功能：获取竞品对比数据
调用方式：python car_competitor_compare.py --competitor "人保" --compare_dimension "服务"
"""

import argparse
import json


COMPETITOR_DATA = {
    "人保": {
        "价格": {"我方": "中等", "竞品": "较低", "说明": "人保价格通常略低，但保障范围可能不同"},
        "服务": {"我方": "优秀", "竞品": "良好", "说明": "平安理赔速度更快，万元以下1天赔付"},
        "保障": {"我方": "全面", "竞品": "全面", "说明": "主要险种保障范围相近"},
        "网点": {"我方": "广泛", "竞品": "广泛", "说明": "两家网点都很多"},
    },
    "太平洋": {
        "价格": {"我方": "中等", "竞品": "中等", "说明": "价格水平相近"},
        "服务": {"我方": "优秀", "竞品": "良好", "说明": "平安APP体验更好，线上服务更便捷"},
        "保障": {"我方": "全面", "竞品": "全面", "说明": "主要险种保障范围相近"},
        "网点": {"我方": "广泛", "竞品": "广泛", "说明": "两家网点都很多"},
    },
    "国寿": {
        "价格": {"我方": "中等", "竞品": "较高", "说明": "国寿价格通常略高"},
        "服务": {"我方": "优秀", "竞品": "良好", "说明": "平安理赔速度更快"},
        "保障": {"我方": "全面", "竞品": "全面", "说明": "主要险种保障范围相近"},
        "网点": {"我方": "广泛", "竞品": "较多", "说明": "平安网点覆盖更广"},
    }
}


def compare_competitor(competitor: str, compare_dimension: str) -> dict:
    data = COMPETITOR_DATA.get(competitor)
    if not data:
        return {"error": f"暂无{competitor}的对比数据"}

    if compare_dimension == "全部":
        comparison = data
    else:
        comparison = {compare_dimension: data.get(compare_dimension, {"说明": "暂无数据"})}

    return {
        "competitor": competitor,
        "compare_dimension": compare_dimension,
        "comparison": comparison,
        "our_advantages": [
            "理赔速度快：万元以下1天赔付",
            "APP体验好：线上报案、理赔、查询一站式",
            "增值服务多：道路救援、代驾、洗车等",
            "网点多：全国超过3000家服务网点"
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="车险竞品对比工具")
    parser.add_argument("--competitor", required=True, help="竞品公司")
    parser.add_argument("--compare_dimension", default="全部", help="对比维度")
    args = parser.parse_args()
    result = compare_competitor(args.competitor, args.compare_dimension)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
