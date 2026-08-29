"""ADR-0004 Stage 3: mock 文献库测试。

契约：
1. 文献库 ≥ 30 条
2. 每条含 title/authors/year/abstract/doi/source/relevance_score
3. 覆盖劳动 / 发展 / 公共 / 计量 / 宏观 5 个子领域（每个 ≥ 5 条）
4. DOI 格式合理
5. relevance_score 默认 0.5
6. filter_by_query: 命中关键词返回非空 + 调整分数；空 query 返回全部
"""
from __future__ import annotations

import re

from agent.nodes.literature_sources.mock_corpus import (
    filter_by_query,
    mock_literature_corpus,
)


# ---------------------------------------------------------------------------
# 文献库规模与字段
# ---------------------------------------------------------------------------
def test_corpus_has_at_least_30_entries():
    """Fitness Function: 文献库条目数 >= 30。"""
    entries = mock_literature_corpus()
    assert len(entries) >= 30, f"mock 文献库仅 {len(entries)} 条，需 >= 30"


def test_each_entry_has_required_fields():
    """Fitness Function: 每条文献含 title/authors/year/abstract/doi。"""
    entries = mock_literature_corpus()
    assert len(entries) > 0
    for e in entries:
        assert "title" in e and e["title"], f"缺失 title: {e}"
        assert "authors" in e
        assert isinstance(e["authors"], list)
        assert len(e["authors"]) > 0, f"authors 为空: {e}"
        assert "year" in e
        assert isinstance(e["year"], int)
        assert e["year"] >= 2000, f"year 异常: {e}"
        assert "abstract" in e
        assert e["abstract"], f"abstract 为空: {e}"
        assert "doi" in e
        assert e["doi"], f"doi 为空: {e}"


def test_each_entry_has_source_and_relevance():
    """每条文献含 source 和 relevance_score。"""
    entries = mock_literature_corpus()
    for e in entries:
        assert "source" in e and e["source"] == "mock"
        assert "relevance_score" in e
        assert 0.0 <= e["relevance_score"] <= 1.0


def test_doi_format_reasonable():
    """DOI 格式合理（10.xxxx/... 形式）。"""
    entries = mock_literature_corpus()
    doi_pattern = re.compile(r"^10\.\d{4,9}/[\w.\-]+$")
    for e in entries:
        doi = e["doi"]
        assert doi_pattern.match(doi), f"DOI 格式异常: {doi}"


def test_default_relevance_score_is_0_5():
    """默认 relevance_score = 0.5（filter_by_query 调整前的基线）。"""
    entries = mock_literature_corpus()
    for e in entries:
        assert e["relevance_score"] == 0.5


# ---------------------------------------------------------------------------
# 5 子领域覆盖
# ---------------------------------------------------------------------------
SUBFIELD_KEYWORDS = {
    "labor": ["劳动", "labour", "labor", "wage", "employment", "education"],
    "development": ["发展", "develop", "poverty", "rural", "welfare"],
    "public": ["公共", "tax", "税", "fiscal", "social security", "社保"],
    "econometrics": ["计量", "did", "iv", "rdd", "regression", "synthetic"],
    "macro": ["宏观", "monetary", "fiscal", "inflation", "通胀", "货币政策"],
}


def _matches_subfield(entry, subfield_name: str) -> bool:
    """判断 entry 的 title+abstract 是否含 subfield_name 任一关键词。"""
    text = (entry.get("title", "") + " " + entry.get("abstract", "")).lower()
    kws = SUBFIELD_KEYWORDS[subfield_name]
    return any(kw.lower() in text for kw in kws)


def _classify_subfield(entry) -> str:
    """按 title + abstract 关键词判断子领域（任一命中即归类，可能多归属）。"""
    text = (entry.get("title", "") + " " + entry.get("abstract", "")).lower()
    for name, kws in SUBFIELD_KEYWORDS.items():
        if any(kw.lower() in text for kw in kws):
            return name
    return "unknown"


def test_corpus_covers_5_subfields():
    """覆盖劳动/发展/公共/计量/宏观 5 个子领域，每个 >= 5 条。

    采用"任一关键词命中即计数"（允许同一文献归属多个子领域），
    因为部分文献确实跨子领域（如宏观劳动经济学）。
    """
    entries = mock_literature_corpus()
    for name in SUBFIELD_KEYWORDS:
        count = sum(1 for e in entries if _matches_subfield(e, name))
        assert count >= 5, (
            f"子领域 {name} 仅 {count} 条命中关键词，需 >= 5"
        )


