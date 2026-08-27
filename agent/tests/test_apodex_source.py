"""深搜旁路（Apodex 耗材实验）：文献源适配器契约。

北极星关联：search_literature 的"深搜旁路"。Apodex 两周免费 API
（OpenAI 兼容端点，Apodex-1.1）作为可选文献源接入——过期/无 key/调用
失败一律降级 mock_degraded，产品不对其产生任何硬依赖（耗材语义）。

约定（与 crossref / semantic_scholar 源一致）：
- 无 APODEX_API_KEY → 节点降级 mock_degraded
- 源函数失败抛 RuntimeError → 节点降级 mock_degraded
- pytest 默认 mock，不受影响
"""

import json

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


def test_search_assembles_sse_stream_when_server_streams(monkeypatch):
    """服务端忽略 stream:false 强推 SSE 时，适配器自行拼装完整内容。"""
    import io
    from nodes.literature_sources import apodex

    class _FakeResp:
        headers = {"content-type": "text/event-stream"}
        def __init__(self, data):
            self._buf = io.BytesIO(data)
        def read(self):
            return self._buf.read()
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    sse = (
        'data: {"choices":[{"delta":{"content":"```json\\n"}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"[{\\\"title\\\":\\\"Deep Paper\\\",\\\"authors\\\":[\\\"Ada\\\"],\\\"year\\\":2020}]"}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"\\n```"}}]}\n\n'
        "data: [DONE]\n\n"
    ).encode("utf-8")

    captured = {}
    def _fake_urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data.decode())
        return _FakeResp(sse)

    monkeypatch.setattr(
        "nodes.literature_sources.apodex.urllib.request.urlopen", _fake_urlopen
    )
    entries = apodex.apodex_search("q", "k-test")
    assert captured["body"]["stream"] is False, "应显式请求非流式"
    assert entries == [
        {
            "title": "Deep Paper",
            "authors": ["Ada"],
            "year": 2020,
            "source": "apodex",
            "relevance_score": 1.0,
        }
    ]


def test_parse_extracts_array_from_prose_prefix(monkeypatch):
    """模型无视指令包了 prose/围栏：数组在正文中也要被找到。"""
    from nodes.literature_sources import apodex

    payload = {
        "choices": [
            {
                "message": {
                    "content": (
                        "下面是代表性文献：\n\n"
                        '```json\n[{"title":"Real One","year":2011,'
                        '"authors":["Du"]}]\n```\n'
                    )
                }
            }
        ]
    }
    entries = apodex.parse_entries(payload)
    assert [e["title"] for e in entries] == ["Real One"]


def test_parse_survives_concatenated_json_bodies(monkeypatch):
    """多段 JSON 连排（流式 chunk 与完整对象混排）不炸，取含数组的对象。"""
    import json as _json
    from nodes.literature_sources import apodex

    obj_a = {"id": "c1", "object": "chat.completion.chunk", "choices": []}
    obj_b = {
        "choices": [
            {"message": {"content": '[{"title":"Mixed Body","year":2008,"authors":["Li"]}]'}}
        ]
    }
    blob = "  " + _json.dumps(obj_a) + "\n\n" + _json.dumps(obj_b)
    entries = apodex.parse_entries({"choices": [{"message": {"content": blob}}]})
    assert [e["title"] for e in entries] == ["Mixed Body"]


def test_parse_finds_array_in_reasoning_content(monkeypatch):
    """免费模型思考很重、可能把最终数组只写在 reasoning_content（或被
    max_tokens 截断在思考尾部）：收集器必须连 reasoning_content 一起扫。"""
    from nodes.literature_sources import apodex

    payload = {
        "choices": [
            {
                "finish_reason": "length",
                "message": {
                    "content": "",
                    "reasoning_content": (
                        "planning... candidate list:\n"
                        '[{"title":"From Thinking","year":2016,"authors":["Feng"]}]'
                    ),
                },
            }
        ]
    }
    entries = apodex.parse_entries(payload)
    assert [e["title"] for e in entries] == ["From Thinking"]


def test_parse_bad_json_raises_valueerror():
    from nodes.literature_sources import apodex

    with pytest.raises(ValueError):
        apodex.parse_entries({"choices": [{"message": {"content": "not json"}}]})


def test_parse_empty_choices_raises_valueerror():
    from nodes.literature_sources import apodex

    with pytest.raises(ValueError):
        apodex.parse_entries({"choices": []})
