"""ADR-0004 Stage 2/4: search_literature 节点测试。"""
import pytest

from nodes.search_literature import (
    MAX_LITERATURE_ENTRIES,
    _build_query,
    _mock_search,
    resolve_literature_source,
    search_literature,
)


def test_search_returns_literature_output():
    """正常检索返回 LiteratureOutput。"""
    state = {"research_direction": "劳动经济学", "title_chapter": {"title": "教育回报"}}
    result = search_literature(state)
    assert "literature_entries" in result
    assert "literature_query" in result
    assert "literature_source" in result
    assert result["literature_produced_by"] == "search_literature"


def test_search_query_built_from_direction_not_title():
    """查询串只由研究方向派生，不拼标题。"""
    state = {"research_direction": "劳动经济学", "title_chapter": {"title": "教育回报"}}
    result = search_literature(state)
    assert "劳动经济学" in result["literature_query"]
    assert "教育回报" not in result["literature_query"]


def test_search_disabled_returns_empty():
    """literature_source=disabled 返回空列表。"""
    state = {"research_direction": "test", "literature_source": "disabled"}
    result = search_literature(state)
    assert result["literature_entries"] == []
    assert result["literature_source"] == "disabled"


def test_search_limit_length(monkeypatch):
    """文献条目数 <= 20（Fitness Function）。"""

    def fake_mock_search(query):
        return [
            {"title": f"Paper {i}", "doi": f"10.1000/p{i}"}
            for i in range(30)
        ]

    monkeypatch.setattr(
        "nodes.search_literature._mock_search", fake_mock_search
    )
    state = {"research_direction": "test"}
    result = search_literature(state)
    assert len(result["literature_entries"]) == MAX_LITERATURE_ENTRIES
    assert len(result["literature_entries"]) <= 20


def test_search_dedup_by_doi(monkeypatch):
    """按 doi 去重。"""

    def fake_mock_search(query):
        return [
            {"title": "Paper A", "doi": "10.1000/aaa"},
            {"title": "Paper A duplicate", "doi": "10.1000/aaa"},
            {"title": "Paper B", "doi": "10.1000/bbb"},
            {"title": "Paper C"},  # 无 doi，按 title 去重
            {"title": "Paper C"},  # 无 doi，按 title 去重
        ]

    monkeypatch.setattr(
        "nodes.search_literature._mock_search", fake_mock_search
    )
    state = {"research_direction": "test"}
    result = search_literature(state)
    titles = [e["title"] for e in result["literature_entries"]]
    assert "Paper A" in titles
    assert "Paper A duplicate" not in titles
    assert "Paper B" in titles
    # 无 doi 但同 title 的应去重为一个
    assert titles.count("Paper C") == 1


def test_search_empty_state_defaults():
    """state 为空时用默认查询。"""
    result = search_literature({})
    assert result["literature_query"]  # 不为空
    assert result["literature_source"] == "mock"


def test_each_entry_has_required_fields():
    """每条文献含 title/authors/year/abstract/doi（Fitness Function）。

    Stage 3：遍历 mock 文献库，断言每条含全部必需字段。
    """
    from nodes.literature_sources.mock_corpus import mock_literature_corpus

    entries = mock_literature_corpus()
    assert len(entries) > 0, "mock 文献库不应为空"
    for e in entries:
        assert "title" in e and e["title"], f"缺失 title: {e}"
        assert "authors" in e and isinstance(e["authors"], list) and e["authors"]
        assert "year" in e and isinstance(e["year"], int)
        assert "abstract" in e and e["abstract"]
        assert "doi" in e and e["doi"]  # mock 文献库所有条目都应有 doi


def test_build_query_str_direction():
    """_build_query: research_direction 为 str 时直接使用，忽略标题。"""
    q = _build_query("劳动经济学", "教育回报")
    assert "劳动经济学" in q
    assert "教育回报" not in q


def test_build_query_dict_direction():
    """_build_query: research_direction 为 dict 时取 question/method 字段。"""
    rd = {"question": "教育对收入的影响", "method": "OLS"}
    q = _build_query(rd, "教育回报")
    assert "教育对收入的影响" in q
    assert "OLS" in q
    assert "教育回报" not in q


def test_build_query_defaults_to_economics():
    """_build_query: 无可用输入时默认 'economics'。"""
    assert _build_query("", "") == "economics"
    assert _build_query(None, "") == "economics"


def test_mock_search_no_match_returns_empty():
    """Stage 3: _mock_search 对未命中的查询返回空列表。"""
    # mock 文献库为英文标题 + 中文摘要，"any query" 不命中任何条目
    assert _mock_search("any query") == []


def test_mock_search_match_returns_non_empty():
    """Stage 3: _mock_search 对命中的查询返回非空列表。"""
    entries = _mock_search("劳动 教育")
    assert len(entries) > 0
    for e in entries:
        assert "title" in e and e["title"]
        assert "doi" in e


