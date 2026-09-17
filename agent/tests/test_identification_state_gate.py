"""#40 增量一：识别诊断的三轴状态与执行许可（验收契约 C1–C4、C7）。

契约：docs/acceptance/identification-state-gate.md

这一组用例钉住的是「同一个 state 只允许有一个判定」，以及被修掉的三处旧语义：
全 warn 掉成 0 星、全跑不成写成通过、效应显著性冒充设计有效性。
"""
import os

import pandas as pd
import pytest

from agent.engine import identification_state as ids
from agent.engine.identification_state import (
    ASSESSMENT_INSUFFICIENT_EVIDENCE,
    ASSESSMENT_NOT_APPLICABLE,
    ASSESSMENT_RISK_FOUND,
    ASSESSMENT_RISK_NOT_FOUND,
    EXECUTION_NOT_RUN,
    PERMISSION_ALLOW,
    PERMISSION_CONFIRM,
    PERMISSION_FORBID,
    assess_diagnostics,
    design_validity_diagnostics,
    identification_decision,
    identification_hard_block,
    permission_is,
)
from agent.nodes.identification_verify import _diag_did, identification_verify


@pytest.fixture(autouse=True)
def _restore_forced_mock_env():
    """兜住 ``agent.eval.run_task`` 的模块级环境副作用。

    那个模块在 import 期执行 ``os.environ["ECONPAPER_LLM"] = "mock"``（离线评测
    必须强制 mock，是它自己的设计），但这是**进程级**副作用：只要同进程里先跑到
    它，后面 ``test_llm_router`` 里依赖 ``GENERATE_LLM_PROVIDER`` 的用例就全部
    退化成 mock（ECONPAPER_LLM=mock 在 router 优先级第 1 位）。
    本文件是第一个 import 它的测试，所以在这里清干净，避免把测试顺序变成隐式依赖。
    """
    before = os.environ.get("ECONPAPER_LLM")
    yield
    if before is None:
        os.environ.pop("ECONPAPER_LLM", None)
    else:
        os.environ["ECONPAPER_LLM"] = before


# ---------------------------------------------------------------------------
# C1 全 warn 不再是硬阻断
# ---------------------------------------------------------------------------

def test_all_warning_is_not_a_hard_block():
    assessed = assess_diagnostics(
        [{"test": "check_a", "status": "warn"}, {"test": "check_b", "status": "warn"}]
    )

    assert assessed["star_rating"] == 2, "全 warn 不该掉进 0 星"
    assert assessed["assessment"] == ASSESSMENT_RISK_FOUND
    assert assessed["passed"] is True  # 没有硬失败项


def test_all_warning_permissions_continue_but_do_not_promote():
    state = {
        "research_direction": {"method": "iv"},
        "identification_diag": {
            "strategy": "iv",
            "diagnostics": [{"test": "iv_diag", "status": "warn"}],
            "execution": "completed",
            "assessment": ASSESSMENT_RISK_FOUND,
            "passed": True,
            "star_rating": 2,
        },
        "star_rating": 2,
    }
    decision = identification_decision(state)

    assert decision["hard_block"] is False, "有风险不等于硬阻断"
    perms = decision["permissions"]
    assert perms["continue_to_estimate"] == PERMISSION_ALLOW
    # 「要劝、用户可越」：因果可写但必须越过留痕，主结果不给干净许可。
    assert perms["causal_language"] == PERMISSION_CONFIRM
    assert perms["promote_main_result"] == PERMISSION_CONFIRM
    assert perms["requires_disclosure"] is True


def test_all_warning_node_output_is_not_identification_failed(monkeypatch, tmp_path):
    csv_path = tmp_path / "panel.csv"
    pd.DataFrame({"y": [1.0, 2.0], "x": [0.0, 1.0]}).to_csv(csv_path, index=False)

    def fake_iv(df, d, diagnostics, report_lines):
        diagnostics.append({"test": "iv_diag", "status": "warn", "first_stage_F": 6.0})
        report_lines.append("IV 诊断: first-stage F=6.0，弱工具风险。")
        return False

    monkeypatch.setitem(
        __import__(
            "agent.nodes.identification_verify", fromlist=["_DISPATCH"]
        )._DISPATCH,
        "iv",
        fake_iv,
    )
    result = identification_verify(
        {
            "csv_path": str(csv_path),
            "research_direction": {
                "method": "iv",
                "outcome": "y",
                "endogenous": "x",
                "instrument": "x",
            },
        }
    )

    assert result["star_rating"] == 2
    assert result["identification_failed"] is False, "全 warn 不该被升级成硬阻断"
    diag = result["identification_diag"]
    assert diag["assessment"] == ASSESSMENT_RISK_FOUND
    assert diag["passed"] is True


