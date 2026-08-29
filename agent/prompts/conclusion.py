"""Conclusion (结论) chapter prompt template (T-07).

引导写"主要发现 + 政策含义 + 局限与未来"。
"""
from __future__ import annotations

from .revision import REVISION_BLOCK, fill_revision

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【结论】章节。"
    "结论章节不是结果的简单重复，而是把发现拔高到政策与学术意义层面。"
    "必须包含以下三个部分，按顺序展开：\n"
    "1. 主要发现：用 3-4 条要点总结本文的核心实证结果（不只是系数符号，"
    "而是经济学结论），与引言中的研究问题一一对应。\n"
    "2. 政策含义：基于发现提出 2-3 条政策建议，要具体、可执行，"
    "对应到现实的政策杠杆（补贴 / 监管 / 信息披露等）。\n"
    "3. 局限与未来：诚实承认本文的 2-3 条局限（数据 / 方法 / 外推性），"
    "并指出未来研究可以如何拓展。\n\n"
    "写作风格：中文学术写作；二级标题用 `## `；段落之间用空行分隔；"
    "不要写一级标题；不要重复结果章节的具体数字。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【结论】章节，约 600-1000 字。\n\n"
    "主要结果：\n{results}\n\n"
    "研究问题：{research_question}\n\n"
    "要求：按【主要发现 → 政策含义 → 局限与未来】三段式展开，"
    "主要发现用要点列出；政策建议要具体可执行；"
    "局限至少列出 2 条。"
    + REVISION_BLOCK
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: results, research_question.
    Optional: low_dims, revision_suggestions.
    """
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**fill_revision(kwargs))
