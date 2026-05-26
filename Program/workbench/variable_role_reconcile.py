from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p4.variable_role_reconciliation.v1"
ROLE_KEYS = ["outcome", "treatment", "controls", "instruments", "fixed_effects", "cluster_by"]
PROTECTED_FORMAL_PATHS = [
    "state/product/research_question.json",
    "state/product/variable_roles.json",
    "state/product/design_spec.json",
    "state/product/run_plan.json",
]


def build_variable_role_reconciliation(project_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    research_question = read_json(project_root / "state" / "product" / "research_question.json")
    variable_roles = read_json(project_root / "state" / "product" / "variable_roles.json")
    design_spec = read_json(project_root / "state" / "product" / "design_spec.json")
    run_plan = read_json(project_root / "state" / "product" / "run_plan.json")

    recommended_dataset = (
        design_spec.get("dataset_path")
        or run_plan.get("dataset_path")
        or variable_roles.get("dataset_path")
        or ""
    )
    recommended_roles = normalize_roles(design_spec.get("variables") or {})
    current_roles = normalize_roles(variable_roles.get("roles") or {})
    dataset_profile = profile_dataset(project_root, recommended_dataset)
    missing_dataset_fields = missing_fields(recommended_roles, dataset_profile.get("columns", []))
    detected_conflicts = detect_conflicts(
        variable_roles=variable_roles,
        design_spec=design_spec,
        run_plan=run_plan,
        current_roles=current_roles,
        recommended_roles=recommended_roles,
        recommended_dataset=recommended_dataset,
        missing_dataset_fields=missing_dataset_fields,
    )
    risk_flags = build_risk_flags(
        research_question=research_question,
        design_spec=design_spec,
        recommended_roles=recommended_roles,
        missing_dataset_fields=missing_dataset_fields,
    )

    proposal = {
        "schema_version": SCHEMA_VERSION,
        "proposal_id": f"p4b_variable_role_reconciliation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "proposal_type": "variable_role_reconciliation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "needs_human_review",
        "evidence_level": "local_file",
        "write_policy": {
            "mode": "proposal_only",
            "does_not_modify": PROTECTED_FORMAL_PATHS,
            "requires_human_approval_to_apply": True,
        },
        "formal_state_write": {
            "can_promote": False,
            "requires_human_review": True,
            "protected_paths": PROTECTED_FORMAL_PATHS,
        },
        "formal_state_inputs": {
            "research_question": summarize_state_input(
                research_question,
                "state/product/research_question.json",
                ["version", "status", "question", "evidence_level"],
            ),
            "variable_roles": summarize_state_input(
                variable_roles,
                "state/product/variable_roles.json",
                ["version", "status", "dataset_path", "evidence_level", "roles"],
            ),
            "design_spec": summarize_state_input(
                design_spec,
                "state/product/design_spec.json",
                ["version", "status", "dataset_path", "research_question", "variables", "identification_strategy"],
            ),
            "run_plan": summarize_state_input(
                run_plan,
                "state/product/run_plan.json",
                ["version", "status", "dataset_path", "tasks"],
            ),
        },
        "detected_conflicts": detected_conflicts,
        "recommended_variable_roles": {
            "dataset_path": recommended_dataset,
            "dataset_name": Path(recommended_dataset).name if recommended_dataset else "",
            "roles": recommended_roles,
        },
        "dataset_profile": dataset_profile,
        "missing_dataset_fields": missing_dataset_fields,
        "risk_flags": risk_flags,
        "role_evidence_matrix": build_role_evidence_matrix(recommended_roles),
        "evidence_requirements": build_evidence_requirements(recommended_roles),
        "review_questions": build_review_questions(research_question, variable_roles, recommended_dataset, recommended_roles),
        "agent_team_schedule": {
            "call_when": "after_proposal_written",
            "recall_when": "before_formal_writeback",
            "integration_owner": "main_codex_thread",
            "parallel_lanes": [
                {
                    "agent": "DataAgent",
                    "task": "核验字段、样本口径、缺失率和变量构造 provenance。",
                    "output": "data_evidence_package",
                },
                {
                    "agent": "MethodAgent",
                    "task": "核验变量角色是否满足 IV / DID / OLS 等方法前置条件。",
                    "output": "method_gate_package",
                },
                {
                    "agent": "LiteratureAgent",
                    "task": "核验变量选择是否有文献依据和可引用来源。",
                    "output": "literature_variable_evidence_package",
                },
            ],
            "next_call_after_integration": "after_human_review_approves_or_requests_revision",
            "boundary": "Agent Team 只写证据包和 proposal，不直接写 state/product 正式层。",
        },
    }
    report = build_report(proposal)
    return proposal, report


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_roles(roles: dict[str, Any]) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {}
    for key in ROLE_KEYS:
        value = roles.get(key, [])
        if value is None:
            normalized[key] = []
        elif isinstance(value, list):
            normalized[key] = [str(item) for item in value]
        else:
            normalized[key] = [str(value)]
    return normalized


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
            "note": "Only CSV header profiling is available in this CLI slice.",
        }
    with absolute_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            columns = next(reader)
        except StopIteration:
            columns = []
        row_count = sum(1 for _ in reader)
    return {
        "path": dataset_path,
        "exists": True,
        "suffix": absolute_path.suffix.lower(),
        "columns": columns,
        "row_count": row_count,
        "size_bytes": absolute_path.stat().st_size,
    }