# ---------------------------------------------------------------------------
# C2 全 error / 全 skipped 是未知，不是通过
# ---------------------------------------------------------------------------

def test_all_error_is_unknown_not_passed():
    assessed = assess_diagnostics([{"test": "check_a", "status": "error"}])

    assert assessed["star_rating"] is None
    assert assessed["passed"] is None, "尚未评估不等于通过"
    assert assessed["assessment"] == ASSESSMENT_INSUFFICIENT_EVIDENCE


def test_all_skipped_is_unknown_not_passed():
    assessed = assess_diagnostics([{"test": "check_a", "status": "skipped"}])

    assert assessed["star_rating"] is None
    assert assessed["passed"] is None
    assert assessed["assessment"] == ASSESSMENT_INSUFFICIENT_EVIDENCE
    assert assessed["execution"] == EXECUTION_NOT_RUN


def test_no_diagnostics_at_all_is_not_applicable():
    assessed = assess_diagnostics([])

    assert assessed["star_rating"] is None
    assert assessed["passed"] is None
    assert assessed["assessment"] == ASSESSMENT_NOT_APPLICABLE


def _block_statspai_import(monkeypatch):
    """Force every ``import statspai`` to raise ModuleNotFoundError."""
    import sys

    real_import = __import__

    def blocked(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "statspai" or (isinstance(name, str) and name.startswith("statspai.")):
            raise ModuleNotFoundError("No module named 'statspai'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", blocked)
    monkeypatch.delitem(sys.modules, "statspai", raising=False)
    for key in [k for k in list(sys.modules) if k.startswith("statspai.")]:
        monkeypatch.delitem(sys.modules, key, raising=False)


def test_unrunnable_node_reports_unknown_and_never_claims_passed(tmp_path, monkeypatch):
    csv_path = tmp_path / "panel.csv"
    pd.DataFrame(
        {
            "y": [1.0, 1.2, 2.0, 2.4],
            "treat": [0, 0, 1, 1],
            "year": [2000, 2001, 2000, 2001],
            "id": [1, 1, 2, 2],
        }
    ).to_csv(csv_path, index=False)
    _block_statspai_import(monkeypatch)

    result = identification_verify(
        {
            "csv_path": str(csv_path),
            "research_direction": {
                "method": "did",
                "outcome": "y",
                "treatment": "treat",
                "time_col": "year",
                "id_col": "id",
            },
        }
    )
    diag = result["identification_diag"]

    assert diag["passed"] is None
    assert diag["assessment"] == ASSESSMENT_INSUFFICIENT_EVIDENCE
    assert diag["execution"] in {"failed", "not_run"}
    assert result["identification_failed"] is False
    assert result["star_rating"] is None

    report = diag["report"]
    assert "检查通过" not in report
    assert "该方法不成立" not in report
    assert "尚未核查" in report


def test_star_cannot_upgrade_a_diagnosis_whose_checks_never_ran():
    """星级回填只对「完全没有明细」的旧快照生效。

    有明细却全 skipped，说明检查一条都没跑成 —— 那种 state 不能因为记着 3 星就拿到
    干净因果许可与主结果晋升，否则「未知不许伪装成通过」这条就被绕过了。
    """
    decision = identification_decision(
        {
            "star_rating": 3,
            "identification_diag": {
                "strategy": "did",
                "star_rating": 3,
                "diagnostics": [{"test": "bacon_decomposition", "status": "skipped"}],
            },
        }
    )

    assert decision["assessment"] == ASSESSMENT_INSUFFICIENT_EVIDENCE
    assert decision["passed"] is None
    assert decision["permissions"]["causal_language"] == PERMISSION_FORBID
    assert decision["permissions"]["promote_main_result"] != PERMISSION_ALLOW
    assert decision["permissions"]["requires_disclosure"] is True


def test_partial_run_never_claims_nothing_was_found():
    """一条检查通过、另一条没跑成：不能报「没发现问题」。"""
    assessed = assess_diagnostics(
        [{"test": "check_a", "status": "pass"}, {"test": "check_b", "status": "error"}]
    )

    assert assessed["passed"] is None
    assert assessed["assessment"] == ASSESSMENT_INSUFFICIENT_EVIDENCE
    assert assessed["execution"] == "partial"


def test_star_only_snapshot_still_backfills_from_the_star():
    """只有星级、没有明细的旧快照仍按星级回填（早期会话与既有夹具靠它）。"""
    decision = identification_decision({"star_rating": 2})

    assert decision["assessment"] == ASSESSMENT_RISK_FOUND
    assert decision["permissions"]["causal_language"] == PERMISSION_CONFIRM


def test_unknown_state_still_allows_continuing():
    decision = identification_decision({})

    assert decision["hard_block"] is False
    assert decision["permissions"]["continue_to_estimate"] == PERMISSION_ALLOW
    assert decision["permissions"]["causal_language"] == PERMISSION_FORBID
    assert decision["permissions"]["requires_disclosure"] is True


# ---------------------------------------------------------------------------
# C3 显著性与设计有效性分离
# ---------------------------------------------------------------------------

def _did_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "y": [1.0, 1.1, 1.3, 1.2, 2.0, 2.1, 2.4, 2.2],
            "treat": [0, 0, 0, 0, 1, 1, 1, 1],
            "year": [2000, 2001, 2002, 2003, 2000, 2001, 2002, 2003],
            "id": [1, 1, 1, 1, 2, 2, 2, 2],
            "g": [0, 0, 0, 0, 2002, 2002, 2002, 2002],
        }
    )