# ---------------------------------------------------------------------------
# ADR-0004 Stage 4: semantic_scholar 分发与降级
# ---------------------------------------------------------------------------
def test_search_literature_semantic_scholar_with_api_key(monkeypatch):
    """literature_source=semantic_scholar 且有 API key 时调真实 API。"""
    fake_entries = [
        {
            "title": "Real Paper",
            "authors": ["Author A"],
            "year": 2023,
            "abstract": "Real abstract",
            "doi": "10.1234/real.001",
            "source": "semantic_scholar",
            "relevance_score": 1.0,
        }
    ]

    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.get_api_key_from_env",
        lambda: "real_key_123",
    )
    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.semantic_scholar_search",
        lambda query, api_key, **kwargs: fake_entries,
    )

    state = {"research_direction": "test", "literature_source": "semantic_scholar"}
    result = search_literature(state)

    assert result["literature_source"] == "semantic_scholar"
    assert len(result["literature_entries"]) == 1
    assert result["literature_entries"][0]["title"] == "Real Paper"
    assert result["literature_entries"][0]["source"] == "semantic_scholar"


def test_search_literature_semantic_scholar_without_api_key_degrades(monkeypatch):
    """literature_source=semantic_scholar 但无 API key 时降级为 mock_degraded。"""
    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.get_api_key_from_env",
        lambda: None,
    )
    # semantic_scholar_search 不应被调用
    def _fail_if_called(*args, **kwargs):
        raise AssertionError("semantic_scholar_search 不应在无 API key 时被调用")

    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.semantic_scholar_search",
        _fail_if_called,
    )

    state = {
        "research_direction": "劳动 教育",
        "literature_source": "semantic_scholar",
    }
    result = search_literature(state)

    assert result["literature_source"] == "mock_degraded"
    # 降级后用 mock 文献库，"劳动 教育" 命中条目
    assert isinstance(result["literature_entries"], list)


def test_search_literature_semantic_scholar_empty_api_key_degrades(monkeypatch):
    """literature_source=semantic_scholar 但 API key 为空字符串时降级。"""
    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.get_api_key_from_env",
        lambda: "",
    )

    state = {
        "research_direction": "劳动 教育",
        "literature_source": "semantic_scholar",
    }
    result = search_literature(state)

    assert result["literature_source"] == "mock_degraded"


def test_search_literature_semantic_scholar_api_error_degrades(monkeypatch):
    """API 调用失败（RuntimeError）时降级为 mock_degraded。"""
    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.get_api_key_from_env",
        lambda: "real_key_123",
    )

    def _raise_runtime_error(*args, **kwargs):
        raise RuntimeError("Semantic Scholar API 调用失败: network error")

    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.semantic_scholar_search",
        _raise_runtime_error,
    )

    state = {
        "research_direction": "劳动 教育",
        "literature_source": "semantic_scholar",
    }
    result = search_literature(state)

    assert result["literature_source"] == "mock_degraded"
    # 降级后用 mock 文献库，仍有条目
    assert isinstance(result["literature_entries"], list)


def test_search_literature_semantic_scholar_with_api_key_dedup(monkeypatch):
    """semantic_scholar 路径也走去重逻辑。"""
    fake_entries = [
        {
            "title": "Paper A",
            "authors": ["A"],
            "year": 2023,
            "abstract": "",
            "doi": "10.1000/aaa",
            "source": "semantic_scholar",
            "relevance_score": 1.0,
        },
        {
            "title": "Paper A duplicate",
            "authors": ["B"],
            "year": 2022,
            "abstract": "",
            "doi": "10.1000/aaa",  # 同 DOI 应被去重
            "source": "semantic_scholar",
            "relevance_score": 0.9,
        },
        {
            "title": "Paper B",
            "authors": ["C"],
            "year": 2021,
            "abstract": "",
            "doi": "10.1000/bbb",
            "source": "semantic_scholar",
            "relevance_score": 0.8,
        },
    ]

    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.get_api_key_from_env",
        lambda: "real_key_123",
    )
    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.semantic_scholar_search",
        lambda query, api_key, **kwargs: fake_entries,
    )

    state = {"research_direction": "test", "literature_source": "semantic_scholar"}
    result = search_literature(state)

    assert result["literature_source"] == "semantic_scholar"
    titles = [e["title"] for e in result["literature_entries"]]
    assert "Paper A" in titles
    assert "Paper A duplicate" not in titles
    assert "Paper B" in titles


