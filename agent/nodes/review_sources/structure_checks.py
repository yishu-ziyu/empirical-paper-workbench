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


def _allowed_indices(citation_indices: Any) -> set[int]:
    allowed: set[int] = set()
    if isinstance(citation_indices, dict):
        for value in citation_indices.values():
            if isinstance(value, int) and not isinstance(value, bool):
                allowed.add(value)
            elif isinstance(value, str) and value.isdigit():
                allowed.add(int(value))
    return allowed


def _invented_citations(content: str, citation_indices: Any) -> List[int]:
    cited = {int(n) for n in _CITE_RE.findall(content or "")}
    if not cited:
        return []
    return sorted(cited - _allowed_indices(citation_indices))


def _citation_table_empty(citation_indices: Any) -> bool:
    return not isinstance(citation_indices, dict) or not citation_indices


_SENTENCE_SPLIT_RE = re.compile(r"[。！？!?\n]")
_YEAR_RE = re.compile(r"\d{4}")


def _index_to_doi(citation_indices: Any) -> dict[int, str]:
    """citation_indices（doi → N）翻转成 N → doi，容错字符串数字。"""
    out: dict[int, str] = {}
    if isinstance(citation_indices, dict):
        for key, value in citation_indices.items():
            if isinstance(value, int) and not isinstance(value, bool):
                out[value] = str(key)
            elif isinstance(value, str) and value.isdigit():
                out[int(value)] = str(key)
    return out


def _entries_by_doi(literature_entries: Any) -> dict[str, dict]:
    """文献条目按 DOI 索引（非 dict / 无 doi 的条目跳过）。"""
    out: dict[str, dict] = {}
    if isinstance(literature_entries, list):
        for e in literature_entries:
            if isinstance(e, dict) and e.get("doi"):
                out[str(e["doi"])] = e
    return out


def _split_sentences(text: str) -> list[tuple[int, int]]:
    """把文本切成句子 span 列表 [(start, end)]（含终止符）。"""
    spans: list[tuple[int, int]] = []
    start = 0
    for m in _SENTENCE_SPLIT_RE.finditer(text):
        spans.append((start, m.end()))
        start = m.end()
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def _sentence_of(pos: int, spans: list[tuple[int, int]]) -> tuple[int, int]:
    """返回包含位置 pos 的句子 span；越界时返回全文首末兜底。"""
    for s, e in spans:
        if s <= pos < e:
            return (s, e)
    return (0, len(text))


def _unattributed_author_year(content: str, citation_indices: Any) -> bool:
    """编号表非空时：作者-年份叙述所在的句子里必须至少有一个合法 [N]。

    表为空时的作者-年份编造由既有空表规则覆盖；这里只管"有表可用却
    不挂编号"的无从核对叙述。
    """
    if _citation_table_empty(citation_indices):
        return False
    text = content or ""
    allowed = _allowed_indices(citation_indices)
    for s, e in _split_sentences(text):
        seg = text[s:e]
        has_author_year = bool(
            _AUTHOR_YEAR_NARRATIVE.search(seg) or _AUTHOR_YEAR_PAREN.search(seg)
        )
        if not has_author_year:
            continue
        has_valid_marker = any(
            s <= m.start() < e and int(m.group(1)) in allowed
            for m in _CITE_RE.finditer(text)
        )
        if not has_valid_marker:
            return True
    return False


def _year_conflict(marker_year: int, entry: Optional[dict]) -> bool:
    """条目缺失时不判定（无从比对）；有条目才严格比年份。"""
    if not isinstance(entry, dict):
        return False
    try:
        return int(entry.get("year")) != marker_year
    except (TypeError, ValueError):
        return False


def _citation_year_mismatches(
    content: str,
    citation_indices: Any,
    literature_entries: Any,
) -> bool:
    """[N] 前紧邻的作者-年份必须与该编号指向的条目元数据一致。

    归属规则：一个作者-年份只归属于其后最近的那个 [N]（处理
    "Lee and Chen (2021) [2][3]" 连续标记），已被消费的年份不再配给后续标记。
    条目表未提供（None）或该编号查不到条目时不判（fail-open 给接地层）。
    """
    n2doi = _index_to_doi(citation_indices)
    if not n2doi:
        return False
    by_doi = _entries_by_doi(literature_entries)
    if not by_doi:
        return False

    text = content or ""
    spans = _split_sentences(text)
    consumed_until = -1
    for m in _CITE_RE.finditer(text):
        idx = int(m.group(1))
        entry = by_doi.get(n2doi.get(idx, ""))
        if not isinstance(entry, dict):
            continue
        s, e = _sentence_of(m.start(), spans)
        # 只看本句内、位于 [N] 之前、且未被更早标记消费掉的作者-年份
        candidates = [
            am
            for am in _AUTHOR_YEAR_NARRATIVE.finditer(text, s, m.start())
            if am.end() > consumed_until
        ] + [
            am
            for am in _AUTHOR_YEAR_PAREN.finditer(text, s, m.start())
            if am.end() > consumed_until
        ]
        if not candidates:
            continue
        chosen = max(candidates, key=lambda am: am.start())
        ym = _YEAR_RE.search(chosen.group(0))
        consumed_until = chosen.end()
        if ym and _year_conflict(int(ym.group(0)), entry):
            return True
    return False


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
    literature_entries: Any = None,
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
        unattributed = _unattributed_author_year(content or "", citation_indices)
        if invented or unattributed or (
            _citation_table_empty(citation_indices)
            and _has_author_year_citation(content or "")
        ):
            failures.append("invented_citation")
        if _citation_year_mismatches(
            content or "", citation_indices, literature_entries
        ):
            failures.append("citation_year_mismatch")

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