def missing_fields(roles: dict[str, list[str]], columns: list[str]) -> list[str]:
    column_set = set(columns)
    missing: list[str] = []
    for key in ROLE_KEYS:
        for field in roles.get(key, []):
            if field and field not in column_set:
                missing.append(field)
    return missing


def detect_conflicts(
    *,
    variable_roles: dict[str, Any],
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    current_roles: dict[str, list[str]],
    recommended_roles: dict[str, list[str]],
    recommended_dataset: str,
    missing_dataset_fields: list[str],
) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    current_dataset = variable_roles.get("dataset_path")
    if current_dataset and recommended_dataset and current_dataset != recommended_dataset:
        conflicts.append(
            {
                "id": "formal_variable_roles_use_legacy_dataset",
                "severity": "high",
                "formal_field": "state/product/variable_roles.json:dataset_path",
                "current_value": current_dataset,
                "recommended_value": recommended_dataset,
                "evidence_paths": [
                    "state/product/variable_roles.json",
                    "state/product/design_spec.json",
                    "state/product/run_plan.json",
                ],
            }
        )
    role_diffs = {
        key: {"current": current_roles.get(key, []), "recommended": recommended_roles.get(key, [])}
        for key in ROLE_KEYS
        if current_roles.get(key, []) != recommended_roles.get(key, [])
    }
    if role_diffs:
        conflicts.append(
            {
                "id": "formal_variable_roles_disagree_with_design_spec",
                "severity": "high",
                "formal_field": "state/product/variable_roles.json:roles",
                "current_value": current_roles,
                "recommended_value": recommended_roles,
                "role_diffs": role_diffs,
                "evidence_paths": ["state/product/variable_roles.json", "state/product/design_spec.json"],
            }
        )
    if design_spec.get("dataset_path") and run_plan.get("dataset_path") and design_spec.get("dataset_path") != run_plan.get("dataset_path"):
        conflicts.append(
            {
                "id": "design_spec_run_plan_dataset_mismatch",
                "severity": "high",
                "current_value": design_spec.get("dataset_path"),
                "recommended_value": run_plan.get("dataset_path"),
                "evidence_paths": ["state/product/design_spec.json", "state/product/run_plan.json"],
            }
        )
    if missing_dataset_fields:
        conflicts.append(
            {
                "id": "recommended_roles_missing_from_dataset",
                "severity": "high",
                "missing_fields": missing_dataset_fields,
                "evidence_paths": ["state/product/design_spec.json", recommended_dataset],
            }
        )
    return conflicts


def build_risk_flags(
    *,
    research_question: dict[str, Any],
    design_spec: dict[str, Any],
    recommended_roles: dict[str, list[str]],
    missing_dataset_fields: list[str],
) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []
    if recommended_roles.get("instruments"):
        risks.append(
            {
                "id": "instrument_requires_exclusion_restriction_review",
                "severity": "high",
                "message": "工具变量进入正式层前，需要单独证明相关性、排他性约束和构造来源。",
            }
        )
    question = research_question.get("question", "")
    design_question = design_spec.get("research_question", "")
    if question and design_question and question != design_question:
        risks.append(
            {
                "id": "research_question_scope_needs_alignment",
                "severity": "medium",
                "message": "题目层口径与 DesignSpec 口径不完全一致，需要确认是收窄到工资回报，还是保留劳动力匹配效率的总题目。",
            }
        )
    if missing_dataset_fields:
        risks.append(
            {
                "id": "dataset_header_missing_recommended_fields",
                "severity": "high",
                "message": "建议变量角色中存在数据字段缺失，不能进入正式执行。",
            }
        )
    return risks


def build_evidence_requirements(roles: dict[str, list[str]]) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = [
        {
            "role": "outcome",
            "fields": roles.get("outcome", []),
            "required_evidence": ["变量定义", "单位和变换方式", "缺失率", "结果变量与研究问题的对应关系"],
        },
        {
            "role": "treatment",
            "fields": roles.get("treatment", []),
            "required_evidence": ["处理变量定义", "构造来源", "内生性风险", "时间和地区层级"],
        },
        {
            "role": "controls",
            "fields": roles.get("controls", []),
            "required_evidence": ["控制变量选择依据", "遗漏变量风险", "与文献基准设定的对应关系"],
        },
    ]
    if roles.get("instruments"):
        requirements.append(
            {
                "role": "instruments",
                "fields": roles.get("instruments", []),
                "required_evidence": ["第一阶段相关性", "排他性约束论证", "弱工具变量诊断", "构造 provenance"],
            }
        )
    return requirements


