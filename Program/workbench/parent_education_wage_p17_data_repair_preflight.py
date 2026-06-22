from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOPIC = "父母受教育水平对子女工资收入的影响"
SCHEMA_VERSION = "p17.parent_education_wage_data_repair_preflight.v1"

P12_PREFLIGHT_PATH = Path("Results/json/parent_education_wage_p12_design_spec_preflight.json")
P13_JSON_PATH = Path("Results/json/parent_education_wage_p13_run_plan_approval.json")
P16_JSON_PATH = Path("Results/json/parent_education_wage_p16_user_acceptance_packet.json")
P17_JSON_PATH = Path("Results/json/parent_education_wage_p17_data_repair_preflight.json")
P17_REVIEW_PATH = Path("Reviews/parent_education_wage_p17_data_repair_preflight.md")
DEFAULT_DATASET_PATH = Path("Data/Final/cfps_robot_reallocation.csv")
SUGGESTED_REPAIRED_DATASET_PATH = Path("Data/Interim/parent_education_wage_repaired.csv")

DEFAULT_SOURCE_ROOTS = [
    Path("Data/Raw/cfps_source"),
    Path("/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A001CFPS中国家庭追踪调查"),
]

SOURCE_SPECS = [
    {
        "id": "famconf_parent_highest_education",
        "label": "CFPS family config parent education",
        "recommended_priority": 1,
        "years": {
            "2020": {
                "relative_path": "2020cfps/STATA版本/cfps2020famconf_202301.dta",
                "father_field": "tb4_a20_f",
                "mother_field": "tb4_a20_m",
            },
            "2022": {
                "relative_path": "2022CFPS/cfps2022famconf_202410.dta",
                "father_field": "tb4_a22_f",
                "mother_field": "tb4_a22_m",
            },
        },
    },
    {
        "id": "person_age14_parent_education",
        "label": "CFPS person age-14 parent education",
        "recommended_priority": 2,
        "years": {
            "2020": {
                "relative_path": "2020cfps/STATA版本/cfps2020person_202112.dta",
                "father_field": "qv102",
                "mother_field": "qv202",
            },
            "2022": {
                "relative_path": "2022CFPS/cfps2022person_202410.dta",
                "father_field": "qv102",
                "mother_field": "qv202",
            },
        },
    },
]


def run_parent_education_wage_p17_data_repair_preflight(project_root: Path) -> tuple[dict[str, Any], Path, Path]:
    project_root = project_root.resolve()
    preflight = build_parent_education_wage_p17_data_repair_preflight(project_root, artifact_exists=True)
    json_path = project_root / P17_JSON_PATH
    review_path = project_root / P17_REVIEW_PATH
    write_json(json_path, preflight)
    write_text(review_path, render_review(preflight))
    return preflight, json_path, review_path


def get_parent_education_wage_p17_data_repair_preflight(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    path = project_root / P17_JSON_PATH
    if path.exists():
        payload = load_json(path)
        payload["artifact_exists"] = True
        return payload
    return build_parent_education_wage_p17_data_repair_preflight(project_root, artifact_exists=False)


def build_parent_education_wage_p17_data_repair_preflight(
    project_root: Path,
    artifact_exists: bool = False,
) -> dict[str, Any]:
    dataset_path = resolve_dataset_path(project_root)
    dataset_full_path = project_root / dataset_path
    current_dataset = profile_current_dataset(dataset_full_path, dataset_path)
    missing_fields = missing_required_fields(project_root, current_dataset["columns"])
    source_root = select_source_root(project_root)
    source_root_display = str(source_root) if source_root else None
    parent_candidates = build_parent_education_candidates(
        dataset_full_path,
        current_dataset,
        source_root,
        project_root,
    )
    recommended = recommended_parent_candidate(parent_candidates)
    experience_candidate = build_experience_candidate(current_dataset)
    blocking_reasons = []
    if "parent_education" not in missing_fields and "experience" not in missing_fields:
        blocking_reasons.append("p17_not_required_current_dataset_already_has_required_fields")
    if source_root is None:
        blocking_reasons.append("cfps_source_root_not_found")

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "topic": TOPIC,
        "status": "data_repair_preflight_ready_for_review",
        "stage": "P17",
        "artifact_exists": artifact_exists,
        "current_dataset": current_dataset,
        "missing_fields": missing_fields,
        "source_root": source_root_display,
        "parent_education_candidates": parent_candidates,
        "recommended_parent_education_source": recommended["id"] if recommended else None,
        "recommended_parent_education_construction": "max(valid father education, valid mother education)",
        "experience_candidate": experience_candidate,
        "suggested_repaired_dataset_path": SUGGESTED_REPAIRED_DATASET_PATH.as_posix(),
        "can_modify_final_dataset": False,
        "can_write_repaired_dataset": False,
        "can_create_run_id": False,
        "can_execute_model": False,
        "blocking_reasons": blocking_reasons,
        "next_action": "review_data_repair_preflight_before_p18_apply_gate",
        "product_control_signal": {
            "phase": "P17",
            "label": "Data Repair Preflight",
            "status": "review_parent_education_and_experience_candidates",
            "next_action": "review_data_repair_preflight_before_p18_apply_gate",
        },
        "outputs": {
            "json": P17_JSON_PATH.as_posix(),
            "review": P17_REVIEW_PATH.as_posix(),
        },
    }


