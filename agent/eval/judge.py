"""三位审稿人如何判。默认走规则，保证对照可复现；有真模型时再问模型。"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from eval.personas import system_prompt
from nodes.review_sources.structure_checks import is_keyword_stuffed, is_overclaim

_CITE_RE = re.compile(r"\[(\d+)\]")
_DECISION_RE = re.compile(r"\b(accept|reject)\b", re.IGNORECASE)


def _content(state: Dict[str, Any]) -> str:
    chapters = state.get("body_chapters") or []
    if chapters and isinstance(chapters[0], dict):
        return str(chapters[0].get("content") or "")
    return ""


def _chapter_type(state: Dict[str, Any]) -> str:
    chapters = state.get("body_chapters") or []
    if chapters and isinstance(chapters[0], dict):
        return str(chapters[0].get("type") or "")
    return ""


def _invented_citation(state: Dict[str, Any]) -> bool:
    content = _content(state)
    indices = state.get("citation_indices") or {}
    allowed = set()
    if isinstance(indices, dict):
        allowed = {int(v) for v in indices.values() if isinstance(v, int)}
    for match in _CITE_RE.finditer(content):
        if int(match.group(1)) not in allowed:
            return True
    return False


def _missing_method_anchor(state: Dict[str, Any], content: str) -> bool:
    method = str((state.get("research_direction") or {}).get("method") or "").upper()
    chapter = _chapter_type(state)
    if chapter not in {"methods", "intro"}:
        return False
    if method == "DID":
        return not any(
            token in content
            for token in ("Callaway", "交错", "平行趋势", "Sant'Anna", "Sant’Anna")
        )
    if method == "IV":
        return not any(
            token in content
            for token in ("一阶段 F", "first stage", "first-stage", "Stock-Yogo", "Stock–Yogo")
        )
    if method == "RDD":
        return not any(token in content for token in ("带宽", "McCrary", "操纵"))
    return False


def _hard_reject(state: Dict[str, Any]) -> Optional[str]:
    if state.get("identification_failed") or state.get("star_rating") == 0:
        return "识别没过关"
    if _invented_citation(state):
        return "引用编号对不上"
    return None


def _soft_reject(persona_id: str, state: Dict[str, Any]) -> Optional[str]:
    content = _content(state)
    if is_keyword_stuffed(content):
        return "只堆方法词，没有识别设计"
    if persona_id in {"applied_micro", "journal_referee"} and is_overclaim(content):
        return "证据不支持这么强的结论"
    if persona_id == "econometrician" and _missing_method_anchor(state, content):
        return "方法锚缺失"
    if persona_id == "journal_referee" and len(content) < 40:
        return "篇幅过短，不送外审"
    return None


def rule_judge(
    persona_id: str,
    state: Dict[str, Any],
    *,
    see_auto: bool,
) -> Dict[str, str]:
    """可复现的规则审稿。see_auto 时，机器说通过会放过软伤，硬伤仍否决。"""
    hard = _hard_reject(state)
    if hard:
        return {"decision": "reject", "comment": hard}
    soft = _soft_reject(persona_id, state)
    auto = "fail"
    scores = state.get("review_scores") or []
    if scores:
        try:
            auto = "pass" if float(scores[0]) >= 0.7 else "fail"
        except (TypeError, ValueError):
            auto = "fail"
    if soft:
        if see_auto and auto == "pass":
            return {
                "decision": "accept",
                "comment": f"机器已通过，{soft} 先记下但不否决",
            }
        return {"decision": "reject", "comment": soft}
    if see_auto and auto == "fail":
        return {"decision": "reject", "comment": "机器未通过，本文也未见过硬识别"}
    return {"decision": "accept", "comment": "识别与证据对齐"}


def _parse_llm_decision(text: str) -> Optional[Dict[str, str]]:
    blob = text.strip()
    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", blob, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            decision_match = _DECISION_RE.search(blob)
            if not decision_match:
                return None
            return {
                "decision": decision_match.group(1).lower(),
                "comment": blob[:160],
            }
    if not isinstance(data, dict):
        return None
    decision = str(data.get("decision") or "").lower()
    if decision not in {"accept", "reject"}:
        return None
    comment = str(data.get("comment") or "")[:200]
    return {"decision": decision, "comment": comment or "无备注"}


def llm_judge(
    persona_id: str,
    state: Dict[str, Any],
    *,
    see_auto: bool,
) -> Optional[Dict[str, str]]:
    """有真模型就问；失败返回 None，由规则兜底。"""
    try:
        from llm.call_llm import call_llm
        from llm.router import router
    except Exception:
        return None
    config = router.get_config("review")
    if config.provider == "mock" or not config.api_key:
        return None
    content = _content(state)
    direction = state.get("research_direction") or {}
    prompt_parts = [
        f"章节类型：{_chapter_type(state)}",
        f"研究问题：{direction.get('question')}",
        f"方法：{direction.get('method')}",
        f"正文：\n{content}",
    ]
    if see_auto:
        prompt_parts.append(f"机器结论：{(state.get('review_feedback') or ['无'])[0]}")
        scores = state.get("review_scores") or []
        if scores:
            prompt_parts.append(f"机器综合分：{scores[0]}")
    else:
        prompt_parts.append("（无机器分数）")
    try:
        raw = call_llm(
            "\n".join(prompt_parts),
            node_type="review",
            system=system_prompt(persona_id, see_auto=see_auto),
        )
    except Exception:
        return None
    parsed = _parse_llm_decision(raw)
    if not parsed:
        return None
    if _hard_reject(state) and parsed["decision"] == "accept":
        parsed = {
            "decision": "reject",
            "comment": f"硬伤否决（模型想通过）：{_hard_reject(state)}",
        }
    return parsed


def judge(
    persona_id: str,
    state: Dict[str, Any],
    *,
    see_auto: bool,
    allow_llm: bool = True,
) -> Dict[str, Any]:
    source = "rules"
    verdict = None
    if allow_llm:
        verdict = llm_judge(persona_id, state, see_auto=see_auto)
        if verdict:
            source = "llm"
    if verdict is None:
        verdict = rule_judge(persona_id, state, see_auto=see_auto)
    return {
        "decision": verdict["decision"],
        "comment": verdict["comment"],
        "judge_source": source,
        "persona": persona_id,
        "ab_arm": "see_auto" if see_auto else "blind",
    }
