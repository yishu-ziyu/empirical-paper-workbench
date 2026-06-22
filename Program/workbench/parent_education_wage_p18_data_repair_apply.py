from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.parent_education_wage_p17_data_repair_preflight import (
    P12_PREFLIGHT_PATH,
    P17_JSON_PATH,
    SOURCE_SPECS,
    SUGGESTED_REPAIRED_DATASET_PATH,
    find_source_path,
    is_valid_education_value,
    read_source_rows,
)


TOPIC = "父母受教育水平对子女工资收入的影响"
SCHEMA_VERSION = "p18.parent_education_wage_data_repair_apply.v1"
P18_JSON_PATH = Path("Results/json/parent_education_wage_p18_data_repair_apply.json")
P18_REVIEW_PATH = Path("Reviews/parent_education_wage_p18_data_repair_apply.md")

DEFAULT_EDUCATION_YEARS_MAPPING = {
    "1": 0,
    "2": 6,
    "3": 9,
    "4": 12,
    "5": 15,
    "6": 16,
    "7": 19,
    "8": 22,
}


def run_parent_education_wage_p18_data_repair_apply(
    project_root: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], Path | None, Path | None]:
    project_root = project_root.resolve()
    result = build_parent_education_wage_p18_data_repair_apply(project_root, payload, apply=True)
    if result.get("status") != "data_repair_applied_ready_for_p13_p16":
        return result, None, None
    json_path = project_root / P18_JSON_PATH
    review_path = project_root / P18_REVIEW_PATH
    write_json(json_path, result)
    write_text(review_path, render_review(result))
    return result, json_path, review_path


