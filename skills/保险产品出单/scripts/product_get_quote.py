import importlib.util
import json
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


class InsuranceQuoteInput(BaseModel):
    product_keyword: str = Field(description="用户想购买的产品名称关键词")
    age: int = Field(description="投保人年龄")
    gender: str = Field(description="投保人性别，'男'或'女'")


@tool("insurance_get_quote", args_schema=InsuranceQuoteInput)
def insurance_issuance_tool(product_keyword: str, age: int, gender: str) -> str:
    """
    [保险出单 Skill]
    仅在用户明确决定购买某个具体产品，并且已经提供了年龄和性别后调用。
    用于计算最终保费并生成投保链接。
    """
    result = insurance_db.calculate_premium(product_keyword, age, gender)

    if "error" in result:
        return f"出单失败: {result['error']}"

    return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    # 参数检查
    if len(sys.argv) < 4:
        print("Usage: python product_get_quote.py <product_keyword> <age> <gender>")
        print("Example: python product_get_quote.py 医疗 30 男")
        sys.exit(1)

    keyword = sys.argv[1]
    try:
        age = int(sys.argv[2])
    except ValueError:
        print("Error: Age must be an integer")
        sys.exit(1)

    gender = sys.argv[3]

    if gender not in ("男", "女"):
        print("Error: gender must be '男' or '女'")
        sys.exit(1)

    print(
        f"正在调用保费计算工具 (Product: {keyword}, Age: {age}, Gender: {gender})...\n"
    )

    try:
        result = insurance_db.calculate_premium(keyword, age, gender)

        if "error" in result:
            print(f"出单失败: {result['error']}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"工具调用出错: {e}")


if __name__ == "__main__":
    main()
