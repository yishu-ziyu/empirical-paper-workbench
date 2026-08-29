"""统一 call_llm 的 HTTP 通道（urlopen 假响应，不打真网）。"""
from __future__ import annotations

import json

import pytest

from agent.llm.call_llm import call_llm
from agent.llm.router import LLMConfig


class _FakeResp:
    def __init__(self, payload: dict):
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._raw

    def __enter__(self) -> "_FakeResp":
        return self

    def __exit__(self, *args) -> bool:
        return False


def test_call_llm_posts_chat_completions(monkeypatch):
    seen: dict = {}

    def fake_urlopen(req, timeout=0):
        seen["url"] = req.full_url
        seen["data"] = json.loads(req.data.decode("utf-8"))
        seen["timeout"] = timeout
        seen["auth"] = req.get_header("Authorization")
        return _FakeResp(
            {"choices": [{"message": {"content": "Hello from model"}}]}
        )

    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr("agent.llm.call_llm.urllib.request.urlopen", fake_urlopen)

    text = call_llm("hi", node_type="title", system="sys")
    assert text == "Hello from model"
    assert seen["url"] == "https://api.minimaxi.com/v1/chat/completions"
    assert seen["timeout"] == 120
    assert seen["data"]["model"] == "MiniMax-M3"
    assert seen["data"]["thinking"] == {"type": "disabled"}
    assert seen["data"]["messages"][0] == {"role": "system", "content": "sys"}
    assert seen["data"]["messages"][1] == {"role": "user", "content": "hi"}
    assert seen["auth"] == "Bearer sk-test"


def test_call_llm_strips_think_blocks(monkeypatch):
    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr(
        "agent.llm.call_llm.urllib.request.urlopen",
        lambda req, timeout=0: _FakeResp(
            {
                "choices": [
                    {
                        "message": {
                            "content": "<think>内部推理</think>\n\n供需均衡论"
                        }
                    }
                ]
            }
        ),
    )
    assert call_llm("p", node_type="title") == "供需均衡论"


def test_call_llm_extracts_list_content(monkeypatch):
    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr(
        "agent.llm.call_llm.urllib.request.urlopen",
        lambda req, timeout=0: _FakeResp(
            {
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"type": "text", "text": "A"},
                                {"type": "text", "text": "B"},
                            ]
                        }
                    }
                ]
            }
        ),
    )
    assert call_llm("p", node_type="generate") == "AB"


def test_call_llm_http_error_raises(monkeypatch):
    import urllib.error
    from io import BytesIO

    def boom(req, timeout=0):
        raise urllib.error.HTTPError(
            url="https://api.minimaxi.com/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=BytesIO(b'{"error":"no"}'),
        )

    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr("agent.llm.call_llm.urllib.request.urlopen", boom)
    with pytest.raises(RuntimeError, match="LLM HTTP 401"):
        call_llm("p", node_type="title")
