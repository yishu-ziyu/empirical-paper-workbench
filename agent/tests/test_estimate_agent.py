"""估计 Agent 测试（Phase A）。

LLM 一律用 pydantic-ai 的 TestModel / FunctionModel，绝不真调网络：
- TestModel：自动按 output_type 产结构化输出，验证全链路映射回 state 契约；
- FunctionModel：脚本化"先调工具、再给最终结果"，验证工具真跑沙箱、
  RLM 截断落盘、输出映射不编造数字。

估计 Agent 是可选臂：provider 不可用返回 None，异常回退固定分派并记
degradation，输出 state 键与固定分派完全一致（results / estimate）。
"""
from __future__ import annotations

import os
import sys

import pandas as pd
import pytest

from agent.engine.estimate_agent import (
    EstimateAgentOutput,
    build_estimate_agent,
    estimate_output_from_agent,
    profiling_text_from_state,
    provider_ready,
    run_estimate_via_agent,
    _truncate_to_file,
    _usage_limits,
)
from agent.engine.sandbox import KernelSession, SubprocessSession
from agent.llm.router import LLMConfig, MINIMAX_BASE_URL
from agent.nodes.estimate import estimate
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.test import TestModel


def make_state(tmp_path, **spec_extra) -> dict:
    """带真实 CSV 的最小 estimate state（tmp 文件，不碰 fixtures）。"""
    df = pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], "x": [0, 1, 0, 1, 0, 1]})
    csv_path = tmp_path / "main.csv"
    df.to_csv(csv_path, index=False)
    spec = {"formula": "y ~ x", "treatment": "x", "outcome": "y"}
    spec.update(spec_extra)
    return {"csv_path": str(csv_path), "main_specification": spec}


PASS_OUTPUT = EstimateAgentOutput(
    method="ols",
    final_code="import pandas as pd\n...",
    coefficient=0.5,
    se=0.1,
    pvalue=0.02,
    n_obs=6,
    stars=2,
    verdict="pass",
    iterations=2,
    summary="OLS(y ~ x) 跑通，x 系数 0.5。",
)


# ===========================================================================
# provider 判定：mock / 未配 key 不启用
# ===========================================================================

def test_provider_mock_not_ready():
    assert provider_ready(LLMConfig(provider="mock", model="default")) is False


def test_provider_minimax_needs_key():
    assert provider_ready(LLMConfig(provider="minimax", model="MiniMax-M3", api_key=None)) is False
    ready = LLMConfig(provider="minimax", model="MiniMax-M3", api_key="k", base_url=MINIMAX_BASE_URL)
    assert provider_ready(ready) is True


def test_provider_openai_compat_allowed():
    assert provider_ready(LLMConfig(provider="openai", model="gpt-x", api_key="k")) is True
    assert provider_ready(LLMConfig(provider="anthropic", model="claude", api_key="k")) is False


def test_usage_limits_constructs():
    """迭代预算上限构造成功（字段名随 pydantic-ai 版本变化已做兼容）。"""
    assert _usage_limits() is not None


# ===========================================================================
# 输出映射：state 契约与"不编造数字"红线
# ===========================================================================

def test_mapping_pass_keeps_state_contract():
    spec = {"formula": "y ~ x", "treatment": "x", "outcome": "y"}
    out = estimate_output_from_agent(PASS_OUTPUT, method="ols", spec=spec)
    # 顶层 state 键与固定分派完全一致
    assert set(out.keys()) == {"results", "estimate"}
    payload = out["estimate"]
    assert payload["status"] == "ok"
    assert payload["produced_by"] == "estimate"
    assert payload["estimator"] == "estimate_agent"
    assert payload["method"] == "ols"
    assert payload["treatment"] == "x"
    assert payload["treatment_row"] == "| x | 0.5000 | 0.1000 | 0.0200 |"
    assert payload["coef"] == 0.5 and payload["se"] == 0.1 and payload["p"] == 0.02
    assert payload["n"] == 6 and payload["stars"] == 2
    # results 表格式与固定分派一致（结果章按这个引用）
    assert "# 主结果" in out["results"]
    assert "| 变量 | 系数 | SE | p |" in out["results"]
    assert "| x | 0.5000 | 0.1000 | 0.0200 |" in out["results"]
    assert "N = 6" in out["results"]


