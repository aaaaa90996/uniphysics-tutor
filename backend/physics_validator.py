"""物理答案校验器

对大模型输出进行规则化检查，发现问题后返回 warnings，
可让模型根据 warnings 修订答案。
"""

import re
from typing import Optional


def validate_physics_answer(
    answer: str,
    question: Optional[str] = None,
    mode: str = "explain",
) -> list[str]:
    """校验物理回答，返回警告列表

    Args:
        answer: 模型生成的回答
        question: 原始问题（可选，用于上下文判断）
        mode: 模式（explain/solve/diagnose）

    Returns:
        警告信息列表，空列表表示通过
    """
    warnings: list[str] = []

    # 合并问题与回答用于判断上下文
    full_text = f"{question or ''} {answer}"

    # ── 规则 1：牛顿第二定律 → 需说明惯性系 ──────────────
    if _mentions_newton_second_law(full_text) and not _mentions_inertial_frame(answer):
        warnings.append(
            "【牛顿第二定律】使用 F=ma 时应说明参考系为惯性系。"
            "请在回答中补充「本定律仅在惯性参考系中成立」的说明。"
        )

    # ── 规则 2：动量守恒 → 需说明合外力为零 ──────────────
    if _mentions_momentum_conservation(full_text) and not _mentions_zero_net_force(answer):
        warnings.append(
            "【动量守恒】使用动量守恒定律时应说明系统所受合外力为零或可忽略。"
            "请在回答中补充守恒条件。"
        )

    # ── 规则 3：机械能守恒 → 需说明非保守力做功为零 ──────
    if _mentions_mechanical_energy_conservation(full_text) and not _mentions_conservative_only(answer):
        warnings.append(
            "【机械能守恒】使用机械能守恒时应说明只有保守力做功，或非保守力做功为零。"
            "请在回答中补充「系统内只有保守力做功」的条件说明。"
        )

    # ── 规则 4：高斯定理求电场 → 需说明对称性 ────────────
    if _mentions_gauss_for_field(full_text) and not _mentions_symmetry(answer):
        warnings.append(
            "【高斯定理求电场】使用高斯定理直接求电场时，需要电荷分布具有足够高的对称性"
            "（球对称、圆柱对称、或平面对称），否则无法将 E 提出积分号。"
            "请在回答中说明对称性条件。"
        )

    # ── 规则 5：电磁感应 → 需说明磁通量变化和方向 ────────
    if _mentions_induction(full_text) and not _mentions_flux_change(answer):
        warnings.append(
            "【电磁感应】涉及电磁感应时，应明确说明磁通量如何变化"
            "以及感应电动势/电流方向的判断（楞次定律或右手定则）。"
        )

    # ── 规则 6：矢量运算 → 需说明方向和坐标系 ────────────
    if _mentions_vector_quantity(full_text) and not _mentions_direction_or_coordinate(answer):
        warnings.append(
            "【矢量方向】回答中涉及矢量（力、速度、加速度、电场、磁场等），"
            "请说明方向或选用的坐标系。"
        )

    # ── 规则 7：积分运算 → 需说明积分区域和边界条件 ──────
    if _mentions_integral(answer) and not _mentions_boundary(answer):
        warnings.append(
            "【积分边界】回答中包含积分表达式时，请说明积分区域和边界条件。"
        )

    # ── 规则 8：电势与电场混淆检查 ────────────────────────
    if _mentions_potential_zero_implies_field_zero(full_text):
        warnings.append(
            "【电势与电场】电势为零处电场不一定为零。"
            "电场是电势的负梯度 E = -∇V，某点 V=0 不代表其梯度为零。"
            "请检查并修正相关表述。"
        )

    # ── 规则 9：量纲/单位检查 ─────────────────────────────
    dim_warnings = _check_dimensional_issues(answer)
    warnings.extend(dim_warnings)

    # ── 规则 10：缺少适用条件 ─────────────────────────────
    if mode == "explain" and _has_formula_without_conditions(answer):
        warnings.append(
            "【适用条件缺失】回答中包含公式但未说明适用条件。"
            "请补充公式在什么条件下成立。"
        )

    return warnings


# ── 规则检测辅助函数 ─────────────────────────────────────

