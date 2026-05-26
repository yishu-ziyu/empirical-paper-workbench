from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Product.backend.method_workflow_service import build_method_workflows


SCHEMA_VERSION = "p4.method_gate.v1"
PROTECTED_FORMAL_PATHS = [
    "state/product/research_question.json",
    "state/product/variable_roles.json",
    "state/product/design_spec.json",
    "state/product/run_plan.json",
]


def build_method_gate_report(project_root: Path, *, profile: str = "aer_like") -> dict[str, Any]:
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
    dataset_profile = profile_dataset(project_root, design_spec.get("dataset_path") or run_plan.get("dataset_path") or "")
    method_diagnostics = read_json(project_root / "Results" / "json" / "method_diagnostics_report.json")
    method_workflow = next(
        (method for method in build_method_workflows(design_spec) if method.get("id") == method_family),
        None,
    )

    pre_checks = build_pre_checks(design_spec, run_plan, task, variables, dataset_profile)
    diagnostics = build_diagnostics(design_spec, task, dataset_profile, method_diagnostics)
    yellow_items = build_yellow_items(pre_checks, diagnostics, method_subtype)
    red_items = build_red_items(pre_checks, diagnostics)
    gate_status = choose_gate_status(red_items, yellow_items)
    required_evidence = build_required_evidence(yellow_items, red_items, method_subtype)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "status": "needs_human_review" if gate_status != "green" else "ready_for_reviewer",
        "evidence_level": "local_file_plus_method_standard",
        "method_family": method_family,
        "method_subtype": method_subtype,
        "gate_status": gate_status,
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
        "method_diagnostics_ref": build_method_diagnostics_ref(method_diagnostics),
        "method_workflow_ref": method_workflow or {},
        "variables": variables,
        "dataset_profile": dataset_profile,
        "pre_checks": pre_checks,
        "diagnostics": diagnostics,
        "required_evidence": required_evidence,
        "blocking_items": red_items,
        "yellow_items": yellow_items,
        "red_items": red_items,
        "recommended_next_tasks": build_recommended_next_tasks(required_evidence, method_subtype),
        "formal_state_write": {
            "can_promote": False,
            "requires_human_review": True,
            "protected_paths": PROTECTED_FORMAL_PATHS,
        },
        "write_policy": {
            "mode": "method_gate_report_only",
            "does_not_modify": PROTECTED_FORMAL_PATHS,
            "requires_human_review_before_formal_state_writeback": True,
        },
        "agent_team_schedule": build_agent_team_schedule(gate_status),
        "paper_quality_contract": {
            "readable_by": "p4.paper_quality.v1",
            "report_path": "Results/json/method_gate_report.json",
            "blocks_export_if_red": True,
        },
    }


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def select_primary_task(run_plan: dict[str, Any]) -> dict[str, Any]:
    tasks = run_plan.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return {}
    return next((task for task in tasks if str(task.get("estimator") or task.get("method_id")).lower() == "iv"), tasks[0])


def infer_method_family(design_spec: dict[str, Any], task: dict[str, Any]) -> str:
    candidates = [
        task.get("method_id"),
        task.get("estimator"),
        design_spec.get("model", {}).get("estimator"),
        design_spec.get("identification_strategy", {}).get("name"),
    ]
    joined = " ".join(str(candidate).lower() for candidate in candidates if candidate)
    if "iv" in joined or "2sls" in joined:
        return "iv"
    for method in ["did", "rdd", "psm", "dml"]:
        if method in joined:
            return method
    return "ols"


def infer_method_subtype(design_spec: dict[str, Any], task: dict[str, Any], method_family: str) -> str:
    text = " ".join(
        str(value).lower()
        for value in [
            design_spec.get("identification_strategy", {}).get("name"),
            design_spec.get("identification_strategy", {}).get("summary"),
            task.get("id"),
            task.get("label"),
            task.get("formula"),
            task.get("instrument_formula"),
        ]
        if value
    )
    if method_family == "iv" and ("bartik" in text or "shift" in text):
        return "bartik_shift_share_iv"
    if method_family == "iv":
        return "iv_2sls"
    return method_family


