from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS

from Product.backend.method_workflow_service import build_method_workflows
from Program.workbench.method_gate import (
    PROTECTED_FORMAL_PATHS,
    extract_variables,
    infer_method_family,
    infer_method_subtype,
    profile_dataset,
    read_json,
    select_primary_task,
)


SCHEMA_VERSION = "p4.method_diagnostics.v1"


def build_method_diagnostics_report(
    project_root: Path,
    *,
    profile: str = "aer_like",
    max_leave_one_out: int = 10,
) -> dict[str, Any]:
    design_spec = read_json(project_root / "state" / "product" / "design_spec.json")
    run_plan = read_json(project_root / "state" / "product" / "run_plan.json")
    if not design_spec:
        raise ValueError("Missing state/product/design_spec.json")
    if not run_plan:
        raise ValueError("Missing state/product/run_plan.json")

    task = select_primary_task(run_plan)
    method_family = infer_method_family(design_spec, task)
    method_subtype = infer_method_subtype(design_spec, task, method_family)
    variables = extract_variables(design_spec, task)
    dataset_path = design_spec.get("dataset_path") or run_plan.get("dataset_path") or ""
    dataset_profile = profile_dataset(project_root, dataset_path)
    method_workflow = next(
        (method for method in build_method_workflows(design_spec) if method.get("id") == method_family),
        None,
    )

    dataset = load_analysis_dataset(project_root, dataset_path, variables)
    baseline = run_iv_2sls(dataset, variables)
    first_stage = summarize_first_stage(baseline)
    reduced_form = run_reduced_form(dataset, variables)
    ols_comparison = run_ols_comparison(dataset, variables)
    sample = build_sample_consistency(dataset_profile, dataset, run_plan)
    shift_share = build_shift_share_component_review(dataset, variables)
    diagnostics = build_diagnostics(
        baseline,
        first_stage,
        reduced_form,
        ols_comparison,
        sample,
        shift_share,
        max_leave_one_out=max_leave_one_out,
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "status": choose_report_status(diagnostics),
        "evidence_level": "local_file_plus_recomputed_method_diagnostics",
        "method_family": method_family,
        "method_subtype": method_subtype,
        "method_gate_ref": {
            "path": "Results/json/method_gate_report.json",
            "status": read_json(project_root / "Results" / "json" / "method_gate_report.json").get("gate_status"),
        },
        "design_spec_ref": {
            "path": "state/product/design_spec.json",
            "version": design_spec.get("version"),
            "status": design_spec.get("status"),
        },
        "run_plan_ref": {
            "path": "state/product/run_plan.json",
            "version": run_plan.get("version"),
            "status": run_plan.get("status"),
            "task_id": task.get("id"),
        },
        "method_workflow_ref": method_workflow or {},
        "variables": variables,
        "dataset_profile": {
            **dataset_profile,
            "usable_rows": int(dataset.shape[0]),
            "dropped_rows": max(int((dataset_profile.get("row_count") or 0) - dataset.shape[0]), 0),
            "cluster_count": int(dataset[variables["cluster_by"][0]].nunique()) if variables.get("cluster_by") else None,
        },
        "diagnostics": diagnostics,
        "source_artifacts": [
            {
                "id": "analysis_dataset",
                "path": dataset_path,
                "role": "input_dataset",
                "status": "read",
            },
            {
                "id": "method_diagnostics_report",
                "path": "Results/json/method_diagnostics_report.json",
                "role": "diagnostics_artifact",
                "status": "written_by_cli",
            },
        ],
        "reproducibility": {
            "entrypoint": "Program/method_diagnostics.py",
            "command": "python3 Program/method_diagnostics.py --project-root .",
            "python_packages": {
                "pandas": pd.__version__,
                "statsmodels": "statsmodels.formula.api",
                "linearmodels": "IV2SLS",
            },
            "output_paths": ["Results/json/method_diagnostics_report.json"],
        },
        "formal_state_write": {
            "can_promote": False,
            "requires_human_review": True,
            "protected_paths": PROTECTED_FORMAL_PATHS,
        },
        "write_policy": {
            "mode": "method_diagnostics_report_only",
            "does_not_modify": PROTECTED_FORMAL_PATHS,
            "requires_human_review_before_formal_state_writeback": True,
        },
        "agent_team_schedule": build_agent_team_schedule(),
    }


