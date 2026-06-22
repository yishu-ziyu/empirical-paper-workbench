from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.parent_education_wage_data_field_binding_ledger import discover_source_fields


SCHEMA_VERSION = "p2.parent_education_wage_execution_readiness.v1"
TOPIC = "父母受教育水平对子女工资收入的影响"
TOPIC_SLUG = "parent-education-wage"
DEFAULT_DATA_FIELD_LEDGER_PATH = Path("Results/json/parent_education_wage_data_field_binding_ledger.json")
DEFAULT_DESIGN_PATH = Path("Tasks/parent-education-wage/design.json")
DEFAULT_LEDGER_PATH = Path("Results/json/parent_education_wage_p2_execution_readiness.json")
DEFAULT_REVIEW_PATH = Path("Reviews/parent_education_wage_p2_execution_readiness.md")
FORMAL_VARIABLE_ROLES_PATH = Path("state/product/variable_roles.json")
FORMAL_DESIGN_SPEC_PATH = Path("state/product/design_spec.json")
FORMAL_RUN_PLAN_PATH = Path("state/product/run_plan.json")

OLD_TOPIC_TERMS = ("robot_exposure", "robot_density", "ln_robot", "bartik_iv")
TARGET_FIELDS = ("father_education", "mother_education", "parent_education", "hukou")

FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "father_education": (
        "father_education",
        "father edu",
        "father education",
        "faedu",
        "fed",
        "paedu",
        "父亲教育",
        "父亲受教育",
        "父亲学历",
        "父亲最高学历",
        "父亲受教育程度",
        "父亲文化程度",
    ),
    "mother_education": (
        "mother_education",
        "mother edu",
        "mother education",
        "maedu",
        "medu",
        "母亲教育",
        "母亲受教育",
        "母亲学历",
        "母亲最高学历",
        "母亲受教育程度",
        "母亲文化程度",
    ),
    "parent_education": (
        "parent_education",
        "parent education",
        "parents education",
        "父母教育",
        "父母受教育",
        "父母学历",
        "父母文化程度",
    ),
    "hukou": (
        "hukou",
        "urban_hukou",
        "户口",
        "户籍",
        "户口状况",
        "户口登记",
    ),
}


def run_parent_education_wage_execution_readiness(project_root: Path) -> tuple[dict[str, Any], Path, Path]:
    repair_parent_education_wage_design_draft(project_root)
    ledger = build_parent_education_wage_execution_readiness_ledger(project_root)
    json_path, review_path = write_parent_education_wage_execution_readiness_ledger(project_root, ledger)
    return ledger, json_path, review_path


def build_parent_education_wage_execution_readiness_ledger(project_root: Path) -> dict[str, Any]:
    data_field_ledger = load_json(project_root / DEFAULT_DATA_FIELD_LEDGER_PATH)
    design = load_json(project_root / DEFAULT_DESIGN_PATH)
    source_fields = discover_source_fields(project_root)
    missing_fields = normalize_missing_fields(data_field_ledger)
    field_supplementation = build_field_supplementation(missing_fields, source_fields)
    unresolved_parent_fields = [
        item["dataset_column"]
        for item in field_supplementation
        if item["dataset_column"] in {"father_education", "mother_education", "parent_education"}
        and item["supplement_status"] != "ready_for_human_binding"
    ]
    blocking_reasons: list[str] = []
    if unresolved_parent_fields:
        blocking_reasons.append("missing_parent_education_fields")
    if not variable_operationalization_ready(field_supplementation):
        blocking_reasons.append("human_variable_operationalization_required")
    if design_has_old_topic_terms(design):
        blocking_reasons.append("design_code_stub_topic_contamination")
    execution_preflight_allowed = not blocking_reasons
    status = "ready_for_execution_preflight_review" if execution_preflight_allowed else "blocked_missing_parent_education_fields"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "status": status,
        "execution_preflight_allowed": execution_preflight_allowed,
        "run_id": None,
        "blocking_reasons": blocking_reasons,
        "source_artifacts": {
            "data_field_binding_ledger": {
                "path": DEFAULT_DATA_FIELD_LEDGER_PATH.as_posix(),
                "status": data_field_ledger.get("status", ""),
            },
            "design_draft": {
                "path": DEFAULT_DESIGN_PATH.as_posix(),
                "old_topic_terms_present": design_has_old_topic_terms(design),
            },
            "formal_variable_roles": {"path": FORMAL_VARIABLE_ROLES_PATH.as_posix(), "read_only": True},
            "formal_design_spec": {"path": FORMAL_DESIGN_SPEC_PATH.as_posix(), "read_only": True},
            "formal_run_plan": {"path": FORMAL_RUN_PLAN_PATH.as_posix(), "read_only": True},
        },
        "field_supplementation": field_supplementation,
        "variable_operationalization_draft": build_variable_operationalization_draft(data_field_ledger, field_supplementation),
        "design_repair_status": {
            "old_topic_terms_present": design_has_old_topic_terms(design),
            "formal_design_spec_modified": False,
            "next_action": "repair_task_design_draft" if design_has_old_topic_terms(design) else "review_repaired_design_draft",
        },
        "method_execution_gate": {
            "allowed": execution_preflight_allowed,
            "blocked_methods": build_blocked_methods(design, blocking_reasons),
            "required_before_run": [
                "bind_parent_education_fields",
                "confirm_parent_education_construction",
                "approve_design_spec_draft",
                "approve_run_plan_draft",
            ],
        },
        "statspai_boundary": {
            "allowed_after": "analysis_ready_dataframe",
            "forbidden_calls": ["sp.paper"],
            "current_stage_call_statspai": False,
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
            "phase": "P2",
            "label": "执行准入",
            "status": status,
            "next_action": "bind_parent_education_fields_before_execution"
            if not execution_preflight_allowed
            else "human_review_execution_preflight",
        },
        "outputs": {
            "json": DEFAULT_LEDGER_PATH.as_posix(),
            "review": DEFAULT_REVIEW_PATH.as_posix(),
        },
    }


