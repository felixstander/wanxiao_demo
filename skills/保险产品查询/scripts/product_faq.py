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


class ProductQAInput(BaseModel):
    query: str = Field(
        description="用户关于保险产品的具体问题或关键词，例如'有什么医疗险'或'尊享e生保什么'"
    )


def _search_products_text(query: str) -> str:
    products = insurance_db.search_products(query)

    if not products:
        return "未找到相关产品信息。"

    response = "找到以下相关产品资料：\n"
    for p in products:
        response += f"- 【{p['name']}】: {p['description']} (标签: {', '.join(p['tags'])})\n"
    return response


@tool("insurance_product_search", args_schema=ProductQAInput)
def product_faq_tool(query: str) -> str:
    """
    [产品答疑 Skill]
    用于回答用户关于保险产品特性、保障范围的咨询。
    不要用于推荐，只用于检索信息。
    """
    return _search_products_text(query)


# ----------------------------------------------------------------
# 2. 第二部分：主程序 (修改后的运行逻辑)
# ----------------------------------------------------------------


def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("Usage: python product_faq.py <query>")
        print("Example: python product_faq.py '有什么医疗险'")
        sys.exit(1)

    user_query = " ".join(sys.argv[1:])

    print(f"正在使用工具检索: {user_query} ...\n")

    try:
        print(_search_products_text(user_query))

    except Exception as e:
        print(f"工具调用出错: {e}")


if __name__ == "__main__":
    main()