def load_analysis_dataset(project_root: Path, dataset_path: str, variables: dict[str, Any]) -> pd.DataFrame:
    path = Path(dataset_path)
    absolute_path = path if path.is_absolute() else project_root / path
    if not absolute_path.exists():
        raise ValueError(f"Missing dataset: {dataset_path}")
    if absolute_path.suffix.lower() != ".csv":
        raise ValueError(f"Method diagnostics currently expects CSV data, got {absolute_path.suffix}")

    columns = required_columns(variables)
    raw = pd.read_csv(absolute_path)
    missing = sorted(set(columns) - set(raw.columns))
    if missing:
        raise ValueError(f"Dataset is missing declared variables: {', '.join(missing)}")
    data = raw[columns].copy()
    for column in columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=columns)
    if data.empty:
        raise ValueError("No usable rows after dropping missing declared variables")
    return data


def required_columns(variables: dict[str, Any]) -> list[str]:
    fields = [
        variables.get("outcome"),
        variables.get("endogenous_treatment"),
        variables.get("instrument"),
        *variables.get("controls", []),
        *variables.get("fixed_effects", []),
        *variables.get("cluster_by", []),
    ]
    return unique([str(field) for field in fields if field])


def run_iv_2sls(data: pd.DataFrame, variables: dict[str, Any]) -> dict[str, Any]:
    outcome = variables["outcome"]
    treatment = variables["endogenous_treatment"]
    instrument = variables["instrument"]
    controls = variables.get("controls") or []
    fixed_effects = variables.get("fixed_effects") or []
    cluster_by = variables.get("cluster_by") or []
    formula = build_iv_formula(outcome, treatment, instrument, controls, fixed_effects)
    clusters = data[cluster_by[0]] if cluster_by else None
    result = IV2SLS.from_formula(formula, data=data).fit(
        cov_type="clustered" if cluster_by else "robust",
        clusters=clusters,
    )
    return {
        "formula": formula,
        "nobs": int(result.nobs),
        "coef": safe_float(result.params.get(treatment)),
        "std_error": safe_float(result.std_errors.get(treatment)),
        "t_stat": safe_float(result.tstats.get(treatment)),
        "p_value": safe_float(result.pvalues.get(treatment)),
        "conf_int": safe_conf_int(result, treatment),
        "cov_type": result.cov_type,
        "cluster_by": cluster_by,
        "first_stage": result.first_stage.diagnostics.to_dict(orient="index"),
        "durbin": test_statistic_payload(result.durbin()),
        "wu_hausman": test_statistic_payload(result.wu_hausman()),
        "anderson_rubin": test_statistic_payload(result.anderson_rubin),
    }


def run_reduced_form(data: pd.DataFrame, variables: dict[str, Any]) -> dict[str, Any]:
    return run_ols(
        data,
        outcome=variables["outcome"],
        treatment=variables["instrument"],
        controls=variables.get("controls") or [],
        fixed_effects=variables.get("fixed_effects") or [],
        cluster_by=variables.get("cluster_by") or [],
    )


def run_ols_comparison(data: pd.DataFrame, variables: dict[str, Any]) -> dict[str, Any]:
    return run_ols(
        data,
        outcome=variables["outcome"],
        treatment=variables["endogenous_treatment"],
        controls=variables.get("controls") or [],
        fixed_effects=variables.get("fixed_effects") or [],
        cluster_by=variables.get("cluster_by") or [],
    )


def run_ols(
    data: pd.DataFrame,
    *,
    outcome: str,
    treatment: str,
    controls: list[str],
    fixed_effects: list[str],
    cluster_by: list[str],
) -> dict[str, Any]:
    formula = build_ols_formula(outcome, treatment, controls, fixed_effects)
    model = smf.ols(formula, data=data)
    if cluster_by:
        result = model.fit(cov_type="cluster", cov_kwds={"groups": data[cluster_by[0]]})
    else:
        result = model.fit(cov_type="HC1")
    return {
        "formula": formula,
        "nobs": int(result.nobs),
        "coef": safe_float(result.params.get(treatment)),
        "std_error": safe_float(result.bse.get(treatment)),
        "t_stat": safe_float(result.tvalues.get(treatment)),
        "p_value": safe_float(result.pvalues.get(treatment)),
        "conf_int": safe_conf_int(result, treatment),
        "cov_type": str(result.cov_type),
        "cluster_by": cluster_by,
    }


def summarize_first_stage(baseline: dict[str, Any]) -> dict[str, Any]:
    stages = baseline.get("first_stage") or {}
    if not stages:
        return {}
    row = next(iter(stages.values()))
    return {
        "first_stage_f": safe_float(row.get("f.stat")),
        "first_stage_p": safe_float(row.get("f.pval")),
        "partial_r_squared": safe_float(row.get("partial.rsquared")),
        "rsquared": safe_float(row.get("rsquared")),
        "f_dist": row.get("f.dist"),
    }


