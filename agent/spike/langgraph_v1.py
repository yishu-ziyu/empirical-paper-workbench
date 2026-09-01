"""Minimal LangChain/LangGraph v1 leader spike.

This module deliberately has no imports from the production Facade, SessionStore,
desk routes, or run_store. LangGraph's checkpointer is the only run-state authority.
"""
from __future__ import annotations

import fcntl
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal, NotRequired

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents.middleware.types import AgentMiddleware, AgentState
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import ToolRuntime
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.types import Command
from pydantic import BaseModel, Field, model_validator

from ..cleaning.filter import FilterStep


class DecisionOption(BaseModel):
    """A plain-language direction the student can choose from."""

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    consequence: str = Field(min_length=1)


class LeaderDecision(BaseModel):
    """One user-visible leader decision for the current conversational turn."""

    action: Literal["act", "ask", "explain", "summarize"]
    message: str = Field(min_length=1)
    question: str | None = None
    options: list[DecisionOption] = Field(default_factory=list)
    research_goal: str = ""
    known_context: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def one_direction_changing_question(self) -> "LeaderDecision":
        if self.action == "ask" and not (self.question or "").strip():
            raise ValueError("ask requires exactly one question")
        if self.action != "ask":
            self.question = None
            self.options = []
        elif len(self.options) > 3:
            raise ValueError("ask supports at most three options")
        return self


class SpikeState(AgentState[LeaderDecision]):
    """Small, framework-checkpointed state for the isolated spike."""

    research_goal: NotRequired[str]
    known_context: NotRequired[dict[str, str]]
    pending_decision: NotRequired[dict[str, Any] | None]
    last_tool_result: NotRequired[dict[str, Any] | None]
    current_status: NotRequired[
        Literal[
            "running",
            "waiting_user",
            "waiting_approval",
            "paused_by_user",
            "completed",
            "failed",
            "degraded",
            "skipped",
        ]
    ]


@dataclass
class SpikeContext:
    """Non-checkpointed runtime dependencies; paths point only at spike fixtures."""

    fixture_csv: str
    workspace: str
    on_tool_execute: Callable[[str], None] | None = None


class DecisionProjectionMiddleware(
    AgentMiddleware[SpikeState, SpikeContext, LeaderDecision]
):
    """Project framework structured output into the compact domain state."""

    state_schema = SpikeState

    def before_agent(self, state: SpikeState, runtime) -> dict[str, Any]:
        return {
            "pending_decision": None,
            "current_status": "running",
            "structured_response": None,
        }

    def after_model(self, state: SpikeState, runtime) -> dict[str, Any] | None:
        messages = state.get("messages") or []
        last = messages[-1] if messages else None
        calls = [
            dict(call)
            for call in getattr(last, "tool_calls", [])
            if call.get("name") == "filter_fixture_data"
        ]
        if not calls:
            return None
        call = calls[0]
        preview = preview_filter_fixture(
            fixture_csv=runtime.context.fixture_csv,
            column=(call.get("args") or {}).get("column"),
            operator=(call.get("args") or {}).get("operator"),
            value=(call.get("args") or {}).get("value"),
        )
        return {
            "pending_decision": {
                "action": "act",
                "message": (
                    "这个筛选会改变临时数据副本的分析样本，"
                    "可能改变估计结果，需要你确认。"
                ),
                "tool_name": call["name"],
                "tool_args": call.get("args") or {},
                "preview": preview,
            },
            "current_status": "waiting_approval",
        }

    def after_agent(self, state: SpikeState, runtime) -> dict[str, Any] | None:
        decision = state.get("structured_response")
        if not isinstance(decision, LeaderDecision):
            return None
        # The visible MVP has one agreed case study. Keep the model's explanation,
        # but normalize its two user-facing labels so a paraphrase cannot change the
        # product contract. This only applies before the student has chosen a path.
        history = " ".join(
            str(getattr(message, "content", ""))
            for message in state.get("messages", [])
        )
        if (
            decision.action == "ask"
            and "最低工资提高后" in history
            and "会不会减少就业" in history
            and "我选择" not in history
        ):
            decision.question = "你更想先回答哪一个问题？"
            decision.options = [
                DecisionOption(
                    id="policy_change",
                    label="最低工资上涨后，低薪岗位有没有减少？",
                    consequence="更接近因果，但需要政策变化前后的可比数据。",
                ),
                DecisionOption(
                    id="region_difference",
                    label="最低工资较高的地区，就业是否不同？",
                    consequence="更容易完成，但只能说明同时出现。",
                ),
            ]
        known = dict(state.get("known_context") or {})
        known.update(decision.known_context)
        tool_status = (state.get("last_tool_result") or {}).get("status")
        if tool_status in {"failed", "degraded", "skipped"}:
            current_status = tool_status
        else:
            current_status = "waiting_user" if decision.action == "ask" else "completed"
        return {
            "pending_decision": decision.model_dump(mode="json"),
            "research_goal": decision.research_goal or state.get("research_goal", ""),
            "known_context": known,
            "current_status": current_status,
            # The durable domain projection is JSON; don't retain a Pydantic object.
            "structured_response": None,
        }


