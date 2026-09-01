"""Conclusion (结论) chapter prompt template (T-07).

引导写"主要发现 + 政策含义 + 局限与未来"。
"""
from __future__ import annotations

from .revision import REVISION_BLOCK, fill_revision

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【结论】章节。"
    "结论章节不是结果的简单重复，也不得把发现扩展到证据之外。"
    "当方法为 OLS 或主张类型为 association 时，禁止因果表述。"
    "必须包含以下三个部分，按顺序展开：\n"
    "1. 主要发现：只总结已绑定的核心实证结果，最多 3-4 条（不只是系数符号，"
    "而是经济学结论），与引言中的研究问题一一对应。\n"
    "2. 现实含义：只能在已提供的政策证据和主张边界内讨论。没有政策证据时，"
    "不得声称政策效果或给出强政策建议，只能说明当前结果的适用边界。\n"
    "3. 局限与未来：诚实承认本文的 2-3 条局限（数据 / 方法 / 外推性），"
    "并指出未来研究可以如何拓展。\n\n"
    "写作风格：中文学术写作；二级标题用 `## `；段落之间用空行分隔；"
    "不要写一级标题；不要重复结果章节的具体数字。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【结论】章节，约 600-1000 字。\n\n"
    "主要结果：\n{results}\n\n"
    "已绑定估计事实：\n{estimate_facts}\n\n"
    "稳健性状态：{robustness_status}\n\n"
    "异质性证据：{heterogeneity_evidence}\n\n"
    "政策证据：{policy_evidence}\n\n"
    "研究问题：{research_question}\n\n"
    "要求：按【主要发现 → 政策含义 → 局限与未来】三段式展开，"
    "主要发现用要点列出；稳健性未运行、降级或证据不足时，不得宣称稳健；"
    "异质性证据是未运行/未提供时，不得生成地区、行业、性别差异或数字；"
    "政策证据为未提供时，不得声称政策效果，不得给出强政策建议，"
    "只能说明当前结果的适用边界；"
    "主张类型为 association 或计量方法为 OLS 时，禁止因果表述；"
    "局限至少列出 2 条。"
    + REVISION_BLOCK
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: results, research_question.
    Optional: low_dims, revision_suggestions.
    """
    filled = fill_revision(kwargs)
    filled.setdefault("estimate_facts", "未提供")
    filled.setdefault("robustness_status", "未运行")
    filled.setdefault("heterogeneity_evidence", "未运行/未提供")
    filled.setdefault("policy_evidence", "未提供")
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**filled)
