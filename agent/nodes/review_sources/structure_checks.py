"""评审结构层：词面只是先验，结构失败封顶 0.65。

纯规则，不调 LLM。methods 要方程；association 不要识别假设菜单。
lit_review 的 [N] 必须落在 citation_indices；编号表为空时作者-年份也算编造。
results 的 method 必须与 methods 章一致。
"""
from __future__ import annotations

import re
from typing import Any, Iterable, List, Optional

STRUCTURE_SCORE_CAP = 0.65

_UNSET = object()

# 按识别策略选假设菜单。命中 ≥2 条才算结构过。
_HYPOTHESIS_MENUS: dict[str, List[str]] = {
    "did": ["平行趋势", "parallel trend", "sutva", "无预期效应", "no anticipation"],
    "双重差分": ["平行趋势", "parallel trend", "sutva", "无预期效应", "no anticipation"],
    "iv": ["外生性", "排除限制", "exclusion", "exogen", "相关性", "relevance"],
    "工具变量": ["外生性", "排除限制", "exclusion", "exogen", "相关性", "relevance"],
    "rdd": ["不可操纵", "连续性", "local random", "断点"],
    "断点": ["不可操纵", "连续性", "local random", "断点"],
}

_DEFAULT_HYPOTHESES = ["外生性", "sutva", "识别假设", "exclusion", "平行趋势"]

_EQUATION_RE = re.compile(r"\$[^$]+\$")
_CITE_RE = re.compile(r"\[(\d+)\]")
# Name (2020) / Name and Name (2020) / 张三 (2020)
_AUTHOR_YEAR_NARRATIVE = re.compile(
    r"(?:[A-Z][A-Za-z.\-']*(?:\s+and\s+[A-Z][A-Za-z.\-']*)*"
    r"|[\u4e00-\u9fff]{1,8})\s*\(\d{4}\)"
)
# (Author, 2020) / （张三, 2020）
_AUTHOR_YEAR_PAREN = re.compile(
    r"[（(](?:[A-Z][A-Za-z.\-']+|[\u4e00-\u9fff]{1,8})[,，]\s*\d{4}[)）]"
)


def _normalize_method(method: str) -> str:
    return (method or "").strip().lower()


def hypothesis_menu(method: str) -> List[str]:
    """按 method 选假设菜单；未知方法退回通用清单。"""
    key = _normalize_method(method)
    if not key:
        return list(_DEFAULT_HYPOTHESES)
    for name, menu in _HYPOTHESIS_MENUS.items():
        if name in key:
            return list(menu)
    return list(_DEFAULT_HYPOTHESES)


def _count_hypothesis_hits(content: str, menu: Iterable[str]) -> int:
    text = (content or "").lower()
    return sum(1 for item in menu if item.lower() in text)


def _invented_citations(content: str, citation_indices: Any) -> List[int]:
    cited = {int(n) for n in _CITE_RE.findall(content or "")}
    if not cited:
        return []
    allowed: set[int] = set()
    if isinstance(citation_indices, dict):
        for value in citation_indices.values():
            if isinstance(value, int):
                allowed.add(value)
            elif isinstance(value, str) and value.isdigit():
                allowed.add(int(value))
    return sorted(cited - allowed)


def _citation_table_empty(citation_indices: Any) -> bool:
    return not isinstance(citation_indices, dict) or not citation_indices


def _has_author_year_citation(content: str) -> bool:
    text = content or ""
    return bool(
        _AUTHOR_YEAR_NARRATIVE.search(text) or _AUTHOR_YEAR_PAREN.search(text)
    )


def _effective_claim(claim: str, star_rating: Any) -> str:
    """association skips the identification-assumption menu.

    Default (claim omitted, star not passed) stays causal_with_caveat so old
    tests still require hypotheses. Explicit star_rating=None is association,
    including DiD that never received a star.
    """
    claim_l = str(claim or "").strip().lower()
    if claim_l in {"association", "assoc", "correlation"}:
        return "association"
    if claim_l == "causal_with_caveat":
        return "causal_with_caveat"
    if star_rating is not _UNSET and star_rating is None:
        return "association"
    return "causal_with_caveat"


def check_structure(
    chapter_type: str,
    content: str,
    *,
    method: str = "",
    methods_method: str = "",
    citation_indices: Any = None,
    claim: str = "",
    star_rating: Any = _UNSET,
) -> List[str]:
    """返回结构失败码。空列表 = 结构过关。"""
    failures: List[str] = []
    kind = (chapter_type or "").strip()

    if kind == "methods":
        if not _EQUATION_RE.search(content or ""):
            failures.append("missing_equation")
        if _effective_claim(claim, star_rating) != "association":
            menu = hypothesis_menu(method)
            if _count_hypothesis_hits(content or "", menu) < 2:
                failures.append("missing_ident_assumptions")

    if kind == "lit_review":
        invented = _invented_citations(content or "", citation_indices)
        if invented or (
            _citation_table_empty(citation_indices)
            and _has_author_year_citation(content or "")
        ):
            failures.append("invented_citation")

    if kind == "results":
        expected = _normalize_method(methods_method) or _normalize_method(method)
        actual = _normalize_method(method)
        if methods_method and actual and expected != actual:
            failures.append("method_mismatch")
        if expected and expected not in (content or "").lower():
            failures.append("method_not_in_results")

    return failures


def apply_structure_cap(score: float, failures: Optional[List[str]]) -> float:
    """任一项结构失败：综合分上限 0.65。"""
    if failures:
        return min(float(score), STRUCTURE_SCORE_CAP)
    return float(score)
