"""Prompt templates for econpaper agent nodes.

T-07: 6 章节模板（intro / lit_review / data_desc / methods / results /
conclusion）。每个模板模块暴露：

- ``SYSTEM_PROMPT``: 章节特化的写作指引（str）
- ``USER_TEMPLATE``: 含 ``{var}`` 占位符的 user prompt 模板（str）
- ``render(**kwargs) -> (system, user)``: 渲染并返回 (system, user) tuple

``get_prompt(chapter_type)`` 按 chapter_type 路由到对应模板模块。
"""
from __future__ import annotations

import importlib
from types import ModuleType
from typing import Mapping

# chapter_type → 模板模块名（同 package 下）
_CHAPTER_TYPE_TO_MODULE: Mapping[str, str] = {
    "intro": "intro",
    "lit_review": "lit_review",
    "data_desc": "data_desc",
    "methods": "methods",
    "results": "results",
    "conclusion": "conclusion",
}


def get_prompt(chapter_type: str) -> ModuleType:
    """按 chapter_type 返回对应模板模块。

    模块暴露 ``SYSTEM_PROMPT`` / ``USER_TEMPLATE`` / ``render``。
    未知 chapter_type 抛 ``ValueError``（不 silent fallback，防止 bug 被掩盖）。
    """
    if chapter_type not in _CHAPTER_TYPE_TO_MODULE:
        raise ValueError(
            f"Unknown chapter_type: {chapter_type!r}. "
            f"Valid types: {sorted(_CHAPTER_TYPE_TO_MODULE)}"
        )
    # 同 package（agent.prompts）下相对导入；用 importlib 确保 chapter_type 来自
    # 用户输入时安全。基于 __package__ 构造，无需进程级 sys.path 拼接。
    return importlib.import_module(f".{_CHAPTER_TYPE_TO_MODULE[chapter_type]}", __package__)


__all__ = ["get_prompt"]
