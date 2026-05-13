from __future__ import annotations

import csv
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .registry import add_project, get_project, get_project_by_id, list_projects
from .orchestrator import orchestrate_project, run_workbench
from .observability_service import (
    load_observable_events,
    load_observable_gates,
    load_observable_steps,
    load_run_observability,
    resolve_observable_gate,
)
from .run_store import create_run, get_run, list_runs, save_run


ESSENTIAL_PATHS = [
    "README.md",
    ".gitignore",
    "paper.yaml",
    "Data",
    "Manuscripts",
    "Program",
    "Reference",
    "Results",
    "Submissions",
    "Tasks",
    "docs",
    "state",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def copy_essential_tree(repo_root: Path, target_root: Path) -> None:
    target_root.mkdir(parents=True, exist_ok=True)
    for rel in ESSENTIAL_PATHS:
        src = repo_root / rel
        dst = target_root / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def reset_runtime_outputs(target_root: Path) -> None:
    cleanup_paths = [
        target_root / "Results" / "index.json",
        target_root / "Results" / "json" / "analysis_result.json",
        target_root / "Results" / "json" / "project_snapshot.json",
        target_root / "Results" / "logs" / "run_paper.log",
        target_root / "Results" / "logs" / "export_docx.log",
        target_root / "Manuscripts" / "generated" / "paper_draft.md",
        target_root / "Manuscripts" / "generated" / "paper_draft.tex",
        target_root / "Submissions" / "paper_draft.docx",
        target_root / "Submissions" / "export_manifest.json",
        target_root / "state" / "project_state.json",
    ]
    for path in cleanup_paths:
        if path.exists():
            path.unlink()


def customize_paper_yaml(target_root: Path, slug: str, title: str, question: str) -> None:
    paper_path = target_root / "paper.yaml"
    payload = yaml.safe_load(paper_path.read_text(encoding="utf-8"))
    payload["project"]["slug"] = slug
    payload["project"]["title"] = title
    payload["research"]["question"] = question
    paper_path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def create_workspace(
    product_root: Path,
    repo_root: Path,
    slug: str,
    title: str,
    question: str,
) -> dict[str, Any]:
    workspace_root = product_root / "workspaces" / slug
    if workspace_root.exists():
        raise FileExistsError(slug)
    copy_essential_tree(repo_root, workspace_root)
    reset_runtime_outputs(workspace_root)
    customize_paper_yaml(workspace_root, slug=slug, title=title, question=question)
    project = {
        "slug": slug,
        "title": title,
        "question": question,
        "root": str(workspace_root),
        "source": "product-wizard",
        "created_at": utc_now(),
    }
    add_project(product_root, repo_root, project)
    return project


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def latest_orchestration_snapshot(root: Path) -> dict[str, Any] | None:
    candidates = [
        root / "06_workspace" / "runs",
        root / "workspace" / "runs",
        root / "state" / "orchestration",
    ]
    orchestrations_root = next((path for path in candidates if path.exists()), None)
    if orchestrations_root is None:
        return None
    manifests = sorted(orchestrations_root.glob("*/run_manifest.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not manifests:
        return None
    manifest_path = manifests[0]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    revised_path = manifest_path.parent / "06_writing" / "paper_draft.md"
    review_path = manifest_path.parent / "07_review" / "reviewer_decision.json"
    if not revised_path.exists():
        revised_path = manifest_path.parent / "outputs" / "paper_draft_revised.md"
    if not review_path.exists():
        review_path = manifest_path.parent / "reviews" / "01_reviewer.json"
    return {
        "manifest": manifest,
        "revised_draft_path": str(revised_path.relative_to(root)) if revised_path.exists() else None,
        "revised_draft": revised_path.read_text(encoding="utf-8") if revised_path.exists() else None,
        "review_packet": json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else None,
    }


def project_snapshot(project: dict[str, Any]) -> dict[str, Any]:
    root = Path(project["root"])
    return {
        **project,
        "paper": load_json_if_exists(root / "state" / "project_state.json"),
        "results_index": load_json_if_exists(root / "Results" / "index.json"),
        "analysis_result": load_json_if_exists(root / "Results" / "json" / "analysis_result.json"),
        "latest_orchestration": latest_orchestration_snapshot(root),
        "artifacts": {
            "markdown": (root / "Manuscripts" / "generated" / "paper_draft.md").exists(),
            "latex": (root / "Manuscripts" / "generated" / "paper_draft.tex").exists(),
            "docx": (root / "Submissions" / "paper_draft.docx").exists(),
        },
    }


def project_api_view(project: dict[str, Any]) -> dict[str, Any]:
    snapshot = project_snapshot(project)
    paper = snapshot.get("paper") or {}
    return {
        "id": project["id"],
        "slug": project["slug"],
        "title": project["title"],
        "question": project.get("question", ""),
        "root": project["root"],
        "project_root": project["project_root"],
        "language": project.get("language", "zh"),
        "current_stage": paper.get("current_stage", "question-definition"),
        "dataset_exists": paper.get("dataset_exists", False),
        "last_run_mode": paper.get("last_run_mode", "never"),
        "created_at": project["created_at"],
        "updated_at": project.get("updated_at", project["created_at"]),
    }


def project_detail_view(project: dict[str, Any]) -> dict[str, Any]:
    snapshot = project_snapshot(project)
    return {
        "id": project["id"],
        **snapshot,
        "project_root": project["project_root"],
        "language": project.get("language", "zh"),
    }


def run_pipeline(project: dict[str, Any], live: bool) -> dict[str, Any]:
    root = Path(project["root"])
    command = ["python3", "Program/run_paper.py", "--project-root", "."]
    if not live:
        command.append("--dry-run")
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def export_docx(project: dict[str, Any]) -> dict[str, Any]:
    root = Path(project["root"])
    command = ["python3", "Program/export_docx.py", "--project-root", "."]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def load_project_snapshot(product_root: Path, repo_root: Path, slug: str) -> dict[str, Any]:
    return project_snapshot(get_project(product_root, repo_root, slug))


def load_project_list(product_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    return [project_snapshot(project) for project in list_projects(product_root, repo_root)]


def run_orchestration(project: dict[str, Any], live: bool) -> dict[str, Any]:
    root = Path(project["root"])
    manifest = orchestrate_project(root, run_live=live)
    return {
        "run_id": manifest["run_id"],
        "manifest": manifest,
        "run_dir": manifest["run_root"],
    }


def register_project_root(
    product_root: Path,
    repo_root: Path,
    slug: str,
    title: str,
    project_root: Path,
    language: str,
) -> dict[str, Any]:
    has_generic_runner = (project_root / "paper.yaml").exists() and (project_root / "Program" / "run_paper.py").exists()
    has_thesis_layout = (project_root / "01_data").exists() and (project_root / "02_code").exists() and (project_root / "04_paper").exists()
    if not (has_generic_runner or has_thesis_layout):
        raise FileNotFoundError("paper.yaml + Program/run_paper.py or thesis 01_data/02_code/04_paper")

    question = ""
    if (project_root / "paper.yaml").exists():
        question = yaml.safe_load((project_root / "paper.yaml").read_text(encoding="utf-8")).get("research", {}).get("question", "")
    elif (project_root / "state" / "project_state.json").exists():
        question = load_json_if_exists(project_root / "state" / "project_state.json").get("research_question", "")
    project = {
        "id": f"proj_{slug.replace('-', '_')}",
        "slug": slug,
        "title": title,
        "question": question,
        "root": str(project_root),
        "project_root": str(project_root),
        "language": language,
        "source": "registered",
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    add_project(product_root, repo_root, project)
    return project


def get_project_api_view(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    return project_api_view(get_project_by_id(product_root, repo_root, project_id))


def list_project_api_views(product_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    return [project_api_view(project) for project in list_projects(product_root, repo_root)]


def get_project_detail_api_view(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    return project_detail_view(get_project_by_id(product_root, repo_root, project_id))


def execute_run(project: dict[str, Any], mode: str, dataset_path: str | None = None) -> dict[str, Any]:
    root = Path(project["project_root"])
    dataset_source = resolve_dataset_source(root, dataset_path)
    run = create_run(root, project["id"], mode)
    run["status"] = "running"
    if dataset_source:
        run["dataset_source"] = dataset_source
    save_run(root, run)

    command = ["python3", "Program/run_paper.py", "--project-root", ".", "--run-id", run["id"]]
    if mode == "dry-run":
        command.append("--dry-run")

    process = subprocess.run(command, cwd=root, text=True, capture_output=True)
    state_path = root / "state" / "project_state.json"
    results_index_path = root / "Results" / "index.json"
    state = load_json_if_exists(state_path)
    results = load_json_if_exists(results_index_path)
    artifact_paths = []
    if state_path.exists():
        artifact_paths.append("state/project_state.json")
    if results_index_path.exists():
        artifact_paths.append("Results/index.json")
    if results and results.get("artifacts"):
        artifact_paths.extend(
            [
                artifact["path"]
                for artifact in results["artifacts"]
                if artifact.get("exists")
            ]
        )

    run.update(
        {
            "status": "succeeded" if process.returncode == 0 else "failed",
            "finished_at": utc_now(),
            "state_path": "state/project_state.json" if state_path.exists() else None,
            "results_index_path": "Results/index.json" if results_index_path.exists() else None,
            "artifact_count": len(artifact_paths),
            "artifact_paths": artifact_paths,
            "observability": {
                "manifest_path": f"state/runs/{run['id']}/run_manifest.json",
                "steps_path": f"state/runs/{run['id']}/run_steps.json",
                "events_path": f"state/runs/{run['id']}/run_events.jsonl",
                "gates_path": f"state/runs/{run['id']}/gates.json",
            },
            "state": {
                "current_stage": state.get("current_stage") if state else None,
                "last_run_mode": state.get("last_run_mode") if state else None,
                "dataset_exists": state.get("dataset_exists") if state else None,
            }
            if state
            else None,
            "results": results,
            "dataset_source": dataset_source,
            "error": None
            if process.returncode == 0
            else {"stdout": process.stdout, "stderr": process.stderr},
        }
    )
    persist_run_dataset_source(root, run["id"], dataset_source)
    save_run(root, run)
    return run


def execute_full_run_from_run_plan(project: dict[str, Any]) -> dict[str, Any]:
    from Product.backend.design_spec_service import load_saved_design_spec, load_saved_run_plan

    root = Path(project["project_root"])
    design_spec = load_saved_design_spec(root)
    run_plan = load_saved_run_plan(root)
    if not run_plan or run_plan.get("status") != "approved":
        raise FileNotFoundError("approved RunPlan is required")
    if not design_spec or design_spec.get("status") != "approved":
        raise FileNotFoundError("approved DesignSpec is required")

    dataset_source = resolve_dataset_source(root, run_plan.get("dataset_path"))
    plan_binding = build_run_plan_binding(design_spec, run_plan)
    research_engine = build_research_engine_reference()
    run = create_run(root, project["id"], "full-run")
    run["status"] = "running"
    run["dataset_source"] = dataset_source
    run["plan_binding"] = plan_binding
    run["research_engine"] = research_engine
    save_run(root, run)

    command = ["python3", "Program/run_paper.py", "--project-root", ".", "--run-id", run["id"]]
    process = subprocess.run(command, cwd=root, text=True, capture_output=True)
    state_path = root / "state" / "project_state.json"
    results_index_path = root / "Results" / "index.json"
    state = load_json_if_exists(state_path)
    results = load_json_if_exists(results_index_path)
    artifact_paths = []
    if state_path.exists():
        artifact_paths.append("state/project_state.json")
    if results_index_path.exists():
        artifact_paths.append("Results/index.json")
    if results and results.get("artifacts"):
        artifact_paths.extend(
            [
                artifact["path"]
                for artifact in results["artifacts"]
                if artifact.get("exists")
            ]
        )

    run.update(
        {
            "status": "succeeded" if process.returncode == 0 else "failed",
            "finished_at": utc_now(),
            "state_path": "state/project_state.json" if state_path.exists() else None,
            "results_index_path": "Results/index.json" if results_index_path.exists() else None,
            "artifact_count": len(artifact_paths),
            "artifact_paths": artifact_paths,
            "observability": {
                "manifest_path": f"state/runs/{run['id']}/run_manifest.json",
                "steps_path": f"state/runs/{run['id']}/run_steps.json",
                "events_path": f"state/runs/{run['id']}/run_events.jsonl",
                "gates_path": f"state/runs/{run['id']}/gates.json",
            },
            "state": {
                "current_stage": state.get("current_stage") if state else None,
                "last_run_mode": state.get("last_run_mode") if state else None,
                "dataset_exists": state.get("dataset_exists") if state else None,
            }
            if state
            else None,
            "results": results,
            "dataset_source": dataset_source,
            "plan_binding": plan_binding,
            "research_engine": research_engine,
            "execution_evidence_level": "local_execution",
            "error": None
            if process.returncode == 0
            else {"stdout": process.stdout, "stderr": process.stderr},
        }
    )
    persist_run_dataset_source(root, run["id"], dataset_source)
    persist_full_run_provenance(root, run["id"], plan_binding, research_engine)
    save_run(root, run)
    return run


def build_run_plan_binding(design_spec: dict[str, Any], run_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_level": "local_file",
        "variable_role_set_version": design_spec.get("variable_role_set_version"),
        "design_spec_version": run_plan.get("design_spec_version"),
        "run_plan_version": run_plan.get("version"),
        "dataset_path": run_plan.get("dataset_path"),
        "tasks": [
            {
                "id": task.get("id"),
                "formula": task.get("formula"),
                "estimator": task.get("estimator"),
                "status": task.get("status"),
            }
            for task in run_plan.get("tasks", [])
        ],
        "outputs": run_plan.get("outputs", []),
    }


def build_research_engine_reference() -> dict[str, Any]:
    return {
        "name": "Feynman-compatible research engine",
        "integration_mode": "callable_external",
        "embedded": False,
        "license": "MIT",
        "repository": "companion-inc/feynman",
        "evidence_level": "local_file",
        "note": "Feynman is treated as an external research-engine reference; its source is not embedded.",
    }


def resolve_dataset_source(project_root: Path, dataset_path: str | None) -> dict[str, Any] | None:
    configured_path = None
    if not dataset_path:
        configured = load_json_if_exists(project_root / "state" / "project_state.json")
        dataset_path = configured.get("dataset_path") if configured else None
    if not dataset_path:
        paper_path = project_root / "paper.yaml"
        if paper_path.exists():
            payload = yaml.safe_load(paper_path.read_text(encoding="utf-8")) or {}
            configured_path = payload.get("data", {}).get("final_dataset")
            dataset_path = configured_path
    elif (project_root / "paper.yaml").exists():
        payload = yaml.safe_load((project_root / "paper.yaml").read_text(encoding="utf-8")) or {}
        configured_path = payload.get("data", {}).get("final_dataset")
    if not dataset_path:
        return None

    raw_path = Path(dataset_path)
    if raw_path.is_absolute() or ".." in raw_path.parts:
        raise PermissionError(str(dataset_path))
    root = project_root.resolve()
    path = (root / raw_path).resolve()
    if path != root and root not in path.parents:
        raise PermissionError(str(dataset_path))
    if not path.is_file():
        raise FileNotFoundError(str(dataset_path))

    stat = path.stat()
    relative_path = path.relative_to(root).as_posix()
    source = {
        "path": path.relative_to(root).as_posix(),
        "name": path.name,
        "file_type": path.suffix.lower().lstrip("."),
        "size": stat.st_size,
        "exists": True,
        "evidence_level": "local_file",
        "role": "configured_final_dataset" if configured_path and Path(configured_path).as_posix() == relative_path else "selected_dataset",
    }
    source.update(inspect_dataset_source_shape(path))
    return source


def inspect_dataset_source_shape(path: Path) -> dict[str, int | None]:
    if path.suffix.lower() != ".csv":
        return {"row_count": None, "column_count": None}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return {"row_count": 0, "column_count": 0}
    return {"row_count": max(len(rows) - 1, 0), "column_count": len(rows[0])}


def persist_run_dataset_source(project_root: Path, run_id: str, dataset_source: dict[str, Any] | None) -> None:
    if not dataset_source:
        return
    manifest_path = project_root / "state" / "runs" / run_id / "run_manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["dataset_source"] = dataset_source
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def persist_full_run_provenance(
    project_root: Path,
    run_id: str,
    plan_binding: dict[str, Any],
    research_engine: dict[str, Any],
) -> None:
    manifest_path = project_root / "state" / "runs" / run_id / "run_manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["run_plan_binding"] = plan_binding
    manifest["research_engine"] = research_engine
    manifest["execution_evidence_level"] = "local_execution"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def get_project_run(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return get_run(Path(project["project_root"]), run_id)


def get_project_run_observability(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return load_run_observability(Path(project["project_root"]), run_id)


def get_project_run_events(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return load_observable_events(Path(project["project_root"]), run_id)


def get_project_run_steps(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return load_observable_steps(Path(project["project_root"]), run_id)


def get_project_run_gates(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    return load_observable_gates(Path(project["project_root"]), run_id)


def resolve_project_run_gate(project: dict[str, Any], run_id: str, gate_id: str, action: str, note: str) -> dict[str, Any]:
    return resolve_observable_gate(Path(project["project_root"]), run_id, gate_id, action, note)


def list_project_runs(project: dict[str, Any]) -> list[dict[str, Any]]:
    return list_runs(Path(project["project_root"]))


def execute_workbench_run(project: dict[str, Any], mode: str, user_goal: str) -> dict[str, Any]:
    root = Path(project["project_root"])
    return run_workbench(root, mode=mode, user_goal=user_goal)


def get_workbench_run(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    root = Path(project["project_root"])
    for base in [root / "06_workspace" / "runs", root / "workspace" / "runs"]:
        manifest_path = base / run_id / "run_manifest.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text(encoding="utf-8"))
    raise KeyError(run_id)
