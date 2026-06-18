from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p5.parent_education_wage_variable_role_preflight.v1"
TOPIC = "父母受教育水平对子女工资收入的影响"
TOPIC_SLUG = "parent-education-wage"

DEFAULT_PREFLIGHT_PATH = Path("Results/json/parent_education_wage_p5_variable_role_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/parent_education_wage_p5_variable_role_preflight.md")
P4_FIELD_SOURCE_PATH = Path("Results/json/parent_education_wage_p4_field_source_candidates.json")
P1B_DATA_FIELD_PATH = Path("Results/json/parent_education_wage_data_field_binding_ledger.json")
P2_READINESS_PATH = Path("Results/json/parent_education_wage_p2_execution_readiness.json")
FORMAL_VARIABLE_ROLES_PATH = Path("state/product/variable_roles.json")
FORMAL_DESIGN_SPEC_PATH = Path("state/product/design_spec.json")
FORMAL_RUN_PLAN_PATH = Path("state/product/run_plan.json")


def run_parent_education_wage_variable_role_preflight(project_root: Path) -> tuple[dict[str, Any], Path, Path]:
    preflight = build_parent_education_wage_variable_role_preflight(project_root)
    json_path, review_path = write_parent_education_wage_variable_role_preflight(project_root, preflight)
    return preflight, json_path, review_path


def build_parent_education_wage_variable_role_preflight(project_root: Path) -> dict[str, Any]:
    p4 = load_json(project_root / P4_FIELD_SOURCE_PATH)
    p1b = load_json(project_root / P1B_DATA_FIELD_PATH)
    p2 = load_json(project_root / P2_READINESS_PATH)
    candidate_items = {item.get("dataset_column"): item for item in p4.get("field_source_candidates", [])}
    input_warnings = build_input_warnings(project_root, p4, p1b, p2)

    father = selected_binding(candidate_items, "father_education")
    mother = selected_binding(candidate_items, "mother_education")
    hukou = selected_binding(candidate_items, "hukou")
    parent_ready = bool(father.get("preferred_candidate") and mother.get("preferred_candidate"))
    if not parent_ready:
        status = "blocked_missing_parent_education_candidates"
    elif input_warnings:
        status = "variable_role_preflight_ready_with_input_warnings"
    else:
        status = "variable_role_preflight_ready_for_review"

    outcomes = matched_columns(p1b, roles={"Y"})
    controls = matched_columns(p1b, roles={"control"})
    outcome_preferred = "ln_wage" if "ln_wage" in outcomes else (outcomes[0] if outcomes else None)
    control_preferred = [item for item in ("age", "female", "urban", "edu_last", "experience", "province") if item in controls]

    role_bindings = [
        father,
        mother,
        parent_construction_binding(parent_ready),
        hukou,
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "status": status,
        "run_id": None,
        "source_artifacts": {
            "p4_field_source_candidates": artifact_state(project_root, P4_FIELD_SOURCE_PATH, p4.get("status")),
            "p1b_data_field_binding_ledger": artifact_state(project_root, P1B_DATA_FIELD_PATH, p1b.get("status")),
            "p2_execution_readiness": artifact_state(project_root, P2_READINESS_PATH, p2.get("status")),
        },
        "draft_variable_roles": {
            "outcome": {
                "preferred": outcome_preferred,
                "alternatives": outcomes,
                "decision_status": "draft_needs_human_review"
                if outcomes
                else "source_ledger_missing_needs_review",
            },
            "treatment": {
                "preferred": "parent_education",
                "source_fields": ["father_education", "mother_education"],
                "construction": {
                    "derived_variable": "parent_education",
                    "source_fields": ["father_education", "mother_education"],
                    "options": [
                        "max(father_education, mother_education)",
                        "mean(father_education, mother_education)",
                        "separate father/mother coefficients",
                    ],
                    "recommended_default": "max(father_education, mother_education)",
                    "decision_status": "requires_human_confirmation",
                },
            },
            "controls": {
                "preferred": control_preferred,
                "alternatives": controls,
                "decision_status": "draft_needs_human_review",
            },
            "moderators": {
                "preferred": ["hukou"] if hukou.get("preferred_candidate") else [],
                "decision_status": "requires_human_confirmation",
            },
        },
        "role_bindings": role_bindings,
        "human_review_required": [
            "confirm_preferred_cfps_wave",
            "confirm_parent_education_construction",
            "confirm_hukou_role",
            "confirm_outcome_and_controls",
            "approve_before_formal_variable_roles_write",
        ],
        "input_warnings": input_warnings,
        "can_write_formal_variable_roles": False,
        "would_write_if_approved": "state/product/variable_roles_drafts.json",
        "formal_state": {
            "variable_roles": formal_state(project_root, FORMAL_VARIABLE_ROLES_PATH),
            "design_spec": formal_state(project_root, FORMAL_DESIGN_SPEC_PATH),
            "run_plan": formal_state(project_root, FORMAL_RUN_PLAN_PATH),
        },
        "boundary_flags": {
            "modified_formal_variable_roles": False,
            "modified_formal_design_spec": False,
            "modified_formal_run_plan": False,
            "executed_regression": False,
            "created_run_id": False,
            "called_statspai_paper": False,
        },
        "product_control_signal": {
            "phase": "P5",
            "label": "VariableRoleSet",
            "status": status,
            "next_action": "human_review_variable_role_preflight"
            if parent_ready
            else "return_to_p4_field_source_candidates",
        },
        "outputs": {
            "json": DEFAULT_PREFLIGHT_PATH.as_posix(),
            "review": DEFAULT_REVIEW_PATH.as_posix(),
        },
    }


