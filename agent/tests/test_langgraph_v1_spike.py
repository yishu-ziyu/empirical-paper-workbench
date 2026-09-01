from __future__ import annotations

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import psycopg
import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command
from pydantic import Field

from agent.spike.langgraph_v1 import (
    SpikeContext,
    build_spike_agent,
    filter_fixture_data,
    initial_spike_state,
)


class ScriptedChatModel(BaseChatModel):
    """Framework model test double; orchestration still runs in LangChain/LangGraph."""

    responses: list[AIMessage]
    bound_tool_names: list[str] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "scripted-spike"

    def bind_tools(self, tools, **kwargs):
        self.bound_tool_names = [getattr(tool, "name", str(tool)) for tool in tools]
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        if not self.responses:
            raise AssertionError("scripted model exhausted")
        return ChatResult(generations=[ChatGeneration(message=self.responses.pop(0))])


def _decision_call(
    call_id: str,
    *,
    action: str,
    message: str,
    question: str | None = None,
    research_goal: str = "",
    known_context: dict[str, str] | None = None,
) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "LeaderDecision",
                "args": {
                    "action": action,
                    "message": message,
                    "question": question,
                    "research_goal": research_goal,
                    "known_context": known_context or {},
                },
                "id": call_id,
                "type": "tool_call",
            }
        ],
    )


def _tool_call(call_id: str) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "filter_fixture_data",
                "args": {"column": "year", "operator": ">=", "value": 1992},
                "id": call_id,
                "type": "tool_call",
            }
        ],
    )


def _write_fixture(path: Path) -> bytes:
    path.write_text(
        "state,year,employment\nNJ,1991,10\nNJ,1992,12\nPA,1991,9\nPA,1992,9\n",
        encoding="utf-8",
    )
    return path.read_bytes()


def test_two_turn_agent_interrupts_before_side_effect_and_resumes_after_rebuild(tmp_path):
    fixture = tmp_path / "minimum-wage.csv"
    original_bytes = _write_fixture(fixture)
    workspace = tmp_path / "spike-workspace"
    checkpoint_db = tmp_path / "spike-checkpoints.sqlite"
    executions: list[str] = []
    context = SpikeContext(
        fixture_csv=str(fixture),
        workspace=str(workspace),
        on_tool_execute=executions.append,
    )
    config = {"configurable": {"thread_id": "spike-session-1"}}

    first_model = ScriptedChatModel(
        responses=[
            _decision_call(
                "decision-1",
                action="ask",
                message="先确认比较对象，避免把地区差异误当政策效果。",
                question="你想比较政策前后，还是不同地区？",
                research_goal="研究最低工资是否影响就业",
                known_context={"outcome": "employment"},
            ),
            _tool_call("filter-1"),
        ]
    )

    with SqliteSaver.from_conn_string(str(checkpoint_db)) as saver:
        graph = build_spike_agent(model=first_model, checkpointer=saver)
        first = graph.invoke(
            initial_spike_state("我想看看最低工资对就业有没有影响"),
            config,
            context=context,
        )
        assert first["pending_decision"]["action"] == "ask"
        assert first["pending_decision"]["question"] == "你想比较政策前后，还是不同地区？"
        assert first["current_status"] == "waiting_user"

        paused = graph.invoke(
            {"messages": [{"role": "user", "content": "比较新泽西和宾州的政策前后"}]},
            config,
            context=context,
        )
        assert paused["__interrupt__"]
        assert graph.get_state(config).values["current_status"] == "waiting_approval"
        assert graph.get_state(config).values["pending_decision"]["action"] == "act"
        interrupt_value = paused["__interrupt__"][0].value
        assert interrupt_value["action_requests"][0]["name"] == "filter_fixture_data"
        assert "临时数据副本" in interrupt_value["action_requests"][0]["description"]
        assert executions == []
        assert not workspace.exists()

    # Simulate app/runner destruction: rebuild graph + model + SQLite connection.
    resumed_model = ScriptedChatModel(
        responses=[
            _decision_call(
                "decision-2",
                action="summarize",
                message="已按你确认的范围筛选临时副本；原数据未改。接下来可以检查两地趋势。",
                research_goal="比较新泽西和宾州最低工资政策前后的就业变化",
                known_context={"comparison": "NJ_vs_PA", "outcome": "employment"},
            )
        ]
    )
    with SqliteSaver.from_conn_string(str(checkpoint_db)) as saver:
        rebuilt = build_spike_agent(model=resumed_model, checkpointer=saver)
        final = rebuilt.invoke(
            Command(resume={"decisions": [{"type": "approve"}]}),
            config,
            context=context,
        )
        history = list(rebuilt.get_state_history(config))

    assert executions == ["filter-1"]
    assert fixture.read_bytes() == original_bytes
    assert final["last_tool_result"]["status"] == "success"
    assert final["last_tool_result"]["n_before"] == 4
    assert final["last_tool_result"]["n_after"] == 2
    assert Path(final["last_tool_result"]["output_path"]).is_file()
    assert final["pending_decision"]["action"] == "summarize"
    assert final["current_status"] == "completed"
    assert final["research_goal"] == "比较新泽西和宾州最低工资政策前后的就业变化"
    assert len(history) >= 4

    tool_messages = [m for m in final["messages"] if isinstance(m, ToolMessage)]
    assert len([m for m in tool_messages if m.name == "filter_fixture_data"]) == 1
    assert any(
        call.get("name") == "filter_fixture_data"
        for message in final["messages"]
        if isinstance(message, AIMessage)
        for call in message.tool_calls
    )


