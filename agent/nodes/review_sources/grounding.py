"""结果章数字接地：主估计行必须在正文，不得另造处理系数。

纯函数，不调 LLM，不读 identification_diag.report。
"""
from __future__ import annotations

import re
from typing import Iterable, List, Set

COEF_TOL = 1e-4

# | <label> | <float> |
_ROW_RE = re.compile(
    r"\|\s*([^|\n]+?)\s*\|\s*"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*\|"
)

_HEADER_RE = re.compile(
    r"\|\s*变量\s*\|\s*系数\s*\|\s*SE\s*\|\s*p\s*\|",
    re.IGNORECASE,
)

_FIXED_TREATMENT_LABELS = frozenset({"att", "rd", "scm_gap"})
_TREATMENT_ALIASES = frozenset({"treat", "treatment"})


def check_grounding(state: dict, content: str) -> list[str]:
    """Return zero or more of:
    missing_estimate_number, invented_number, invented_table,
    wording_exceeds_evidence
    """
    text = content or ""
    failures: List[str] = []
    payload = state if isinstance(state, dict) else {}
    if _wording_exceeds_evidence(payload, text):
        failures.append("wording_exceeds_evidence")

    estimate = payload.get("estimate") if isinstance(payload, dict) else None
    if not isinstance(estimate, dict):
        return failures
    treatment_row = estimate.get("treatment_row")
    if not isinstance(treatment_row, str) or not treatment_row:
        return failures

    if treatment_row not in text:
        failures.append("missing_estimate_number")

    if estimate.get("status") == "ok":
        if _has_invented_treatment_number(estimate, text):
            failures.append("invented_number")
        if _count_result_headers(text) >= 2:
            failures.append("invented_table")
    return failures


def _wording_exceeds_evidence(state: dict, text: str) -> bool:
    from agent.engine.claim_wording import wording_exceeds_evidence
    from agent.engine.readiness import current_research_claim

    claim = current_research_claim(state if isinstance(state, dict) else {})
    return wording_exceeds_evidence(claim, text)


def _norm_label(label: str) -> str:
    return " ".join((label or "").strip().lower().split())


def _treatment_labels(estimate: dict) -> Set[str]:
    labels = set(_FIXED_TREATMENT_LABELS)
    treatment = _norm_label(str(estimate.get("treatment") or ""))
    if treatment:
        labels.add(treatment)
        labels.update(_TREATMENT_ALIASES)
    return labels


def _parse_coef(estimate: dict) -> float | None:
    try:
        return float(estimate.get("coef"))
    except (TypeError, ValueError):
        return None


def _iter_labeled_floats(text: str) -> Iterable[tuple[str, float]]:
    for match in _ROW_RE.finditer(text or ""):
        raw_label, raw_value = match.group(1), match.group(2)
        if re.fullmatch(r"[-: ]+", raw_label or ""):
            continue
        try:
            value = float(raw_value)
        except ValueError:
            continue
        yield raw_label, value


def _has_invented_treatment_number(estimate: dict, text: str) -> bool:
    coef = _parse_coef(estimate)
    if coef is None:
        return False
    labels = _treatment_labels(estimate)
    if not labels:
        return False
    for raw_label, value in _iter_labeled_floats(text):
        if _norm_label(raw_label) not in labels:
            continue
        if abs(value - coef) > COEF_TOL:
            return True
    return False


def _count_result_headers(text: str) -> int:
    return len(_HEADER_RE.findall(text or ""))