def _stub_statspai(monkeypatch, *, pvalue):
    statspai = pytest.importorskip("statspai")

    class _CS:
        estimate = 0.42
        pvalue_ = pvalue

    cs = _CS()
    cs.pvalue = pvalue

    monkeypatch.setattr(
        statspai,
        "bacon_decomposition",
        lambda *a, **k: {
            "beta_twfe": 0.11,
            "negative_weight_share": 0.0,
            "already_treated_control_weight_share": 0.0,
            "n_comparisons": 3,
        },
    )
    monkeypatch.setattr(statspai, "callaway_santanna", lambda *a, **k: cs)
    return statspai


def _run_did(monkeypatch, *, pvalue):
    _stub_statspai(monkeypatch, pvalue=pvalue)
    diagnostics: list = []
    report_lines: list = []
    passed = _diag_did(
        _did_frame(),
        {
            "outcome_col": "y",
            "treatment_col": "treat",
            "time_col": "year",
            "id_col": "id",
            "treatment_group_col": "g",
        },
        diagnostics,
        report_lines,
    )
    cs = next(d for d in diagnostics if d["test"] == "callaway_santanna")
    return passed, diagnostics, cs


def test_callaway_santanna_is_an_estimate_record_not_a_design_check(monkeypatch):
    _passed, diagnostics, cs = _run_did(monkeypatch, pvalue=0.001)

    assert cs["role"] == ids.ROLE_EFFECT_ESTIMATE
    assert cs["status"] == "reported"
    assert cs["status"] not in {"pass", "warn", "fail"}
    assert cs not in design_validity_diagnostics(diagnostics), (
        "效应估计记录不能进入设计有效性判定"
    )
    assert cs["significant_at_0_05"] is True


def test_missing_pvalue_stays_unknown(monkeypatch):
    _passed, diagnostics, cs = _run_did(monkeypatch, pvalue=None)

    assert cs["pvalue"] is None, "缺失 p 值不能被折成 0"
    assert cs["significant_at_0_05"] is None, "缺失 p 值不能推断显著与否"


def test_effect_significance_does_not_move_design_validity(monkeypatch):
    _p_sig, sig_diags, _ = _run_did(monkeypatch, pvalue=0.001)
    _p_none, none_diags, _ = _run_did(monkeypatch, pvalue=None)

    assert assess_diagnostics(sig_diags) == assess_diagnostics(none_diags), (
        "显著性不同的两次运行，设计有效性判定必须一致"
    )


