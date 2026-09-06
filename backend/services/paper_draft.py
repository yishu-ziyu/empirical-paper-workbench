"""Frame 5 paper draft orchestration over the canonical Facade session state.

The service is deliberately copy-on-write: agent nodes run on a deep copy and
the Facade is saved once, only after title, six chapters, reviews and references
all pass the formal-draft gates.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Iterable, Mapping

from facade import facade

from agent.engine.bind import bind_chapter_kwargs
from agent.nodes.generate_chapter import generate_chapter as generate_chapter_node
from agent.nodes.generate_references import generate_references as generate_references_node
from agent.nodes.generate_title import generate_title as generate_title_node
from agent.nodes.literature_sources.crossref import resolve_doi
from agent.nodes.review_chapter import (
    REVIEW_SCORE_THRESHOLD,
    review_chapter as review_chapter_node,
)


_CHAPTER_TYPES = (
    "intro",
    "lit_review",
    "data_desc",
    "methods",
    "results",
    "conclusion",
)
_CLAIM_ID = "main-estimate"
_UNREADY_STATUSES = {"warn", "warning", "error", "failed", "fail", "degraded", "skipped"}
_SHORT_DRAFT_INSTRUCTION = (
    "本轮生成短而完整的中文初稿：优先保留事实、证据与限制，"
    "不扩写未绑定的数字、因果、政策或文献结论。"
)
_NUMBER_RE = re.compile(r"(?<![A-Za-z_])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?%?")
_MAX_CHAPTER_GENERATIONS = 3
_REPAIRABLE_GROUNDING_FAILURES = {
    "causal_claim_forbidden",
    "invented_number",
    "invented_table",
    "missing_estimate_number",
}
_STRUCTURE_FAILURE_RE = re.compile(r"结构层失败：([^\u3002]+)")
_REVIEW_RUBRIC_DIMS = {
    "endogeneity",
    "identification",
    "robustness",
    "contribution",
    "readability",
}


def _generation_is_authentic(chapter: Any) -> bool:
    return (
        isinstance(chapter, Mapping)
        and chapter.get("generation_source") == "llm"
        and chapter.get("generation_degraded") is False
    )


def _review_is_authentic(result: Mapping[str, Any], index: int) -> bool:
    if (
        result.get("review_source") != "llm"
        or result.get("review_degraded") is not False
        or result.get("review_typed") is not True
    ):
        return False
    rubrics = result.get("review_rubrics") or []
    rubric = rubrics[index] if isinstance(rubrics, list) and index < len(rubrics) else None
    if not isinstance(rubric, Mapping) or set(rubric) != _REVIEW_RUBRIC_DIMS:
        return False
    return all(
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and 0.0 <= float(value) <= 1.0
        for value in rubric.values()
    )


def _set_section_review_provenance(
    state: dict,
    index: int,
    review_result: Mapping[str, Any],
    grounding_failures: Iterable[str],
    structure_failures: Iterable[str],
) -> None:
    chapters = list(state.get("body_chapters") or [])
    chapter = dict(chapters[index])
    chapter.update(
        {
            "review_source": str(review_result.get("review_source") or ""),
            "review_degraded": bool(review_result.get("review_degraded")),
            "review_typed": bool(review_result.get("review_typed")),
            "review_status": "passed",
            "grounding_failures": list(grounding_failures),
            "structure_failures": list(structure_failures),
        }
    )
    chapters[index] = chapter
    state["body_chapters"] = chapters


def _formal_sections_are_authentic(state: Mapping[str, Any]) -> bool:
    chapters = state.get("body_chapters") or []
    if len(chapters) != len(_CHAPTER_TYPES):
        return False
    return all(
        _generation_is_authentic(chapter)
        and chapter.get("review_source") == "llm"
        and chapter.get("review_degraded") is False
        and chapter.get("review_typed") is True
        and chapter.get("review_status") == "passed"
        and not chapter.get("grounding_failures")
        and not chapter.get("structure_failures")
        and chapter.get("versions") == [chapter.get("content")]
        for chapter in chapters
        if isinstance(chapter, Mapping)
    ) and all(isinstance(chapter, Mapping) for chapter in chapters)


def _clean_abstract(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    return re.sub(r"</?jats:[^>]+>", "", text).strip() or None


def _first_title(message: Mapping[str, Any]) -> str | None:
    raw = message.get("title")
    if isinstance(raw, list) and raw:
        return str(raw[0] or "").strip() or None
    return str(raw or "").strip() or None


def _verified_crossref_entries(state: Mapping[str, Any]) -> tuple[list[dict], list[str]]:
    """Return DOI-resolved Crossref entries and formal-draft gaps."""
    if str(state.get("literature_source") or "") != "crossref":
        return [], ["literature_source_not_crossref"]

    candidates = [
        dict(entry)
        for entry in (state.get("literature_entries") or [])
        if isinstance(entry, Mapping) and entry.get("source") == "crossref"
    ]
    if not candidates:
        return [], ["no_crossref_literature"]

    verified: list[dict] = []
    for entry in candidates:
        doi = str(entry.get("doi") or "").strip()
        if not doi:
            return [], ["crossref_doi_missing"]
        try:
            message = resolve_doi(doi)
        except Exception:
            return [], ["doi_resolve_failed"]
        resolved = str((message or {}).get("DOI") or "").strip()
        if not resolved or resolved.casefold() != doi.casefold():
            return [], ["doi_resolve_failed"]
        copied = dict(entry)
        copied["doi"] = resolved
        copied["title"] = _first_title(message) or str(entry.get("title") or "")
        copied["abstract"] = (
            _clean_abstract((message or {}).get("abstract"))
            or _clean_abstract(entry.get("abstract"))
            or ""
        )
        copied["source"] = "crossref"
        copied["doi_verified"] = True
        copied["doi_resolved_source"] = "crossref"
        verified.append(copied)
    return verified, []


def _formal_citation_state(state: dict, entries: list[dict]) -> None:
    ordered = sorted(
        entries,
        key=lambda entry: (entry.get("year", 0) or 0, entry.get("title", "") or ""),
    )
    indices = {str(entry["doi"]): index for index, entry in enumerate(ordered, 1)}
    allowed = set(indices)
    prior_graph = state.get("citation_graph") or {}
    prior_edges = prior_graph.get("edges") if isinstance(prior_graph, Mapping) else []
    edges = [
        dict(edge)
        for edge in (prior_edges or [])
        if isinstance(edge, Mapping)
        and edge.get("from") in allowed
        and edge.get("to") in allowed
    ]
    state["literature_entries"] = ordered
    state["citation_indices"] = indices
    state["citation_graph"] = {
        "entries": ordered,
        "edges": edges,
        "indices": indices,
    }


def _effective_claim(state: Mapping[str, Any]) -> str:
    direction = state.get("research_direction") or {}
    method = direction.get("method") if isinstance(direction, Mapping) else ""
    return str(bind_chapter_kwargs(state, {"type": "methods", "method": method})["claim"])


def _preflight(state: Mapping[str, Any]) -> tuple[list[str], str, list[dict]]:
    gaps: list[str] = []
    estimate = state.get("estimate") or {}
    if not isinstance(estimate, Mapping) or estimate.get("status") != "ok":
        gaps.append("estimate_not_ok")
    else:
        if not str(estimate.get("treatment_row") or "").strip():
            gaps.append("treatment_row_missing")
        if not str(estimate.get("formula") or "").strip():
            gaps.append("formula_missing")
        n = estimate.get("n")
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
            gaps.append("sample_size_missing")

    claim = _effective_claim(state)
    if claim not in {"association", "causal_with_caveat"}:
        gaps.append("claim_not_supported")
    if state.get("grounding_failures"):
        gaps.append("grounding_failure")

    entries, literature_gaps = _verified_crossref_entries(state)
    gaps.extend(literature_gaps)
    return list(dict.fromkeys(gaps)), claim, entries


def _outline_gap(state: Mapping[str, Any]) -> str | None:
    outline = state.get("outline") or []
    types = [entry.get("type") for entry in outline if isinstance(entry, Mapping)]
    return None if types == list(_CHAPTER_TYPES) else "fixed_six_chapter_outline_missing"


def _analysis_evidence(state: Mapping[str, Any]) -> dict:
    estimate = state.get("estimate") or {}
    if not isinstance(estimate, Mapping):
        estimate = {}
    return {
        "formula": str(estimate.get("formula") or ""),
        "n": estimate.get("n"),
        "coef": estimate.get("coef"),
        "se": estimate.get("se"),
        "p": estimate.get("p"),
        "treatment": str(estimate.get("treatment") or ""),
        "treatment_row": str(estimate.get("treatment_row") or ""),
        "estimator": str(estimate.get("estimator") or ""),
        "status": str(estimate.get("status") or ""),
    }


def _source_evidence(entries: Iterable[Any]) -> list[dict]:
    sources: list[dict] = []
    for raw in entries or []:
        if not isinstance(raw, Mapping) or raw.get("source") != "crossref":
            continue
        doi = str(raw.get("doi") or "").strip()
        sources.append(
            {
                "title": str(raw.get("title") or ""),
                "abstract": _clean_abstract(raw.get("abstract")),
                "doi": doi,
                "url": str(raw.get("url") or (f"https://doi.org/{doi}" if doi else "")),
                "source": "crossref",
                "status": "verified" if raw.get("doi_verified") is True else "unverified",
                "excerpt": None,
                "excerpt_status": "unavailable",
            }
        )
    return sources


def _claim_text(state: Mapping[str, Any], claim: str) -> str:
    direction = state.get("research_direction") or {}
    estimate = state.get("estimate") or {}
    outcome = direction.get("dv") if isinstance(direction, Mapping) else None
    treatment = estimate.get("treatment") if isinstance(estimate, Mapping) else None
    coef = estimate.get("coef") if isinstance(estimate, Mapping) else None
    n = estimate.get("n") if isinstance(estimate, Mapping) else None
    relation = "条件关联" if claim == "association" else "因果效应"
    return f"{treatment} 与 {outcome} 的{relation}估计为 {coef}（N={n}）。"


def _number_tokens(value: Any) -> set[str]:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return {match.group(0) for match in _NUMBER_RE.finditer(text)}


def _ungrounded_numbers(state: Mapping[str, Any], chapter: Mapping[str, Any]) -> list[str]:
    """Reject chapter numbers absent from the state-backed prompt inputs.

    This complements the existing results-table grounding check. It deliberately
    compares literal tokens: a derived percentage is not allowed unless that
    percentage was already bound into the chapter inputs.
    """
    bound = bind_chapter_kwargs(state, chapter)
    truth = {
        key: state.get(key)
        for key in (
            "research_direction",
            "main_specification",
            "estimate",
            "results",
            "robustness_results",
            "identification_diag",
            "literature_entries",
            "citation_indices",
            "uploaded_datasets",
            "cleaning_report",
            "data_summary",
            "eda_results",
            "spec_curve",
            "policy_evidence",
        )
    }
    allowed = _number_tokens(truth) | _number_tokens(bound)
    forbidden_wording = bound.get("claim_unsupported_wording")
    if forbidden_wording and str(forbidden_wording) not in {"", "未提供"}:
        allowed -= _number_tokens(forbidden_wording)
    content = str(chapter.get("content") or "")
    return sorted(_number_tokens(content) - allowed)


def _offending_sentences(content: str, tokens: Iterable[str]) -> list[str]:
    remaining = {str(token) for token in tokens if str(token)}
    if not remaining:
        return []
    sentences: list[str] = []
    for raw in re.split(r"(?<=[。！？!?])|\n+", content or ""):
        sentence = " ".join(raw.split()).strip()
        sentence_numbers = _number_tokens(sentence)
        hits = sentence_numbers & remaining
        if sentence and hits:
            sentences.append(sentence)
            remaining -= hits
            if not remaining:
                break
    return list(dict.fromkeys(sentences))


def _allowed_fact_summary(state: Mapping[str, Any], chapter: Mapping[str, Any]) -> str:
    analysis = _analysis_evidence(state)
    analysis_parts = [
        f"{label}={analysis.get(key)}"
        for key, label in (
            ("formula", "formula"),
            ("n", "N"),
            ("coef", "coef"),
            ("se", "SE"),
            ("p", "p"),
            ("treatment_row", "treatment_row"),
        )
        if analysis.get(key) not in (None, "")
    ]
    literature_parts: list[str] = []
    for entry in state.get("literature_entries") or []:
        if not isinstance(entry, Mapping):
            continue
        title = str(entry.get("title") or "").strip() or "未提供标题"
        year = entry.get("year")
        doi = str(entry.get("doi") or "").strip() or "未提供 DOI"
        literature_parts.append(
            f"《{title}》 year={year if year not in (None, '') else '未提供'}; DOI={doi}"
        )

    bound_numbers = sorted(
        _number_tokens(bind_chapter_kwargs(state, chapter)),
        key=lambda value: (len(value), value),
    )
    visible_numbers = ", ".join(bound_numbers[:24]) or "无"
    if len(bound_numbers) > 24:
        visible_numbers += f" （其余 {len(bound_numbers) - 24} 个仅可从当前已绑定章节输入逐字复用）"
    return (
        f"允许的分析事实：{'; '.join(analysis_parts) or '无'}。"
        f"允许的文献事实：{'; '.join(literature_parts) or '无'}。"
        f"当前章已绑定的数字字面量：{visible_numbers}。"
    )


def _review_suggestion(review_result: Mapping[str, Any], index: int) -> str:
    suggestions = review_result.get("revision_suggestions") or []
    if isinstance(suggestions, list) and index < len(suggestions):
        return str(suggestions[index] or "").strip()
    return ""


def _structure_failures(review_result: Mapping[str, Any], suggestion: str) -> list[str]:
    failures = review_result.get("structure_failures") or []
    if isinstance(failures, str):
        failures = [failures]
    found = [str(item).strip() for item in failures if str(item).strip()]
    for match in _STRUCTURE_FAILURE_RE.finditer(suggestion):
        found.extend(
            item.strip()
            for item in match.group(1).split(",")
            if item.strip()
        )
    return list(dict.fromkeys(found))


def _revision_instruction(
    state: Mapping[str, Any],
    chapter: Mapping[str, Any],
    *,
    failures: Iterable[str],
    invented_numbers: Iterable[str] = (),
    offending_sentences: Iterable[str] = (),
    structure_failures: Iterable[str] = (),
    reviewer_suggestion: str = "",
) -> str:
    codes = list(dict.fromkeys(str(code) for code in failures if str(code)))
    numbers = list(dict.fromkeys(str(value) for value in invented_numbers if str(value)))
    sentences = list(
        dict.fromkeys(
            [
                *(str(item) for item in offending_sentences if str(item)),
                *_offending_sentences(str(chapter.get("content") or ""), numbers),
            ]
        )
    )
    details = [f"失败码：{', '.join(codes) or '无'}。"]
    if numbers:
        details.append(f"未绑定数字/年份：{', '.join(numbers)}。")
    if sentences:
        details.append(f"必须删除或改写的原句：{' | '.join(sentences)}")
    if numbers:
        details.append(
            "防止二次发明：叙述句不得复述、四舍五入或换算描述统计；"
            "只能逐字保留当前已绑定输入中的原始表格行。"
        )
    if any(value.endswith("%") for value in numbers):
        details.append(
            "本轮禁止输出任何百分比；将比例句改为“存在缺失”等无数字表述。"
        )
    if numbers and chapter.get("type") == "data_desc":
        details.append(
            "数据描述安全重写方案（必须采用）："
            "三个二级标题下的叙述句只做定性说明，不写任何阿拉伯数字；"
            "描述统计只能把用户提示中“EDA 结果（描述统计）”的原始表格块"
            "逐字复制一次。不得手写、重排、缩写或另建描述统计表；"
            "特别不得添加千位逗号、改变小数位、把数值改写为万或百分比。"
        )
    structure = [str(item) for item in structure_failures if str(item)]
    if structure:
        details.append(f"必须修复的结构问题：{', '.join(structure)}。")
    if reviewer_suggestion:
        details.append(f"评审的可执行建议：{reviewer_suggestion}")
    details.append(_allowed_fact_summary(state, chapter))
    details.append(
        "硬性输出检查：上述未绑定 token 再出现即为失败。"
        "优先删除包含它们的整句；如确有必要，只能逐字复用上述明确事实，"
        "不得换成另一个数字。未提供年份的文献不得补年份。"
        "不得合理估计、换算、推导或新造数字。"
    )
    return f"{_SHORT_DRAFT_INSTRUCTION}\n" + "\n".join(details)


def _attempt_gap(
    chapter_type: str,
    attempt: int,
    failures: Iterable[str],
    *,
    values: Iterable[str] = (),
) -> str:
    joined = ",".join(dict.fromkeys(str(item) for item in failures if str(item)))
    gap = (
        f"chapter_retry_exhausted:{chapter_type}:attempt={attempt}:"
        f"failures={joined or 'unknown'}"
    )
    details = ",".join(dict.fromkeys(str(item) for item in values if str(item)))
    return f"{gap}:values={details}" if details else gap


def _limitation(state: Mapping[str, Any], claim: str) -> str:
    if claim == "association":
        return "当前 OLS 主结果只表示给定样本、变量和控制条件下的关联，不构成因果效应。"
    return "因果表述仅限于当前 state 中已通过的识别与稳健性证据，不得外推。"


def _iter_problem_statuses(value: Any, path: str = "state") -> Iterable[tuple[str, str, str]]:
    if isinstance(value, Mapping):
        status = str(value.get("status") or "").strip().lower()
        if status in _UNREADY_STATUSES:
            detail = value.get("reason") or value.get("report") or value.get("error") or status
            yield path, status, str(detail)
        if value.get("degraded") is True and status != "degraded":
            yield path, "degraded", str(value.get("reason") or "degraded")
        for key, child in value.items():
            if key not in {"content", "versions", "results", "summary_table"}:
                yield from _iter_problem_statuses(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_problem_statuses(child, f"{path}[{index}]")


def _open_questions(
    state: Mapping[str, Any], gaps: Iterable[str], extra: Iterable[dict] = ()
) -> list[dict]:
    questions: list[dict] = [
        {
            "code": str(gap),
            "message": str(gap),
            "source": "readiness_gate",
            "severity": "error",
        }
        for gap in gaps
    ]
    for path, status, detail in _iter_problem_statuses(state):
        questions.append(
            {
                "code": f"{path}:{status}",
                "message": detail,
                "source": path,
                "severity": "warning" if status in {"warn", "warning", "degraded", "skipped"} else "error",
            }
        )
    for item in state.get("degradations") or []:
        if isinstance(item, Mapping):
            questions.append(
                {
                    "code": str(item.get("reason") or "degradation"),
                    "message": str(item.get("reason") or "degradation"),
                    "source": str(item.get("node") or "degradations"),
                    "severity": "warning",
                }
            )
    questions.extend(dict(item) for item in extra)
    unique: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for question in questions:
        key = (str(question.get("code")), str(question.get("source")))
        if key not in seen:
            seen.add(key)
            unique.append(question)
    return unique


def _not_ready(state: Mapping[str, Any], gaps: Iterable[str], extra: Iterable[dict] = ()) -> dict:
    unique_gaps = list(dict.fromkeys(str(gap) for gap in gaps))
    return {
        "status": "not_ready",
        "readiness": "not_ready",
        "gaps": unique_gaps,
        "paper": None,
        "main_claim": None,
        "evidence": None,
        "open_questions": _open_questions(state, unique_gaps, extra),
    }


def _evidence_read_model(state: Mapping[str, Any], claim: str) -> dict:
    return {
        "claim_id": _CLAIM_ID,
        "claim_type": claim,
        "analysis": _analysis_evidence(state),
        "sources": _source_evidence(state.get("literature_entries") or []),
        "limitation": _limitation(state, claim),
    }


def build_paper_draft(session_id: str, *, state_facade: Any = None) -> dict:
    """Build and atomically persist one title, six reviewed chapters and references."""
    state_facade = state_facade or facade
    live_state = state_facade.get_state(session_id)
    gaps, claim, verified_entries = _preflight(live_state)
    outline_gap = _outline_gap(live_state)
    if outline_gap:
        gaps.append(outline_gap)
    if gaps:
        return _not_ready(live_state, gaps)

    working = deepcopy(live_state)
    _formal_citation_state(working, verified_entries)
    # paper-draft is a new initial draft. Existing chapter/version history is a
    # different future revision/snapshot concern and must not leak into v1.
    working["body_chapters"] = []
    working["review_feedback"] = []
    working["revision_suggestions"] = [
        _SHORT_DRAFT_INSTRUCTION for _ in _CHAPTER_TYPES
    ]
    working["review_scores"] = []
    working["review_rubrics"] = []
    working["review_iteration"] = 0
    working["review_chapter_index"] = None
    working["current_chapter_index"] = 0
    working.pop("paper_draft_attempts", None)

    try:
        title_result = generate_title_node(working)
    except Exception as exc:
        return _not_ready(
            live_state,
            ["title_generation_failed"],
            [{"code": "title_generation_failed", "message": str(exc), "source": "generate_title", "severity": "error"}],
        )
    title = (title_result or {}).get("title_chapter")
    if not isinstance(title, Mapping) or not str(title.get("title") or "").strip():
        return _not_ready(live_state, ["title_generation_failed"])
    if not _generation_is_authentic(title):
        return _not_ready(
            live_state,
            ["generation_not_authentic"],
            [{
                "code": "generation_not_authentic",
                "message": (
                    f"generation_source={title.get('generation_source')};"
                    f"degraded={title.get('generation_degraded')}"
                ),
                "source": "title",
                "severity": "error",
            }],
        )
    working.update(title_result)

    run_questions: list[dict] = []
    attempt_evidence: list[dict] = []
    for index, expected_type in enumerate(_CHAPTER_TYPES):
        for attempt in range(1, _MAX_CHAPTER_GENERATIONS + 1):
            attempt_state = deepcopy(working)
            attempt_state["current_chapter_index"] = index
            attempt_state["current_chapter"] = None
            try:
                chapter_result = generate_chapter_node(attempt_state)
            except Exception as exc:
                return _not_ready(
                    live_state,
                    ["chapter_generation_failed"],
                    [{"code": "chapter_generation_failed", "message": str(exc), "source": expected_type, "severity": "error"}],
                )
            if not isinstance(chapter_result, Mapping) or chapter_result.get("write_blocked"):
                blockers = list((chapter_result or {}).get("write_blockers") or [])
                return _not_ready(live_state, ["chapter_generation_failed", *blockers])
            attempt_state.update(chapter_result)
            chapters = attempt_state.get("body_chapters") or []
            chapter = chapters[index] if index < len(chapters) else None
            if (
                not isinstance(chapter, Mapping)
                or chapter.get("type") != expected_type
                or not str(chapter.get("content") or "").strip()
            ):
                return _not_ready(live_state, ["chapter_generation_failed"])
            if not _generation_is_authentic(chapter):
                return _not_ready(
                    live_state,
                    ["generation_not_authentic"],
                    [{
                        "code": "generation_not_authentic",
                        "message": (
                            f"generation_source={chapter.get('generation_source')};"
                            f"degraded={chapter.get('generation_degraded')}"
                        ),
                        "source": expected_type,
                        "severity": "error",
                    }],
                )

            invented_numbers = _ungrounded_numbers(attempt_state, chapter)

            try:
                review_result = review_chapter_node(
                    attempt_state,
                    structured_retries=0,
                )
            except Exception as exc:
                return _not_ready(
                    live_state,
                    ["chapter_review_failed"],
                    [{"code": "chapter_review_failed", "message": str(exc), "source": expected_type, "severity": "error"}],
                )
            if not isinstance(review_result, Mapping):
                return _not_ready(live_state, ["chapter_review_failed"])
            if not _review_is_authentic(review_result, index):
                authenticity_gaps = ["chapter_review_not_authentic"]
                if review_result.get("review_degraded"):
                    authenticity_gaps.insert(0, "chapter_review_degraded")
                return _not_ready(live_state, authenticity_gaps)

            scores = review_result.get("review_scores") or attempt_state.get("review_scores") or []
            score = scores[index] if index < len(scores) else None
            if not isinstance(score, (int, float)):
                return _not_ready(live_state, ["chapter_review_failed"])
            grounding = list(review_result.get("grounding_failures") or [])
            if invented_numbers and "invented_number" not in grounding:
                grounding.append("invented_number")
            reviewer_suggestion = _review_suggestion(review_result, index)
            structure = _structure_failures(review_result, reviewer_suggestion)
            repairable_grounding = bool(grounding) and all(
                code in _REPAIRABLE_GROUNDING_FAILURES for code in grounding
            )
            needs_repair = repairable_grounding or bool(structure)
            if grounding and not repairable_grounding:
                return _not_ready(live_state, ["grounding_failure", *grounding])
            if score < REVIEW_SCORE_THRESHOLD and not needs_repair:
                return _not_ready(live_state, ["chapter_review_failed"])
            if needs_repair:
                failures = list(dict.fromkeys([*grounding, *structure]))
                attempt_evidence.append(
                    {
                        "chapter": expected_type,
                        "attempt": attempt,
                        "status": "retry" if attempt < _MAX_CHAPTER_GENERATIONS else "exhausted",
                        "failures": failures,
                        "invented_numbers": invented_numbers,
                        "offending_sentences": _offending_sentences(
                            str(chapter.get("content") or ""), invented_numbers
                        ),
                        "review_source": str(review_result.get("review_source") or ""),
                        "score": score,
                    }
                )
                if attempt == _MAX_CHAPTER_GENERATIONS:
                    detail = _attempt_gap(
                        expected_type,
                        attempt,
                        failures,
                        values=invented_numbers,
                    )
                    gaps = ["chapter_review_failed", detail]
                    if grounding:
                        gaps = ["grounding_failure", *grounding, detail]
                    elif structure:
                        gaps = ["structure_failure", *structure, detail]
                    history = [
                        {
                            "code": f"chapter_retry_attempt_{record['attempt']}",
                            "message": (
                                f"chapter={record['chapter']};attempt={record['attempt']};"
                                f"failures={','.join(record['failures'])};"
                                f"values={','.join(record.get('invented_numbers') or [])}"
                            ),
                            "source": expected_type,
                            "severity": "error",
                        }
                        for record in attempt_evidence
                        if record.get("chapter") == expected_type
                    ]
                    return _not_ready(
                        live_state,
                        gaps,
                        [
                            {
                                "code": "chapter_retry_exhausted",
                                "message": detail,
                                "source": expected_type,
                                "severity": "error",
                            },
                            *history,
                        ],
                    )
                suggestions = list(working.get("revision_suggestions") or [])
                while len(suggestions) < len(_CHAPTER_TYPES):
                    suggestions.append("")
                suggestions[index] = _revision_instruction(
                    attempt_state,
                    chapter,
                    failures=failures,
                    invented_numbers=[
                        value
                        for record in attempt_evidence
                        if record.get("chapter") == expected_type
                        for value in record.get("invented_numbers") or []
                    ],
                    offending_sentences=[
                        sentence
                        for record in attempt_evidence
                        if record.get("chapter") == expected_type
                        for sentence in record.get("offending_sentences") or []
                    ],
                    structure_failures=structure,
                    reviewer_suggestion=reviewer_suggestion,
                )
                working["revision_suggestions"] = suggestions
                continue

            attempt_state.update(review_result)
            attempt_state["current_chapter_index"] = index + 1
            _set_section_review_provenance(
                attempt_state,
                index,
                review_result,
                grounding,
                structure,
            )
            attempt_evidence.append(
                {
                    "chapter": expected_type,
                    "attempt": attempt,
                    "status": "passed",
                    "failures": [],
                    "review_source": str(review_result.get("review_source") or ""),
                    "score": score,
                }
            )
            working = attempt_state
            break

    working["paper_draft_attempts"] = attempt_evidence
    if not _formal_sections_are_authentic(working):
        return _not_ready(live_state, ["section_provenance_incomplete"])

    results_chapter = (working.get("body_chapters") or [])[4]
    treatment_row = str((working.get("estimate") or {}).get("treatment_row") or "")
    if treatment_row not in str(results_chapter.get("content") or ""):
        return _not_ready(live_state, ["results_missing_treatment_row"])

    try:
        references_result = generate_references_node(working)
    except Exception as exc:
        return _not_ready(
            live_state,
            ["references_generation_failed"],
            [{"code": "references_generation_failed", "message": str(exc), "source": "generate_references", "severity": "error"}],
        )
    references = list((references_result or {}).get("references_list") or [])
    if not references:
        return _not_ready(live_state, ["references_missing"])
    working.update(references_result)

    evidence = _evidence_read_model(working, claim)
    main_claim = {
        "id": _CLAIM_ID,
        "text": _claim_text(working, claim),
        "type": claim,
    }
    response = {
        "status": "ready",
        "readiness": "ready",
        "gaps": [],
        "paper": {
            "title": str(working["title_chapter"]["title"]),
            "sections": [dict(chapter) for chapter in working["body_chapters"]],
            "references": references,
        },
        "main_claim": main_claim,
        "evidence": evidence,
        "open_questions": _open_questions(working, [], run_questions),
    }
    state_facade.save_state(session_id, working)
    return response


def get_claim_evidence(
    session_id: str,
    claim_id: str,
    *,
    state_facade: Any = None,
) -> dict:
    """Project the saved main claim from Facade state; no secondary store."""
    if claim_id != _CLAIM_ID:
        raise KeyError(claim_id)
    state_facade = state_facade or facade
    state = state_facade.get_state(session_id)
    chapters = state.get("body_chapters") or []
    sources = state.get("literature_entries") or []
    if (
        len(chapters) != len(_CHAPTER_TYPES)
        or not state.get("references_list")
        or not sources
        or any(
            not isinstance(source, Mapping) or source.get("doi_verified") is not True
            for source in sources
        )
    ):
        raise KeyError(claim_id)
    claim = _effective_claim(state)
    return _evidence_read_model(state, claim)