def repair_parent_education_wage_design_draft(project_root: Path) -> dict[str, Any]:
    path = project_root / DEFAULT_DESIGN_PATH
    design = load_json(path)
    before = json.dumps(design, ensure_ascii=False)
    if not design:
        return {
            "repaired": False,
            "reason": "design_draft_missing",
            "modified_formal_design_spec": False,
        }
    design["code_stub"] = repaired_code_stub()
    for candidate in design.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        rationale = str(candidate.get("rationale", ""))
        candidate["rationale"] = rationale.replace("（含 ISEI、行业机器人渗透率、城乡/性别等）", "（含子女教育、年龄、性别、城乡和地区等）")
    design["generated_by"] = "p2-execution-readiness-repair"
    design["contamination_repair"] = {
        "repaired_at": datetime.now(timezone.utc).isoformat(),
        "removed_old_topic_term_count": sum(1 for term in OLD_TOPIC_TERMS if term in before),
        "modified_formal_design_spec": False,
        "note": "Only the task-level design draft was repaired; formal state/product/design_spec.json was not modified.",
    }
    after = json.dumps(design, ensure_ascii=False)
    repaired = before != after
    if repaired:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(design, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "repaired": repaired,
        "removed_terms": [term for term in OLD_TOPIC_TERMS if term in before],
        "path": DEFAULT_DESIGN_PATH.as_posix(),
        "modified_formal_design_spec": False,
    }


def repaired_code_stub() -> str:
    return "\n".join(
        [
            "# P2 execution-preflight sketch only; do not run before fields are bound.",
            'required = ["ln_wage", "father_education", "mother_education", "hukou", "age", "female", "urban", "edu_last"]',
            "missing = [name for name in required if name not in df.columns]",
            "if missing:",
            '    raise ValueError(f"Missing execution fields: {missing}")',
            'df["parent_education"] = df[["father_education", "mother_education"]].max(axis=1)',
            'formula = "ln_wage ~ parent_education + age + female + urban + edu_last"',
            "# Next stage: approve VariableRoleSet draft, DesignSpec draft, and RunPlan draft before estimation.",
        ]
    )


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def normalize_missing_fields(data_field_ledger: dict[str, Any]) -> list[dict[str, Any]]:
    missing = data_field_ledger.get("missing_fields") if isinstance(data_field_ledger.get("missing_fields"), list) else []
    known = {str(item.get("dataset_column")): item for item in missing if isinstance(item, dict) and item.get("dataset_column")}
    for field in TARGET_FIELDS:
        known.setdefault(field, {"dataset_column": field})
    return [known[field] for field in TARGET_FIELDS]