def selected_binding(candidate_items: dict[str, dict[str, Any]], dataset_column: str) -> dict[str, Any]:
    item = candidate_items.get(dataset_column, {})
    candidates = list(item.get("candidates") or [])
    preferred = choose_preferred_candidate(dataset_column, candidates)
    return {
        "dataset_column": dataset_column,
        "semantic_label": item.get("semantic_label", dataset_column),
        "binding_status": "candidate_selected_for_review" if preferred else "missing_candidate",
        "preferred_candidate": preferred,
        "candidate_count": len(candidates),
        "source_candidates": candidates[:5],
        "decision_status": "requires_human_confirmation" if preferred else "locate_source_field",
        "can_write_formal_variable_roles": False,
    }


def choose_preferred_candidate(dataset_column: str, candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    if dataset_column == "hukou":
        for candidate in candidates:
            if str(candidate.get("name", "")).lower() == "qa2":
                return candidate
    return candidates[0]


def parent_construction_binding(parent_ready: bool) -> dict[str, Any]:
    return {
        "dataset_column": "parent_education",
        "semantic_label": "父母受教育水平",
        "binding_status": "constructable_needs_review" if parent_ready else "missing_parent_source_fields",
        "preferred_candidate": None,
        "candidate_count": 0,
        "source_candidates": [],
        "construction": {
            "source_fields": ["father_education", "mother_education"],
            "recommended_default": "max(father_education, mother_education)",
            "decision_status": "requires_human_confirmation",
        },
        "decision_status": "requires_human_confirmation",
        "can_write_formal_variable_roles": False,
    }


def matched_columns(ledger: dict[str, Any], roles: set[str]) -> list[str]:
    columns: list[str] = []
    for binding in ledger.get("field_bindings", []):
        if binding.get("role") in roles and binding.get("binding_status") == "matched":
            column = binding.get("dataset_column")
            if column and column not in columns:
                columns.append(column)
    return columns


def build_input_warnings(project_root: Path, p4: dict[str, Any], p1b: dict[str, Any], p2: dict[str, Any]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    if not (project_root / P4_FIELD_SOURCE_PATH).exists() or not p4.get("field_source_candidates"):
        warnings.append(
            {
                "id": "missing_p4_field_source_candidates",
                "severity": "blocking",
                "message": "P5 requires P4 field source candidates before variable-role preflight.",
            }
        )
    if not (project_root / P1B_DATA_FIELD_PATH).exists() or not p1b.get("field_bindings"):
        warnings.append(
            {
                "id": "missing_p1b_data_field_binding_ledger",
                "severity": "needs_review",
                "message": "Outcome and controls cannot be trusted until the P1-B data field binding ledger is present.",
            }
        )
    if not (project_root / P2_READINESS_PATH).exists():
        warnings.append(
            {
                "id": "missing_p2_execution_readiness",
                "severity": "needs_review",
                "message": "Execution-readiness blockers are not available for this preflight.",
            }
        )
    return warnings


def artifact_state(project_root: Path, relative_path: Path, status: str | None = None) -> dict[str, Any]:
    path = project_root / relative_path
    return {"path": relative_path.as_posix(), "exists": path.exists(), "status": status}


def formal_state(project_root: Path, relative_path: Path) -> dict[str, Any]:
    return {"path": relative_path.as_posix(), "exists": (project_root / relative_path).exists(), "modified": False}


def write_parent_education_wage_variable_role_preflight(
    project_root: Path,
    preflight: dict[str, Any],
    preflight_path: Path = DEFAULT_PREFLIGHT_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_preflight_path = project_root / preflight_path
    absolute_review_path = project_root / review_path
    absolute_preflight_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review_path.write_text(render_review(preflight), encoding="utf-8")
    return absolute_preflight_path, absolute_review_path


def render_review(preflight: dict[str, Any]) -> str:
    treatment = preflight["draft_variable_roles"]["treatment"]
    controls = preflight["draft_variable_roles"]["controls"]
    lines = [
        "# P5 VariableRoleSet 草案预检",
        "",
        f"- 题目：{preflight['topic']}",
        f"- 状态：`{preflight['status']}`",
        f"- outcome 草案：`{preflight['draft_variable_roles']['outcome']['preferred'] or '待确认'}`",
        f"- treatment 草案：`{treatment['preferred']}`",
        f"- parent_education 构造建议：`{treatment['construction']['recommended_default']}`",
        f"- controls 草案：{', '.join(controls['preferred']) if controls['preferred'] else 'none'}",
        "- 正式 VariableRoleSet 写回：否",
        "- 正式 DesignSpec 写回：否",
        "- 正式 RunPlan 写回：否",
        "- 执行回归：否",
        "",
        "## 字段绑定草案",
    ]
    for binding in preflight["role_bindings"]:
        candidate = binding.get("preferred_candidate") or {}
        lines.append(
            f"- `{binding['dataset_column']}` | {binding['binding_status']} | "
            f"`{candidate.get('name', 'none')}` | {candidate.get('label', '')}"
        )
    if preflight.get("input_warnings"):
        lines.extend(["", "## 输入警告"])
        lines.extend(f"- `{item['id']}` | {item['severity']} | {item['message']}" for item in preflight["input_warnings"])
    lines.extend(["", "## 人工确认"])
    lines.extend(f"- `{item}`" for item in preflight["human_review_required"])
    lines.append("")
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
