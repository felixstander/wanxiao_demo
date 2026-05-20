#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
car_negotiate_demo.py

车险谈判中间件演示脚本。

演示内容：
1. 创建带有 CarNegotiateMiddleware 的 deep agent
2. 模拟车险销售对话的多个阶段
3. 观察 before_agent 注入的意图分析和 skill 选择指导
4. 观察 after_agent 抽取的对话关键信息

使用方法：
    python car_negotiate_demo.py

环境要求：
    - .env 文件中配置 OPENROUTER_API_KEY
"""

import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from car_negotiate_middleware import CarNegotiateMiddleware
from car_negotiate_tools import CAR_NEGOTIATE_TOOLS

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = PROJECT_ROOT / "skills" / "car-negotiate-skills"

# 模拟对话场景（完整10轮，覆盖 M1-M10 全链路）
DEMO_CONVERSATION = [
    {
        "role": "user",
        "content": "你好，我想给我的车报个价，车牌号是京A12345，大众帕萨特",
        "expected_skill": "car-quote",
        "stage": "M1-报价",
    },
    {
        "role": "user",
        "content": "这个方案都保什么？能给我详细讲讲吗",
        "expected_skill": "car-plan-explain",
        "stage": "M2-方案讲解",
    },
    {
        "role": "user",
        "content": "我觉得三者险200万不够，我想升到300万",
        "expected_skill": "car-plan-adjust",
        "stage": "M3-方案调整",
    },
    {
        "role": "user",
        "content": "这个价格有点贵啊，能不能便宜点",
        "expected_skill": "car-price-negotiate",
        "stage": "M4-价格谈判",
    },
    {
        "role": "user",
        "content": "为什么比去年贵了好多？去年才3200",
        "expected_skill": "car-price-diff-explain",
        "stage": "M5-价格差异解释",
    },
    {
        "role": "user",
        "content": "你们有什么赠品或者优惠吗",
        "expected_skill": "car-service-card",
        "stage": "M6-服务卡券",
    },
    {
        "role": "user",
        "content": "我听说人保比你们便宜，你们有什么优势",
        "expected_skill": "car-competitor-compare",
        "stage": "M7-竞品对比",
    },
    {
        "role": "user",
        "content": "我再考虑考虑吧",
        "expected_skill": "car-promotion",
        "stage": "M8-促单",
    },
    {
        "role": "user",
        "content": "你们理赔快吗？出险了怎么理赔",
        "expected_skill": "car-claim-service",
        "stage": "M9-理赔服务",
    },
    {
        "role": "user",
        "content": "好的，我确定了，现在就办理吧",
        "expected_skill": "car-payment",
        "stage": "M10-投保支付",
    },
]


def build_car_negotiate_agent(
    use_middleware: bool = True, user_id: str = "demo-user-001"
):
    """构建带有 CarNegotiateMiddleware 的车险谈判 Agent。

    Args:
        use_middleware: 是否启用中间件（用于对比效果）
        user_id: 用户ID，用于区分不同用户的会话数据
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = "minimax/minimax-m2.5"
    extrace_model_name = "qwen/qwen3.5-35b-a3b"

    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Please set it in .env")

    os.environ["OPENAI_API_KEY"] = api_key

    # 主模型
    llm = ChatOpenAI(
        model=model_name,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
    )

    # 构建 system prompt
    system_prompt = """你是一位专业的平安车险销售顾问，擅长车险转保业务。

你的任务是根据客户的需求，灵活运用各种 skill 模块为客户提供专业服务。

当前可用的 skill 模块包括：
- car-quote: 车险报价（M1）
- car-plan-explain: 方案讲解（M2）
- car-plan-adjust: 方案调整（M3）
- car-price-negotiate: 价格谈判（M4）
- car-price-diff-explain: 价格差异解释（M5）
- car-service-card: 服务卡券（M6）
- car-competitor-compare: 竞品对比（M7）
- car-promotion: 促单（M8）
- car-claim-service: 理赔服务（M9）
- car-payment: 投保支付（M10）

工作原则：
1. 仔细倾听客户需求，选择最合适的 skill 模块
2. 每个对话阶段明确当前所处的模块
3. 使用专业但通俗易懂的语言
4. 不贬低竞品，突出平安差异化优势
5. 积极促成成交，但不强迫客户
"""

    # 使用本地 FilesystemBackend（演示用，不需要 Daytona）
    backend = FilesystemBackend(root_dir=str(PROJECT_ROOT))
    skills = [str(SKILLS_DIR)]

    # 构建中间件列表
    middleware_list = []
    if use_middleware:
        # 用于 after_agent 抽取事实 + before_agent 策略推荐的模型
        middleware_llm = ChatOpenAI(
            model=extrace_model_name,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.1,
        )
        middleware = CarNegotiateMiddleware(
            extraction_llm=middleware_llm,
            strategy_llm=middleware_llm,
            db_path=PROJECT_ROOT / "car_negotiate.db",
            output_dir=PROJECT_ROOT / "middleware_logs",
        )
        middleware.set_user_id(user_id)
        middleware_list.append(middleware)
        print(f"✅ 中间件已启用 (user_id={user_id})")
    else:
        print("⚠️  中间件已禁用（用于对比效果）")

    agent = create_deep_agent(
        model=llm,
        tools=CAR_NEGOTIATE_TOOLS,
        store=InMemoryStore(),
        backend=backend,
        skills=skills,
        middleware=middleware_list,
        checkpointer=MemorySaver(),
        system_prompt=system_prompt,
    )

    return agent, middleware_list[0] if middleware_list else None


def run_demo():
    """运行演示对话。"""
    print("=" * 80)
    print("车险谈判中间件演示")
    print("=" * 80)
    print(f"\n📂 Skills 目录: {SKILLS_DIR}")
    print(f"📂 中间件日志目录: {PROJECT_ROOT / 'middleware_logs'}")
    print("\n" + "=" * 80)

    agent, _ = build_car_negotiate_agent(use_middleware=True)
    thread_id = "car-negotiate-demo-001"

    # 逐轮执行对话
    for i, turn in enumerate(DEMO_CONVERSATION, 1):
        print(f"\n{'─' * 80}")
        print(
            f"🔄 第 {i} 轮对话 | 预期阶段: {turn['stage']} | 预期 Skill: {turn['expected_skill']}"
        )
        print(f"👤 用户: {turn['content']}")
        print("─" * 80)

        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": turn["content"]}]},
                config={"configurable": {"thread_id": thread_id}},
            )

            # 提取 AI 回复
            ai_reply = ""
            messages = result.get("messages", [])
            for msg in reversed(messages):
                msg_type = ""
                content = ""
                if isinstance(msg, dict):
                    msg_type = msg.get("type", "") or msg.get("role", "")
                    content = msg.get("content", "")
                else:
                    msg_type = getattr(msg, "type", "")
                    content = getattr(msg, "content", "")

                if msg_type in ("ai", "assistant", "AIMessage"):
                    ai_reply = content if isinstance(content, str) else str(content)
                    break

            print(
                f"🤖 坐席: {ai_reply[:300]}..."
                if len(ai_reply) > 300
                else f"🤖 坐席: {ai_reply}"
            )

        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 80)
    print("演示结束")
    print(f"📄 中间件抽取的会话数据已保存到: {PROJECT_ROOT / 'middleware_logs'}")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
