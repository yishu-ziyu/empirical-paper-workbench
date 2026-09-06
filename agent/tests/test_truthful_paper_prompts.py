"""Frame 5: chapter prompts expose only state-backed paper facts."""
from __future__ import annotations

import pytest

from agent.engine.bind import bind_chapter_kwargs
from agent.prompts import get_prompt

from conftest import make_write_ready_state


def _passing_identification(method: str) -> dict:
    return {
        "strategy": method,
        "diagnostics": [{"test": f"{method}_diagnostic", "status": "pass"}],
        "passed": True,
        "report": "识别证据已通过",
        "star_rating": 3,
    }


def _passing_robustness(method: str, estimator: str) -> dict:
    result = {
        "produced_by": "robustness_check",
        "diagnostics": [],
        "robustness": [],
        "heterogeneity": [],
        "placebos": [],
        "summary_table": "# 稳健性检验汇总",
    }
    if method == "scm":
        result["placebos"] = [
            {
                "type": "placebo_time",
                "n_placebos": 4,
                "n_significant": 0,
                "share_significant": 0.0,
            }
        ]
    elif estimator == "statspai.callaway_santanna":
        result["robustness"] = [
            {
                "type": "cs_variant",
                "control_group": "nevertreated",
                "notyet_cutoff": "period",
                "level": "nevertreated/period",
                "coef": 0.2,
                "se": 0.05,
                "p": 0.01,
            }
        ]
    else:
        result["robustness"] = [
            {
                "type": {
                    "did": "clustering",
                    "iv": "iv_cluster",
                    "rd": "rd_variant",
                }[method],
                "level": "unit",
                "coef": 0.2,
                "se": 0.05,
                "p": 0.01,
            }
        ]
    return result


def _causal_state(
    *,
    method: str = "iv",
    estimator: str = "statspai.ivreg",
    **overrides,
) -> dict:
    ready = make_write_ready_state()
    state = make_write_ready_state(
        research_direction={
            "question": "Q",
            "method": method,
            "claim": "causal_with_caveat",
        },
        star_rating=3,
        identification_diag=_passing_identification(method),
        estimate={
            **ready["estimate"],
            "method": method,
            "status": "ok",
            "estimator": estimator,
        },
        robustness_results=_passing_robustness(method, estimator),
    )
    state.update(overrides)
    return state


def test_data_desc_missing_provenance_is_explicit_and_forbids_invention():
    state = {
        "uploaded_datasets": [
            {
                "name": "classroom.csv",
                "columns": ["score", "treated"],
                "rows": 24,
            }
        ]
    }

    bound = bind_chapter_kwargs(state, {"type": "data_desc"})
    system, user = get_prompt("data_desc").render(**bound)
    prompt = system + "\n" + user

    assert "classroom.csv" in prompt
    assert "24" in prompt
    assert "调查机构：未提供" in prompt
    assert "调查年份/覆盖时段：未提供" in prompt
    assert "抽样框/抽样设计：未提供" in prompt
    assert "禁止编造" in prompt
    assert "只能描述" in prompt


def test_data_desc_binds_research_direction_variable_roles_without_inference():
    state = {
        "research_direction": {
            "dv": "income",
            "iv": "schooling",
            "controls": ["age", "region"],
        }
    }

    bound = bind_chapter_kwargs(state, {"type": "data_desc"})
    system, user = get_prompt("data_desc").render(**bound)
    prompt = system + "\n" + user

    assert "因变量：income" in prompt
    assert "自变量：schooling" in prompt
    assert "控制变量：age、region" in prompt
    assert "不得推断额外变量角色" in prompt


def test_data_desc_marks_each_missing_variable_role_as_not_provided():
    bound = bind_chapter_kwargs(
        {"research_direction": {"dv": "income"}}, {"type": "data_desc"}
    )
    _, user = get_prompt("data_desc").render(**bound)

    assert "因变量：income" in user
    assert "自变量：未提供" in user
    assert "控制变量：未提供" in user


