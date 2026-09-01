from __future__ import annotations

from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field


class ScriptedChatModel(BaseChatModel):
    responses: list[AIMessage]
    bound_tool_names: list[str] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "scripted-http-spike"

    def bind_tools(self, tools, **kwargs):
        self.bound_tool_names = [getattr(tool, "name", str(tool)) for tool in tools]
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=self.responses.pop(0))])


def _decision(action: str, message: str, *, question: str | None = None) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "LeaderDecision",
                "args": {
                    "action": action,
                    "message": message,
                    "question": question,
                    "research_goal": "比较最低工资政策前后的就业变化",
                    "known_context": {"outcome": "employment"},
                },
                "id": f"decision-{action}",
                "type": "tool_call",
            }
        ],
    )


def _filter_call() -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "filter_fixture_data",
                "args": {"column": "year", "operator": ">=", "value": 1992},
                "id": "http-filter-1",
                "type": "tool_call",
            }
        ],
    )


def _filter_call_with_value(call_id: str, value: int) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "filter_fixture_data",
                "args": {"column": "year", "operator": ">=", "value": value},
                "id": call_id,
                "type": "tool_call",
            }
        ],
    )


def test_http_spike_is_disabled_by_default(client, monkeypatch):
    monkeypatch.delenv("ECONPAPER_ENABLE_AGENT_SPIKE", raising=False)
    response = client.post(
        "/spike/agent/disabled/turn",
        json={"message": "test"},
    )
    assert response.status_code == 404


def test_http_spike_exposes_real_framework_pause_and_resume(client, tmp_path, monkeypatch):
    fixture = tmp_path / "minimum-wage.csv"
    fixture.write_text(
        "state,year,employment\nNJ,1991,10\nNJ,1992,12\nPA,1991,9\nPA,1992,9\n",
        encoding="utf-8",
    )
    original = fixture.read_bytes()
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("ECONPAPER_ENABLE_AGENT_SPIKE", "true")
    monkeypatch.setenv("ECONPAPER_SPIKE_DB", str(tmp_path / "spike.sqlite"))
    monkeypatch.setenv("ECONPAPER_SPIKE_FIXTURE", str(fixture))
    monkeypatch.setenv("ECONPAPER_SPIKE_WORKSPACE", str(workspace))

    models = [
        ScriptedChatModel(
            responses=[
                _decision(
                    "ask",
                    "先确认比较对象。",
                    question="你想比较政策前后，还是不同地区？",
                )
            ]
        ),
        ScriptedChatModel(responses=[_filter_call()]),
        ScriptedChatModel(
            responses=[_decision("summarize", "筛选只改了临时副本，下一步检查趋势。")]
        ),
    ]
    monkeypatch.setattr("routers.agent_spike.build_leader_model", lambda: models.pop(0))

    first = client.post(
        "/spike/agent/http-session/turn",
        json={"message": "我想看看最低工资对就业有没有影响"},
    )
    assert first.status_code == 200
    assert first.json()["status"] == "waiting_user"
    assert first.json()["decision"]["action"] == "ask"
    assert any(event["kind"] == "message" for event in first.json()["events"])

    second = client.post(
        "/spike/agent/http-session/turn",
        json={"message": "比较新泽西和宾州的政策前后"},
    )
    assert second.status_code == 200
    assert second.json()["status"] == "waiting_approval"
    assert second.json()["interrupt"]["action_requests"][0]["name"] == "filter_fixture_data"
    assert any(event["kind"] == "interrupt" for event in second.json()["events"])
    assert not workspace.exists()

    # Every request rebuilds model, graph, saver and connection; the SQLite thread is authority.
    final = client.post(
        "/spike/agent/http-session/decision",
        json={"decision": "approve"},
    )
    assert final.status_code == 200
    body = final.json()
    assert body["status"] == "completed"
    assert body["decision"]["action"] == "summarize"
    assert body["last_tool_result"]["status"] == "success"
    assert fixture.read_bytes() == original
    assert Path(body["last_tool_result"]["output_path"]).is_file()
    assert any(
        event["kind"] == "message" and event.get("tool_name") == "filter_fixture_data"
        for event in body["events"]
    )


