#!/usr/bin/env python3
"""
CSV to Prompt Generator
读取CSV文件，将字段名和内容拼接为提示词
只使用Python基础库
"""

import argparse
import csv
import sys
from pathlib import Path


def read_csv_file(file_path):
    """读取CSV文件，返回(字段名列表, 数据行列表)"""
    rows = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 不存在", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"读取文件时出错：{e}", file=sys.stderr)
        sys.exit(1)

    if len(rows) == 0:
        print("错误：CSV文件为空", file=sys.stderr)
        sys.exit(1)

    return rows[0], rows[1:]


def generate_prompt(headers, row_data):
    """将字段名和单行数据拼接为提示词，测试集字段放最后"""
    normal_parts = []
    testcase_parts = []

    testcase_keywords = ["问题测试集"]

    for i, header in enumerate(headers):
        value = row_data[i] if i < len(row_data) else ""
        part = f"【{header}】\n{value}"

        if any(keyword in header for keyword in testcase_keywords):
            testcase_parts.append(part)
        else:
            normal_parts.append(part)

    return "\n\n".join(normal_parts + testcase_parts)


def generate_all_prompts(file_path):
    """生成所有数据行的提示词"""
    headers, data_rows = read_csv_file(file_path)

    prompts = []
    for i, row in enumerate(data_rows):
        prompt = generate_prompt(headers, row)
        prompts.append(f"=== 第 {i + 1} 条记录 ===\n{prompt}")

    result = "\n\n" + "=" * 50 + "\n\n".join(prompts)
    print(result)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="读取CSV文件，将字段名和内容拼接为提示词",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        示例：
        python3 csv_to_prompt.py data
        """,
    )

    parser.add_argument("file", help="CSV文件名（会自动拼接为 ../data/{文件名}）")

    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    file_path = script_dir.parent / "data" / f"{args.file}.csv"

    generate_all_prompts(str(file_path))


if __name__ == "__main__":
    main()