def test_data_desc_preserves_explicitly_empty_controls():
    bound = bind_chapter_kwargs(
        {"research_direction": {"controls": []}}, {"type": "data_desc"}
    )
    _, user = get_prompt("data_desc").render(**bound)

    assert "控制变量：无（state 明确为空）" in user


def test_results_bind_includes_approved_claim_wording_and_run_facts():
    state = make_write_ready_state(
        research_lab={
            "claims": [
                {
                    "id": "claim.card.education-earnings",
                    "approved_by_user": True,
                    "supported_wording": "Education is positively associated with earnings.",
                    "conditionally_supported_wording": (
                        "Under the college-proximity IV assumptions, IV estimates "
                        "suggest a positive local causal return to schooling."
                    ),
                    "unsupported_wording": (
                        "One more year of education raises everyone's wage by 13%."
                    ),
                    "run_facts": "OLS spec_id=ols_full_controls coef=0.08 n=3010",
                }
            ],
            "current_claim_id": "claim.card.education-earnings",
        }
    )
    bound = bind_chapter_kwargs(state, {"type": "results"})
    _, user = get_prompt("results").render(**bound)
    assert "Education is positively associated with earnings." in user
    assert "positive local causal return" in user
    assert "raises everyone's wage by 13%" in user
    assert "OLS spec_id=ols_full_controls coef=0.08 n=3010" in user
    assert bound["claim"] == "association"


def test_methods_binds_actual_estimate_spec_and_unknown_covariance():
    ready = make_write_ready_state()
    estimate = {
        **ready["estimate"],
        "formula": "income ~ age + schooling",
        "estimator": "statsmodels.ols",
        "n": 88,
    }
    estimate.pop("cluster", None)
    state = make_write_ready_state(
        estimate=estimate,
        main_specification={
            "produced_by": "set_direction",
            "method": "ols",
            "formula": "income ~ age + schooling",
            "controls": ["schooling"],
        },
    )

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "ols"})
    system, user = get_prompt("methods").render(**bound)
    prompt = system + "\n" + user

    assert "income ~ age + schooling" in prompt
    assert "schooling" in prompt
    assert "statsmodels.ols" in prompt
    assert "N：88" in prompt
    assert state["estimate"]["treatment_row"] in prompt
    assert "协方差/标准误设定：未提供" in prompt
    assert "HC1" in prompt and "不得" in prompt


def test_methods_binds_explicit_cluster_covariance():
    ready = make_write_ready_state()
    state = make_write_ready_state(
        estimate={**ready["estimate"], "cluster": "county_id"},
        main_specification={
            "produced_by": "set_direction",
            "method": "ols",
            "formula": "income ~ age",
            "controls": [],
        },
    )
    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "ols"})
    _, user = get_prompt("methods").render(**bound)

    assert "按 county_id 聚类的标准误" in user
    assert "控制变量：无（state 明确为空）" in user


def test_causal_methods_downgrades_when_identification_and_robustness_unverified():
    ready = make_write_ready_state()
    state = make_write_ready_state(
        research_direction={
            "question": "Q",
            "method": "did",
            "claim": "causal_with_caveat",
        },
        star_rating=2,
        identification_diag={"report": "平行趋势未提供检验结果"},
        estimate={
            **ready["estimate"],
            "method": "did",
            "estimator": "statspai.feols",
            "status": "ok",
        },
        robustness_results=None,
    )
    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "did"})
    system, user = get_prompt("methods").render(**bound)
    prompt = system + "\n" + user

    assert bound["claim"] == "association"
    assert bound["identification_report"] == "平行趋势未提供检验结果"
    assert bound["robustness_status"] == "未运行"
    assert "主张模式：association" in prompt
    assert "识别证据未明确通过" in prompt
    assert "稳健性证据未明确通过" in prompt
    assert "按【识别策略" not in prompt


