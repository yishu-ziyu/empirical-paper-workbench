"""ADR-0004 Stage 3: mock 评审 LLM。

按规则评分，不调真实 LLM。评分规则确定性（可复现），用于开发/测试环境。

评分规则：
- endogeneity: 提及内生 / IV / 工具变量 / endogen → 0.8；否则 0.4
- identification: 提及 DID / 双重差分 / RDD / 断点回归 / 自然实验 / identific → 0.8；否则 0.4
- robustness: 提及稳健 / 安慰剂 / placebo / robust → 0.8；否则 0.4
- contribution: 提及贡献 / novelty / 政策 / policy / contrib → 0.7；否则 0.5
- readability: 内容长度 > 200 字 → 0.8；> 100 字 → 0.6；否则 0.3

阈值规则（来自 review_chapter.py：REVIEW_SCORE_THRESHOLD=0.7）：
- 5 维加权综合分（0.3*endo + 0.25*ident + 0.2*rob + 0.15*contrib + 0.1*read）
- 全高质内容综合分 ≈ 0.775；全低质内容综合分 ≈ 0.385
"""
from typing import Any, List

from protocols import ReviewOutput, ReviewRubric


def mock_review_llm(
    chapter_content: str,
    rubric_template: ReviewRubric,
    research_direction: str,
    literature_entries: List[Any],
) -> dict:
    """mock 评审 LLM，按规则评分（确定性）。

    Args:
        chapter_content: 章节正文（用于关键词匹配与长度判断）
        rubric_template: 5 维 rubric 模板（mock 忽略，按规则重新生成）
        research_direction: 研究方向（mock 不使用）
        literature_entries: 文献列表（mock 不使用）

    Returns:
        {"rubric": ReviewRubric, "feedback": str, "suggestions": str}
    """
    content = chapter_content or ""
    content_lower = content.lower()

    rubric: ReviewRubric = ReviewRubric()

    # endogeneity: 提及内生性 / IV / 工具变量 → 高分
    if any(
        kw in content_lower
        for kw in ["内生", "iv", "工具变量", "endogen"]
    ):
        rubric["endogeneity"] = 0.8
    else:
        rubric["endogeneity"] = 0.4

    # identification: 提及 DID / RDD / 自然实验 / 双重差分 → 高分
    if any(
        kw in content_lower
        for kw in ["did", "双重差分", "rdd", "断点回归", "自然实验", "identific"]
    ):
        rubric["identification"] = 0.8
    else:
        rubric["identification"] = 0.4

    # robustness: 提及稳健性 / 安慰剂 / placebo → 高分
    if any(
        kw in content_lower for kw in ["稳健", "安慰剂", "placebo", "robust"]
    ):
        rubric["robustness"] = 0.8
    else:
        rubric["robustness"] = 0.4

    # contribution: 提及贡献 / novelty / 政策 → 高分
    if any(
        kw in content_lower
        for kw in ["贡献", "novelty", "政策", "policy", "contrib"]
    ):
        rubric["contribution"] = 0.7
    else:
        rubric["contribution"] = 0.5

    # readability: 内容长度 > 200 字 → 高分
    if len(content) > 200:
        rubric["readability"] = 0.8
    elif len(content) > 100:
        rubric["readability"] = 0.6
    else:
        rubric["readability"] = 0.3

    # 综合反馈：识别低分维度并给出针对性建议
    low_dims = [d for d, s in rubric.items() if s < 0.5]
    if low_dims:
        feedback = f"评审反馈：以下维度需加强：{', '.join(low_dims)}。"
        suggestions = (
            f"建议：1) 强化{'、'.join(low_dims)}相关论述；"
            "2) 补充实证证据；3) 增加文献支撑。"
        )
    else:
        feedback = "评审反馈：章节质量良好，各维度达标。"
        suggestions = "建议：进一步深化分析，可考虑扩展稳健性检验。"

    return {
        "rubric": rubric,
        "feedback": feedback,
        "suggestions": suggestions,
    }
