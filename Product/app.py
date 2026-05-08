from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from Product.backend.artifact_service import get_artifact, promote_artifact
from Product.backend.codex_provider import local_codex_status
from Product.backend.project_service import (
    create_workspace,
    execute_workbench_run,
    execute_run,
    export_docx,
    get_project_api_view,
    get_project_detail_api_view,
    get_project_run,
    get_workbench_run,
    load_project_list,
    load_project_snapshot,
    list_project_api_views,
    list_project_runs,
    register_project_root,
    run_orchestration,
    run_pipeline,
)
from Product.backend.registry import ensure_registry, get_project_by_id
from Product.backend.workflow_service import (
    cancel_workflow,
    create_workflow,
    get_report,
    get_task,
    get_workflow_bundle,
    list_workflows,
    load_artifacts,
    load_tasks,
    start_workflow,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_ROOT = REPO_ROOT / "Product"
WEB_ROOT = PRODUCT_ROOT / "web"

ensure_registry(PRODUCT_ROOT, REPO_ROOT)

app = FastAPI(title="Econ Workbench Product Shell", version="0.1.0")
app.mount("/assets", StaticFiles(directory=WEB_ROOT / "assets"), name="assets")


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": {},
            }
        },
    )


class CreateProjectPayload(BaseModel):
    slug: str = Field(min_length=3)
    title: str
    question: str


class CreateManagedProjectPayload(BaseModel):
    slug: str = Field(min_length=3)
    title: str
    project_root: str
    language: str = "zh"


class RunPayload(BaseModel):
    mode: str = "dry-run"


class WorkbenchRunPayload(BaseModel):
    mode: str = "dry-run"
    user_goal: str = ""


class CreateWorkflowPayload(BaseModel):
    title: str = Field(min_length=1)
    project_id: str | None = None


class PromoteArtifactPayload(BaseModel):
    target: str


@app.get("/api/status")
def api_status() -> dict:
    return {
        "ok": True,
        "product_root": str(PRODUCT_ROOT),
        "repo_root": str(REPO_ROOT),
        "projects_count": len(load_project_list(PRODUCT_ROOT, REPO_ROOT)),
    }


@app.get("/api/v1/health")
def api_v1_health() -> dict:
    return {
        "status": "ok",
        "service": "econ-paper-product-api",
        "version": "0.1.0",
    }


@app.get("/api/v1/providers/local-codex")
def api_v1_local_codex_provider() -> dict:
    return local_codex_status()


