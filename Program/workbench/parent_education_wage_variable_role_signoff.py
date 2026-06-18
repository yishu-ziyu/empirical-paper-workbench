from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.variable_role_service import load_variable_role_draft_state, write_variable_role_draft_state
from Program.workbench.parent_education_wage_variable_role_preflight import (
    DEFAULT_PREFLIGHT_PATH,
    TOPIC,
    TOPIC_SLUG,
)


SCHEMA_VERSION = "p6.parent_education_wage_variable_role_signoff.v1"
DEFAULT_SIGNOFF_PATH = Path("Results/json/parent_education_wage_p6_variable_role_signoff.json")
DEFAULT_REVIEW_PATH = Path("Reviews/parent_education_wage_p6_variable_role_signoff.md")
FORMAL_VARIABLE_ROLES_PATH = Path("state/product/variable_roles.json")
VARIABLE_ROLE_DRAFTS_PATH = Path("state/product/variable_roles_drafts.json")


def run_parent_education_wage_variable_role_signoff(project_root: Path) -> tuple[dict[str, Any], Path, Path]:
    signoff = build_parent_education_wage_variable_role_signoff(project_root)
    json_path, review_path = write_parent_education_wage_variable_role_signoff(project_root, signoff)
    return signoff, json_path, review_path


def build_parent_education_wage_variable_role_signoff(project_root: Path) -> dict[str, Any]:
    preflight = load_json(project_root / DEFAULT_PREFLIGHT_PATH)
    required = list(preflight.get("human_review_required") or default_required_decisions())
    source_status = preflight.get("status") or "p5_variable_role_preflight_missing"
    status = "variable_role_signoff_required" if source_status == "variable_role_preflight_ready_for_review" else "blocked_missing_ready_p5_preflight"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "status": status,
        "source_preflight": {
            "path": DEFAULT_PREFLIGHT_PATH.as_posix(),
            "exists": bool(preflight),
            "status": source_status,
        },
        "required_decisions": required,
        "decision_prompts": decision_prompts(required),
        "recommended_decisions": recommended_decisions(preflight, required),
        "promotion_targets": [
            {
                "id": "editable_draft",
                "label": "可编辑变量角色草稿",
                "writes": VARIABLE_ROLE_DRAFTS_PATH.as_posix(),
                "requires_complete_signoff": True,
                "allowed_now": source_status == "variable_role_preflight_ready_for_review",
            },
            {
                "id": "formal_variable_roles",
                "label": "正式 VariableRoleSet",
                "writes": FORMAL_VARIABLE_ROLES_PATH.as_posix(),
                "requires_complete_signoff": True,
                "requires_explicit_formal_authorization": True,
                "allowed_now": False,
            },
        ],
        "draft_preview": build_draft_preview(preflight),
        "can_write_editable_draft": source_status == "variable_role_preflight_ready_for_review",
        "can_write_formal_variable_roles": False,
        "formal_state": {
            "variable_roles": {
                "path": FORMAL_VARIABLE_ROLES_PATH.as_posix(),
                "exists": (project_root / FORMAL_VARIABLE_ROLES_PATH).exists(),
                "modified": False,
            }
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
            "phase": "P6",
            "label": "人工签收",
            "status": status,
            "next_action": "collect_human_variable_role_signoff",
        },
        "outputs": {
            "json": DEFAULT_SIGNOFF_PATH.as_posix(),
            "review": DEFAULT_REVIEW_PATH.as_posix(),
        },
    }


