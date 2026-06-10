from __future__ import annotations

import asyncio
import json
import queue
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from Product.backend.agent_task_queue_service import (
    AgentTaskQueueBlockedError,
    create_project_agent_task_queue,
    execute_project_agent_task,
    generate_project_draft_literature_review,
    generate_project_draft_section_plan,
    generate_project_draft_section_tasks,
    generate_project_formal_export_preflight,
    generate_project_internal_skill_execution_packet,
    generate_project_manuscript_citation_plan,
    generate_project_pdf_candidate_export,
    generate_project_section_drafts,
    generate_project_verified_literature_package,
    get_project_agent_task_queue,
    record_project_citation_verification_evidence,
    review_project_draft_literature_review,
    review_project_draft_section_plan,
    review_project_draft_section_tasks,
    review_project_formal_writeback_preflight,
    review_project_manuscript_citation_plan,
    review_project_section_drafts,
    review_project_verified_literature_package,
    review_project_reference_seed_package,
    select_project_agent_task_backend,
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
from Product.backend.execution_backend_service import ExecutionBackendSelectionError
from Product.backend.git_experiment_logger import (
    commit_stage,
    get_experiment_history,
    revert_to_commit,
)
from Product.backend.formal_submission_package_service import (
    FormalSubmissionPackageSummaryRequiredError,
    get_project_formal_submission_package_summary,
)
from Product.backend.orchestrator import (
    load_checkpoints,
    resolve_checkpoint,
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
from Product.backend.run_event_bus import ensure_queue, get_queue, list_active_runs
from Product.backend.verifier_service import (
    ExportCandidateRequiredError,
    get_project_verifier_checks,
    run_project_verifier_checks,
)
from Product.backend.supervisor_plan_service import (
    InvalidSupervisorPlanReviewActionError,
    SupervisorPlanBlockedError,
    SupervisorPlanExecutionError,
    generate_project_supervisor_plan,
    get_project_supervisor_plan,
    review_project_supervisor_plan,
)
from Product.backend.topic_intake_service import ensure_topic_supervisor_plan
from Product.backend.task_dispatch_service import (
    AgentTaskDispatchReviewError,
    review_project_agent_task_dispatch,
)
from Product.backend.trace_learning_service import (
    TraceLearningProposalBlockedError,
    capture_project_trace_learning_bad_case,
    generate_project_trace_learning_regression_test_patch_proposal,
    get_project_trace_learning_bad_cases,
    generate_project_trace_learning_regression_proposal,
    get_project_trace_learning_regression_proposals,
    review_project_trace_learning_regression_proposal,
    review_project_trace_learning_regression_test_patch_proposal,
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
from Product.backend.identity_service import (
    IdentityServiceError,
    activate_agent,
    deactivate_agent,
    get_project_identity,
    init_project_identities,
)
from Product.backend.permission_service import (
    PermissionServiceError,
    check_permission,
    get_project_permissions,
    init_project_permissions,
    save_project_permissions,
    update_policy,
)
from Product.backend.capability_registry import (
    CapabilityRegistryError,
    get_project_capabilities,
    reindex_capabilities,
)
from Product.backend.cost_service import (
    CostServiceError,
    finish_cost_event,
    get_project_costs,
    start_cost_event,
)
from Product.api.brief import router as brief_router
from Product.api.brief_stream import router as brief_stream_router
from Product.api.supervisor import router as supervisor_router
from Product.api.auto_research import router as auto_research_router


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_ROOT = REPO_ROOT / "Product"
WEB_ROOT = PRODUCT_ROOT / "web"
WEB_DIST_ROOT = PRODUCT_ROOT / "web-dist"

ensure_registry(PRODUCT_ROOT, REPO_ROOT)

app = FastAPI(title="Econ Workbench Product Shell", version="0.1.0")

# CORS for vite dev server (5173) → uvicorn (8765) split
# SSE 流式响应在 vite 内置 http-proxy 下不工作 (Subagent 3 验证),
# 改为前端直接用 absolute URL + CORS 跨域是更稳的方案.
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        # 2026-06-05: vite 5173 偶尔被占用, 自动 fallback 到 5174/5175
        "http://127.0.0.1:5175",
        "http://localhost:5175",
    ],
    allow_origin_regex=r"http://(127\.0\.0\.1|localhost):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=WEB_ROOT / "assets"), name="assets")
if (WEB_DIST_ROOT / "assets").exists():
    app.mount("/react/assets", StaticFiles(directory=WEB_DIST_ROOT / "assets"), name="react-assets")

# 5-tab vertical slice routers (L1: brief, L2: search, L3: variables, L4: design, L5: execute)
app.include_router(brief_router)
# Phase 1 brief-step-cards: SSE stream + resume endpoints (additive, does not replace /api/brief)
app.include_router(brief_stream_router)
# Task 42 (ui-gap-fill): intake-time mode-dispatch endpoints (no project_id)
app.include_router(supervisor_router)
app.include_router(auto_research_router)

from Product.api.design import router as design_router  # noqa: E402
app.include_router(design_router)

# L3-variables: 数据变量 (Variables) tab
from Product.api.variables import router as variables_router  # noqa: E402
app.include_router(variables_router)

# L5-execution: 执行实验 (Execution) tab - SSE endpoint
from Product.api.execute import router as execute_router  # noqa: E402
app.include_router(execute_router)

# Task 41: 后端 11 service 状态聚合 (状态条 single source of truth)
from Product.api.system import router as system_router  # noqa: E402
app.include_router(system_router)

# Task 43: DesignPanel 抽屉 — 浏览全部 StatsPAI 方法
from Product.api.capabilities import router as capabilities_router  # noqa: E402
app.include_router(capabilities_router)

# Task 44: 6th tab (identification-audit) real statspai diagnostics
from Product.api.identification import router as identification_router  # noqa: E402
app.include_router(identification_router)


# ── 5-tab routers (L1-L5 各自 register 自己的) ─────────────────────────────
# L2-search owns /api/search
from Product.api.search import router as search_router  # noqa: E402
app.include_router(search_router)


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


class ResolveCheckpointPayload(BaseModel):
    status: str
    user_feedback: str = ""


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


class TopicIntakeSupervisorPlanPayload(BaseModel):
    topic: str = Field(min_length=1)
    slug: str | None = None
    note: str = ""


class SupervisorPlanReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskQueuePayload(BaseModel):
    note: str = ""


class TraceLearningBadCasePayload(BaseModel):
    stage: str = Field(min_length=1)
    user_feedback: str = Field(min_length=1)
    surface: str = "browser"
    page_url: str = ""
    target_text: str = ""
    agent_output: str = ""
    expected_behavior: str = ""
    fix_layer: str = ""
    severity: str = "medium"
    related_files: list[str] = Field(default_factory=list)


class TraceLearningProposalReviewPayload(BaseModel):
    decision: str = Field(min_length=1)
    reviewer: str = "human"
    note: str = ""


class AgentTaskDispatchReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskReferenceSeedReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskDraftLiteratureReviewReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskVerifiedLiteraturePackageReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskManuscriptCitationPlanReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskDraftSectionPlanReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskDraftSectionTasksReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskSectionDraftsReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskFormalWritebackPreflightReviewPayload(BaseModel):
    action: str
    note: str = ""


class AgentTaskFormalExportPreflightPayload(BaseModel):
    note: str = ""


class AgentTaskPdfCandidateExportPayload(BaseModel):
    note: str = ""


class AgentTaskCitationVerificationEvidencePayload(BaseModel):
    connector: str
    authors: list[str] = Field(default_factory=list)
    year: str = ""
    title: str = ""
    venue: str = ""
    doi_or_stable_url: str = ""
    relevance: str = ""
    evidence_url: str = ""
    note: str = ""


class AgentTaskSelectBackendPayload(BaseModel):
    backend_id: str
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


class GovernanceInitPayload(BaseModel):
    note: str = ""


class GovernancePermissionCheckPayload(BaseModel):
    subject_id: str
    action: str
    note: str = ""


class GovernancePermissionPolicyPayload(BaseModel):
    subject_id: str
    allow: list[str] = []
    deny: list[str] = []


class GovernancePermissionUpdatePayload(BaseModel):
    policies: list[GovernancePermissionPolicyPayload]


class GovernanceCostEventPayload(BaseModel):
    workflow_id: str = ""
    task_id: str = ""
    actor_id: str
    capability_id: str
    event_type: str = "agent_task_run"
    note: str = ""


class GovernanceCostFinishPayload(BaseModel):
    event_id: str
    status: str
    wall_seconds: float = 0.0
    provider: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_usd: float = 0.0
    note: str = ""


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


@app.post("/api/v1/topic-intake/supervisor-plan", status_code=201)
def api_v1_topic_intake_supervisor_plan(payload: TopicIntakeSupervisorPlanPayload) -> dict:
    try:
        return ensure_topic_supervisor_plan(
            PRODUCT_ROOT,
            REPO_ROOT,
            payload.topic,
            payload.slug,
            payload.note,
        )
    except ValueError as exc:
        return error_response(400, "invalid_topic_intake", str(exc))
    except FileNotFoundError as exc:
        return error_response(400, "topic_workspace_invalid", f"Missing required file: {exc}")


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


@app.get("/api/v1/projects/{project_id}/trace-learning/bad-cases")
def api_v1_project_trace_learning_bad_cases(project_id: str) -> dict:
    try:
        return get_project_trace_learning_bad_cases(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/trace-learning/bad-cases", status_code=201)
def api_v1_capture_project_trace_learning_bad_case(project_id: str, payload: TraceLearningBadCasePayload) -> dict:
    try:
        return capture_project_trace_learning_bad_case(PRODUCT_ROOT, REPO_ROOT, project_id, payload.model_dump())
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/trace-learning/regression-proposals")
def api_v1_project_trace_learning_regression_proposals(project_id: str) -> dict:
    try:
        return get_project_trace_learning_regression_proposals(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/trace-learning/regression-proposals", status_code=201)
def api_v1_generate_project_trace_learning_regression_proposal(project_id: str) -> dict:
    try:
        return generate_project_trace_learning_regression_proposal(PRODUCT_ROOT, REPO_ROOT, project_id)
    except TraceLearningProposalBlockedError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/trace-learning/regression-proposals/{proposal_id}/review", status_code=201)
def api_v1_review_project_trace_learning_regression_proposal(
    project_id: str,
    proposal_id: str,
    payload: TraceLearningProposalReviewPayload,
) -> dict:
    try:
        return review_project_trace_learning_regression_proposal(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            proposal_id,
            payload.model_dump(),
        )
    except TraceLearningProposalBlockedError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post(
    "/api/v1/projects/{project_id}/trace-learning/regression-proposals/{proposal_id}/test-patch-proposals",
    status_code=201,
)
def api_v1_generate_project_trace_learning_regression_test_patch_proposal(
    project_id: str,
    proposal_id: str,
) -> dict:
    try:
        return generate_project_trace_learning_regression_test_patch_proposal(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            proposal_id,
        )
    except TraceLearningProposalBlockedError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post(
    "/api/v1/projects/{project_id}/trace-learning/regression-test-patch-proposals/{patch_proposal_id}/review",
    status_code=201,
)
def api_v1_review_project_trace_learning_regression_test_patch_proposal(
    project_id: str,
    patch_proposal_id: str,
    payload: TraceLearningProposalReviewPayload,
) -> dict:
    try:
        return review_project_trace_learning_regression_test_patch_proposal(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            patch_proposal_id,
            payload.model_dump(),
        )
    except TraceLearningProposalBlockedError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/internal-skill-execution-packet")
def api_v1_generate_project_internal_skill_execution_packet(
    project_id: str,
    task_id: str,
) -> dict:
    try:
        return generate_project_internal_skill_execution_packet(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
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
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/reference-seed-review")
def api_v1_review_project_reference_seed_package(
    project_id: str,
    task_id: str,
    payload: AgentTaskReferenceSeedReviewPayload,
) -> dict:
    try:
        return review_project_reference_seed_package(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 400 if exc.code == "invalid_reference_seed_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/draft-literature-review")
def api_v1_generate_project_draft_literature_review(
    project_id: str,
    task_id: str,
) -> dict:
    try:
        return generate_project_draft_literature_review(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/draft-literature-review-review")
def api_v1_review_project_draft_literature_review(
    project_id: str,
    task_id: str,
    payload: AgentTaskDraftLiteratureReviewReviewPayload,
) -> dict:
    try:
        return review_project_draft_literature_review(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 400 if exc.code == "invalid_draft_literature_review_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/citation-verification/{citation_task_id}")
def api_v1_record_project_citation_verification_evidence(
    project_id: str,
    task_id: str,
    citation_task_id: str,
    payload: AgentTaskCitationVerificationEvidencePayload,
) -> dict:
    try:
        return record_project_citation_verification_evidence(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            citation_task_id,
            payload.model_dump(),
        )
    except AgentTaskQueueBlockedError as exc:
        if exc.code in ("citation_verification_evidence_incomplete",):
            status_code = 400
        elif exc.code in ("agent_task_not_found", "citation_verification_task_not_found"):
            status_code = 404
        else:
            status_code = 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/verified-literature-package")
def api_v1_generate_project_verified_literature_package(
    project_id: str,
    task_id: str,
) -> dict:
    try:
        return generate_project_verified_literature_package(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/verified-literature-package-review")
def api_v1_review_project_verified_literature_package(
    project_id: str,
    task_id: str,
    payload: AgentTaskVerifiedLiteraturePackageReviewPayload,
) -> dict:
    try:
        return review_project_verified_literature_package(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 400 if exc.code == "invalid_verified_literature_package_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/manuscript-citation-plan")
def api_v1_generate_project_manuscript_citation_plan(
    project_id: str,
    task_id: str,
) -> dict:
    try:
        return generate_project_manuscript_citation_plan(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/manuscript-citation-plan-review")
def api_v1_review_project_manuscript_citation_plan(
    project_id: str,
    task_id: str,
    payload: AgentTaskManuscriptCitationPlanReviewPayload,
) -> dict:
    try:
        return review_project_manuscript_citation_plan(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 400 if exc.code == "invalid_manuscript_citation_plan_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/draft-section-plan")
def api_v1_generate_project_draft_section_plan(
    project_id: str,
    task_id: str,
) -> dict:
    try:
        return generate_project_draft_section_plan(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/draft-section-plan-review")
def api_v1_review_project_draft_section_plan(
    project_id: str,
    task_id: str,
    payload: AgentTaskDraftSectionPlanReviewPayload,
) -> dict:
    try:
        return review_project_draft_section_plan(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 400 if exc.code == "invalid_draft_section_plan_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/draft-section-tasks")
def api_v1_generate_project_draft_section_tasks(
    project_id: str,
    task_id: str,
) -> dict:
    try:
        return generate_project_draft_section_tasks(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/draft-section-tasks-review")
def api_v1_review_project_draft_section_tasks(
    project_id: str,
    task_id: str,
    payload: AgentTaskDraftSectionTasksReviewPayload,
) -> dict:
    try:
        return review_project_draft_section_tasks(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 400 if exc.code == "invalid_draft_section_tasks_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/section-drafts")
def api_v1_generate_project_section_drafts(
    project_id: str,
    task_id: str,
) -> dict:
    try:
        return generate_project_section_drafts(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/section-drafts-review")
def api_v1_review_project_section_drafts(
    project_id: str,
    task_id: str,
    payload: AgentTaskSectionDraftsReviewPayload,
) -> dict:
    try:
        return review_project_section_drafts(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 400 if exc.code == "invalid_section_drafts_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/formal-writeback-preflight-review")
def api_v1_review_project_formal_writeback_preflight(
    project_id: str,
    task_id: str,
    payload: AgentTaskFormalWritebackPreflightReviewPayload,
) -> dict:
    try:
        return review_project_formal_writeback_preflight(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.action,
            payload.note,
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 400 if exc.code == "invalid_formal_writeback_preflight_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/formal-export-preflight")
def api_v1_generate_project_formal_export_preflight(
    project_id: str,
    task_id: str,
    payload: AgentTaskFormalExportPreflightPayload | None = None,
) -> dict:
    try:
        return generate_project_formal_export_preflight(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.note if payload else "",
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/pdf-candidate-export")
def api_v1_generate_project_pdf_candidate_export(
    project_id: str,
    task_id: str,
    payload: AgentTaskPdfCandidateExportPayload | None = None,
) -> dict:
    try:
        return generate_project_pdf_candidate_export(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.note if payload else "",
        )
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/select-backend")
def api_v1_select_project_agent_task_backend(
    project_id: str,
    task_id: str,
    payload: AgentTaskSelectBackendPayload,
) -> dict:
    try:
        return select_project_agent_task_backend(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
            payload.backend_id,
        )
    except ExecutionBackendSelectionError as exc:
        status_code = 400 if exc.code in ("invalid_backend_id", "dispatch_review_required") else 409
        return error_response(status_code, exc.code, str(exc))
    except AgentTaskDispatchReviewError as exc:
        status_code = 400 if exc.code == "invalid_dispatch_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/execute")
def api_v1_execute_project_agent_task(
    project_id: str,
    task_id: str,
) -> dict:
    try:
        return execute_project_agent_task(
            PRODUCT_ROOT,
            REPO_ROOT,
            project_id,
            task_id,
        )
    except AgentTaskDispatchReviewError as exc:
        status_code = 400 if exc.code == "invalid_dispatch_review_action" else 409
        if exc.code == "agent_task_not_found":
            status_code = 404
        return error_response(status_code, exc.code, str(exc))
    except AgentTaskQueueBlockedError as exc:
        status_code = 404 if exc.code == "agent_task_not_found" else 409
        return error_response(status_code, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


# ===== Governance Routes =====

@app.get("/api/v1/projects/{project_id}/governance/identity")
def api_v1_project_governance_identity(project_id: str) -> dict:
    try:
        return get_project_identity(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/governance/identity/init", status_code=201)
def api_v1_init_project_governance_identity(
    project_id: str, payload: GovernanceInitPayload,
) -> dict:
    try:
        return init_project_identities(PRODUCT_ROOT, REPO_ROOT, project_id)
    except IdentityServiceError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/governance/identity/agents/{agent_id}/activate")
def api_v1_activate_governance_agent(project_id: str, agent_id: str) -> dict:
    try:
        return activate_agent(PRODUCT_ROOT, REPO_ROOT, project_id, agent_id)
    except IdentityServiceError as exc:
        return error_response(404, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/governance/identity/agents/{agent_id}/deactivate")
def api_v1_deactivate_governance_agent(project_id: str, agent_id: str) -> dict:
    try:
        return deactivate_agent(PRODUCT_ROOT, REPO_ROOT, project_id, agent_id)
    except IdentityServiceError as exc:
        return error_response(404, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/governance/permissions")
def api_v1_project_governance_permissions(project_id: str) -> dict:
    try:
        return get_project_permissions(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/governance/permissions/init", status_code=201)
def api_v1_init_project_governance_permissions(
    project_id: str, payload: GovernanceInitPayload,
) -> dict:
    try:
        return init_project_permissions(PRODUCT_ROOT, REPO_ROOT, project_id)
    except PermissionServiceError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/governance/permissions/check")
def api_v1_check_governance_permission(
    project_id: str, payload: GovernancePermissionCheckPayload,
) -> dict:
    try:
        return check_permission(
            PRODUCT_ROOT, REPO_ROOT, project_id,
            payload.subject_id, payload.action,
        )
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/governance/permissions/policies/{subject_id}")
def api_v1_update_governance_permission_policy(
    project_id: str, subject_id: str, payload: GovernancePermissionPolicyPayload,
) -> dict:
    try:
        return update_policy(
            PRODUCT_ROOT, REPO_ROOT, project_id,
            subject_id, payload.allow, payload.deny,
        )
    except PermissionServiceError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.put("/api/v1/projects/{project_id}/governance/permissions")
def api_v1_save_governance_permissions(
    project_id: str, payload: GovernancePermissionUpdatePayload,
) -> dict:
    try:
        policies = [p.model_dump() for p in payload.policies]
        return save_project_permissions(PRODUCT_ROOT, REPO_ROOT, project_id, policies)
    except PermissionServiceError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/governance/capabilities")
def api_v1_project_governance_capabilities(project_id: str) -> dict:
    try:
        return get_project_capabilities(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/governance/capabilities/reindex", status_code=201)
def api_v1_reindex_governance_capabilities(
    project_id: str, payload: GovernanceInitPayload,
) -> dict:
    try:
        return reindex_capabilities(PRODUCT_ROOT, REPO_ROOT, project_id)
    except CapabilityRegistryError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.get("/api/v1/projects/{project_id}/governance/costs")
def api_v1_project_governance_costs(project_id: str) -> dict:
    try:
        return get_project_costs(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/governance/costs/start", status_code=201)
def api_v1_start_governance_cost_event(
    project_id: str, payload: GovernanceCostEventPayload,
) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
        project_root = Path(project.get("project_root") or project["root"]).resolve()
        event_id = start_cost_event(
            project_root, project_id,
            payload.workflow_id, payload.task_id,
            payload.actor_id, payload.capability_id,
            payload.event_type,
        )
        return {
            "event_id": event_id,
            "status": "started",
            "project_id": project_id,
        }
    except CostServiceError as exc:
        return error_response(409, exc.code, str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")


@app.post("/api/v1/projects/{project_id}/governance/costs/finish")
def api_v1_finish_governance_cost_event(
    project_id: str, payload: GovernanceCostFinishPayload,
) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
        project_root = Path(project.get("project_root") or project["root"]).resolve()
        return finish_cost_event(
            project_root, payload.event_id, payload.status,
            payload.wall_seconds, payload.provider, payload.model,
            payload.input_tokens, payload.output_tokens, payload.estimated_usd,
        )
    except CostServiceError as exc:
        return error_response(409, exc.code, str(exc))
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


@app.get("/api/v1/projects/{project_id}/formal-submission-package-summary")
def api_v1_project_formal_submission_package_summary(project_id: str) -> dict:
    try:
        return get_project_formal_submission_package_summary(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FormalSubmissionPackageSummaryRequiredError:
        return error_response(
            409,
            "formal_submission_package_summary_required",
            "Run python3 Program/formal_submission_package_summary.py --project-root . before reading the formal submission package summary.",
        )


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


@app.get("/api/v1/projects/{project_id}/verifier-checks")
def api_v1_project_verifier_checks(project_id: str) -> dict:
    try:
        return get_project_verifier_checks(PRODUCT_ROOT, REPO_ROOT, project_id)
    except ExportCandidateRequiredError as exc:
        return error_response(409, "export_candidate_required", str(exc))
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    except FileNotFoundError as exc:
        return error_response(409, "full_run_required", str(exc))
    except ValueError as exc:
        return error_response(409, "result_artifact_required", str(exc))


@app.post("/api/v1/projects/{project_id}/verifier-checks/run", status_code=201)
def api_v1_run_project_verifier_checks(project_id: str) -> dict:
    try:
        return run_project_verifier_checks(PRODUCT_ROOT, REPO_ROOT, project_id)
    except ExportCandidateRequiredError as exc:
        return error_response(409, "export_candidate_required", str(exc))
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


@app.get("/api/v1/projects/{project_id}/runs/active")
def api_v1_project_active_runs(project_id: str) -> dict:
    """Return active run IDs for this project."""
    try:
        get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")

    active_runs = list_active_runs()
    return {"project_id": project_id, "active_runs": active_runs}


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


@app.get("/api/v1/projects/{project_id}/runs/{run_id}/stream")
async def api_v1_run_event_stream(project_id: str, run_id: str):
    """Server-Sent Events endpoint for real-time run updates."""
    try:
        get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")

    q = get_queue(run_id) or ensure_queue(run_id)

    async def event_generator():
        yield (
            "event: connected\n"
            f"data: {json.dumps({'run_id': run_id, 'status': 'listening'}, ensure_ascii=False)}\n\n"
        )

        while True:
            try:
                event = await asyncio.wait_for(
                    asyncio.to_thread(q.get, timeout=1.0),
                    timeout=5.0,
                )
                data = json.dumps(event, ensure_ascii=False)
                yield f"event: {event['type']}\ndata: {data}\n\n"

                if event["type"] in ("run.completed", "run.failed"):
                    break
            except (asyncio.TimeoutError, queue.Empty):
                yield ":keep-alive\n\n"
            except Exception:
                break

        yield f"event: closed\ndata: {json.dumps({'run_id': run_id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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


@app.get("/api/v1/projects/{project_id}/experiments")
def api_v1_project_experiments(project_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    project_root = Path(project.get("project_root", project.get("root", "")))
    experiments = get_experiment_history(project_root)
    return {
        "project_id": project_id,
        "experiments": experiments,
    }


@app.post("/api/v1/projects/{project_id}/experiments/{commit_hash}/revert")
def api_v1_revert_experiment(project_id: str, commit_hash: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    project_root = Path(project.get("project_root", project.get("root", "")))
    result = revert_to_commit(project_root, commit_hash)
    return {
        "project_id": project_id,
        "commit_hash": commit_hash,
        "reverted": result["reverted"],
        "reason": result.get("reason", ""),
        "snapshot": get_project_detail_api_view(PRODUCT_ROOT, REPO_ROOT, project_id),
    }


@app.get("/api/v1/projects/{project_id}/checkpoints")
def api_v1_project_checkpoints(project_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    project_root = Path(project.get("project_root", project.get("root", "")))
    checkpoints = load_checkpoints(project_root)
    return {
        "project_id": project_id,
        "checkpoints": checkpoints,
    }


@app.get("/api/v1/projects/{project_id}/checkpoints/pending")
def api_v1_project_checkpoints_pending(project_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    project_root = Path(project.get("project_root", project.get("root", "")))
    checkpoints = load_checkpoints(project_root)
    pending = [cp for cp in checkpoints if cp.get("status") == "pending"]
    return {
        "project_id": project_id,
        "pending": pending,
    }


@app.post("/api/v1/projects/{project_id}/checkpoints/{checkpoint_id}/resolve")
def api_v1_resolve_checkpoint(
    project_id: str, checkpoint_id: str, payload: ResolveCheckpointPayload
) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError as exc:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    project_root = Path(project.get("project_root", project.get("root", "")))
    result = resolve_checkpoint(
        project_root=project_root,
        checkpoint_id=checkpoint_id,
        status=payload.status,
        user_feedback=payload.user_feedback,
    )
    return {
        "project_id": project_id,
        "checkpoint_id": checkpoint_id,
        "resolved": result.get("resolved", False),
        "checkpoint": result.get("checkpoint"),
        "reason": result.get("reason", ""),
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
@app.get("/react")
@app.get("/react/")
def index() -> FileResponse:
    # `/` now serves the React build (topic-first intake screen).
    # `/react` and `/react/` are kept as backward-compatible aliases.
    index_path = WEB_DIST_ROOT / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=404,
            detail="React build is missing. Run `npm run build` in Product/web-react.",
        )
    return FileResponse(index_path)


@app.get("/legacy")
@app.get("/legacy/")
def legacy_index() -> FileResponse:
    # Old multi-nav workbench kept reachable in case anything depends on it.
    return FileResponse(WEB_ROOT / "index.html")
