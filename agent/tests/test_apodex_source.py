"""深搜旁路（Apodex 耗材实验）：文献源适配器契约。

北极星关联：search_literature 的"深搜旁路"。Apodex 两周免费 API
（OpenAI 兼容端点，Apodex-1.1）作为可选文献源接入——过期/无 key/调用
失败一律降级 mock_degraded，产品不对其产生任何硬依赖（耗材语义）。

约定（与 crossref / semantic_scholar 源一致）：
- 无 APODEX_API_KEY → 节点降级 mock_degraded
- 源函数失败抛 RuntimeError → 节点降级 mock_degraded
- pytest 默认 mock，不受影响
"""

import pytest

from nodes.search_literature import search_literature


FAKE_ENTRIES = [
    {
        "title": "Automation and Labor Markets",
        "authors": ["Acemoglu", "Restrepo"],
        "year": 2022,
        "doi": "10.1257/jel.20201234",
        "abstract": "robots",
        "source": "apodex",
    }
]


def test_missing_key_degrades_to_mock():
    """没配 key 时选 apodex 源 → 直接降级，绝不打网。"""
    result = search_literature(
        {"research_direction": "automation wages", "literature_source": "apodex"}
    )
    assert result["literature_source"] == "mock_degraded"
    assert result["literature_entries"]
    assert all(e.get("source") == "mock" for e in result["literature_entries"])


def test_apodex_happy_path(monkeypatch):
    monkeypatch.setenv("APODEX_API_KEY", "k-test")
    monkeypatch.setattr(
        "nodes.literature_sources.apodex.apodex_search",
        lambda query, api_key, **kwargs: FAKE_ENTRIES,
    )
    result = search_literature(
        {"research_direction": "automation wages", "literature_source": "apodex"}
    )
    assert result["literature_source"] == "apodex"
    assert result["literature_entries"][0]["doi"] == "10.1257/jel.20201234"


def test_apodex_error_degrades_to_mock(monkeypatch):
    monkeypatch.setenv("APODEX_API_KEY", "k-test")

    def _boom(query, api_key, **kwargs):
        raise RuntimeError("deep search down")

    monkeypatch.setattr("nodes.literature_sources.apodex.apodex_search", _boom)
    result = search_literature(
        {"research_direction": "automation wages", "literature_source": "apodex"}
    )
    assert result["literature_source"] == "mock_degraded"


# ---------------------------------------------------------------------------
# 适配器单元：OpenAI 兼容响应 → LiteratureEntry 列表
# ---------------------------------------------------------------------------

def test_parse_unwraps_choices_and_fenced_json(monkeypatch):
    from nodes.literature_sources import apodex

    payload = {
        "choices": [
            {
                "message": {
                    "content": (
                        "```json\n"
                        '[{"title":"A Paper","authors":["Alpha","Beta"],'
                        '"year":"2021","doi":"10.1/x"}]\n'
                        "```"
                    )
                }
            }
        ]
    }
    entries = apodex.parse_entries(payload)
    assert entries == [
        {
            "title": "A Paper",
            "authors": ["Alpha", "Beta"],
            "year": 2021,
            "doi": "10.1/x",
            "source": "apodex",
            "relevance_score": 1.0,
        }
    ]


def test_parse_drops_titleless_and_coerces(monkeypatch):
    from nodes.literature_sources import apodex

    payload = {
        "choices": [
            {
                "message": {
                    "content": '[{"authors":["X"],"year":2020},'
                    '{"title":"Keep","year":2019,"authors":"Solo"}]'
                }
            }
        ]
    }
    entries = apodex.parse_entries(payload)
    assert len(entries) == 1
    assert entries[0]["authors"] == ["Solo"]
    assert isinstance(entries[0]["year"], int)


def test_parse_bad_json_raises_valueerror():
    from nodes.literature_sources import apodex

    with pytest.raises(ValueError):
        apodex.parse_entries({"choices": [{"message": {"content": "not json"}}]})


def test_parse_empty_choices_raises_valueerror():
    from nodes.literature_sources import apodex

    with pytest.raises(ValueError):
        apodex.parse_entries({"choices": []})