def build_sample_consistency(dataset_profile: dict[str, Any], data: pd.DataFrame, run_plan: dict[str, Any]) -> dict[str, Any]:
    expected = run_plan.get("expected_sample_size")
    raw_rows = dataset_profile.get("row_count") or 0
    usable = int(data.shape[0])
    status = "green"
    review_items: list[str] = []
    if expected is not None and int(expected) != usable:
        status = "yellow"
        review_items.append("expected_sample_size_differs_from_usable_rows")
    if raw_rows and raw_rows != usable:
        status = "yellow"
        review_items.append("raw_rows_differ_from_usable_rows_after_missing_drop")
    return {
        "status": status,
        "raw_rows": raw_rows,
        "usable_rows": usable,
        "expected_sample_size": expected,
        "review_items": review_items,
    }


def build_shift_share_component_review(data: pd.DataFrame, variables: dict[str, Any]) -> dict[str, Any]:
    component_columns = [column for column in data.columns if "share" in column.lower() or "shock" in column.lower()]
    instrument = variables["instrument"]
    return {
        "component_available": bool(component_columns),
        "component_columns": component_columns,
        "instrument_variance": safe_float(data[instrument].var()) if instrument in data else None,
        "instrument_missing_share": safe_float(data[instrument].isna().mean()) if instrument in data else None,
        "review_items": [] if component_columns else ["missing_shift_share_components"],
    }


def build_diagnostics(
    baseline: dict[str, Any],
    first_stage: dict[str, Any],
    reduced_form: dict[str, Any],
    ols_comparison: dict[str, Any],
    sample: dict[str, Any],
    shift_share: dict[str, Any],
    *,
    max_leave_one_out: int,
) -> list[dict[str, Any]]:
    first_stage_f = first_stage.get("first_stage_f")
    weak_iv_status = "green" if first_stage_f is not None and first_stage_f >= 10 else "yellow"
    ar = baseline.get("anderson_rubin") or {}
    ar_available = ar.get("stat") is not None
    return [
        diagnostic(
            "baseline_iv_2sls_binding",
            "green" if baseline.get("coef") is not None and baseline.get("conf_int") else "red",
            scope="machine_run",
            outputs=pick_outputs(baseline, ["coef", "std_error", "t_stat", "p_value", "conf_int", "nobs", "cov_type", "cluster_by"]),
            rule={"requires": ["coefficient", "standard_error", "confidence_interval", "task_binding"]},
        ),
        diagnostic(
            "first_stage_relevance",
            "green" if first_stage_f is not None and first_stage_f >= 10 else "yellow",
            scope="machine_run",
            outputs=first_stage,
            rule={"green_if": "first_stage_f >= 10 and partial_r_squared is recorded"},
        ),
        diagnostic(
            "robust_first_stage_f_or_kp",
            weak_iv_status,
            scope="machine_run",
            outputs={
                "statistic": first_stage_f,
                "p_value": first_stage.get("first_stage_p"),
                "backend": "linearmodels_first_stage_clustered",
            },
            rule={"green_if": "clustered first-stage statistic >= 10"},
        ),
        diagnostic(
            "weak_iv_robust_inference_ar_or_clr",
            "yellow" if not ar_available else "green",
            scope="machine_run",
            outputs={
                "anderson_rubin": ar,
                "clr": None,
                "note": "exactly_identified_model_ar_overidentification_test_not_available" if not ar_available else "ar_available",
            },
            rule={"green_if": "AR or CLR robust inference is available and supports the main direction"},
            review_items=[] if ar_available else ["weak_iv_robust_ci_follow_up"],
        ),
        diagnostic(
            "reduced_form",
            "green" if reduced_form.get("coef") is not None else "red",
            scope="machine_run",
            outputs=pick_outputs(reduced_form, ["coef", "std_error", "t_stat", "p_value", "conf_int", "nobs", "cov_type", "cluster_by"]),
            rule={"requires": "outcome ~ instrument + controls + fixed effects"},
        ),
        diagnostic(
            "ols_comparison",
            "green" if ols_comparison.get("coef") is not None else "red",
            scope="machine_run",
            outputs=pick_outputs(ols_comparison, ["coef", "std_error", "t_stat", "p_value", "conf_int", "nobs", "cov_type", "cluster_by"]),
            rule={"requires": "outcome ~ treatment + controls + fixed effects"},
        ),
        diagnostic(
            "sample_consistency",
            sample["status"],
            scope="machine_run",
            outputs=sample,
            rule={"green_if": "raw rows, usable rows and expected sample size are aligned or explained"},
            review_items=sample.get("review_items", []),
        ),
        diagnostic(
            "shift_share_identification_diagnostics",
            "yellow" if not shift_share["component_available"] else "green",
            scope="machine_run",
            outputs=shift_share,
            rule={"green_if": "share and shock components are available and can reconstruct the Bartik instrument"},
            review_items=shift_share.get("review_items", []),
        ),
        diagnostic(
            "shift_share_rotemberg_weights",
            "needs_manual_review",
            scope="manual_review",
            outputs={"max_leave_one_out": max_leave_one_out},
            rule={"requires": "industry-level share and shock components"},
            review_items=shift_share.get("review_items", ["missing_shift_share_components"]),
        ),
        diagnostic(
            "leave_one_out_or_alternative_shock",
            "needs_manual_review",
            scope="manual_review",
            outputs={"component_available": shift_share["component_available"]},
            rule={"requires": "industry or shock level leave-one-out components"},
            review_items=shift_share.get("review_items", ["missing_shift_share_components"]),
        ),
        diagnostic(
            "artifact_binding",
            "green",
            scope="machine_run",
            outputs={
                "diagnostics_artifact_path": "Results/json/method_diagnostics_report.json",
                "task_scoped": True,
            },
            rule={"requires": "task-scoped diagnostics report is written"},
        ),
    ]