def test_corpus_has_labor_economics_entries():
    """劳动经济学条目存在。"""
    entries = mock_literature_corpus()
    labor = [e for e in entries if _matches_subfield(e, "labor")]
    assert len(labor) >= 5


def test_corpus_has_development_economics_entries():
    """发展经济学条目存在。"""
    entries = mock_literature_corpus()
    dev = [e for e in entries if _matches_subfield(e, "development")]
    assert len(dev) >= 5


def test_corpus_has_public_economics_entries():
    """公共经济学条目存在。"""
    entries = mock_literature_corpus()
    pub = [e for e in entries if _matches_subfield(e, "public")]
    assert len(pub) >= 5


def test_corpus_has_econometrics_entries():
    """计量经济学条目存在。"""
    entries = mock_literature_corpus()
    econ = [e for e in entries if _matches_subfield(e, "econometrics")]
    assert len(econ) >= 5


def test_corpus_has_macro_economics_entries():
    """宏观经济学条目存在。"""
    entries = mock_literature_corpus()
    macro = [e for e in entries if _matches_subfield(e, "macro")]
    assert len(macro) >= 5


# ---------------------------------------------------------------------------
# filter_by_query
# ---------------------------------------------------------------------------
def test_filter_by_query_returns_relevant():
    """filter_by_query 按关键词过滤：劳动 + 教育 命中多条。"""
    entries = mock_literature_corpus()
    filtered = filter_by_query(entries, "劳动 教育")
    assert len(filtered) > 0
    for e in filtered:
        assert e["relevance_score"] >= 0.3
        assert e["relevance_score"] <= 1.0


def test_filter_empty_query_returns_all():
    """空 query 返回全部（不调整 relevance_score）。"""
    entries = mock_literature_corpus()
    filtered = filter_by_query(entries, "")
    assert len(filtered) == len(entries)


def test_filter_none_query_returns_all():
    """None / 空白 query 返回全部。"""
    entries = mock_literature_corpus()
    # filter_by_query 用 if not query 兜底，None 也走该分支
    assert filter_by_query(entries, None) == entries  # type: ignore[arg-type]


def test_filter_relevance_score_formula():
    """filter_by_query 的 relevance_score = min(1.0, 0.3 + 0.2 * match_count)。"""
    entries = mock_literature_corpus()
    # 单关键词命中：match_count=1 → 0.3 + 0.2*1 = 0.5
    filtered = filter_by_query(entries, "劳动经济学")
    assert len(filtered) > 0
    for e in filtered:
        # 单关键词命中 match_count=1 → 0.5
        assert e["relevance_score"] == 0.5


def test_filter_multi_keyword_higher_score():
    """多关键词命中时 relevance_score 高于单关键词。"""
    entries = mock_literature_corpus()
    single = filter_by_query(entries, "劳动")
    multi = filter_by_query(entries, "劳动 教育")
    # 多关键词命中条目应有更高的 relevance_score
    if multi:
        max_multi = max(e["relevance_score"] for e in multi)
        max_single = max(e["relevance_score"] for e in single) if single else 0.0
        assert max_multi >= max_single


def test_filter_multi_keyword_caps_at_1():
    """多关键词命中时 relevance_score 上限 1.0。"""
    entries = mock_literature_corpus()
    # "劳动 教育 IV DID 稳健 政策 自然实验" 7 个关键词，命中越多分数越高
    filtered = filter_by_query(
        entries, "劳动 教育 iv did 稳健 政策 自然实验"
    )
    assert len(filtered) > 0
    for e in filtered:
        assert e["relevance_score"] <= 1.0


def test_filter_no_match_returns_empty():
    """无命中关键词时返回空列表。"""
    entries = mock_literature_corpus()
    # "xyz" 不在任何文献的 title/abstract 中
    filtered = filter_by_query(entries, "xyz")
    assert filtered == []


def test_filter_short_keywords_ignored():
    """长度 <= 1 的关键词被忽略。"""
    entries = mock_literature_corpus()
    # 单字符关键词被过滤，等价于空 query → 返回全部
    filtered = filter_by_query(entries, "a b c")
    # 注意：长度 <= 1 的关键词被跳过，keywords=[]，函数走 entries 分支
    assert len(filtered) == len(entries)


def test_filter_case_insensitive():
    """关键词匹配大小写不敏感。"""
    entries = mock_literature_corpus()
    lower = filter_by_query(entries, "did")
    upper = filter_by_query(entries, "DID")
    # DID 出现在多个 abstract 中（如 DID 双重差分）
    assert len(lower) == len(upper)
    assert len(lower) > 0