def get_parent_education_wage_p18_data_repair_apply(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    path = project_root / P18_JSON_PATH
    if path.exists():
        payload = load_json(path)
        payload["artifact_exists"] = True
        return payload
    return build_parent_education_wage_p18_data_repair_apply(project_root, {}, apply=False)


def build_parent_education_wage_p18_data_repair_apply(
    project_root: Path,
    payload: dict[str, Any],
    apply: bool,
) -> dict[str, Any]:
    p17_path = project_root / P17_JSON_PATH
    if not p17_path.exists():
        return blocked_packet("blocked_missing_p17_data_repair_preflight", ["missing_p17_data_repair_preflight"])

    p17 = load_json(p17_path)
    validation_errors = validate_payload(payload) if apply else []
    if validation_errors:
        return blocked_packet("blocked_missing_human_apply_confirmation", validation_errors, p17)
    if not apply:
        return {
            **blocked_packet("p18_apply_gate_waiting_for_confirmation", [], p17),
            "artifact_exists": False,
            "can_apply_repair": True,
            "apply_endpoint_hint": "POST with reviewer, note, confirm_apply, confirm_education_years_mapping",
        }

    dataset_relative = Path(str((p17.get("current_dataset") or {}).get("path") or ""))
    source_root = Path(str(p17.get("source_root") or "")) if p17.get("source_root") else None
    source_id = str(payload.get("parent_education_source") or p17.get("recommended_parent_education_source") or "")
    output_relative = Path(str(payload.get("output_path") or p17.get("suggested_repaired_dataset_path") or SUGGESTED_REPAIRED_DATASET_PATH))
    dataset_path = project_root / dataset_relative
    output_path = project_root / output_relative

    safety_errors = validate_apply_paths(project_root, dataset_path, output_path)
    if safety_errors:
        return blocked_packet("blocked_unsafe_repaired_dataset_path", safety_errors, p17)
    if not dataset_path.exists():
        return blocked_packet("blocked_missing_current_dataset", ["missing_current_dataset"], p17)

    source_spec = find_source_spec(source_id)
    if source_spec is None:
        return blocked_packet("blocked_unknown_parent_education_source", ["unknown_parent_education_source"], p17)
    if source_root is None or not source_root.exists():
        return blocked_packet("blocked_missing_cfps_source_root", ["missing_cfps_source_root"], p17)

    rows, fieldnames = read_target_dataset(dataset_path)
    parent_lookup, source_profiles = build_parent_lookup(project_root, source_root, source_spec)
    mapping = normalized_mapping(payload.get("education_years_mapping") or DEFAULT_EDUCATION_YEARS_MAPPING)
    repaired_rows = []
    parent_nonmissing = 0
    experience_nonmissing = 0
    for row in rows:
        repaired = dict(row)
        pid = str(row.get("pid", "")).strip()
        year = str(row.get("year", "")).strip()
        parent_value = parent_lookup.get((year, pid))
        education_years = map_education_years(row.get("edu_last"), mapping)
        experience = compute_experience(row.get("age"), education_years)
        repaired["parent_education"] = format_number(parent_value)
        repaired["education_years"] = format_number(education_years)
        repaired["experience"] = format_number(experience)
        repaired["parent_education_source_id"] = source_id
        repaired["data_repair_stage"] = "P18"
        parent_nonmissing += 1 if parent_value is not None else 0
        experience_nonmissing += 1 if experience is not None else 0
        repaired_rows.append(repaired)

    output_fieldnames = extend_fieldnames(
        fieldnames,
        ["parent_education", "education_years", "experience", "parent_education_source_id", "data_repair_stage"],
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(repaired_rows)

    update_p12_dataset_path(project_root, output_relative, dataset_relative)

    result = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "topic": TOPIC,
        "stage": "P18",
        "status": "data_repair_applied_ready_for_p13_p16",
        "artifact_exists": True,
        "reviewer": str(payload.get("reviewer") or "").strip(),
        "note": str(payload.get("note") or "").strip(),
        "source_p17_json": P17_JSON_PATH.as_posix(),
        "input_dataset_path": dataset_relative.as_posix(),
        "repaired_dataset_path": output_relative.as_posix(),
        "parent_education_source": source_id,
        "source_profiles": source_profiles,
        "row_count": len(repaired_rows),
        "parent_education_nonmissing": parent_nonmissing,
        "experience_nonmissing": experience_nonmissing,
        "education_years_mapping": mapping,
        "updated_p12_dataset_path": True,
        "can_modify_final_dataset": False,
        "can_create_run_id": False,
        "can_execute_model": False,
        "can_run_p13_p16": True,
        "next_action": "rerun_p13_p16_with_repaired_dataset",
        "outputs": {
            "json": P18_JSON_PATH.as_posix(),
            "review": P18_REVIEW_PATH.as_posix(),
            "repaired_dataset": output_relative.as_posix(),
        },
    }
    return result


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors = []
    if not str(payload.get("reviewer") or "").strip():
        errors.append("missing_reviewer")
    if not str(payload.get("note") or "").strip():
        errors.append("missing_note")
    if payload.get("confirm_apply") is not True:
        errors.append("missing_confirm_apply")
    if payload.get("confirm_education_years_mapping") is not True:
        errors.append("missing_confirm_education_years_mapping")
    return errors


def validate_apply_paths(project_root: Path, dataset_path: Path, output_path: Path) -> list[str]:
    errors = []
    try:
        dataset_resolved = dataset_path.resolve()
        output_resolved = output_path.resolve()
        project_resolved = project_root.resolve()
    except FileNotFoundError:
        dataset_resolved = dataset_path.absolute()
        output_resolved = output_path.absolute()
        project_resolved = project_root.resolve()
    if output_resolved == dataset_resolved:
        errors.append("output_path_matches_input_dataset")
    if project_resolved not in output_resolved.parents:
        errors.append("output_path_outside_project")
    try:
        relative_output = output_resolved.relative_to(project_resolved)
    except ValueError:
        relative_output = Path("..")
    if relative_output.parts[:2] == ("Data", "Final"):
        errors.append("output_path_must_not_be_data_final")
    return errors


def read_target_dataset(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = [str(item) for item in (reader.fieldnames or [])]
        return list(reader), fieldnames


def build_parent_lookup(
    project_root: Path,
    source_root: Path,
    source_spec: dict[str, Any],
) -> tuple[dict[tuple[str, str], float], list[dict[str, Any]]]:
    lookup: dict[tuple[str, str], float] = {}
    profiles = []
    for year, year_spec in source_spec["years"].items():
        father_field = year_spec["father_field"]
        mother_field = year_spec["mother_field"]
        source_path = find_source_path(source_root, year_spec["relative_path"])
        rows = read_source_rows(source_path, ["pid", father_field, mother_field]) if source_path else []
        constructed = 0
        for row in rows:
            pid = str(row.get("pid", "")).strip()
            if not pid:
                continue
            values = []
            for field in (father_field, mother_field):
                value = row.get(field)
                if is_valid_education_value(value):
                    values.append(float(str(value).strip()))
            if not values:
                continue
            lookup[(str(year), pid)] = max(values)
            constructed += 1
        source_display = ""
        if source_path:
            try:
                source_display = source_path.relative_to(project_root).as_posix()
            except ValueError:
                source_display = str(source_path)
        profiles.append(
            {
                "year": str(year),
                "source_path": source_display,
                "source_exists": bool(source_path and source_path.exists()),
                "source_rows": len(rows),
                "constructable_source_rows": constructed,
                "father_field": father_field,
                "mother_field": mother_field,
            }
        )
    return lookup, profiles


def find_source_spec(source_id: str) -> dict[str, Any] | None:
    for spec in SOURCE_SPECS:
        if spec["id"] == source_id:
            return spec
    return None


def normalized_mapping(mapping: dict[str, Any]) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key, value in mapping.items():
        try:
            normalized[str(int(float(str(key).strip())))] = int(float(str(value).strip()))
        except (TypeError, ValueError):
            continue
    return normalized


def map_education_years(value: Any, mapping: dict[str, int]) -> float | None:
    try:
        key = str(int(float(str(value).strip())))
    except (TypeError, ValueError):
        return None
    mapped = mapping.get(key)
    return float(mapped) if mapped is not None else None


def compute_experience(age_value: Any, education_years: float | None) -> float | None:
    if education_years is None:
        return None
    try:
        age = float(str(age_value).strip())
    except (TypeError, ValueError):
        return None
    return max(age - education_years - 6, 0)


def format_number(value: float | None) -> str:
    if value is None:
        return ""
    if abs(value - int(value)) < 1e-9:
        return str(int(value))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def extend_fieldnames(existing: list[str], additions: list[str]) -> list[str]:
    fieldnames = list(existing)
    for item in additions:
        if item not in fieldnames:
            fieldnames.append(item)
    return fieldnames


def update_p12_dataset_path(project_root: Path, repaired_dataset_path: Path, original_dataset_path: Path) -> None:
    p12_path = project_root / P12_PREFLIGHT_PATH
    if not p12_path.exists():
        return
    p12 = load_json(p12_path)
    draft = p12.setdefault("draft_design_spec", {})
    audit = p12.setdefault("data_repair_audit", [])
    audit.append(
        {
            "stage": "P18",
            "updated_at": now(),
            "from_dataset_path": original_dataset_path.as_posix(),
            "to_dataset_path": repaired_dataset_path.as_posix(),
        }
    )
    draft["dataset_path"] = repaired_dataset_path.as_posix()
    write_json(p12_path, p12)


def blocked_packet(status: str, blocking_reasons: list[str], p17: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "topic": TOPIC,
        "stage": "P18",
        "status": status,
        "artifact_exists": False,
        "source_p17_json": P17_JSON_PATH.as_posix(),
        "suggested_repaired_dataset_path": (
            str((p17 or {}).get("suggested_repaired_dataset_path") or SUGGESTED_REPAIRED_DATASET_PATH.as_posix())
        ),
        "blocking_reasons": blocking_reasons,
        "can_modify_final_dataset": False,
        "can_create_run_id": False,
        "can_execute_model": False,
        "can_run_p13_p16": False,
        "next_action": "run_or_review_p17_before_p18_apply",
    }


def render_review(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# P18 Data Repair Apply Gate",
            "",
            f"- Status: {result.get('status')}",
            f"- Reviewer: {result.get('reviewer')}",
            f"- Input dataset: `{result.get('input_dataset_path')}`",
            f"- Repaired dataset: `{result.get('repaired_dataset_path')}`",
            f"- Rows: {result.get('row_count')}",
            f"- parent_education nonmissing: {result.get('parent_education_nonmissing')}",
            f"- experience nonmissing: {result.get('experience_nonmissing')}",
            f"- Can modify final dataset: `{result.get('can_modify_final_dataset')}`",
            f"- Can run P13-P16: `{result.get('can_run_p13_p16')}`",
            "",
            "结论：P18 只写 Data/Interim 修复数据，并把 P12 预检改指向修复数据；不覆盖 Data/Final。",
            "",
        ]
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()