def build_role_evidence_matrix(roles: dict[str, list[str]]) -> list[dict[str, Any]]:
    role_templates = {
        "outcome": {
            "evidence_requirements": [
                "codebook_definition",
                "source_dataset_and_provenance",
                "unit_of_observation",
                "time_period_or_measurement_timing",
                "construction_formula_or_raw_field",
                "missingness_distribution_variation",
                "research_question_alignment",
            ],
            "risk_flags": [
                "missing_codebook_definition",
                "constructed_variable_without_formula",
                "multiple_testing_or_outcome_mining_risk",
                "needs_human_review",
            ],
        },
        "treatment": {
            "evidence_requirements": [
                "intervention_or_exposure_definition",
                "assignment_or_take_up_mechanism",
                "source_dataset_and_provenance",
                "time_period_or_measurement_timing",
                "variation_by_unit_or_time",
                "role_specific_identification_claim",
            ],
            "risk_flags": [
                "name_only_heuristic",
                "ambiguous_unit_or_time",
                "reverse_causality_risk",
                "needs_human_review",
            ],
        },
        "controls": {
            "evidence_requirements": [
                "pre_treatment_timing",
                "confounder_or_design_role",
                "supporting_literature_or_design_note",
                "missingness_distribution_variation",
            ],
            "risk_flags": [
                "post_treatment_control_risk",
                "mediator_or_collider_risk",
                "sample_selection_or_attrition_risk",
                "needs_human_review",
            ],
        },
        "instruments": {
            "evidence_requirements": [
                "instrument_construction_provenance",
                "first_stage_relevance",
                "weak_iv_diagnostics",
                "exclusion_restriction_narrative",
                "direct_path_to_outcome_review",
                "supporting_literature_or_design_note",
            ],
            "risk_flags": [
                "instrument_relevance_unchecked",
                "instrument_weak_first_stage_risk",
                "instrument_exclusion_untestable",
                "instrument_direct_path_to_outcome_risk",
                "needs_human_review",
            ],
        },
        "fixed_effects": {
            "evidence_requirements": [
                "panel_or_group_structure",
                "variation_left_after_absorption",
                "design_reason_for_absorption",
            ],
            "risk_flags": [
                "over_absorption_risk",
                "ambiguous_unit_or_time",
                "needs_human_review",
            ],
        },
        "cluster_by": {
            "evidence_requirements": [
                "treatment_assignment_level",
                "error_correlation_level",
                "cluster_count",
            ],
            "risk_flags": [
                "few_clusters_risk",
                "cluster_level_mismatch_risk",
                "needs_human_review",
            ],
        },
    }
    matrix: list[dict[str, Any]] = []
    for role in ROLE_KEYS:
        template = role_templates[role]
        matrix.append(
            {
                "role": role,
                "fields": roles.get(role, []),
                "status": "exploratory_draft_needs_human_review",
                "evidence_requirements": template["evidence_requirements"],
                "risk_flags": template["risk_flags"],
            }
        )
    return matrix


def build_review_questions(
    research_question: dict[str, Any],
    variable_roles: dict[str, Any],
    recommended_dataset: str,
    recommended_roles: dict[str, list[str]],
) -> list[str]:
    return [
        f"是否将正式 VariableRoleSet 从 {variable_roles.get('dataset_path', 'unknown')} 调和到 {recommended_dataset}？",
        f"是否确认 outcome={recommended_roles.get('outcome', [])}、treatment={recommended_roles.get('treatment', [])} 作为下一轮真实执行入口？",
        f"题目“{research_question.get('question', '')}”是否需要同步到 DesignSpec 的更窄工资回报口径，还是保留为更宽研究问题？",
    ]


def summarize_state_input(payload: dict[str, Any], path: str, keys: list[str]) -> dict[str, Any]:
    summary = {"path": path, "exists": bool(payload)}
    for key in keys:
        if key in payload:
            summary[key] = payload[key]
    return summary


def build_report(proposal: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "p4.variable_role_reconciliation_report.v1",
        "generated_at": proposal["generated_at"],
        "status": proposal["status"],
        "proposal_path": "state/proposals/variable_role_reconciliation.json",
        "conflict_count": len(proposal.get("detected_conflicts", [])),
        "risk_count": len(proposal.get("risk_flags", [])),
        "recommended_next_tasks": [
            "review_variable_role_reconciliation",
            "dispatch_data_method_literature_agents",
            "approve_or_request_revision_before_formal_writeback",
        ],
        "agent_team_schedule": proposal.get("agent_team_schedule", {}),
    }


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