def test_http_spike_stream_is_sse_and_reports_preview_before_approval(
    client, tmp_path, monkeypatch
):
    fixture = tmp_path / "minimum-wage.csv"
    fixture.write_text(
        "state,year,employment\nNJ,1991,10\nNJ,1992,12\nPA,1991,9\nPA,1992,9\n",
        encoding="utf-8",
    )
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("ECONPAPER_ENABLE_AGENT_SPIKE", "true")
    monkeypatch.setenv("ECONPAPER_SPIKE_DB", str(tmp_path / "spike.sqlite"))
    monkeypatch.setenv("ECONPAPER_SPIKE_FIXTURE", str(fixture))
    monkeypatch.setenv("ECONPAPER_SPIKE_WORKSPACE", str(workspace))

    models = [
        ScriptedChatModel(responses=[_decision("ask", "先确认比较对象。", question="你想比较政策前后，还是不同地区？")]),
        ScriptedChatModel(responses=[_filter_call()]),
    ]
    monkeypatch.setattr("routers.agent_spike.build_leader_model", lambda: models.pop(0))

    first = client.post(
        "/spike/agent/stream-session/turn/stream",
        json={"message": "我想研究最低工资提高后，会不会减少就业。"},
    )
    assert first.status_code == 200
    assert first.headers["content-type"].startswith("text/event-stream")
    assert "data:" in first.text
    assert '"kind": "state"' in first.text

    second = client.post(
        "/spike/agent/stream-session/turn/stream",
        json={"message": "比较政策前后。"},
    )
    assert second.status_code == 200
    assert '"kind": "interrupt"' in second.text
    assert '"n_after": 2' in second.text
    assert '"n_before": 4' in second.text
    assert not workspace.exists()


def test_http_spike_state_restores_waiting_approval_after_refresh(
    client, tmp_path, monkeypatch
):
    fixture = tmp_path / "minimum-wage.csv"
    fixture.write_text(
        "state,year,employment\nNJ,1991,10\nNJ,1992,12\nPA,1991,9\nPA,1992,9\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ECONPAPER_ENABLE_AGENT_SPIKE", "true")
    monkeypatch.setenv("ECONPAPER_SPIKE_DB", str(tmp_path / "spike.sqlite"))
    monkeypatch.setenv("ECONPAPER_SPIKE_FIXTURE", str(fixture))
    monkeypatch.setenv("ECONPAPER_SPIKE_WORKSPACE", str(tmp_path / "workspace"))
    model = ScriptedChatModel(responses=[_filter_call()])
    monkeypatch.setattr("routers.agent_spike.build_leader_model", lambda: model)

    paused = client.post(
        "/spike/agent/state-session/turn",
        json={"message": "请先筛选 1992 年后的数据"},
    )
    assert paused.status_code == 200
    restored = client.get("/spike/agent/state-session/state")
    assert restored.status_code == 200
    assert restored.json()["status"] == "waiting_approval"
    assert restored.json()["interrupt"]["action_requests"][0]["name"] == "filter_fixture_data"


