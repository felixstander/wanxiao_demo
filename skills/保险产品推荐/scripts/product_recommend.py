import importlib.util
import sys
from pathlib import Path

from langchain_core.tools import tool
from pydantic import BaseModel, Field

def _load_insurance_database_module():
    skills_dir = Path(__file__).resolve().parents[2]
    module_path = skills_dir / "insurance_database.py"

    spec = importlib.util.spec_from_file_location("insurance_database", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load insurance_database from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


InsuranceDatabase = getattr(_load_insurance_database_module(), "InsuranceDatabase")

insurance_db = InsuranceDatabase()


class ProductRecommendationInput(BaseModel):
    budget_desc: str = Field(
        description="用户的预算描述，例如'几百块'、'不差钱'、'便宜点'"
    )
    user_requirement: str = Field(
        description="用户的核心需求，例如'看病报销'、'担心得癌症'、'意外防护'、'给孩子买'"
    )


def _recommend_products_text(budget_desc: str, user_requirement: str) -> str:
    # 简单的自然语言转枚举映射
    budget_level = "medium"
    if any(x in budget_desc for x in ["便宜", "少", "低", "百", "500"]):
        budget_level = "low"
    elif any(x in budget_desc for x in ["贵", "高", "万", "充足"]):
        budget_level = "high"

    recs = insurance_db.recommend(budget_level, user_requirement)

    if not recs:
        return "根据您的需求，暂时没有完美匹配的推荐，建议查看我们的全线产品。"

    top_list = recs[:2]  # 推荐前两个
    type_label_map = {
        "medical": "医疗险",
        "critical": "重疾险",
        "accident": "意外险",
    }
    response_text = (
        f"基于您 '{budget_desc}' 的预算和 '{user_requirement}' 的需求，我为您推荐：\n"
    )
    for idx, item in enumerate(top_list, start=1):
        product_type = item.get("type")
        type_value = getattr(product_type, "value", str(product_type))
        type_label = type_label_map.get(type_value, str(type_value))
        response_text += (
            f"\n{idx}. 【{item['name']}】\n   类型: {type_label}\n   理由: {item['description']}\n"
        )

    return response_text


@tool("insurance_product_recommend", args_schema=ProductRecommendationInput)
def recommend_product_tool(budget_desc: str, user_requirement: str) -> str:
    """
    [产品推荐 Skill]
    当用户表达了特定的预算偏好或保障需求，但不确定买哪个产品时使用。
    该工具会根据预算和需求筛选最优产品。
    """
    return _recommend_products_text(budget_desc, user_requirement)


def main():
    if len(sys.argv) < 3:
        print("Usage: python product_recommend.py <budget_desc> <user_requirement>")
        print("Example: python product_recommend.py 几百块 看病报销")
        sys.exit(1)

    budget_desc = sys.argv[1]
    user_requirement = " ".join(sys.argv[2:])
    print(f"正在调用推荐工具 (Budget: {budget_desc}, Req: {user_requirement})...\n")

    try:
        # CLI 快速测试：直接调用与工具一致的核心逻辑。
        print(_recommend_products_text(budget_desc, user_requirement))

    except Exception as e:
        print(f"工具调用出错: {e}")


if __name__ == "__main__":
    main()