def test_methods_degrades_requested_causal_method_when_actual_estimate_is_ols():
    ready = make_write_ready_state()
    state = make_write_ready_state(
        research_direction={
            "question": "Q",
            "method": "did",
            "claim": "causal_with_caveat",
        },
        star_rating=2,
        identification_diag={
            "strategy": "did",
            "passed": True,
            "report": "识别证据已通过",
        },
        estimate={
            **ready["estimate"],
            "method": "did",
            "status": "degraded",
            "estimator": "statsmodels.ols",
        },
    )

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "did"})
    system, user = get_prompt("methods").render(**bound)
    prompt = system + "\n" + user

    assert "主张模式：association" in prompt
    assert "请求方法 did 未成功执行" in prompt
    assert "按【识别策略" not in prompt
    assert "主张模式：causal_with_caveat" not in prompt
    assert "平行趋势已满足" not in prompt
    assert "工具变量有效" not in prompt


def test_methods_keeps_causal_template_for_verified_executed_estimator():
    ready = make_write_ready_state()
    state = make_write_ready_state(
        research_direction={
            "question": "Q",
            "method": "iv",
            "claim": "causal_with_caveat",
        },
        star_rating=3,
        identification_diag=_passing_identification("iv"),
        estimate={
            **ready["estimate"],
            "method": "iv",
            "status": "ok",
            "estimator": "statspai.ivreg",
        },
        robustness_results=_passing_robustness("iv", "statspai.ivreg"),
    )

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "iv"})
    system, user = get_prompt("methods").render(**bound)
    prompt = system + "\n" + user

    assert "主张模式：causal_with_caveat" in prompt
    assert "按【识别策略" in prompt
    assert "statspai.ivreg" in prompt
    assert "请求方法 iv 未成功执行" not in prompt


@pytest.mark.parametrize(
    ("method", "estimator"),
    [
        ("did", "statspai.feols"),
        ("did", "statspai.callaway_santanna"),
        ("iv", "statspai.ivreg"),
        ("rd", "statspai.rdrobust"),
        ("scm", "statspai.synth"),
    ],
)
def test_methods_keeps_causal_template_for_each_supported_estimator(
    method, estimator
):
    ready = make_write_ready_state()
    state = make_write_ready_state(
        research_direction={
            "question": "Q",
            "method": method,
            "claim": "causal_with_caveat",
        },
        star_rating=3,
        identification_diag=_passing_identification(method),
        estimate={
            **ready["estimate"],
            "method": method,
            "status": "ok",
            "estimator": estimator,
        },
        robustness_results=_passing_robustness(method, estimator),
    )

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": method})
    system, user = get_prompt("methods").render(**bound)
    prompt = system + "\n" + user

    assert "主张模式：causal_with_caveat" in prompt
    assert "按【识别策略" in prompt
    assert estimator in prompt
    assert f"请求方法 {method} 未成功执行" not in prompt


@pytest.mark.parametrize(
    ("method", "estimator"),
    [
        ("iv", "thirdparty.ivreg_placeholder"),
        ("iv", "future.super2sls_beta"),
        ("did", "not_statspai.feols_fake"),
        ("rd", "vendor.rdrobust_preview"),
        ("scm", "statspai.synthesized_ols"),
    ],
)
def test_methods_downgrades_estimator_name_collisions(method, estimator):
    ready = make_write_ready_state()
    state = make_write_ready_state(
        research_direction={
            "question": "Q",
            "method": method,
            "claim": "causal_with_caveat",
        },
        star_rating=3,
        identification_diag=_passing_identification(method),
        estimate={
            **ready["estimate"],
            "method": method,
            "status": "ok",
            "estimator": estimator,
        },
        robustness_results=_passing_robustness(method, "statspai.ivreg"),
    )

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": method})
    system, user = get_prompt("methods").render(**bound)
    prompt = system + "\n" + user

    assert "主张模式：association" in prompt
    assert "按【识别策略" not in prompt
    assert f"请求方法 {method} 未成功执行" in prompt
    assert "主张模式：causal_with_caveat" not in prompt