def build_field_supplementation(missing_fields: list[dict[str, Any]], source_fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = []
    for field in missing_fields:
        dataset_column = str(field.get("dataset_column", ""))
        candidates = find_field_candidates(dataset_column, source_fields)
        items.append(
            {
                "dataset_column": dataset_column,
                "semantic_label": field.get("semantic_label", ""),
                "supplement_status": "candidate_found" if candidates else "missing",
                "candidates": candidates[:10],
                "required_next_state": "human_bind_candidate_field" if candidates else "locate_source_field_or_adjust_research_scope",
                "can_write_formal_variable_roles": False,
            }
        )
    return items


def find_field_candidates(dataset_column: str, source_fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aliases = FIELD_ALIASES.get(dataset_column, (dataset_column,))
    candidates: list[dict[str, Any]] = []
    for field in source_fields:
        name = str(field.get("name", ""))
        label = str(field.get("label", ""))
        haystack = f"{name} {label}".lower()
        matched_alias = next((alias for alias in aliases if alias.lower() in haystack), "")
        if not matched_alias:
            continue
        candidates.append(
            {
                "name": name,
                "label": label,
                "source_path": field.get("source_path", ""),
                "source_type": field.get("source_type", ""),
                "evidence_level": field.get("evidence_level", "local_file"),
                "match_reason": f"matched_alias:{matched_alias}",
            }
        )
    return candidates


def variable_operationalization_ready(field_supplementation: list[dict[str, Any]]) -> bool:
    by_field = {item["dataset_column"]: item for item in field_supplementation}
    return all(by_field.get(field, {}).get("supplement_status") == "ready_for_human_binding" for field in TARGET_FIELDS)


def build_variable_operationalization_draft(
    data_field_ledger: dict[str, Any],
    field_supplementation: list[dict[str, Any]],
) -> dict[str, Any]:
    matched_columns = {
        str(item.get("dataset_column"))
        for item in data_field_ledger.get("matched_fields", [])
        if isinstance(item, dict) and item.get("dataset_column")
    }
    return {
        "outcome": {
            "preferred": "ln_wage" if "ln_wage" in matched_columns else "wage",
            "alternatives": [field for field in ("ln_wage", "wage") if field in matched_columns],
            "decision_status": "draft_needs_human_review",
        },
        "treatment": {
            "preferred": "parent_education",
            "status": "blocked_missing_parent_education_fields",
            "source_fields": ["father_education", "mother_education"],
        },
        "parent_education_construction": {
            "draft_options": ["max(father_education, mother_education)", "mean(father_education, mother_education)", "separate father/mother coefficients"],
            "decision_status": "requires_human_confirmation",
        },
        "controls": [field for field in ("age", "female", "urban", "edu_last", "province") if field in matched_columns],
        "moderators": ["hukou"] if any(item["dataset_column"] == "hukou" for item in field_supplementation) else [],
        "can_write_formal_variable_roles": False,
    }


def build_blocked_methods(design: dict[str, Any], blocking_reasons: list[str]) -> list[dict[str, Any]]:
    candidates = design.get("candidates") if isinstance(design.get("candidates"), list) else []
    if not candidates:
        candidates = [{"method": design.get("recommended") or "method_to_be_reviewed"}]
    return [
        {
            "method": str(candidate.get("method", "method_to_be_reviewed")),
            "status": "blocked" if blocking_reasons else "ready_for_review",
            "blocking_reasons": blocking_reasons,
            "can_execute": not blocking_reasons,
        }
        for candidate in candidates
    ]


def design_has_old_topic_terms(design: dict[str, Any]) -> bool:
    body = json.dumps(design, ensure_ascii=False).lower()
    return any(term in body for term in OLD_TOPIC_TERMS)


def write_parent_education_wage_execution_readiness_ledger(
    project_root: Path,
    ledger: dict[str, Any],
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_ledger_path = project_root / ledger_path
    absolute_review_path = project_root / review_path
    absolute_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review_path.write_text(render_review(ledger), encoding="utf-8")
    return absolute_ledger_path, absolute_review_path


def render_review(ledger: dict[str, Any]) -> str:
    lines = [
        "# P2 执行准入账本",
        "",
        f"- 题目：{ledger['topic']}",
        f"- 状态：`{ledger['status']}`",
        f"- execution_preflight_allowed：{str(ledger['execution_preflight_allowed']).lower()}",
        "- run id：未创建" if not ledger["run_id"] else f"- run id：`{ledger['run_id']}`",
        "- 正式 VariableRoleSet 写回：否",
        "- 正式 DesignSpec 写回：否",
        "- 正式 RunPlan 写回：否",
        "",
        "## 阻塞原因",
    ]
    if ledger["blocking_reasons"]:
        lines.extend(f"- `{reason}`" for reason in ledger["blocking_reasons"])
    else:
        lines.append("- 无硬阻塞，等待人工审阅。")
    lines.extend(["", "## 字段补证"])
    for item in ledger["field_supplementation"]:
        candidates = ", ".join(candidate["name"] for candidate in item["candidates"]) or "none"
        lines.append(f"- `{item['dataset_column']}` | {item['supplement_status']} | candidates={candidates}")
    lines.extend(["", "## 变量口径 Draft"])
    draft = ledger["variable_operationalization_draft"]
    lines.append(f"- outcome: `{draft['outcome']['preferred']}`")
    lines.append(f"- treatment: `{draft['treatment']['preferred']}` | {draft['treatment']['status']}")
    lines.append(f"- parent education construction: {draft['parent_education_construction']['decision_status']}")
    lines.extend(["", "## 方法执行门"])
    for method in ledger["method_execution_gate"]["blocked_methods"]:
        lines.append(f"- `{method['method']}` | {method['status']} | reasons={', '.join(method['blocking_reasons']) or 'none'}")
    lines.append("")
    return "\n".join(lines)
