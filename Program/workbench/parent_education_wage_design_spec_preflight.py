from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Product.backend.design_spec_service import build_formula, build_method_catalog
from Product.backend.variable_role_service import load_saved_variable_role_set
from Program.workbench.parent_education_wage_variable_role_preflight import TOPIC, TOPIC_SLUG


SCHEMA_VERSION = "p12.parent_education_wage_design_spec_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path("Results/json/parent_education_wage_p12_design_spec_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/parent_education_wage_p12_design_spec_preflight.md")
FORMAL_DESIGN_SPEC_PATH = Path("state/product/design_spec.json")
FORMAL_RUN_PLAN_PATH = Path("state/product/run_plan.json")


def run_parent_education_wage_design_spec_preflight(project_root: Path) -> tuple[dict[str, Any], Path, Path]:
    preflight = build_parent_education_wage_design_spec_preflight(project_root)
    json_path, review_path = write_parent_education_wage_design_spec_preflight(project_root, preflight)
    return preflight, json_path, review_path


def build_parent_education_wage_design_spec_preflight(project_root: Path) -> dict[str, Any]:
    role_set = load_saved_variable_role_set(project_root)
    base = base_packet(project_root)
    if not role_set or role_set.get("status") != "approved":
        return {
            **base,
            "status": "blocked_missing_formal_variable_roles",
            "formal_variable_role_set": None,
            "draft_design_spec": None,
            "method_catalog": {"methods": []},
            "blocking_reasons": ["complete_p9_formal_variable_role_save"],
            "product_control_signal": {
                "phase": "P12",
                "label": "DesignSpec Preflight",
                "status": "blocked_missing_formal_variable_roles",
                "next_action": "complete_p9_formal_variable_role_save",
            },
        }

    roles = normalize_roles(role_set.get("roles", {}))
    missing_roles = required_role_gaps(roles)
    dataset_path = str(role_set.get("dataset_path", "")).strip()
    if not dataset_path:
        missing_roles.append("dataset_path")
    if missing_roles:
        return {
            **base,
            "status": "blocked_incomplete_formal_variable_roles",
            "formal_variable_role_set": role_set,
            "draft_design_spec": None,
            "method_catalog": {"methods": []},
            "blocking_reasons": missing_roles,
            "product_control_signal": {
                "phase": "P12",
                "label": "DesignSpec Preflight",
                "status": "blocked_incomplete_formal_variable_roles",
                "next_action": "return_to_p9_formal_variable_role_save",
            },
        }

    formula = build_formula(roles)
    model = {
        "estimator": "ols",
        "formula": formula,
        "fixed_effects": roles.get("fixed_effects", []),
        "cluster_by": roles.get("cluster_by", []),
        "sample_filter": "all",
    }
    draft_design_spec = {
        "id": "design_spec_preflight_parent_education_wage",
        "version": 0,
        "status": "preflight_draft",
        "evidence_level": "local_file",
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "variable_role_set_version": role_set.get("version", 0),
        "variable_role_set_path": "state/product/variable_roles.json",
        "dataset_path": dataset_path,
        "research_question": TOPIC,
        "variables": roles,
        "identification_strategy": {
            "name": "baseline_ols",
            "summary": "先以 OLS 作为可审阅基准规格；DID/IV/RDD 只有在额外识别变量补齐后才可进入后续审批。",
            "assumptions": [
                "父母教育构造口径已在 P11/P9 中签收。",
                "结果变量、处理变量和控制变量均来自已签收分析数据集。",
            ],
            "threats": [
                "父母教育可能仍有内生性，OLS 只能作为基准相关性规格。",
                "当前没有工具变量、处理时点或 running variable，不能声称 IV/DID/RDD。",
            ],
        },
        "model": model,
        "human_review_required": [
            "confirm_baseline_ols_as_first_design_spec",
            "confirm_parent_education_endogeneity_limitation",
            "confirm_no_did_iv_rdd_without_extra_identification_fields",
            "approve_before_formal_design_spec_write",
        ],
        "updated_at": now(),
    }
    method_catalog = build_method_catalog({"variables": roles, "model": model})
    return {
        **base,
        "status": "design_spec_preflight_ready_for_review",
        "formal_variable_role_set": {
            "path": "state/product/variable_roles.json",
            "version": role_set.get("version", 0),
            "status": role_set.get("status"),
            "dataset_path": dataset_path,
            "roles": roles,
        },
        "draft_design_spec": draft_design_spec,
        "method_catalog": method_catalog,
        "blocking_reasons": [],
        "can_request_human_design_spec_confirmation": True,
        "product_control_signal": {
            "phase": "P12",
            "label": "DesignSpec Preflight",
            "status": "design_spec_preflight_ready_for_review",
            "next_action": "human_review_design_spec_preflight",
        },
    }


