#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险理赔服务工具

功能：返回理赔流程和服务优势说明
调用方式：python car_claim_service.py --concern_type "速度"
"""

import argparse
import json


CLAIM_PROCESS = {
    "报案": {
        "步骤": "拨打95511或通过平安APP报案",
        "时效": "7x24小时",
        "说明": "随时随地可报案，APP一键报案更便捷"
    },
    "查勘": {
        "步骤": "查勘员联系客户，确认事故情况",
        "时效": "市区30分钟到达",
        "说明": "专业查勘员快速响应"
    },
    "定损": {
        "步骤": "确定损失金额",
        "时效": "简单案件现场定损",
        "说明": "合作修理厂可直接定损"
    },
    "赔付": {
        "步骤": "审核通过后赔付",
        "时效": "万元以下1天赔付",
        "说明": "快速到账，无需等待"
    }
}


ADVANTAGES = {
    "速度": [
        "万元以下案件1天赔付",
        "理赔款最快10分钟到账",
        "小额案件免查勘，直接赔付"
    ],
    "便捷": [
        "APP一键报案，不用打电话",
        "线上传资料，不用跑网点",
        "合作修理厂直赔，不用垫付"
    ],
    "赔付比例": [
        "定损金额100%赔付（不计免赔）",
        "无免赔额（已购买不计免赔）",
        "第三方损失全额赔付"
    ],
    "服务": [
        "7x24小时客服热线",
        "全国通赔，异地出险也能赔",
        "专属理赔顾问一对一服务"
    ]
}


def get_claim_service(concern_type: str) -> dict:
    advantages = ADVANTAGES.get(concern_type, ADVANTAGES["服务"])

    return {
        "concern_type": concern_type,
        "claim_process": CLAIM_PROCESS,
        "advantages": advantages,
        "case_example": {
            "案例": "张先生上周出险，通过APP报案后，查勘员30分钟到达现场，当天完成定损，第二天理赔款就到账了",
            "赔付金额": "8500元",
            "用时": "2天"
        }
    }


def main():
    parser = argparse.ArgumentParser(description="车险理赔服务工具")
    parser.add_argument("--concern_type", default="服务", help="顾虑类型")
    args = parser.parse_args()
    result = get_claim_service(args.concern_type)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
