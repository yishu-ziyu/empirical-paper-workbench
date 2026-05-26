from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p4.reviewer_scorecard.v1"
PROTECTED_FORMAL_PATHS = [
    "state/product/reviewer_scorecard.json",
    "state/product/agent_task_queue.json",
    "state/product/research_question.json",
    "state/product/variable_roles.json",
    "state/product/design_spec.json",
    "state/product/run_plan.json",
]


def build_reviewer_scorecard_report(project_root: Path, profile: str = "aer_like") -> dict[str, Any]:
    diagnostics_path = project_root / "Results" / "json" / "method_diagnostics_report.json"
    method_gate_path = project_root / "Results" / "json" / "method_gate_report.json"
    diagnostics = read_json(diagnostics_path)
    method_gate = read_json(method_gate_path)
    diagnostic_map = {item.get("id"): item for item in diagnostics.get("diagnostics", [])}

    dimensions = build_dimensions(diagnostic_map, diagnostics)
    revision_tasks = build_revision_tasks(diagnostic_map, method_gate)
    blocks_draft = has_red_blocker(diagnostic_map, method_gate)
    blocks_export_or_formal_claims = any(
        task["blocking_scope"] in {"formal_claims", "formal_claims_and_export", "export"}
        for task in revision_tasks
    )
    overall_score = round(sum(dimension["score"] for dimension in dimensions), 1)
    overall_verdict = build_overall_verdict(blocks_draft, blocks_export_or_formal_claims)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "status": "needs_revision" if revision_tasks else "ready_for_manuscript_expansion",
        "reviewer_backend": "deterministic_method_diagnostics_reviewer",
        "evidence_level": "local_file_plus_recomputed_method_diagnostics",
        "method_family": diagnostics.get("method_family") or method_gate.get("method_family"),
        "method_subtype": diagnostics.get("method_subtype") or method_gate.get("method_subtype"),
        "source_refs": {
            "method_diagnostics_report": {
                "path": "Results/json/method_diagnostics_report.json",
                "schema_version": diagnostics.get("schema_version"),
                "status": diagnostics.get("status"),
            },
            "method_gate_report": {
                "path": "Results/json/method_gate_report.json",
                "schema_version": method_gate.get("schema_version"),
                "gate_status": method_gate.get("gate_status"),
                "status": method_gate.get("status"),
            },
        },
        "overall_score": overall_score,
        "overall_verdict": overall_verdict,
        "blocks_draft": blocks_draft,
        "blocks_export_or_formal_claims": blocks_export_or_formal_claims,
        "confidence_level": build_confidence_level(overall_score, blocks_export_or_formal_claims),
        "dimensions": dimensions,
        "revision_tasks": revision_tasks,
        "formal_state_write": {
            "status": "not_written",
            "protected_paths": PROTECTED_FORMAL_PATHS,
            "reason": "P4-D4 reviewer scorecard is a draft-layer report; formal scorecard and task queue require explicit human acceptance.",
        },
        "agent_team_schedule": build_agent_team_schedule(),
    }


