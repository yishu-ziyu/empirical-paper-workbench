"""Review-chapter LLM prompt templates.

Extracted verbatim from ``nodes/review_chapter.py`` so the node only keeps
orchestration and degradation logic. The rendered prompt text is byte-for-byte
identical to what the node produced before extraction.
"""
from __future__ import annotations

# 审稿人系统提示（只输出 JSON rubric + feedback + suggestions）的静态前缀。
REVIEW_PROMPT_PREFIX = (
    "你是经济学论文审稿人。只输出 JSON，不要 markdown。"
    "字段：rubric{endogeneity,identification,robustness,contribution,readability}"
    "（每维 0 到 1）、feedback、suggestions。\n"
)

# 课设深度校准：评审不得按核心刊标准扣 contribution。
COURSE_BLOCK = (
    "这是本科课程论文，不是期刊投稿。"
    "不得因为没有边际贡献、三条贡献、政策贡献或学术增量而扣 contribution。"
    "contribution 只看题目有没有写清楚、有没有按课设作答。"
)

# association 主张：不要求 IV/RDD/DID，只查是否把相关写成因果。
ASSOCIATION_CLAIM_INSTRUCTION = (
    COURSE_BLOCK
    + "本文主张模式是 association（条件相关，不是因果识别）。"
    "不得因为没有 IV、RDD、DID、工具变量或识别策略而扣 "
    "identification / endogeneity / contribution。"
    "这些方法不是本篇的要求。"
    "只检查：有没有把相关写成因果；论述是否清楚。"
)

# 因果主张：按课设深度看识别策略，不要按核心刊标准。
CAUSAL_CLAIM_INSTRUCTION = COURSE_BLOCK + "识别策略按课设深度来看，不要按核心刊标准。"


def assemble_review_prompt(
    claim_block: str,
    research_direction: str,
    literature_count: int,
    chapter_content: str,
) -> str:
    """组装配审稿 LLM prompt（与原 review_chapter 拼接结果完全一致）。"""
    return (
        REVIEW_PROMPT_PREFIX
        + f"{claim_block}\n"
        + f"研究方向：{research_direction}\n"
        + f"文献条数：{literature_count}\n"
        + f"章节正文：\n{chapter_content}"
    )