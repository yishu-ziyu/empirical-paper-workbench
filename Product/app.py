from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from Product.backend.agent_task_queue_service import (
    AgentTaskQueueBlockedError,
    create_project_agent_task_queue,
    get_project_agent_task_queue,
)
from Product.backend.agent_registry_service import get_agent_details, list_agents
from Product.backend.artifact_service import get_artifact, promote_artifact
from Product.backend.codex_provider import local_codex_status
from Product.backend.design_spec_service import (
    get_project_design_spec,
    get_project_run_plan,
    save_project_design_spec,
    save_project_run_plan,
)
from Product.backend.draft_service import list_project_drafts
from Product.backend.manuscript_candidate_service import (
    CandidatePromotionRequiredError,
    CandidateReviewRequiredError,
    ExportPackageRequiredError,
    InvalidCandidateReviewActionError,
    InvalidWritebackApprovalActionError,
    ManuscriptCandidateNotFoundError,
    WritebackApprovalRequiredError,
    get_project_export_package,
    get_project_manuscript_candidates,
    save_project_docx_export_preflight,
    save_project_manuscript_candidate_export_preflight,
    save_project_manuscript_candidate_promotion,
    save_project_manuscript_candidate_review,
    save_project_writeback_approval,
)
from Product.backend.method_workflow_service import (
    MethodWorkflowBlockedError,
    get_project_method_workflows,
)
from Product.backend.overview_service import (
    CloudUploadRequiredError,
    DatasetImportProfileStateError,
    DatasetImportSourceChangedError,
    DatasetPreflightStateError,
    apply_external_dataset_bind_preflight,
    get_project_design,
    get_project_journey,
    get_project_overview,
    list_project_datasets,
    profile_external_dataset_import,
    save_external_dataset_bind_preflight,
)
from Product.backend.project_service import (
    MethodExecutionError,
    UnsupportedRunPlanMethodError,
    create_workspace,
    execute_workbench_run,
    execute_full_run_from_run_plan,
    execute_run,
    export_docx,
    get_project_api_view,
    get_project_detail_api_view,
    get_project_run,
    get_project_run_events,
    get_project_run_gates,
    get_project_run_observability,
    get_project_run_steps,
    get_workbench_run,
    load_project_list,
    load_project_snapshot,
    list_project_api_views,
    list_project_runs,
    register_project_root,
    resolve_project_run_gate,
    run_orchestration,
    run_pipeline,
)
from Product.backend.provenance_service import get_artifact_provenance
from Product.backend.registry import ensure_registry, get_project_by_id
from Product.backend.research_question_service import (
    InvalidResearchQuestionError,
    get_current_research_question,
    save_current_research_question,
)
from Product.backend.results_draft_service import (
    FindingNotFoundError,
    InvalidReviewActionError,
    get_project_results_draft,
    save_project_finding_review,
)
from Product.backend.reviewer_score_service import (
    generate_project_reviewer_scorecard,
    get_project_reviewer_scorecard,
)
from Product.backend.supervisor_plan_service import (
    InvalidSupervisorPlanReviewActionError,
    SupervisorPlanBlockedError,
    SupervisorPlanExecutionError,
    generate_project_supervisor_plan,
    get_project_supervisor_plan,
    review_project_supervisor_plan,
)
from Product.backend.task_dispatch_service import (
    AgentTaskDispatchReviewError,
    review_project_agent_task_dispatch,
)
from Product.backend.variable_role_service import (
    FieldProfileRequiredError,
    InvalidVariableRoleCandidateActionError,
    VariableRoleCandidateApprovalRequiredError,
    VariableRoleCandidateNotFoundError,
    generate_project_variable_role_candidate,
    get_project_variable_role_candidates,
    get_project_variable_roles,
    promote_project_variable_role_candidate,
    review_project_variable_role_candidate,
    save_project_variable_roles,
)
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


