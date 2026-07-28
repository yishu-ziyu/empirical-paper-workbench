"""Methods (方法) chapter prompt template (T-07).

引导写"识别策略 + 计量模型 + 假设条件"。
"""
from __future__ import annotations

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【方法】章节。"
    "方法章节必须让读者明白本文如何用数据回答研究问题，核心是识别策略。"
    "必须包含以下三个部分，按顺序展开：\n"
    "1. 识别策略：开篇用一两段话交代本文的识别策略（OLS / IV / DID / RDD / "
    "PSM / FE 等），并说明该策略如何解决内生性问题或选择性偏误。\n"
    "2. 计量模型：给出主回归方程（用 LaTeX 行内公式 ` $...$ ` 标注），"
    "解释每个变量与系数的经济学含义，下标 i / t 的含义，误差项结构。\n"
    "3. 假设条件：列出识别策略成立的关键假设（外生性、平行趋势、SUTVA 等），"
    "并简要说明本文如何尽量满足或在稳健性部分检验这些假设。\n\n"
    "写作风格：中文学术写作；公式用 LaTeX；二级标题用 `## `；"
    "段落之间用空行分隔；不要写一级标题。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【方法】章节，约 800-1200 字。\n\n"
    "计量方法：{method}\n\n"
    "研究问题：{research_question}\n\n"
    "要求：按【识别策略 → 计量模型 → 假设条件】三段式展开，"
    "主回归方程用 LaTeX 行内公式标注；"
    "至少列出 2 条识别假设并说明检验思路。"
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: method, research_question.
    """
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**kwargs)