def test_mapping_fail_writes_no_numbers():
    """verdict=fail：镜像 error payload，treatment_row 留空，不写 coef/se/p。"""
    fail = EstimateAgentOutput(
        method="iv",
        final_code="",
        verdict="fail",
        iterations=3,
        summary="缺工具变量列，无法识别。",
    )
    out = estimate_output_from_agent(fail, method="iv", spec={"treatment": "treatment"})
    payload = out["estimate"]
    assert payload["status"] == "error"
    assert payload["produced_by"] == "estimate"
    assert payload["treatment_row"] == ""
    for key in ("coef", "se", "p", "n", "stars"):
        assert key not in payload
    assert "缺工具变量列" in payload["error"]
    assert "| 变量 | 系数 | SE | p |" not in out["results"]
    assert "0.5" not in out["results"]


# ===========================================================================
# FunctionModel：工具真跑沙箱 + RLM 截断落盘
# ===========================================================================

def _function_model(script):
    """两次请求：先调 run_python 跑脚本，再回最终结构化输出。"""
    calls = {"n": 0}

    def _final_with(tool_text: str) -> str:
        # 把工具输出回填进 summary，模拟"系数来自真实运行"
        out = PASS_OUTPUT.model_copy()
        out.summary = f"tool said: {tool_text[:80]}"
        return out.model_dump_json()

    def _model(messages, info):
        calls["n"] += 1
        if calls["n"] == 1:
            return ModelResponse(
                parts=[ToolCallPart(tool_name="run_python", args={"code": script})]
            )
        # 第二次请求能看到上一次工具回传的内容
        last_texts = "".join(
            str(getattr(part, "content", ""))
            for msg in messages
            for part in (getattr(msg, "parts", None) or [])
            if type(part).__name__ == "ToolReturnPart"
        )
        return ModelResponse(parts=[TextPart(content=_final_with(last_texts))])

    return FunctionModel(_model), calls


def test_function_model_run_python_executes_in_sandbox(tmp_path):
    model, calls = _function_model("print(6 * 7)")
    agent = build_estimate_agent(model=model)
    out = run_estimate_via_agent(agent, make_state(tmp_path), session=SubprocessSession(str(tmp_path)))
    assert calls["n"] == 2
    payload = out["estimate"]
    assert payload["produced_by"] == "estimate"
    assert payload["treatment_row"] == "| x | 0.5000 | 0.1000 | 0.0200 |"
    # 工具回传里带上了沙箱真实输出（42 来自 run_python，不是模型编的）
    assert "tool said:" in payload["summary"]
    assert "42" in payload["summary"]


def test_run_python_truncates_and_dumps_to_workdir(tmp_path):
    """RLM/compaction 纪律：>2000 字符输出只回前 2000 字符，全文落盘 workdir 并回传路径。"""
    long_text = "x" * 5000
    returned = _truncate_to_file(long_text, str(tmp_path), attempts=1)
    assert len(returned) <= 2000 + 120  # 2000 字符 + 1 行截断说明
    assert "已截断" in returned
    assert "5000 字符" in returned
    dumped = tmp_path / "sandbox_output_attempt1.txt"
    assert dumped.is_file()
    assert dumped.read_text(encoding="utf-8") == long_text


def test_run_python_short_output_untouched(tmp_path):
    """≤2000 字符的输出原样返回，不落盘。"""
    text = "short output\n" * 10
    returned = _truncate_to_file(text, str(tmp_path), attempts=1)
    assert returned == text
    assert not (tmp_path / "sandbox_output_attempt1.txt").exists()


def test_serialize_conversation_truncates_tool_results():
    """序列化器：工具结果截 2000 字符（对齐 compaction.md），其余角色逐条保留。"""
    from agent.engine.estimate_agent import serialize_conversation

    class UserPromptPart:
        def __init__(self, content):
            self.content = content

    class ToolReturnPart:
        def __init__(self, tool_name, content):
            self.tool_name = tool_name
            self.content = content

    class Msg:
        def __init__(self, parts):
            self.parts = parts

    long = "y" * 5000
    msgs = [
        Msg([UserPromptPart("跑 DiD")]),
        Msg([ToolReturnPart("run_python", long)]),
    ]
    text = serialize_conversation(msgs)
    assert "[User]: 跑 DiD" in text
    assert "[Tool result] run_python:" in text
    assert "y" * 2001 not in text
    assert "原长 5000 字符" in text


