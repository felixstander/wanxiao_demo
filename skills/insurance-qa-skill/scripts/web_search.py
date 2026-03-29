#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部网页搜索工具

功能：执行网络搜索，获取实时新闻、政策、市场动态等外部信息
调用方式：python web_search.py --question "搜索问题"
输出：
  - web_detail (List[str]): 前3个相关网页的详细内容
  - web_sumn (str): 基于搜索结果的总结

示例：
    python web_search.py --question "2025年3月保险监管新政策"
    python web_search.py --question "北京今天天气"
"""

import argparse
import sys
import json
import re
from typing import List, Dict, Optional
from datetime import datetime

# 模拟外部搜索API（实际实现中应替换为真实的搜索API，如Google、Bing等）
class WebSearchAPI:
    """模拟外部网页搜索API"""
    
    def __init__(self):
        # 模拟搜索结果数据
        self.mock_results = {
            "保险政策": [
                {
                    "title": "2025年保险监管新规出台",
                    "url": "https://www.cbirc.gov.cn/news/2025/0328/xxx.html",
                    "date": "2025-03-28",
                    "content": "银保监会今日发布《关于规范重疾险业务的通知》，主要内容包括：1. 扩大轻症保障范围；2. 规范费率报备要求；3. 明确新规适用于新备案产品..."
                },
                {
                    "title": "解读最新保险政策：对消费者有何影响",
                    "url": "https://finance.sina.com.cn/insurance/2025-03-27/doc-xxx.shtml",
                    "date": "2025-03-27",
                    "content": "专家分析认为，2025年3月发布的新规主要针对新备案重疾险产品，存量保单原则上不受影响..."
                }
            ],
            "天气": [
                {
                    "title": "北京今日天气预报",
                    "url": "https://weather.com.cn/beijing/20250328",
                    "date": "2025-03-28",
                    "content": "北京今日晴，气温 15-25°C，北风 3 级，空气质量良。未来三天天气预报..."
                }
            ]
        }
    
    def search(self, query: str) -> Dict:
        """
        执行网络搜索
        
        Args:
            query: 搜索查询词
            
        Returns:
            dict: 包含 web_detail 和 web_sumn 的字典
        """
        # TODO: 实际实现中应调用真实的搜索API
        # 这里仅作为伪代码示例
        
        query_lower = query.lower()
        
        # 模拟搜索逻辑
        matched_results = []
        
        for keyword, results in self.mock_results.items():
            if keyword in query_lower or any(kw in query_lower for kw in keyword):
                matched_results.extend(results)
        
        # 如果没有匹配，返回默认结果
        if not matched_results:
            matched_results = [
                {
                    "title": "相关搜索结果",
                    "url": "https://example.com/search",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "content": f"关于'{query}'的搜索结果..."
                }
            ]
        
        # 限制返回前3个结果
        matched_results = matched_results[:3]
        
        # 构建 web_detail (List[str])
        web_detail = []
        for idx, result in enumerate(matched_results, 1):
            detail = f"""网页{idx}标题：{result['title']}
URL：{result['url']}
发布日期：{result['date']}
内容：{result['content']}"""
            web_detail.append(detail)
        
        # 生成 web_sumn (str)
        web_sumn = self._generate_summary(query, matched_results)
        
        return {
            "web_detail": web_detail,
            "web_sumn": web_sumn
        }
    
    def _generate_summary(self, query: str, results: List[Dict]) -> str:
        """
        基于搜索结果生成总结（实际应用中可使用LLM）
        
        Args:
            query: 原始查询
            results: 搜索结果列表
            
        Returns:
            str: 内容总结
        """
        if not results:
            return "未找到相关信息"
        
        # 简单模拟总结逻辑
        if "保险" in query:
            return f"""根据搜索结果，关于"{query}"的主要信息如下：

1. 2025年3月保险监管主要新政策包括扩大轻症保障范围、规范费率报备要求等。
2. 新规主要适用于新备案的重疾险产品，存量保单原则上不受影响。

信息来源：{', '.join([r['title'] for r in results[:2]])}等"""
        
        elif "天气" in query:
            result = results[0]
            return f"""根据搜索结果：