def test_reject_resume_does_not_execute_tool(tmp_path):
    fixture = tmp_path / "minimum-wage.csv"
    _write_fixture(fixture)
    workspace = tmp_path / "spike-workspace"
    checkpoint_db = tmp_path / "spike-checkpoints.sqlite"
    executions: list[str] = []
    context = SpikeContext(
        fixture_csv=str(fixture),
        workspace=str(workspace),
        on_tool_execute=executions.append,
    )
    config = {"configurable": {"thread_id": "spike-session-reject"}}

    model = ScriptedChatModel(responses=[_tool_call("filter-reject")])
    with SqliteSaver.from_conn_string(str(checkpoint_db)) as saver:
        graph = build_spike_agent(model=model, checkpointer=saver)
        paused = graph.invoke(
            initial_spike_state("请先筛选 1992 年后的数据"),
            config,
            context=context,
        )
        assert paused["__interrupt__"]

    final_model = ScriptedChatModel(
        responses=[
            _decision_call(
                "decision-reject",
                action="explain",
                message="你拒绝了筛选，所以数据没有变化。",
                research_goal="检查最低工资与就业",
            )
        ]
    )
    with SqliteSaver.from_conn_string(str(checkpoint_db)) as saver:
        rebuilt = build_spike_agent(model=final_model, checkpointer=saver)
        final = rebuilt.invoke(
            Command(
                resume={
                    "decisions": [
                        {"type": "reject", "message": "先保留完整样本"}
                    ]
                }
            ),
            config,
            context=context,
        )

    assert executions == []
    assert not workspace.exists()
    assert final["pending_decision"]["action"] == "explain"
    assert final["current_status"] == "completed"
    assert any(
        isinstance(message, ToolMessage) and message.status == "error"
        for message in final["messages"]
    )