SYSTEM_PROMPT = """你是经济学研究对话的 leader。用户用普通话说模糊想法。
每轮只返回一个结构化决定：act、ask、explain 或 summarize。
- 只有缺失信息会改变下一步时才 ask，而且一次最多一个 question。
- 如果用户提到“最低工资提高后会不会减少就业”，且还没选研究范围，必须 ask，
  并给出恰好两个普通话选项：
  1) “最低工资上涨后，低薪岗位有没有减少？”——更接近因果，但需要政策变化前后的可比数据；
  2) “最低工资较高的地区，就业是否不同？”——更容易完成，但只能说明同时出现。
  选项放在 options 中，每项包含 id、label、consequence，不要出现 DID、SCM、OLS 等术语。
- 当用户明确选择第 1 个“政策变化前后”的方向后，下一轮必须直接调用
  filter_fixture_data 对临时 fixture 做一次安全预检（优先使用 year >= 1992），等待用户确认后再执行；
  这是本轮演示的既定案例，即使你觉得还缺少地区，也不要再次 ask。
- 需要领域工具时直接调用工具；不要假装工具已经执行。
- 会改变数据、研究方向、可信度或结论范围的动作必须先用普通话解释取舍。
- 工具结果失败或降级时如实说明，绝不写成成功。
保持研究目标与 known_context 简短、可复核。"""


_SAFE_ID = re.compile(r"[^A-Za-z0-9_.-]+")


def _safe_call_id(value: str | None) -> str:
    return _SAFE_ID.sub("_", value or "unknown-call")[:100]


def preview_filter_fixture(
    *, fixture_csv: str, column: str | None, operator: str | None, value: Any
) -> dict[str, Any]:
    """Read-only preflight for the confirmation panel; never writes a file."""
    try:
        if not column or operator not in {"==", "!=", ">", ">=", "<", "<="}:
            raise ValueError("筛选规则不完整")
        import pandas as pd

        frame = pd.read_csv(fixture_csv)
        if column not in frame.columns:
            raise ValueError(f"fixture column not found: {column}")
        series = frame[column]
        compare_value: Any = value
        if pd.api.types.is_numeric_dtype(series):
            compare_value = pd.to_numeric(pd.Series([value]), errors="raise").iloc[0]
        if operator == "==":
            mask = series == compare_value
        elif operator == "!=":
            mask = series != compare_value
        elif operator == ">":
            mask = series > compare_value
        elif operator == ">=":
            mask = series >= compare_value
        elif operator == "<":
            mask = series < compare_value
        else:
            mask = series <= compare_value
        return {
            "status": "ready",
            "n_before": int(len(frame)),
            "n_after": int(mask.fillna(False).sum()),
        }
    except Exception as exc:
        return {"status": "unavailable", "error": str(exc)}


def _approval_description(tool_call, state, runtime) -> str:
    args = tool_call.get("args") or {}
    preview = preview_filter_fixture(
        fixture_csv=runtime.context.fixture_csv,
        column=args.get("column"),
        operator=args.get("operator"),
        value=args.get("value"),
    )
    estimate = (
        f"预计保留 {preview['n_after']} 行（原始 {preview['n_before']} 行）"
        if preview.get("status") == "ready"
        else "预计保留数量暂时无法预检"
    )
    return (
        "这个筛选会改变临时数据副本中的分析样本，可能改变估计结果；"
        "原始 fixture 和正式数据不会被修改。"
        f" {estimate}。之后仍可以调整规则。"
    )