def diagnostic(
    id_: str,
    status: str,
    *,
    scope: str,
    outputs: dict[str, Any],
    rule: dict[str, Any],
    review_items: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": id_,
        "status": status,
        "scope": scope,
        "outputs": json_safe(outputs),
        "rule": rule,
        "review_items": review_items or [],
    }


def build_iv_formula(outcome: str, treatment: str, instrument: str, controls: list[str], fixed_effects: list[str]) -> str:
    terms = ["1", *controls, *[f"C({field})" for field in fixed_effects]]
    return f"{outcome} ~ {' + '.join(terms)} + [{treatment} ~ {instrument}]"


def build_ols_formula(outcome: str, treatment: str, controls: list[str], fixed_effects: list[str]) -> str:
    terms = [treatment, *controls, *[f"C({field})" for field in fixed_effects]]
    return f"{outcome} ~ {' + '.join(terms)}"


def test_statistic_payload(value: Any) -> dict[str, Any]:
    stat = safe_float(getattr(value, "stat", None))
    p_value = safe_float(getattr(value, "pval", None))
    return {
        "stat": stat,
        "p_value": p_value,
        "distribution": getattr(value, "dist_name", None),
        "valid": stat is not None and p_value is not None,
    }


def safe_conf_int(result: Any, variable: str) -> list[float] | None:
    try:
        conf = result.conf_int().loc[variable]
    except (KeyError, AttributeError, ValueError):
        return None
    return [safe_float(conf.iloc[0]), safe_float(conf.iloc[1])]


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:
        return None
    return number


def choose_report_status(diagnostics: list[dict[str, Any]]) -> str:
    statuses = {item["status"] for item in diagnostics}
    if "red" in statuses:
        return "blocked"
    if statuses & {"yellow", "needs_manual_review"}:
        return "completed_with_review_items"
    return "ready_for_reviewer"


def pick_outputs(payload: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: payload.get(key) for key in keys if key in payload}


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def json_safe(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def build_agent_team_schedule() -> dict[str, Any]:
    return {
        "call_when": "after_method_gate_yellow_without_red_blockers",
        "recall_when": "after_method_diagnostics_report_written",
        "integration_owner": "main_codex_thread",
        "parallel_lanes": [
            {
                "agent": "ExecutionAgent",
                "task": "真实执行 baseline IV、first stage、reduced form、OLS comparison、sample consistency 和 artifact binding。",
                "output": "method_diagnostics_report",
            },
            {
                "agent": "MethodAgent",
                "task": "诊断产物写出后复核 green/yellow/red 和 needs_manual_review 边界。",
                "activation": "after_execution_agent_recall",
                "output": "method_gate_patch_or_review_notes",
            },
            {
                "agent": "ReviewerAgent",
                "task": "把方法诊断转成审稿式 scorecard 和 revision tasks。",
                "activation": "after_method_agent_recheck",
                "output": "reviewer_scorecard_patch",
            },
        ],
        "next_call_after_recall": "method_agent_and_reviewer_agent",
        "boundary": "ExecutionAgent 写诊断产物；MethodAgent/ReviewerAgent 只读摘要和缺口；主线程合并报告，不直接改正式层。",
    }


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