def resolve_dataset_path(project_root: Path) -> Path:
    p13_path = project_root / P13_JSON_PATH
    if p13_path.exists():
        p13 = load_json(p13_path)
        dataset_path = p13.get("dataset_path")
        if dataset_path:
            return Path(str(dataset_path))
    p12_path = project_root / P12_PREFLIGHT_PATH
    if p12_path.exists():
        p12 = load_json(p12_path)
        dataset_path = ((p12.get("draft_design_spec") or {}).get("dataset_path"))
        if dataset_path:
            return Path(str(dataset_path))
    return DEFAULT_DATASET_PATH


def profile_current_dataset(dataset_full_path: Path, dataset_path: Path) -> dict[str, Any]:
    columns: list[str] = []
    row_count = 0
    year_counts: dict[str, int] = {}
    pid_count = 0
    pids: set[str] = set()
    age_nonmissing = 0
    edu_last_nonmissing = 0
    if dataset_full_path.exists():
        with dataset_full_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = [item.strip() for item in (reader.fieldnames or []) if item and item.strip()]
            for row in reader:
                row_count += 1
                year = str(row.get("year", "")).strip()
                if year:
                    year_counts[year] = year_counts.get(year, 0) + 1
                pid = str(row.get("pid", "")).strip()
                if pid:
                    pids.add(pid)
                if str(row.get("age", "")).strip():
                    age_nonmissing += 1
                if str(row.get("edu_last", "")).strip():
                    edu_last_nonmissing += 1
    pid_count = len(pids)
    return {
        "path": dataset_path.as_posix(),
        "exists": dataset_full_path.exists(),
        "columns": columns,
        "row_count": row_count,
        "year_counts": year_counts,
        "pid_count": pid_count,
        "age_nonmissing": age_nonmissing,
        "edu_last_nonmissing": edu_last_nonmissing,
    }


def missing_required_fields(project_root: Path, dataset_columns: list[str]) -> list[str]:
    p13_path = project_root / P13_JSON_PATH
    if p13_path.exists():
        p13 = load_json(p13_path)
        missing = [str(item) for item in p13.get("missing_dataset_columns", [])]
        if missing:
            return missing
    required = ["ln_wage", "parent_education", "age", "female", "urban", "edu_last", "experience"]
    return [field for field in required if field not in dataset_columns]


def select_source_root(project_root: Path) -> Path | None:
    for root in DEFAULT_SOURCE_ROOTS:
        candidate = project_root / root if not root.is_absolute() else root
        if candidate.exists():
            return candidate
    return None


def build_parent_education_candidates(
    dataset_full_path: Path,
    current_dataset: dict[str, Any],
    source_root: Path | None,
    project_root: Path,
) -> list[dict[str, Any]]:
    target_rows = read_target_rows(dataset_full_path)
    candidates = []
    for spec in SOURCE_SPECS:
        year_profiles = []
        constructable_total = 0
        target_total = 0
        for year, year_spec in spec["years"].items():
            target_for_year = [row for row in target_rows if str(row.get("year", "")).strip() == year]
            profile = profile_source_year(source_root, project_root, year, year_spec, target_for_year)
            year_profiles.append(profile)
            constructable_total += int(profile["parent_constructable_rows"])
            target_total += int(profile["target_rows"])
        rate = round(constructable_total / target_total, 4) if target_total else 0.0
        candidates.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "status": "candidate_found" if constructable_total else "candidate_missing_or_zero_coverage",
                "recommended_priority": spec["recommended_priority"],
                "construction": "parent_education = max(valid father education, valid mother education)",
                "target_rows": target_total,
                "parent_constructable_rows": constructable_total,
                "parent_constructable_rate": rate,
                "year_profiles": year_profiles,
            }
        )
    return candidates


