"""ADR-0004 Stage 4: Semantic Scholar API 客户端测试。

契约：
1. 所有测试 mock urllib.request.urlopen，不真发 HTTP 请求
2. 正常调用返回 LiteratureEntry 列表（含全部必需字段）
3. 空 query 返回空列表
4. 无 api_key 也能调用（受 rate limit，但函数不强制）
5. API 调用失败抛 RuntimeError
6. relevance_score 按返回顺序递减（最低 0.3）
7. DOI 可能为 None（externalIds 里不一定有 DOI）
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from agent.nodes.literature_sources.semantic_scholar import (
    MAX_RESULTS,
    SEMANTIC_SCHOLAR_BASE,
    get_api_key_from_env,
    semantic_scholar_search,
)


def _mock_api_response(papers):
    """构造 Semantic Scholar API 响应 JSON。"""
    return {"total": len(papers), "data": papers, "offset": 0}


def _make_mock_urlopen(payload: dict):
    """构造 mock urlopen context manager，返回指定 payload。"""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(payload).encode("utf-8")
    mock_resp.__enter__ = lambda self: self
    mock_resp.__exit__ = lambda *args: None
    return mock_resp


# ---------------------------------------------------------------------------
# 正常调用
# ---------------------------------------------------------------------------
def test_search_returns_entries():
    """正常调用返回 LiteratureEntry 列表。"""
    mock_papers = [
        {
            "paperId": "p1",
            "title": "Test Paper 1",
            "authors": [{"name": "Author A"}, {"name": "Author B"}],
            "year": 2023,
            "abstract": "Abstract 1",
            "externalIds": {"DOI": "10.1234/test.001"},
        },
        {
            "paperId": "p2",
            "title": "Test Paper 2",
            "authors": [{"name": "Author C"}],
            "year": 2022,
            "abstract": "Abstract 2",
            "externalIds": {},
        },
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )

        result = semantic_scholar_search("test query", api_key="fake_key")

    assert len(result) == 2
    assert result[0]["title"] == "Test Paper 1"
    assert result[0]["authors"] == ["Author A", "Author B"]
    assert result[0]["year"] == 2023
    assert result[0]["abstract"] == "Abstract 1"
    assert result[0]["doi"] == "10.1234/test.001"
    assert result[0]["source"] == "semantic_scholar"
    assert result[0]["relevance_score"] >= 0.3

    # 第二条无 DOI
    assert result[1]["doi"] is None
    assert result[1]["title"] == "Test Paper 2"


def _get_header_case_insensitive(req, name: str):
    """从 urllib Request 取 header（大小写不敏感）。urllib 会 title-case 化 key。"""
    name_lower = name.lower()
    for k, v in req.headers.items():
        if k.lower() == name_lower:
            return v
    return None


def test_search_passes_api_key_header():
    """有 api_key 时请求头含 x-api-key。"""
    mock_papers = []
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )

        semantic_scholar_search("query", api_key="secret_key_123")

    # 检查 Request 对象的 headers（urllib title-case 化 key：X-api-key）
    call_args = mock_urlopen.call_args
    req = call_args[0][0]
    assert _get_header_case_insensitive(req, "x-api-key") == "secret_key_123"
    assert _get_header_case_insensitive(req, "Accept") == "application/json"


def test_search_url_contains_query_and_fields():
    """请求 URL 含 query/limit/fields 参数。"""
    mock_papers = []
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )

        semantic_scholar_search("labor economics", api_key="k", max_results=10)

    call_args = mock_urlopen.call_args
    req = call_args[0][0]
    url = req.full_url
    assert SEMANTIC_SCHOLAR_BASE in url
    assert "query=labor+economics" in url
    assert "limit=10" in url
    assert "fields=" in url


# ---------------------------------------------------------------------------
# 边界情况
# ---------------------------------------------------------------------------
def test_search_empty_query_returns_empty():
    """空 query 返回空列表（不调 API）。"""
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        result = semantic_scholar_search("")
        assert result == []
        mock_urlopen.assert_not_called()


def test_search_whitespace_query_returns_empty():
    """纯空白 query 返回空列表。"""
    result = semantic_scholar_search("   ")
    assert result == []


def test_search_no_api_key_works():
    """无 api_key 也能调用（受 rate limit，但函数不强制）。"""
    mock_papers = [
        {
            "paperId": "p1",
            "title": "T",
            "authors": [],
            "year": 2023,
            "abstract": "",
            "externalIds": {},
        }
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )

        result = semantic_scholar_search("query", api_key=None)

    assert len(result) == 1
    # 检查请求头不含 x-api-key（大小写不敏感）
    call_args = mock_urlopen.call_args
    req = call_args[0][0]
    assert _get_header_case_insensitive(req, "x-api-key") is None


def test_search_max_results_capped_at_max():
    """max_results 超过 MAX_RESULTS 时被截断为 MAX_RESULTS。"""
    mock_papers = []
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )

        semantic_scholar_search("query", api_key="k", max_results=100)

    call_args = mock_urlopen.call_args
    req = call_args[0][0]
    url = req.full_url
    # limit 参数被截断为 MAX_RESULTS（20）
    assert f"limit={MAX_RESULTS}" in url


# ---------------------------------------------------------------------------
# 错误处理
# ---------------------------------------------------------------------------
def test_search_api_error_raises_runtime_error():
    """API 调用失败（网络错误）抛 RuntimeError。"""
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen",
        side_effect=Exception("network error"),
    ):
        with pytest.raises(RuntimeError, match="Semantic Scholar API"):
            semantic_scholar_search("query")


def test_search_http_error_raises_runtime_error():
    """HTTP 错误（如 429 rate limit）抛 RuntimeError。"""
    import urllib.error

    http_err = urllib.error.HTTPError(
        url="https://example.com",
        code=429,
        msg="Too Many Requests",
        hdrs=None,
        fp=None,
    )
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen",
        side_effect=http_err,
    ):
        with pytest.raises(RuntimeError, match="Semantic Scholar API"):
            semantic_scholar_search("query")


def test_search_json_decode_error_raises_runtime_error():
    """响应非 JSON 时抛 RuntimeError。"""
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"not valid json"
    mock_resp.__enter__ = lambda self: self
    mock_resp.__exit__ = lambda *args: None
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen",
        return_value=mock_resp,
    ):
        with pytest.raises(RuntimeError, match="Semantic Scholar API"):
            semantic_scholar_search("query")


def test_search_empty_data_returns_empty():
    """API 返回空 data 列表时返回空。"""
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            {"total": 0, "data": []}
        )
        result = semantic_scholar_search("query")
    assert result == []


def test_search_missing_data_key_returns_empty():
    """API 响应缺少 data 键时返回空。"""
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen({"total": 0})
        result = semantic_scholar_search("query")
    assert result == []


# ---------------------------------------------------------------------------
# relevance_score 递减
# ---------------------------------------------------------------------------
def test_relevance_score_decreasing():
    """relevance_score 按返回顺序递减。"""
    mock_papers = [
        {
            "paperId": f"p{i}",
            "title": f"T{i}",
            "authors": [],
            "year": 2023,
            "abstract": "",
            "externalIds": {},
        }
        for i in range(5)
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )
        result = semantic_scholar_search("query")

    scores = [e["relevance_score"] for e in result]
    assert scores[0] > scores[-1]
    # 第一个 1.0，第二个 0.95，...
    assert scores[0] == 1.0
    assert scores[1] == 0.95
    assert all(s >= 0.3 for s in scores)


def test_relevance_score_floor_0_3():
    """relevance_score 最低 0.3（超过 14 条后不再继续下降）。"""
    mock_papers = [
        {
            "paperId": f"p{i}",
            "title": f"T{i}",
            "authors": [],
            "year": 2023,
            "abstract": "",
            "externalIds": {},
        }
        for i in range(20)
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )
        result = semantic_scholar_search("query")

    # 第 15 条（i=14）后 score 应为 0.3 floor
    # i=14: max(0.3, 1.0 - 14*0.05) = max(0.3, 0.3) = 0.3
    # i=15: max(0.3, 1.0 - 15*0.05) = max(0.3, 0.25) = 0.3
    for e in result[14:]:
        assert e["relevance_score"] == 0.3


# ---------------------------------------------------------------------------
# 字段完整性
# ---------------------------------------------------------------------------
def test_each_entry_has_required_fields():
    """每条含 title/authors/year/abstract/doi/source/relevance_score。"""
    mock_papers = [
        {
            "paperId": "p1",
            "title": "T",
            "authors": [{"name": "A"}],
            "year": 2023,
            "abstract": "Abs",
            "externalIds": {"DOI": "10.1/x"},
        },
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )
        result = semantic_scholar_search("q")

    required = [
        "title",
        "authors",
        "year",
        "abstract",
        "doi",
        "source",
        "relevance_score",
    ]
    for e in result:
        for k in required:
            assert k in e, f"缺失字段 {k}: {e}"


def test_authors_filter_empty_names():
    """authors 中空 name 被过滤掉。"""
    mock_papers = [
        {
            "paperId": "p1",
            "title": "T",
            "authors": [{"name": "A"}, {"name": ""}, {}, {"name": "B"}],
            "year": 2023,
            "abstract": "",
            "externalIds": {},
        },
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )
        result = semantic_scholar_search("q")

    assert result[0]["authors"] == ["A", "B"]


def test_missing_year_defaults_to_zero():
    """paper 缺 year 字段时默认 0。"""
    mock_papers = [
        {
            "paperId": "p1",
            "title": "T",
            "authors": [],
            "abstract": "",
            "externalIds": {},
            # 无 year
        },
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )
        result = semantic_scholar_search("q")

    assert result[0]["year"] == 0


def test_missing_abstract_defaults_to_empty():
    """paper 缺 abstract 字段时默认空字符串。"""
    mock_papers = [
        {
            "paperId": "p1",
            "title": "T",
            "authors": [],
            "year": 2023,
            "externalIds": {},
            # 无 abstract
        },
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )
        result = semantic_scholar_search("q")

    assert result[0]["abstract"] == ""


def test_missing_title_defaults_to_empty():
    """paper 缺 title 字段时默认空字符串。"""
    mock_papers = [
        {
            "paperId": "p1",
            "authors": [],
            "year": 2023,
            "abstract": "",
            "externalIds": {},
            # 无 title
        },
    ]
    with patch(
        "agent.nodes.literature_sources.semantic_scholar.urllib.request.urlopen"
    ) as mock_urlopen:
        mock_urlopen.return_value = _make_mock_urlopen(
            _mock_api_response(mock_papers)
        )
        result = semantic_scholar_search("q")

    assert result[0]["title"] == ""


# ---------------------------------------------------------------------------
# get_api_key_from_env
# ---------------------------------------------------------------------------
def test_get_api_key_from_env_present(monkeypatch):
    """环境变量存在时返回 key。"""
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "test_key_123")
    assert get_api_key_from_env() == "test_key_123"


def test_get_api_key_from_env_absent(monkeypatch):
    """环境变量缺失时返回 None。"""
    monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)
    assert get_api_key_from_env() is None


def test_get_api_key_from_env_empty_string(monkeypatch):
    """环境变量为空字符串时返回空字符串（调用方需自行判断真值）。"""
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "")
    # 空字符串在 search_literature 节点里被 `if not api_key` 判为 falsy → 降级
    assert get_api_key_from_env() == ""
