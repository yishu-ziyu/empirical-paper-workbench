from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


DATASET_SUFFIXES = {".csv", ".dta", ".xlsx", ".xls", ".sav", ".parquet", ".feather"}
ROLE_KEYS = ("outcome", "treatment", "controls", "instruments", "fixed_effects", "cluster_by")
DATASET_IMPORT_PREFLIGHT_PATH = Path("state/product/dataset_import_preflights.json")
VARIABLE_ROLE_CANDIDATE_PATH = Path("state/product/variable_role_candidates.json")


class FieldProfileRequiredError(RuntimeError):
    pass


class InvalidVariableRoleCandidateActionError(RuntimeError):
    pass


class VariableRoleCandidateNotFoundError(KeyError):
    pass


class VariableRoleCandidateApprovalRequiredError(RuntimeError):
    pass


def variable_role_state_path(project_root: Path) -> Path:
    return project_root / "state" / "product" / "variable_roles.json"


def variable_role_candidate_state_path(project_root: Path) -> Path:
    return project_root / VARIABLE_ROLE_CANDIDATE_PATH


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
    candidate_id: str | None = None,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    candidate = load_approved_variable_role_candidate(project_root, candidate_id) if candidate_id else None
    dataset = None if candidate else resolve_dataset_path(project_root, dataset_path)
    existing = load_saved_variable_role_set(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    previous_events = existing.get("decision_events", []) if existing else []
    event = {
        "actor": "user",
        "action": "confirm_variable_roles_from_candidate" if candidate else "confirm_variable_roles",
        "timestamp": utc_now(),
        "note": note,
    }
    source = candidate.get("source", {}) if candidate else {}
    binding = candidate.get("binding", {}) if candidate else {}
    saved_dataset_path = dataset.relative_to(project_root).as_posix() if dataset else dataset_path
    dataset_name = dataset.name if dataset else source.get("name") or Path(dataset_path).name
    role_set = {
        "id": "variable_role_set",
        "version": version,
        "status": "approved",
        "evidence_level": "local_file",
        "dataset_path": saved_dataset_path,
        "dataset_name": dataset_name,
        "updated_at": event["timestamp"],
        "roles": normalize_roles(roles),
        "decision_events": [*previous_events, event],
    }
    if candidate:
        role_set.update(
            {
                "candidate_id": candidate["id"],
                "dataset_import_id": candidate.get("dataset_import_id"),
                "dataset_import_profile_id": candidate.get("dataset_import_profile_id"),
                "source": source,
                "binding": binding,
                "provenance": {
                    "candidate_state_path": VARIABLE_ROLE_CANDIDATE_PATH.as_posix(),
                    "dataset_import_manifest_path": DATASET_IMPORT_PREFLIGHT_PATH.as_posix(),
                    "field_profile_source": "dataset_import_profile.fields",
                },
            }
        )
    path = variable_role_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(role_set, ensure_ascii=False, indent=2), encoding="utf-8")
    if candidate:
        mark_variable_role_candidate_applied(project_root, candidate["id"], version, event)
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


def load_approved_variable_role_candidate(project_root: Path, candidate_id: str | None) -> dict[str, Any]:
    if not candidate_id:
        raise VariableRoleCandidateNotFoundError("")
    state = load_variable_role_candidate_state(project_root)
    candidate = state.get("candidates", {}).get(candidate_id)
    if not isinstance(candidate, dict):
        raise VariableRoleCandidateNotFoundError(candidate_id)
    if candidate.get("status") != "approved_candidate" or not candidate.get("can_apply_to_variable_roles"):
        raise VariableRoleCandidateApprovalRequiredError(candidate_id)
    return candidate


def mark_variable_role_candidate_applied(
    project_root: Path,
    candidate_id: str,
    variable_role_set_version: int,
    event: dict[str, Any],
) -> None:
    state = load_variable_role_candidate_state(project_root)
    candidate = state.get("candidates", {}).get(candidate_id)
    if not isinstance(candidate, dict):
        return
    candidate["status"] = "applied_to_variable_roles"
    candidate["can_apply_to_variable_roles"] = False
    candidate["applied_variable_role_set_version"] = variable_role_set_version
    candidate["updated_at"] = event["timestamp"]
    candidate.setdefault("review_events", []).append(
        {
            **event,
            "action": "apply_to_variable_role_set",
        }
    )
    state.setdefault("candidates", {})[candidate_id] = candidate
    state["latest_candidate_id"] = candidate_id
    state["updated_at"] = candidate["updated_at"]
    write_variable_role_candidate_state(project_root, state)