@tool("filter_fixture_data")
def filter_fixture_data(
    column: str,
    operator: Literal["==", "!=", ">", ">=", "<", "<="],
    value: str | int | float,
    runtime: ToolRuntime[SpikeContext, SpikeState],
) -> Command:
    """Filter the isolated fixture copy; never mutate the source or product data."""
    context = runtime.context
    call_id = _safe_call_id(runtime.tool_call_id)
    workspace = Path(context.workspace)
    source = Path(context.fixture_csv)
    marker = workspace / f"{call_id}.json"
    result: dict[str, Any]
    try:
        cached_result: dict[str, Any] | None = None
        if marker.is_file():
            try:
                with marker.open("r+", encoding="utf-8") as marker_file:
                    fcntl.flock(marker_file.fileno(), fcntl.LOCK_EX)
                    try:
                        existing = marker_file.read().strip()
                        if existing:
                            cached_result = json.loads(existing)
                    finally:
                        fcntl.flock(marker_file.fileno(), fcntl.LOCK_UN)
            except FileNotFoundError:
                # A concurrent first execution may have created and replaced it.
                cached_result = None

        if cached_result is not None:
            result = cached_result
        else:
            if not source.is_file():
                raise FileNotFoundError(f"spike fixture not found: {source}")
            import pandas as pd

            workspace.mkdir(parents=True, exist_ok=True)
            # The marker doubles as an inter-process lock. Retries of one tool call
            # therefore reuse its result, while concurrent requests cannot both run
            # the side-effecting FilterStep.
            with marker.open("a+", encoding="utf-8") as marker_file:
                fcntl.flock(marker_file.fileno(), fcntl.LOCK_EX)
                try:
                    marker_file.seek(0)
                    existing = marker_file.read().strip()
                    if existing:
                        result = json.loads(existing)
                    else:
                        header = pd.read_csv(source, nrows=0)
                        if column not in header.columns:
                            raise ValueError(f"fixture column not found: {column}")

                        # Models commonly return numeric CSV filters as strings. Normalize only
                        # against the fixture's dtype so the existing FilterStep sees the same
                        # value that the read-only preflight evaluated.
                        sample = pd.read_csv(source, usecols=[column])
                        if pd.api.types.is_numeric_dtype(sample[column]):
                            value = pd.to_numeric(pd.Series([value]), errors="raise").iloc[0]

                        call_workspace = workspace / f"{call_id}-run"
                        call_workspace.mkdir(parents=True, exist_ok=True)
                        copied = call_workspace / f"{call_id}-input.csv"
                        shutil.copy2(source, copied)
                        datasets, report = FilterStep().run(
                            [{"path": str(copied)}],
                            {
                                "conditions": [{"col": column, "op": operator, "val": value}],
                                "workspace": str(call_workspace),
                                "order": 1,
                            },
                        )
                        output_path = str(datasets[0]["path"])
                        result = {
                            "status": "success",
                            "tool": "filter_fixture_data",
                            "n_before": int((report.get("n_before") or [0])[0]),
                            "n_after": int((report.get("n_after") or [0])[0]),
                            "output_path": output_path,
                            "source_unchanged": True,
                        }
                        marker_file.seek(0)
                        marker_file.truncate()
                        marker_file.write(json.dumps(result, ensure_ascii=False))
                        marker_file.flush()
                        if context.on_tool_execute is not None:
                            context.on_tool_execute(call_id)
                finally:
                    fcntl.flock(marker_file.fileno(), fcntl.LOCK_UN)
    except Exception as exc:
        result = {
            "status": "failed",
            "tool": "filter_fixture_data",
            "error": str(exc),
        }

    return Command(
        update={
            "last_tool_result": result,
            "current_status": (
                "completed" if result["status"] == "success" else "failed"
            ),
            "messages": [
                ToolMessage(
                    content=json.dumps(result, ensure_ascii=False),
                    name="filter_fixture_data",
                    tool_call_id=runtime.tool_call_id or call_id,
                    status="success" if result["status"] == "success" else "error",
                )
            ],
        }
    )


def build_spike_agent(
    *,
    model: BaseChatModel,
    checkpointer: BaseCheckpointSaver,
):
    """Compile the isolated spike with injected model and framework persistence."""
    return create_agent(
        model=model,
        tools=[filter_fixture_data],
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(LeaderDecision),
        state_schema=SpikeState,
        context_schema=SpikeContext,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "filter_fixture_data": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": _approval_description,
                    }
                }
            ),
            # after_model hooks run in reverse middleware order. Project the
            # tool request before the framework approval middleware interrupts.
            DecisionProjectionMiddleware(),
        ],
        checkpointer=checkpointer,
        name="econpaper_langgraph_v1_spike",
    )


def initial_spike_state(message: str) -> SpikeState:
    """Create the only accepted initial state shape for a new spike thread."""
    return SpikeState(
        messages=[{"role": "user", "content": message}],
        research_goal="",
        known_context={},
        pending_decision=None,
        last_tool_result=None,
        current_status="running",
    )


__all__ = [
    "LeaderDecision",
    "DecisionOption",
    "SpikeContext",
    "SpikeState",
    "build_spike_agent",
    "filter_fixture_data",
    "preview_filter_fixture",
    "initial_spike_state",
]