{result['content']}

信息来源：{result['title']}（{result['url'].split('/')[2]}）"""
        
        else:
            sources = [f"{r['title']}（{r['url'].split('/')[2]}）" for r in results[:2]]
            return f"""根据搜索结果，关于"{query}"：

{results[0]['content'][:200]}...

信息来源：{', '.join(sources)}"""


def sanitize_input(query: str) -> str:
    """
    清理用户输入，防止注入攻击并脱敏敏感信息
    
    Args:
        query: 原始输入查询
        
    Returns:
        清理后的查询字符串
    """
    # 移除危险字符
    dangerous_chars = [';', '&', '|', '`', '$', '<', '>']
    for char in dangerous_chars:
        query = query.replace(char, '')
    
    # 脱敏保险敏感信息（保单号、身份证号等）
    # 移除可能的保单号（XX123456格式）
    query = re.sub(r'\b[A-Z]{2}\d{6,}\b', '[保单号已隐藏]', query)
    # 移除可能的身份证号
    query = re.sub(r'\b\d{17}[\dXx]\b', '[身份证已隐藏]', query)
    # 移除手机号
    query = re.sub(r'\b1[3-9]\d{9}\b', '[手机号已隐藏]', query)
    
    return query.strip()


def validate_sources(web_detail: List[str]) -> List[str]:
    """
    验证来源可信度并标记
    
    Args:
        web_detail: 网页详情列表
        
    Returns:
        带可信度标记的详情列表
    """
    validated = []
    
    for detail in web_detail:
        # 提取URL
        url_match = re.search(r'URL：(.+)', detail)
        if url_match:
            url = url_match.group(1)
            
            # 可信度评估
            if any(domain in url for domain in ['.gov.cn', 'cbirc.gov.cn']):
                credibility = "【高可信度：官方来源】"
            elif any(domain in url for domain in ['sina.com', 'qq.com', '163.com', 'sohu.com']):
                credibility = "【中可信度：主流媒体】"
            else:
                credibility = "【低可信度：仅供参考】"
            
            detail = detail + f"\n可信度：{credibility}"
        
        validated.append(detail)
    
    return validated


def main():
    """主函数：解析命令行参数并执行搜索"""
    parser = argparse.ArgumentParser(
        description='外部网页搜索工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python web_search.py --question "2025年3月保险监管新政策"
  python web_search.py --question "北京今天天气"
  python web_search.py --question "重疾险和医疗险区别" --format json
        '''
    )
    
    parser.add_argument(
        '--question',
        type=str,
        required=True,
        help='搜索查询词（必填）'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        default='json',
        choices=['json', 'text'],
        help='输出格式（默认：json）'
    )
    
    parser.add_argument(
        '--num-results',
        type=int,
        default=3,
        help='返回结果数量（默认：3）'
    )
    
    try:
        args = parser.parse_args()
        
        # 输入清理和脱敏
        question = sanitize_input(args.question)
        
        if not question:
            print(json.dumps({
                "web_detail": [],
                "web_sumn": "[ERROR] 查询参数异常：搜索词不能为空",
                "status": "error"
            }, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
        
        # 执行搜索
        api = WebSearchAPI()
        result = api.search(question)
        
        # 验证来源可信度
        result['web_detail'] = validate_sources(result['web_detail'])
        
        # 添加元数据
        result['query'] = question
        result['search_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result['status'] = "success"
        
        # 输出结果
        if args.format == 'json':
            # JSON格式输出（便于程序解析）
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 文本格式输出
            print(f"搜索查询：{result['query']}")
            print(f"搜索时间：{result['search_time']}")
            print("\n" + "="*50)
            print("网页详情：")
            print("="*50)
            for detail in result['web_detail']:
                print(detail)
                print("-"*50)
            print("\n内容总结：")
            print("="*50)
            print(result['web_sumn'])
            
    except Exception as e:
        error_output = {
            "web_detail": [],
            "web_sumn": f"[ERROR] 搜索服务异常: {str(e)}",
            "status": "error"
        }
        print(json.dumps(error_output, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()