@pytest.mark.parametrize(
    ("estimate_status", "estimator", "identification_diag"),
    [
        ("error", "statspai.ivreg", {"passed": True, "report": "已通过"}),
        ("ok", "statsmodels.ols", {"passed": True, "report": "已通过"}),
        ("ok", "statspai.ivreg", {"passed": False, "status": "failed"}),
    ],
)
def test_methods_downgrades_any_failed_causal_execution_or_identification(
    estimate_status, estimator, identification_diag
):
    ready = make_write_ready_state()
    state = make_write_ready_state(
        research_direction={
            "question": "Q",
            "method": "iv",
            "claim": "causal_with_caveat",
        },
        star_rating=2,
        identification_diag=identification_diag,
        estimate={
            **ready["estimate"],
            "method": "iv",
            "status": estimate_status,
            "estimator": estimator,
        },
    )

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "iv"})
    system, user = get_prompt("methods").render(**bound)
    prompt = system + "\n" + user

    assert "主张模式：association" in prompt
    assert "按【识别策略" not in prompt
    assert "实际结果" in prompt
    assert "不能支持因果主张" in prompt


@pytest.mark.parametrize(
    ("case", "identification_diag"),
    [
        ("missing", None),
        (
            "unverified",
            {
                "strategy": "iv",
                "diagnostics": [
                    {"test": "iv_diag", "status": "skipped", "reason": "missing inputs"}
                ],
                "passed": True,
                "report": "识别策略尚未评分",
                "star_rating": None,
            },
        ),
    ],
)
def test_causal_claim_requires_explicitly_verified_identification(
    case, identification_diag
):
    state = _causal_state(identification_diag=identification_diag)

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "iv"})

    assert bound["claim"] == "association", case
    assert "主张类型：association" in bound["estimate_facts"], case


@pytest.mark.parametrize(
    ("case", "identification_diag"),
    [
        (
            f"top_status_{status}",
            {**_passing_identification("iv"), "status": status},
        )
        for status in ("unverified", "skipped", "fallback")
    ]
    + [
        (
            "top_reason_not_verified",
            {
                **_passing_identification("iv"),
                "reason": "not actually verified",
            },
        ),
        (
            "top_mock_flag",
            {**_passing_identification("iv"), "mock": True},
        ),
        (
            "nested_failure_reason",
            {
                **_passing_identification("iv"),
                "diagnostics": [
                    {
                        "test": "iv_diag",
                        "status": "pass",
                        "details": {"reason": "fallback evidence"},
                    }
                ],
            },
        ),
    ],
)
def test_causal_claim_rejects_identification_failure_markers(
    case, identification_diag
):
    state = _causal_state(identification_diag=identification_diag)

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "iv"})

    assert bound["claim"] == "association", case


def test_causal_claim_accepts_explicit_success_identification_status():
    identification_diag = {
        **_passing_identification("iv"),
        "status": "success",
        "reason": "verified by diagnostics",
        "message": "verification complete",
    }

    bound = bind_chapter_kwargs(
        _causal_state(identification_diag=identification_diag),
        {"type": "methods", "method": "iv"},
    )

    assert bound["claim"] == "causal_with_caveat"


@pytest.mark.parametrize(
    ("case", "state_rating", "diag_rating"),
    [
        ("one_star", 1, 1),
        ("two_stars", 2, 2),
        ("above_domain", 4, 4),
        ("far_above_domain", 999, 999),
        ("state_diag_mismatch", 3, 2),
    ],
)
def test_causal_claim_requires_production_three_star_identification(
    case, state_rating, diag_rating
):
    identification_diag = {
        **_passing_identification("iv"),
        "star_rating": diag_rating,
    }

    bound = bind_chapter_kwargs(
        _causal_state(
            star_rating=state_rating,
            identification_diag=identification_diag,
        ),
        {"type": "methods", "method": "iv"},
    )

    assert bound["claim"] == "association", case