def test_same_tool_call_id_is_idempotent_under_concurrent_retry(tmp_path):
    """Retries of one approved call share one side effect, even concurrently."""
    fixture = tmp_path / "minimum-wage.csv"
    original_bytes = _write_fixture(fixture)
    executions: list[str] = []
    context = SpikeContext(
        fixture_csv=str(fixture),
        workspace=str(tmp_path / "spike-workspace"),
        on_tool_execute=executions.append,
    )
    runtime = SimpleNamespace(context=context, tool_call_id="same-call")

    def invoke_tool():
        return filter_fixture_data.func(
            "year", ">=", 1992, runtime=runtime
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        commands = list(pool.map(lambda _: invoke_tool(), range(2)))

    results = [command.update["last_tool_result"] for command in commands]
    assert results[0] == results[1]
    assert results[0]["status"] == "success"
    assert executions == ["same-call"]
    assert Path(results[0]["output_path"]).is_file()
    assert fixture.read_bytes() == original_bytes


def test_failed_tool_stays_failed_after_leader_reply(tmp_path):
    fixture = tmp_path / "minimum-wage.csv"
    _write_fixture(fixture)
    checkpoint_db = tmp_path / "spike-checkpoints.sqlite"
    context = SpikeContext(
        fixture_csv=str(fixture),
        workspace=str(tmp_path / "workspace"),
    )
    config = {"configurable": {"thread_id": "spike-session-failed"}}
    bad_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "filter_fixture_data",
                "args": {"column": "missing_col", "operator": ">=", "value": 1},
                "id": "filter-failed",
                "type": "tool_call",
            }
        ],
    )

    with SqliteSaver.from_conn_string(str(checkpoint_db)) as saver:
        graph = build_spike_agent(
            model=ScriptedChatModel(responses=[bad_call]),
            checkpointer=saver,
        )
        paused = graph.invoke(
            initial_spike_state("筛选数据"), config, context=context
        )
        assert paused["__interrupt__"]

    with SqliteSaver.from_conn_string(str(checkpoint_db)) as saver:
        rebuilt = build_spike_agent(
            model=ScriptedChatModel(
                responses=[
                    _decision_call(
                        "decision-failed",
                        action="explain",
                        message="筛选失败：数据里没有这个变量。",
                    )
                ]
            ),
            checkpointer=saver,
        )
        final = rebuilt.invoke(
            Command(resume={"decisions": [{"type": "approve"}]}),
            config,
            context=context,
        )

    assert final["last_tool_result"]["status"] == "failed"
    assert final["current_status"] == "failed"


def test_postgres_checkpointer_can_resume_approved_tool_exactly_once(tmp_path):
    """Production-store proof; skipped when the configured Postgres is unavailable."""
    url = (os.environ.get("CHECKPOINT_DB_URL") or "").strip()
    if not url:
        pytest.skip("CHECKPOINT_DB_URL is not configured")
    try:
        probe = psycopg.connect(
            url, autocommit=True, prepare_threshold=0, connect_timeout=5
        )
        probe.close()
    except psycopg.Error as exc:
        pytest.skip(f"checkpoint Postgres unavailable: {type(exc).__name__}")

    fixture = tmp_path / "minimum-wage.csv"
    _write_fixture(fixture)
    executions: list[str] = []
    context = SpikeContext(
        fixture_csv=str(fixture),
        workspace=str(tmp_path / "workspace"),
        on_tool_execute=executions.append,
    )
    thread_id = f"spike-postgres-{uuid.uuid4()}"
    config = {"configurable": {"thread_id": thread_id}}

    try:
        with psycopg.connect(
            url, autocommit=True, prepare_threshold=0, connect_timeout=5
        ) as conn:
            saver = PostgresSaver(conn)
            saver.setup()
            graph = build_spike_agent(
                model=ScriptedChatModel(responses=[_tool_call("pg-filter-1")]),
                checkpointer=saver,
            )
            paused = graph.invoke(
                initial_spike_state("筛选 1992 年后的临时样本"),
                config,
                context=context,
            )
            assert paused["__interrupt__"]
            assert executions == []

        with psycopg.connect(
            url, autocommit=True, prepare_threshold=0, connect_timeout=5
        ) as conn:
            rebuilt_saver = PostgresSaver(conn)
            rebuilt = build_spike_agent(
                model=ScriptedChatModel(
                    responses=[
                        _decision_call(
                            "pg-decision",
                            action="summarize",
                            message="Postgres 恢复后筛选完成。",
                        )
                    ]
                ),
                checkpointer=rebuilt_saver,
            )
            final = rebuilt.invoke(
                Command(resume={"decisions": [{"type": "approve"}]}),
                config,
                context=context,
            )
            assert final["last_tool_result"]["status"] == "success"
            assert executions == ["pg-filter-1"]
    finally:
        try:
            with psycopg.connect(
                url, autocommit=True, prepare_threshold=0, connect_timeout=5
            ) as conn:
                PostgresSaver(conn).delete_thread(thread_id)
        except psycopg.Error:
            pass
