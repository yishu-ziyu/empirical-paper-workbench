"""OLS hard lock: leftover TWFE phrasing must not survive generate-chapter."""
from __future__ import annotations

from agent.engine.bind import bind_chapter_kwargs, format_estimate_facts
from agent.engine.ols_lock import (
    OLS_PROMPT_LOCK,
    contains_forbidden_twfe_claim,
    estimator_label,
    ols_lock_active,
    sanitize_ols_text,
)
from agent.nodes.estimate import estimate
from agent.nodes.generate_chapter import generate_chapter
from agent.prompts import get_prompt

from conftest import make_write_ready_state


CONTRAST_TWFE = "本文不是简单相关回归，而是采用双向固定效应估计政策效应。"
SPEC_STATE_YEAR_FE = "主回归加入州固定效应与年份固定效应，并在州层面聚类。"


def test_denial_span_does_not_skip_contrast_twfe_claim():
    """Issue #24 leftover: 不是…而是采用双向固定效应 is still a TWFE claim."""
    assert contains_forbidden_twfe_claim(CONTRAST_TWFE)
    cleaned = sanitize_ols_text(CONTRAST_TWFE)
    assert "双向固定效应" not in cleaned
    assert "TWFE" not in cleaned
    assert "feols" not in cleaned.lower()
    assert "OLS" in cleaned


def test_spec_sentence_state_and_year_fe_is_forbidden():
    """Issue #24 leftover: 加入州固定效应与年份固定效应 never said 双向."""
    assert contains_forbidden_twfe_claim(SPEC_STATE_YEAR_FE)
    cleaned = sanitize_ols_text(SPEC_STATE_YEAR_FE)
    assert "州固定效应" not in cleaned
    assert "年份固定效应" not in cleaned
    assert "固定效应" not in cleaned
    assert "OLS" in cleaned


def test_ols_lock_active_for_ols_and_unspecified_not_did():
    assert ols_lock_active({"research_direction": {"method": "ols"}})
    assert ols_lock_active({"research_direction": {"method": "OLS"}})
    assert ols_lock_active({"research_direction": {}})
    assert not ols_lock_active({"research_direction": {"method": "did"}})
    assert not ols_lock_active({"research_direction": {"method": "iv"}})
    assert not ols_lock_active({"main_specification": {"method": "did"}})


def test_estimator_label_is_ols_regress_or_lm():
    assert estimator_label("statspai.feols") == "OLS"
    assert estimator_label("statsmodels.ols") == "OLS"
    assert estimator_label("xtreg") == "OLS"
    assert estimator_label("reghdfe") == "OLS"
    assert estimator_label("felm") == "lm"
    assert estimator_label("OLS") == "OLS"


def test_methods_and_results_prompts_lock_ols_not_did():
    ols_system, ols_user = get_prompt("methods").render(
        method="ols", research_question="年龄与收入"
    )
    ols_prompt = ols_system + "\n" + ols_user
    assert OLS_PROMPT_LOCK in ols_prompt
    assert "regress" in ols_prompt
    assert "lm" in ols_prompt

    did_system, did_user = get_prompt("methods").render(
        method="did",
        research_question="政策效应",
        claim="causal_with_caveat",
    )
    did_prompt = did_system + "\n" + did_user
    assert OLS_PROMPT_LOCK not in did_prompt


def test_bind_rewrites_feols_estimator_when_direction_is_ols():
    state = make_write_ready_state(
        estimate={
            **make_write_ready_state()["estimate"],
            "estimator": "statspai.feols",
        }
    )
    facts = format_estimate_facts(state)
    assert "估计器：OLS" in facts
    assert "feols" not in facts.lower()
    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "ols"})
    assert "feols" not in bound["estimate_facts"].lower()
    assert "OLS" in bound["estimate_facts"]


def test_generate_chapter_strips_contrast_and_spec_twfe(mock_llm_for):
    recorder = mock_llm_for("generate_chapter", return_value="")
    recorder.return_value = (
        "## 模型设定\n"
        f"{CONTRAST_TWFE}\n\n"
        "## 计量模型\n"
        f"{SPEC_STATE_YEAR_FE}\n"
        "本文用 feols / xtreg / reghdfe / TWFE 估计。\n"
    )
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "methods", "title": "方法", "method": "ols"}],
    )
    result = generate_chapter(state)
    content = result["body_chapters"][0]["content"]
    assert "双向固定效应" not in content
    assert "州固定效应" not in content
    assert "年份固定效应" not in content
    assert "TWFE" not in content
    assert "feols" not in content.lower()
    assert "xtreg" not in content.lower()
    assert "reghdfe" not in content.lower()
    system, user = recorder.calls[0]["args"]
    assert OLS_PROMPT_LOCK in system
    assert OLS_PROMPT_LOCK in user


def test_generate_chapter_did_keeps_twfe_wording(mock_llm_for):
    recorder = mock_llm_for(
        "generate_chapter",
        return_value="本文采用双向固定效应（TWFE / feols）估计处理效应。",
    )
    ready = make_write_ready_state()
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "methods", "title": "方法", "method": "did"}],
        research_direction={
            **ready["research_direction"],
            "method": "did",
            "claim": "causal_with_caveat",
        },
        estimate={
            **ready["estimate"],
            "method": "did",
            "estimator": "statspai.feols",
        },
    )
    result = generate_chapter(state)
    content = result["body_chapters"][0]["content"]
    assert "双向固定效应" in content
    assert "feols" in content
    _, user = recorder.calls[0]["args"]
    assert OLS_PROMPT_LOCK not in user


def test_estimate_ols_labels_ols_not_feols(tmp_path):
    import pandas as pd

    df = pd.DataFrame(
        {
            "y": [1.0, 2.0, 2.0, 3.0, 3.0, 4.0],
            "x": [0, 0, 1, 0, 1, 1],
            "id": [1, 1, 1, 2, 2, 2],
            "year": [2000, 2001, 2002, 2000, 2001, 2002],
        }
    )
    csv_path = tmp_path / "ols.csv"
    df.to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "research_direction": {"method": "ols", "dv": "y", "iv": "x"},
            "main_specification": {
                "method": "ols",
                "formula": "y ~ x | id + year",
                "feols_formula": "y ~ x | id + year",
                "treatment": "x",
                "outcome": "y",
                "id_col": "id",
                "time_col": "year",
            },
        }
    )
    est = out["estimate"]
    assert est["status"] == "ok"
    assert est["estimator"] == "OLS"
    assert est["estimator"] in {"OLS", "regress", "lm"}
    assert "feols" not in str(est["estimator"]).lower()
    assert "|" not in str(est["formula"])
    table = out["results"]
    assert "feols" not in table.lower()
    assert "TWFE" not in table
    assert "双向固定效应" not in table
    assert "xtreg" not in table.lower()
    assert "reghdfe" not in table.lower()
    assert "估计器：`OLS`" in table
