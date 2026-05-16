from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


RESEARCH_QUESTION_PATH = Path("state/product/research_question.json")
ALLOWED_SOURCES = {"user_input", "project_seed", "imported"}


class InvalidResearchQuestionError(ValueError):
    pass


def research_question_state_path(project_root: Path) -> Path:
    return project_root / RESEARCH_QUESTION_PATH


def load_saved_research_question(project_root: Path) -> dict[str, Any] | None:
    path = research_question_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def get_current_research_question(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    question = load_or_build_research_question(project, project_root)
    return {
        "_meta": {
            "evidence_level": question.get("evidence_level", "local_file"),
            "service": "research_question_service",
            "generated_at": utc_now(),
        },
        "project": project_identity(project),
        "research_question": question,
    }


def save_current_research_question(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    question_text: str,
    source: str,
    note: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    normalized_question = question_text.strip()
    if not normalized_question:
        raise InvalidResearchQuestionError("Research question cannot be empty.")
    normalized_source = source if source in ALLOWED_SOURCES else "user_input"
    existing = load_saved_research_question(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    previous_events = existing.get("decision_events", []) if existing else []
    timestamp = utc_now()
    event = {
        "actor": "user",
        "action": "confirm_research_question",
        "timestamp": timestamp,
        "note": note,
        "source": normalized_source,
    }
    state = {
        "id": "research_question",
        "topic_session_id": f"topic_session_v{version}",
        "version": version,
        "status": "confirmed",
        "question": normalized_question,
        "evidence_level": "local_file",
        "source": normalized_source,
        "path": RESEARCH_QUESTION_PATH.as_posix(),
        "exists": True,
        "updated_at": timestamp,
        "decision_events": [*previous_events, event],
        "write_boundary": "ResearchQuestion 只确认研究上下文；不会自动改写 VariableRoleSet、DesignSpec 或 RunPlan。",
    }
    path = research_question_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "research_question_service",
            "generated_at": utc_now(),
        },
        "project": project_identity(project),
        "research_question": state,
    }


def load_or_build_research_question(project: dict[str, Any], project_root: Path) -> dict[str, Any]:
    saved = load_saved_research_question(project_root)
    if saved:
        return saved
    project_question = project.get("question") or read_project_seed_question(project_root)
    status = "draft_from_project" if project_question else "empty"
    return {
        "id": "research_question",
        "topic_session_id": "",
        "version": 0,
        "status": status,
        "question": project_question,
        "evidence_level": "local_file",
        "source": "project_seed" if project_question else "none",
        "path": RESEARCH_QUESTION_PATH.as_posix(),
        "exists": False,
        "updated_at": None,
        "decision_events": [],
        "write_boundary": "ResearchQuestion 只确认研究上下文；不会自动改写 VariableRoleSet、DesignSpec 或 RunPlan。",
    }


def read_project_seed_question(project_root: Path) -> str:
    paper_path = project_root / "paper.yaml"
    if not paper_path.exists():
        return ""
    try:
        payload = yaml.safe_load(paper_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return ""
    return str(payload.get("research", {}).get("question", "") or "").strip()


def project_identity(project: dict[str, Any]) -> dict[str, str]:
    return {
        "id": project["id"],
        "slug": project["slug"],
        "title": project["title"],
    }