def extract_variables(design_spec: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    roles = design_spec.get("variables") or {}
    model = design_spec.get("model") or {}
    return {
        "outcome": first_string(roles.get("outcome")),
        "endogenous_treatment": first_string(roles.get("treatment")),
        "instrument": first_string(roles.get("instruments")),
        "controls": normalize_string_list(roles.get("controls")),
        "fixed_effects": normalize_string_list(roles.get("fixed_effects")) or normalize_string_list(model.get("fixed_effects")) or normalize_string_list(task.get("fixed_effects")),
        "cluster_by": normalize_string_list(roles.get("cluster_by")) or normalize_string_list(model.get("cluster_by")) or normalize_string_list(task.get("cluster_by")),
        "formula": task.get("formula") or model.get("formula"),
        "instrument_formula": task.get("instrument_formula") or model.get("instrument_formula"),
    }


def build_pre_checks(
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    task: dict[str, Any],
    variables: dict[str, Any],
    dataset_profile: dict[str, Any],
) -> list[dict[str, Any]]:
    strategy = design_spec.get("identification_strategy") or {}
    assumptions = normalize_string_list(strategy.get("assumptions"))
    threats = normalize_string_list(strategy.get("threats"))
    columns = set(dataset_profile.get("columns") or [])
    checks = [
        check("design_spec_approved", "passed" if design_spec.get("status") == "approved" else "missing", [design_spec.get("status")]),
        check("run_plan_approved", "passed" if run_plan.get("status") == "approved" else "missing", [run_plan.get("status")]),
        check("variables_declared", "passed" if variables["outcome"] and variables["endogenous_treatment"] else "missing", [variables["outcome"], variables["endogenous_treatment"]]),
        check("instrument_declared", "passed" if variables["instrument"] else "missing", [variables["instrument"]]),
        check("structural_equation_declared", "passed" if variables.get("formula") else "missing", [variables.get("formula")]),
        check("first_stage_equation_declared", "passed" if variables.get("instrument_formula") else "missing", [variables.get("instrument_formula")]),
        check("fixed_effects_declared", "passed" if variables.get("fixed_effects") else "needs_human_review", variables.get("fixed_effects", [])),
        check("cluster_level_declared", "passed" if variables.get("cluster_by") else "needs_human_review", variables.get("cluster_by", [])),
        check("analysis_sample_declared", "passed" if dataset_profile.get("exists") else "missing", [dataset_profile.get("path")]),
        check(
            "dataset_contains_declared_variables",
            "passed" if all_declared_fields_present(variables, columns) else "missing",
            sorted(columns),
        ),
        check(
            "exclusion_restriction_argument",
            "needs_human_review" if has_keyword(assumptions + threats, ["排他", "exclusion"]) else "missing",
            assumptions + threats,
            severity="blocking_if_missing",
        ),
        check(
            "share_or_shock_exogeneity_position",
            "needs_human_review" if has_keyword(assumptions + threats, ["产业结构", "行业", "冲击", "shock", "share"]) else "missing",
            assumptions + threats,
            severity="blocking_if_missing",
        ),
        check("late_monotonicity_position", "missing", [], severity="review_required_for_late_claims"),
    ]
    if variables["instrument"]:
        checks.append(check("overidentification_applicability", "not_applicable", [variables["instrument"]]))
    return checks


def build_diagnostics(
    design_spec: dict[str, Any],
    task: dict[str, Any],
    dataset_profile: dict[str, Any],
    method_diagnostics: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    strategy = design_spec.get("identification_strategy") or {}
    first_stage = strategy.get("first_stage_diagnostics") or (design_spec.get("diagnostics") or {}).get("first_stage") or {}
    task_diag = task.get("diagnostics") or task.get("reference_result") or {}
    f_stat = first_non_null(
        first_stage.get("f_statistic"),
        first_stage.get("first_stage_f"),
        task_diag.get("first_stage_f"),
        task_diag.get("first_stage_F"),
    )
    partial_r2 = first_non_null(
        first_stage.get("partial_r_squared"),
        task_diag.get("partial_r_squared"),
        task_diag.get("partial_r2"),
    )
    dwh_f = first_non_null(first_stage.get("dwh_f_statistic"), (design_spec.get("diagnostics") or {}).get("dwh", {}).get("f_statistic"))
    dwh_p = first_non_null(first_stage.get("dwh_p_value"), (design_spec.get("diagnostics") or {}).get("dwh", {}).get("p_value"))
    cluster_count = estimate_cluster_count(dataset_profile)
    computed = collect_method_diagnostics(method_diagnostics or {})
    return [
        diagnostic("first_stage_f", "passed" if f_stat is not None and float(f_stat) > 10 else "missing", observed=f_stat, threshold=10),
        diagnostic("partial_r_squared", "recorded" if partial_r2 is not None else "missing", observed=partial_r2),
        diagnostic("dwh_endogeneity_test", "recorded" if dwh_f is not None or dwh_p is not None else "missing", observed=dwh_f, p_value=dwh_p),
        diagnostic("cluster_count", "recorded" if cluster_count is not None else "missing", observed=cluster_count),
        diagnostic_from_computed(computed, "reduced_form", "missing"),
        diagnostic_from_computed(computed, "robust_first_stage_f_or_kp", "missing"),
        diagnostic_from_computed(computed, "weak_iv_robust_inference_ar_or_clr", "missing"),
        diagnostic_from_computed(computed, "shift_share_identification_diagnostics", "missing"),
        diagnostic_from_computed(computed, "shift_share_rotemberg_weights", "missing"),
        diagnostic_from_computed(computed, "leave_one_out_or_alternative_shock", "missing"),
        diagnostic_from_computed(computed, "result_artifact_binding", "missing"),
    ]


def build_yellow_items(pre_checks: list[dict[str, Any]], diagnostics: list[dict[str, Any]], method_subtype: str) -> list[str]:
    items = [
        f"missing_{item['id']}"
        for item in diagnostics
        if item.get("status") in {"missing", "needs_manual_review", "blocked", "yellow"}
        and item["id"]
        in {
            "reduced_form",
            "robust_first_stage_f_or_kp",
            "weak_iv_robust_inference_ar_or_clr",
            "shift_share_identification_diagnostics",
            "shift_share_rotemberg_weights",
            "leave_one_out_or_alternative_shock",
            "result_artifact_binding",
        }
    ]
    for item in pre_checks:
        if item.get("status") == "needs_human_review":
            items.append(f"review_{item['id']}")
    if "missing_weak_iv_robust_inference_ar_or_clr" in items:
        items.append("missing_weak_iv_robust_inference")
    if method_subtype == "bartik_shift_share_iv" and "missing_shift_share_identification_diagnostics" not in items:
        items.append("missing_shift_share_identification_diagnostics")
    return sorted(set(items))


def build_red_items(pre_checks: list[dict[str, Any]], diagnostics: list[dict[str, Any]]) -> list[str]:
    items: list[str] = []
    hard_pre_checks = {
        "design_spec_approved",
        "run_plan_approved",
        "variables_declared",
        "instrument_declared",
        "structural_equation_declared",
        "first_stage_equation_declared",
        "analysis_sample_declared",
        "dataset_contains_declared_variables",
    }
    for item in pre_checks:
        if item.get("id") in hard_pre_checks and item.get("status") == "missing":
            items.append(f"missing_{item['id']}")
    first_stage = next((item for item in diagnostics if item.get("id") == "first_stage_f"), None)
    if first_stage and first_stage.get("status") == "missing":
        items.append("missing_first_stage_diagnostics")
    return sorted(set(items))


def build_method_diagnostics_ref(method_diagnostics: dict[str, Any]) -> dict[str, Any]:
    if not method_diagnostics:
        return {
            "path": "Results/json/method_diagnostics_report.json",
            "status": "missing",
        }
    return {
        "path": "Results/json/method_diagnostics_report.json",
        "schema_version": method_diagnostics.get("schema_version"),
        "status": method_diagnostics.get("status"),
        "generated_at": method_diagnostics.get("generated_at"),
    }


def collect_method_diagnostics(method_diagnostics: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_id = {
        str(item.get("id")): item
        for item in method_diagnostics.get("diagnostics", [])
        if item.get("id")
    }
    aliases = {
        "robust_first_stage_f_or_kp": "robust_first_stage_f_or_kp",
        "weak_iv_robust_inference_ar_or_clr": "weak_iv_robust_inference_ar_or_clr",
        "result_artifact_binding": "artifact_binding",
    }
    for target, source in aliases.items():
        if target not in by_id and source in by_id:
            by_id[target] = by_id[source]
    return by_id


def diagnostic_from_computed(computed: dict[str, dict[str, Any]], id_: str, fallback_status: str) -> dict[str, Any]:
    item = computed.get(id_)
    if not item:
        return diagnostic(id_, fallback_status)
    status = item.get("status")
    if status == "green":
        mapped_status = "recorded"
    elif status in {"yellow", "needs_manual_review", "blocked", "red"}:
        mapped_status = status
    else:
        mapped_status = "recorded"
    payload = diagnostic(id_, mapped_status)
    outputs = item.get("outputs")
    if outputs:
        payload["observed"] = outputs
    review_items = item.get("review_items")
    if review_items:
        payload["review_items"] = review_items
    return payload


def choose_gate_status(red_items: list[str], yellow_items: list[str]) -> str:
    if red_items:
        return "red"
    if yellow_items:
        return "yellow"
    return "green"


def build_required_evidence(yellow_items: list[str], red_items: list[str], method_subtype: str) -> list[str]:
    mapping = {
        "missing_reduced_form": "reduced_form",
        "missing_robust_first_stage_f_or_kp": "robust_first_stage_f_or_kp",
        "missing_weak_iv_robust_inference": "weak_iv_robust_inference_ar_or_clr",
        "missing_weak_iv_robust_inference_ar_or_clr": "weak_iv_robust_inference_ar_or_clr",
        "missing_shift_share_identification_diagnostics": "shift_share_identification_diagnostics",
        "missing_shift_share_rotemberg_weights": "shift_share_rotemberg_weights",
        "missing_leave_one_out_or_alternative_shock": "leave_one_out_or_alternative_shock",
        "missing_result_artifact_binding": "result_artifact_binding",
        "review_exclusion_restriction_argument": "exclusion_restriction_review",
        "review_share_or_shock_exogeneity_position": "shift_share_identification_narrative_review",
    }
    evidence = [mapping[item] for item in yellow_items + red_items if item in mapping]
    if method_subtype == "bartik_shift_share_iv":
        evidence.extend(["shift_share_identification_diagnostics", "exclusion_restriction_review"])
    return sorted(set(evidence))


def build_recommended_next_tasks(required_evidence: list[str], method_subtype: str) -> list[dict[str, Any]]:
    tasks = [
        {
            "id": "run_iv_reduced_form",
            "agent": "ExecutionAgent",
            "reason": "把工具变量对结果变量的 reduced form 写成独立结果。",
            "required_evidence": ["reduced_form"],
        },
        {
            "id": "run_weak_iv_robust_inference",
            "agent": "ExecutionAgent",
            "reason": "补 Anderson-Rubin / CLR 等弱工具稳健推断。",
            "required_evidence": ["weak_iv_robust_inference_ar_or_clr", "robust_first_stage_f_or_kp"],
        },
        {
            "id": "review_exclusion_restriction",
            "agent": "MethodAgent",
            "reason": "审阅 Bartik 工具变量排他性约束和识别叙事。",
            "required_evidence": ["exclusion_restriction_review"],
        },
    ]
    if method_subtype == "bartik_shift_share_iv":
        tasks.append(
            {
                "id": "run_shift_share_diagnostics",
                "agent": "ExecutionAgent",
                "reason": "补 Rotemberg weights、leave-one-out 或 shock-level / exposure-level 诊断。",
                "required_evidence": ["shift_share_identification_diagnostics"],
            }
        )
    return [task for task in tasks if set(task["required_evidence"]) & set(required_evidence)]


def build_agent_team_schedule(gate_status: str) -> dict[str, Any]:
    return {
        "call_when": "after_design_spec_and_run_plan_approved",
        "recall_when": "after_method_gate_report_written",
        "integration_owner": "main_codex_thread",
        "parallel_lanes": [
            {
                "agent": "MethodAgent",
                "task": "核验 IV/Bartik 前置条件、排除限制、shift-share 识别叙事和方法门状态。",
                "output": "method_gate_patch",
            },
            {
                "agent": "DataAgent",
                "task": "核验变量字段、样本、聚类层级、Bartik 构造来源和数据时间顺序。",
                "output": "data_method_evidence_package",
            },
            {
                "agent": "ExecutionAgent",
                "task": "在 gate 非 red 时补 first stage、reduced form、弱工具稳健推断和 shift-share 诊断。",
                "output": "method_diagnostics_artifacts",
                "activation": "defer_until_gate_not_red",
            },
        ],
        "next_call_after_integration": "after_method_diagnostics_execution",
        "next_recall_when": "before_reviewer_scorecard_and_manuscript_claims",
        "if_red": "收回主估计，只允许补变量、设计或诊断 proposal。",
        "if_yellow": "允许继续草稿层和诊断执行，但所有因果主张保持 needs_human_review。",
        "if_green": "进入 ReviewerAgent 审稿式修订和 ManuscriptAgent 扩写。",
        "boundary": "Agent Team 只写方法证据包、诊断产物和 proposal，不直接写 state/product 正式层。",
        "current_gate_status": gate_status,
    }


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def profile_dataset(project_root: Path, dataset_path: str) -> dict[str, Any]:
    if not dataset_path:
        return {"path": "", "exists": False, "columns": [], "row_count": 0}
    path = Path(dataset_path)
    absolute_path = path if path.is_absolute() else project_root / path
    if not absolute_path.exists():
        return {"path": dataset_path, "exists": False, "columns": [], "row_count": 0}
    if absolute_path.suffix.lower() != ".csv":
        return {
            "path": dataset_path,
            "exists": True,
            "suffix": absolute_path.suffix.lower(),
            "columns": [],
            "row_count": None,
            "size_bytes": absolute_path.stat().st_size,
        }
    with absolute_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        row_count = 0
        cluster_values: dict[str, set[str]] = {}
        for row in reader:
            row_count += 1
            for cluster_key in ["provcd", "cluster", "state"]:
                if cluster_key in row:
                    cluster_values.setdefault(cluster_key, set()).add(row[cluster_key])
    return {
        "path": dataset_path,
        "exists": True,
        "suffix": absolute_path.suffix.lower(),
        "columns": columns,
        "row_count": row_count,
        "size_bytes": absolute_path.stat().st_size,
        "cluster_counts": {key: len(values) for key, values in cluster_values.items()},
    }


def estimate_cluster_count(dataset_profile: dict[str, Any]) -> int | None:
    cluster_counts = dataset_profile.get("cluster_counts") or {}
    if not cluster_counts:
        return None
    return next(iter(cluster_counts.values()))


def all_declared_fields_present(variables: dict[str, Any], columns: set[str]) -> bool:
    if not columns:
        return False
    fields = [
        variables.get("outcome"),
        variables.get("endogenous_treatment"),
        variables.get("instrument"),
        *variables.get("controls", []),
        *variables.get("fixed_effects", []),
        *variables.get("cluster_by", []),
    ]
    return all(field in columns for field in fields if field)


def normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def first_string(value: Any) -> str:
    values = normalize_string_list(value)
    return values[0] if values else ""


def first_non_null(*values: Any) -> Any:
    return next((value for value in values if value is not None), None)


def has_keyword(values: list[str], keywords: list[str]) -> bool:
    text = "\n".join(values).lower()
    return any(keyword.lower() in text for keyword in keywords)


def check(id_: str, status: str, evidence: list[Any], *, severity: str = "required") -> dict[str, Any]:
    return {
        "id": id_,
        "status": status,
        "severity": severity,
        "evidence": [item for item in evidence if item not in {None, ""}],
    }


def diagnostic(id_: str, status: str, *, observed: Any = None, threshold: Any = None, p_value: Any = None) -> dict[str, Any]:
    payload = {"id": id_, "status": status}
    if observed is not None:
        payload["observed"] = observed
    if threshold is not None:
        payload["threshold"] = threshold
    if p_value is not None:
        payload["p_value"] = p_value
    return payload
