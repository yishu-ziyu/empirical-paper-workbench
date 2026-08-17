"""ADR-0004 Stage 3: 章节自动评审节点。

对当前刚生成的章节（review_chapter_index = current_chapter_index - 1）评审，
产出 5 维 rubric 评分 + 反馈 + 修改建议。评审不通过且未达迭代上限时，
回退 current_chapter_index 触发重生成。

设计要点（ADR 0004 §5、§11.2）：
- 评审节点只读 body_chapters，绝不写 body_chapters（Fitness Function 强制）
- call_review_llm 是模块级函数，便于 monkeypatch（与 generate_chapter.call_llm 同模式）；
  Stage 3 默认接 mock_review_llm（nodes.review_sources.mock_review），
  生产环境可通过 monkeypatch 替换为真实 LLM
- max_review_iterations 硬上限 3（即使用户设 5，也截断为 3）
- 空章节不触发回退（避免无限循环）
- 强制通过（iteration >= max）时不重置 review_iteration，让 route_after_review
  能据此委托 route_after_chapter；新章节检测到 review_chapter_index 变化时重置
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, List, Optional

from protocols import ReviewOutput, ReviewRubric
from state import EconPaperState

# 评审通过阈值（运行时常量，不入 state）
REVIEW_SCORE_THRESHOLD = 0.7

# 综合分加权公式（实证章节默认）
# 0.3*endogeneity + 0.25*identification + 0.2*robustness + 0.15*contribution + 0.1*readability
RUBRIC_WEIGHTS = {
    "endogeneity": 0.3,
    "identification": 0.25,
    "robustness": 0.2,
    "contribution": 0.15,
    "readability": 0.1,
}

# ADR-0004 Decision C：非实证章节内生性权重降为 0，可读 / 贡献抬高
RUBRIC_WEIGHTS_BY_TYPE = {
    "methods": RUBRIC_WEIGHTS,
    "results": RUBRIC_WEIGHTS,
    "data_desc": {
        "endogeneity": 0.0,
        "identification": 0.1,
        "robustness": 0.25,
        "contribution": 0.25,
        "readability": 0.4,
    },
    "lit_review": {
        "endogeneity": 0.0,
        "identification": 0.1,
        "robustness": 0.1,
        "contribution": 0.4,
        "readability": 0.4,
    },
    "intro": {
        "endogeneity": 0.0,
        "identification": 0.05,
        "robustness": 0.05,
        "contribution": 0.15,
        "readability": 0.75,
    },
    "conclusion": {
        "endogeneity": 0.0,
        "identification": 0.05,
        "robustness": 0.1,
        "contribution": 0.2,
        "readability": 0.65,
    },
}

_RUBRIC_DIMS = (
    "endogeneity",
    "identification",
    "robustness",
    "contribution",
    "readability",
)

# 关联主张禁用子串（当作本文主张）。允许句不在此列。
FORBIDDEN_CAUSAL_CLAIMS = (
    "本文识别了因果",
    "因果效应显著",
    "识别策略成立",
    "解决内生性",
)
ALLOWED_CAUSAL_PHRASES = (
    "无法做因果识别",
    "仅解释为相关",
)

RUBRIC_WEIGHTS_METHODS_ASSOCIATION = {
    "endogeneity": 0.0,
    "identification": 0.1,
    "robustness": 0.25,
    "contribution": 0.25,
    "readability": 0.4,
}

CAUSAL_CLAIM_SCORE_CAP = 0.50
ASSOCIATION_SCORE_FLOOR = 0.7

_CAUSAL_IDENT_DEMAND = (
    "工具变量",
    "双重差分",
    "断点回归",
    "识别策略",
    "自然实验",
    "内生性",
    "rdd",
)

_GROUNDING_CODES = (
    "causal_claim_forbidden",
    "invented_number",
    "missing_estimate_number",
    "invented_table",
)


def invoke_review_llm(
    config: Any,
    chapter_content: str,
    rubric_template: ReviewRubric,
    research_direction: str,
    literature_entries: List[Any],
    claim: str = "",
) -> dict:
    """非 mock 评审通道。要求 JSON ``{rubric, feedback, suggestions}``。"""
    from llm.call_llm import call_llm as unified_call

    claim_block = _review_claim_instruction(claim)
    prompt = (
        "你是经济学论文审稿人。只输出 JSON，不要 markdown。"
        "字段：rubric{endogeneity,identification,robustness,contribution,readability}"
        "（每维 0 到 1）、feedback、suggestions。\n"
        f"{claim_block}\n"
        f"研究方向：{research_direction}\n"
        f"文献条数：{len(literature_entries or [])}\n"
        f"章节正文：\n{chapter_content}"
    )
    raw = unified_call(prompt, node_type="review")
    parsed = _parse_review_json(raw)
    if parsed is None:
        raise ValueError("review llm returned unparseable json")
    return parsed


def _parse_review_json(raw: str) -> Optional[dict]:
    """解析评审 JSON。失败返回 None，由调用方降级 mock。"""
    if not raw or not isinstance(raw, str):
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            payload = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
    if not isinstance(payload, dict):
        return None
    rubric_raw = payload.get("rubric") or {}
    if not isinstance(rubric_raw, dict):
        return None
    rubric: ReviewRubric = ReviewRubric()
    for dim in _RUBRIC_DIMS:
        try:
            value = float(rubric_raw.get(dim, 0.0))
        except (TypeError, ValueError):
            value = 0.0
        rubric[dim] = min(1.0, max(0.0, value))
    return {
        "rubric": rubric,
        "feedback": str(payload.get("feedback") or ""),
        "suggestions": str(payload.get("suggestions") or ""),
    }


def call_review_llm(
    chapter_content: str,
    rubric_template: ReviewRubric,
    research_direction: str,
    literature_entries: List[Any],
    claim: str = "",
) -> dict:
    """模块级 LLM 调用函数（与 generate_chapter.call_llm 同一 monkeypatch 模式）。

    ADR-0008: 通过 LLMRouter 调用评审 LLM。
    - provider == "mock"（默认）→ 调 mock_review_llm（开发/测试）
    - provider == "anthropic" / "openai" → 走 invoke_review_llm；
      JSON 解析失败降级回 mock，不把 graph 打费
    """
    from llm.router import router
    from nodes.review_sources.mock_review import mock_review_llm

    config = router.get_config("review")

    if config.provider == "mock":
        result = mock_review_llm(
            chapter_content,
            rubric_template,
            research_direction,
            literature_entries,
            claim=claim,
        )
        return {**result, "review_source": "mock", "review_degraded": False}

    try:
        result = invoke_review_llm(
            config,
            chapter_content,
            rubric_template,
            research_direction,
            literature_entries,
            claim=claim,
        )
        return {**result, "review_source": "llm", "review_degraded": False}
    except Exception:
        result = mock_review_llm(
            chapter_content,
            rubric_template,
            research_direction,
            literature_entries,
            claim=claim,
        )
        return {
            **result,
            "review_source": "mock_fallback",
            "review_degraded": True,
        }


def weights_for_chapter(chapter_type: str, claim: str = "") -> dict:
    """按章取 rubric 权重。未知 type 退回实证默认。"""
    if (chapter_type or "") == "methods" and claim == "association":
        return dict(RUBRIC_WEIGHTS_METHODS_ASSOCIATION)
    return RUBRIC_WEIGHTS_BY_TYPE.get(chapter_type or "", RUBRIC_WEIGHTS)


def _compute_composite_score(
    rubric: ReviewRubric, chapter_type: str = "methods", claim: str = ""
) -> float:
    """加权综合分。默认 methods 权重，兼容既有单测。"""
    weights = weights_for_chapter(chapter_type, claim=claim)
    total = 0.0
    for dim, weight in weights.items():
        total += rubric.get(dim, 0.0) * weight
    return round(total, 6)


def _chapter_type_of(chapter: Any, state: EconPaperState, idx: int) -> str:
    if isinstance(chapter, dict) and chapter.get("type"):
        return str(chapter["type"])
    outline = state.get("outline") or []
    if isinstance(outline, list) and 0 <= idx < len(outline):
        spec = outline[idx]
        if isinstance(spec, dict):
            return str(spec.get("type") or "")
    return ""


def _methods_method_from_outline(state: EconPaperState) -> str:
    outline = state.get("outline") or []
    if not isinstance(outline, list):
        return ""
    for spec in outline:
        if isinstance(spec, dict) and spec.get("type") == "methods":
            return str(spec.get("method") or "")
    return str(state.get("method") or "")


def _claim_of(state: EconPaperState) -> str:
    raw = state.get("claim")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    rd = state.get("research_direction")
    if isinstance(rd, dict):
        user_claim = rd.get("claim")
        if isinstance(user_claim, str) and user_claim.strip():
            return user_claim.strip()
    try:
        from engine.readiness import claim_mode

        return claim_mode(state) or ""
    except Exception:
        return ""


def _review_claim_instruction(claim: str) -> str:
    course = (
        "这是本科课程论文，不是期刊投稿。"
        "不得因为没有边际贡献、三条贡献、政策贡献或学术增量而扣 contribution。"
        "contribution 只看题目有没有写清楚、有没有按课设作答。"
    )
    if _is_association_claim(claim):
        return (
            course
            + "本文主张模式是 association（条件相关，不是因果识别）。"
            "不得因为没有 IV、RDD、DID、工具变量或识别策略而扣 "
            "identification / endogeneity / contribution。"
            "这些方法不是本篇的要求。"
            "只检查：有没有把相关写成因果；论述是否清楚。"
        )
    return course + "识别策略按课设深度来看，不要按核心刊标准。"


def _is_association_claim(claim: str) -> bool:
    return str(claim or "").strip().lower() in {
        "association",
        "assoc",
        "correlation",
    }


def _demands_causal_ident(text: str) -> bool:
    raw = text or ""
    low = raw.lower()
    if re.search(r"\biv\b", low) or re.search(r"\bdid\b", low):
        return True
    return any(token in low for token in _CAUSAL_IDENT_DEMAND)


def apply_association_review_guard(
    rubric: dict,
    feedback: str,
    suggestions: str,
    claim: str,
    content: str,
) -> tuple[dict, str, str]:
    """现场 LLM 常按因果稿打相关文。相关且未写禁句时，缺 IV/RDD 不是失败。"""
    if not _is_association_claim(claim):
        return dict(rubric), feedback, suggestions
    if _has_forbidden_causal_claim(content):
        return dict(rubric), feedback, suggestions
    next_rubric = dict(rubric)
    for dim in ("endogeneity", "identification", "contribution"):
        try:
            value = float(next_rubric.get(dim) or 0.0)
        except (TypeError, ValueError):
            value = 0.0
        if value < ASSOCIATION_SCORE_FLOOR:
            next_rubric[dim] = ASSOCIATION_SCORE_FLOOR
    if _demands_causal_ident(f"{feedback}\n{suggestions}"):
        for dim in ("endogeneity", "identification", "robustness", "contribution"):
            try:
                value = float(next_rubric.get(dim) or 0.0)
            except (TypeError, ValueError):
                value = 0.0
            next_rubric[dim] = max(value, ASSOCIATION_SCORE_FLOOR)
        try:
            readability = float(next_rubric.get("readability") or 0.0)
        except (TypeError, ValueError):
            readability = 0.0
        next_rubric["readability"] = max(readability, ASSOCIATION_SCORE_FLOOR)
        note = "本文按相关写。缺少 IV / RDD / 双重差分不是缺陷。"
        kept_fb = _drop_required_ident_spans(feedback)
        kept_sg = _drop_required_ident_spans(suggestions)
        feedback = note if not kept_fb else f"{note}\n{kept_fb}"
        suggestions = kept_sg or "保持相关表述，不要把系数写成处理效应。"
    return next_rubric, feedback, suggestions


def _looks_like_ident_requirement(text: str) -> bool:
    return any(
        token in text
        for token in (
            "必须",
            "应使用",
            "应当",
            "缺少识别",
            "补双重",
            "补 IV",
            "否则识别",
            "识别失败",
        )
    )


def _drop_required_ident_spans(text: str) -> str:
    if not text:
        return ""
    kept: list[str] = []
    for part in re.split(r"(?<=[。；\n])", text):
        piece = part.strip()
        if not piece:
            continue
        if _demands_causal_ident(piece) and _looks_like_ident_requirement(piece):
            continue
        kept.append(part)
    return "".join(kept).strip()


def _has_forbidden_causal_claim(content: str) -> bool:
    text = content or ""
    for allowed in ALLOWED_CAUSAL_PHRASES:
        text = text.replace(allowed, "")
    return any(token in text for token in FORBIDDEN_CAUSAL_CLAIMS)


def _visibility_fields(
    review_source: str,
    review_degraded: bool,
    grounding_failures: List[str],
    degradations: Optional[List[Any]] = None,
) -> dict:
    fields: dict = {
        "review_source": review_source,
        "review_degraded": review_degraded,
        "grounding_failures": list(grounding_failures),
    }
    if degradations:
        fields["degradations"] = degradations
    return fields


def review_chapter(state: EconPaperState) -> ReviewOutput:
    """对当前刚生成的章节评审。

    1. review_enabled == False → 返回 {} (no-op)
    2. 计算 idx = current_chapter_index - 1（generate_chapter 已自增）
    3. idx < 0 或 body_chapters 为空 → 返回 {}
    4. 检测新章节：若 state['review_chapter_index'] != idx，说明换了章节，重置 review_iteration = 0
    5. 读 body_chapters[idx].content + research_direction + literature_entries
    6. 调 call_review_llm 得 rubric + feedback + suggestions
    7. 加权算综合分
    8. 写 review_feedback[idx] / revision_suggestions[idx] / review_scores[idx] / review_rubrics[idx]
    9. 若综合分 < threshold 且 review_iteration < max_review_iterations:
       - 写 current_chapter_index = idx（回退）
       - 写 review_iteration += 1
       若综合分 >= threshold（真正通过）:
       - 写 review_iteration = 0（重置，为下一章准备）
       否则（强制通过，iteration >= max）:
       - 不重置 review_iteration（保留 max 值，让 route_after_review 据此委托）
    10. 写 review_chapter_index = idx
    11. 返回 ReviewOutput（不含 body_chapters）
    """
    review_enabled = state.get("review_enabled", True)
    if not review_enabled:
        return {}

    current_idx = state.get("current_chapter_index", 0)
    idx = current_idx - 1
    if idx < 0:
        return {}

    body_chapters = state.get("body_chapters", [])
    if idx >= len(body_chapters):
        return {}

    # 读现有评审列表（可能为空或部分填充），复制为可变列表
    review_feedback: List[str] = list(state.get("review_feedback", []) or [])
    revision_suggestions: List[str] = list(state.get("revision_suggestions", []) or [])
    review_scores: List[float] = list(state.get("review_scores", []) or [])
    review_rubrics: List[Any] = list(state.get("review_rubrics", []) or [])

    # 扩展列表到 idx+1（用占位符填充）
    while len(review_feedback) <= idx:
        review_feedback.append("")
    while len(revision_suggestions) <= idx:
        revision_suggestions.append("")
    while len(review_scores) <= idx:
        review_scores.append(0.0)
    while len(review_rubrics) <= idx:
        review_rubrics.append({})

    chapter = body_chapters[idx]
    chapter_content = chapter.get("content", "") if isinstance(chapter, dict) else ""

    # 空章节：评分 0，但不触发回退（避免空章节无限重生成）
    if not chapter_content:
        review_feedback[idx] = "章节内容为空，跳过评审"
        revision_suggestions[idx] = ""
        review_scores[idx] = 0.0
        review_rubrics[idx] = {
            "endogeneity": 0.0, "identification": 0.0,
            "robustness": 0.0, "contribution": 0.0, "readability": 0.0,
        }
        return {
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "review_scores": review_scores,
            "review_rubrics": review_rubrics,
            "review_iteration": 0,
            "review_chapter_index": idx,
            **_visibility_fields("", False, []),
        }

    # 新章节检测：若上一轮 review_chapter_index != idx，说明换了章节，重置迭代
    prev_review_idx = state.get("review_chapter_index")
    if prev_review_idx is not None and prev_review_idx != idx:
        review_iteration = 0
    else:
        review_iteration = state.get("review_iteration", 0)

    research_direction = state.get("research_direction", "")
    literature_entries = state.get("literature_entries", [])
    max_iterations = min(state.get("max_review_iterations", 2), 3)

    claim = _claim_of(state)
    chapter_type = _chapter_type_of(chapter, state, idx)
    grounding_failures: List[str] = []
    if claim == "association" and _has_forbidden_causal_claim(chapter_content):
        grounding_failures.append("causal_claim_forbidden")
    if chapter_type == "results":
        from nodes.review_sources.grounding import check_grounding

        grounding_failures.extend(check_grounding(state, chapter_content))

    rubric_template = ReviewRubric()
    llm_result = call_review_llm(
        chapter_content,
        rubric_template,
        research_direction,
        literature_entries,
        claim=claim,
    )
    rubric = dict(llm_result["rubric"])
    feedback = str(llm_result["feedback"] or "")
    suggestions = str(llm_result["suggestions"] or "")
    review_source = str(llm_result.get("review_source") or "mock")
    review_degraded = bool(llm_result.get("review_degraded"))
    method = ""
    if isinstance(chapter, dict):
        method = str(chapter.get("method") or state.get("method") or "")
    else:
        method = str(state.get("method") or "")

    from nodes.review_sources.structure_checks import (
        apply_structure_cap,
        check_structure,
    )
    from nodes.review_sources.threat_cards import (
        active_threat_cards,
        apply_threat_caps,
    )

    triggered = apply_threat_caps(rubric, chapter_content, active_threat_cards(state))
    if triggered:
        suggestions = (
            f"{suggestions} 未处理识别威胁：{', '.join(triggered)}。"
        ).strip()
    rubric, feedback, suggestions = apply_association_review_guard(
        rubric,
        feedback,
        suggestions,
        claim,
        chapter_content,
    )

    score = _compute_composite_score(rubric, chapter_type, claim=claim)
    structure_kwargs = {}
    if "star_rating" in state:
        structure_kwargs["star_rating"] = state.get("star_rating")
    failures = check_structure(
        chapter_type,
        chapter_content,
        method=method,
        methods_method=_methods_method_from_outline(state),
        citation_indices=state.get("citation_indices"),
        claim=claim,
        **structure_kwargs,
    )
    score = apply_structure_cap(score, failures)
    if failures:
        suggestions = (
            f"{suggestions} 结构层失败：{', '.join(failures)}。不得只堆关键词。"
        ).strip()
    hit_codes = [code for code in grounding_failures if code in _GROUNDING_CODES]
    if hit_codes:
        score = min(score, CAUSAL_CLAIM_SCORE_CAP)
        suggestions = (
            f"{suggestions} 主张/接地层失败：{', '.join(hit_codes)}。"
        ).strip()

    review_feedback[idx] = feedback
    revision_suggestions[idx] = suggestions
    review_scores[idx] = score
    review_rubrics[idx] = rubric

    degradations = None
    if review_degraded:
        degradations = list(state.get("degradations") or [])
        degradations.append({
            "node": "review_chapter",
            "reason": "review_llm_unparseable_or_error",
            "fallback": "mock_review_llm",
            "visible": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    visible = _visibility_fields(
        review_source, review_degraded, grounding_failures, degradations
    )

    if score < REVIEW_SCORE_THRESHOLD and review_iteration < max_iterations:
        # 回退：重生成当前章
        return {
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "review_scores": review_scores,
            "review_rubrics": review_rubrics,
            "review_iteration": review_iteration + 1,
            "review_chapter_index": idx,
            "current_chapter_index": idx,  # 回退
            **visible,
        }
    elif score >= REVIEW_SCORE_THRESHOLD:
        # 真正通过：重置迭代，为下一章准备
        return {
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "review_scores": review_scores,
            "review_rubrics": review_rubrics,
            "review_iteration": 0,
            "review_chapter_index": idx,
            **visible,
        }
    else:
        # 强制通过（iteration >= max）：保留 review_iteration，让 route_after_review
        # 能据此委托 route_after_chapter；下一章评审时由新章节检测重置
        return {
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "review_scores": review_scores,
            "review_rubrics": review_rubrics,
            "review_iteration": review_iteration,
            "review_chapter_index": idx,
            **visible,
        }
