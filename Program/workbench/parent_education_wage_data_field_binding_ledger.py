from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p1b.parent_education_wage_data_field_binding_ledger.v1"
TOPIC = "父母受教育水平对子女工资收入的影响"
TOPIC_SLUG = "parent-education-wage"
DEFAULT_VARIABLES_PATH = Path("Tasks/parent-education-wage/variables.yaml")
DEFAULT_LEDGER_PATH = Path("Results/json/parent_education_wage_data_field_binding_ledger.json")
DEFAULT_REVIEW_PATH = Path("Reviews/parent_education_wage_data_field_binding_ledger.md")
FORMAL_VARIABLE_ROLES_PATH = Path("state/product/variable_roles.json")


def build_parent_education_wage_data_field_binding_ledger(project_root: Path) -> dict[str, Any]:
    variables_path = project_root / DEFAULT_VARIABLES_PATH
    variable_candidates = parse_variables_yaml(variables_path.read_text(encoding="utf-8") if variables_path.exists() else "")
    source_fields = discover_source_fields(project_root)
    field_bindings = [build_field_binding(candidate, source_fields) for candidate in variable_candidates]
    missing_parent_fields = [
        item["dataset_column"]
        for item in field_bindings
        if item["dataset_column"] in {"father_education", "mother_education", "parent_education"}
        and item["binding_status"] != "matched"
    ]
    blocking_reasons = []
    if missing_parent_fields:
        blocking_reasons.append("missing_parent_education_source_fields")
    if not variable_candidates:
        blocking_reasons.append("missing_variable_candidates")
    status = "blocked_missing_parent_education_fields" if missing_parent_fields else "needs_human_data_field_binding_review"
    if not variable_candidates:
        status = "blocked_missing_variable_candidates"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "status": status,
        "source_artifacts": {
            "variables_yaml": {
                "path": DEFAULT_VARIABLES_PATH.as_posix(),
                "exists": variables_path.exists(),
            },
            "formal_variable_roles": {
                "path": FORMAL_VARIABLE_ROLES_PATH.as_posix(),
                "exists": (project_root / FORMAL_VARIABLE_ROLES_PATH).exists(),
                "read_only": True,
            },
        },
        "candidate_variable_count": len(variable_candidates),
        "field_source_count": len(source_fields),
        "field_bindings": field_bindings,
        "matched_fields": [item for item in field_bindings if item["binding_status"] == "matched"],
        "missing_fields": [item for item in field_bindings if item["binding_status"] != "matched"],
        "blocking_reasons": blocking_reasons,
        "boundary_flags": {
            "modified_formal_variable_roles": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "wrote_state_product": False,
        },
        "promotion": {
            "allowed": False,
            "required_decision": "human_approve_parent_education_wage_data_field_binding",
            "would_write_if_approved": "state/product/variable_roles.json",
        },
        "review_gates": [
            "parent_education_source_fields_required",
            "wage_measurement_definition_review",
            "child_education_control_role_review",
            "sample_and_year_coverage_review",
        ],
        "product_control_signal": {
            "phase": "P1-B",
            "label": "变量字段绑定",
            "status": status,
            "next_action": "locate_parent_education_fields_or_adjust_variable_candidates",
        },
        "outputs": {
            "json": DEFAULT_LEDGER_PATH.as_posix(),
            "review": DEFAULT_REVIEW_PATH.as_posix(),
        },
    }


def parse_variables_yaml(text: str) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("- role:"):
            if current:
                candidates.append(current)
            current = {"role": stripped.split(":", 1)[1].strip()}
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key in {"dataset_column", "semantic_label", "description", "review_status"}:
            current[key] = value.strip()
    if current:
        candidates.append(current)
    return [item for item in candidates if item.get("dataset_column")]


def discover_source_fields(project_root: Path) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for csv_path in sorted((project_root / "Data" / "Final").glob("*.csv")):
        fields.extend(discover_csv_fields(project_root, csv_path))
    fields.extend(discover_variable_role_candidate_fields(project_root))
    return fields


def discover_csv_fields(project_root: Path, csv_path: Path) -> list[dict[str, Any]]:
    try:
        with csv_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            row_count = sum(1 for _ in reader)
    except UnicodeDecodeError:
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            row_count = sum(1 for _ in reader)
    relative_path = csv_path.relative_to(project_root).as_posix()
    return [
        {
            "name": name,
            "label": "",
            "source_path": relative_path,
            "source_type": "csv_header",
            "row_count": row_count,
            "evidence_level": "local_file",
        }
        for name in header
        if name
    ]


def discover_variable_role_candidate_fields(project_root: Path) -> list[dict[str, Any]]:
    path = project_root / "state" / "product" / "variable_role_candidates.json"
    if not path.exists():
        return []
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    fields: list[dict[str, Any]] = []
    for candidate in state.get("candidates", {}).values():
        source = candidate.get("source", {}) if isinstance(candidate, dict) else {}
        for option in candidate.get("field_options", []):
            if not isinstance(option, dict) or not option.get("name"):
                continue
            fields.append(
                {
                    "name": option.get("name"),
                    "label": option.get("label", ""),
                    "source_path": source.get("path", ""),
                    "source_type": "variable_role_candidate_field_options",
                    "row_count": candidate.get("quality_profile", {}).get("row_count"),
                    "evidence_level": candidate.get("evidence_level", "local_file"),
                }
            )
    return fields


def build_field_binding(candidate: dict[str, str], source_fields: list[dict[str, Any]]) -> dict[str, Any]:
    dataset_column = candidate.get("dataset_column", "")
    matches = [field for field in source_fields if field.get("name") == dataset_column]
    return {
        "role": candidate.get("role", ""),
        "dataset_column": dataset_column,
        "semantic_label": candidate.get("semantic_label", ""),
        "candidate_review_status": candidate.get("review_status", ""),
        "binding_status": "matched" if matches else "missing",
        "evidence_level": "local_file",
        "matched_sources": matches[:8],
        "required_next_state": "human_review" if matches else "locate_or_rename_source_field",
        "can_write_formal_variable_roles": False,
    }


def write_parent_education_wage_data_field_binding_ledger(
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
        "# P1-B 数据字段绑定账本",
        "",
        f"- 题目：{ledger['topic']}",
        f"- 状态：`{ledger['status']}`",
        f"- 候选变量数：{ledger['candidate_variable_count']}",
        f"- matched：{len(ledger['matched_fields'])}",
        f"- missing：{len(ledger['missing_fields'])}",
        "- 不写正式变量角色",
        "- 不写 DesignSpec / RunPlan",
        "",
        "## 阻塞原因",
    ]
    if ledger["blocking_reasons"]:
        for reason in ledger["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    else:
        lines.append("- 无硬阻塞，等待人工审阅。")
    lines.extend(["", "## 字段绑定"])
    for item in ledger["field_bindings"]:
        source = item["matched_sources"][0]["source_path"] if item["matched_sources"] else "missing"
        lines.append(
            f"- `{item['dataset_column']}` ({item['role']}) | {item['binding_status']} | {source} | {item['semantic_label']}"
        )
    lines.extend(["", "## 审阅门禁"])
    for gate in ledger["review_gates"]:
        lines.append(f"- `{gate}`")
    lines.append("")
    return "\n".join(lines)
