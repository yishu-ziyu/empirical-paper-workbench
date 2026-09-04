"""统一 call_llm 的 HTTP 通道（urlopen 假响应，不打真网）。"""
from __future__ import annotations

import asyncio
import json
import threading

import pytest

from agent.llm.call_llm import call_llm
from agent.llm.router import LLMConfig
from agent.engine.cancellation import ExecutionCancelled, cancellation_scope


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


def test_call_llm_aborts_an_inflight_request_when_execution_is_cancelled(monkeypatch):
    started = threading.Event()
    release_legacy_request = threading.Event()
    cancellation = threading.Event()
    http_request_cancelled = threading.Event()
    errors: list[BaseException] = []

    class SlowAsyncClient:
        def __init__(self, *_args, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return False

        async def post(self, *_args, **_kwargs):
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                http_request_cancelled.set()
                raise

    def slow_legacy_urlopen(*_args, **_kwargs):
        started.set()
        release_legacy_request.wait(2)
        return _FakeResp(
            {"choices": [{"message": {"content": "late response"}}]}
        )

    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda _node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr("httpx.AsyncClient", SlowAsyncClient)
    monkeypatch.setattr(
        "agent.llm.call_llm.urllib.request.urlopen", slow_legacy_urlopen
    )

    def invoke():
        try:
            with cancellation_scope(cancellation.is_set):
                call_llm("cancel me", node_type="title")
        except BaseException as exc:
            errors.append(exc)

    caller = threading.Thread(target=invoke)
    caller.start()
    assert started.wait(1)
    cancellation.set()
    caller.join(0.5)
    stopped_promptly = not caller.is_alive()
    release_legacy_request.set()
    caller.join(2)

    assert stopped_promptly
    assert errors and isinstance(errors[0], ExecutionCancelled)
    assert http_request_cancelled.is_set()


def test_call_llm_cancellable_transport_preserves_success_response(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "cancellable result"}}]}

    class AsyncClient:
        def __init__(self, *_args, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return False

        async def post(self, *_args, **_kwargs):
            return Response()

    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda _node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr("httpx.AsyncClient", AsyncClient)

    with cancellation_scope(lambda: False):
        assert call_llm("complete", node_type="title") == "cancellable result"


def test_call_llm_cancellable_transport_preserves_network_error(monkeypatch):
    import httpx

    class AsyncClient:
        def __init__(self, *_args, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return False

        async def post(self, *_args, **_kwargs):
            request = httpx.Request("POST", "https://api.minimaxi.com/v1/chat/completions")
            raise httpx.ConnectError("offline", request=request)

    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda _node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr("httpx.AsyncClient", AsyncClient)

    with cancellation_scope(lambda: False):
        with pytest.raises(RuntimeError, match="LLM 网络失败"):
            call_llm("fail", node_type="title")


def test_call_llm_cancellable_transport_preserves_http_error(monkeypatch):
    import httpx

    class AsyncClient:
        def __init__(self, *_args, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return False

        async def post(self, *_args, **_kwargs):
            request = httpx.Request("POST", "https://api.minimaxi.com/v1/chat/completions")
            return httpx.Response(429, request=request, text="rate limited")

    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda _node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr("httpx.AsyncClient", AsyncClient)

    with cancellation_scope(lambda: False):
        with pytest.raises(RuntimeError, match="LLM HTTP 429"):
            call_llm("fail", node_type="title")
