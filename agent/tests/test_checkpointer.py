"""GS-E1: MemorySaver / no-Postgres local boot for the LangGraph checkpointer.

Importing ``graph`` used to compile PostgresSaver at module import, so
``from graph import graph`` (and therefore POST /upload) failed with 503
when CHECKPOINT_DB_URL was unset. These tests pin the MemorySaver path.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import MemorySaver

import graph as graph_mod


@pytest.fixture
def reset_graph_runtime():
    graph_mod._reset_runtime()
    yield
    graph_mod._reset_runtime()


def test_get_checkpointer_uses_memory_when_url_unset(monkeypatch, reset_graph_runtime):
    monkeypatch.delenv("CHECKPOINT_DB_URL", raising=False)
    graph_mod._reset_runtime()
    cp = graph_mod._get_checkpointer()
    assert isinstance(cp, MemorySaver)


def test_get_checkpointer_uses_memory_when_url_empty(monkeypatch, reset_graph_runtime):
    monkeypatch.setenv("CHECKPOINT_DB_URL", "   ")
    graph_mod._reset_runtime()
    cp = graph_mod._get_checkpointer()
    assert isinstance(cp, MemorySaver)


def test_unset_url_does_not_call_psycopg(monkeypatch, reset_graph_runtime):
    monkeypatch.delenv("CHECKPOINT_DB_URL", raising=False)
    graph_mod._reset_runtime()
    calls: list[int] = []

    def boom(*_args, **_kwargs):
        calls.append(1)
        raise AssertionError(
            "psycopg.connect must not run when CHECKPOINT_DB_URL is unset"
        )

    monkeypatch.setattr(graph_mod.psycopg, "connect", boom)
    cp = graph_mod._get_checkpointer()
    assert isinstance(cp, MemorySaver)
    assert calls == []


def test_connect_failure_fails_loud_without_memory_cache(
    monkeypatch, reset_graph_runtime
):
    monkeypatch.setenv(
        "CHECKPOINT_DB_URL",
        "postgresql://nope@127.0.0.1:1/none",
    )
    graph_mod._reset_runtime()

    captured: dict = {}

    def boom(*_args, **kwargs):
        captured.update(kwargs)
        raise OSError("connection refused")

    monkeypatch.setattr(graph_mod.psycopg, "connect", boom)
    with pytest.raises(OSError, match="connection refused"):
        graph_mod._get_checkpointer()
    assert captured.get("connect_timeout") == 5
    assert graph_mod._CHECKPOINTER is None


def test_setup_failure_closes_connection_then_fails_loud(
    monkeypatch, reset_graph_runtime
):
    """connect() success + setup() fail must close the socket, then raise."""
    monkeypatch.setenv(
        "CHECKPOINT_DB_URL",
        "postgresql://nope@127.0.0.1:1/none",
    )
    graph_mod._reset_runtime()
    closed: list[int] = []

    class FakeConn:
        def close(self) -> None:
            closed.append(1)

    class BoomSaver:
        def __init__(self, _conn) -> None:
            pass

        def setup(self) -> None:
            raise RuntimeError("setup failed")

    monkeypatch.setattr(graph_mod.psycopg, "connect", lambda *_a, **_k: FakeConn())
    monkeypatch.setattr(graph_mod, "PostgresSaver", BoomSaver)
    with pytest.raises(RuntimeError, match="setup failed"):
        graph_mod._get_checkpointer()
    assert closed == [1]
    assert graph_mod._CHECKPOINTER is None


def test_public_graph_is_lazy_until_used(monkeypatch, reset_graph_runtime):
    monkeypatch.delenv("CHECKPOINT_DB_URL", raising=False)
    graph_mod._reset_runtime()
    assert graph_mod.graph is not None
    assert graph_mod.graph._compiled is None


def test_build_graph_compiles_without_postgres(monkeypatch, reset_graph_runtime):
    monkeypatch.delenv("CHECKPOINT_DB_URL", raising=False)
    graph_mod._reset_runtime()
    compiled = graph_mod.build_graph()
    assert compiled is not None
    node_ids = set(compiled.get_graph().nodes.keys())
    assert "upload_data" in node_ids
    assert "clean_data" in node_ids
    assert isinstance(graph_mod._CHECKPOINTER, MemorySaver)


def test_from_graph_import_graph_without_live_postgres():
    """``from graph import graph`` must not require a live Postgres."""
    agent_dir = str(Path(__file__).resolve().parents[1])
    env = os.environ.copy()
    env.pop("CHECKPOINT_DB_URL", None)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = agent_dir + (os.pathsep + existing if existing else "")
    code = (
        "from graph import graph\n"
        "assert graph is not None\n"
        "assert getattr(graph, '_compiled', 'missing') is None\n"
        "from graph import _get_checkpointer\n"
        "from langgraph.checkpoint.memory import MemorySaver\n"
        "assert isinstance(_get_checkpointer(), MemorySaver)\n"
        "print('import-ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "import-ok" in result.stdout