def profile_source_year(
    source_root: Path | None,
    project_root: Path,
    year: str,
    year_spec: dict[str, str],
    target_rows: list[dict[str, str]],
) -> dict[str, Any]:
    father_field = year_spec["father_field"]
    mother_field = year_spec["mother_field"]
    source_path = find_source_path(source_root, year_spec["relative_path"]) if source_root else None
    source_rows = read_source_rows(source_path, ["pid", father_field, mother_field]) if source_path else []
    source_by_pid = {str(row.get("pid", "")).strip(): row for row in source_rows if str(row.get("pid", "")).strip()}
    matched = 0
    father_valid = 0
    mother_valid = 0
    constructable = 0
    for row in target_rows:
        pid = str(row.get("pid", "")).strip()
        source = source_by_pid.get(pid)
        if not source:
            continue
        matched += 1
        father_ok = is_valid_education_value(source.get(father_field))
        mother_ok = is_valid_education_value(source.get(mother_field))
        father_valid += 1 if father_ok else 0
        mother_valid += 1 if mother_ok else 0
        constructable += 1 if father_ok or mother_ok else 0
    relative_source = ""
    if source_path:
        try:
            relative_source = source_path.relative_to(project_root).as_posix()
        except ValueError:
            relative_source = str(source_path)
    return {
        "year": year,
        "source_path": relative_source,
        "source_exists": bool(source_path and source_path.exists()),
        "father_field": father_field,
        "mother_field": mother_field,
        "target_rows": len(target_rows),
        "source_rows": len(source_rows),
        "matched_rows": matched,
        "father_valid_rows": father_valid,
        "mother_valid_rows": mother_valid,
        "parent_constructable_rows": constructable,
        "parent_constructable_rate": round(constructable / len(target_rows), 4) if target_rows else 0.0,
    }


def build_experience_candidate(current_dataset: dict[str, Any]) -> dict[str, Any]:
    columns = current_dataset["columns"]
    can_derive = "age" in columns and "edu_last" in columns
    row_count = int(current_dataset["row_count"])
    usable_rows = min(int(current_dataset["age_nonmissing"]), int(current_dataset["edu_last_nonmissing"]))
    return {
        "id": "experience_from_age_and_education_years",
        "status": "derivable_needs_review" if can_derive else "blocked_missing_age_or_edu_last",
        "formula": "experience = max(age - education_years - 6, 0)",
        "required_columns": ["age", "edu_last"],
        "available_columns": [column for column in ["age", "edu_last"] if column in columns],
        "requires_education_years_mapping": True,
        "can_apply_without_mapping": False,
        "target_rows": row_count,
        "candidate_usable_rows": usable_rows if can_derive else 0,
        "review_note": "edu_last 是学历等级，需要先确认 education_years 映射后才能写入修复数据。",
    }


def recommended_parent_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (-int(item["parent_constructable_rows"]), int(item["recommended_priority"])),
    )[0]


def read_target_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def find_source_path(source_root: Path | None, relative_path: str) -> Path | None:
    if source_root is None:
        return None
    path = source_root / relative_path
    if path.exists():
        return path
    csv_path = path.with_suffix(".csv")
    if csv_path.exists():
        return csv_path
    return path


def read_source_rows(path: Path | None, columns: list[str]) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return [{column: row.get(column) for column in columns} for row in csv.DictReader(handle)]
    if path.suffix.lower() == ".dta":
        try:
            import pandas as pd
        except ImportError:
            return []
        frame = pd.read_stata(path, columns=columns, convert_categoricals=False)
        return frame.to_dict(orient="records")
    return []


def is_valid_education_value(value: Any) -> bool:
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return False
    return number >= 0 and number != 79


def render_review(preflight: dict[str, Any]) -> str:
    parent_lines = []
    for candidate in preflight.get("parent_education_candidates", []):
        parent_lines.append(
            f"- {candidate['id']}: {candidate['parent_constructable_rows']}/"
            f"{candidate['target_rows']} rows ({candidate['parent_constructable_rate']})"
        )
    return "\n".join(
        [
            "# P17 Data Repair Preflight",
            "",
            f"- Status: {preflight['status']}",
            f"- Missing fields: {', '.join(preflight.get('missing_fields', [])) or 'none'}",
            f"- Recommended parent_education source: {preflight.get('recommended_parent_education_source') or 'none'}",
            f"- Experience candidate: {preflight.get('experience_candidate', {}).get('status')}",
            f"- Suggested repaired dataset: {preflight['suggested_repaired_dataset_path']}",
            f"- Can modify final dataset: {preflight['can_modify_final_dataset']}",
            f"- Can create run id: {preflight['can_create_run_id']}",
            f"- Can execute model: {preflight['can_execute_model']}",
            "",
            "## Parent Education Candidates",
            *parent_lines,
            "",
            "## Next Action",
            "",
            preflight["next_action"],
            "",
        ]
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
