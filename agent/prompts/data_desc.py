"""Data description (数据描述) chapter prompt template (T-07).

引导写"数据来源 + 变量定义 + 描述统计表引用"。
"""
from __future__ import annotations

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【数据描述】章节。"
    "数据描述章节是读者复现本文结果的关键，必须清晰交代数据来源、变量构造、"
    "描述统计。必须包含以下三个部分，按顺序展开：\n"
    "1. 数据来源：交代数据集名称、调查机构、调查频率、覆盖时段、抽样设计、"
    "样本规模。若有清洗 / 筛选步骤，简要说明保留与剔除样本的标准与最终样本量。\n"
    "2. 变量定义：列出本文使用的因变量、自变量、控制变量。每个变量给出"
    "经济学含义、测量方式、单位。若变量由多个原始变量构造，说明构造逻辑。\n"
    "3. 描述统计表引用：引用 EDA 阶段产出的描述统计表（均值 / 标准差 / "
    "最小值 / 最大值 / 缺失数），指出关键变量的分布特征与潜在异常。\n\n"
    "写作风格：中文学术写作；变量名用等宽字体 `code` 标注；"
    "描述统计表引用用 `见表 1` 形式；二级标题用 `## `；不要写一级标题。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【数据描述】章节，约 800-1200 字。\n\n"
    "数据概述：{data_summary}\n\n"
    "EDA 结果（描述统计）：\n{eda_results}\n\n"
    "要求：按【数据来源 → 变量定义 → 描述统计表引用】三段式展开，"
    "变量定义部分至少列出因变量、自变量与 2 个控制变量；"
    "描述统计部分必须引用上面的 EDA 结果。"
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: data_summary, eda_results.
    """
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**kwargs)