@pytest.mark.parametrize(
    ("case", "robustness_results"),
    [
        ("not_run", None),
        ("empty", {}),
        (
            "no_result_rows",
            {
                "produced_by": "robustness_check",
                "diagnostics": [],
                "robustness": [],
                "placebos": [],
            },
        ),
        (
            "degraded",
            {
                **_passing_robustness("iv", "statspai.ivreg"),
                "degraded": True,
                "reason": "iv_battery_failed",
            },
        ),
        (
            "error",
            {
                **_passing_robustness("iv", "statspai.ivreg"),
                "diagnostics": [{"test": "ivreg", "status": "error"}],
            },
        ),
        (
            "skipped",
            {
                **_passing_robustness("iv", "statspai.ivreg"),
                "diagnostics": [{"test": "ivreg", "status": "skipped"}],
            },
        ),
        (
            "fallback",
            {
                **_passing_robustness("iv", "statspai.ivreg"),
                "diagnostics": [{"test": "ivreg", "status": "fallback"}],
            },
        ),
        (
            "failed",
            {
                **_passing_robustness("iv", "statspai.ivreg"),
                "status": "failed",
            },
        ),
    ],
)
def test_causal_claim_requires_explicitly_successful_robustness(
    case, robustness_results
):
    state = _causal_state(robustness_results=robustness_results)

    bound = bind_chapter_kwargs(state, {"type": "methods", "method": "iv"})

    assert bound["claim"] == "association", case
    assert "主张类型：association" in bound["estimate_facts"], case


@pytest.mark.parametrize("status", ["fallback", "error", "skipped", "fail"])
def test_causal_claim_rejects_non_success_robustness_top_status(status):
    robustness_results = {
        **_passing_robustness("iv", "statspai.ivreg"),
        "status": status,
    }

    bound = bind_chapter_kwargs(
        _causal_state(robustness_results=robustness_results),
        {"type": "methods", "method": "iv"},
    )

    assert bound["claim"] == "association", status


@pytest.mark.parametrize(
    ("case", "row"),
    [
        (
            "row_fallback_status",
            {"type": "iv_cluster", "status": "fallback", "coef": 0.2},
        ),
        (
            "row_error_status",
            {"type": "iv_cluster", "status": "error", "coef": 0.2},
        ),
        (
            "row_mock_source",
            {"type": "iv_cluster", "source": "mock", "coef": 0.2},
        ),
        ("row_mock_flag", {"type": "iv_cluster", "mock": True, "coef": 0.2}),
        ("row_mock_type", {"type": "mock", "coef": 0.2}),
        (
            "row_placeholder_mode",
            {"type": "iv_cluster", "mode": "placeholder", "coef": 0.2},
        ),
        ("row_type_only", {"type": "iv_cluster"}),
        ("row_null_stat", {"type": "iv_cluster", "coef": None}),
        ("row_non_finite_stat", {"type": "iv_cluster", "coef": float("nan")}),
        ("row_empty_interval", {"type": "wild_cluster_bootstrap", "ci_boot": {}}),
        ("row_unknown_schema", {"type": "future_variant", "coef": 0.2}),
        (
            "row_nested_failure_reason",
            {
                "type": "iv_cluster",
                "coef": 0.2,
                "metadata": {"reason": "fallback result"},
            },
        ),
    ],
)
def test_causal_claim_rejects_non_real_robustness_result_rows(case, row):
    robustness_results = {
        **_passing_robustness("iv", "statspai.ivreg"),
        "robustness": [row],
    }

    bound = bind_chapter_kwargs(
        _causal_state(robustness_results=robustness_results),
        {"type": "methods", "method": "iv"},
    )

    assert bound["claim"] == "association", case