def test_search_literature_semantic_scholar_with_api_key_limit(monkeypatch):
    """semantic_scholar 路径也走限长逻辑（<= MAX_LITERATURE_ENTRIES）。"""
    fake_entries = [
        {
            "title": f"Paper {i}",
            "authors": [],
            "year": 2023,
            "abstract": "",
            "doi": f"10.1000/p{i}",
            "source": "semantic_scholar",
            "relevance_score": 0.5,
        }
        for i in range(30)
    ]

    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.get_api_key_from_env",
        lambda: "real_key_123",
    )
    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.semantic_scholar_search",
        lambda query, api_key, **kwargs: fake_entries,
    )

    state = {"research_direction": "test", "literature_source": "semantic_scholar"}
    result = search_literature(state)

    assert len(result["literature_entries"]) == MAX_LITERATURE_ENTRIES
    assert len(result["literature_entries"]) <= 20


def test_search_literature_semantic_scholar_propagates_query(monkeypatch):
    """semantic_scholar 路径正确派生 literature_query。"""
    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.get_api_key_from_env",
        lambda: "real_key_123",
    )
    monkeypatch.setattr(
        "nodes.literature_sources.semantic_scholar.semantic_scholar_search",
        lambda query, api_key, **kwargs: [],
    )

    state = {
        "research_direction": "劳动经济学",
        "title_chapter": {"title": "教育回报"},
        "literature_source": "semantic_scholar",
    }
    result = search_literature(state)

    assert "劳动经济学" in result["literature_query"]
    assert "教育回报" not in result["literature_query"]
    assert result["literature_source"] == "semantic_scholar"


def test_search_literature_mock_default_unchanged():
    """pytest 下默认仍 mock，不打真网。"""
    state = {"research_direction": "劳动 教育"}
    result = search_literature(state)

    assert result["literature_source"] == "mock"
    assert isinstance(result["literature_entries"], list)
    # mock 路径条目 source 应为 "mock"
    for e in result["literature_entries"]:
        assert e["source"] == "mock"


def test_pytest_default_does_not_call_crossref(monkeypatch):
    """pytest 默认路径不得调用 crossref_search。"""

    def _boom(*args, **kwargs):
        raise AssertionError("crossref must not be called under pytest default")

    monkeypatch.setattr(
        "nodes.literature_sources.crossref.crossref_search",
        _boom,
    )
    result = search_literature({"research_direction": "劳动 教育"})
    assert result["literature_source"] == "mock"


def test_pytest_ignores_literature_source_env(monkeypatch):
    """pytest 优先于 LITERATURE_SOURCE，避免本地 env 把测试打到真网。"""
    monkeypatch.setenv("LITERATURE_SOURCE", "crossref")

    def _boom(*args, **kwargs):
        raise AssertionError("crossref must not be called under pytest")

    monkeypatch.setattr(
        "nodes.literature_sources.crossref.crossref_search",
        _boom,
    )
    assert resolve_literature_source({}) == "mock"
    result = search_literature({"research_direction": "劳动 教育"})
    assert result["literature_source"] == "mock"


def test_resolve_runtime_last_resort_is_crossref(monkeypatch):
    """运行时最后一档是 crossref，不是 mock。"""
    monkeypatch.setattr("llm.ssot.in_pytest", lambda: False)
    monkeypatch.delenv("LITERATURE_SOURCE", raising=False)
    monkeypatch.delenv("ECONPAPER_LLM", raising=False)
    assert resolve_literature_source({}) == "crossref"
    assert resolve_literature_source({"literature_source": ""}) == "crossref"
    assert resolve_literature_source({"literature_source": None}) == "crossref"


def test_resolve_econpaper_llm_mock_even_outside_pytest(monkeypatch):
    monkeypatch.setattr("llm.ssot.in_pytest", lambda: False)
    monkeypatch.setenv("ECONPAPER_LLM", "mock")
    monkeypatch.delenv("LITERATURE_SOURCE", raising=False)
    assert resolve_literature_source({}) == "mock"


def test_resolve_literature_source_env_outside_pytest(monkeypatch):
    monkeypatch.setattr("llm.ssot.in_pytest", lambda: False)
    monkeypatch.setenv("LITERATURE_SOURCE", "semantic_scholar")
    monkeypatch.delenv("ECONPAPER_LLM", raising=False)
    assert resolve_literature_source({}) == "semantic_scholar"


def test_resolve_explicit_state_wins(monkeypatch):
    monkeypatch.setattr("llm.ssot.in_pytest", lambda: False)
    monkeypatch.setenv("LITERATURE_SOURCE", "crossref")
    monkeypatch.delenv("ECONPAPER_LLM", raising=False)
    assert resolve_literature_source({"literature_source": "disabled"}) == "disabled"


