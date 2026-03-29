#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内部保险产品问答工具

功能：查询内部保险产品数据库，获取条款、费率、理赔规则等官方信息
调用方式：python product_answer.py --question "保险问题"
输出：answer (str) - 关于保险问题的文本答案

示例：
    python product_answer.py --question "重疾险等待期是多少天"
    python product_answer.py --question "30岁男性重疾险50万保额年缴保费"
"""

import argparse
import sys
import json
from typing import Optional

# 模拟内部数据库连接（实际实现中应替换为真实的数据库或API调用）
class InsuranceDatabase:
    """模拟内部保险产品数据库"""
    
    def __init__(self):
        # 模拟产品数据
        self.products = {
            "重疾险": {
                "name": "XX重疾险（2024版）",
                "waiting_period": "90天",
                "coverage": "100种重疾 + 50种轻症",
                "premium_table": {
                    "30岁男性": {"50万": "8500.00", "30万": "5200.00"},
                    "30岁女性": {"50万": "7800.00", "30万": "4800.00"},
                }
            },
            "百万医疗险": {
                "name": "安康百万医疗险（2024版）",
                "waiting_period": "30天",
                "coverage": "一般医疗200万，重疾医疗400万",
                "premium_table": {
                    "30岁": "680",
                    "35岁": "850",
                }
            }
        }
    
    def query(self, question: str) -> str:
        """
        根据问题查询保险产品信息
        
        Args:
            question: 标准化的保险问题描述
            
        Returns:
            answer: 关于保险问题的文本答案
        """
        # TODO: 实际实现中应使用NLP或规则引擎解析问题
        # 这里仅作为伪代码示例
        
        question_lower = question.lower()
        
        # 模拟查询逻辑
        if "重疾险" in question and "等待期" in question:
            product = self.products["重疾险"]
            return f"""根据《{product['name']}》条款第3.2条：

等待期：自合同生效日起 {product['waiting_period']}（等待期内非意外身故退还已交保费）

条款依据：第3.2条 等待期定义
数据更新时间：2024-01-15"""
        
        elif "保费" in question and "30岁男性" in question and "50万" in question:
            product = self.products["重疾险"]
            premium = product["premium_table"]["30岁男性"]["50万"]
            return f"""根据《{product['name']}》：

被保人：30岁男性
保额：500,000元
年缴保费：¥{premium}/年（标准体费率）

注：最终保费以核保结果为准，可能因健康状况、职业类别等因素调整。"""
        
        elif "百万医疗险" in question:
            product = self.products["百万医疗险"]
            return f"""产品：{product['name']}

保障范围：
- {product['coverage']}
- 等待期：{product['waiting_period']}

详情请参考条款原文。"""
        
        else:
            return """未找到与查询相关的产品信息。可能原因：
1. 产品名称可能有差异
2. 该产品可能已停售或仅限特定渠道销售
3. 暂无此产品数据

建议：
- 核对产品完整名称后重试
- 联系客服人工查询：400-XXX-XXXX"""


def sanitize_input(question: str) -> str:
    """
    清理用户输入，防止注入攻击
    
    Args:
        question: 原始输入问题
        
    Returns:
        清理后的问题字符串
    """
    # 移除危险字符
    dangerous_chars = [';', '&', '|', '`', '$', '<', '>']
    for char in dangerous_chars:
        question = question.replace(char, '')
    return question.strip()


def main():
    """主函数：解析命令行参数并执行查询"""
    parser = argparse.ArgumentParser(
        description='内部保险产品问答工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python product_answer.py --question "重疾险等待期是多少天"
  python product_answer.py --question "30岁男性重疾险50万保额年缴保费"
        '''
    )
    
    parser.add_argument(
        '--question',
        type=str,
        required=True,
        help='标准化的保险问题描述（必填）'
    )
    
    # 可选参数（用于扩展）
    parser.add_argument(
        '--format',
        type=str,
        default='text',
        choices=['text', 'json'],
        help='输出格式（默认：text）'
    )
    
    parser.add_argument(
        '--version',
        type=str,
        help='指定条款版本（如：2024版）'
    )
    
    try:
        args = parser.parse_args()
        
        # 输入清理
        question = sanitize_input(args.question)
        
        if not question:
            print("[ERROR] 查询参数异常：问题不能为空", file=sys.stderr)
            sys.exit(1)
        
        # 初始化数据库并查询
        db = InsuranceDatabase()
        answer = db.query(question)
        
        # 根据格式输出
        if args.format == 'json':
            output = {
                "answer": answer,
                "question": question,
                "status": "success"
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            # 标准文本输出（stdout）
            print(answer)
            
    except Exception as e:
        print(f"[ERROR] 数据库连接超时: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()