def test_causal_claim_accepts_real_wild_cluster_interval_result():
    robustness_results = {
        **_passing_robustness("iv", "statspai.ivreg"),
        "robustness": [],
        "placebos": [
            {
                "type": "wild_cluster_bootstrap",
                "ci_boot": [-0.1, 0.3],
                "p_boot": 0.04,
            }
        ],
    }

    bound = bind_chapter_kwargs(
        _causal_state(robustness_results=robustness_results),
        {"type": "methods", "method": "iv"},
    )

    assert bound["claim"] == "causal_with_caveat"


@pytest.mark.parametrize(
    ("case", "interval"),
    [
        ("reversed_sequence", [0.3, -0.1]),
        ("reversed_mapping", {"lower": 0.3, "upper": -0.1}),
    ],
)
def test_causal_claim_rejects_reversed_robustness_intervals(case, interval):
    robustness_results = {
        **_passing_robustness("iv", "statspai.ivreg"),
        "robustness": [],
        "placebos": [
            {
                "type": "wild_cluster_bootstrap",
                "ci_boot": interval,
                "p_boot": 0.04,
            }
        ],
    }

    bound = bind_chapter_kwargs(
        _causal_state(robustness_results=robustness_results),
        {"type": "methods", "method": "iv"},
    )

    assert bound["claim"] == "association", case


@pytest.mark.parametrize(
    ("case", "failure_marker"),
    [
        ("failure_reason", {"reason": "not actually verified"}),
        ("fallback_flag", {"fallback": True}),
        ("skipped_flag", {"skipped": True}),
        ("fail_flag", {"fail": True}),
    ],
)
def test_causal_claim_rejects_robustness_top_failure_markers(
    case, failure_marker
):
    robustness_results = {
        **_passing_robustness("iv", "statspai.ivreg"),
        **failure_marker,
    }

    bound = bind_chapter_kwargs(
        _causal_state(robustness_results=robustness_results),
        {"type": "methods", "method": "iv"},
    )

    assert bound["claim"] == "association", case


@pytest.mark.parametrize(
    "failure_case",
    [
        "estimate_degraded",
        "estimate_error",
        "ols_estimator",
        "identification_failed",
        "identification_unverified",
        "robustness_failed",
        "robustness_mock_row",
    ],
)
def test_effective_claim_downgrade_propagates_to_all_claim_consuming_chapters(
    failure_case
):
    state = _causal_state()
    if failure_case in {"estimate_degraded", "estimate_error"}:
        state["estimate"] = {
            **state["estimate"],
            "status": failure_case.removeprefix("estimate_"),
        }
    elif failure_case == "ols_estimator":
        state["estimate"] = {**state["estimate"], "estimator": "statsmodels.ols"}
    elif failure_case == "identification_failed":
        state["identification_diag"] = {
            "strategy": "iv",
            "diagnostics": [{"test": "iv_diag", "status": "fail"}],
            "passed": False,
            "status": "failed",
            "report": "识别失败",
            "star_rating": 0,
        }
        state["identification_failed"] = True
    elif failure_case == "identification_unverified":
        state["identification_diag"] = {
            **state["identification_diag"],
            "status": "unverified",
        }
    elif failure_case == "robustness_failed":
        state["robustness_results"] = {
            **state["robustness_results"],
            "degraded": True,
            "reason": "iv_battery_failed",
        }
    elif failure_case == "robustness_mock_row":
        state["robustness_results"] = {
            **state["robustness_results"],
            "robustness": [
                {"type": "iv_cluster", "source": "mock", "coef": 0.2}
            ],
        }

    bound_by_chapter = {
        chapter_type: bind_chapter_kwargs(
            state,
            {
                "type": chapter_type,
                **({"method": "iv"} if chapter_type == "methods" else {}),
            },
        )
        for chapter_type in ("methods", "results", "conclusion")
    }

    assert {bound["claim"] for bound in bound_by_chapter.values()} == {"association"}
    for chapter_type, bound in bound_by_chapter.items():
        assert "主张类型：association" in bound["estimate_facts"], (
            failure_case,
            chapter_type,
        )
        system, user = get_prompt(chapter_type).render(**bound)
        prompt = system + "\n" + user
        assert "禁止因果表述" in prompt, (failure_case, chapter_type)
        if chapter_type == "methods":
            assert "主张模式：association" in prompt
            assert "主张模式：causal_with_caveat" not in prompt