def error_response(status_code: int, code: str, message: str, details: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
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
    dataset_path: str | None = None


class WorkbenchRunPayload(BaseModel):
    mode: str = "dry-run"
    user_goal: str = ""


class ResolveGatePayload(BaseModel):
    action: str
    note: str = ""


class VariableRolePayload(BaseModel):
    dataset_path: str
    roles: dict[str, list[str]]
    note: str = ""
    candidate_id: str | None = None


class DesignSpecPayload(BaseModel):
    research_question: str
    identification_strategy: dict
    model: dict
    note: str = ""


class RunPlanPayload(BaseModel):
    tasks: list[dict]
    outputs: list[str]
    note: str = ""


class ExternalDatasetBindPreflightPayload(BaseModel):
    source_path: str
    strategy: str = "copy_to_project_raw"
    note: str = ""


class ExternalDatasetPreflightApplyPayload(BaseModel):
    action: str
    runtime_mode: str = "local"
    note: str = ""


class DatasetImportProfilePayload(BaseModel):
    row_limit: int = Field(default=200, ge=1, le=1000)


class VariableRoleCandidatePayload(BaseModel):
    note: str = ""


class VariableRoleCandidateReviewPayload(BaseModel):
    action: str
    note: str = ""
    candidate_roles: dict[str, list[str]] | None = None


class VariableRoleCandidatePromotePayload(BaseModel):
    note: str = ""


class FindingReviewPayload(BaseModel):
    action: str
    note: str = ""


class ManuscriptCandidateReviewPayload(BaseModel):
    action: str
    note: str = ""


class ManuscriptCandidatePromotePayload(BaseModel):
    note: str = ""


class ManuscriptCandidateExportPreflightPayload(BaseModel):
    note: str = ""


class WritebackApprovalPayload(BaseModel):
    action: str
    note: str = ""


class DocxPreflightPayload(BaseModel):
    note: str = ""


class ReviewerScorecardPayload(BaseModel):
    note: str = ""


class SupervisorPlanPayload(BaseModel):
    objective: str = Field(min_length=1)
    note: str = ""


class SupervisorPlanReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskQueuePayload(BaseModel):
    note: str = ""


class AgentTaskDispatchReviewPayload(BaseModel):
    action: str
    note: str = ""


class ResearchQuestionPayload(BaseModel):
    question: str
    source: str = "user_input"
    note: str = ""


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


@app.get("/api/v1/agents")
def api_v1_agents() -> dict:
    return list_agents()


@app.get("/api/v1/agents/{agent_id}/details")
def api_v1_agent_details(agent_id: str) -> dict:
    try:
        return get_agent_details(agent_id)
    except KeyError as exc:
        return error_response(404, "agent_not_found", f"Agent {agent_id} does not exist.")


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


@app.get("/api/v1/artifacts/{artifact_id}/provenance")
def api_v1_artifact_provenance(artifact_id: str) -> dict:
    try:
        return get_artifact_provenance(PRODUCT_ROOT, artifact_id)
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


@app.get("/api/v1/projects/{project_id}/overview")
def api_v1_project_overview(project_id: str) -> dict:
    try:
        return get_project_overview(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/journey")
def api_v1_project_journey(project_id: str) -> dict:
    try:
        return get_project_journey(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/research-question/current")
def api_v1_project_current_research_question(project_id: str) -> dict:
    try:
        return get_current_research_question(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/research-question/current")
def api_v1_save_project_current_research_question(project_id: str, payload: ResearchQuestionPayload) -> dict:
    try:
        return save_current_research_question(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            payload.question,
            payload.source,
            payload.note,
        )
    except InvalidResearchQuestionError as exc:
        return error_response(400, "invalid_research_question", str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/datasets")
def api_v1_project_datasets(project_id: str) -> dict:
    try:
        return list_project_datasets(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/datasets/external-bind-preflight", status_code=201)
def api_v1_external_dataset_bind_preflight(
    project_id: str,
    payload: ExternalDatasetBindPreflightPayload,
) -> dict:
    try:
        return save_external_dataset_bind_preflight(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            payload.source_path,
            payload.strategy,
            payload.note,
        )
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except PermissionError as exc:
        return error_response(400, "invalid_external_dataset_path", f"Path is outside the external data catalog: {exc}")
    except FileNotFoundError as exc:
        return error_response(400, "external_dataset_not_found", f"External dataset file does not exist: {exc}")
    except ValueError as exc:
        return error_response(400, "invalid_external_dataset_path", f"Unsupported external dataset path or strategy: {exc}")


@app.post("/api/v1/projects/{project_id}/datasets/external-bind-preflight/{preflight_id}/apply")
def api_v1_external_dataset_preflight_apply(
    project_id: str,
    preflight_id: str,
    payload: ExternalDatasetPreflightApplyPayload,
) -> dict:
    try:
        return apply_external_dataset_bind_preflight(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            preflight_id,
            payload.action,
            payload.runtime_mode,
            payload.note,
        )
    except CloudUploadRequiredError as exc:
        return error_response(409, "cloud_upload_required", str(exc))
    except DatasetPreflightStateError as exc:
        return error_response(409, "dataset_preflight_not_ready", str(exc))
    except FileExistsError as exc:
        return error_response(409, "dataset_target_exists", f"Target dataset already exists: {exc}")
    except KeyError as exc:
        return error_response(404, "dataset_preflight_not_found", f"Dataset preflight does not exist: {preflight_id}.")
    except PermissionError as exc:
        return error_response(400, "invalid_external_dataset_path", f"Path is outside the allowed boundary: {exc}")
    except FileNotFoundError as exc:
        return error_response(400, "external_dataset_not_found", f"External dataset file does not exist: {exc}")
    except ValueError as exc:
        return error_response(400, "invalid_dataset_import_action", str(exc))


@app.post("/api/v1/projects/{project_id}/datasets/imports/{dataset_import_id}/profile")
def api_v1_external_dataset_import_profile(
    project_id: str,
    dataset_import_id: str,
    payload: DatasetImportProfilePayload,
) -> dict:
    try:
        return profile_external_dataset_import(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            dataset_import_id,
            payload.row_limit,
        )
    except DatasetImportSourceChangedError as exc:
        return error_response(409, "dataset_import_source_changed", str(exc))
    except DatasetImportProfileStateError as exc:
        return error_response(409, "dataset_import_not_profileable", str(exc))
    except KeyError as exc:
        return error_response(404, "dataset_import_not_found", f"Dataset import does not exist: {dataset_import_id}.")
    except PermissionError as exc:
        return error_response(400, "invalid_external_dataset_path", f"Path is outside the allowed boundary: {exc}")
    except FileNotFoundError as exc:
        return error_response(400, "dataset_import_source_missing", f"Dataset import source file does not exist: {exc}")
    except ValueError as exc:
        return error_response(400, "invalid_dataset_import_profile", str(exc))


@app.get("/api/v1/projects/{project_id}/variable-role-candidates")
def api_v1_project_variable_role_candidates(project_id: str) -> dict:
    try:
        return get_project_variable_role_candidates(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/datasets/imports/{dataset_import_id}/variable-role-candidates")
def api_v1_generate_project_variable_role_candidate(
    project_id: str,
    dataset_import_id: str,
    payload: VariableRoleCandidatePayload,
) -> dict:
    try:
        return JSONResponse(
            status_code=201,
            content=generate_project_variable_role_candidate(
                PRODUCT_ROOT,
                REPO_ROOT,
                project_id,
                dataset_import_id,
                payload.note,
            ),
        )
    except FieldProfileRequiredError as exc:
        return error_response(409, "field_profile_required", str(exc))
    except KeyError as exc:
        return error_response(404, "dataset_import_not_found", f"Dataset import does not exist: {dataset_import_id}.")


@app.put("/api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/review")
def api_v1_review_project_variable_role_candidate(
    project_id: str,
    candidate_id: str,
    payload: VariableRoleCandidateReviewPayload,
) -> dict:
    try:
        return review_project_variable_role_candidate(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            candidate_id,
            payload.action,
            payload.note,
            payload.candidate_roles,
        )
    except InvalidVariableRoleCandidateActionError as exc:
        return error_response(400, "invalid_variable_role_candidate_action", str(exc))
    except VariableRoleCandidateNotFoundError as exc:
        return error_response(404, "variable_role_candidate_not_found", f"Variable role candidate does not exist: {candidate_id}.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/promote")
def api_v1_promote_project_variable_role_candidate(
    project_id: str,
    candidate_id: str,
    payload: VariableRoleCandidatePromotePayload,
) -> dict:
    try:
        return JSONResponse(
            status_code=201,
            content=promote_project_variable_role_candidate(
                PRODUCT_ROOT,
                REPO_ROOT,
                project_id,
                candidate_id,
                payload.note,
            ),
        )
    except VariableRoleCandidateApprovalRequiredError as exc:
        return error_response(
            409,
            "variable_role_candidate_approval_required",
            f"Variable role candidate must be approved before draft promotion: {candidate_id}.",
        )
    except VariableRoleCandidateNotFoundError as exc:
        return error_response(404, "variable_role_candidate_not_found", f"Variable role candidate does not exist: {candidate_id}.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/variable-roles")
def api_v1_project_variable_roles(project_id: str) -> dict:
    try:
        return get_project_variable_roles(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(400, "dataset_not_found", f"Dataset file does not exist: {exc}")
    except ValueError as exc:
        return error_response(400, "invalid_dataset_path", f"Unsupported dataset path: {exc}")


@app.put("/api/v1/projects/{project_id}/variable-roles")
def api_v1_save_project_variable_roles(project_id: str, payload: VariableRolePayload) -> dict:
    try:
        return save_project_variable_roles(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            payload.dataset_path,
            payload.roles,
            payload.note,
            payload.candidate_id,
        )
    except VariableRoleCandidateApprovalRequiredError as exc:
        return error_response(
            409,
            "variable_role_candidate_approval_required",
            f"Variable role candidate must be approved before formal save: {payload.candidate_id}.",
        )
    except VariableRoleCandidateNotFoundError as exc:
        return error_response(404, "variable_role_candidate_not_found", f"Variable role candidate does not exist: {payload.candidate_id}.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except PermissionError as exc:
        return error_response(400, "invalid_dataset_path", f"Dataset path must stay inside the project: {exc}")
    except FileNotFoundError as exc:
        return error_response(400, "dataset_not_found", f"Dataset file does not exist: {exc}")
    except ValueError as exc:
        return error_response(400, "invalid_dataset_path", f"Unsupported dataset path: {exc}")


@app.get("/api/v1/projects/{project_id}/design-spec")
def api_v1_project_design_spec(project_id: str) -> dict:
    try:
        return get_project_design_spec(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "variable_roles_required", str(exc))


@app.put("/api/v1/projects/{project_id}/design-spec")
def api_v1_save_project_design_spec(project_id: str, payload: DesignSpecPayload) -> dict:
    try:
        return save_project_design_spec(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            payload.research_question,
            payload.identification_strategy,
            payload.model,
            payload.note,
        )
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "variable_roles_required", str(exc))


@app.get("/api/v1/projects/{project_id}/run-plan")
def api_v1_project_run_plan(project_id: str) -> dict:
    try:
        return get_project_run_plan(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "design_spec_required", str(exc))


@app.get("/api/v1/projects/{project_id}/method-workflows")
def api_v1_project_method_workflows(project_id: str) -> dict:
    try:
        return get_project_method_workflows(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/supervisor-plan")
def api_v1_project_supervisor_plan(project_id: str) -> dict:
    try:
        return get_project_supervisor_plan(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/supervisor-plan", status_code=201)
def api_v1_generate_project_supervisor_plan(project_id: str, payload: SupervisorPlanPayload) -> dict:
    try:
        return generate_project_supervisor_plan(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            payload.objective,
            payload.note,
        )
    except SupervisorPlanBlockedError as exc:
        return error_response(409, exc.code, str(exc))
    except SupervisorPlanExecutionError as exc:
        return error_response(502, "local_codex_supervisor_failed", str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/supervisor-plan/review")
def api_v1_review_project_supervisor_plan(project_id: str, payload: SupervisorPlanReviewPayload) -> dict:
    try:
        return review_project_supervisor_plan(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            payload.action,
            payload.note,
        )
    except InvalidSupervisorPlanReviewActionError as exc:
        return error_response(400, "invalid_supervisor_plan_review_action", f"Unsupported review action: {payload.action}.")
    except SupervisorPlanBlockedError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/agent-task-queue")
def api_v1_project_agent_task_queue(project_id: str) -> dict:
    try:
        return get_project_agent_task_queue(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue", status_code=201)
def api_v1_create_project_agent_task_queue(
    project_id: str,
    payload: AgentTaskQueuePayload | None = None,
) -> dict:
    try:
        return create_project_agent_task_queue(PRODUCT_ROOT, REPO_ROOT, project_id)
    except AgentTaskQueueBlockedError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/dispatch-review")
def api_v1_review_project_agent_task_dispatch(
    project_id: str,
    task_id: str,
    payload: AgentTaskDispatchReviewPayload,
) -> dict:
    try:
        return review_project_agent_task_dispatch(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskDispatchReviewError as exc:
        status_code = 400 if exc.code == "invalid_dispatch_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/run-plan")
def api_v1_save_project_run_plan(project_id: str, payload: RunPlanPayload) -> dict:
    try:
        return save_project_run_plan(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            payload.tasks,
            payload.outputs,
            payload.note,
        )
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "design_spec_required", str(exc))
    except MethodWorkflowBlockedError as exc:
        return error_response(409, exc.code, str(exc), {"blocked_methods": exc.blocked_methods})


@app.get("/api/v1/projects/{project_id}/design")
def api_v1_project_design(project_id: str) -> dict:
    try:
        return get_project_design(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/drafts")
def api_v1_project_drafts(project_id: str) -> dict:
    try:
        return list_project_drafts(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/results-draft")
def api_v1_project_results_draft(project_id: str) -> dict:
    try:
        return get_project_results_draft(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.put("/api/v1/projects/{project_id}/results-draft/findings/{finding_id}/review")
def api_v1_review_project_finding(project_id: str, finding_id: str, payload: FindingReviewPayload) -> dict:
    try:
        return save_project_finding_review(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            finding_id,
            payload.action,
            payload.note,
        )
    except InvalidReviewActionError as exc:
        return error_response(400, "invalid_review_action", f"Invalid finding review action: {exc}")
    except FindingNotFoundError as exc:
        return error_response(404, "finding_not_found", f"Finding {exc} does not exist in latest results.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.get("/api/v1/projects/{project_id}/manuscript-candidates")
def api_v1_project_manuscript_candidates(project_id: str) -> dict:
    try:
        return get_project_manuscript_candidates(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.put("/api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/review")
def api_v1_review_manuscript_candidate(
    project_id: str,
    candidate_id: str,
    payload: ManuscriptCandidateReviewPayload,
) -> dict:
    try:
        return save_project_manuscript_candidate_review(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            candidate_id,
            payload.action,
            payload.note,
        )
    except InvalidCandidateReviewActionError as exc:
        return error_response(400, "invalid_candidate_review_action", f"Invalid candidate review action: {exc}")
    except ManuscriptCandidateNotFoundError as exc:
        return error_response(404, "manuscript_candidate_not_found", f"Candidate {exc} does not exist.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.post("/api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/promote")
def api_v1_promote_manuscript_candidate(
    project_id: str,
    candidate_id: str,
    payload: ManuscriptCandidatePromotePayload,
) -> dict:
    try:
        return save_project_manuscript_candidate_promotion(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            candidate_id,
            payload.note,
        )
    except CandidateReviewRequiredError as exc:
        return error_response(409, "candidate_review_required", f"Candidate {exc} must be approved before promote.")
    except ManuscriptCandidateNotFoundError as exc:
        return error_response(404, "manuscript_candidate_not_found", f"Candidate {exc} does not exist.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.post("/api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/export-preflight")
def api_v1_export_preflight_manuscript_candidate(
    project_id: str,
    candidate_id: str,
    payload: ManuscriptCandidateExportPreflightPayload,
) -> dict:
    try:
        return save_project_manuscript_candidate_export_preflight(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            candidate_id,
            payload.note,
        )
    except CandidatePromotionRequiredError as exc:
        return error_response(409, "candidate_promotion_required", f"Candidate {exc} must be ready_for_export before export preflight.")
    except ManuscriptCandidateNotFoundError as exc:
        return error_response(404, "manuscript_candidate_not_found", f"Candidate {exc} does not exist.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.get("/api/v1/projects/{project_id}/export-package")
def api_v1_project_export_package(project_id: str) -> dict:
    try:
        return get_project_export_package(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.get("/api/v1/projects/{project_id}/reviewer-scorecard")
def api_v1_project_reviewer_scorecard(project_id: str) -> dict:
    try:
        return get_project_reviewer_scorecard(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.post("/api/v1/projects/{project_id}/reviewer-scorecard", status_code=201)
def api_v1_generate_project_reviewer_scorecard(project_id: str, payload: ReviewerScorecardPayload) -> dict:
    try:
        return generate_project_reviewer_scorecard(PRODUCT_ROOT, REPO_ROOT, project_id, payload.note)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.post("/api/v1/projects/{project_id}/export-package/{candidate_id}/writeback-approval")
def api_v1_writeback_approval(
    project_id: str,
    candidate_id: str,
    payload: WritebackApprovalPayload,
) -> dict:
    try:
        return save_project_writeback_approval(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            candidate_id,
            payload.action,
            payload.note,
        )
    except InvalidWritebackApprovalActionError as exc:
        return error_response(400, "invalid_writeback_approval_action", f"Writeback approval action {exc} is not supported.")
    except ExportPackageRequiredError as exc:
        return error_response(409, "export_package_required", f"Candidate {exc} must be preview_ready before writeback approval.")
    except ManuscriptCandidateNotFoundError as exc:
        return error_response(404, "manuscript_candidate_not_found", f"Candidate {exc} does not exist.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.post("/api/v1/projects/{project_id}/export-package/{candidate_id}/docx-preflight")
def api_v1_docx_export_preflight(
    project_id: str,
    candidate_id: str,
    payload: DocxPreflightPayload,
) -> dict:
    try:
        return save_project_docx_export_preflight(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            candidate_id,
            payload.note,
        )
    except WritebackApprovalRequiredError as exc:
        return error_response(409, "writeback_approval_required", f"Candidate {exc} must have approved writeback before docx preflight.")
    except ExportPackageRequiredError as exc:
        return error_response(409, "export_package_required", f"Candidate {exc} must be preview_ready before docx preflight.")
    except ManuscriptCandidateNotFoundError as exc:
        return error_response(404, "manuscript_candidate_not_found", f"Candidate {exc} does not exist.")
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.post("/api/v1/projects/{project_id}/runs", status_code=202)
def api_v1_create_run(project_id: str, payload: RunPayload) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return execute_run(project, payload.mode, payload.dataset_path)
    except PermissionError as exc:
        return error_response(400, "invalid_dataset_path", f"Dataset path must stay inside the project: {exc}")
    except FileNotFoundError as exc:
        return error_response(400, "dataset_not_found", f"Dataset file does not exist: {exc}")


@app.post("/api/v1/projects/{project_id}/runs/full", status_code=202)
def api_v1_create_full_run(project_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return execute_full_run_from_run_plan(project)
    except PermissionError as exc:
        return error_response(400, "invalid_dataset_path", f"Dataset path must stay inside the project: {exc}")
    except FileNotFoundError as exc:
        message = str(exc)
        if "RunPlan" in message or "DesignSpec" in message:
            return error_response(409, "run_plan_required", message)
        return error_response(400, "dataset_not_found", f"Dataset file does not exist: {exc}")
    except UnsupportedRunPlanMethodError as exc:
        return error_response(409, "unsupported_run_plan_method", f"Unsupported RunPlan method: {exc}")
    except MethodExecutionError as exc:
        return error_response(409, "method_execution_failed", f"{exc.code}: {exc}")


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


@app.get("/api/v1/projects/{project_id}/runs/{run_id}/observability")
def api_v1_run_observability(project_id: str, run_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return get_project_run_observability(project, run_id)
    except KeyError as exc:
        return error_response(404, "run_not_found", f"Run {run_id} observability does not exist.")


@app.get("/api/v1/projects/{project_id}/runs/{run_id}/events")
def api_v1_run_events(project_id: str, run_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return get_project_run_events(project, run_id)
    except KeyError as exc:
        return error_response(404, "run_not_found", f"Run {run_id} events do not exist.")


@app.get("/api/v1/projects/{project_id}/runs/{run_id}/steps")
def api_v1_run_steps(project_id: str, run_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return get_project_run_steps(project, run_id)
    except KeyError as exc:
        return error_response(404, "run_not_found", f"Run {run_id} steps do not exist.")


@app.get("/api/v1/projects/{project_id}/runs/{run_id}/gates")
def api_v1_run_gates(project_id: str, run_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return get_project_run_gates(project, run_id)
    except KeyError as exc:
        return error_response(404, "run_not_found", f"Run {run_id} gates do not exist.")


@app.post("/api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve")
def api_v1_resolve_run_gate(project_id: str, run_id: str, gate_id: str, payload: ResolveGatePayload) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return resolve_project_run_gate(project, run_id, gate_id, payload.action, payload.note)
    except ValueError as exc:
        return error_response(400, "invalid_gate_action", f"Gate action {payload.action} is not supported.")
    except KeyError as exc:
        return error_response(404, "gate_not_found", f"Gate {gate_id} does not exist for run {run_id}.")


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