def test_compact_history_six_section_deterministic():
    """六段结构化摘要：只填可抽出的事实，模板六段齐全。"""
    from agent.engine.estimate_agent import compact_history_six_section, serialize_conversation

    class ToolCallPart:
        def __init__(self, tool_name, args):
            self.tool_name = tool_name
            self.args = args

    class ToolReturnPart:
        def __init__(self, tool_name, content):
            self.tool_name = tool_name
            self.content = content

    class Msg:
        def __init__(self, parts):
            self.parts = parts

    class Args:
        def __init__(self, args_json):
            self.args_json = args_json

    msgs = [
        Msg([ToolCallPart("run_python", Args('{"code": "df.shape"}'))]),
        Msg([ToolReturnPart("run_python", "ok")]),
    ]
    text = compact_history_six_section(msgs, method="did", treatment="treat")
    for section in ("## Goal", "## Constraints & Preferences", "## Progress",
                    "## Key Decisions", "## Next Steps", "## Critical Context"):
        assert section in text
    assert "did" in text and "treat" in text
    assert "df.shape" in text
    assert serialize_conversation(msgs).count("[Tool result]") == 1


def test_function_model_truncation_flows_to_model(tmp_path):
    script = "\n".join(f"print('row-{i:03d} ' + 'x' * 20)" for i in range(200))
    model, _calls = _function_model(script)
    agent = build_estimate_agent(model=model)
    out = run_estimate_via_agent(agent, make_state(tmp_path), session=SubprocessSession(str(tmp_path)))
    dumped = tmp_path / "sandbox_output_attempt1.txt"
    assert dumped.is_file(), "超长沙箱输出应落盘"
    assert out["estimate"]["status"] == "ok"


# ===========================================================================
# TestModel：全链路映射回 state 契约
# ===========================================================================

def test_test_model_full_run_state_contract(tmp_path):
    agent = build_estimate_agent(model=TestModel())
    out = run_estimate_via_agent(agent, make_state(tmp_path), session=SubprocessSession(str(tmp_path)))
    assert set(out.keys()) == {"results", "estimate"}
    payload = out["estimate"]
    assert payload["status"] == "ok"          # TestModel 取 Literal 第一个值 pass
    assert payload["produced_by"] == "estimate"
    assert payload["estimator"] == "estimate_agent"
    assert payload["method"] == "ols"
    assert "| 变量 | 系数 | SE | p |" in out["results"]


@pytest.mark.skipif(
    __import__("importlib.util", fromlist=["util"]).find_spec("ipykernel") is None,
    reason="持久内核后端需要 ipykernel",
)
def test_test_model_full_run_with_kernel_session(tmp_path):
    """dev 主后端贯通：TestModel + 持久内核会话跑完整个工具链。"""
    state = make_state(tmp_path)
    session = KernelSession(str(tmp_path))
    try:
        agent = build_estimate_agent(model=TestModel())
        out = run_estimate_via_agent(agent, state, session=session)
    finally:
        session.close()
    assert out["estimate"]["produced_by"] == "estimate"


# ===========================================================================
# estimate 节点：开关 / 回退 / degradation
# ===========================================================================

@pytest.fixture
def force_agent_enabled(monkeypatch):
    monkeypatch.setattr("agent.nodes.estimate._estimate_agent_enabled", lambda: True)


def test_estimate_node_agent_success_short_circuits(tmp_path, force_agent_enabled, monkeypatch):
    """Agent 臂成功：原样返回其契约输出，不走固定分派。"""
    canned = {
        "results": "# 主结果\n\n| 变量 | 系数 | SE | p |\n|------|------|----|---|\n| x | 0.5000 | 0.1000 | 0.0200 |",
        "estimate": {"status": "ok", "produced_by": "estimate", "estimator": "estimate_agent"},
    }
    monkeypatch.setattr("agent.engine.estimate_agent.run_estimate_agent", lambda state: canned)
    out = estimate(make_state(tmp_path))
    assert out is canned
    assert out["estimate"]["estimator"] == "estimate_agent"


