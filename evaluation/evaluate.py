"""UniPhysics Tutor 评估脚本

对测试集中的每个问题调用后端 API，然后按多个维度评估回答质量。

用法：
    python evaluate.py

    # 自定义 API 地址
    python evaluate.py --api http://localhost:8000

    # 只测试特定 case
    python evaluate.py --case t01_concept_gauss
"""

import json
import os
import sys
import time
import argparse
from typing import Optional

import requests


def load_test_cases(path: str = "test_cases.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def call_api(api_base: str, endpoint: str, payload: dict) -> dict:
    """调用后端 API"""
    url = f"{api_base}{endpoint}"
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def evaluate_answer(
    answer: str,
    expected_elements: list[str],
    must_not_contain: list[str],
    question: str,
) -> dict:
    """评估一个回答的质量

    Returns:
        {
            "score": 0-100,
            "details": {...},
            "issues": [...]
        }
    """
    score = 100
    details = {}
    issues = []

    # 1. 检查必要元素
    for elem in expected_elements:
        # 模糊匹配（忽略大小写和空格）
        found = elem.lower() in answer.lower()
        details[f"contains:{elem}"] = found
        if not found:
            score -= 100 // (len(expected_elements) + len(must_not_contain) + 1)
            issues.append(f"缺少关键内容: '{elem}'")

    # 2. 检查禁止内容
    for forbidden in must_not_contain:
        found = forbidden.lower() in answer.lower()
        details[f"forbidden:{forbidden}"] = not found
        if found:
            score -= 20
            issues.append(f"包含错误内容: '{forbidden}'")

    # 3. 是否说明了适用条件
    conditions_keywords = ["条件", "前提", "假设", "只在", "仅在", "限于", "当"]
    has_conditions = any(kw in answer for kw in conditions_keywords)
    details["has_conditions"] = has_conditions
    if not has_conditions:
        score -= 5
        issues.append("建议补充适用条件说明")

    # 4. 是否有单位检查（对解题模式）
    unit_keywords = ["单位", "量纲", "m/s", "N", "J", "kg"]
    has_unit_check = any(kw in answer for kw in unit_keywords)
    details["has_unit_reference"] = has_unit_check

    # 5. 是否适合本科生
    undergrad_indicators = ["理解", "注意", "常见", "误区", "混淆", "例如", "简单"]
    undergrad_score = sum(1 for kw in undergrad_indicators if kw in answer)
    details["undergraduate_friendly"] = undergrad_score >= 1
    if undergrad_score < 1:
        score -= 5
        issues.append("回答可能不够通俗，建议增加对本科生的教学性语言")

    return {
        "score": max(0, score),
        "details": details,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="UniPhysics Tutor 评估")
    parser.add_argument("--api", default="http://localhost:8000", help="后端 API 地址")
    parser.add_argument("--case", default=None, help="只测试特定 case ID")
    parser.add_argument("--output", default="evaluation_report.json", help="输出报告路径")
    args = parser.parse_args()

    # 加载测试用例
    test_file = os.path.join(os.path.dirname(__file__), "test_cases.json")
    data = load_test_cases(test_file)

    print(f"UniPhysics Tutor 评估")
    print(f"{'=' * 60}")
    print(f"API: {args.api}")
    print(f"测试用例: {len(data['test_cases'])} 个")
    print(f"评估维度: {', '.join(data['dimensions'])}")
    print()

    # 检查 API 健康状态
    try:
        health = requests.get(f"{args.api}/api/health", timeout=10).json()
        print(f"后端状态: {health.get('status')} | LLM: {health.get('llm_configured')} | KB: {health.get('knowledge_base_loaded')}")
    except Exception as e:
        print(f"❌ 无法连接到后端: {e}")
        print("请确保后端已启动: cd backend && uvicorn main:app --reload --port 8000")
        return

    print(f"\n{'=' * 60}")
    print("开始测试...\n")

    results = []
    total_score = 0
    passed = 0
    failed = 0

    for tc in data["test_cases"]:
        if args.case and tc["id"] != args.case:
            continue

        print(f"[{tc['id']}] {tc.get('question', tc.get('student_answer', ''))[:60]}...")

        try:
            # 根据 mode 选择 API
            if tc.get("mode") == "diagnose":
                payload = {
                    "student_answer": tc.get("student_answer", ""),
                    "question_context": tc.get("question_context"),
                    "course": tc.get("course"),
                }
                resp = call_api(args.api, "/api/diagnose", payload)
                answer_text = json.dumps(resp, ensure_ascii=False)
            else:
                payload = {
                    "message": tc.get("question", tc.get("student_answer", "")),
                    "mode": tc.get("mode", "explain"),
                    "course": tc.get("course"),
                }
                resp = call_api(args.api, "/api/chat", payload)
                answer_text = resp.get("answer", "")

            # 评估
            eval_result = evaluate_answer(
                answer_text,
                tc.get("expected_elements", []),
                tc.get("must_not_contain", []),
                tc.get("question", ""),
            )

            status = "✅" if eval_result["score"] >= 70 else "⚠️" if eval_result["score"] >= 50 else "❌"
            print(f"  {status} 得分: {eval_result['score']}/100")
            for issue in eval_result["issues"]:
                print(f"     → {issue}")

            total_score += eval_result["score"]
            if eval_result["score"] >= 70:
                passed += 1
            else:
                failed += 1

            results.append({
                "id": tc["id"],
                **eval_result,
            })

        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            results.append({
                "id": tc["id"],
                "error": str(e),
                "score": 0,
            })
            failed += 1

        time.sleep(0.5)  # 避免请求过快

    # 汇总
    n = len(results)
    print(f"\n{'=' * 60}")
    print(f"评估完成")
    print(f"总数: {n} | 通过(≥70): {passed} | 未通过: {failed}")
    if n > 0:
        print(f"平均分: {total_score / n:.1f}/100")

    # 保存报告
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total": n,
                "passed": passed,
                "failed": failed,
                "average_score": total_score / n if n > 0 else 0,
            },
            "dimensions": data["dimensions"],
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n详细报告已保存至: {args.output}")


if __name__ == "__main__":
    main()