@app.post("/api/v1/workflows", status_code=201)
def api_v1_create_workflow(payload: CreateWorkflowPayload) -> dict:
    try:
        return create_workflow(PRODUCT_ROOT, REPO_ROOT, payload.title, payload.project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {payload.project_id} does not exist.")


@app.get("/api/v1/workflows")
def api_v1_workflows() -> dict:
    return {"items": list_workflows(PRODUCT_ROOT)}


@app.get("/api/v1/workflows/{workflow_id}")
def api_v1_workflow(workflow_id: str) -> dict:
    try:
        return get_workflow_bundle(PRODUCT_ROOT, REPO_ROOT, workflow_id)
    except KeyError as exc:
        return error_response(404, "workflow_not_found", f"Workflow {workflow_id} does not exist.")


@app.post("/api/v1/workflows/{workflow_id}/start")
def api_v1_start_workflow(workflow_id: str) -> dict:
    try:
        return start_workflow(PRODUCT_ROOT, REPO_ROOT, workflow_id)
    except KeyError as exc:
        return error_response(404, "workflow_not_found", f"Workflow {workflow_id} does not exist.")


@app.post("/api/v1/workflows/{workflow_id}/cancel")
def api_v1_cancel_workflow(workflow_id: str) -> dict:
    try:
        return cancel_workflow(PRODUCT_ROOT, workflow_id)
    except KeyError as exc:
        return error_response(404, "workflow_not_found", f"Workflow {workflow_id} does not exist.")


@app.get("/api/v1/workflows/{workflow_id}/tasks")
def api_v1_workflow_tasks(workflow_id: str) -> dict:
    try:
        return {"items": load_tasks(PRODUCT_ROOT, workflow_id)}
    except KeyError as exc:
        return error_response(404, "workflow_not_found", f"Workflow {workflow_id} does not exist.")


@app.get("/api/v1/workflows/{workflow_id}/tasks/{task_id}")
def api_v1_workflow_task(workflow_id: str, task_id: str) -> dict:
    try:
        return {"task": get_task(PRODUCT_ROOT, workflow_id, task_id)}
    except KeyError as exc:
        return error_response(404, "task_not_found", f"Task {task_id} does not exist.")


@app.get("/api/v1/workflows/{workflow_id}/artifacts")
def api_v1_workflow_artifacts(workflow_id: str) -> dict:
    try:
        return {"items": load_artifacts(PRODUCT_ROOT, workflow_id)}
    except KeyError as exc:
        return error_response(404, "workflow_not_found", f"Workflow {workflow_id} does not exist.")


@app.get("/api/v1/artifacts/{artifact_id}")
def api_v1_artifact(artifact_id: str) -> dict:
    try:
        return get_artifact(PRODUCT_ROOT, REPO_ROOT, artifact_id)
    except KeyError as exc:
        return error_response(404, "artifact_not_found", f"Artifact {artifact_id} does not exist.")


@app.post("/api/v1/artifacts/{artifact_id}/promote")
def api_v1_promote_artifact(artifact_id: str, payload: PromoteArtifactPayload) -> dict:
    try:
        return promote_artifact(PRODUCT_ROOT, REPO_ROOT, artifact_id, payload.target)
    except ValueError as exc:
        return error_response(400, "invalid_target", f"Unsupported promote target: {payload.target}.")
    except PermissionError as exc:
        return error_response(409, "promotion_blocked", str(exc))
    except FileNotFoundError as exc:
        return error_response(404, "artifact_file_missing", f"Artifact file does not exist: {exc}")
    except KeyError as exc:
        return error_response(404, "artifact_not_found", f"Artifact {artifact_id} does not exist.")


@app.get("/api/v1/workflows/{workflow_id}/report")
def api_v1_workflow_report(workflow_id: str) -> dict:
    try:
        return get_report(PRODUCT_ROOT, REPO_ROOT, workflow_id)
    except KeyError as exc:
        return error_response(404, "workflow_not_found", f"Workflow {workflow_id} does not exist.")


@app.get("/api/v1/projects")
def api_v1_projects() -> dict:
    return {"items": list_project_api_views(PRODUCT_ROOT, REPO_ROOT)}


@app.post("/api/v1/projects", status_code=201)
def api_v1_create_project(payload: CreateManagedProjectPayload) -> dict:
    try:
        project = register_project_root(
            PRODUCT_ROOT,
            REPO_ROOT,
            slug=payload.slug,
            title=payload.title,
            project_root=Path(payload.project_root).resolve(),
            language=payload.language,
        )
    except FileNotFoundError as exc:
        return error_response(400, "invalid_request", f"Missing required file: {exc}")
    return get_project_api_view(PRODUCT_ROOT, REPO_ROOT, project["id"])


@app.get("/api/v1/projects/{project_id}")
def api_v1_project(project_id: str) -> dict:
    try:
        return get_project_detail_api_view(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/runs", status_code=202)
def api_v1_create_run(project_id: str, payload: RunPayload) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    return execute_run(project, payload.mode)


@app.get("/api/v1/projects/{project_id}/runs")
def api_v1_runs(project_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    return {"items": list_project_runs(project)}


@app.post("/api/v1/projects/{project_id}/workbench-runs", status_code=202)
def api_v1_create_workbench_run(project_id: str, payload: WorkbenchRunPayload) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    return execute_workbench_run(project, payload.mode, payload.user_goal)


@app.get("/api/v1/projects/{project_id}/workbench-runs/{run_id}")
def api_v1_workbench_run(project_id: str, run_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return get_workbench_run(project, run_id)
    except KeyError as exc:
        return error_response(404, "run_not_found", f"Workbench run {run_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/runs/{run_id}")
def api_v1_run(project_id: str, run_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return get_project_run(project, run_id)
    except KeyError as exc:
        return error_response(404, "run_not_found", f"Run {run_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/export")
def api_v1_export(project_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    result = export_docx(project)
    return {
        "project_id": project_id,
        "execution": result,
        "snapshot": get_project_detail_api_view(PRODUCT_ROOT, REPO_ROOT, project_id),
    }


@app.post("/api/v1/projects/{project_id}/orchestrate")
def api_v1_orchestrate(project_id: str, mode: str = "dry-run") -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    result = run_orchestration(project, live=(mode == "live"))
    return {
        "project_id": project_id,
        "mode": mode,
        "orchestration": result,
        "snapshot": get_project_detail_api_view(PRODUCT_ROOT, REPO_ROOT, project_id),
    }


@app.get("/api/projects")
def api_projects() -> dict:
    return {"projects": load_project_list(PRODUCT_ROOT, REPO_ROOT)}


@app.get("/api/projects/{slug}")
def api_project(slug: str) -> dict:
    try:
        return load_project_snapshot(PRODUCT_ROOT, REPO_ROOT, slug)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown project: {slug}") from exc


@app.post("/api/projects")
def api_create_project(payload: CreateProjectPayload) -> dict:
    try:
        project = create_workspace(
            PRODUCT_ROOT,
            REPO_ROOT,
            slug=payload.slug,
            title=payload.title,
            question=payload.question,
        )
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=f"Project already exists: {payload.slug}") from exc
    return {"project": project}


@app.post("/api/projects/{slug}/run")
def api_run_project(slug: str, mode: str = "live") -> dict:
    try:
        project = load_project_snapshot(PRODUCT_ROOT, REPO_ROOT, slug)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown project: {slug}") from exc
    result = run_pipeline(project, live=(mode != "dry-run"))
    return {
        "project": slug,
        "mode": mode,
        "execution": result,
        "snapshot": load_project_snapshot(PRODUCT_ROOT, REPO_ROOT, slug),
    }


@app.post("/api/projects/{slug}/export")
def api_export_project(slug: str) -> dict:
    try:
        project = load_project_snapshot(PRODUCT_ROOT, REPO_ROOT, slug)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown project: {slug}") from exc
    result = export_docx(project)
    return {
        "project": slug,
        "execution": result,
        "snapshot": load_project_snapshot(PRODUCT_ROOT, REPO_ROOT, slug),
    }


@app.post("/api/projects/{slug}/orchestrate")
def api_orchestrate_project(slug: str, mode: str = "dry-run") -> dict:
    try:
        project = load_project_snapshot(PRODUCT_ROOT, REPO_ROOT, slug)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown project: {slug}") from exc
    result = run_orchestration(project, live=(mode == "live"))
    return {
        "project": slug,
        "mode": mode,
        "orchestration": result,
        "snapshot": load_project_snapshot(PRODUCT_ROOT, REPO_ROOT, slug),
    }


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")