def test_http_spike_workspace_isolated_per_session_and_new_session_does_not_reuse_output(
    client, tmp_path, monkeypatch
):
    fixture = tmp_path / "minimum-wage.csv"
    fixture.write_text(
        "state,year,employment\nNJ,1991,10\nNJ,1992,12\nPA,1991,9\nPA,1992,9\n",
        encoding="utf-8",
    )
    original_bytes = fixture.read_bytes()
    workspace_root = tmp_path / "workspace-root"
    monkeypatch.setenv("ECONPAPER_ENABLE_AGENT_SPIKE", "true")
    monkeypatch.setenv("ECONPAPER_SPIKE_DB", str(tmp_path / "spike.sqlite"))
    monkeypatch.setenv("ECONPAPER_SPIKE_FIXTURE", str(fixture))
    monkeypatch.setenv("ECONPAPER_SPIKE_WORKSPACE", str(workspace_root))
    from routers.agent_spike import _paths

    _, context_a = _paths("session-a")
    _, context_b = _paths("session-b")
    assert context_a.workspace != context_b.workspace

    # Reusing the same tool-call id is intentional: a fixed workspace would
    # incorrectly treat C as a replay of A's marker and output.
    models = [
        ScriptedChatModel(responses=[_filter_call()]),
        ScriptedChatModel(responses=[_filter_call()]),
        ScriptedChatModel(responses=[_decision("summarize", "已完成筛选。")]),
        ScriptedChatModel(responses=[_filter_call()]),
        ScriptedChatModel(responses=[_decision("summarize", "已完成筛选。")]),
        ScriptedChatModel(responses=[]),
    ]
    monkeypatch.setattr("routers.agent_spike.build_leader_model", lambda: models.pop(0))

    first_a = client.post(
        "/spike/agent/session-a/turn",
        json={"message": "请先筛选 1992 年后的数据"},
    )
    first_b = client.post(
        "/spike/agent/session-b/turn",
        json={"message": "请先筛选 1992 年后的数据"},
    )
    assert first_a.status_code == first_b.status_code == 200
    assert first_a.json()["status"] == first_b.json()["status"] == "waiting_approval"
    assert not workspace_root.exists()

    approved_a = client.post(
        "/spike/agent/session-a/decision",
        json={"decision": "approve"},
    )
    assert approved_a.status_code == 200
    output_a = Path(approved_a.json()["last_tool_result"]["output_path"])
    assert output_a.is_file()
    assert not Path(context_b.workspace).exists()
    assert client.get("/spike/agent/session-b/state").json()["status"] == "waiting_approval"

    first_c = client.post(
        "/spike/agent/session-c/turn",
        json={"message": "请先筛选 1992 年后的数据"},
    )
    assert first_c.status_code == 200
    assert first_c.json()["status"] == "waiting_approval"
    approved_c = client.post(
        "/spike/agent/session-c/decision",
        json={"decision": "approve"},
    )
    assert approved_c.status_code == 200
    output_c = Path(approved_c.json()["last_tool_result"]["output_path"])
    assert output_c.is_file()
    assert output_c != output_a
    assert output_c.parent != output_a.parent
    assert fixture.read_bytes() == original_bytes


def test_http_spike_pause_is_checkpointed_and_resume_restores_approval_without_side_effect(
    client, tmp_path, monkeypatch
):
    fixture = tmp_path / "minimum-wage.csv"
    fixture.write_text(
        "state,year,employment\nNJ,1991,10\nNJ,1992,12\nPA,1991,9\nPA,1992,9\n",
        encoding="utf-8",
    )
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("ECONPAPER_ENABLE_AGENT_SPIKE", "true")
    monkeypatch.setenv("ECONPAPER_SPIKE_DB", str(tmp_path / "spike.sqlite"))
    monkeypatch.setenv("ECONPAPER_SPIKE_FIXTURE", str(fixture))
    monkeypatch.setenv("ECONPAPER_SPIKE_WORKSPACE", str(workspace))

    models = [
        ScriptedChatModel(responses=[_filter_call()]),
        ScriptedChatModel(responses=[_decision("summarize", "已完成筛选。")]),
        ScriptedChatModel(responses=[]),
    ]
    monkeypatch.setattr("routers.agent_spike.build_leader_model", lambda: models.pop(0))

    waiting = client.post(
        "/spike/agent/pause-session/turn",
        json={"message": "请先筛选 1992 年后的数据"},
    )
    assert waiting.status_code == 200
    assert waiting.json()["status"] == "waiting_approval"
    paused = client.post("/spike/agent/pause-session/pause")
    assert paused.status_code == 200
    assert paused.json()["status"] == "paused_by_user"
    assert paused.json()["interrupt"]["action_requests"][0]["name"] == "filter_fixture_data"
    assert not workspace.exists()

    refreshed = client.get("/spike/agent/pause-session/state")
    assert refreshed.status_code == 200
    assert refreshed.json()["status"] == "paused_by_user"
    assert refreshed.json()["interrupt"]
    resumed = client.post("/spike/agent/pause-session/resume")
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "waiting_approval"
    assert resumed.json()["interrupt"]
    assert not workspace.exists()

    approved = client.post(
        "/spike/agent/pause-session/decision",
        json={"decision": "approve"},
    )
    assert approved.status_code == 200
    assert approved.json()["last_tool_result"]["status"] == "success"
    output = Path(approved.json()["last_tool_result"]["output_path"])
    assert output.is_file()
    before_repeat = output.read_bytes()
    repeated = client.post(
        "/spike/agent/pause-session/decision",
        json={"decision": "approve"},
    )
    assert repeated.status_code == 409
    assert output.read_bytes() == before_repeat


