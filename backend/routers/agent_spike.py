"""Isolated HTTP seam for the LangGraph v1 leader spike.

Every request rebuilds the model, graph and SQLite connection. Conversation and
approval state survive only through the LangGraph checkpointer keyed by thread_id.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from pydantic import BaseModel, Field

from agent.spike.langgraph_v1 import (
    SpikeContext,
    build_spike_agent,
    initial_spike_state,
    preview_filter_fixture,
)
from config import settings

router = APIRouter(prefix="/spike/agent", tags=["isolated-agent-spike"])


class SpikeTurnRequest(BaseModel):
    message: str = Field(min_length=1)


class SpikeDecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    message: str | None = None


class SpikeResponse(BaseModel):
    session_id: str
    status: str
    decision: dict[str, Any] | None = None
    interrupt: dict[str, Any] | None = None
    last_tool_result: dict[str, Any] | None = None
    events: list[dict[str, Any]] = Field(default_factory=list)


class _CheckpointOnlyModel(BaseChatModel):
    """Compile a graph for checkpoint reads/writes without a provider call."""

    @property
    def _llm_type(self) -> str:
        return "checkpoint-only"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        raise RuntimeError("checkpoint-only graph must not invoke the leader model")


def build_leader_model() -> BaseChatModel:
    """Build through LangChain's provider registry; no product provider is hardcoded."""
    model_id = (os.environ.get("ECONPAPER_SPIKE_MODEL") or "").strip()
    if not model_id:
        raise HTTPException(
            status_code=503,
            detail="ECONPAPER_SPIKE_MODEL is required for the isolated spike",
        )
    try:
        return init_chat_model(model_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"spike model unavailable: {exc}") from exc


def _build_checkpoint_graph(checkpointer):
    """Build the same graph shape for checkpoint-only HTTP operations."""
    return build_spike_agent(
        model=_CheckpointOnlyModel(),
        checkpointer=checkpointer,
    )


def _session_workspace(root: str, session_id: str) -> str:
    """Derive an isolated workspace from LangGraph's thread identity."""
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:24]
    return str(Path(root) / f"session-{digest}")


def _paths(session_id: str) -> tuple[str, SpikeContext]:
    enabled = (os.environ.get("ECONPAPER_ENABLE_AGENT_SPIKE") or "").lower() == "true"
    if not settings.DEBUG or not enabled:
        raise HTTPException(status_code=404, detail="isolated agent spike is disabled")
    db = (os.environ.get("ECONPAPER_SPIKE_DB") or "").strip()
    fixture = (os.environ.get("ECONPAPER_SPIKE_FIXTURE") or "").strip()
    workspace_root = (os.environ.get("ECONPAPER_SPIKE_WORKSPACE") or "").strip()
    if not db or not fixture or not workspace_root:
        raise HTTPException(
            status_code=503,
            detail=(
                "isolated spike requires ECONPAPER_SPIKE_DB, "
                "ECONPAPER_SPIKE_FIXTURE and ECONPAPER_SPIKE_WORKSPACE"
            ),
        )
    if not Path(fixture).is_file():
        raise HTTPException(status_code=400, detail="spike fixture does not exist")
    return db, SpikeContext(
        fixture_csv=fixture,
        workspace=_session_workspace(workspace_root, session_id),
    )


def _serialize_event(event: dict[str, Any]) -> dict[str, Any]:
    event_type = event.get("type")
    data = event.get("data")
    if event_type == "messages" and isinstance(data, tuple) and len(data) == 2:
        message, metadata = data
        node = metadata.get("langgraph_node") if isinstance(metadata, dict) else None
        if isinstance(message, AIMessage):
            return {
                "kind": "message",
                "node": node,
                "message_type": "ai",
                "tool_calls": [dict(call) for call in message.tool_calls],
            }
        if isinstance(message, ToolMessage):
            return {
                "kind": "message",
                "node": node,
                "message_type": "tool",
                "tool_name": message.name,
                "tool_call_id": message.tool_call_id,
                "status": message.status,
                "content": message.content,
            }
    if event_type == "updates" and isinstance(data, dict):
        interrupts = data.get("__interrupt__")
        if interrupts:
            return {
                "kind": "interrupt",
                "value": interrupts[0].value,
                "interrupt_id": interrupts[0].id,
            }
        return {"kind": "update", "nodes": list(data.keys())}
    return {"kind": str(event_type or "unknown")}


