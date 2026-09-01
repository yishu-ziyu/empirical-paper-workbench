"""Data description (数据描述) chapter prompt template (T-07).

引导写"数据来源 + 变量定义 + 描述统计表引用"。
"""
from __future__ import annotations

from .revision import REVISION_BLOCK, fill_revision

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【数据描述】章节。"
    "数据描述章节是读者复现本文结果的关键，必须清晰交代数据来源、变量构造、"
    "描述统计。必须包含以下三个部分，按顺序展开：\n"
    "1. 数据来源：只能描述用户提示中已提供的数据集名称、调查机构、覆盖时段、"
    "抽样设计、样本规模与清洗信息。缺失项必须原样写为“未提供”，禁止编造机构、"
    "采样框、调查年份或数据集背景。\n"
    "2. 变量定义：只列出用户提示中已明确的因变量、自变量、控制变量、"
    "经济学含义、测量方式、单位和构造逻辑；未提供时不得根据列名猜测。\n"
    "3. 描述统计表引用：引用 EDA 阶段产出的描述统计表（均值 / 标准差 / "
    "最小值 / 最大值 / 缺失数），指出关键变量的分布特征与潜在异常。\n\n"
    "写作风格：中文学术写作；变量名用等宽字体 `code` 标注；"
    "描述统计表引用用 `见表 1` 形式；二级标题用 `## `；不要写一级标题。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【数据描述】章节，约 800-1200 字。\n\n"
    "数据来源事实（未提供就是当前边界）：\n{data_provenance}\n\n"
    "已明确的变量角色：\n{variable_roles}\n\n"
    "数据概述：{data_summary}\n\n"
    "EDA 结果（描述统计）：\n{eda_results}\n\n"
    "要求：按【数据来源 → 变量定义 → 描述统计表引用】三段式展开；"
    "只能按上面的明确角色与 EDA 事实撰写，不得推断额外变量角色、单位或构造方式；"
    "没有 EDA 结果时写“未提供”，不得生成描述统计数字。"
    + REVISION_BLOCK
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: data_summary, eda_results.
    Optional: low_dims, revision_suggestions.
    """
    filled = fill_revision(kwargs)
    filled.setdefault("data_provenance", "未提供")
    filled.setdefault(
        "variable_roles", "因变量：未提供\n自变量：未提供\n控制变量：未提供"
    )
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**filled)
