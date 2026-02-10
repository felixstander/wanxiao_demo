from enum import Enum
from typing import Any, Dict, List

# ==========================================
# 1. Mock Data & API Wrapper
# (参考 arxiv_search.py 的 API 封装模式)
# ==========================================


class InsuranceProductType(str, Enum):
    MEDICAL = "medical"  # 医疗险
    CRITICAL = "critical"  # 重疾险
    ACCIDENT = "accident"  # 意外险


class InsuranceDatabase:
    """
    模拟保险核心系统的 API 包装器。
    在真实场景中，这里会调用后端 REST API 或数据库。
    """

    def __init__(self):
        # 模拟数据库数据
        self._products = [
            {
                "id": "prod_med_001",
                "name": "尊享e生百万医疗险2024",
                "type": InsuranceProductType.MEDICAL,
                "tags": ["报销", "住院", "几百元", "高保额"],
                "base_price": 300,
                "description": "国民级医疗险，最高600万保额。包含一般医疗、重疾医疗，扣除1万免赔额后100%报销。适合需要大额医疗费用保障的人群。",
            },
            {
                "id": "prod_crit_001",
                "name": "超级玛丽9号重疾险",
                "type": InsuranceProductType.CRITICAL,
                "tags": ["确诊给钱", "收入补偿", "几千元", "长期"],
                "base_price": 3000,
                "description": "确诊合同约定的110种重疾，直接赔付保额（如50万）。这笔钱不限用途，可用于康复或弥补收入损失。",
            },
            {
                "id": "prod_acc_001",
                "name": "大护甲5号意外险",
                "type": InsuranceProductType.ACCIDENT,
                "tags": ["意外身故", "跌打损伤", "几十元", "极高性价比"],
                "base_price": 100,
                "description": "主要保障意外导致的身故、伤残以及意外医疗费用（如猫抓狗咬、摔伤）。价格非常便宜。",
            },
            # --- 新增 10 款产品 ---
            # 1. 医疗险补充
            {
                "id": "prod_med_002",
                "name": "好医保长期医疗（20年版）",
                "type": InsuranceProductType.MEDICAL,
                "tags": ["报销", "保证续保", "支付宝", "长期医疗"],
                "base_price": 260,
                "description": "保证续保20年，期间产品停售也可续保。保额400万，非常适合担心未来买不到保险的人群。",
            },
            {
                "id": "prod_med_003",
                "name": "少儿门诊暖宝保超能版",
                "type": InsuranceProductType.MEDICAL,
                "tags": ["少儿", "门诊", "感冒发烧", "报销"],
                "base_price": 660,
                "description": "专为孩子设计，不仅保住院，平时感冒发烧看门诊也能报销。含意外医疗和疾病门诊，宝妈首选。",
            },
            {
                "id": "prod_med_004",
                "name": "平安终身防癌医疗险",
                "type": InsuranceProductType.MEDICAL,
                "tags": ["老人", "防癌", "三高可买", "终身续保"],
                "base_price": 450,
                "description": "主要针对癌症医疗费用，终身保证续保。健康告知宽松，高血压、糖尿病人群也能购买。",
            },
            # 2. 重疾险补充
            {
                "id": "prod_crit_002",
                "name": "达尔文8号重疾险",
                "type": InsuranceProductType.CRITICAL,
                "tags": ["多次赔付", "性价比", "重疾", "癌症二次赔"],
                "base_price": 3200,
                "description": "重疾赔付后，非同组轻中症依然有效。可选癌症多次赔付，保障非常全面。",
            },
            {
                "id": "prod_crit_003",
                "name": "妈咪保贝星礼版",
                "type": InsuranceProductType.CRITICAL,
                "tags": ["少儿重疾", "白血病", "定期", "孩子"],
                "base_price": 600,
                "description": "少儿重疾险之王，针对白血病等少儿特疾双倍赔付。价格便宜，适合给孩子做定期保障。",
            },
            {
                "id": "prod_crit_004",
                "name": "康惠保旗舰版2.0",
                "type": InsuranceProductType.CRITICAL,
                "tags": ["前症保障", "重疾", "老牌", "基础保障"],
                "base_price": 2800,
                "description": "独有的前症保障（比轻症更轻的疾病也能赔）。保留了纯重疾投保选项，适合预算有限只想保大病的人。",
            },
            # 3. 意外险补充
            {
                "id": "prod_acc_002",
                "name": "小蜜蜂3号综合意外险",
                "type": InsuranceProductType.ACCIDENT,
                "tags": ["猝死保障", "交通意外", "高保额", "成人"],
                "base_price": 156,
                "description": "包含猝死保障，公共交通意外额外赔付。住院有津贴，适合经常出差的职场人士。",
            },
            {
                "id": "prod_acc_003",
                "name": "平安小顽童3号",
                "type": InsuranceProductType.ACCIDENT,
                "tags": ["少儿意外", "烧烫伤", "误食异物", "0免赔"],
                "base_price": 68,
                "description": "专为儿童设计，涵盖烧烫伤、误食异物等儿童高发意外。意外医疗0免赔，100%报销。",
            },
            {
                "id": "prod_acc_004",
                "name": "孝心安3号老年意外险",
                "type": InsuranceProductType.ACCIDENT,
                "tags": ["老人意外", "骨折", "摔倒", "救护车"],
                "base_price": 110,
                "description": "专为中老年人设计，最高85岁可投保。涵盖跌倒骨折、救护车费用，不仅保身故，更重医疗。",
            },
            {
                "id": "prod_acc_005",
                "name": "运动卫士高风险运动险",
                "type": InsuranceProductType.ACCIDENT,
                "tags": ["滑雪", "潜水", "短期", "高风险"],
                "base_price": 30,
                "description": "针对滑雪、潜水、攀岩等高风险运动的短期意外险。普通意外险通常不保这些项目。",
            },
        ]

    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """根据关键词搜索产品"""
        query = query.lower()
        results = []
        for p in self._products:
            if (
                query in p["name"].lower()
                or any(t in query for t in p["tags"])
                or query in p["description"]
            ):
                results.append(p)
        # 如果没有搜到，返回所有以供参考 (模拟模糊匹配机制)
        return results if results else self._products

    def recommend(self, budget_level: str, requirement: str) -> List[Dict[str, Any]]:
        """
        简单的推荐规则引擎
        budget_level: high (>2000), medium (500-2000), low (<500)
        """
        scored_products = []

        for p in self._products:
            score = 0
            # 价格匹配
            price = p["base_price"]
            if budget_level == "low" and price < 500:
                score += 2
            elif budget_level == "medium" and 500 <= price <= 2000:
                score += 2
            elif budget_level == "high" and price > 2000:
                score += 2

            # 需求匹配
            if "报销" in requirement or "医疗" in requirement:
                if p["type"] == InsuranceProductType.MEDICAL:
                    score += 3
            if "赔钱" in requirement or "重疾" in requirement or "大病" in requirement:
                if p["type"] == InsuranceProductType.CRITICAL:
                    score += 3
            if "意外" in requirement:
                if p["type"] == InsuranceProductType.ACCIDENT:
                    score += 3

            if score > 0:
                scored_products.append({"product": p, "score": score})

        # 按分数降序
        scored_products.sort(key=lambda x: x["score"], reverse=True)
        return [item["product"] for item in scored_products]

    def calculate_premium(
        self, product_name_keyword: str, age: int, gender: str
    ) -> Dict[str, Any]:
        """核保与保费计算"""
        # 1. 模糊匹配产品
        target = None
        for p in self._products:
            if product_name_keyword in p["name"]:
                target = p
                break

        if not target:
            return {"error": f"未找到包含 '{product_name_keyword}' 的产品"}


        # 2. 简单的费率逻辑
        ratio = 1.0
        if age > 50:
            ratio *= 1.5
        elif age > 30:
            ratio *= 1.2

        if gender == "男":
            ratio *= 1.1

        final_price = target["base_price"] * ratio

        return {
            "success": True,
            "product_name": target["name"],
            "input_age": age,
            "input_gender": gender,
            "final_price": round(final_price, 2),
            "policy_id": f"POL_{abs(hash(target['id'] + str(age))) % 1000000}",
        }