def _run_framework_stream(graph, graph_input, config, context) -> list[dict[str, Any]]:
    """Transport adapter only: consume LangGraph's real stream without replaying output."""
    return [
        _serialize_event(event)
        for event in graph.stream(
            graph_input,
            config,
            context=context,
            stream_mode=["updates", "messages"],
            version="v2",
        )
    ]


def _state_event(response: SpikeResponse) -> dict[str, Any]:
    """Project the durable checkpoint into one final transport event."""
    return {
        "kind": "state",
        "session_id": response.session_id,
        "status": response.status,
        "decision": response.decision,
        "interrupt": response.interrupt,
        "last_tool_result": response.last_tool_result,
    }


def _sse_line(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"


def _stream_framework(
    *, db: str, model: BaseChatModel, context: SpikeContext, session_id: str,
    graph_input: Any, config: dict[str, Any]
):
    """Yield framework v2 events as SSE, keeping SQLite open for the stream."""
    with SqliteSaver.from_conn_string(db) as saver:
        graph = build_spike_agent(model=model, checkpointer=saver)
        events: list[dict[str, Any]] = []
        for event in graph.stream(
            graph_input,
            config,
            context=context,
            stream_mode=["updates", "messages"],
            version="v2",
        ):
            compact = _serialize_event(event)
            events.append(compact)
            yield _sse_line(compact)
        response = _response(graph, config, session_id, events, context)
        yield _sse_line(_state_event(response))


def _stream_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }


def _stream_response(
    *, db: str, context: SpikeContext, session_id: str, graph_input: Any,
    config: dict[str, Any], model: BaseChatModel
) -> StreamingResponse:
    return StreamingResponse(
        _stream_framework(
            db=db,
            model=model,
            context=context,
            session_id=session_id,
            graph_input=graph_input,
            config=config,
        ),
        media_type="text/event-stream",
        headers=_stream_headers(),
    )


def _response(
    graph, config, session_id: str, events: list[dict[str, Any]], context: SpikeContext
) -> SpikeResponse:
    snapshot = graph.get_state(config)
    values = dict(snapshot.values or {})
    interrupt_value = None
    for task in snapshot.tasks:
        if task.interrupts:
            interrupt_value = task.interrupts[0].value
            break
    decision = values.get("pending_decision")
    if interrupt_value and not decision:
        request = (interrupt_value.get("action_requests") or [{}])[0]
        args = request.get("args") or {}
        decision = {
            "action": "act",
            "message": request.get("description") or "这个动作需要你的确认。",
            "tool_name": request.get("name"),
            "tool_args": args,
            "preview": preview_filter_fixture(
                fixture_csv=context.fixture_csv,
                column=args.get("column"),
                operator=args.get("operator"),
                value=args.get("value"),
            ),
        }
    status = values.get("current_status", "failed")
    if interrupt_value and status != "paused_by_user":
        status = "waiting_approval"
    return SpikeResponse(
        session_id=session_id,
        status=status,
        decision=decision,
        interrupt=interrupt_value,
        last_tool_result=values.get("last_tool_result"),
        events=events,
    )


@router.post("/{session_id}/turn", response_model=SpikeResponse, include_in_schema=False)
def spike_turn(session_id: str, payload: SpikeTurnRequest) -> SpikeResponse:
    db, context = _paths(session_id)
    config = {"configurable": {"thread_id": session_id}}
    with SqliteSaver.from_conn_string(db) as saver:
        checkpoint_graph = _build_checkpoint_graph(saver)
        existing = checkpoint_graph.get_state(config)
        if existing.next:
            raise HTTPException(status_code=409, detail="spike is waiting for approval")
        graph = build_spike_agent(model=build_leader_model(), checkpointer=saver)
        graph_input = (
            {"messages": [{"role": "user", "content": payload.message}]}
            if existing.values
            else initial_spike_state(payload.message)
        )
        events = _run_framework_stream(graph, graph_input, config, context)
        return _response(graph, config, session_id, events, context)


@router.post("/{session_id}/decision", response_model=SpikeResponse, include_in_schema=False)
def spike_decision(session_id: str, payload: SpikeDecisionRequest) -> SpikeResponse:
    db, context = _paths(session_id)
    config = {"configurable": {"thread_id": session_id}}
    decision: dict[str, Any] = {"type": payload.decision}
    if payload.message:
        decision["message"] = payload.message
    with SqliteSaver.from_conn_string(db) as saver:
        checkpoint_graph = _build_checkpoint_graph(saver)
        snapshot = checkpoint_graph.get_state(config)
        if snapshot.values.get("current_status") == "paused_by_user":
            raise HTTPException(status_code=409, detail="spike is paused; resume before approval")
        if not snapshot.next:
            raise HTTPException(status_code=409, detail="spike has no pending approval")
        graph = build_spike_agent(model=build_leader_model(), checkpointer=saver)
        events = _run_framework_stream(
            graph,
            Command(resume={"decisions": [decision]}),
            config,
            context,
        )
        return _response(graph, config, session_id, events, context)


