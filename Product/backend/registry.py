from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def registry_path(product_root: Path) -> Path:
    return product_root / "state" / "projects.json"


def default_registry(product_root: Path, repo_root: Path) -> dict[str, Any]:
    return {
        "updated_at": utc_now(),
        "projects": [
            {
                "id": "proj_undergraduate_thesis",
                "slug": "undergraduate-thesis",
                "title": "待定题目：经济学实证论文",
                "question": "effect of trained on wage",
                "root": str(repo_root),
                "project_root": str(repo_root),
                "language": "zh",
                "source": "seed",
                "created_at": utc_now(),
                "updated_at": utc_now(),
            }
        ],
    }


def ensure_registry(product_root: Path, repo_root: Path) -> Path:
    path = registry_path(product_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            json.dumps(default_registry(product_root, repo_root), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return path


def read_registry(product_root: Path, repo_root: Path) -> dict[str, Any]:
    path = ensure_registry(product_root, repo_root)
    payload = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for project in payload.get("projects", []):
        changed |= normalize_project_record(project)
    if changed:
        write_registry(product_root, payload)
    return payload


def write_registry(product_root: Path, payload: dict[str, Any]) -> None:
    path = registry_path(product_root)
    payload["updated_at"] = utc_now()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def list_projects(product_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    return read_registry(product_root, repo_root)["projects"]


def get_project(product_root: Path, repo_root: Path, slug: str) -> dict[str, Any]:
    projects = list_projects(product_root, repo_root)
    for project in projects:
        if project["slug"] == slug:
            return project
    raise KeyError(slug)


def get_project_by_id(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    projects = list_projects(product_root, repo_root)
    for project in projects:
        if project["id"] == project_id:
            return project
    raise KeyError(project_id)


def get_project_by_id_or_transient(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    try:
        return get_project_by_id(product_root, repo_root, project_id)
    except KeyError:
        root = repo_root.resolve()
        slug = project_id.removeprefix("proj_").replace("_", "-") or root.name
        timestamp = utc_now()
        return {
            "id": project_id,
            "slug": slug,
            "title": root.name,
            "question": "",
            "root": str(root),
            "project_root": str(root),
            "language": infer_language(root),
            "source": "transient_runtime",
            "created_at": timestamp,
            "updated_at": timestamp,
        }


def add_project(product_root: Path, repo_root: Path, project: dict[str, Any]) -> None:
    payload = read_registry(product_root, repo_root)
    payload["projects"] = [p for p in payload["projects"] if p["slug"] != project["slug"]]
    payload["projects"].append(project)
    write_registry(product_root, payload)


def normalize_project_record(project: dict[str, Any]) -> bool:
    changed = False
    slug = project["slug"]
    project_root = project.get("project_root") or project.get("root")
    if project.get("id") is None:
        project["id"] = f"proj_{slug.replace('-', '_')}"
        changed = True
    if project.get("project_root") is None:
        project["project_root"] = project_root
        changed = True
    if project.get("root") is None:
        project["root"] = project_root
        changed = True
    if project.get("language") is None:
        project["language"] = infer_language(Path(project_root))
        changed = True
    if project.get("updated_at") is None:
        project["updated_at"] = utc_now()
        changed = True
    if project.get("created_at") is None:
        project["created_at"] = utc_now()
        changed = True
    return changed


def infer_language(project_root: Path) -> str:
    paper_path = project_root / "paper.yaml"
    if paper_path.exists():
        try:
            payload = yaml.safe_load(paper_path.read_text(encoding="utf-8"))
            return payload.get("project", {}).get("language", "zh")
        except Exception:
            return "zh"
    return "zh"