def test_http_spike_checkpoint_actions_do_not_require_leader_model(
    client, tmp_path, monkeypatch
):
    """Pause, refresh and resume are checkpoint operations, not model turns."""
    fixture = tmp_path / "minimum-wage.csv"
    fixture.write_text(
        "state,year,employment\nNJ,1991,10\nNJ,1992,12\nPA,1991,9\nPA,1992,9\n",
        encoding="utf-8",
    )
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("ECONPAPER_ENABLE_AGENT_SPIKE", "true")
    monkeypatch.setenv("ECONPAPER_SPIKE_DB", str(tmp_path / "spike.sqlite"))
    monkeypatch.setenv("ECONPAPER_SPIKE_FIXTURE", str(fixture))
    monkeypatch.setenv("ECONPAPER_SPIKE_WORKSPACE", str(workspace))

    monkeypatch.setattr(
        "routers.agent_spike.build_leader_model",
        lambda: ScriptedChatModel(responses=[_filter_call()]),
    )
    waiting = client.post(
        "/spike/agent/provider-independent/turn",
        json={"message": "请先筛选 1992 年后的数据"},
    )
    assert waiting.status_code == 200
    assert waiting.json()["status"] == "waiting_approval"

    def provider_unavailable():
        raise AssertionError("checkpoint actions must not build or call the leader")

    monkeypatch.setattr("routers.agent_spike.build_leader_model", provider_unavailable)

    paused = client.post("/spike/agent/provider-independent/pause")
    assert paused.status_code == 200
    assert paused.json()["status"] == "paused_by_user"
    assert client.get("/spike/agent/provider-independent/state").json()["status"] == "paused_by_user"

    resumed = client.post("/spike/agent/provider-independent/resume")
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "waiting_approval"
    assert not workspace.exists()


def test_http_spike_distinct_tool_calls_keep_distinct_session_outputs(
    client, tmp_path, monkeypatch
):
    """A later run in one session must not overwrite an earlier sidecar."""
    fixture = tmp_path / "minimum-wage.csv"
    original = (
        "state,year,employment\nNJ,1991,10\nNJ,1992,12\nPA,1991,9\nPA,1992,9\n"
    )
    fixture.write_text(original, encoding="utf-8")
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("ECONPAPER_ENABLE_AGENT_SPIKE", "true")
    monkeypatch.setenv("ECONPAPER_SPIKE_DB", str(tmp_path / "spike.sqlite"))
    monkeypatch.setenv("ECONPAPER_SPIKE_FIXTURE", str(fixture))
    monkeypatch.setenv("ECONPAPER_SPIKE_WORKSPACE", str(workspace))

    models = [
        ScriptedChatModel(responses=[_filter_call_with_value("call-one", 1992)]),
        ScriptedChatModel(responses=[_decision("summarize", "第一轮完成。")]),
        ScriptedChatModel(responses=[_filter_call_with_value("call-two", 1991)]),
        ScriptedChatModel(responses=[_decision("summarize", "第二轮完成。")]),
    ]
    monkeypatch.setattr("routers.agent_spike.build_leader_model", lambda: models.pop(0))

    first = client.post(
        "/spike/agent/multi-run/turn",
        json={"message": "筛选 1992 年后的数据"},
    )
    assert first.status_code == 200
    first_approved = client.post(
        "/spike/agent/multi-run/decision",
        json={"decision": "approve"},
    )
    assert first_approved.status_code == 200
    first_output = Path(first_approved.json()["last_tool_result"]["output_path"])
    first_bytes = first_output.read_bytes()

    second = client.post(
        "/spike/agent/multi-run/turn",
        json={"message": "再筛选 1991 年后的数据"},
    )
    assert second.status_code == 200
    second_approved = client.post(
        "/spike/agent/multi-run/decision",
        json={"decision": "approve"},
    )
    assert second_approved.status_code == 200
    second_output = Path(second_approved.json()["last_tool_result"]["output_path"])

    assert first_output != second_output
    assert first_output.read_bytes() == first_bytes
    assert second_output.read_text(encoding="utf-8").count("\n") == 5
    assert fixture.read_text(encoding="utf-8") == original