@router.post("/{session_id}/turn/stream", include_in_schema=False)
def spike_turn_stream(session_id: str, payload: SpikeTurnRequest) -> StreamingResponse:
    db, context = _paths(session_id)
    config = {"configurable": {"thread_id": session_id}}
    with SqliteSaver.from_conn_string(db) as saver:
        checkpoint_graph = _build_checkpoint_graph(saver)
        existing = checkpoint_graph.get_state(config)
        if existing.next:
            raise HTTPException(status_code=409, detail="spike is waiting for approval")
        graph_input = (
            {"messages": [{"role": "user", "content": payload.message}]}
            if existing.values
            else initial_spike_state(payload.message)
        )
    model = build_leader_model()
    return _stream_response(
        db=db,
        context=context,
        session_id=session_id,
        graph_input=graph_input,
        config=config,
        model=model,
    )


@router.post("/{session_id}/decision/stream", include_in_schema=False)
def spike_decision_stream(
    session_id: str, payload: SpikeDecisionRequest
) -> StreamingResponse:
    db, context = _paths(session_id)
    config = {"configurable": {"thread_id": session_id}}
    with SqliteSaver.from_conn_string(db) as saver:
        checkpoint_graph = _build_checkpoint_graph(saver)
        snapshot = checkpoint_graph.get_state(config)
        if snapshot.values.get("current_status") == "paused_by_user":
            raise HTTPException(status_code=409, detail="spike is paused; resume before approval")
        if not snapshot.next:
            raise HTTPException(status_code=409, detail="spike has no pending approval")
    model = build_leader_model()
    decision: dict[str, Any] = {"type": payload.decision}
    if payload.message:
        decision["message"] = payload.message
    return _stream_response(
        db=db,
        context=context,
        session_id=session_id,
        graph_input=Command(resume={"decisions": [decision]}),
        config=config,
        model=model,
    )


@router.post("/{session_id}/pause", response_model=SpikeResponse, include_in_schema=False)
def spike_pause(session_id: str) -> SpikeResponse:
    db, context = _paths(session_id)
    config = {"configurable": {"thread_id": session_id}}
    with SqliteSaver.from_conn_string(db) as saver:
        graph = _build_checkpoint_graph(saver)
        snapshot = graph.get_state(config)
        has_interrupt = any(task.interrupts for task in snapshot.tasks)
        if not snapshot.next or not has_interrupt:
            raise HTTPException(status_code=409, detail="spike has no pending approval")
        if snapshot.values.get("current_status") != "paused_by_user":
            graph.update_state(config, {"current_status": "paused_by_user"})
            # update_state creates a new checkpoint but clears the pending
            # interrupt. Re-run only the framework approval node to recreate
            # that interrupt; no model or tool is invoked by this input.
            graph.invoke(None, config, context=context)
        return _response(graph, config, session_id, [], context)


@router.post("/{session_id}/resume", response_model=SpikeResponse, include_in_schema=False)
def spike_resume(session_id: str) -> SpikeResponse:
    db, context = _paths(session_id)
    config = {"configurable": {"thread_id": session_id}}
    with SqliteSaver.from_conn_string(db) as saver:
        graph = _build_checkpoint_graph(saver)
        snapshot = graph.get_state(config)
        has_interrupt = any(task.interrupts for task in snapshot.tasks)
        if snapshot.values.get("current_status") != "paused_by_user" or not snapshot.next or not has_interrupt:
            raise HTTPException(status_code=409, detail="spike is not paused")
        graph.update_state(config, {"current_status": "waiting_approval"})
        graph.invoke(None, config, context=context)
        return _response(graph, config, session_id, [], context)


@router.get("/{session_id}/state", response_model=SpikeResponse, include_in_schema=False)
def spike_state(session_id: str) -> SpikeResponse:
    db, context = _paths(session_id)
    config = {"configurable": {"thread_id": session_id}}
    with SqliteSaver.from_conn_string(db) as saver:
        graph = _build_checkpoint_graph(saver)
        snapshot = graph.get_state(config)
        if not snapshot.values and not snapshot.next:
            raise HTTPException(status_code=404, detail="spike session not found")
        return _response(graph, config, session_id, [], context)