def test_failed_effect_estimate_does_not_downgrade_design_validity(monkeypatch):
    """CS 估计抛异常 ≠ Goodman-Bacon 那条设计有效性检查没通过。

    否则一次稳健估计失败会把主张从 causal_with_caveat 打成 association —— 而旧的
    星级口径不会，这属于没申报的行为变化。
    """
    statspai = pytest.importorskip("statspai")
    _stub_statspai(monkeypatch, pvalue=0.001)

    def _boom(*_a, **_k):
        raise RuntimeError("callaway failed")

    monkeypatch.setattr(statspai, "callaway_santanna", _boom)

    diagnostics: list = []
    report_lines: list = []
    _diag_did(
        _did_frame(),
        {
            "outcome_col": "y",
            "treatment_col": "treat",
            "time_col": "year",
            "id_col": "id",
            "treatment_group_col": "g",
        },
        diagnostics,
        report_lines,
    )

    cs = next(d for d in diagnostics if d["test"] == "callaway_santanna")
    assert cs["role"] == ids.ROLE_EFFECT_ESTIMATE
    assert cs["status"] == "error"
    assert "callaway failed" in " ".join(report_lines), "失败必须留在报告里，不许静默"

    assessed = assess_diagnostics(diagnostics)
    assert assessed["assessment"] == ASSESSMENT_RISK_NOT_FOUND, (
        "设计有效性由 Bacon 决定，不因稳健估计失败而降级"
    )
    assert assessed["star_rating"] == 3


# ---------------------------------------------------------------------------
# C4 五个入口的许可决定一致
# ---------------------------------------------------------------------------

def _row(name, **extra):
    return {"name": name, **extra}


_ROWS = [
    _row("未跑诊断", state={}),
    _row(
        "跑完但未知",
        state={
            "identification_diag": {
                "strategy": "did",
                "diagnostics": [{"test": "bacon_decomposition", "status": "error"}],
                "execution": "failed",
                "assessment": ASSESSMENT_INSUFFICIENT_EVIDENCE,
                "passed": None,
                "star_rating": None,
            },
            "star_rating": None,
        },
    ),
    _row(
        "0 星",
        state={
            "identification_diag": {
                "strategy": "did",
                "diagnostics": [{"test": "bacon_decomposition", "status": "fail"}],
                "execution": "completed",
                "assessment": ASSESSMENT_RISK_FOUND,
                "passed": False,
                "star_rating": 0,
            },
            "star_rating": 0,
            "identification_failed": True,
        },
    ),
]


@pytest.mark.parametrize("row", _ROWS, ids=[r["name"] for r in _ROWS])
def test_pipeline_entries_share_one_verdict(row):
    from agent.engine.bind import _identification_failed
    from agent.engine.readiness import paper_ready_to_write
    from agent.graph import route_after_identification

    state = row["state"]
    blocked = identification_hard_block(state)
    assert blocked is (row["name"] == "0 星")

    routed_to_pause = route_after_identification(state) == "hitl_pause"
    assert routed_to_pause is blocked, "图的边与判定函数必须一致"

    # 章节写入闸门：阻断时用同一个阻挡码，不阻断时不得出现它。
    # 写入是否就绪还取决于别的条件（有没有跑过识别、有没有估计），
    # 所以这里只断言「star_0 这个阻挡码」与判定一致，不断言就绪本身。
    ready, blockers = paper_ready_to_write(state, "intro")
    assert ("star_0" in blockers) is blocked
    if blocked:
        assert ready is False

    # 章节绑定问的是更严的一档：0 星必然不可信；未知不因此被判不可信。
    assert _identification_failed(state) is blocked


