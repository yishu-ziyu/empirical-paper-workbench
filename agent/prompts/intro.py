"""Intro (引言) chapter prompt template (T-07).

引导写"研究背景 + 研究问题 + 贡献 + 论文结构"。
"""
from __future__ import annotations

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【引言】章节。"
    "引言是整篇论文的导引，必须包含以下四个部分，且按顺序展开：\n"
    "1. 研究背景：交代议题的现实重要性与学术脉络（政策语境、 stylized facts、"
    "已有研究的总体走向），约 200-300 字。\n"
    "2. 研究问题：用一两句话清晰陈述本文要回答的核心问题（可识别、可检验），"
    "并指出该问题在此前文献中未被充分回答。\n"
    "3. 贡献：列出本文相对现有研究的 2-3 条边际贡献（数据 / 方法 / 识别 / "
    "机制），用要点列出。\n"
    "4. 论文结构：用一段话简述后续章节安排（第二部分文献综述、第三部分数据描述、"
    "第四部分方法、第五部分结果、第六部分结论）。\n\n"
    "写作风格：中文学术写作；避免口语化；不要使用 emoji；段落之间用空行分隔；"
    "二级标题用 `## `；不要写一级标题（系统会加）。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【引言】章节，约 800-1200 字。\n\n"
    "研究问题：{research_question}\n\n"
    "数据概述：{data_summary}\n\n"
    "要求：按【研究背景 → 研究问题 → 贡献 → 论文结构】四段式展开，"
    "每段都要写实质内容，不要写占位符。"
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: research_question, data_summary.
    """
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**kwargs)
