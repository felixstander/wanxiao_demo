#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangSmith Token 消耗分析报告
从 LangSmith Trace 中提取各部分 token 消耗数据
"""

import pandas as pd
from datetime import datetime
import json

# 桌面路径
DESKTOP_PATH = "/Users/felixcxr/Desktop"

# ============================================
# 主运行 (LangGraph) 数据
# ============================================
main_run_data = {
    "步骤名称": "LangGraph (总运行)",
    "运行类型": "Chain",
    "模型": "-",
    "耗时(秒)": 42.80,
    "总Tokens": 45484,
    "输入Tokens": 44690,
    "输出Tokens": 794,
    "Cache Read": 20672,
    "说明": "整个对话流程的总消耗"
}

# ============================================
# System Prompt 分析
# ============================================
system_prompt_sections = [
    {
        "部分": "System Prompt - 核心身份定位",
        "描述": "代理人的核心定位、工作原则、身份边界",
        "估算Tokens": 350,
        "占比": "约0.8%",
        "内容摘要": "你是代理人万能销售助手、保险专家助手、服务对象是保险代理人..."
    },
    {
        "部分": "System Prompt - 工作原则与合规",
        "描述": "专业严谨、合规优先、风格要求、沟通风格、合规要求",
        "估算Tokens": 280,
        "占比": "约0.6%",
        "内容摘要": "专业严谨、合规优先、语气温柔专业稳定..."
    },
    {
        "部分": "System Prompt - 输出约束",
        "描述": "对用户可见输出约束、禁止输出的话术类型",
        "估算Tokens": 220,
        "占比": "约0.5%",
        "内容摘要": "禁止输出我来帮你、让我先、一/二/三等结构化引导词..."
    },
    {
        "部分": "System Prompt - 工具说明 (write_todos)",
        "描述": "write_todos 工具的详细使用说明",
        "估算Tokens": 850,
        "占比": "约1.9%",
        "内容摘要": "创建任务列表、何时使用、状态管理、完成要求..."
    },
    {
        "部分": "System Prompt - 文件系统工具",
        "描述": "ls, read_file, write_file, edit_file, glob, grep 工具说明",
        "估算Tokens": 480,
        "占比": "约1.1%",
        "内容摘要": "文件系统交互工具的使用说明和示例..."
    },
    {
        "部分": "System Prompt - execute 工具",
        "描述": "execute 工具的使用说明和示例",
        "估算Tokens": 650,
        "占比": "约1.4%",
        "内容摘要": "执行 shell 命令、使用示例、最佳实践..."
    },
    {
        "部分": "System Prompt - task 工具",
        "描述": "task 工具的使用说明、子代理类型、使用场景",
        "估算Tokens": 1200,
        "占比": "约2.6%",
        "内容摘要": "启动子代理、使用场景、示例用法、注意事项..."
    },
    {
        "部分": "System Prompt - Skills System",
        "描述": "Skills 系统说明、可用技能列表、使用方法",
        "估算Tokens": 900,
        "占比": "约2.0%",
        "内容摘要": "技能库说明、保险产品查询、销售场景、产品推荐等技能..."
    },
    {
        "部分": "System Prompt - 双层记忆系统",
        "描述": "长期记忆和每日日志的说明、记忆准则",
        "估算Tokens": 1800,
        "占比": "约4.0%",
        "内容摘要": "记忆目录结构、何时更新记忆、学习反馈示例..."
    }
]

# ============================================
# 记忆内容 (Memory) 分析
# ============================================
memory_sections = [
    {
        "部分": "Memory - MEMORY.md (长期记忆)",
        "描述": "关键联系人信息：张三、李四、王五的详细资料",
        "估算Tokens": 420,
        "占比": "约0.9%",
        "内容摘要": "张三35岁男性高意向、李四42岁女性中意向、王五28岁男性低意向..."
    },
    {
        "部分": "Memory - Daily 2026-02-28",
        "描述": "今日会话记录和客户分析详情",
        "估算Tokens": 850,
        "占比": "约1.9%",
        "内容摘要": "张三分析、李四分析、王五分析、出单信息..."
    }
]

# ============================================
# Skills (技能文件) 分析
# ============================================
skills_sections = [
    {
        "部分": "Skills - wanxiao-sales-scenario",
        "描述": "万销销售场景技能：客户意向判断与分流",
        "估算Tokens": 2100,
        "占比": "约4.6%",
        "内容摘要": "客户意向判断、工具编排、销售指导手册、MCP工具绑定..."
    },
    {
        "部分": "Skills - 其他技能元数据",
        "描述": "保险产品查询、产品推荐、出单等技能描述",
        "估算Tokens": 680,
        "占比": "约1.5%",
        "内容摘要": "多个技能的名称和描述信息..."
    }
]

# ============================================
# 模型调用步骤详细分析
# ============================================
model_calls = [
    {
        "步骤": "第1轮模型调用",
        "动作": "分析用户意图，调用 read_file 读取 Skill.md",
        "模型": "glm-5",
        "耗时(秒)": 8.34,
        "总Tokens": 9283,
        "输入Tokens": 9051,
        "输出Tokens": 232,
        "CacheRead": 0,
        "输入内容": "System Prompt + Memory + Skills + 用户问题",
        "输出内容": "调用 read_file 工具，参数为万销销售场景 SKILL.md"
    },
    {
        "步骤": "第2轮模型调用",
        "动作": "读取 Skill.md 后，调用 intelligent_judgment 工具",
        "模型": "glm-5",
        "耗时(秒)": 8.13,
        "总Tokens": 11811,
        "输入Tokens": 11659,
        "输出Tokens": 152,
        "CacheRead": 9024,
        "输入内容": "历史上下文 + Skill.md 内容",
        "输出内容": "调用 execute 工具，执行 intelligent_judgment"
    },
    {
        "步骤": "第3轮模型调用",
        "动作": "获取意向后，调用 issue_policy_tool 出单工具",
        "模型": "glm-5",
        "耗时(秒)": 5.17,
        "总Tokens": 11906,
        "输入Tokens": 11834,
        "输出Tokens": 72,
        "CacheRead": 0,
        "输入内容": "历史上下文 + intelligent_judgment 结果",
        "输出内容": "调用 execute 工具，执行 issue_policy_tool"
    },
    {
        "步骤": "第4轮模型调用",
        "动作": "整合所有信息，生成最终回复",
        "模型": "glm-5",
        "耗时(秒)": 15.90,
        "总Tokens": 12484,
        "输入Tokens": 12146,
        "输出Tokens": 338,
        "CacheRead": 11648,
        "输入内容": "完整上下文 + 工具执行结果",
        "输出内容": "张三客户分析报告：高意向阶段、出单信息、下一步建议"
    }
]

# ============================================
# 工具执行结果分析
# ============================================
tool_results = [
    {
        "工具名称": "read_file",
        "描述": "读取万销销售场景 SKILL.md",
        "结果Tokens": 2100,
        "结果内容摘要": "万销销售场景技能完整内容，包含工作流、销售指导手册、工具编排"
    },
    {
        "工具名称": "execute (intelligent_judgment)",
        "描述": "智能判断客户意向",
        "结果Tokens": 380,
        "结果内容摘要": "张三高意向客户分析：意向分数69分、行为特征、推荐工具"
    },
    {
        "工具名称": "execute (issue_policy_tool)",
        "描述": "出单工具执行结果",
        "结果Tokens": 620,
        "结果内容摘要": "出单成功：月保费119.79元、年保费1437.5元、报价页面链接"
    }
]

# ============================================
# Token 消耗汇总分类
# ============================================
token_summary = [
    {
        "分类": "System Prompt (系统提示词)",
        "Tokens": 5530,
        "占比": "12.2%",
        "说明": "核心身份、工作原则、工具说明、Skills系统、记忆系统说明"
    },
    {
        "分类": "Memory (记忆内容)",
        "Tokens": 1270,
        "占比": "2.8%",
        "说明": "长期记忆(MEMORY.md) + 每日日志(Daily)"
    },
    {
        "分类": "Skills (技能文件)",
        "Tokens": 2780,
        "占比": "6.1%",
        "说明": "万销销售场景技能及其他技能元数据"
    },
    {
        "分类": "User Input (用户输入)",
        "Tokens": 15,
        "占比": "0.03%",
        "说明": "帮我看一下张三现在处于哪个阶段"
    },
    {
        "分类": "Tool Results (工具结果)",
        "Tokens": 3100,
        "占比": "6.8%",
        "说明": "read_file + intelligent_judgment + issue_policy_tool 结果"
    },
    {
        "分类": "Model Output (模型输出)",
        "Tokens": 794,
        "占比": "1.7%",
        "说明": "4轮模型调用的输出总合"
    },
    {
        "分类": "Context Overhead (上下文开销)",
        "Tokens": 31895,
        "占比": "70.1%",
        "说明": "重复传递的历史上下文、格式化开销、JSON结构等"
    },
    {
        "分类": "总计",
        "Tokens": 45484,
        "占比": "100%",
        "说明": "整个对话流程的总token消耗"
    }
]

# ============================================
# 生成 Excel 文件
# ============================================
def generate_excel():
    """生成包含所有 token 分析数据的 Excel 文件"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{DESKTOP_PATH}/LangSmith_Token_Analysis_{timestamp}.xlsx"
    
    # 创建 Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        
        # 1. 总览表
        df_overview = pd.DataFrame([main_run_data])
        df_overview.to_excel(writer, sheet_name='总览', index=False)
        
        # 2. Token消耗汇总
        df_summary = pd.DataFrame(token_summary)
        df_summary.to_excel(writer, sheet_name='Token消耗汇总', index=False)
        
        # 3. System Prompt 详细分析
        df_system = pd.DataFrame(system_prompt_sections)
        df_system.to_excel(writer, sheet_name='System Prompt分析', index=False)
        
        # 4. Memory 分析
        df_memory = pd.DataFrame(memory_sections)
        df_memory.to_excel(writer, sheet_name='Memory分析', index=False)
        
        # 5. Skills 分析
        df_skills = pd.DataFrame(skills_sections)
        df_skills.to_excel(writer, sheet_name='Skills分析', index=False)
        
        # 6. 模型调用详细
        df_models = pd.DataFrame(model_calls)
        df_models.to_excel(writer, sheet_name='模型调用详细', index=False)
        
        # 7. 工具结果
        df_tools = pd.DataFrame(tool_results)
        df_tools.to_excel(writer, sheet_name='工具结果分析', index=False)
        
        # 8. 优化建议
        suggestions = [
            {
                "优化建议": "System Prompt 精简",
                "当前问题": "System Prompt 约5530 tokens，占比12.2%",
                "优化方案": "将不常用的工具说明移到需要时才加载；精简重复的描述",
                "预期节省": "2000-3000 tokens (约4-7%)"
            },
            {
                "优化建议": "Memory 内容动态加载",
                "当前问题": "Memory 长期加载所有客户信息 (1270 tokens)",
                "优化方案": "只加载与当前问题相关的客户记忆",
                "预期节省": "800-1000 tokens (约2%)"
            },
            {
                "优化建议": "Skills 按需加载",
                "当前问题": "Skills 元数据常驻 (2780 tokens)",
                "优化方案": "根据用户意图动态加载相关 Skill 的完整内容",
                "预期节省": "2000 tokens (约4%)"
            },
            {
                "优化建议": "上下文压缩",
                "当前问题": "Context Overhead 占70.1% (31895 tokens)",
                "优化方案": "使用摘要机制，压缩历史轮次；移除中间过程的冗余信息",
                "预期节省": "5000-10000 tokens (约11-22%)"
            },
            {
                "优化建议": "Cache 机制优化",
                "当前问题": "目前 cache_read 20672 tokens",
                "优化方案": "增加更多重复内容的缓存命中",
                "预期节省": "可减少首次调用延迟"
            }
        ]
        df_suggestions = pd.DataFrame(suggestions)
        df_suggestions.to_excel(writer, sheet_name='优化建议', index=False)
        
        # 9. 原始数据记录
        raw_data = {
            "Trace ID": "019ca274-c11f-7c02-b281-80397c16165a",
            "项目名称": "bc350d71-bb8d-411f-bdf6-771963e07be0",
            "模型": "glm-5 (ChatOpenAI)",
            "总耗时": "42.80秒",
            "首Token时间": "6.42秒",
            "开始时间": "2026-02-28 12:14:46",
            "结束时间": "2026-02-28 12:15:29",
            "总Tokens": 45484,
            "输入Tokens": 44690,
            "输出Tokens": 794,
            "Cache Read": 20672,
            "模型调用次数": 4,
            "工具调用次数": 3
        }
        df_raw = pd.DataFrame([raw_data])
        df_raw.to_excel(writer, sheet_name='原始数据', index=False)
    
    print(f"✅ Excel 文件已生成: {filename}")
    return filename

if __name__ == "__main__":
    generate_excel()