def test_runtime_crossref_failure_is_mock_degraded(monkeypatch):
    """运行时默认走 Crossref；失败必须 mock_degraded，不能假装成功。"""
    monkeypatch.setattr("llm.ssot.in_pytest", lambda: False)
    monkeypatch.delenv("LITERATURE_SOURCE", raising=False)
    monkeypatch.delenv("ECONPAPER_LLM", raising=False)

    def _boom(query, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(
        "nodes.literature_sources.crossref.crossref_search",
        _boom,
    )
    result = search_literature({"research_direction": "劳动 教育"})
    assert result["literature_source"] == "mock_degraded"
    assert result["literature_source"] != "crossref"
    assert result["literature_produced_by"] == "search_literature"
    assert result["literature_entries"]
    for e in result["literature_entries"]:
        assert e["source"] == "mock"


def test_search_literature_disabled_still_works():
    """Stage 4 后 disabled 路径保持原行为（回归测试）。"""
    state = {"research_direction": "test", "literature_source": "disabled"}
    result = search_literature(state)
    assert result["literature_entries"] == []
    assert result["literature_source"] == "disabled"


# ---------------------------------------------------------------------------
# #8 方法锚 + 反证跳
# ---------------------------------------------------------------------------
CALLAWAY_DOI = "10.1016/j.jeconom.2022.019"
STOCK_YOGO_DOI = "10.1016/j.jeconom.2021.020"
LEE_LEMIEUX_DOI = "10.1016/j.jeconom.2020.021"


def _unrelated_hits(n: int = 1):
    return [
        {
            "title": f"Unrelated {i}",
            "authors": ["A"],
            "year": 2020,
            "abstract": " unrelated ",
            "doi": f"10.1/u{i}",
            "source": "mock",
            "relevance_score": 0.5,
        }
        for i in range(n)
    ]


def test_did_session_includes_callaway_anchor(monkeypatch):
    """DID 方向即使词袋没命中，也要塞 Callaway–Sant'Anna。"""

    monkeypatch.setattr(
        "nodes.search_literature._mock_search", lambda query: _unrelated_hits()
    )
    result = search_literature(
        {"research_direction": {"question": "养老金", "method": "DID"}}
    )
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert CALLAWAY_DOI in dois
    assert len(result["literature_entries"]) <= MAX_LITERATURE_ENTRIES


def test_iv_session_includes_stock_yogo_anchor(monkeypatch):
    monkeypatch.setattr(
        "nodes.search_literature._mock_search", lambda query: _unrelated_hits()
    )
    result = search_literature(
        {"research_direction": {"question": "教育回报", "method": "IV"}}
    )
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert STOCK_YOGO_DOI in dois


def test_rdd_session_includes_lee_lemieux_anchor(monkeypatch):
    monkeypatch.setattr(
        "nodes.search_literature._mock_search", lambda query: _unrelated_hits()
    )
    result = search_literature(
        {"research_direction": {"question": "高考分数", "method": "RDD"}}
    )
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert LEE_LEMIEUX_DOI in dois


def test_chinese_did_alias_includes_anchor(monkeypatch):
    monkeypatch.setattr(
        "nodes.search_literature._mock_search", lambda query: _unrelated_hits()
    )
    result = search_literature(
        {"research_direction": {"question": "医保", "method": "双重差分"}}
    )
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert CALLAWAY_DOI in dois


def test_threat_hop_adds_counterexample_paper(monkeypatch):
    """反证跳会把「该方法的威胁」那条加进来，不覆盖方法锚。"""

    def fake(query: str):
        if "交错" in query:
            return [
                {
                    "title": "Staggered treatment bias",
                    "authors": ["X"],
                    "year": 2021,
                    "abstract": "交错 DID 威胁",
                    "doi": "10.9/threat",
                    "source": "mock",
                    "relevance_score": 0.6,
                }
            ]
        return _unrelated_hits()

    monkeypatch.setattr("nodes.search_literature._mock_search", fake)
    result = search_literature(
        {"research_direction": {"question": "养老金", "method": "DID"}}
    )
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert CALLAWAY_DOI in dois
    assert "10.9/threat" in dois
    assert "10.1/u0" in dois


def test_anchor_survives_when_l0_already_full(monkeypatch):
    """L0 已有 20 条时，方法锚仍在，总长仍 <= 20。"""

    monkeypatch.setattr(
        "nodes.search_literature._mock_search", lambda query: _unrelated_hits(20)
    )
    result = search_literature(
        {"research_direction": {"question": "养老金", "method": "DID"}}
    )
    entries = result["literature_entries"]
    dois = [e.get("doi") for e in entries]
    assert CALLAWAY_DOI in dois
    assert len(entries) == MAX_LITERATURE_ENTRIES
    assert len(entries) <= 20


def test_no_method_skips_anchor_hop(monkeypatch):
    monkeypatch.setattr(
        "nodes.search_literature._mock_search", lambda query: _unrelated_hits()
    )
    result = search_literature({"research_direction": {"question": "养老金"}})
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert CALLAWAY_DOI not in dois
    assert dois == ["10.1/u0"]