def promote_parent_education_wage_variable_role_signoff(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    signoff = build_parent_education_wage_variable_role_signoff(project_root)
    preflight = load_json(project_root / DEFAULT_PREFLIGHT_PATH)
    required = signoff["required_decisions"]
    decisions = payload.get("decisions") if isinstance(payload.get("decisions"), dict) else {}
    missing = [item for item in required if not str(decisions.get(item, "")).strip()]
    target = payload.get("promotion_target") or "editable_draft"

    if signoff["status"] != "variable_role_signoff_required":
        return blocked_result(signoff, "blocked_missing_ready_p5_preflight", missing)
    if missing:
        return blocked_result(signoff, "variable_role_signoff_incomplete", missing)
    if target == "formal_variable_roles":
        result = blocked_result(signoff, "formal_variable_roles_write_blocked", [])
        result["blocking_reasons"] = ["formal_write_requires_separate_explicit_authorization"]
        return result
    if target != "editable_draft":
        result = blocked_result(signoff, "invalid_variable_role_promotion_target", [])
        result["blocking_reasons"] = [f"unsupported_promotion_target:{target}"]
        return result

    draft = build_variable_role_set_draft(preflight, decisions, str(payload.get("note", "")))
    state = load_variable_role_draft_state(project_root)
    state.setdefault("drafts", {})[draft["id"]] = draft
    state["latest_draft_id"] = draft["id"]
    state["pending_variable_roles_draft"] = draft
    state["updated_at"] = draft["updated_at"]
    write_variable_role_draft_state(project_root, state)

    result = {
        **signoff,
        "status": "variable_role_draft_promoted_for_editing",
        "promotion_target": "editable_draft",
        "missing_decisions": [],
        "decisions": decisions,
        "variable_role_set_draft": draft,
    }
    result["boundary_flags"] = {**result["boundary_flags"], "modified_variable_roles_draft": True}
    result["product_control_signal"] = {
        **result["product_control_signal"],
        "status": result["status"],
        "next_action": "edit_and_review_variable_role_draft",
    }
    write_parent_education_wage_variable_role_signoff(project_root, result)
    return result


def build_variable_role_set_draft(preflight: dict[str, Any], decisions: dict[str, Any], note: str) -> dict[str, Any]:
    timestamp = utc_now()
    safe_timestamp = "".join(character for character in timestamp if character.isalnum())
    draft_roles = preflight.get("draft_variable_roles", {})
    roles = {
        "outcome": as_role_list(draft_roles.get("outcome", {}).get("preferred")),
        "treatment": as_role_list(draft_roles.get("treatment", {}).get("preferred")),
        "controls": as_role_list(draft_roles.get("controls", {}).get("preferred", [])),
        "instruments": [],
        "fixed_effects": [],
        "cluster_by": [],
        "unit_id": [],
        "time_variable": [],
        "entity_id": [],
        "panel_time": [],
        "treatment_timing": [],
        "running_variable": [],
    }
    return {
        "id": f"variable_roles_draft_parent_education_wage_p6_{safe_timestamp}",
        "status": "draft",
        "evidence_level": "local_file",
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "source_preflight_path": DEFAULT_PREFLIGHT_PATH.as_posix(),
        "source_signoff_path": DEFAULT_SIGNOFF_PATH.as_posix(),
        "roles": roles,
        "operationalization": {
            "parent_education": draft_roles.get("treatment", {}).get("construction", {}),
            "moderators": draft_roles.get("moderators", {}),
            "role_bindings": preflight.get("role_bindings", []),
        },
        "decisions": decisions,
        "write_boundary": "draft_only_until_formal_variable_role_approval",
        "created_at": timestamp,
        "updated_at": timestamp,
        "decision_events": [
            {
                "actor": "user",
                "action": "promote_p5_preflight_to_editable_variable_role_draft",
                "timestamp": timestamp,
                "note": note,
            }
        ],
    }


def parent_education_wage_p6_gate_applies(project_root: Path) -> bool:
    preflight = load_json(project_root / DEFAULT_PREFLIGHT_PATH)
    signoff = load_json(project_root / DEFAULT_SIGNOFF_PATH)
    return preflight.get("schema_version") == "p5.parent_education_wage_variable_role_preflight.v1" or signoff.get("schema_version") == SCHEMA_VERSION


def has_parent_education_wage_p6_promoted_draft(project_root: Path) -> bool:
    state = load_variable_role_draft_state(project_root)
    drafts = state.get("drafts", {})
    if isinstance(drafts, dict):
        for draft in drafts.values():
            if is_parent_education_wage_p6_draft(draft):
                return True
    return is_parent_education_wage_p6_draft(state.get("pending_variable_roles_draft"))


def is_parent_education_wage_p6_draft(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("status") in {"draft", "applied_to_variable_roles"}
        and value.get("source_signoff_path") == DEFAULT_SIGNOFF_PATH.as_posix()
        and value.get("source_preflight_path") == DEFAULT_PREFLIGHT_PATH.as_posix()
    )


def blocked_result(signoff: dict[str, Any], status: str, missing: list[str]) -> dict[str, Any]:
    result = {
        **signoff,
        "status": status,
        "missing_decisions": missing,
        "can_write_editable_draft": False,
        "can_write_formal_variable_roles": False,
    }
    result["boundary_flags"] = {**result["boundary_flags"], "modified_variable_roles_draft": False}
    result["product_control_signal"] = {
        **result["product_control_signal"],
        "status": status,
        "next_action": "complete_human_variable_role_signoff",
    }
    return result


def build_draft_preview(preflight: dict[str, Any]) -> dict[str, Any]:
    draft_roles = preflight.get("draft_variable_roles", {})
    return {
        "outcome": draft_roles.get("outcome", {}).get("preferred"),
        "treatment": draft_roles.get("treatment", {}).get("preferred"),
        "parent_education_construction": draft_roles.get("treatment", {}).get("construction", {}).get("recommended_default"),
        "controls": draft_roles.get("controls", {}).get("preferred", []),
        "formal_write": False,
    }


def decision_prompts(required: list[str]) -> list[dict[str, str]]:
    labels = {
        "confirm_preferred_cfps_wave": "确认使用当前 P4 推荐的 CFPS 字段来源",
        "confirm_parent_education_construction": "确认父母教育合成口径",
        "confirm_hukou_role": "确认 hukou 作为控制、异质性或候选保留",
        "confirm_outcome_and_controls": "确认 outcome 和 controls",
        "approve_before_formal_variable_roles_write": "确认本次只进入草稿，正式写回需另行批准",
    }
    return [{"id": item, "label": labels.get(item, item), "required": "true"} for item in required]


def recommended_decisions(preflight: dict[str, Any], required: list[str]) -> dict[str, str]:
    preview = build_draft_preview(preflight)
    defaults = {
        "confirm_preferred_cfps_wave": "confirmed_current_p4_sources",
        "confirm_parent_education_construction": str(
            preview.get("parent_education_construction") or "max(father_education, mother_education)"
        ),
        "confirm_hukou_role": "control_or_heterogeneity_candidate",
        "confirm_outcome_and_controls": "ln_wage_with_age_female_urban_edu_last_experience",
        "approve_before_formal_variable_roles_write": "draft_only_no_formal_write",
    }
    return {item: defaults[item] for item in required if item in defaults}


def default_required_decisions() -> list[str]:
    return [
        "confirm_preferred_cfps_wave",
        "confirm_parent_education_construction",
        "confirm_hukou_role",
        "confirm_outcome_and_controls",
        "approve_before_formal_variable_roles_write",
    ]


def as_role_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def write_parent_education_wage_variable_role_signoff(
    project_root: Path,
    signoff: dict[str, Any],
    signoff_path: Path = DEFAULT_SIGNOFF_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_signoff_path = project_root / signoff_path
    absolute_review_path = project_root / review_path
    absolute_signoff_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_signoff_path.write_text(json.dumps(signoff, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review_path.write_text(render_review(signoff), encoding="utf-8")
    return absolute_signoff_path, absolute_review_path


def render_review(signoff: dict[str, Any]) -> str:
    preview = signoff.get("draft_preview", {})
    lines = [
        "# P6 人工签收与提升路径",
        "",
        f"- 题目：{signoff.get('topic', TOPIC)}",
        f"- 状态：`{signoff.get('status')}`",
        f"- outcome 草案：`{preview.get('outcome') or '待确认'}`",
        f"- treatment 草案：`{preview.get('treatment') or '待确认'}`",
        f"- 父母教育构造建议：`{preview.get('parent_education_construction') or '待确认'}`",
        f"- controls 草案：{', '.join(preview.get('controls') or []) or 'none'}",
        "- 可编辑 draft 写入：完整签收后可以",
        "- 正式 VariableRoleSet 写回：否",
        "- 执行回归：否",
        "",
        "## 待人工签收项",
    ]
    lines.extend(f"- `{item}`" for item in signoff.get("required_decisions", []))
    if signoff.get("recommended_decisions"):
        lines.extend(["", "## 页面推荐默认值"])
        lines.extend(f"- `{key}`：`{value}`" for key, value in signoff["recommended_decisions"].items())
    if signoff.get("missing_decisions"):
        lines.extend(["", "## 缺少签收项"])
        lines.extend(f"- `{item}`" for item in signoff["missing_decisions"])
    if signoff.get("variable_role_set_draft"):
        draft = signoff["variable_role_set_draft"]
        lines.extend(["", "## 已生成草稿", f"- draft id：`{draft['id']}`", f"- 写入边界：`{draft['write_boundary']}`"])
    lines.append("")
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}
