from __future__ import annotations

from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


DRAFT_EXTENSIONS = {".md", ".tex", ".txt"}


def local_file_meta(service: str) -> dict[str, str]:
    return {
        "evidence_level": "local_file",
        "service": service,
        "generated_at": utc_now(),
    }


def project_root_for(project: dict[str, Any]) -> Path:
    return Path(project.get("project_root") or project["root"]).resolve()


def title_for(path: Path) -> str:
    if path.suffix == ".md":
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip() or path.stem
    return path.stem.replace("_", " ").replace("-", " ").strip().title() or path.name


def list_project_drafts(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    root = project_root_for(project)
    generated_root = root / "Manuscripts" / "generated"
    items: list[dict[str, Any]] = []
    if generated_root.exists():
        for path in sorted(generated_root.iterdir()):
            if not path.is_file() or path.suffix.lower() not in DRAFT_EXTENSIONS:
                continue
            relative_path = path.resolve().relative_to(root)
            items.append(
                {
                    "chapter_id": path.stem,
                    "title": title_for(path),
                    "path": relative_path.as_posix(),
                    "status": "available",
                    "format": path.suffix.lstrip("."),
                    "updated_at": utc_now(),
                }
            )
    return {
        "_meta": local_file_meta("draft_service"),
        "project_id": project_id,
        "source_root": "Manuscripts/generated",
        "items": items,
        "empty_state": {
            "title": "尚未生成草稿",
            "description": "已检查 Manuscripts/generated/，当前没有可展示草稿文件。",
            "next_action": "先生成或放入 Markdown/LaTeX 草稿文件。",
        }
        if not items
        else None,
    }