def get_project_variable_role_candidates(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    state = load_variable_role_candidate_state(project_root)
    latest_id = state.get("latest_candidate_id")
    latest = state.get("candidates", {}).get(latest_id) if latest_id else None
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "variable_role_candidate_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "variable_role_candidates": list(state.get("candidates", {}).values()),
        "latest_variable_role_candidate": latest,
    }


def generate_project_variable_role_candidate(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    dataset_import_id: str,
    note: str = "",
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    manifest = load_dataset_import_manifest(project_root)
    dataset_import = manifest.get("dataset_imports", {}).get(dataset_import_id)
    if not isinstance(dataset_import, dict):
        raise KeyError(dataset_import_id)

    profile_id = dataset_import.get("field_profile", {}).get("id")
    profile = manifest.get("dataset_import_profiles", {}).get(profile_id) if profile_id else None
    if not isinstance(profile, dict) or profile.get("status") != "profiled" or not profile.get("fields"):
        raise FieldProfileRequiredError(f"Dataset import {dataset_import_id} does not have a profiled field dictionary.")

    fields = profile.get("fields", [])
    candidate_roles = infer_roles_from_field_profile(fields)
    candidate_id = build_variable_role_candidate_id(dataset_import_id, profile.get("id", "profile"))
    event = {
        "actor": "system",
        "action": "generate_variable_role_candidate",
        "timestamp": utc_now(),
        "note": note,
    }
    candidate = {
        "id": candidate_id,
        "dataset_import_id": dataset_import_id,
        "dataset_import_profile_id": profile.get("id"),
        "status": "needs_review",
        "evidence_level": "local_file",
        "source": profile.get("source", {}),
        "binding": profile.get("binding", {}),
        "quality_profile": {
            "row_count": profile.get("quality_profile", {}).get("row_count"),
            "column_count": profile.get("quality_profile", {}).get("column_count"),
            "row_count_source": profile.get("quality_profile", {}).get("row_count_source"),
        },
        "candidate_roles": candidate_roles,
        "field_options": build_field_options(fields, candidate_roles),
        "checks": [
            {
                "id": "formal_writeback_boundary",
                "label": "不会写入正式变量角色集",
                "status": "passed",
                "detail": "该候选只进入字段审阅状态机；正式 VariableRoleSet 仍需用户在编辑器里手动保存。",
            },
            {
                "id": "field_profile_source",
                "label": "字段画像来自真实本地文件",
                "status": "passed",
                "detail": "候选基于 dataset_import_profile.fields、变量标签和 Stata 类型生成。",
            },
        ],
        "can_apply_to_variable_roles": False,
        "does_not_mutate_variable_role_set": True,
        "manifest_path": VARIABLE_ROLE_CANDIDATE_PATH.as_posix(),
        "created_at": event["timestamp"],
        "updated_at": event["timestamp"],
        "review_events": [event],
    }
    state = load_variable_role_candidate_state(project_root)
    state.setdefault("candidates", {})[candidate_id] = candidate
    state["latest_candidate_id"] = candidate_id
    state["updated_at"] = candidate["updated_at"]
    write_variable_role_candidate_state(project_root, state)
    return variable_role_candidate_response(project, candidate)


def review_project_variable_role_candidate(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    candidate_id: str,
    action: str,
    note: str = "",
    candidate_roles: dict[str, Any] | None = None,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    if action not in {"approve_candidate", "needs_revision", "reject"}:
        raise InvalidVariableRoleCandidateActionError(action)
    state = load_variable_role_candidate_state(project_root)
    candidate = state.get("candidates", {}).get(candidate_id)
    if not isinstance(candidate, dict):
        raise VariableRoleCandidateNotFoundError(candidate_id)

    if candidate_roles is not None:
        candidate["candidate_roles"] = normalize_roles(candidate_roles)
        candidate["field_options"] = build_field_options(
            candidate.get("field_options", []),
            candidate["candidate_roles"],
        )

    if action == "approve_candidate":
        candidate["status"] = "approved_candidate"
        candidate["can_apply_to_variable_roles"] = True
    elif action == "needs_revision":
        candidate["status"] = "needs_review"
        candidate["can_apply_to_variable_roles"] = False
    else:
        candidate["status"] = "rejected"
        candidate["can_apply_to_variable_roles"] = False

    event = {
        "actor": "user",
        "action": action,
        "timestamp": utc_now(),
        "note": note,
    }
    candidate.setdefault("review_events", []).append(event)
    candidate["updated_at"] = event["timestamp"]
    candidate["does_not_mutate_variable_role_set"] = True
    state.setdefault("candidates", {})[candidate_id] = candidate
    state["latest_candidate_id"] = candidate_id
    state["updated_at"] = candidate["updated_at"]
    write_variable_role_candidate_state(project_root, state)
    return variable_role_candidate_response(project, candidate)


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


def infer_roles_from_field_profile(fields: list[dict[str, Any]]) -> dict[str, list[str]]:
    field_names = [str(field.get("name", "")).strip() for field in fields if str(field.get("name", "")).strip()]
    outcome = first_field_matching(fields, {"wage", "income", "salary", "earnings", "outcome", "y", "工资", "收入"})
    treatment = first_field_matching(fields, {"trained", "training", "treatment", "treated", "exposure", "robot", "policy", "培训", "处理", "政策", "机器人"})
    reserved = set(outcome + treatment)
    controls = [
        name
        for name in field_names
        if name not in reserved
        and is_control_candidate(next((field for field in fields if field.get("name") == name), {}))
    ]
    return normalize_roles(
        {
            "outcome": outcome,
            "treatment": treatment,
            "controls": controls[:12],
            "instruments": [],
            "fixed_effects": [],
            "cluster_by": [],
        }
    )


def first_field_matching(fields: list[dict[str, Any]], terms: set[str]) -> list[str]:
    for field in fields:
        name = str(field.get("name", "")).strip()
        if not name:
            continue
        haystack = f"{name} {field.get('label', '')}".lower()
        if any(term.lower() in haystack for term in terms):
            return [name]
    return []


def is_control_candidate(field: dict[str, Any]) -> bool:
    name = str(field.get("name", "")).lower()
    if name in {"id", "pid", "person_id", "individual_id", "year", "city", "province"}:
        return False
    inferred_type = str(field.get("inferred_type", "")).lower()
    stata_type = str(field.get("stata_type", "")).lower()
    if inferred_type == "text" or stata_type.startswith("str"):
        return False
    return True


def build_field_options(fields: list[dict[str, Any]], roles: dict[str, list[str]]) -> list[dict[str, Any]]:
    role_lookup = {}
    for role, names in roles.items():
        for name in names:
            role_lookup[name] = role
    options = []
    for field in fields:
        name = str(field.get("name", "")).strip()
        recommended = role_lookup.get(name, "exclude")
        options.append(
            {
                "name": name,
                "label": field.get("label"),
                "inferred_type": field.get("inferred_type"),
                "stata_type": field.get("stata_type"),
                "display_format": field.get("display_format"),
                "missing_rate": field.get("missing_rate"),
                "recommended_role": recommended,
                "recommendation_reason": variable_role_recommendation_reason(recommended),
            }
        )
    return options


def variable_role_recommendation_reason(role: str) -> str:
    return {
        "outcome": "字段名或变量标签与结果变量关键词匹配。",
        "treatment": "字段名或变量标签与处理变量关键词匹配。",
        "controls": "数值字段且未被识别为结果/处理/ID 字段。",
        "instruments": "未自动识别工具变量，需要人工判断。",
        "fixed_effects": "未自动识别固定效应，需要人工判断。",
        "cluster_by": "未自动识别聚类方式，需要人工判断。",
        "exclude": "未进入默认候选，仍可人工调整。",
    }.get(role, "需要人工判断。")


def build_variable_role_candidate_id(dataset_import_id: str, profile_id: str) -> str:
    digest = hashlib.sha1(f"{dataset_import_id}:{profile_id}".encode("utf-8")).hexdigest()[:12]
    return f"variable_role_candidate_{digest}"


def load_dataset_import_manifest(project_root: Path) -> dict[str, Any]:
    path = project_root / DATASET_IMPORT_PREFLIGHT_PATH
    if not path.exists():
        return {"dataset_imports": {}, "dataset_import_profiles": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"dataset_imports": {}, "dataset_import_profiles": {}}
    if not isinstance(payload, dict):
        return {"dataset_imports": {}, "dataset_import_profiles": {}}
    payload.setdefault("dataset_imports", {})
    payload.setdefault("dataset_import_profiles", {})
    return payload


def load_variable_role_candidate_state(project_root: Path) -> dict[str, Any]:
    path = variable_role_candidate_state_path(project_root)
    if not path.exists():
        return {"candidates": {}, "latest_candidate_id": None, "updated_at": None}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"candidates": {}, "latest_candidate_id": None, "updated_at": None}
    if not isinstance(payload, dict):
        return {"candidates": {}, "latest_candidate_id": None, "updated_at": None}
    payload.setdefault("candidates", {})
    payload.setdefault("latest_candidate_id", None)
    payload.setdefault("updated_at", None)
    return payload


def write_variable_role_candidate_state(project_root: Path, state: dict[str, Any]) -> None:
    path = variable_role_candidate_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def variable_role_candidate_response(project: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "variable_role_candidate_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "variable_role_candidate": candidate,
    }


def normalize_roles(roles: dict[str, Any]) -> dict[str, list[str]]:
    return {key: normalize_role_list(roles.get(key, [])) for key in ROLE_KEYS}


def normalize_role_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
