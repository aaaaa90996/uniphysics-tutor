"""提示词加载器 — 从 prompts/ 目录加载模板"""

import os
from config import settings


# 缓存已加载的提示词
_cache: dict[str, str] = {}


def _load_md(filepath: str) -> str:
    """读取 Markdown 提示词文件"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_system_prompt() -> str:
    """加载系统提示词"""
    if "system" not in _cache:
        _cache["system"] = _load_md(
            os.path.join(settings.PROMPTS_PATH, "system_prompt.md")
        )
    return _cache["system"]


def get_solver_prompt() -> str:
    """加载解题提示词"""
    if "solver" not in _cache:
        _cache["solver"] = _load_md(
            os.path.join(settings.PROMPTS_PATH, "solver_prompt.md")
        )
    return _cache["solver"]


def get_diagnose_prompt() -> str:
    """加载诊断提示词"""
    if "diagnose" not in _cache:
        _cache["diagnose"] = _load_md(
            os.path.join(settings.PROMPTS_PATH, "diagnose_prompt.md")
        )
    return _cache["diagnose"]


def get_exercise_prompt() -> str:
    """加载出题提示词"""
    if "exercise" not in _cache:
        _cache["exercise"] = _load_md(
            os.path.join(settings.PROMPTS_PATH, "exercise_prompt.md")
        )
    return _cache["exercise"]


def get_rewrite_prompt() -> str:
    """加载根据 warnings 修正答案的提示词"""
    if "rewrite" not in _cache:
        _cache["rewrite"] = _load_md(
            os.path.join(settings.PROMPTS_PATH, "rewrite_with_warnings_prompt.md")
        )
    return _cache["rewrite"]


def reload_all():
    """重新加载所有提示词（热更新）"""
    _cache.clear()