def test_prewrite_and_facade_do_not_inline_star_checks():
    """流程入口不得再自己写 star_rating == 0 —— 那正是判定漂移的来源。

    扫描整个运行时代码树，不只是这四个文件：漏扫一次就会像 agent/eval 那样
    留下一份「真图的手写镜像」，对同一份 state 给出相反答案。
    """
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    pattern = re.compile(r'star_rating"\s*\)\s*==\s*0|star_rating"\]\s*==\s*0')
    allowed = {
        "agent/engine/identification_state.py",  # 判定函数的家
    }
    skipped_dirs = {".venv", "node_modules", "__pycache__", ".git"}

    offenders = []
    for base in ("agent", "backend"):
        for path in (root / base).rglob("*.py"):
            rel = path.relative_to(root).as_posix()
            if skipped_dirs & set(path.parts):
                continue
            if rel in allowed or "/tests/" in rel or rel.endswith("_test.py"):
                continue
            # 少数文件不是 UTF-8（历史编码），按字节宽松解码即可：
            # 要匹配的是纯 ASCII 片段。
            text = path.read_bytes().decode("utf-8", "ignore")
            if pattern.search(text):
                offenders.append(rel)

    assert offenders == [], f"这些入口还在内联星级判断：{offenders}"


@pytest.mark.parametrize("row", _ROWS, ids=[r["name"] for r in _ROWS])
def test_eval_reviewer_agrees_with_the_graph(row):
    """评审器是图的手写镜像，硬拒绝必须问同一个判定。"""
    from agent.eval.judge import _hard_reject
    from agent.graph import route_after_identification

    blocked = route_after_identification(row["state"]) == "hitl_pause"
    assert (_hard_reject(row["state"]) is not None) is blocked, (
        "评审器的硬拒绝与图的条件边必须一致"
    )


def _isolate_pipeline_nodes(monkeypatch):
    """把 run_pipeline 沿途的节点换成探针，只观察边怎么走。"""
    monkeypatch.setattr("agent.nodes.clean_data.clean_data", lambda state: {})
    monkeypatch.setattr("agent.nodes.set_direction.set_direction", lambda state: {})
    monkeypatch.setattr(
        "agent.nodes.identification_verify.identification_verify", lambda state: {}
    )
    monkeypatch.setattr(
        "agent.nodes.estimate.estimate", lambda state: {"estimate": {"ran": True}}
    )


def test_eval_pipeline_truncates_exactly_when_the_graph_pauses(monkeypatch):
    """run_pipeline 的截断点必须与 route_after_identification 同步。

    特别是 ``identification_failed=True`` 而没有星级的 state：只认
    ``star_rating == 0`` 的手写镜像会继续跑估计，而真图已经停在 hitl_pause。
    """
    from agent.eval.run_task import run_pipeline

    _isolate_pipeline_nodes(monkeypatch)

    flagged = {
        "research_direction": {"question": "Q", "dv": "y", "method": "did"},
        "identification_failed": True,
    }
    _state, nodes_run, stop_reasons = run_pipeline(dict(flagged))
    assert "estimate" not in nodes_run, "识别已失败却还在跑估计"
    assert stop_reasons


def test_eval_pipeline_keeps_running_when_identification_is_unknown(monkeypatch):
    """未知不是拒绝的依据：台架不得把「还没评估」当成截断理由。"""
    from agent.eval.run_task import run_pipeline

    _isolate_pipeline_nodes(monkeypatch)

    unknown = {"research_direction": {"question": "Q", "dv": "y", "method": "did"}}
    _state, nodes_run, _stop = run_pipeline(dict(unknown))
    assert "estimate" in nodes_run


# ---------------------------------------------------------------------------
# C7 端到端：真实数据 → 三轴与许可
# ---------------------------------------------------------------------------

def test_real_did_run_reports_completed_and_clean(tmp_path):
    statspai = pytest.importorskip("statspai")
    csv_path = tmp_path / "california_prop99.csv"
    statspai.california_prop99().to_csv(csv_path, index=False)

    result = identification_verify(
        {
            "csv_path": str(csv_path),
            "research_direction": {
                "method": "did",
                "outcome_col": "packspercapita",
                "treatment_col": "treated",
                "time_col": "year",
                "id_col": "state",
            },
        }
    )
    diag = result["identification_diag"]

    assert diag["execution"] == "completed"
    assert diag["assessment"] == ASSESSMENT_RISK_NOT_FOUND
    assert diag["star_rating"] == 3
    assert diag["passed"] is True
    assert result["identification_failed"] is False

    perms = diag["permissions"]
    assert permission_is(perms["causal_language"], PERMISSION_ALLOW)
    assert permission_is(perms["promote_main_result"], PERMISSION_ALLOW)
    assert perms["requires_disclosure"] is False