def test_estimate_node_agent_error_falls_back_with_degradation(tmp_path, force_agent_enabled, monkeypatch):
    """Agent 抛异常：回退固定分派，payload 记 degradation（facade 条目模式）。"""
    def boom(_state):
        raise RuntimeError("sandbox exploded")

    monkeypatch.setattr("agent.engine.estimate_agent.run_estimate_agent", boom)
    out = estimate(make_state(tmp_path))
    payload = out["estimate"]
    assert payload["status"] == "ok"                      # 固定分派照常出表
    assert payload["estimator"] == "statspai.feols"       # 没有被 Agent 污染
    entries = payload["degradations"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["node"] == "run_estimate"
    assert entry["reason"].startswith("estimate_agent_failed")
    assert "sandbox exploded" in entry["reason"]
    assert entry["fallback"] == "fixed_dispatch"
    assert entry["visible"] is True
    assert entry["timestamp"]


def test_estimate_node_agent_none_no_degradation(tmp_path, force_agent_enabled, monkeypatch):
    """provider 不可用（返回 None）：静默回退，不算 degradation。"""
    monkeypatch.setattr("agent.engine.estimate_agent.run_estimate_agent", lambda state: None)
    out = estimate(make_state(tmp_path))
    assert out["estimate"]["estimator"] == "statspai.feols"
    assert "degradations" not in out["estimate"]


def test_estimate_node_disabled_by_default(tmp_path, monkeypatch):
    """默认关（env 未设）：行为与 Phase A 前一致，无 degradations 键。"""
    monkeypatch.delenv("ECONPAPER_ESTIMATE_AGENT", raising=False)
    out = estimate(make_state(tmp_path))
    payload = out["estimate"]
    assert payload["status"] == "ok"
    assert payload["estimator"] == "statspai.feols"
    assert "degradations" not in payload


def test_estimate_agent_enabled_env_flag(monkeypatch):
    """agent/config 的 env 覆盖：ECONPAPER_ESTIMATE_AGENT=1 打开 / 未设关闭。"""
    import types

    # 绕开 backend/config.py 同名冲突：让 sys.modules["config"] 暂无旗标
    monkeypatch.setitem(sys.modules, "config", types.SimpleNamespace())
    monkeypatch.delitem(sys.modules, "_econpaper_agent_config", raising=False)
    import agent.nodes.estimate as est_mod

    monkeypatch.setenv("ECONPAPER_ESTIMATE_AGENT", "1")
    assert est_mod._estimate_agent_enabled() is True
    monkeypatch.delenv("ECONPAPER_ESTIMATE_AGENT", raising=False)
    monkeypatch.delitem(sys.modules, "_econpaper_agent_config", raising=False)
    assert est_mod._estimate_agent_enabled() is False


# ===========================================================================
# profiling 摘要（数据只进沙箱，进上下文的是摘要）
# ===========================================================================

def test_profiling_text_from_state():
    state = {
        "data_summary": "CHARLS 2018 面板",
        "cleaning_report": {
            "steps": [
                {
                    "name": "profiling",
                    "status": "success",
                    "report": {
                        "profiles": [
                            {
                                "n_rows": 100,
                                "n_cols": 3,
                                "dataset_type": "generic",
                                "variables": {
                                    "income": {"dtype": "float64", "missing_rate": 0.05, "n_unique": 90, "is_numeric": True},
                                    "age": {"dtype": "int64", "missing_rate": 0.0, "n_unique": 40, "is_numeric": True},
                                },
                            }
                        ]
                    },
                }
            ]
        },
    }
    text = profiling_text_from_state(state)
    assert text.startswith("data_summary: CHARLS 2018 面板")
    assert "rows=100" in text
    assert "income" in text and "missing_rate=0.05" in text


def test_profiling_text_empty_state():
    assert profiling_text_from_state({}) == ""
