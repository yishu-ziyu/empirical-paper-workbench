"""Intro (引言) chapter prompt template (T-07).

课程论文：研究背景 + 研究问题 + 论文结构。不要写贡献。
"""
from __future__ import annotations

import re

from prompts.revision import REVISION_BLOCK, fill_revision

_CONTRIB_SECTION = re.compile(
    r"(?:^|\n)##[ \t]*贡献[^\n]*\n(?:.*?)(?=\n## |\Z)",
    re.S,
)


def strip_contribution(content: str) -> str:
    """课设引言若仍写出「## 贡献」，整段拿掉。"""
    text = _CONTRIB_SECTION.sub("\n", content or "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()

SYSTEM_PROMPT = (
    "你在写一篇本科课程论文的【引言】，不是期刊投稿。"
    "只要三段，按顺序写：\n"
    "1. 研究背景：这个题目为什么值得看，用日常能懂的话说清，约 150-250 字。"
    "不要堆政策口号，不要仿核心刊开篇。\n"
    "2. 研究问题：用一两句话写清本文要回答什么，用的是哪份数据、哪个方法。"
    "相关分析就写相关，不要写成文献缺口或识别策略。\n"
    "3. 论文结构：用一小段说明后面几章各写什么。\n\n"
    "禁止：不要写「贡献」「边际贡献」「本文的贡献有三」「政策含义」；"
    "不要用 ## 贡献 这种标题；不要列数据/方法/识别三条增量。\n"
    "写作：中文课设口吻，清楚即可；二级标题用 `## `；不要写一级标题；"
    "段落之间空一行。"
)

USER_TEMPLATE = (
    "请为以下课程论文撰写【引言】章节，约 500-800 字。\n\n"
    "研究问题：{research_question}\n\n"
    "数据概述：{data_summary}\n\n"
    "要求：按【研究背景 → 研究问题 → 论文结构】三段写。"
    "不要写贡献。不要写占位符。"
    + REVISION_BLOCK
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: research_question, data_summary.
    Optional: low_dims, revision_suggestions.
    """
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**fill_revision(kwargs))