def test_effective_causal_claim_with_both_evidence_gates_propagates_to_all_chapters():
    state = _causal_state()

    bound_by_chapter = {
        chapter_type: bind_chapter_kwargs(
            state,
            {
                "type": chapter_type,
                **({"method": "iv"} if chapter_type == "methods" else {}),
            },
        )
        for chapter_type in ("methods", "results", "conclusion")
    }

    assert {bound["claim"] for bound in bound_by_chapter.values()} == {
        "causal_with_caveat"
    }
    assert all(
        "主张类型：causal_with_caveat" in bound["estimate_facts"]
        for bound in bound_by_chapter.values()
    )


def test_results_and_conclusion_mark_unrun_robustness_and_heterogeneity():
    state = make_write_ready_state(robustness_results=None)
    bound = bind_chapter_kwargs(state, {"type": "results", "method": "ols"})

    for chapter_type in ("results", "conclusion"):
        system, user = get_prompt(chapter_type).render(**bound)
        prompt = system + "\n" + user
        assert "稳健性状态：未运行" in prompt
        assert "异质性证据：未运行/未提供" in prompt
        assert "不得宣称稳健" in prompt
        assert "不得生成地区、行业、性别" in prompt


def test_degraded_robustness_is_evidence_insufficient_not_robust():
    state = make_write_ready_state(
        robustness_results={
            "produced_by": "robustness_check",
            "degraded": True,
            "reason": "no_cluster_or_groups",
            "robustness": [],
            "heterogeneity": [],
            "summary_table": "OLS battery skipped",
        }
    )
    bound = bind_chapter_kwargs(state, {"type": "results", "method": "ols"})

    for chapter_type in ("results", "conclusion"):
        system, user = get_prompt(chapter_type).render(**bound)
        prompt = system + "\n" + user
        assert "已运行但降级" in prompt
        assert "证据不足" in prompt
        assert "no_cluster_or_groups" in prompt
        assert "不得宣称稳健" in prompt


def test_conclusion_without_policy_evidence_stays_inside_result_boundary():
    bound = bind_chapter_kwargs(
        make_write_ready_state(), {"type": "conclusion"}
    )
    system, user = get_prompt("conclusion").render(**bound)
    prompt = system + "\n" + user

    assert "政策证据：未提供" in prompt
    assert "不得声称政策效果" in prompt
    assert "不得给出强政策建议" in prompt
    assert "当前结果的适用边界" in prompt


def test_results_and_conclusion_bind_estimate_facts_and_forbid_causal_ols():
    state = make_write_ready_state(
        main_specification={
            "produced_by": "set_direction",
            "method": "ols",
            "formula": "income ~ age + schooling",
            "controls": ["schooling"],
        }
    )
    bound = bind_chapter_kwargs(state, {"type": "results", "method": "ols"})

    for chapter_type in ("methods", "results", "conclusion"):
        system, user = get_prompt(chapter_type).render(**bound)
        prompt = system + "\n" + user
        assert state["estimate"]["formula"] in prompt
        assert state["estimate"]["estimator"] in prompt
        assert state["estimate"]["treatment_row"] in prompt
        assert "N：5" in prompt
        assert "主张类型：association" in prompt
        assert "禁止因果表述" in prompt


def test_results_prompt_forbids_every_unbound_number():
    bound = bind_chapter_kwargs(
        make_write_ready_state(), {"type": "results", "method": "ols"}
    )
    system, user = get_prompt("results").render(**bound)
    prompt = system + "\n" + user

    assert "任何具体数字" in prompt
    assert "未绑定数字" in prompt
    assert "主处理变量行" in prompt
