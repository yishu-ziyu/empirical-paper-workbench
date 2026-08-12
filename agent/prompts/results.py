"""Results (结果) chapter prompt template (T-07).

引导写"基准回归 + 稳健性 + 异质性"。
"""
from __future__ import annotations

from prompts.revision import REVISION_BLOCK, fill_revision

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【结果】章节。"
    "结果章节是论文的核心实证展示，必须有条理地呈现基准、稳健性、异质性三层结果。"
    "必须包含以下三个部分，按顺序展开：\n"
    "1. 基准回归：报告主回归结果，给出系数符号、显著性、经济学含义。"
    "至少引用一张基准回归表（见表 2），逐列解读关键变量的系数变化。\n"
    "2. 稳健性：从子样本、替代变量、替代方法、控制变量增减等维度做稳健性检验，"
    "简要说明结果是否稳健。\n"
    "3. 异质性：按至少一个维度（性别 / 地区 / 时间 / 处理强度等）做异质性分析，"
    "讨论异质性背后的经济学机制。\n\n"
    "写作风格：中文学术写作；表引用用 `见表 N` 形式；"
    "二级标题用 `## `；段落之间用空行分隔；不要写一级标题。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【结果】章节，约 1000-1500 字。\n\n"
    "回归结果（StatsPAI 输出）：\n{results}\n\n"
    "计量方法：{method}\n\n"
    "要求：按【基准回归 → 稳健性 → 异质性】三段式展开，"
    "基准回归部分必须引用上面的回归结果并解读系数；"
    "异质性部分至少讨论 1 个维度。"
    + REVISION_BLOCK
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: results, method.
    Optional: low_dims, revision_suggestions.
    """
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**fill_revision(kwargs))