def write_reviewer_scorecard_report(project_root: Path, report: dict[str, Any], output_path: Path | None = None) -> Path:
    output = output_path or (project_root / "Results" / "json" / "reviewer_scorecard_report.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"required report is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_dimensions(diagnostic_map: dict[str, dict[str, Any]], diagnostics: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        execution_binding_dimension(diagnostic_map),
        instrument_relevance_dimension(diagnostic_map),
        weak_iv_dimension(diagnostic_map),
        bartik_dimension(diagnostic_map),
        sample_transparency_dimension(diagnostic_map, diagnostics),
    ]


def execution_binding_dimension(diagnostic_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    baseline = diagnostic_map.get("baseline_iv_2sls_binding", {})
    artifact = diagnostic_map.get("artifact_binding", {})
    score = 18 if is_green(baseline) and is_green(artifact) else 10
    deductions = []
    if not is_green(baseline):
        deductions.append("baseline_iv_2sls_not_bound")
    if not is_green(artifact):
        deductions.append("artifact_binding_not_green")
    return dimension(
        "execution_binding",
        "执行结果绑定",
        score,
        "green" if score >= 16 else "yellow",
        [evidence_from_diagnostic(baseline), evidence_from_diagnostic(artifact)],
        deductions,
        [],
    )


def instrument_relevance_dimension(diagnostic_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    first_stage = diagnostic_map.get("first_stage_relevance", {})
    robust_first_stage = diagnostic_map.get("robust_first_stage_f_or_kp", {})
    first_stage_f = as_float(first_stage.get("outputs", {}).get("first_stage_f"))
    score = 17 if is_green(first_stage) and is_green(robust_first_stage) and first_stage_f >= 10 else 9
    deductions = []
    if first_stage_f < 10:
        deductions.append("first_stage_f_below_10")
    if not is_green(robust_first_stage):
        deductions.append("clustered_first_stage_statistic_missing")
    return dimension(
        "instrument_relevance",
        "工具变量相关性",
        score,
        "green" if score >= 16 else "yellow",
        [evidence_from_diagnostic(first_stage), evidence_from_diagnostic(robust_first_stage)],
        deductions,
        [],
    )


def weak_iv_dimension(diagnostic_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    weak_iv = diagnostic_map.get("weak_iv_robust_inference_ar_or_clr", {})
    score = 18 if is_green(weak_iv) else 8
    task = revision_task(
        "add_weak_iv_robust_interval_or_caveat",
        "major",
        "MethodAgent",
        "formal_claims",
        "weak_iv_robust_inference_ar_or_clr",
        "补充 AR/CLR 等弱工具稳健区间；若当前 exactly identified 设定无法给出，则在主结论中加入因果表述 caveat。",
    )
    return dimension(
        "weak_iv_and_inference_robustness",
        "弱工具与推断稳健性",
        score,
        "green" if is_green(weak_iv) else "yellow",
        [evidence_from_diagnostic(weak_iv)],
        [] if is_green(weak_iv) else ["weak_iv_robust_interval_missing"],
        [] if is_green(weak_iv) else [task],
    )


def bartik_dimension(diagnostic_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    shift_share = diagnostic_map.get("shift_share_identification_diagnostics", {})
    rotemberg = diagnostic_map.get("shift_share_rotemberg_weights", {})
    leave_one_out = diagnostic_map.get("leave_one_out_or_alternative_shock", {})
    all_green = is_green(shift_share) and is_green(rotemberg) and is_green(leave_one_out)
    tasks = [] if all_green else [
        revision_task(
            "recover_bartik_share_shock_components",
            "major",
            "DataAgent",
            "formal_claims_and_export",
            "shift_share_identification_diagnostics",
            "恢复或构造 Bartik share/shock 原始组件，避免把聚合 bartik_iv 当作完整 shift-share 诊断。",
        ),
        revision_task(
            "add_rotemberg_weights_review",
            "major",
            "MethodAgent",
            "formal_claims_and_export",
            "shift_share_rotemberg_weights",
            "在 share/shock 组件可用后计算或审阅 Rotemberg weights。",
        ),
        revision_task(
            "add_leave_one_out_or_alternative_shock_check",
            "major",
            "ExecutionAgent",
            "formal_claims_and_export",
            "leave_one_out_or_alternative_shock",
            "补充 leave-one-out 或 alternative shock 稳健性，不能用普通省级稳健性替代。",
        ),
        revision_task(
            "write_exclusion_and_shock_exogeneity_review",
            "major",
            "MethodAgent",
            "formal_claims",
            "method_gate_review_items",
            "补写排他性限制和 shock exogeneity 的审稿式论证。",
        ),
    ]
    return dimension(
        "bartik_identification_credibility",
        "Bartik 识别可信度",
        18 if all_green else 6,
        "green" if all_green else "yellow",
        [evidence_from_diagnostic(shift_share), evidence_from_diagnostic(rotemberg), evidence_from_diagnostic(leave_one_out)],
        [] if all_green else ["shift_share_components_or_diagnostics_missing"],
        tasks,
    )


def sample_transparency_dimension(diagnostic_map: dict[str, dict[str, Any]], diagnostics: dict[str, Any]) -> dict[str, Any]:
    sample = diagnostic_map.get("sample_consistency", {})
    dataset = diagnostics.get("dataset_profile", {})
    score = 18 if is_green(sample) else 12
    tasks = [] if is_green(sample) else [
        revision_task(
            "explain_missing_drop_and_analysis_sample",
            "minor",
            "DataAgent",
            "transparency_only",
            "sample_consistency",
            "解释 raw rows 到 usable rows 的样本流失、缺失处理和外部有效性边界。",
        )
    ]
    return dimension(
        "sample_and_reporting_transparency",
        "样本与报告透明度",
        score,
        "green" if is_green(sample) else "yellow",
        [evidence_from_diagnostic(sample), {"path": dataset.get("path"), "row_count": dataset.get("row_count"), "usable_rows": dataset.get("usable_rows")}],
        [] if is_green(sample) else ["analysis_sample_drop_requires_explanation"],
        tasks,
    )


def build_revision_tasks(diagnostic_map: dict[str, dict[str, Any]], method_gate: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for dimension_item in [
        weak_iv_dimension(diagnostic_map),
        bartik_dimension(diagnostic_map),
        sample_transparency_dimension(diagnostic_map, {"dataset_profile": {}}),
    ]:
        tasks.extend(dimension_item["revision_tasks"])

    yellow_items = set(method_gate.get("yellow_items", []))
    if "review_exclusion_restriction_argument" in yellow_items and not any(
        task["id"] == "write_exclusion_and_shock_exogeneity_review" for task in tasks
    ):
        tasks.append(
            revision_task(
                "write_exclusion_and_shock_exogeneity_review",
                "major",
                "MethodAgent",
                "formal_claims",
                "method_gate_review_items",
                "补写排他性限制和 shock exogeneity 的审稿式论证。",
            )
        )
    return dedupe_tasks(tasks)


def dimension(
    dimension_id: str,
    label: str,
    score: int,
    status: str,
    evidence: list[dict[str, Any]],
    deductions: list[str],
    revision_tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": dimension_id,
        "label": label,
        "score": score,
        "max_score": 20,
        "status": status,
        "evidence": evidence,
        "deductions": deductions,
        "revision_tasks": revision_tasks,
    }


def revision_task(
    task_id: str,
    severity: str,
    agent: str,
    blocking_scope: str,
    evidence_source: str,
    recommended_action: str,
) -> dict[str, Any]:
    return {
        "id": task_id,
        "severity": severity,
        "agent": agent,
        "blocking_scope": blocking_scope,
        "evidence_source": evidence_source,
        "recommended_action": recommended_action,
        "requires_human_acceptance": True,
        "status": "suggested",
    }


def evidence_from_diagnostic(item: dict[str, Any]) -> dict[str, Any]:
    if not item:
        return {"diagnostic_id": None, "status": "missing"}
    return {
        "diagnostic_id": item.get("id"),
        "status": item.get("status"),
        "outputs": item.get("outputs", {}),
        "review_items": item.get("review_items", []),
    }


def is_green(item: dict[str, Any]) -> bool:
    return item.get("status") == "green"


def as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def has_red_blocker(diagnostic_map: dict[str, dict[str, Any]], method_gate: dict[str, Any]) -> bool:
    if method_gate.get("gate_status") == "red":
        return True
    if method_gate.get("blocking_items"):
        return True
    return any(item.get("status") == "red" for item in diagnostic_map.values())


def build_overall_verdict(blocks_draft: bool, blocks_export_or_formal_claims: bool) -> str:
    if blocks_draft:
        return "blocked"
    if blocks_export_or_formal_claims:
        return "draft_allowed_with_causal_caveat"
    return "draft_allowed"


def build_confidence_level(overall_score: float, blocks_export_or_formal_claims: bool) -> str:
    if blocks_export_or_formal_claims:
        return "medium"
    if overall_score >= 80:
        return "high"
    if overall_score >= 60:
        return "medium"
    return "low"


def dedupe_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for task in tasks:
        if task["id"] in seen:
            continue
        seen.add(task["id"])
        unique.append(task)
    return unique


def build_agent_team_schedule() -> dict[str, Any]:
    return {
        "call_when": "after_method_diagnostics_report_written",
        "called_agents": [
            {
                "agent": "MethodAgent",
                "task": "复核 method_diagnostics_report 的 yellow / needs_manual_review 项。",
                "output": "method_scorecard_deductions",
            },
            {
                "agent": "ReviewerAgent",
                "task": "把方法诊断转成审稿式 scorecard 和 revision tasks。",
                "output": "reviewer_scorecard_report",
            },
        ],
        "recall_when": "after_reviewer_scorecard_report_written",
        "next_call_after_recall": "manuscript_or_export_review",
        "next_call_agents": ["ManuscriptAgent", "ReviewerAgent", "VerifierAgent", "ExportAgent"],
        "boundary": "Scorecard 只写 Results/json 报告；进入正式层或任务队列前必须人工确认。",
    }