def write_parent_education_wage_design_spec_preflight(
    project_root: Path,
    preflight: dict[str, Any],
) -> tuple[Path, Path]:
    json_path = project_root / DEFAULT_PREFLIGHT_PATH
    review_path = project_root / DEFAULT_REVIEW_PATH
    json_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_review(preflight), encoding="utf-8")
    return json_path, review_path


def base_packet(project_root: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "run_id": None,
        "can_write_design_spec": False,
        "can_write_run_plan": False,
        "can_create_run_id": False,
        "can_execute_model": False,
        "can_request_human_design_spec_confirmation": False,
        "formal_state": {
            "design_spec": formal_state(project_root, FORMAL_DESIGN_SPEC_PATH),
            "run_plan": formal_state(project_root, FORMAL_RUN_PLAN_PATH),
        },
        "boundary_flags": {
            "modified_formal_variable_roles": False,
            "modified_formal_design_spec": False,
            "modified_formal_run_plan": False,
            "created_run_id": False,
            "executed_regression": False,
        },
        "outputs": {
            "json": DEFAULT_PREFLIGHT_PATH.as_posix(),
            "review": DEFAULT_REVIEW_PATH.as_posix(),
        },
    }


def normalize_roles(value: dict[str, Any]) -> dict[str, list[str]]:
    role_keys = [
        "outcome",
        "treatment",
        "controls",
        "instruments",
        "fixed_effects",
        "cluster_by",
        "unit_id",
        "time_variable",
        "entity_id",
        "panel_time",
        "treatment_timing",
        "running_variable",
    ]
    return {key: normalize_string_list(value.get(key)) for key in role_keys}


def required_role_gaps(roles: dict[str, list[str]]) -> list[str]:
    gaps: list[str] = []
    if not roles.get("outcome"):
        gaps.append("outcome")
    if not roles.get("treatment"):
        gaps.append("treatment")
    return gaps


def normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def formal_state(project_root: Path, relative_path: Path) -> dict[str, Any]:
    path = project_root / relative_path
    return {
        "path": relative_path.as_posix(),
        "exists": path.exists(),
        "size": path.stat().st_size if path.exists() else 0,
    }


def render_review(preflight: dict[str, Any]) -> str:
    draft = preflight.get("draft_design_spec") or {}
    method_catalog = preflight.get("method_catalog") or {}
    methods = method_catalog.get("methods") or []
    lines = [
        "# P12 DesignSpec Preflight Review",
        "",
        f"- status: `{preflight.get('status')}`",
        f"- topic: {preflight.get('topic')}",
        f"- dataset: {draft.get('dataset_path', 'n/a')}",
        f"- formula: `{draft.get('model', {}).get('formula', '')}`",
        f"- can_write_design_spec: `{preflight.get('can_write_design_spec')}`",
        f"- can_write_run_plan: `{preflight.get('can_write_run_plan')}`",
        f"- can_create_run_id: `{preflight.get('can_create_run_id')}`",
        f"- can_execute_model: `{preflight.get('can_execute_model')}`",
        "",
        "## Method Readiness",
        "",
    ]
    for method in methods:
        blockers = ", ".join(method.get("blockers") or []) or "none"
        lines.append(f"- {method.get('id')}: {method.get('readiness_status')} / blockers: {blockers}")
    lines.extend(
        [
            "",
            "## Human Review Required",
            "",
        ]
    )
    for item in draft.get("human_review_required", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "P12 only writes this preflight review package. It does not write formal DesignSpec, RunPlan, run id, or model results.",
            "",
        ]
    )
    return "\n".join(lines)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
