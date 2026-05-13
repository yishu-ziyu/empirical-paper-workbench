from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


DATASET_SUFFIXES = {".csv", ".dta", ".xlsx", ".xls", ".sav", ".parquet", ".feather"}
ROLE_KEYS = ("outcome", "treatment", "controls", "instruments", "fixed_effects", "cluster_by")


def variable_role_state_path(project_root: Path) -> Path:
    return project_root / "state" / "product" / "variable_roles.json"


def load_saved_variable_role_set(project_root: Path) -> dict[str, Any] | None:
    path = variable_role_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def has_approved_variable_role_set(project_root: Path) -> bool:
    saved = load_saved_variable_role_set(project_root)
    return bool(saved and saved.get("status") == "approved")


def get_project_variable_roles(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    role_set = load_saved_variable_role_set(project_root) or build_draft_variable_role_set(project_root)
    return {
        "_meta": {
            "evidence_level": role_set.get("evidence_level", "local_file"),
            "service": "variable_role_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "variable_role_set": role_set,
    }


def save_project_variable_roles(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    dataset_path: str,
    roles: dict[str, Any],
    note: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    dataset = resolve_dataset_path(project_root, dataset_path)
    existing = load_saved_variable_role_set(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    previous_events = existing.get("decision_events", []) if existing else []
    event = {
        "actor": "user",
        "action": "confirm_variable_roles",
        "timestamp": utc_now(),
        "note": note,
    }
    role_set = {
        "id": "variable_role_set",
        "version": version,
        "status": "approved",
        "evidence_level": "local_file",
        "dataset_path": dataset.relative_to(project_root).as_posix(),
        "dataset_name": dataset.name,
        "updated_at": event["timestamp"],
        "roles": normalize_roles(roles),
        "decision_events": [*previous_events, event],
    }
    path = variable_role_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(role_set, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "variable_role_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "variable_role_set": role_set,
    }


def build_draft_variable_role_set(project_root: Path) -> dict[str, Any]:
    dataset = select_dataset(project_root)
    columns = read_dataset_columns(dataset) if dataset else []
    return {
        "id": "variable_role_set",
        "version": 0,
        "status": "draft",
        "evidence_level": "local_file",
        "dataset_path": dataset.relative_to(project_root).as_posix() if dataset else None,
        "dataset_name": dataset.name if dataset else None,
        "updated_at": utc_now(),
        "columns": columns,
        "roles": infer_roles(columns),
        "decision_events": [],
    }


def select_dataset(project_root: Path) -> Path | None:
    configured = configured_dataset_path(project_root)
    if configured:
        candidate = resolve_dataset_path(project_root, configured)
        if candidate.exists():
            return candidate
    data_root = project_root / "Data"
    if not data_root.exists():
        return None
    return next(
        (
            path.resolve()
            for path in sorted(data_root.rglob("*"))
            if path.is_file() and path.suffix.lower() in DATASET_SUFFIXES
        ),
        None,
    )


def resolve_dataset_path(project_root: Path, dataset_path: str) -> Path:
    path = (project_root / dataset_path).resolve()
    path.relative_to(project_root)
    if not path.exists():
        raise FileNotFoundError(dataset_path)
    if not path.is_file() or path.suffix.lower() not in DATASET_SUFFIXES:
        raise ValueError(dataset_path)
    return path


def configured_dataset_path(project_root: Path) -> str | None:
    paper_path = project_root / "paper.yaml"
    if not paper_path.exists():
        return None
    payload = yaml.safe_load(paper_path.read_text(encoding="utf-8")) or {}
    configured = payload.get("data", {}).get("final_dataset")
    return str(configured).replace("\\", "/") if configured else None


def read_dataset_columns(path: Path) -> list[str]:
    if path.suffix.lower() != ".csv":
        return []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader, [])


def infer_roles(columns: list[str]) -> dict[str, list[str]]:
    outcome = first_matching(columns, {"wage", "income", "salary", "earnings", "outcome", "y"})
    treatment = first_matching(columns, {"trained", "treatment", "treated", "exposure", "robot", "x"})
    reserved = set(outcome + treatment)
    controls = [
        column
        for column in columns
        if column not in reserved and column.lower() not in {"id", "person_id", "year", "city", "province"}
    ]
    return {
        "outcome": outcome,
        "treatment": treatment,
        "controls": controls,
        "instruments": [],
        "fixed_effects": [],
        "cluster_by": [],
    }


def first_matching(columns: list[str], candidates: set[str]) -> list[str]:
    for column in columns:
        if column.lower() in candidates:
            return [column]
    return []


def normalize_roles(roles: dict[str, Any]) -> dict[str, list[str]]:
    return {key: normalize_role_list(roles.get(key, [])) for key in ROLE_KEYS}


def normalize_role_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