def _mentions_newton_second_law(text: str) -> bool:
    patterns = [
        r"牛顿第二定律", r"F\s*=\s*m\s*a", r"F=ma",
        r"运动方程.*m\s*\\frac", r"Newton.*second",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_inertial_frame(text: str) -> bool:
    patterns = [r"惯性系", r"惯性参考系", r"inertial frame"]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_momentum_conservation(text: str) -> bool:
    patterns = [
        r"动量守恒", r"momentum.*conserv", r"总动量.*不变",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_zero_net_force(text: str) -> bool:
    patterns = [
        r"合外力.*(?:为零|零|0)", r"外力.*(?:忽略|不计|为零)",
        r"不受外力", r"孤立系统", r"net.*force.*zero",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_mechanical_energy_conservation(text: str) -> bool:
    patterns = [
        r"机械能守恒", r"mechanical energy.*conserv",
        r"动能.*势能.*不变", r"动能.*势能.*常量",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_conservative_only(text: str) -> bool:
    patterns = [
        r"保守力", r"非保守力.*(?:不做功|为零|为0|忽略)",
        r"只有.*重力.*做功", r"只有.*弹力.*做功",
        r"conservative force", r"non-conservative.*zero",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_gauss_for_field(text: str) -> bool:
    """检测是否用高斯定理求电场（而不仅仅是提及高斯定理）"""
    has_gauss = bool(re.search(r"高斯定理", text))
    has_field_calc = bool(re.search(
        r"(?:求|计算|求出|得到).*电场|电场.*(?:求|计算|求出|得到)",
        text
    ))
    has_symmetry_use = bool(re.search(
        r"(?:球对称|圆柱对称|平面对称|对称分布).*高斯|高斯.*(?:球对称|圆柱对称|平面对称|对称分布)",
        text
    ))
    return has_gauss and (has_field_calc or has_symmetry_use)


def _mentions_symmetry(text: str) -> bool:
    patterns = [
        r"对称", r"symmetry", r"球对称", r"圆柱对称",
        r"平面对称", r"均匀.*球", r"无限长.*圆柱", r"无限大.*平面",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_induction(text: str) -> bool:
    patterns = [
        r"电磁感应", r"感应电动势", r"法拉第", r"Faraday",
        r"楞次", r"Lenz", r"磁通量.*变化", r"变化.*磁通量",
        r"induced.*(?:emf|current|electromotive)",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_flux_change(text: str) -> bool:
    patterns = [
        r"磁通量.*(?:变化|改变|增加|减少)", r"(?:变化|改变|增加|减少).*磁通量",
        r"d\\Phi", r"\\frac.*d.*\\Phi", r"-d\\Phi",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_vector_quantity(text: str) -> bool:
    """检测是否涉及矢量物理量"""
    patterns = [
        r"\\vec|\\mathbf",                  # LaTeX 矢量记号
        r"(?:力|速度|加速度|电场|磁场|位移|动量|角动量)(?!.*(?:大小|数值|标量))",
        r"矢量", r"vector",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_direction_or_coordinate(text: str) -> bool:
    patterns = [
        r"方向", r"坐标", r"x\s*轴", r"y\s*轴", r"z\s*轴",
        r"沿.*方向", r"垂直", r"平行", r"径向", r"切向",
        r"direction", r"coordinate", r"\^[ijkxyz]",
        r"\\hat", r"\\mathbf\{[ijk]\}",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_integral(text: str) -> bool:
    patterns = [r"\\int", r"\\oint", r"积分", r"integral"]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_boundary(text: str) -> bool:
    patterns = [
        r"积分.*(?:限|区间|区域|路径|曲面|边界)",
        r"(?:限|区间|区域|路径|曲面|边界).*积分",
        r"从.*到", r"boundary", r"0\s*(?:到|→|to)\s*",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _mentions_potential_zero_implies_field_zero(text: str) -> bool:
    patterns = [
        r"电势.*(?:为零|为0|是零).*电场.*(?:也为零|也为0|是零|一定为零)",
        r"电势为零.*电场为零",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _has_formula_without_conditions(text: str) -> bool:
    """检查是否给出公式但未说明适用条件"""
    has_formula = bool(re.search(
        r"(?:F\s*=\s*m\s*a|E\s*=\s*\\frac|B\s*=\s*\\frac|"
        r"\\Phi\s*=\s*|\\oint|\\sum|守恒|conservation)",
        text
    ))
    has_conditions = bool(re.search(
        r"(?:适用条件|成立条件|条件|前提|假设|要求|只在|仅在|限于|"
        r"当.*时|如果.*则|在.*情况下)",
        text
    ))
    return has_formula and not has_conditions


def _check_dimensional_issues(text: str) -> list[str]:
    """简单量纲检查"""
    warnings = []
    # 检查是否有常见量纲混淆
    if re.search(r"能量.*kg.*m/s", text):
        warnings.append("【量纲错误】能量单位应为 kg·m²/s² (焦耳)，非 kg·m/s。")
    if re.search(r"力.*kg.*m\^2/s", text):
        warnings.append("【量纲错误】力单位应为 kg·m/s² (牛顿)，非 kg·m²/s。")
    return warnings


# ── 结合 LLM 的校验-修订循环 ─────────────────────────────

def validate_and_rewrite(
    answer: str,
    question: str,
    mode: str,
    llm_client,
    prompt_loader,
    max_retries: int = 2,
) -> tuple[str, list[str]]:
    """校验答案，如有警告则让 LLM 修订

    Returns:
        (final_answer, all_warnings)
    """
    all_warnings: list[str] = []
    current_answer = answer

    for attempt in range(max_retries):
        warnings = validate_physics_answer(current_answer, question, mode)
        if not warnings:
            break

        all_warnings.extend(warnings)

        # 让模型根据警告修订
        rewrite_prompt = prompt_loader.get_rewrite_prompt()
        full_prompt = f"""{rewrite_prompt}

## 原始问题
{question}

## 原始回答
{current_answer}

## 需要修正的问题
{chr(10).join(f'- {w}' for w in warnings)}

请根据以上警告修订回答，确保修正所有指出的问题。直接输出修订后的完整回答。"""

        try:
            current_answer = llm_client.chat(full_prompt, system_prompt="")
        except Exception as e:
            print(f"[Validator] LLM rewrite failed: {e}")
            break

    return current_answer, all_warnings
