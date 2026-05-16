#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车险投保支付工具

功能：模拟车险投保支付系统，生成支付链接和订单
调用方式：python car_payment.py --plate_number "京A12345" --total_premium 3800 --payment_method "微信支付"
"""

import argparse
import json
import random
import time


PAYMENT_METHODS = {
    "微信支付": {"channel": "wechat", "icon": "💚"},
    "支付宝": {"channel": "alipay", "icon": "💙"},
    "银行卡": {"channel": "bank_card", "icon": "💳"},
    "平安APP": {"channel": "pingan_app", "icon": "🛡️"},
}


def create_payment(plate_number: str, total_premium: float, payment_method: str) -> dict:
    """
    模拟车险投保支付系统
    """
    method_info = PAYMENT_METHODS.get(payment_method, PAYMENT_METHODS["微信支付"])
    
    # 生成订单号
    timestamp = int(time.time())
    order_id = f"PA{timestamp}{random.randint(1000, 9999)}"
    
    # 生成支付链接（模拟）
    payment_url = f"https://payment.pingan.com/order/{order_id}?channel={method_info['channel']}"
    
    return {
        "plate_number": plate_number,
        "total_premium": total_premium,
        "payment_method": payment_method,
        "order_id": order_id,
        "payment_url": payment_url,
        "status": "待支付",
        "expire_time": "30分钟内有效",
        "instructions": [
            f"1. 点击支付链接或扫描二维码",
            f"2. 确认支付金额：{total_premium}元",
            f"3. 完成支付验证",
            f"4. 等待支付结果确认",
        ],
        "support_hotline": "95511",
    }


def query_payment_status(order_id: str) -> dict:
    """
    查询支付状态（模拟）
    """
    # 模拟支付成功
    statuses = ["支付成功", "支付处理中", "待支付"]
    status = random.choice(statuses)
    
    result = {
        "order_id": order_id,
        "status": status,
    }
    
    if status == "支付成功":
        result.update({
            "policy_number": f"PA{random.randint(1000000000, 9999999999)}",
            "effective_date": "次日零时",
            "electronic_policy_url": f"https://policy.pingan.com/epolicy/{order_id}",
            "message": "支付成功！保单已生成，您可以在平安APP查看电子保单。",
        })
    elif status == "支付处理中":
        result["message"] = "支付正在处理中，请稍候..."
    else:
        result["message"] = "尚未完成支付，请尽快完成支付以确保保单生效。"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="车险投保支付工具")
    parser.add_argument("--plate_number", required=True, help="车牌号")
    parser.add_argument("--total_premium", type=float, required=True, help="总保费金额")
    parser.add_argument("--payment_method", default="微信支付", help="支付方式")
    parser.add_argument("--query_status", help="查询订单状态")

    args = parser.parse_args()

    if args.query_status:
        result = query_payment_status(args.query_status)
    else:
        result = create_payment(args.plate_number, args.total_premium, args.payment_method)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
