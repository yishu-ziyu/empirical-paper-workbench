const state = {
  projects: [],
  selectedProjectId: null,
  selectedProject: null,
  activeRun: null,

  // UI state
  isLoading: false,
  apiError: null,
  apiNotice: null,
  useMock: false,
  activeReport: null,
  isReportModalOpen: false,
  isPromoting: false,

  // V2 page state
  overviewData: null,
  journeyData: null,
  journeyPrimaryAction: null,
  researchQuestionData: null,
  supervisorPlanData: null,
  agentTaskQueueData: null,
  datasetsData: null,
  variableRolesData: null,
  variableRoleCandidatesData: null,
  designSpecData: null,
  runPlanData: null,
  methodWorkflowsData: null,
  designData: null,
  draftsData: null,
  resultsDraftData: null,
  manuscriptCandidatesData: null,
  exportPackageData: null,
  reviewerScorecardData: null,
  verifierChecksData: null,
  agentsData: null,
  selectedAgentId: null,
  agentDetailData: null,
  agentDetailPreviewLoading: false,
  agentDetailPreviewError: null,
  agentDetailPreviewContent: null,
  agentDetailPreviewPath: null,
  provenanceData: null,
  projectRuns: [],
  selectedRunId: null,
  runObservability: null,
  runObservabilityLoading: false,
  resolvingGateId: null,
  resolvingGateAction: null,
  selectedDatasetPath: null,
  bindingExternalDatasetPath: null,
  applyingExternalPreflightId: null,
  applyingExternalPreflightAction: null,
  profilingDatasetImportId: null,
  generatingVariableRoleCandidateId: null,
  reviewingVariableRoleCandidateId: null,
  reviewingVariableRoleCandidateAction: null,
  promotingVariableRoleCandidateId: null,
  pendingVariableRoleCandidateId: null,
  savingVariableRoles: false,
  savingDesignSpec: false,
  savingRunPlan: false,
  reviewingFindingId: null,
  reviewingFindingAction: null,
  reviewingCandidateId: null,
  reviewingCandidateAction: null,
  promotingCandidateId: null,
  exportingCandidateId: null,
  approvingWritebackCandidateId: null,
  approvingWritebackAction: null,
  preflightingDocxCandidateId: null,
  generatingReviewerScorecard: false,
  runningVerifierChecks: false,
  acceptingReviewerTaskSuggestionId: null,
  generatingSupervisorPlan: false,
  reviewingSupervisorPlanAction: null,
  creatingAgentTaskQueue: false,
  reviewingAgentTaskId: null,
  reviewingAgentTaskAction: null,
  draftingLiteratureReviewTaskId: null,
  reviewingDraftLiteratureReviewTaskId: null,
  reviewingDraftLiteratureReviewAction: null,
  recordingCitationEvidenceTaskId: null,
  recordingCitationEvidenceCitationId: null,
  generatingVerifiedLiteraturePackageTaskId: null,
  reviewingVerifiedLiteraturePackageTaskId: null,
  reviewingVerifiedLiteraturePackageAction: null,
  generatingManuscriptCitationPlanTaskId: null,
  reviewingManuscriptCitationPlanTaskId: null,
  reviewingManuscriptCitationPlanAction: null,
  generatingDraftSectionPlanTaskId: null,
  reviewingDraftSectionPlanTaskId: null,
  reviewingDraftSectionPlanAction: null,
  generatingDraftSectionTasksTaskId: null,
  reviewingDraftSectionTasksTaskId: null,
  reviewingDraftSectionTasksAction: null,
  generatingSectionDraftsTaskId: null,
  reviewingSectionDraftsTaskId: null,
  reviewingSectionDraftsAction: null,
  reviewingFormalWritebackPreflightTaskId: null,
  reviewingFormalWritebackPreflightAction: null,
  generatingFormalExportPreflightTaskId: null,
  generatingPdfCandidateExportTaskId: null,
  executingAgentTaskId: null,
  executingAgentTaskBackend: null,

  // SSE state
  sseConnection: {
    eventSource: null,
    connected: false,
    runId: null,
    reconnectAttempts: 0,
  },

  // Agent output panel state
  agentOutput: {
    visible: false,
    currentStage: null,
    currentAgent: null,
    lines: [],
    isTyping: false,
  },

  // Governance state
  governanceIdentityData: null,
  governancePermissionsData: null,
  governanceCapabilitiesData: null,
  governanceCostsData: null,
  initializingGovernanceIdentity: false,
  initializingGovernancePermissions: false,
  reindexingCapabilities: false,
  activatingAgentId: null,
  deactivatingAgentId: null,

  // Agent Execution Monitor state
  executionMonitor: {
    visible: false,
    taskId: null,
    jobId: null,
    status: null,           // "queued" | "running" | "succeeded" | "failed"
    stage: null,            // "backend_selection" | "data_preflight" | "method_execution" | "result_evaluation" | "complete" | "failed"
    currentMessage: "",
    events: [],             // user-facing events
    technicalEvents: [],    // technical log events
    startedAt: null,
    elapsedSeconds: 0,
    result: null,
    error: null,
    pollIntervalId: null,
  },

  researchTopicConfirmed: false,
  researchTopicDraft: "",

  // HITL Checkpoint state
  checkpoint: {
    pollIntervalId: null,
    pending: null,
    resolving: false,
  },
};

const fallbackWorkflowSteps = [
  "question-definition",
  "data-readiness",
  "identification-design",
  "baseline-estimation",
  "robustness",
  "interpretation",
  "manuscript-drafting",
  "submission-prep",
];

const archivePageNotes = {
  journey: {
    title: "研究旅程",
    summary: "从选题到审阅导出的 8 阶段流水线，每阶段需检查点确认。",
  },
  "data-variables": {
    title: "数据与设计",
    summary: "数据集、变量角色和识别设定的前置证据页。",
  },
  "research-design": {
    title: "研究设计细节",
    summary: "模型公式、识别策略、固定效应和威胁清单。",
  },
  "empirical-execution": {
    title: "实证执行",
    summary: "执行计划预检、真实运行轨迹、人工确认点和产物证据。",
  },
  "paper-draft": {
    title: "结果与草稿",
    summary: "结果论断、正文候选和草稿证据绑定。",
  },
  "artifacts-replication": {
    title: "审阅与导出",
    summary: "导出包、评估器检查、复现清单和下一轮反馈。",
  },
  "agent-console": {
    title: "智能体控制台",
    summary: "智能体身份、权限、能力、成本和审计日志。",
  },
  "governance-panel": {
    title: "治理面板",
    summary: "Agent 身份注册、权限矩阵、能力目录与成本追踪的集中管理。",
  },
};

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : { raw: await response.text() };

  if (!response.ok) {
    const message = payload?.error?.message || payload?.detail || JSON.stringify(payload);
    const error = new Error(`${response.status} ${message}`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function mergedArtifacts(project) {
  const resultArtifacts = project?.results_index?.artifacts ?? [];
  const orchestrationArtifacts = project?.latest_orchestration?.manifest?.artifacts?.map((path) => ({
    kind: "orchestration",
    path,
    description: "Multi-agent orchestration artifact",
    exists: true,
  })) ?? [];
  return [...resultArtifacts, ...orchestrationArtifacts];
}

async function loadSelectedProject() {
  if (!state.selectedProjectId) {
    state.selectedProject = null;
    return;
  }
  state.selectedProject = await fetchJson(`/api/v1/projects/${state.selectedProjectId}`);
}

async function refreshProjects() {
  const payload = await fetchJson("/api/v1/projects");
  state.projects = payload.items;
  if (!state.projects.find((project) => project.id === state.selectedProjectId)) {
    state.selectedProjectId = state.projects[0]?.id ?? null;
  }
  await loadSelectedProject();
}

async function selectProject(projectId) {
  state.selectedProjectId = projectId;
  state.activeRun = null;
  state.researchTopicConfirmed = false;
  state.researchTopicDraft = "";
  await loadSelectedProject();
  // Reload current V2 view data after project switch
  const activeNav = document.querySelector(".nav-link.is-active");
  const viewName = activeNav?.dataset.view;
  if (viewName && isV2View(viewName)) {
    await loadV2Data(viewName);
  }
  // Start HITL checkpoint polling for the selected project
  startCheckpointPolling();
}

function mountNav() {
  document.querySelectorAll(".nav-link").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-link").forEach((node) => node.classList.remove("is-active"));
      document.querySelectorAll(".view").forEach((node) => node.classList.remove("is-active"));
      button.classList.add("is-active");
      const viewName = button.dataset.view;
      document.getElementById(`view-${viewName}`).classList.add("is-active");
      document.getElementById("topbar-title").textContent = button.textContent;
      updateArchiveInspector(viewName);

      // V2 view handling
      if (isV2View(viewName)) {
        document.getElementById("journey-bar").style.display = "block";
        void loadV2Data(viewName);
      } else {
        document.getElementById("journey-bar").style.display = "none";
      }
    });
  });

  // Journey bar click navigation
  document.getElementById("journey-bar")?.addEventListener("click", (event) => {
    const stage = event.target.closest(".journey-stage");
    if (!stage) return;
    event.preventDefault();
    const jumpView = stage.dataset.jumpView;
    if (!jumpView) return;

    // Find nav button
    const navButton = document.querySelector(`.nav-link[data-view="${jumpView}"]`);
    if (navButton) {
      navButton.click();
    }
  });
}

function switchView(viewName) {
  const navButton = document.querySelector(`.nav-link[data-view="${viewName}"]`);
  if (navButton instanceof HTMLElement) {
    navButton.click();
  }
}

function mountArchiveInspector() {
  document.querySelectorAll("[data-inspector-view]").forEach((button) => {
    button.addEventListener("click", () => {
      const viewName = button.dataset.inspectorView;
      const navButton = document.querySelector(`.nav-link[data-view="${viewName}"]`);
      if (navButton) {
        navButton.click();
      }
    });
  });
  updateArchiveInspector("journey");
}

function updateArchiveInspector(viewName) {
  const note = archivePageNotes[viewName] || {
    title: "研究档案",
    summary: "当前页面属于本地实证论文档案的一部分。",
  };
  const titleNode = document.getElementById("archive-current-title");
  const summaryNode = document.getElementById("archive-current-summary");
  if (titleNode) titleNode.textContent = note.title;
  if (summaryNode) summaryNode.textContent = note.summary;
  document.querySelectorAll("[data-inspector-view]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.inspectorView === viewName);
  });
}

function mountProjectSelection() {
  document.body.addEventListener("click", (event) => {
    const target = event.target;
    if (target instanceof HTMLElement && target.dataset.selectProjectId) {
      void selectProject(target.dataset.selectProjectId);
    }
  });
}

// --- V2 API (Phase A GET endpoints) ---
const v2api = {
  overview: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/overview`);
    },
  },
  journey: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/journey`);
    },
  },
  datasets: {
    async list(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/datasets`);
    },
    async bindPreflight(projectId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/datasets/external-bind-preflight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async applyPreflight(projectId, preflightId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/datasets/external-bind-preflight/${preflightId}/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async profileImport(projectId, datasetImportId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/datasets/imports/${datasetImportId}/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  variableRoles: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/variable-roles`);
    },
    async save(projectId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/variable-roles`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  variableRoleCandidates: {
    async list(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/variable-role-candidates`);
    },
    async generate(projectId, datasetImportId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/datasets/imports/${datasetImportId}/variable-role-candidates`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async review(projectId, candidateId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/variable-role-candidates/${candidateId}/review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async promote(projectId, candidateId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/variable-role-candidates/${candidateId}/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  design: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/design`);
    },
  },
  designSpec: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/design-spec`);
    },
    async save(projectId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/design-spec`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  runPlan: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/run-plan`);
    },
    async save(projectId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/run-plan`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  methodWorkflows: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/method-workflows`);
    },
  },
  supervisorPlan: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/supervisor-plan`);
    },
    async generate(projectId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/supervisor-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async review(projectId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/supervisor-plan/review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  agentTaskQueue: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue`);
    },
    async create(projectId, payload = {}) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async reviewDispatch(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/dispatch-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async reviewReferenceSeedPackage(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/reference-seed-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async draftLiteratureReview(projectId, taskId) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/draft-literature-review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    },
    async reviewDraftLiteratureReview(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/draft-literature-review-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async recordCitationVerificationEvidence(projectId, taskId, citationTaskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/citation-verification/${citationTaskId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async generateVerifiedLiteraturePackage(projectId, taskId) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/verified-literature-package`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    },
    async reviewVerifiedLiteraturePackage(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/verified-literature-package-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async generateManuscriptCitationPlan(projectId, taskId) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/manuscript-citation-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    },
    async reviewManuscriptCitationPlan(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/manuscript-citation-plan-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async generateDraftSectionPlan(projectId, taskId) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/draft-section-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    },
    async reviewDraftSectionPlan(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/draft-section-plan-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async generateDraftSectionTasks(projectId, taskId) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/draft-section-tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    },
    async reviewDraftSectionTasks(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/draft-section-tasks-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async generateSectionDrafts(projectId, taskId) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/section-drafts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    },
    async reviewSectionDrafts(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/section-drafts-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async reviewFormalWritebackPreflight(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/formal-writeback-preflight-review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async generateFormalExportPreflight(projectId, taskId, payload = {}) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/formal-export-preflight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async generatePdfCandidateExport(projectId, taskId, payload = {}) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/pdf-candidate-export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async selectBackend(projectId, taskId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/select-backend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async execute(projectId, taskId) {
      return fetchJson(`/api/v1/projects/${projectId}/agent-task-queue/tasks/${taskId}/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    },
  },
  researchQuestion: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/research-question/current`);
    },
    async save(projectId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/research-question/current`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  drafts: {
    async list(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/drafts`);
    },
  },
  resultsDraft: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/results-draft`);
    },
    async reviewFinding(projectId, findingId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/results-draft/findings/${encodeURIComponent(findingId)}/review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  manuscriptCandidates: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/manuscript-candidates`);
    },
    async reviewCandidate(projectId, candidateId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/manuscript-candidates/${encodeURIComponent(candidateId)}/review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async promoteCandidate(projectId, candidateId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/manuscript-candidates/${encodeURIComponent(candidateId)}/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async exportPreflightCandidate(projectId, candidateId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/manuscript-candidates/${encodeURIComponent(candidateId)}/export-preflight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  exportPackage: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/export-package`);
    },
    async approveWriteback(projectId, candidateId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/export-package/${encodeURIComponent(candidateId)}/writeback-approval`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async docxPreflight(projectId, candidateId, payload) {
      return fetchJson(`/api/v1/projects/${projectId}/export-package/${encodeURIComponent(candidateId)}/docx-preflight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  reviewerScorecard: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/reviewer-scorecard`);
    },
    async generate(projectId, payload = {}) {
      return fetchJson(`/api/v1/projects/${projectId}/reviewer-scorecard`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
  },
  verifierChecks: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/verifier-checks`);
    },
    async run(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/verifier-checks/run`, {
        method: "POST",
      });
    },
  },
  agents: {
    async list() {
      return fetchJson(`/api/v1/agents`);
    },
    async get(agentId) {
      return fetchJson(`/api/v1/agents/${agentId}/details`);
    },
  },
  provenance: {
    async get(artifactId) {
      return fetchJson(`/api/v1/artifacts/${artifactId}/provenance`);
    },
  },
  runs: {
    async list(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/runs`);
    },
    async active(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/runs/active`);
    },
    async create(projectId, mode, datasetPath = null) {
      const payload = { mode, dataset_path: datasetPath };
      if (!datasetPath) {
        delete payload.dataset_path;
      }
      return fetchJson(`/api/v1/projects/${projectId}/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    },
    async startFull(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/runs/full`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    },
    async observability(projectId, runId) {
      return fetchJson(`/api/v1/projects/${projectId}/runs/${runId}/observability`);
    },
    async stream(projectId, runId, onEvent) {
      const url = `/api/v1/projects/${projectId}/runs/${runId}/stream`;
      const es = new EventSource(url);

      [
        "connected",
        "run.started",
        "stage.start",
        "stage.output",
        "stage.complete",
        "checkpoint.pending",
        "checkpoint.resolved",
        "run.completed",
        "run.failed",
        "closed",
      ].forEach((eventType) => {
        es.addEventListener(eventType, (event) => {
          onEvent({ type: eventType, data: JSON.parse(event.data) });
          if (["run.completed", "run.failed", "closed"].includes(eventType)) {
            es.close();
          }
        });
      });

      es.onerror = (error) => {
        onEvent({ type: "error", error });
        es.close();
      };

      return es;
    },
    async resolveGate(projectId, runId, gateId, action, note) {
      return fetchJson(`/api/v1/projects/${projectId}/runs/${runId}/gates/${gateId}/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, note }),
      });
    },
  },
  governance: {
    identity: {
      async get(projectId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/identity`);
      },
      async init(projectId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/identity/init`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
      },
      async activateAgent(projectId, agentId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/identity/agents/${agentId}/activate`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
      },
      async deactivateAgent(projectId, agentId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/identity/agents/${agentId}/deactivate`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
      },
    },
    permissions: {
      async get(projectId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/permissions`);
      },
      async init(projectId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/permissions/init`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
      },
      async check(projectId, payload) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/permissions/check`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      },
      async save(projectId, policies) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/permissions`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ policies }),
        });
      },
    },
    capabilities: {
      async get(projectId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/capabilities`);
      },
      async reindex(projectId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/capabilities/reindex`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
      },
    },
    costs: {
      async get(projectId) {
        return fetchJson(`/api/v1/projects/${projectId}/governance/costs`);
      },
    },
  },
  checkpoints: {
    async poll(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/checkpoints/pending`);
    },
    async resolve(projectId, checkpointId, action, feedback) {
      return fetchJson(`/api/v1/projects/${projectId}/checkpoints/${checkpointId}/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: action, user_feedback: feedback || "" }),
      });
    },
  },
};

// ============================================================
// V2 Page Rendering
// ============================================================

const V2_VIEWS = [
  "journey", "data-variables", "research-design",
  "empirical-execution", "paper-draft", "artifacts-replication", "agent-console", "governance-panel",
];

function isV2View(viewName) {
  return V2_VIEWS.includes(viewName);
}

function renderEvidenceBadge(meta) {
  if (!meta || !meta.evidence_level) return "";
  const level = meta.evidence_level;
  const label = level === "mock" ? "演示数据" : level === "local_file" ? "本地文件" : level === "local_execution" ? "真实执行" : level;
  return `<span class="evidence-badge ${level}">${label}</span>`;
}

function yesNo(value) {
  return value ? "是" : "否";
}

function reviewStatusLabel(status) {
  const map = {
    approved: "已确认",
    needs_review: "待审阅",
    needs_revision: "需修改",
    rejected: "已拒绝",
  };
  return map[status] || status || "-";
}

function supervisorReviewActionLabel(action) {
  const map = {
    approve: "批准计划",
    needs_revision: "要求修改",
    reject: "驳回计划",
  };
  return map[action] || action || "-";
}

function candidateStatusLabel(status) {
  const map = {
    draft: "草稿",
    reviewed: "已审阅",
    approved: "已确认",
    needs_review: "待审阅",
    needs_revision: "需修改",
    rejected: "已拒绝",
  };
  return map[status] || status || "-";
}

function promotionStatusLabel(status) {
  const map = {
    not_promoted: "尚未进入导出检查",
    ready_for_export: "已进入导出前检查",
  };
  return map[status] || status || "-";
}

function exportStatusLabel(status) {
  const map = {
    not_started: "尚未生成预览",
    preview_ready: "预览已就绪",
  };
  return map[status] || status || "-";
}

function evaluatorStatusLabel(status) {
  const map = {
    passed: "本轮评估通过",
    failed: "本轮评估失败",
    unknown: "等待评估",
  };
  return map[status] || status || "-";
}

function frontierPhaseLabel(phase) {
  const map = {
    objective: "目标",
    baseline: "基线",
    evaluator: "评估器",
    feedback: "反馈",
    next_iteration: "下一轮动作",
  };
  return map[phase] || phase || "-";
}

function provenanceLabel(label) {
  const map = {
    source_draft: "源草稿",
    result_artifact: "结果产物",
    review_decision: "审阅决定",
    candidate_review: "正文候选审阅",
    promotion_state: "导出前检查",
    export_package: "导出包",
  };
  return map[label] || label;
}

function productTermLabel(value) {
  const text = String(value || "");
  const exact = {
    dataset: "数据集",
    Dataset: "数据集",
    variable_roles: "变量角色集",
    VariableRoleSet: "变量角色集",
    research_question: "研究问题",
    ResearchQuestion: "研究问题",
    design_spec: "研究设计方案",
    DesignSpec: "研究设计方案",
    run_plan: "执行计划",
    RunPlan: "执行计划",
    run: "运行",
    Run: "运行",
    results: "结果",
    Results: "结果",
    draft: "草稿",
    Draft: "草稿",
    review_export: "审阅与导出",
    "Review and Export": "审阅与导出",
    agents: "智能体控制台",
    "Agent 控制台": "智能体控制台",
    start_full_run: "启动完整执行",
    START_FULL_RUN: "启动完整执行",
    missing_outcome: "缺少结果变量",
    missing_treatment: "缺少处理变量",
    missing_instrument: "缺少工具变量",
    missing_panel_time: "缺少面板或时间变量",
    missing_running_variable: "缺少断点运行变量",
    missing_covariates: "缺少协变量",
    outcome_required: "缺少结果变量",
    treatment_required: "缺少处理变量",
    time_variable_required: "缺少时间变量",
    treatment_timing_required: "缺少处理时点",
    instrument_required: "缺少工具变量",
    running_variable_required: "缺少断点运行变量",
    covariates_required: "缺少协变量",
    queued: "已排队",
    ready_for_dispatch: "待派工",
    reviewed_for_dispatch: "已通过派工审阅",
    dispatch_review_required: "等待派工审阅",
    blocked: "已阻断",
    needs_revision: "需要修改",
    ready_to_create: "待创建",
    backend_selected: "已选择执行后端",
    verified_literature_package_ready: "等待文献包审阅",
    verified_literature_package_approved: "文献包已批准",
    verified_literature_package_needs_revision: "文献包需修订",
    verified_literature_package_rejected: "文献包已拒绝",
    manuscript_citation_plan_ready: "引用计划待审阅",
    manuscript_citation_plan_approved: "引用计划已批准",
    manuscript_citation_plan_needs_revision: "引用计划需修订",
    manuscript_citation_plan_rejected: "引用计划已拒绝",
    draft_section_plan_ready: "章节计划待审阅",
    draft_section_plan_approved: "章节计划已批准",
    draft_section_plan_needs_revision: "章节计划需修订",
    draft_section_plan_rejected: "章节计划已拒绝",
    draft_section_tasks_ready: "章节任务包待审阅",
    draft_section_tasks_approved: "章节任务包已批准",
    draft_section_tasks_needs_revision: "章节任务包需修订",
    draft_section_tasks_rejected: "章节任务包已拒绝",
    section_drafts_ready: "章节草稿待审阅",
    section_drafts_needs_revision: "章节草稿需修订",
    section_drafts_rejected: "章节草稿已拒绝",
    formal_writeback_preflight_ready: "正式写回预检已准备",
    formal_sections_written: "正式章节已写入",
    formal_export_preflight_ready: "导出预检已通过",
    formal_export_preflight_blocked: "导出预检有阻断项",
    pdf_candidate_exported: "PDF 候选稿已生成",
    formal_writeback_preflight_needs_revision: "正式写回预检需修订",
    formal_writeback_preflight_rejected: "正式写回预检已拒绝",
    review_verified_literature_package: "审阅已核验文献包",
    generate_manuscript_citation_plan: "生成论文引用计划",
    review_manuscript_citation_plan: "审阅论文引用计划",
    review_draft_section_plan: "审阅章节草稿计划",
    review_draft_section_tasks: "审阅章节草稿任务包",
    approved_for_manuscript_citations: "已批准进入引用计划",
    approved_for_draft_sections: "已批准进入章节草稿",
    approved_for_section_tasks: "已批准生成章节任务",
    approved_for_writer_agent: "已批准给 WriterAgent",
    generate_draft_section_plan: "生成章节草稿计划",
    generate_draft_section_tasks: "生成章节草稿任务包",
    generate_section_drafts: "生成章节草稿",
    review_section_drafts: "审阅章节草稿",
    review_formal_writeback_preflight: "审阅正式写回预检",
    prepare_export_preflight: "准备导出预检",
    run_pdf_export_preflight: "运行 PDF 导出预检",
    review_pdf_candidate: "审阅 PDF 候选稿",
    resolve_export_preflight_blockers: "处理导出阻断项",
    revise_section_drafts: "修订章节草稿",
    replace_section_drafts: "替换章节草稿",
    revise_formal_writeback_preflight: "修订正式写回预检",
    approved_for_formal_writeback_preflight: "已批准进入正式写回预检",
    revise_manuscript_citation_plan: "修订论文引用计划",
    replace_manuscript_citation_plan: "替换论文引用计划",
    revise_draft_section_plan: "修订章节草稿计划",
    replace_draft_section_plan: "替换章节草稿计划",
    revise_draft_section_tasks: "修订章节草稿任务包",
    replace_draft_section_tasks: "替换章节草稿任务包",
    revise_verified_literature_package: "修订已核验文献包",
    replace_verified_literature_package: "替换已核验文献包",
    blocked_by_backend_unavailable: "执行后端不可用",
    choose_fallback_backend: "选择后备执行后端",
    statistical_execution: "统计执行",
    draft_code_generation: "脚本草案生成",
    local_execution_artifacts: "本地执行产物",
    script_or_plan_only: "脚本或计划草案",
    local_execution: "本地执行证据",
    local_file: "本地文件证据",
    "Data Agent": "数据智能体",
    "Execution Agent": "执行智能体",
  };
  if (exact[text]) return exact[text];
  return text
    .replaceAll("VariableRoleSet", "变量角色集")
    .replaceAll("ResearchQuestion", "研究问题")
    .replaceAll("DesignSpec", "研究设计方案")
    .replaceAll("RunPlan", "执行计划")
    .replaceAll("Review and Export", "审阅与导出")
    .replaceAll("Agent 控制台", "智能体控制台")
    .replaceAll("Agent", "智能体")
    .replaceAll("Phase A", "A 阶段")
    .replaceAll("full-run", "完整执行");
}

const WORKFLOW_BLOCKER_LABELS = {
  variable_roles_unconfirmed: "变量角色尚未确认",
  design_unconfirmed: "研究设计尚未确认",
  run_plan_missing: "执行计划尚未生成",
};

const WORKFLOW_STAGE_LABELS = {
  completed: "已完成",
  in_progress: "进行中",
  requires_confirmation: "待确认",
  blocked: "阻塞",
  not_started: "未开始",
};

function getWorkflowContract() {
  return state.overviewData?.workflow_contract || null;
}

function workflowStageLabel(status) {
  return WORKFLOW_STAGE_LABELS[status] || status || "-";
}

function renderWorkflowContract(contract) {
  const actionContainer = document.getElementById("product-next-action-body");
  const spineContainer = document.getElementById("workflow-spine");
  if (!actionContainer || !spineContainer) return;

  if (!contract) {
    actionContainer.innerHTML = "<p class='muted'>正在读取工作流契约...</p>";
    spineContainer.innerHTML = "";
    return;
  }

  const action = contract.next_action || {};
  actionContainer.innerHTML = `
    <div class="next-decision-card">
      <div>
        <span class="eyebrow">${escapeHtml(productTermLabel(action.id || "next_action"))}</span>
        <h4>${escapeHtml(productTermLabel(action.label || "等待下一步"))}</h4>
        <p class="muted">${escapeHtml(productTermLabel(action.reason || "系统正在判断下一步研究决策。"))}</p>
      </div>
      <button class="primary-button" data-open-design-action data-next-action="${escapeHtml(action.id || "confirm_variable_roles")}">
        打开数据与设计
      </button>
    </div>
  `;

  const stages = contract.canonical_stages || [];
  spineContainer.innerHTML = stages.map((stage, index) => `
    <article class="workflow-spine-step is-${escapeHtml(stage.status || "not_started")}">
      <span class="workflow-spine-index">${index + 1}</span>
      <strong>${escapeHtml(productTermLabel(stage.name || stage.id))}</strong>
      <span>${escapeHtml(workflowStageLabel(stage.status))}</span>
    </article>
  `).join("");
  renderIntelligenceLayer(contract.intelligence_layer);
}

function renderIntelligenceLayer(intelligence_layer) {
  const container = document.getElementById("llm-supervisor-body");
  if (!container) return;
  if (!intelligence_layer) {
    container.innerHTML = "<p class='muted'>尚未读取智能中控状态。</p>";
    return;
  }
  const provider = intelligence_layer.provider || {};
  const dispatchPlan = intelligence_layer.dispatch_plan || [];
  const blockers = intelligence_layer.blockers || [];
  const blockerLabel = blockers.length ? `${blockers.length} 项阻塞` : "可进入派工";
  container.innerHTML = `
    <div class="llm-supervisor-card is-${escapeHtml(intelligence_layer.status || "blocked")}">
      <div>
        <span class="meta-label">本地 Codex Supervisor</span>
        <strong>${escapeHtml(intelligence_layer.status === "ready" ? "已启用" : "未启用")}</strong>
        <p class="muted">负责计划、派工、审阅和失败恢复；不会直接改写已确认研究状态。</p>
      </div>
      ${renderEvidenceBadge({ evidence_level: intelligence_layer.evidence_level || "local_file" })}
      <div class="decision-signal-row">
        <span>${escapeHtml(blockerLabel)}</span>
        <span>派工角色：${dispatchPlan.length}</span>
      </div>
    </div>
    <details class="progressive-disclosure llm-supervisor-details" data-disclosure="intelligence-progressive-disclosure">
      <summary>查看中控详情</summary>
      <div class="disclosure-panel">
        <p class="muted">${escapeHtml(intelligence_layer.boundary || "Supervisor 负责计划、派工、审阅和失败恢复。")}</p>
        <div class="llm-provider-grid">
          <div><span class="meta-label">Provider</span><strong>${escapeHtml(provider.provider || "local_codex")}</strong></div>
          <div><span class="meta-label">可用</span><strong>${provider.available ? "是" : "否"}</strong></div>
          <div><span class="meta-label">允许执行</span><strong>${provider.execution_enabled ? "是" : "否"}</strong></div>
          <div><span class="meta-label">版本</span><strong>${escapeHtml(provider.version || "-")}</strong></div>
        </div>
        ${blockers.length ? `<p class="muted">阻塞：${escapeHtml(blockers.map(productTermLabel).join("、"))}</p>` : "<p class='muted'>本地大模型中控可进入真实派工。</p>"}
        <div class="llm-dispatch-plan">
          <span class="meta-label">派工计划</span>
          ${dispatchPlan.map((item) => `
            <article class="llm-dispatch-item">
              <strong>${escapeHtml(item.role || item.agent_id)}</strong>
              <p class="muted">${escapeHtml(item.responsibility || "-")}</p>
            </article>
          `).join("") || "<p class='muted'>尚未生成派工计划。</p>"}
        </div>
      </div>
    </details>
  `;
}

function renderSupervisorPlanSkillReview(plan) {
  const recommendedSkills = Array.isArray(plan.recommended_internal_skills) ? plan.recommended_internal_skills : [];
  const reviewContract = plan.skill_review_contract || {};
  const applicabilityReason = plan.applicability_reason || {};
  const missingEvidence = Array.isArray(plan.missing_evidence) ? plan.missing_evidence : [];

  if (!recommendedSkills.length && !Object.keys(reviewContract).length && !missingEvidence.length) {
    return "";
  }

  const humanReviewStatus = plan.skill_review_status || (reviewContract.human_review_required ? "needs_human_skill_review" : "not_required");
  return `
    <section class="supervisor-plan-skill-review">
      <div class="supervisor-plan-skill-review-head">
        <div>
          <span class="meta-label">人工审阅状态</span>
          <h4>推荐 Skill</h4>
          <p class="muted">${escapeHtml(productTermLabel(humanReviewStatus))}</p>
        </div>
        <span class="pill">${reviewContract.human_review_required ? "需要审阅" : "已满足"}</span>
      </div>
      <div class="supervisor-plan-skill-list">
        ${recommendedSkills.length ? recommendedSkills.map((skill) => {
          const skillId = skill.skill_id || "";
          const reason = applicabilityReason[skillId]
            || skill.semantic_selection_reason
            || skill.matched_reason
            || "等待 Supervisor 补充选择理由。";
          const skillMissingEvidence = missingEvidence.filter((item) => item.skill_id === skillId);
          const sourceNames = Array.isArray(skill.external_source_names) ? skill.external_source_names : [];
          return `
            <article class="supervisor-plan-skill-item">
              <div>
                <span class="meta-label">${escapeHtml(skillId)}</span>
                <strong>${escapeHtml(skill.name || skillId || "未命名 Skill")}</strong>
              </div>
              <div>
                <span class="meta-label">选择理由</span>
                <p>${escapeHtml(reason)}</p>
              </div>
              <div>
                <span class="meta-label">缺失证据</span>
                ${skillMissingEvidence.length ? `
                  <ul>
                    ${skillMissingEvidence.map((item) => `
                      <li>${escapeHtml(item.required_state || item.description || item.reason || "待补齐证据")}</li>
                    `).join("")}
                  </ul>
                ` : "<p class='muted'>当前没有额外缺失项。</p>"}
              </div>
              <div>
                <span class="meta-label">Skill 来源</span>
                <p class="muted">${escapeHtml(sourceNames.length ? sourceNames.join("、") : (skill.selection_source || "internal_registry"))}</p>
              </div>
            </article>
          `;
        }).join("") : "<p class='muted'>当前计划没有推荐内部 Skill。</p>"}
      </div>
      <div class="supervisor-plan-skill-contract">
        <span class="meta-label">审阅契约</span>
        <p class="muted">${escapeHtml(reviewContract.auto_mode_boundary || "Auto Mode 只能生成草案层建议，正式层仍需人工确认。")}</p>
      </div>
    </section>
  `;
}

function renderReferenceChainPolicy(policy, options = {}) {
  if (!policy || typeof policy !== "object") return "";
  const title = options.title || "引用链路策略";
  const className = options.className || "";
  const sourcePriority = Array.isArray(policy.source_priority) ? policy.source_priority : [];
  const sources = (Array.isArray(policy.sources) ? policy.sources : [])
    .map((source) => (typeof source === "string" ? { id: source, label: source } : source))
    .filter(Boolean);
  const sourceById = new Map(
    sources.map((source) => [source.id || source.source_id || source.label, source]),
  );
  const orderedSources = sourcePriority.length
    ? sourcePriority.map((sourceId) => sourceById.get(sourceId) || { id: sourceId, label: sourceId })
    : sources;
  const requiredArtifacts = Array.isArray(policy.required_artifacts) ? policy.required_artifacts : [];
  const statusLabel = productTermLabel(policy.status || "needs_review");
  const sourceLimit = `深度 ${escapeHtml(String(policy.max_depth || 2))} · ${escapeHtml(String(policy.max_iterations || 5))} 轮`;
  const writebackGate = policy.formal_writeback_gate || "review_literature_seed_package";
  const draftPolicy = policy.draft_citation_policy || "候选引用只能进入草案；正式写回前需要人工审阅来源、DOI、作者年份和引用位置。";
  const formalLayerNote = policy.writes_formal_layer
    ? "会触及正式层，必须先完成正式写回门。"
    : "不会静默写入正式层。";

  return `
    <section class="reference-chain-policy ${escapeHtml(className)}">
      <div class="reference-chain-policy__head">
        <div>
          <span class="meta-label">${escapeHtml(title)}</span>
          <strong>${escapeHtml(statusLabel)}</strong>
          <p class="muted">候选引用进入草案，正式层写回前必须通过 ${escapeHtml(writebackGate)}。</p>
        </div>
        <span class="pill">${sourceLimit}</span>
      </div>
      <div class="reference-chain-policy__grid">
        <div>
          <span class="meta-label">来源优先级</span>
          ${orderedSources.length ? `
            <ol>
              ${orderedSources.map((source) => `
                <li>
                  <strong>${escapeHtml(source.label || source.name || source.id || "未命名来源")}</strong>
                  <span class="muted">${escapeHtml(source.reason || source.boundary || source.access_mode || "")}</span>
                </li>
              `).join("")}
            </ol>
          ` : "<p class='muted'>等待 Supervisor 指定来源。</p>"}
        </div>
        <div>
          <span class="meta-label">待生成证据</span>
          ${requiredArtifacts.length ? `
            <ul>
              ${requiredArtifacts.map((artifact) => `<li>${escapeHtml(artifact.label || artifact.id || String(artifact))}</li>`).join("")}
            </ul>
          ` : "<p class='muted'>等待文献 Agent 生成引用种子包。</p>"}
        </div>
        <div>
          <span class="meta-label">草案引用规则</span>
          <p>${escapeHtml(draftPolicy)}</p>
          <p class="muted">候选引用需要标记为 candidate / verified / rejected。</p>
        </div>
        <div>
          <span class="meta-label">正式写回门</span>
          <p>${escapeHtml(writebackGate)}</p>
          <p class="muted">${escapeHtml(formalLayerNote)}</p>
        </div>
      </div>
    </section>
  `;
}

function renderSupervisorPlan() {
  const container = document.getElementById("supervisor-plan-body");
  if (!container) return;
  const plan = state.supervisorPlanData?.supervisor_plan || null;
  if (!plan) {
    container.innerHTML = "<p class='muted'>正在读取 SupervisorPlan...</p>";
    return;
  }
  const hasPlan = plan.status && plan.status !== "empty";
  const risks = plan.risks || [];
  const evidence = plan.evidence_requirements || [];
  const dispatch = plan.subagent_dispatch || [];
  const stagePlan = plan.stage_plan || [];
  const inputQuestion = plan.input_research_question || {};
  const boundQuestion = inputQuestion.question || state.researchQuestionData?.research_question?.question || "";
  const visibleNextAction = plan.next_action?.label || (hasPlan ? "审阅 SupervisorPlan" : "生成 SupervisorPlan");
  const humanReview = plan.human_review || null;
  const humanReviewLabel = supervisorHumanReviewLabel(plan);
  const reviewDisabled = Boolean(state.reviewingSupervisorPlanAction);
  container.innerHTML = `
    <article class="supervisor-plan-card is-${escapeHtml(plan.status || "empty")}">
      <div class="supervisor-plan-summary">
        <div>
          <span class="meta-label">本地 Codex SupervisorPlan</span>
          <h4>${escapeHtml(hasPlan ? reviewStatusLabel(plan.status) : "尚未生成")}</h4>
          <p class="muted">${escapeHtml(hasPlan ? plan.objective : "生成后会进入人工确认，不会直接改写变量角色、研究设计或执行计划。")}</p>
          ${boundQuestion ? `<p class="muted">绑定选题：${escapeHtml(boundQuestion)}</p>` : ""}
        </div>
        ${renderEvidenceBadge({ evidence_level: plan.evidence_level || "local_file" })}
      </div>
      <div class="supervisor-plan-actions">
        <button class="primary-button" data-supervisor-plan-generate ${state.generatingSupervisorPlan ? "disabled" : ""}>
          ${state.generatingSupervisorPlan ? "生成中..." : "生成 SupervisorPlan"}
        </button>
        <span class="muted">人工确认后，才允许进入真实子 Agent 派工。</span>
      </div>
      ${hasPlan ? `
        <div class="supervisor-plan-review-bar">
          <div>
            <span class="meta-label">人工审批</span>
            <strong>${escapeHtml(humanReviewLabel)}</strong>
            <p class="muted">只有批准后的计划才能进入任务队列；要求修改或驳回会阻止派工。</p>
          </div>
          <div class="supervisor-plan-review-actions">
            ${["approve", "needs_revision", "reject"].map((action) => `
              <button
                class="${action === "approve" ? "primary-button" : "secondary-button"}"
                data-supervisor-plan-review-action="${escapeHtml(action)}"
                ${reviewDisabled ? "disabled" : ""}
              >
                ${state.reviewingSupervisorPlanAction === action ? "写回中..." : escapeHtml(supervisorReviewActionLabel(action))}
              </button>
            `).join("")}
          </div>
        </div>
      ` : ""}
      <div class="decision-signal-row">
        <span>下一步：${escapeHtml(visibleNextAction)}</span>
        <span>${hasPlan ? `风险 ${risks.length} 项` : "等待生成计划"}</span>
        <span>${hasPlan ? (plan.can_dispatch ? "可进入任务队列" : "不可派工") : "未生成"}</span>
      </div>
      <details class="progressive-disclosure supervisor-plan-details" data-disclosure="supervisor-plan-progressive-disclosure">
        <summary>查看计划详情</summary>
        <div class="disclosure-panel">
          <div class="supervisor-plan-ledger">
            <div><span class="meta-label">下一步</span><strong>${escapeHtml(visibleNextAction)}</strong></div>
            <div><span class="meta-label">版本</span><strong>${escapeHtml(String(plan.version ?? 0))}</strong></div>
            <div><span class="meta-label">TopicSession</span><strong>${escapeHtml(inputQuestion.topic_session_id || "-")}</strong></div>
            <div><span class="meta-label">ResearchQuestion 版本</span><strong>${escapeHtml(String(inputQuestion.version ?? "-"))}</strong></div>
            <div><span class="meta-label">边界</span><strong>${escapeHtml(plan.write_boundary || "不可直接改写已确认研究状态")}</strong></div>
          </div>
          ${renderSupervisorPlanSkillReview(plan)}
          ${renderReferenceChainPolicy(plan.reference_chain_policy, { title: "引用链路策略", className: "supervisor-plan-reference-policy" })}
          ${hasPlan ? `
            <div class="supervisor-plan-grid">
              ${renderSupervisorPlanColumn("阶段计划", stagePlan, "goal")}
              ${renderSupervisorPlanColumn("子 Agent 分工", dispatch, "task")}
              ${renderSupervisorPlanColumn("证据要求", evidence, "requirement")}
              ${renderSupervisorPlanColumn("风险", risks, "description")}
            </div>
          ` : "<p class='muted'>生成后会在这里显示阶段计划、子 Agent 分工、证据要求和风险。</p>"}
        </div>
      </details>
    </article>
  `;
}

function supervisorHumanReviewLabel(plan) {
  const humanReview = plan?.human_review || null;
  if (humanReview?.action) {
    return supervisorReviewActionLabel(humanReview.action);
  }
  if (plan.status === "approved") {
    return "已批准";
  }
  if (plan.status === "needs_revision") {
    return "要求修改";
  }
  if (plan.status === "rejected") {
    return "已驳回";
  }
  return "尚未审批";
}

function renderSupervisorPlanColumn(title, items, detailKey) {
  return `
    <section class="supervisor-plan-column">
      <h4>${escapeHtml(title)}</h4>
      ${items.length ? items.map((item) => `
        <div class="supervisor-plan-item">
          <strong>${escapeHtml(item.stage || item.agent_id || item.id || item.role || title)}</strong>
          <p class="muted">${escapeHtml(item[detailKey] || item.goal || item.task || item.requirement || item.description || "")}</p>
        </div>
      `).join("") : "<p class='muted'>尚无内容。</p>"}
    </section>
  `;
}

function renderAgentTaskPrimaryAction(action, options = {}) {
  if (!action || !action.id) return "";
  const title = options.title || "当前建议动作";
  const reasonLabel = options.reasonLabel || "为什么现在做这一步";
  const formalLayerNote = action.writes_formal_layer
    ? "会触及正式层，必须人工确认"
    : "只进入草案层或审阅层";
  return `
    <div class="agent-task-primary-action">
      <div>
        <span class="meta-label">${escapeHtml(title)}</span>
        <strong>${escapeHtml(action.label || productTermLabel(action.id))}</strong>
        <p class="muted"><span>${escapeHtml(reasonLabel)}：</span>${escapeHtml(action.reason || "系统正在根据任务状态判断下一步。")}</p>
      </div>
      <div class="agent-task-primary-action__meta">
        ${action.task_title ? `<span class="pill">${escapeHtml(action.task_title)}</span>` : ""}
        <span class="pill">${escapeHtml(action.enabled === false ? "暂不可执行" : "可继续")}</span>
        <span class="pill">${escapeHtml(formalLayerNote)}</span>
      </div>
    </div>
  `;
}

function renderAgentTaskQueue() {
  const container = document.getElementById("agent-task-queue-body");
  if (!container) return;
  const queue = state.agentTaskQueueData?.agent_task_queue || null;
  const plan = state.supervisorPlanData?.supervisor_plan || null;
  if (!queue) {
    container.innerHTML = "<p class='muted'>正在读取 Agent 任务队列...</p>";
    return;
  }
  const hasQueue = queue.status === "ready_for_dispatch" && Array.isArray(queue.tasks) && queue.tasks.length > 0;
  const canCreate = Boolean(queue.can_create || (plan?.status === "approved" && plan?.can_dispatch));
  const summary = queue.summary || {};
  const blockers = queue.blockers || [];
  const ownerAgents = summary.owner_agents || [];
  const uiContract = queue.ui_contract || {};
  const detailsPolicy = uiContract.details_collapsed_by_default ? "详情默认折叠" : "详情默认展开";
  container.innerHTML = `
    <article class="agent-task-queue-card is-${escapeHtml(queue.status || "empty")}">
      <div class="agent-task-queue-summary">
        <div>
          <span class="meta-label">任务队列</span>
          <h4>${escapeHtml(hasQueue ? "已生成派工草案" : "尚未创建任务队列")}</h4>
          <p class="muted">${escapeHtml(hasQueue ? "默认只显示任务摘要和阻塞，输入证据、输出要求和审计日志按需展开。" : "批准 SupervisorPlan 后，可以创建派工草案；不会自动执行或改写研究状态。")}</p>
        </div>
        ${renderEvidenceBadge({ evidence_level: queue.evidence_level || "local_file" })}
      </div>
      <div class="agent-task-queue-ledger">
        <div><span class="meta-label">任务总数</span><strong>${escapeHtml(String(summary.total_tasks || 0))}</strong></div>
        <div><span class="meta-label">排队</span><strong>${escapeHtml(String(summary.queued_count || 0))}</strong></div>
        <div><span class="meta-label">阻塞项</span><strong>${escapeHtml(String(summary.blocked_count || blockers.length || 0))}</strong></div>
        <div><span class="meta-label">已审阅</span><strong>${escapeHtml(String(summary.dispatch_reviewed_count || 0))}</strong></div>
        <div><span class="meta-label">负责人 Agent</span><strong>${escapeHtml(ownerAgents.length ? ownerAgents.join("、") : "-")}</strong></div>
      </div>
      ${renderAgentTaskPrimaryAction(queue.primary_action)}
      ${hasQueue ? `
        <div class="agent-task-list">
          ${(queue.tasks || []).map(renderAgentTaskQueueItem).join("")}
        </div>
      ` : `
        <div class="agent-task-queue-empty">
          ${blockers.length ? blockers.map((blocker) => `
            <div class="agent-task-blocker">
              <strong>${escapeHtml(blocker.label || blocker.code || "等待前置条件")}</strong>
              <p class="muted">${escapeHtml(blocker.description || "")}</p>
            </div>
          `).join("") : "<p class='muted'>SupervisorPlan 已批准，可以创建队列。</p>"}
          <button class="primary-button" data-agent-task-create-action ${!canCreate || state.creatingAgentTaskQueue ? "disabled" : ""}>
            ${state.creatingAgentTaskQueue ? "创建中..." : "创建 Agent 任务队列"}
          </button>
          <p class="muted">这一步只创建可审阅派工草案，不会自动执行或改写研究状态。</p>
        </div>
      `}
      <div class="decision-signal-row">
        <span>来源：${escapeHtml(queue.source_supervisor_plan?.path || "state/product/supervisor_plan.json")}</span>
        <span>${escapeHtml(detailsPolicy)}</span>
        <span>下一步：${escapeHtml(queue.primary_action?.label || queue.next_action?.label || "等待人工检查")}</span>
      </div>
    </article>
  `;

  // After DOM update, check if any task should show execution monitor
  if (hasQueue && Array.isArray(queue.tasks)) {
    queue.tasks.forEach((task) => maybeStartExecutionMonitorForTask(task));
  }
}

function backendOptionLabel(backendId) {
  const map = {
    statspai: "StatsPAI",
    python_ols_adapter: "Python OLS",
    stata_mcp: "StataMCP",
    codex: "Codex",
  };
  return map[backendId] || backendId || "-";
}

function backendDefaultSelectionReason(backendId) {
  const map = {
    statspai: "选择 StatsPAI，因为它适合本地统计执行、结构化结果和可追溯产物。",
    python_ols_adapter: "选择 Python OLS，因为当前任务可以用本地 Python 快速生成基准回归草案和结果证据。",
    stata_mcp: "选择 StataMCP，因为当前任务需要 Stata 生态命令或复现既有 do-file 流程。",
    codex: "选择 Codex，因为当前任务更适合生成脚本草案、诊断建议或人工审阅材料。",
  };
  return map[backendId] || "";
}

function backendDefaultFallbackIds(backendId) {
  const map = {
    statspai: ["python_ols_adapter", "stata_mcp", "codex"],
    python_ols_adapter: ["statspai", "codex"],
    stata_mcp: ["statspai", "python_ols_adapter", "codex"],
    codex: ["statspai", "python_ols_adapter"],
  };
  return map[backendId] || [];
}

function backendDefaultExecutionBoundary(backendId) {
  if (!backendId) return {};
  if (backendId === "codex") {
    return {
      kind: "draft_code_generation",
      output_boundary: "script_or_plan_only",
      can_enter_formal_layer_automatically: false,
    };
  }
  return {
    kind: "statistical_execution",
    output_boundary: "local_execution_artifacts",
    can_enter_formal_layer_automatically: false,
  };
}

function renderAgentTaskBackendDetails(task) {
  const selectedBackend = task.selected_backend || {};
  const blocker = task.backend_blocker || {};
  const backendId = selectedBackend.id || blocker.backend_id || task.execution_backend_id || "";
  const executionBoundary = selectedBackend.execution_boundary || backendDefaultExecutionBoundary(backendId);
  const fallbackBackendIds = Array.isArray(selectedBackend.fallback_backend_ids)
    ? selectedBackend.fallback_backend_ids
    : (Array.isArray(blocker.fallback_backend_ids) ? blocker.fallback_backend_ids : backendDefaultFallbackIds(backendId));
  const selectionReason = selectedBackend.selection_reason || blocker.message || backendDefaultSelectionReason(backendId);
  const hasDetails = Boolean(
    selectionReason
    || fallbackBackendIds.length
    || Object.keys(executionBoundary).length
    || backendId
  );
  if (!hasDetails) return "";

  const formalBoundary = executionBoundary.can_enter_formal_layer_automatically
    ? "允许进入正式层"
    : "不会自动进入正式层，正式写回前需要人工审阅。";
  const outputBoundary = [
    productTermLabel(executionBoundary.kind || ""),
    productTermLabel(executionBoundary.output_boundary || ""),
  ].filter(Boolean).join(" · ");

  return `
    <div class="agent-task-backend-details">
      <div>
        <span class="meta-label">为什么选这个后端</span>
        <p>${escapeHtml(selectionReason || "等待后端选择后显示。")}</p>
      </div>
      <div>
        <span class="meta-label">失败后备选</span>
        ${fallbackBackendIds.length ? `
          <ul>
            ${fallbackBackendIds.map((backendId) => `<li>${escapeHtml(backendOptionLabel(backendId))}</li>`).join("")}
          </ul>
        ` : "<p class='muted'>暂无可用后备后端。</p>"}
      </div>
      <div>
        <span class="meta-label">执行产物范围</span>
        <p>${escapeHtml(outputBoundary || productTermLabel(selectedBackend.evidence_level || blocker.availability_status || "等待执行边界"))}</p>
      </div>
      <div>
        <span class="meta-label">正式层边界</span>
        <p>${escapeHtml(formalBoundary)}</p>
      </div>
    </div>
  `;
}

function firstMethodExecutionResult(executionResult) {
  const methods = executionResult?.method_execution?.methods;
  if (!Array.isArray(methods) || !methods.length) return {};
  return methods.find((method) => method.task_id) || methods[0] || {};
}

function renderReferenceSeedPackageResultReview(executionResult, task = {}) {
  if (executionResult?.execution_kind !== "reference_chain_seed_package") return "";
  const review = executionResult.result_review || {};
  const seedReview = task.reference_seed_review || {};
  const reviewFocus = Array.isArray(review.review_focus) ? review.review_focus : [];
  const candidateQueryCount = Number.isFinite(Number(review.candidate_query_count))
    ? Number(review.candidate_query_count)
    : 0;
  const isReviewing = state.reviewingAgentTaskId === task.id;
  const isApprovedForDraft = seedReview.status === "approved_for_draft";
  const isDrafting = state.draftingLiteratureReviewTaskId === task.id;
  return `
    <div class="agent-task-reference-seed-result">
      <div class="agent-task-reference-seed-result__head">
        <div>
          <span class="meta-label">结果审阅对象</span>
          <strong>${escapeHtml(review.title || "候选来源种子包")}</strong>
          <p class="muted">候选检索式 ${escapeHtml(String(candidateQueryCount))} 条 · ${escapeHtml(review.reference_state || "candidate")}</p>
        </div>
        <span class="pill">${escapeHtml(productTermLabel(review.review_gate || "review_literature_seed_package"))}</span>
      </div>
      <div class="agent-task-reference-seed-result__grid">
        <div>
          <span class="meta-label">种子包文件</span>
          <code>${escapeHtml(review.artifact_path || executionResult.artifact_path || "等待生成 reference_chain_seed_package.json")}</code>
        </div>
        <div>
          <span class="meta-label">下一步审阅门</span>
          <p>${escapeHtml(productTermLabel(review.next_action || "review_literature_seed_package"))}</p>
        </div>
        <div>
          <span class="meta-label">候选检索式</span>
          ${reviewFocus.length ? `
            <ul>
              ${reviewFocus.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
            </ul>
          ` : "<p class='muted'>检查候选来源、检索式和引用状态。</p>"}
        </div>
        <div>
          <span class="meta-label">正式层边界</span>
          <p>${escapeHtml(review.formal_layer_boundary || "不宣称已验证引用；人工审阅前不能写入正式层。")}</p>
          <p class="muted">${review.claims_verified_citations ? "已声明验证引用" : "不宣称已验证引用"}</p>
        </div>
      </div>
      <div class="agent-task-reference-seed-result__actions">
        <div>
          <strong>人工审阅</strong>
          <p class="muted">${seedReview.status ? `已记录：${escapeHtml(productTermLabel(seedReview.status))}` : "批准后只进入草稿综述；不会写入正式层。"}</p>
        </div>
        <div class="agent-task-reference-seed-result__buttons">
          ${isApprovedForDraft ? `
            <button class="primary-button" data-draft-literature-review-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isDrafting ? "disabled" : ""}>
              ${isDrafting ? "生成中..." : "生成草稿层文献综述"}
            </button>
          ` : ""}
          <button class="secondary-button" data-reference-seed-review-action="approve_for_draft" data-agent-task-id="${escapeHtml(task.id || "")}" ${isReviewing ? "disabled" : ""}>
            ${isReviewing && state.reviewingAgentTaskAction === "approve_for_draft" ? "处理中..." : "进入草稿综述"}
          </button>
          <button class="secondary-button" data-reference-seed-review-action="needs_revision" data-agent-task-id="${escapeHtml(task.id || "")}" ${isReviewing ? "disabled" : ""}>
            要求修订
          </button>
          <button class="secondary-button" data-reference-seed-review-action="reject" data-agent-task-id="${escapeHtml(task.id || "")}" ${isReviewing ? "disabled" : ""}>
            拒绝种子包
          </button>
        </div>
      </div>
    </div>
  `;
}

function renderDraftLiteratureReview(task = {}) {
  const draft = task.draft_literature_review || {};
  if (draft.status !== "draft_ready") return "";
  const review = task.draft_literature_review_review || {};
  const isReviewingDraft = state.reviewingDraftLiteratureReviewTaskId === task.id;
  return `
    <div class="agent-task-literature-draft">
      <div>
        <span class="meta-label">草稿层文献综述</span>
        <strong>${escapeHtml(draft.next_action_label || "审阅草稿综述")}</strong>
        <p class="muted">来自候选来源种子包 · ${escapeHtml(draft.citation_state || "candidate")} · 不写入正式层</p>
      </div>
      <div class="agent-task-literature-draft__grid">
        <div>
          <span class="meta-label">草稿文件</span>
          <code>${escapeHtml(draft.artifact_path || "等待生成 draft_literature_review.md")}</code>
        </div>
        <div>
          <span class="meta-label">来源文件</span>
          <code>${escapeHtml(draft.source_artifact_path || "-")}</code>
        </div>
        <div>
          <span class="meta-label">下一步</span>
          <p>${escapeHtml(productTermLabel(draft.next_action || "review_draft_literature_review"))}</p>
        </div>
        <div>
          <span class="meta-label">正式层边界</span>
          <p>${escapeHtml(draft.limitations || "引用仍需核验，不能写入正式层。")}</p>
        </div>
      </div>
      <div class="agent-task-literature-draft__actions">
        <div>
          <strong>草稿审阅</strong>
          <p class="muted">${review.status ? `已记录：${escapeHtml(productTermLabel(review.status))}` : "批准后只打开引用核验任务；不宣称引用已验证。"}</p>
        </div>
        <div class="agent-task-literature-draft__buttons">
          ${["approve_for_citation_verification", "needs_revision", "reject"].map((action) => `
            <button class="${action === "approve_for_citation_verification" ? "primary-button" : "secondary-button"}" data-draft-literature-review-review-action="${action}" data-agent-task-id="${escapeHtml(task.id || "")}" ${isReviewingDraft ? "disabled" : ""}>
              ${isReviewingDraft && state.reviewingDraftLiteratureReviewAction === action ? "写回中..." : escapeHtml(draftLiteratureReviewReviewActionLabel(action))}
            </button>
          `).join("")}
        </div>
      </div>
    </div>
  `;
}

function renderCitationVerificationTasks(task = {}) {
  const citationTasks = Array.isArray(task.citation_verification_tasks)
    ? task.citation_verification_tasks
    : [];
  if (!citationTasks.length) return "";
  const pendingCount = citationTasks.filter((item) => item.status === "pending").length;
  const verifiedCount = citationTasks.filter((item) => item.status === "verified").length;
  const canGeneratePackage = task.status === "citation_verification_complete";
  const isGeneratingPackage = state.generatingVerifiedLiteraturePackageTaskId === task.id;
  return `
    <div class="agent-task-citation-verification">
      <div class="agent-task-citation-verification__head">
        <div>
          <span class="meta-label">引用核验任务</span>
          <strong>${escapeHtml(String(citationTasks.length))} 条候选来源待核验</strong>
          <p class="muted">已核验 ${escapeHtml(String(verifiedCount))} 条 · 等待补证 ${escapeHtml(String(pendingCount))} 条 · 不写入正式层</p>
        </div>
        <span class="pill">${escapeHtml(productTermLabel(task.next_action || "verify_citations"))}</span>
      </div>
      <div class="agent-task-citation-verification__list">
        ${citationTasks.slice(0, 6).map((item) => `
          <article>
            <span class="meta-label">${escapeHtml(item.source_label || item.source_id || "候选来源")}</span>
            <strong>${escapeHtml(productTermLabel(item.status || "pending"))}</strong>
            <p>${escapeHtml(item.query || "等待补充检索式")}</p>
            <p class="muted">需要核验：${escapeHtml((item.required_checks || []).join(" / "))}</p>
            <div class="agent-task-citation-evidence">
              <div>
                <strong>${item.status === "verified" ? "已核验证据" : "等待补证"}</strong>
                <p class="muted">${escapeHtml(item.evidence_record?.doi_or_stable_url || "录入作者、年份、题名、来源和 DOI 或稳定链接后才算完成。")}</p>
              </div>
              ${item.status === "verified" ? "" : `
                <textarea data-citation-evidence-json data-agent-task-id="${escapeHtml(task.id || "")}" data-citation-task-id="${escapeHtml(item.id || "")}" rows="5">${escapeHtml(citationEvidenceTemplate(item))}</textarea>
                <button class="secondary-button" data-citation-verification-evidence-action data-agent-task-id="${escapeHtml(task.id || "")}" data-citation-task-id="${escapeHtml(item.id || "")}" ${state.recordingCitationEvidenceTaskId === task.id && state.recordingCitationEvidenceCitationId === item.id ? "disabled" : ""}>
                  ${state.recordingCitationEvidenceTaskId === task.id && state.recordingCitationEvidenceCitationId === item.id ? "写回中..." : "记录核验证据"}
                </button>
              `}
            </div>
          </article>
        `).join("")}
      </div>
      ${canGeneratePackage ? `
        <div class="agent-task-citation-verification__action">
          <div>
            <strong>引用核验已完成</strong>
            <p class="muted">下一步生成可追溯的已核验文献包，供后续草稿和人工审阅使用。</p>
          </div>
          <button class="primary-button" data-verified-literature-package-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isGeneratingPackage ? "disabled" : ""}>
            ${isGeneratingPackage ? "生成中..." : "生成已核验文献包"}
          </button>
        </div>
      ` : ""}
    </div>
  `;
}

function citationEvidenceTemplate(item = {}) {
  return JSON.stringify({
    connector: "manual",
    authors: [],
    year: "",
    title: item.source_label || "",
    venue: "",
    doi_or_stable_url: "",
    relevance: "direct",
    evidence_url: "",
    note: `核验：${item.query || item.source_label || item.id || ""}`,
  }, null, 2);
}

function renderVerifiedLiteraturePackage(task = {}) {
  const literaturePackage = task.verified_literature_package || {};
  if (!literaturePackage.status) return "";
  const review = task.verified_literature_package_review || {};
  const canReview = task.status === "verified_literature_package_ready";
  const isReviewing = state.reviewingVerifiedLiteraturePackageTaskId === task.id;
  return `
    <div class="agent-task-verified-literature-package">
      <div>
        <span class="meta-label">已核验文献包</span>
        <strong>${escapeHtml(String(literaturePackage.verified_reference_count || 0))} 条来源已核验</strong>
        <p class="muted">引用元数据已形成证据包；正式写入仍等待人工审阅。</p>
      </div>
      <div class="agent-task-verified-literature-package__grid">
        <div>
          <span class="meta-label">文献包</span>
          <code>${escapeHtml(literaturePackage.artifact_path || "Results/json/verified_literature_package.json")}</code>
        </div>
        <div>
          <span class="meta-label">来源日志</span>
          <code>${escapeHtml(literaturePackage.source_log_artifact_path || "Results/json/citation_verification_log.json")}</code>
        </div>
        <div>
          <span class="meta-label">下一步</span>
          <p>${escapeHtml(productTermLabel(task.next_action || literaturePackage.next_action || "review_verified_literature_package"))}</p>
        </div>
        <div>
          <span class="meta-label">正式层边界</span>
          <p>${literaturePackage.formal_write_allowed ? "允许写入正式层" : "不写入正式层"}</p>
        </div>
      </div>
      <div class="agent-task-verified-literature-package__review">
        <div>
          <span class="meta-label">审阅门</span>
          <strong>${escapeHtml(productTermLabel(review.status || "等待审阅"))}</strong>
          <p class="muted">批准后只生成草稿层引用计划，不直接写入正式论文。</p>
        </div>
        ${canReview ? `
          <div class="action-row">
            ${["approve_for_manuscript_citations", "needs_revision", "reject"].map((action) => `
              <button class="${action === "approve_for_manuscript_citations" ? "primary-button" : "secondary-button"}" data-verified-literature-package-review-action="${action}" data-agent-task-id="${escapeHtml(task.id || "")}" ${isReviewing ? "disabled" : ""}>
                ${isReviewing && state.reviewingVerifiedLiteraturePackageAction === action ? "保存中..." : verifiedLiteraturePackageReviewActionLabel(action)}
              </button>
            `).join("")}
          </div>
        ` : ""}
      </div>
    </div>
  `;
}

function renderManuscriptCitationPlan(task = {}) {
  const plan = task.manuscript_citation_plan || {};
  const review = task.manuscript_citation_plan_review || {};
  const canGenerate = task.status === "verified_literature_package_approved";
  const isGenerating = state.generatingManuscriptCitationPlanTaskId === task.id;
  const canReview = task.status === "manuscript_citation_plan_ready";
  const isReviewing = state.reviewingManuscriptCitationPlanTaskId === task.id;
  if (!plan.status && !canGenerate) return "";

  return `
    <div class="agent-task-manuscript-citation-plan">
      <div class="agent-task-manuscript-citation-plan__head">
        <div>
          <span class="meta-label">论文引用计划</span>
          <strong>${plan.status ? escapeHtml(productTermLabel(plan.status)) : "等待生成"}</strong>
          <p class="muted">把已核验文献映射到引言、文献综述和方法设计等章节；生成后仍需人工审阅。</p>
        </div>
        ${canGenerate ? `
          <button class="primary-button" data-manuscript-citation-plan-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isGenerating ? "disabled" : ""}>
            ${isGenerating ? "生成中..." : "生成论文引用计划"}
          </button>
        ` : `<span class="pill">${escapeHtml(productTermLabel(task.next_action || plan.next_action || "review_manuscript_citation_plan"))}</span>`}
      </div>
      ${plan.status ? `
        <div class="agent-task-manuscript-citation-plan__grid">
          <div>
            <span class="meta-label">引用计划</span>
            <code>${escapeHtml(plan.artifact_path || "Results/json/manuscript_citation_plan.json")}</code>
          </div>
          <div>
            <span class="meta-label">来源文献包</span>
            <code>${escapeHtml(plan.source_artifact_path || "Results/json/verified_literature_package.json")}</code>
          </div>
          <div>
            <span class="meta-label">绑定数量</span>
            <p>${escapeHtml(String(plan.citation_binding_count || 0))} 条引用绑定</p>
          </div>
          <div>
            <span class="meta-label">下一步</span>
            <p>${escapeHtml(productTermLabel(plan.next_action || task.next_action || "review_manuscript_citation_plan"))}</p>
          </div>
          <div>
            <span class="meta-label">正式层边界</span>
            <p>${plan.formal_write_allowed ? "允许写入正式层" : "不写入正式层"}</p>
          </div>
        </div>
        <div class="agent-task-manuscript-citation-plan__review">
          <div>
            <span class="meta-label">审阅门</span>
            <strong>${escapeHtml(productTermLabel(review.status || "等待审阅"))}</strong>
            <p class="muted">批准后只开放章节草稿规划，不写入正式论文。</p>
          </div>
          ${canReview ? `
            <div class="action-row">
              ${["approve_for_draft_sections", "needs_revision", "reject"].map((action) => `
                <button class="${action === "approve_for_draft_sections" ? "primary-button" : "secondary-button"}" data-manuscript-citation-plan-review-action="${action}" data-agent-task-id="${escapeHtml(task.id || "")}" ${isReviewing ? "disabled" : ""}>
                  ${isReviewing && state.reviewingManuscriptCitationPlanAction === action ? "保存中..." : manuscriptCitationPlanReviewActionLabel(action)}
                </button>
              `).join("")}
            </div>
          ` : ""}
        </div>
      ` : ""}
    </div>
  `;
}

function renderDraftSectionPlan(task = {}) {
  const plan = task.draft_section_plan || {};
  const review = task.draft_section_plan_review || {};
  const canGenerate = task.status === "manuscript_citation_plan_approved";
  const isGenerating = state.generatingDraftSectionPlanTaskId === task.id;
  const canReview = task.status === "draft_section_plan_ready";
  const isReviewing = state.reviewingDraftSectionPlanTaskId === task.id;
  if (!plan.status && !canGenerate) return "";

  return `
    <div class="agent-task-draft-section-plan">
      <div class="agent-task-draft-section-plan__head">
        <div>
          <span class="meta-label">章节草稿计划</span>
          <strong>${plan.status ? escapeHtml(productTermLabel(plan.status)) : "等待生成"}</strong>
          <p class="muted">把已批准的引用绑定拆成章节草稿任务；这里仍不写正式正文。</p>
        </div>
        ${canGenerate ? `
          <button class="primary-button" data-draft-section-plan-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isGenerating ? "disabled" : ""}>
            ${isGenerating ? "生成中..." : "生成章节草稿计划"}
          </button>
        ` : `<span class="pill">${escapeHtml(productTermLabel(task.next_action || plan.next_action || "review_draft_section_plan"))}</span>`}
      </div>
      ${plan.status ? `
        <div class="agent-task-draft-section-plan__grid">
          <div>
            <span class="meta-label">章节计划</span>
            <code>${escapeHtml(plan.artifact_path || "Results/json/draft_section_plan.json")}</code>
          </div>
          <div>
            <span class="meta-label">来源引用计划</span>
            <code>${escapeHtml(plan.source_artifact_path || "Results/json/manuscript_citation_plan.json")}</code>
          </div>
          <div>
            <span class="meta-label">章节数量</span>
            <p>${escapeHtml(String(plan.section_count || 0))} 个章节任务</p>
          </div>
          <div>
            <span class="meta-label">引用绑定</span>
            <p>${escapeHtml(String(plan.citation_binding_count || 0))} 条绑定</p>
          </div>
          <div>
            <span class="meta-label">下一步</span>
            <p>${escapeHtml(productTermLabel(plan.next_action || task.next_action || "review_draft_section_plan"))}</p>
          </div>
          <div>
            <span class="meta-label">正式层边界</span>
            <p>${plan.formal_write_allowed ? "允许写入正式层" : "不写入正式层"}</p>
          </div>
        </div>
        <div class="agent-task-draft-section-plan__review">
          <div>
            <span class="meta-label">审阅门</span>
            <strong>${escapeHtml(productTermLabel(review.status || "等待审阅"))}</strong>
            <p class="muted">批准后只生成章节草稿任务包，不写入正式正文。</p>
          </div>
          ${canReview ? `
            <div class="action-row">
              ${["approve_for_section_tasks", "needs_revision", "reject"].map((action) => `
                <button class="${action === "approve_for_section_tasks" ? "primary-button" : "secondary-button"}" data-draft-section-plan-review-action="${action}" data-agent-task-id="${escapeHtml(task.id || "")}" ${isReviewing ? "disabled" : ""}>
                  ${isReviewing && state.reviewingDraftSectionPlanAction === action ? "保存中..." : draftSectionPlanReviewActionLabel(action)}
                </button>
              `).join("")}
            </div>
          ` : ""}
        </div>
      ` : ""}
    </div>
  `;
}

function renderDraftSectionTasks(task = {}) {
  const sectionTasks = task.draft_section_tasks || {};
  const review = task.draft_section_tasks_review || {};
  const canGenerate = task.status === "draft_section_plan_approved";
  const isGenerating = state.generatingDraftSectionTasksTaskId === task.id;
  const canReview = task.status === "draft_section_tasks_ready";
  const isReviewing = state.reviewingDraftSectionTasksTaskId === task.id;
  if (!sectionTasks.status && !canGenerate) return "";

  return `
    <div class="agent-task-draft-section-tasks">
      <div class="agent-task-draft-section-tasks__head">
        <div>
          <span class="meta-label">章节草稿任务包</span>
          <strong>${sectionTasks.status ? escapeHtml(productTermLabel(sectionTasks.status)) : "等待生成"}</strong>
          <p class="muted">把已批准章节计划拆成 WriterAgent 后续可执行的草稿任务。生成后进入章节任务审阅。</p>
        </div>
        ${canGenerate ? `
          <button class="primary-button" data-draft-section-tasks-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isGenerating ? "disabled" : ""}>
            ${isGenerating ? "生成中..." : "生成章节草稿任务包"}
          </button>
        ` : `<span class="pill">${escapeHtml(productTermLabel(task.next_action || sectionTasks.next_action || "review_draft_section_tasks"))}</span>`}
      </div>
      ${sectionTasks.status ? `
        <div class="agent-task-draft-section-tasks__checkpoint">
          <div>
            <span class="meta-label">当前产物</span>
            <strong>章节任务包</strong>
            <p>每个章节都有写作目标、引用绑定和输出位置。</p>
          </div>
          <div>
            <span class="meta-label">下一步</span>
            <strong>${escapeHtml(productTermLabel(sectionTasks.next_action || task.next_action || "review_draft_section_tasks"))}</strong>
            <p>审阅通过后，再交给 WriterAgent 生成章节草稿。</p>
          </div>
          <div>
            <span class="meta-label">边界</span>
            <strong title="正式层保持锁定">正式层仍保持锁定</strong>
            <p>当前只准备草稿层任务，不改动正式稿。</p>
          </div>
        </div>
        <div class="agent-task-draft-section-tasks__grid">
          <div>
            <span class="meta-label">任务包</span>
            <code>${escapeHtml(sectionTasks.artifact_path || "Results/json/draft_section_tasks.json")}</code>
          </div>
          <div>
            <span class="meta-label">来源章节计划</span>
            <code>${escapeHtml(sectionTasks.source_artifact_path || "Results/json/draft_section_plan.json")}</code>
          </div>
          <div>
            <span class="meta-label">章节任务</span>
            <p>${escapeHtml(String(sectionTasks.task_count || 0))} 个待审阅任务</p>
          </div>
          <div>
            <span class="meta-label">引用绑定</span>
            <p>${escapeHtml(String(sectionTasks.citation_binding_count || 0))} 条绑定</p>
          </div>
          <div>
            <span class="meta-label">下一步</span>
            <p>${escapeHtml(productTermLabel(sectionTasks.next_action || task.next_action || "review_draft_section_tasks"))}</p>
          </div>
          <div>
            <span class="meta-label">正式层边界</span>
            <p>${sectionTasks.formal_write_allowed ? "允许写入正式层" : "正式层仍保持锁定"}</p>
          </div>
        </div>
        <div class="agent-task-draft-section-tasks__review">
          <div>
            <span class="meta-label">审阅门</span>
            <strong>${escapeHtml(productTermLabel(review.status || sectionTasks.review_status || "等待审阅"))}</strong>
            <p class="muted">${review.status ? "审阅结果已写回章节任务包。" : "确认任务范围、引用绑定和输出位置后，再交给 WriterAgent。正式层仍保持锁定。"}</p>
          </div>
          ${canReview ? `
            <div class="action-row">
              ${["approve_for_writer_agent", "needs_revision", "reject"].map((action) => `
                <button class="${action === "approve_for_writer_agent" ? "primary-button" : "secondary-button"}" data-draft-section-tasks-review-action="${action}" data-agent-task-id="${escapeHtml(task.id || "")}" ${isReviewing ? "disabled" : ""}>
                  ${isReviewing && state.reviewingDraftSectionTasksAction === action ? "保存中..." : draftSectionTasksReviewActionLabel(action)}
                </button>
              `).join("")}
            </div>
          ` : ""}
        </div>
        <p class="muted">任务包只安排章节草稿写作；每个章节任务仍需后续人工审阅后再交给 WriterAgent。</p>
      ` : ""}
    </div>
  `;
}

function renderSectionDrafts(task = {}) {
  const drafts = task.section_drafts || {};
  const review = task.section_drafts_review || {};
  const preflight = task.formal_writeback_preflight || {};
  const manifest = task.formal_writeback_manifest || {};
  const exportPreflight = task.formal_export_preflight || {};
  const pdfCandidateExport = task.pdf_candidate_export || {};
  const exportFollowups = Array.isArray(task.export_preflight_followups) ? task.export_preflight_followups : [];
  const canGenerate = task.status === "draft_section_tasks_approved";
  const isGenerating = state.generatingSectionDraftsTaskId === task.id;
  const canReview = task.status === "section_drafts_ready" && Boolean(drafts.status);
  const isReviewing = state.reviewingSectionDraftsTaskId === task.id;
  const hasPreflight = Boolean(preflight.status || preflight.artifact_path);
  const canReviewPreflight = task.status === "formal_writeback_preflight_ready" && hasPreflight;
  const isReviewingPreflight = state.reviewingFormalWritebackPreflightTaskId === task.id;
  const hasFormalWriteback = Boolean(manifest.status || manifest.artifact_path);
  const hasExportPreflight = Boolean(exportPreflight.status || exportPreflight.artifact_path);
  const hasPdfCandidateExport = Boolean(pdfCandidateExport.status || pdfCandidateExport.pdf_candidate_path);
  const canGenerateExportPreflight = hasFormalWriteback && task.status === "formal_sections_written";
  const isGeneratingExportPreflight = state.generatingFormalExportPreflightTaskId === task.id;
  const canGeneratePdfCandidateExport =
    task.status === "formal_export_preflight_ready" && exportPreflight.status === "formal_export_preflight_ready";
  const isGeneratingPdfCandidateExport = state.generatingPdfCandidateExportTaskId === task.id;
  if (!drafts.status && !canGenerate && !hasPreflight && !hasFormalWriteback && !hasExportPreflight && !hasPdfCandidateExport) return "";

  return `
    <div class="agent-task-section-drafts">
      <div class="agent-task-section-drafts__head">
        <div>
          <span class="meta-label">章节草稿</span>
          <strong>${drafts.status ? "章节草稿已生成" : "等待 WriterAgent 生成草稿"}</strong>
          <p class="muted">WriterAgent 只写草稿层章节；生成后等待人工审阅，正式层仍保持锁定。</p>
        </div>
        ${canGenerate ? `
          <button class="primary-button" data-section-drafts-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isGenerating ? "disabled" : ""}>
            ${isGenerating ? "生成中..." : "生成章节草稿"}
          </button>
        ` : `<span class="pill">${escapeHtml(productTermLabel(task.next_action || drafts.next_action || "review_section_drafts"))}</span>`}
      </div>
      ${drafts.status ? `
        <div class="agent-task-section-drafts__checkpoint">
          <div>
            <span class="meta-label">当前产物</span>
            <strong>章节草稿已生成</strong>
            <p>等待人工审阅内容、引用绑定和证据边界。</p>
          </div>
          <div>
            <span class="meta-label">正式层</span>
            <strong>正式层仍保持锁定</strong>
            <p>这些文件只在草稿层，不写入正式论文。</p>
          </div>
        </div>
        <div class="agent-task-section-drafts__grid">
          <div>
            <span class="meta-label">草稿清单</span>
            <code>${escapeHtml(drafts.artifact_path || "Results/json/section_drafts.json")}</code>
          </div>
          <div>
            <span class="meta-label">来源任务包</span>
            <code>${escapeHtml(drafts.source_artifact_path || "Results/json/draft_section_tasks.json")}</code>
          </div>
          <div>
            <span class="meta-label">章节数量</span>
            <p>${escapeHtml(String(drafts.section_count || 0))} 个草稿章节</p>
          </div>
          <div>
            <span class="meta-label">下一步</span>
            <p>${escapeHtml(productTermLabel(drafts.next_action || task.next_action || "review_section_drafts"))}</p>
          </div>
          <div>
            <span class="meta-label">审阅状态</span>
            <p>等待人工审阅</p>
          </div>
          <div>
            <span class="meta-label">写回边界</span>
            <p>${drafts.formal_write_allowed ? "允许写入正式层" : "正式层仍保持锁定"}</p>
          </div>
        </div>
        ${canReview ? `
          <div class="agent-task-section-drafts__review">
            <div>
              <span class="meta-label">章节草稿审阅</span>
              <strong>决定是否进入正式写回预检</strong>
              <p>预检只生成候选写回清单，不覆盖正式论文。</p>
            </div>
            <div class="action-row">
              ${["approve_for_formal_writeback_preflight", "needs_revision", "reject"].map((action) => `
                <button
                  class="${action === "approve_for_formal_writeback_preflight" ? "primary-button" : "secondary-button"}"
                  data-section-drafts-review-action="${action}"
                  data-agent-task-id="${escapeHtml(task.id || "")}"
                  ${isReviewing ? "disabled" : ""}
                >
                  ${isReviewing && state.reviewingSectionDraftsAction === action ? "保存中..." : sectionDraftsReviewActionLabel(action)}
                </button>
              `).join("")}
            </div>
          </div>
        ` : review.status ? `
          <div class="agent-task-section-drafts__review is-complete">
            <div>
              <span class="meta-label">章节草稿审阅结果</span>
              <strong>${escapeHtml(productTermLabel(review.status))}</strong>
              <p>${escapeHtml(productTermLabel(review.next_action || task.next_action || "review_formal_writeback_preflight"))}</p>
            </div>
          </div>
        ` : ""}
      ` : ""}
      ${hasPreflight ? `
        <div class="agent-task-formal-writeback-preflight" data-testid="formal-writeback-preflight">
          <div>
            <span class="meta-label">正式写回预检</span>
            <strong>正式写回预检已准备</strong>
            <p>候选写回目标 ${escapeHtml(String(preflight.target_count || 0))} 个；正式层仍需人工确认。</p>
          </div>
          <div class="agent-task-formal-writeback-preflight__grid">
            <div>
              <span class="meta-label">预检清单</span>
              <code>${escapeHtml(preflight.artifact_path || "Results/json/section_draft_formal_writeback_preflight.json")}</code>
            </div>
            <div>
              <span class="meta-label">写入权限</span>
              <p>${preflight.formal_write_allowed ? "允许写入" : "仍未授权写入正式层"}</p>
            </div>
            <div>
              <span class="meta-label">下一步</span>
              <p>${escapeHtml(productTermLabel(preflight.next_action || task.next_action || "review_formal_writeback_preflight"))}</p>
            </div>
          </div>
          ${canReviewPreflight ? `
            <div class="agent-task-formal-writeback-preflight__review">
              <div>
                <span class="meta-label">正式层写入决定</span>
                <strong>批准写入正式层</strong>
                <p>批准后写入 Manuscripts/sections；修订或拒绝都不会改正式章节。</p>
              </div>
              <div class="action-row">
                ${["approve_formal_writeback", "needs_revision", "reject"].map((action) => `
                  <button
                    class="${action === "approve_formal_writeback" ? "primary-button" : "secondary-button"}"
                    data-formal-writeback-preflight-review-action="${action}"
                    data-agent-task-id="${escapeHtml(task.id || "")}"
                    ${isReviewingPreflight ? "disabled" : ""}
                  >
                    ${isReviewingPreflight && state.reviewingFormalWritebackPreflightAction === action ? "保存中..." : formalWritebackPreflightReviewActionLabel(action)}
                  </button>
                `).join("")}
              </div>
            </div>
          ` : ""}
        </div>
      ` : ""}
      ${hasFormalWriteback ? `
        <div class="agent-task-formal-writeback-result" data-testid="formal-writeback-result">
          <div>
            <span class="meta-label">正式章节已写入</span>
            <strong>正式章节已写入</strong>
            <p>已写入 ${escapeHtml(String(manifest.written_count || 0))} / ${escapeHtml(String(manifest.target_count || 0))} 个正式章节。下一步：${escapeHtml(productTermLabel(task.next_action || "prepare_export_preflight"))}</p>
          </div>
          <code>${escapeHtml(manifest.artifact_path || "Results/json/formal_writeback_manifest.json")}</code>
          ${canGenerateExportPreflight ? `
            <div class="agent-task-formal-writeback-result__actions">
              <button
                class="primary-button"
                data-formal-export-preflight-action
                data-agent-task-id="${escapeHtml(task.id || "")}"
                ${isGeneratingExportPreflight ? "disabled" : ""}
              >
                ${isGeneratingExportPreflight ? "预检中..." : "生成导出预检台"}
              </button>
            </div>
          ` : ""}
        </div>
      ` : ""}
      ${hasExportPreflight ? `
        <div class="agent-task-formal-export-preflight" data-testid="agent-task-formal-export-preflight">
          <div class="agent-task-formal-export-preflight__head">
            <div>
              <span class="meta-label">导出预检台</span>
              <strong>${escapeHtml(productTermLabel(exportPreflight.status || task.status))}</strong>
              <p>${exportPreflight.status === "formal_export_preflight_blocked" ? "有缺口需要先处理，处理后再进入 PDF/DOCX 预检。" : "正式章节基础检查已通过，可以生成 PDF 候选稿供人工审阅。"}</p>
            </div>
            <span class="pill">${escapeHtml(productTermLabel(exportPreflight.next_action || task.next_action || "run_pdf_export_preflight"))}</span>
          </div>
          <div class="agent-task-formal-export-preflight__grid">
            <div>
              <span class="meta-label">正式章节</span>
              <p>${escapeHtml(String(exportPreflight.section_count || 0))} 个；缺失 ${escapeHtml(String(exportPreflight.missing_section_count || 0))} 个</p>
            </div>
            <div>
              <span class="meta-label">预检记录</span>
              <code>${escapeHtml(exportPreflight.artifact_path || "Results/json/agent_task_export_preflight.json")}</code>
            </div>
            <div>
              <span class="meta-label">审阅文档</span>
              <code>${escapeHtml(exportPreflight.review_path || "Reviews/agent_task_export_preflight.md")}</code>
            </div>
            <div>
              <span class="meta-label">正式层</span>
              <p>${exportPreflight.writes_formal_layer ? "会改写正式层" : "不会改写正式层"}</p>
            </div>
          </div>
          ${(task.blockers || []).length ? `
            <div class="agent-task-formal-export-preflight__blockers">
              <span class="meta-label">阻断项</span>
              <ul>
                ${(task.blockers || []).map((blocker) => `<li>${escapeHtml(blocker.message || blocker.code || "")}</li>`).join("")}
              </ul>
            </div>
          ` : `
            <p class="muted">没有发现正式章节缺失；下一步生成 PDF 候选稿，检查排版、引用和复现边界。</p>
          `}
          ${canGeneratePdfCandidateExport ? `
            <div class="agent-task-formal-export-preflight__actions">
              <button
                class="primary-button"
                data-pdf-candidate-export-action
                data-agent-task-id="${escapeHtml(task.id || "")}"
                ${isGeneratingPdfCandidateExport ? "disabled" : ""}
              >
                ${isGeneratingPdfCandidateExport ? "生成中..." : "生成 PDF 候选稿"}
              </button>
            </div>
          ` : ""}
          ${exportFollowups.length ? `
            <div class="agent-task-formal-export-preflight__followups">
              <span class="meta-label">Agent 后续任务</span>
              ${exportFollowups.map((followup) => `
                <div>
                  <strong>${escapeHtml(followup.owner_agent || "Agent")}</strong>
                  <p>${escapeHtml(followup.description || followup.title || "")}</p>
                </div>
              `).join("")}
            </div>
          ` : ""}
        </div>
      ` : ""}
      ${hasPdfCandidateExport ? `
        <div class="agent-task-pdf-candidate-export" data-testid="agent-task-pdf-candidate-export">
          <div class="agent-task-pdf-candidate-export__head">
            <div>
              <span class="meta-label">PDF 候选稿</span>
              <strong>${escapeHtml(productTermLabel(pdfCandidateExport.status || task.status))}</strong>
              <p>先检查排版、章节完整性、引用边界和复现说明；通过后再进入正式 PDF/DOCX 导出。</p>
            </div>
            <span class="pill">${escapeHtml(productTermLabel(pdfCandidateExport.next_action || task.next_action || "review_pdf_candidate"))}</span>
          </div>
          <div class="agent-task-pdf-candidate-export__grid">
            <div>
              <span class="meta-label">PDF 候选稿</span>
              <code>${escapeHtml(pdfCandidateExport.pdf_candidate_path || "Submissions/formal_package/paper_candidate.pdf")}</code>
            </div>
            <div>
              <span class="meta-label">候选清单</span>
              <code>${escapeHtml(pdfCandidateExport.artifact_path || "Submissions/formal_package/pdf_candidate_manifest.json")}</code>
            </div>
            <div>
              <span class="meta-label">审阅文档</span>
              <code>${escapeHtml(pdfCandidateExport.review_path || "Reviews/pdf_candidate_export_review.md")}</code>
            </div>
            <div>
              <span class="meta-label">正式层</span>
              <p>${pdfCandidateExport.writes_formal_layer ? "会改写正式层" : "不会改写正式层"}</p>
            </div>
          </div>
          <p class="muted">候选稿不覆盖 paper.pdf / paper.docx；人工审阅通过后再进入正式导出。</p>
        </div>
      ` : ""}
    </div>
  `;
}

function renderAgentTaskExecutionHandoff(task) {
  const executionResult = task.execution_result || {};
  const methodResult = firstMethodExecutionResult(executionResult);
  const reproducibility = methodResult.reproducibility || {};
  const evaluator = methodResult.evaluator || executionResult.evaluator || {};
  const resultPath = executionResult.artifact_path
    || executionResult.method_execution?.artifact_path
    || reproducibility.result_artifact_path
    || "";
  const manifestPath = reproducibility.manifest_artifact_path
    || executionResult.method_execution?.manifest_artifact_path
    || "";
  const auditLog = Array.isArray(task.audit_log) ? task.audit_log : [];
  const runId = methodResult.run_id || reproducibility.run_id || "";
  const evaluatorStatus = evaluator.status || executionResult.evaluator_status || "needs_review";
  const nextAction = task.status === "succeeded"
    ? (task.next_action === "completed" ? "进入结果审阅或草稿生成" : productTermLabel(task.next_action || "review_execution_result"))
    : "查看失败原因并重新选择后端";

  if (!resultPath && !manifestPath && !runId && !auditLog.length && !evaluatorStatus) return "";

  return `
    ${renderReferenceSeedPackageResultReview(executionResult, task)}
    ${renderDraftLiteratureReview(task)}
    ${renderCitationVerificationTasks(task)}
    ${renderVerifiedLiteraturePackage(task)}
    ${renderManuscriptCitationPlan(task)}
    ${renderDraftSectionPlan(task)}
    ${renderDraftSectionTasks(task)}
    ${renderSectionDrafts(task)}
    <div class="agent-task-execution-handoff">
      <div>
        <span class="meta-label">结果文件</span>
        <code>${escapeHtml(resultPath || "等待写入结果文件")}</code>
      </div>
      <div>
        <span class="meta-label">运行清单</span>
        <code>${escapeHtml(manifestPath || "等待生成 run_manifest.json")}</code>
      </div>
      <div>
        <span class="meta-label">评估器状态</span>
        <p>${escapeHtml(evaluatorStatusLabel(evaluatorStatus))}${runId ? ` · ${escapeHtml(runId)}` : ""}</p>
      </div>
      <div>
        <span class="meta-label">下一步动作</span>
        <p>${escapeHtml(nextAction)}</p>
      </div>
      <div>
        <span class="meta-label">审计线索</span>
        <p>${escapeHtml(auditLog.length ? `${auditLog.length} 个任务审计事件已记录在任务详情中` : "运行清单和结果文件可用于复核本次执行。")}</p>
      </div>
    </div>
  `;
}

function renderAgentTaskBackendSelection(task) {
  const status = task.status || "";
  const selectedBackend = task.selected_backend || {};
  const backendBlocker = task.backend_blocker || {};
  const isExecuting = state.executingAgentTaskId === task.id;
  const backendOptions = [
    { id: "statspai", label: "StatsPAI" },
    { id: "python_ols_adapter", label: "Python OLS" },
    { id: "stata_mcp", label: "StataMCP" },
    { id: "codex", label: "Codex" },
  ];

  if (status === "reviewed_for_dispatch") {
    return `
      <div class="agent-task-backend-selection">
        <div>
          <span class="meta-label">执行后端</span>
          <p class="muted">选择执行后端并触发运行</p>
        </div>
        <div class="agent-task-backend-actions">
          <select data-backend-select data-agent-task-id="${escapeHtml(task.id || "")}" ${isExecuting ? "disabled" : ""}>
            ${backendOptions.map((opt) => `
              <option value="${escapeHtml(opt.id)}" ${selectedBackend.id === opt.id ? "selected" : ""}>${escapeHtml(opt.label)}</option>
            `).join("")}
          </select>
          <button class="primary-button" data-select-backend-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isExecuting ? "disabled" : ""}>
            ${isExecuting ? "执行中..." : "选择并执行"}
          </button>
        </div>
      </div>
    `;
  }

  if (status === "backend_selected") {
    return `
      <div class="agent-task-backend-selection">
        <div>
          <span class="meta-label">已选后端</span>
          <p class="muted">${escapeHtml(selectedBackend.label || selectedBackend.id || "-")} · ${escapeHtml(selectedBackend.evidence_level || "")}</p>
        </div>
        <div class="agent-task-backend-actions">
          <button class="primary-button" data-execute-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isExecuting ? "disabled" : ""}>
            ${isExecuting ? "执行中..." : "执行"}
          </button>
        </div>
      </div>
      ${renderAgentTaskBackendDetails(task)}
    `;
  }

  if (status === "blocked_by_backend_unavailable") {
    return `
      <div class="agent-task-backend-selection is-blocked">
        <div>
          <span class="meta-label">后端不可用</span>
          <p class="muted">${escapeHtml(backendBlocker.message || "所选执行后端暂时不可用，请选择后备执行后端。")}</p>
        </div>
        <div class="agent-task-backend-actions">
          <select data-backend-select data-agent-task-id="${escapeHtml(task.id || "")}" ${isExecuting ? "disabled" : ""}>
            ${backendOptions.map((opt) => `
              <option value="${escapeHtml(opt.id)}">${escapeHtml(opt.label)}</option>
            `).join("")}
          </select>
          <button class="primary-button" data-select-backend-action data-agent-task-id="${escapeHtml(task.id || "")}" ${isExecuting ? "disabled" : ""}>
            ${isExecuting ? "执行中..." : "选择后备并执行"}
          </button>
        </div>
      </div>
      ${renderAgentTaskBackendDetails(task)}
    `;
  }

  if (status === "succeeded" || status === "failed") {
    const executionResult = task.execution_result || {};
    const resultLabel = status === "succeeded"
      ? `执行成功 · ${escapeHtml(executionResult.engine || "")} · ${escapeHtml(executionResult.evidence_level || "")}`
      : `执行失败 · ${escapeHtml((executionResult.error || {}).code || "")}`;
    return `
      <div class="agent-task-backend-selection">
        <div>
          <span class="meta-label">执行结果</span>
          <p class="muted">${resultLabel}</p>
        </div>
      </div>
      ${renderAgentTaskExecutionHandoff(task)}
      ${renderAgentTaskBackendDetails(task)}
    `;
  }

  return "";
}

function renderAgentTaskSkillBindings(task) {
  const bindings = Array.isArray(task.internal_skill_bindings) ? task.internal_skill_bindings : [];
  if (!bindings.length) {
    return `
      <div class="agent-task-skill-bindings is-empty">
        <span class="meta-label">Skill 绑定</span>
        <p class="muted">尚未绑定内部 Skill。这个任务会按 SupervisorPlan 的普通派工要求审阅。</p>
      </div>
    `;
  }

  return `
    <div class="agent-task-skill-bindings">
      ${bindings.map((binding) => {
        const why = binding.why_this_skill
          || binding.semantic_selection_reason
          || binding.matched_reason
          || "等待 Supervisor 补充选择理由。";
        const artifacts = Array.isArray(binding.expected_artifacts) ? binding.expected_artifacts : [];
        const sources = Array.isArray(binding.skill_sources) ? binding.skill_sources : [];
        return `
          <article class="agent-task-skill-binding">
            <div class="agent-task-skill-head">
              <div>
                <span class="meta-label">内部 Skill</span>
                <strong>${escapeHtml(binding.name || binding.skill_id || "未命名 Skill")}</strong>
                <p class="muted">${escapeHtml(binding.skill_id || "")} · ${escapeHtml(productTermLabel(binding.selection_source || "registry_rule_match"))}</p>
              </div>
              <span class="pill">${escapeHtml(productTermLabel(binding.risk_level || "medium"))}</span>
            </div>
            <div class="agent-task-skill-grid">
              <div>
                <span class="meta-label">为什么选这个 Skill</span>
                <p>${escapeHtml(why)}</p>
              </div>
              <div>
                <span class="meta-label">预期产物</span>
                ${artifacts.length ? `
                  <ul>
                    ${artifacts.map((artifact) => `<li>${escapeHtml(String(artifact))}</li>`).join("")}
                  </ul>
                ` : "<p class='muted'>尚未声明。</p>"}
              </div>
              <div>
                <span class="meta-label">执行边界</span>
                <p>${escapeHtml(productTermLabel(binding.execution_boundary || "review_before_execution"))}</p>
              </div>
              <div>
                <span class="meta-label">Skill 来源</span>
                ${sources.length ? `
                  <ul>
                    ${sources.map((source) => `
                      <li>${escapeHtml(source.name || source.url || "外部来源")}${source.license ? ` · ${escapeHtml(source.license)}` : ""}</li>
                    `).join("")}
                  </ul>
                ` : "<p class='muted'>本地内部方法库。</p>"}
              </div>
            </div>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderAgentTaskQueueItem(task) {
  const inputEvidence = task.input_evidence || {};
  const outputRequirements = task.output_requirements || [];
  const riskFlags = task.risk_flags || [];
  const auditLog = task.audit_log || [];
  const dispatchReadiness = task.dispatch_readiness || {};
  const dispatchReview = task.dispatch_review || {};
  const dispatchBlockers = dispatchReadiness.blockers || task.blockers || [];
  const reviewDisabled = state.reviewingAgentTaskId === task.id;
  return `
    <article class="agent-task-item">
      <div class="agent-task-item-head">
        <div>
          <span class="meta-label">${escapeHtml(productTermLabel(task.role || task.owner_agent || "Agent"))}</span>
          <h5>${escapeHtml(task.title || task.id || "未命名任务")}</h5>
          <p class="muted">负责人 Agent：${escapeHtml(task.owner_agent || "-")} · 状态：${escapeHtml(productTermLabel(task.status || "queued"))} · 下一步：${escapeHtml(task.primary_action?.label || productTermLabel(task.next_action || "dispatch_review_required"))}</p>
        </div>
        <span class="pill">${escapeHtml(productTermLabel(task.status || "queued"))}</span>
      </div>
      <p class="muted">${escapeHtml(task.summary || "")}</p>
      ${renderAgentTaskPrimaryAction(task.primary_action, { title: "任务建议动作" })}
      <div class="agent-task-dispatch-review">
        <div>
          <span class="meta-label">派工审阅</span>
          <strong>${escapeHtml(dispatchReviewLabel(dispatchReview, dispatchReadiness))}</strong>
          ${dispatchBlockers.length ? dispatchBlockers.map((blocker) => `
            <p class="muted">${escapeHtml(blocker.label || blocker.code || "等待审阅")}：${escapeHtml(blocker.description || "")}</p>
          `).join("") : "<p class='muted'>已通过派工审阅；仍需后续绑定真实执行后端。</p>"}
        </div>
        <div class="agent-task-dispatch-actions">
          ${["approve", "needs_revision", "reject"].map((action) => `
            <button class="${action === "approve" ? "primary-button" : "ghost-button"}" data-dispatch-review-action="${action}" data-agent-task-id="${escapeHtml(task.id || "")}" ${reviewDisabled ? "disabled" : ""}>
              ${reviewDisabled && state.reviewingAgentTaskAction === action ? "写回中..." : escapeHtml(dispatchReviewActionLabel(action))}
            </button>
          `).join("")}
        </div>
      </div>
      ${renderAgentTaskBackendSelection(task)}
      ${shouldShowExecutionMonitor(task) ? `
        <div id="agent-execution-monitor" class="agent-execution-monitor"></div>
      ` : ""}
      <details class="progressive-disclosure agent-task-details" data-disclosure="agent-task-progressive-disclosure">
        <summary>查看任务详情</summary>
        <div class="disclosure-panel agent-task-detail-grid">
          <div>
            <span class="meta-label">输入证据</span>
            <pre>${escapeHtml(JSON.stringify(inputEvidence, null, 2))}</pre>
          </div>
          <div>
            <span class="meta-label">输出要求</span>
            ${outputRequirements.length ? outputRequirements.map((item) => `
              <p class="muted">${escapeHtml(item.requirement || item.id || JSON.stringify(item))}</p>
            `).join("") : "<p class='muted'>尚未声明。</p>"}
          </div>
          ${renderAgentTaskSkillBindings(task)}
          ${renderReferenceChainPolicy(task.reference_chain_policy, { title: "任务引用链路", className: "agent-task-reference-policy" })}
          <div>
            <span class="meta-label">风险</span>
            ${riskFlags.length ? riskFlags.map((item) => `
              <p class="muted">${escapeHtml(item.description || item.id || JSON.stringify(item))}</p>
            `).join("") : "<p class='muted'>无阻塞风险。</p>"}
          </div>
          <div>
            <span class="meta-label">审计日志</span>
            ${auditLog.length ? auditLog.map((item) => `
              <p class="muted">${escapeHtml(item.event || "event")} · ${escapeHtml(item.actor || "")}</p>
            `).join("") : "<p class='muted'>尚无审计事件。</p>"}
          </div>
        </div>
      </details>
    </article>
  `;
}

// ============================================================
// Agent Execution Monitor
// ============================================================
// Nothing-style progress panel for long-running empirical tasks.
// Maps to: backend_selection → data_preflight → method_execution → result_evaluation

const EXECUTION_STAGES = [
  { id: "backend_selection", label: "选择执行后端" },
  { id: "data_preflight", label: "数据预检" },
  { id: "method_execution", label: "方法执行" },
  { id: "result_evaluation", label: "结果评估" },
];

function stageIndexForExecution(stage) {
  if (stage === "queued" || stage === "backend_selection") return 0;
  if (stage === "data_preflight") return 1;
  if (stage === "method_execution" || stage === "repair") return 2;
  if (stage === "result_evaluation" || stage === "alignment" || stage === "complete") return 3;
  if (stage === "failed") return 2; // Show at execution stage with error state
  return 0;
}

function executionStageLabel(stage) {
  const found = EXECUTION_STAGES.find((s) => s.id === stage);
  return found ? found.label : stage || "处理中";
}

function setExecutionStage(stageIndex) {
  const stages = document.querySelectorAll(".agent-execution-monitor-stage");
  stages.forEach((el, index) => {
    el.classList.toggle("is-done", index < stageIndex);
    el.classList.toggle("is-active", index === stageIndex);
  });
}

function startExecutionMonitor(taskId, jobId) {
  const mon = state.executionMonitor;
  mon.visible = true;
  mon.taskId = taskId;
  mon.jobId = jobId || taskId;
  mon.status = "queued";
  mon.stage = "backend_selection";
  mon.currentMessage = "任务已派发，正在选择执行后端...";
  mon.events = [];
  mon.technicalEvents = [];
  mon.startedAt = Date.now();
  mon.elapsedSeconds = 0;
  mon.result = null;
  mon.error = null;

  if (mon.pollIntervalId) {
    window.clearInterval(mon.pollIntervalId);
  }
  mon.pollIntervalId = window.setInterval(() => {
    mon.elapsedSeconds = Math.floor((Date.now() - mon.startedAt) / 1000);
    updateExecutionMonitorTimer();
  }, 1000);

  // Emit synthetic start event
  emitExecutionEvent({
    stage: "backend_selection",
    studentMessage: "任务已派发，正在选择执行后端...",
    technicalMessage: `EXECUTE_START taskId=${taskId}`,
    metadata: { agent: "dispatcher" },
  });

  renderAgentExecutionMonitor();
}

function stopExecutionMonitor() {
  const mon = state.executionMonitor;
  if (mon.pollIntervalId) {
    window.clearInterval(mon.pollIntervalId);
    mon.pollIntervalId = null;
  }
}

function resetExecutionMonitor() {
  stopExecutionMonitor();
  state.executionMonitor = {
    visible: false,
    taskId: null,
    jobId: null,
    status: null,
    stage: null,
    currentMessage: "",
    events: [],
    technicalEvents: [],
    startedAt: null,
    elapsedSeconds: 0,
    result: null,
    error: null,
    pollIntervalId: null,
  };
}

function emitExecutionEvent(event) {
  const mon = state.executionMonitor;
  const now = new Date().toISOString().slice(0, 19);
  const userEvent = {
    time: now,
    stage: event.stage || mon.stage || "event",
    severity: event.severity || "info",
    studentMessage: event.studentMessage || event.message || "处理中",
    metadata: event.metadata || {},
  };
  const techEvent = {
    ...userEvent,
    technicalMessage: event.technicalMessage || event.studentMessage || event.message || "",
  };
  if (event.attempt !== undefined) {
    userEvent.attempt = event.attempt;
    techEvent.attempt = event.attempt;
  }

  mon.events.push(userEvent);
  mon.technicalEvents.push(techEvent);
  if (event.studentMessage) {
    mon.currentMessage = event.studentMessage;
  }
  if (event.stage) {
    mon.stage = event.stage;
  }
  if (event.status) {
    mon.status = event.status;
  }
  renderAgentExecutionMonitor();
}

function finishExecutionMonitor(result) {
  const mon = state.executionMonitor;
  mon.status = "succeeded";
  mon.stage = "complete";
  mon.currentMessage = "任务完成，结果已就绪。";
  mon.result = result;
  emitExecutionEvent({
    stage: "complete",
    studentMessage: "任务完成，结果已就绪。",
    technicalMessage: "EXECUTE_COMPLETE",
    status: "succeeded",
  });
  stopExecutionMonitor();
  renderAgentExecutionMonitor();
}

function failExecutionMonitor(errorPayload, studentMessage) {
  const mon = state.executionMonitor;
  mon.status = "failed";
  mon.stage = "failed";
  mon.currentMessage = studentMessage || "任务执行失败。";
  mon.error = errorPayload;
  emitExecutionEvent({
    stage: "failed",
    studentMessage: studentMessage || "任务执行失败。",
    technicalMessage: `EXECUTE_FAILED: ${JSON.stringify(errorPayload)}`,
    status: "failed",
    severity: "error",
  });
  stopExecutionMonitor();
  renderAgentExecutionMonitor();
}

// --- Simulated execution flow (for demo / until real backend wired) ---
async function simulateExecutionFlow(taskId, methodId) {
  const methodNames = {
    ols: "OLS 回归",
    iv: "工具变量 (2SLS)",
    did: "双重差分",
    rdd: "断点回归",
    psm: "倾向得分匹配",
    dml: "双重机器学习",
  };
  const methodName = methodNames[methodId] || methodId || "统计方法";

  // Stage 1: Backend Selection
  await new Promise((r) => setTimeout(r, 800));
  emitExecutionEvent({
    stage: "backend_selection",
    studentMessage: `已选择 StatsPAI 作为执行后端，准备运行 ${methodName}。`,
    technicalMessage: `BACKEND_SELECT backend=statsPAI method=${methodId}`,
    metadata: { agent: "dispatcher" },
  });

  // Stage 2: Data Preflight
  await new Promise((r) => setTimeout(r, 1200));
  emitExecutionEvent({
    stage: "data_preflight",
    studentMessage: "数据预检通过：样本量充足，变量完整性检查无异常。",
    technicalMessage: `DATA_PREFLIGHT n=1250 vars=8 missing=0`,
    metadata: { agent: "preflight" },
  });

  // Stage 3: Method Execution
  await new Promise((r) => setTimeout(r, 2000));
  emitExecutionEvent({
    stage: "method_execution",
    studentMessage: `正在执行 ${methodName}，估计系数中...`,
    technicalMessage: `METHOD_EXEC method=${methodId} engine=statsPAI`,
    metadata: { agent: "executor" },
  });

  await new Promise((r) => setTimeout(r, 1500));
  emitExecutionEvent({
    stage: "method_execution",
    studentMessage: "第一_stage 完成，计算稳健标准误...",
    technicalMessage: `METHOD_EXEC vce=robust cluster=none`,
    metadata: { agent: "executor" },
  });

  // Stage 4: Result Evaluation
  await new Promise((r) => setTimeout(r, 1000));
  emitExecutionEvent({
    stage: "result_evaluation",
    studentMessage: "结果评估完成：系数显著性、模型诊断均通过。",
    technicalMessage: `RESULT_EVAL r2=0.42 f_stat=156.3 p_value=0.000`,
    metadata: { agent: "evaluator" },
  });

  finishExecutionMonitor({
    taskId,
    method: methodId,
    status: "completed",
    message: `${methodName} 执行完成`,
  });
}

// --- Wire monitor start into the review flow ---
function onTaskDispatchedForExecution(task) {
  // Called when a task is approved and ready to execute
  const methodId = inferMethodIdFromTask(task);
  startExecutionMonitor(task.id, task.id);
  // Kick off simulated flow (replace with real backend call)
  simulateExecutionFlow(task.id, methodId);
}

function inferMethodIdFromTask(task) {
  const title = (task.title || "").toLowerCase();
  if (title.includes("ols")) return "ols";
  if (title.includes("iv") || title.includes("2sls")) return "iv";
  if (title.includes("did")) return "did";
  if (title.includes("rdd")) return "rdd";
  if (title.includes("psm") || title.includes("match")) return "psm";
  if (title.includes("dml")) return "dml";
  return "ols";
}

function updateExecutionMonitorTimer() {
  const timerEl = document.getElementById("agent-execution-monitor-timer");
  if (timerEl) {
    timerEl.textContent = String(state.executionMonitor.elapsedSeconds);
  }
}

function renderAgentExecutionMonitor() {
  const container = document.getElementById("agent-execution-monitor");
  if (!container) return;

  const mon = state.executionMonitor;
  if (!mon.visible) {
    container.classList.remove("is-visible");
    container.innerHTML = "";
    return;
  }

  container.classList.add("is-visible");
  const stageIndex = stageIndexForExecution(mon.stage);
  const isFailed = mon.status === "failed";
  const isComplete = mon.status === "succeeded";

  // Last 6 user-facing events
  const recentEvents = mon.events.slice(-6);
  const recentTechnical = mon.technicalEvents.slice(-10);

  container.innerHTML = `
    <div class="agent-execution-monitor-head">
      <p class="agent-execution-monitor-message">${escapeHtml(mon.currentMessage || "准备执行...")}</p>
      <span id="agent-execution-monitor-timer" class="agent-execution-monitor-timer">${mon.elapsedSeconds}</span>
    </div>
    <div class="agent-execution-monitor-stages">
      ${EXECUTION_STAGES.map((stage, index) => `
        <div class="agent-execution-monitor-stage
          ${index < stageIndex ? "is-done" : ""}
          ${index === stageIndex && !isComplete ? "is-active" : ""}
          ${index === stageIndex && isFailed ? "is-active" : ""}
        ">
          <span class="agent-execution-monitor-stage-dot"></span>
          <span class="agent-execution-monitor-stage-label">${escapeHtml(stage.label)}</span>
        </div>
      `).join("")}
    </div>
    <div class="agent-execution-monitor-feed">
      ${recentEvents.length
        ? recentEvents.map((event) => {
            const agent = event.metadata?.agent ? `${event.metadata.agent} · ` : "";
            const attempt = event.attempt ? `第 ${event.attempt} 次 · ` : "";
            const severityClass = event.severity === "warn" ? "is-warn" : event.severity === "error" ? "is-error" : "";
            return `
              <div class="agent-execution-monitor-feed-item ${severityClass}">
                <span class="agent-execution-monitor-feed-item-meta">${escapeHtml(agent + attempt)}</span>
                <span class="agent-execution-monitor-feed-item-body">${escapeHtml(event.studentMessage || event.stage)}</span>
              </div>
            `;
          }).join("")
        : `<div class="agent-execution-monitor-empty">等待事件...</div>`
      }
    </div>
    <details class="agent-execution-monitor-tech">
      <summary>技术日志</summary>
      <pre class="agent-execution-monitor-tech-log">${escapeHtml(
        recentTechnical.length
          ? recentTechnical.map((e) => {
              const attempt = e.attempt ? ` attempt=${e.attempt}` : "";
              return `[${e.time || ""}] ${e.stage || "event"}${attempt} ${e.technicalMessage || ""}`;
            }).join("\n")
          : "暂无技术日志"
      )}</pre>
    </details>
  `;
}

// --- Integration: show monitor when task enters execution ---
function shouldShowExecutionMonitor(task) {
  return task && task.status === "reviewed_for_dispatch" && task.next_action === "select_execution_backend";
}

function maybeStartExecutionMonitorForTask(task) {
  if (!shouldShowExecutionMonitor(task)) return;
  const mon = state.executionMonitor;
  // Only start if not already tracking this task
  if (mon.taskId === task.id && mon.visible) return;
  startExecutionMonitor(task.id, task.id);
}

function dispatchReviewLabel(review, readiness) {
  if (review?.action === "approve") return "人工已批准派工";
  if (review?.action === "reject") return "人工已阻断任务";
  if (review?.action === "needs_revision") return "人工要求修改";
  const blocker = (readiness?.blockers || [])[0];
  return blocker?.code ? productTermLabel(blocker.code) : "等待派工审阅";
}

function dispatchReviewActionLabel(action) {
  const labels = {
    approve: "批准派工",
    needs_revision: "要求修改",
    reject: "阻断任务",
  };
  return labels[action] || action || "审阅";
}

async function handleCreateAgentTaskQueue() {
  if (!state.selectedProjectId) return;
  clearV2Error("overview");
  state.creatingAgentTaskQueue = true;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.create(state.selectedProjectId, {
      note: "Overview 人工创建 Agent Task Queue。",
    });
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `创建 Agent 任务队列失败：${error.message}`);
  } finally {
    state.creatingAgentTaskQueue = false;
    renderAgentTaskQueue();
  }
}

async function handleReviewAgentTaskDispatch(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingAgentTaskId = taskId;
  state.reviewingAgentTaskAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewDispatch(state.selectedProjectId, taskId, {
      action,
      note: `首页派工审阅：${dispatchReviewActionLabel(action)}`,
    });
    renderAgentTaskQueue();

    // If approved, trigger execution monitor flow
    if (action === "approve") {
      const queue = state.agentTaskQueueData?.agent_task_queue;
      const task = queue?.tasks?.find((t) => t.id === taskId);
      if (task) {
        onTaskDispatchedForExecution(task);
      }
    }
  } catch (error) {
    showV2Error("overview", `保存派工审阅失败：${error.message}`);
  } finally {
    state.reviewingAgentTaskId = null;
    state.reviewingAgentTaskAction = null;
    renderAgentTaskQueue();
  }
}

async function handleReferenceSeedPackageReview(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingAgentTaskId = taskId;
  state.reviewingAgentTaskAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewReferenceSeedPackage(state.selectedProjectId, taskId, {
      action,
      note: `候选来源种子包审阅：${referenceSeedReviewActionLabel(action)}`,
    });
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `保存候选来源审阅失败：${error.message}`);
  } finally {
    state.reviewingAgentTaskId = null;
    state.reviewingAgentTaskAction = null;
    renderAgentTaskQueue();
  }
}

async function handleDraftLiteratureReview(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.draftingLiteratureReviewTaskId = taskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.draftLiteratureReview(
      state.selectedProjectId,
      taskId,
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成草稿层文献综述失败：${error.message}`);
  } finally {
    state.draftingLiteratureReviewTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handleDraftLiteratureReviewReview(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingDraftLiteratureReviewTaskId = taskId;
  state.reviewingDraftLiteratureReviewAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewDraftLiteratureReview(state.selectedProjectId, taskId, {
      action,
      note: `草稿综述审阅：${draftLiteratureReviewReviewActionLabel(action)}`,
    });
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `保存草稿综述审阅失败：${error.message}`);
  } finally {
    state.reviewingDraftLiteratureReviewTaskId = null;
    state.reviewingDraftLiteratureReviewAction = null;
    renderAgentTaskQueue();
  }
}

async function handleCitationVerificationEvidence(taskId, citationTaskId) {
  if (!state.selectedProjectId || !taskId || !citationTaskId) return;
  clearV2Error("overview");
  const selector = `textarea[data-citation-evidence-json][data-agent-task-id="${CSS.escape(taskId)}"][data-citation-task-id="${CSS.escape(citationTaskId)}"]`;
  const textarea = document.querySelector(selector);
  let payload;
  try {
    payload = JSON.parse(textarea?.value || "{}");
  } catch (error) {
    showV2Error("overview", `引用核验证据不是有效 JSON：${error.message}`);
    return;
  }

  state.recordingCitationEvidenceTaskId = taskId;
  state.recordingCitationEvidenceCitationId = citationTaskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.recordCitationVerificationEvidence(
      state.selectedProjectId,
      taskId,
      citationTaskId,
      payload,
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `记录引用核验证据失败：${error.message}`);
  } finally {
    state.recordingCitationEvidenceTaskId = null;
    state.recordingCitationEvidenceCitationId = null;
    renderAgentTaskQueue();
  }
}

async function handleVerifiedLiteraturePackage(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.generatingVerifiedLiteraturePackageTaskId = taskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.generateVerifiedLiteraturePackage(
      state.selectedProjectId,
      taskId,
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成已核验文献包失败：${error.message}`);
  } finally {
    state.generatingVerifiedLiteraturePackageTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handleVerifiedLiteraturePackageReview(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingVerifiedLiteraturePackageTaskId = taskId;
  state.reviewingVerifiedLiteraturePackageAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewVerifiedLiteraturePackage(
      state.selectedProjectId,
      taskId,
      {
        action,
        note: `已核验文献包审阅：${verifiedLiteraturePackageReviewActionLabel(action)}`,
      },
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `保存已核验文献包审阅失败：${error.message}`);
  } finally {
    state.reviewingVerifiedLiteraturePackageTaskId = null;
    state.reviewingVerifiedLiteraturePackageAction = null;
    renderAgentTaskQueue();
  }
}

async function handleManuscriptCitationPlan(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.generatingManuscriptCitationPlanTaskId = taskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.generateManuscriptCitationPlan(
      state.selectedProjectId,
      taskId,
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成论文引用计划失败：${error.message}`);
  } finally {
    state.generatingManuscriptCitationPlanTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handleManuscriptCitationPlanReview(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingManuscriptCitationPlanTaskId = taskId;
  state.reviewingManuscriptCitationPlanAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewManuscriptCitationPlan(
      state.selectedProjectId,
      taskId,
      {
        action,
        note: `论文引用计划审阅：${manuscriptCitationPlanReviewActionLabel(action)}`,
      },
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `保存论文引用计划审阅失败：${error.message}`);
  } finally {
    state.reviewingManuscriptCitationPlanTaskId = null;
    state.reviewingManuscriptCitationPlanAction = null;
    renderAgentTaskQueue();
  }
}

async function handleDraftSectionPlan(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.generatingDraftSectionPlanTaskId = taskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.generateDraftSectionPlan(
      state.selectedProjectId,
      taskId,
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成章节草稿计划失败：${error.message}`);
  } finally {
    state.generatingDraftSectionPlanTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handleDraftSectionPlanReview(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingDraftSectionPlanTaskId = taskId;
  state.reviewingDraftSectionPlanAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewDraftSectionPlan(
      state.selectedProjectId,
      taskId,
      {
        action,
        note: `章节草稿计划审阅：${draftSectionPlanReviewActionLabel(action)}`,
      },
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `保存章节草稿计划审阅失败：${error.message}`);
  } finally {
    state.reviewingDraftSectionPlanTaskId = null;
    state.reviewingDraftSectionPlanAction = null;
    renderAgentTaskQueue();
  }
}

async function handleDraftSectionTasks(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.generatingDraftSectionTasksTaskId = taskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.generateDraftSectionTasks(
      state.selectedProjectId,
      taskId,
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成章节草稿任务包失败：${error.message}`);
  } finally {
    state.generatingDraftSectionTasksTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handleDraftSectionTasksReview(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingDraftSectionTasksTaskId = taskId;
  state.reviewingDraftSectionTasksAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewDraftSectionTasks(
      state.selectedProjectId,
      taskId,
      {
        action,
        note: `章节任务包审阅：${draftSectionTasksReviewActionLabel(action)}`,
      },
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `保存章节任务包审阅失败：${error.message}`);
  } finally {
    state.reviewingDraftSectionTasksTaskId = null;
    state.reviewingDraftSectionTasksAction = null;
    renderAgentTaskQueue();
  }
}

async function handleSectionDrafts(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.generatingSectionDraftsTaskId = taskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.generateSectionDrafts(
      state.selectedProjectId,
      taskId,
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成章节草稿失败：${error.message}`);
  } finally {
    state.generatingSectionDraftsTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handleSectionDraftsReview(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingSectionDraftsTaskId = taskId;
  state.reviewingSectionDraftsAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewSectionDrafts(
      state.selectedProjectId,
      taskId,
      {
        action,
        note: `章节草稿审阅：${sectionDraftsReviewActionLabel(action)}`,
      },
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `保存章节草稿审阅失败：${error.message}`);
  } finally {
    state.reviewingSectionDraftsTaskId = null;
    state.reviewingSectionDraftsAction = null;
    renderAgentTaskQueue();
  }
}

async function handleFormalWritebackPreflightReview(taskId, action) {
  if (!state.selectedProjectId || !taskId || !action) return;
  clearV2Error("overview");
  state.reviewingFormalWritebackPreflightTaskId = taskId;
  state.reviewingFormalWritebackPreflightAction = action;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.reviewFormalWritebackPreflight(
      state.selectedProjectId,
      taskId,
      {
        action,
        note: `正式写回预检审阅：${formalWritebackPreflightReviewActionLabel(action)}`,
      },
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `保存正式写回预检审阅失败：${error.message}`);
  } finally {
    state.reviewingFormalWritebackPreflightTaskId = null;
    state.reviewingFormalWritebackPreflightAction = null;
    renderAgentTaskQueue();
  }
}

async function handleFormalExportPreflight(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.generatingFormalExportPreflightTaskId = taskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.generateFormalExportPreflight(
      state.selectedProjectId,
      taskId,
      { note: "正式章节已写入，检查 PDF/DOCX 导出前置条件。" },
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成导出预检失败：${error.message}`);
  } finally {
    state.generatingFormalExportPreflightTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handlePdfCandidateExport(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.generatingPdfCandidateExportTaskId = taskId;
  renderAgentTaskQueue();
  try {
    state.agentTaskQueueData = await v2api.agentTaskQueue.generatePdfCandidateExport(
      state.selectedProjectId,
      taskId,
      { note: "生成 PDF 候选稿，供人工检查排版、章节和引用边界。" },
    );
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成 PDF 候选稿失败：${error.message}`);
  } finally {
    state.generatingPdfCandidateExportTaskId = null;
    renderAgentTaskQueue();
  }
}

function referenceSeedReviewActionLabel(action) {
  const labels = {
    approve_for_draft: "进入草稿综述",
    needs_revision: "要求修订",
    reject: "拒绝种子包",
  };
  return labels[action] || action || "审阅";
}

function draftLiteratureReviewReviewActionLabel(action) {
  const labels = {
    approve_for_citation_verification: "进入引用核验",
    needs_revision: "要求修订",
    reject: "拒绝草稿",
  };
  return labels[action] || action || "审阅";
}

function verifiedLiteraturePackageReviewActionLabel(action) {
  const labels = {
    approve_for_manuscript_citations: "批准进入引用计划",
    needs_revision: "要求修订",
    reject: "拒绝文献包",
  };
  return labels[action] || action || "审阅";
}

function manuscriptCitationPlanReviewActionLabel(action) {
  const labels = {
    approve_for_draft_sections: "批准进入章节草稿",
    needs_revision: "要求修订",
    reject: "拒绝引用计划",
  };
  return labels[action] || action || "审阅";
}

function draftSectionPlanReviewActionLabel(action) {
  const labels = {
    approve_for_section_tasks: "批准生成章节任务",
    needs_revision: "要求修订",
    reject: "拒绝计划",
  };
  return labels[action] || action || "审阅";
}

function draftSectionTasksReviewActionLabel(action) {
  const labels = {
    approve_for_writer_agent: "批准给 WriterAgent",
    needs_revision: "要求修订",
    reject: "拒绝任务包",
  };
  return labels[action] || action || "审阅";
}

function sectionDraftsReviewActionLabel(action) {
  const labels = {
    approve_for_formal_writeback_preflight: "进入正式写回预检",
    needs_revision: "要求修订",
    reject: "拒绝草稿",
  };
  return labels[action] || action || "审阅";
}

function formalWritebackPreflightReviewActionLabel(action) {
  const labels = {
    approve_formal_writeback: "批准写入正式层",
    needs_revision: "要求修订",
    reject: "拒绝写回",
  };
  return labels[action] || action || "审阅";
}

async function handleSelectBackendAndExecute(taskId, backendId) {
  if (!state.selectedProjectId || !taskId || !backendId) return;
  clearV2Error("overview");
  state.executingAgentTaskId = taskId;
  renderAgentTaskQueue();
  try {
    // Step 1: select backend
    state.agentTaskQueueData = await v2api.agentTaskQueue.selectBackend(state.selectedProjectId, taskId, {
      backend_id: backendId,
      note: `选择执行后端：${backendId}`,
    });
    renderAgentTaskQueue();

    const queue = state.agentTaskQueueData?.agent_task_queue;
    const task = queue?.tasks?.find((t) => t.id === taskId);
    if (task) {
      onTaskDispatchedForExecution(task);
    }

    // Step 2: execute
    state.agentTaskQueueData = await v2api.agentTaskQueue.execute(state.selectedProjectId, taskId);
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `选择并执行失败：${error.message}`);
  } finally {
    state.executingAgentTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handleExecuteAgentTask(taskId) {
  if (!state.selectedProjectId || !taskId) return;
  clearV2Error("overview");
  state.executingAgentTaskId = taskId;
  renderAgentTaskQueue();
  try {
    const queue = state.agentTaskQueueData?.agent_task_queue;
    const task = queue?.tasks?.find((t) => t.id === taskId);
    if (task) {
      onTaskDispatchedForExecution(task);
    }

    state.agentTaskQueueData = await v2api.agentTaskQueue.execute(state.selectedProjectId, taskId);
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `执行失败：${error.message}`);
  } finally {
    state.executingAgentTaskId = null;
    renderAgentTaskQueue();
  }
}

async function handleGenerateSupervisorPlan() {
  if (!state.selectedProjectId) return;
  clearV2Error("overview");
  state.generatingSupervisorPlan = true;
  renderSupervisorPlan();
  try {
    state.supervisorPlanData = await v2api.supervisorPlan.generate(state.selectedProjectId, {
      objective: "基于已确认变量角色、研究设计和执行计划，生成下一轮可审阅研究执行计划。",
      note: "用户请求 P2-P：先由本地 Codex Supervisor 提出计划，再进入人工确认。",
    });
    state.overviewData = await v2api.overview.get(state.selectedProjectId);
    state.agentTaskQueueData = await v2api.agentTaskQueue.get(state.selectedProjectId);
    renderWorkflowContract(state.overviewData.workflow_contract);
    renderSupervisorPlan();
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `生成 SupervisorPlan 失败：${error.message}`);
  } finally {
    state.generatingSupervisorPlan = false;
    renderSupervisorPlan();
    renderAgentTaskQueue();
  }
}

async function handleReviewSupervisorPlan(action) {
  if (!state.selectedProjectId || !action) return;
  clearV2Error("overview");
  state.reviewingSupervisorPlanAction = action;
  renderSupervisorPlan();
  try {
    state.supervisorPlanData = await v2api.supervisorPlan.review(state.selectedProjectId, {
      action,
      note: `首页 SupervisorPlan 审阅台人工审批：${supervisorReviewActionLabel(action)}`,
    });
    state.overviewData = await v2api.overview.get(state.selectedProjectId);
    state.agentTaskQueueData = await v2api.agentTaskQueue.get(state.selectedProjectId);
    renderWorkflowContract(state.overviewData.workflow_contract);
    renderSupervisorPlan();
    renderAgentTaskQueue();
  } catch (error) {
    showV2Error("overview", `审批 SupervisorPlan 失败：${error.message}`);
  } finally {
    state.reviewingSupervisorPlanAction = null;
    renderSupervisorPlan();
    renderAgentTaskQueue();
  }
}

function renderEvidenceBanner(meta) {
  if (!meta || meta.evidence_level !== "mock") return "";
  return `
    <div class="evidence-banner">
      <span>⚠</span>
      <span>当前展示的是演示数据（${meta.service || ""}），不代表真实研究结论。</span>
    </div>
  `;
}

function showV2Error(viewId, message) {
  const el = document.getElementById(`${viewId}-error`);
  if (!el) return;
  el.style.display = "flex";
  el.innerHTML = `<span>${escapeHtml(message)}</span><button class="ghost-button" style="padding:4px 10px;font-size:12px;" onclick="this.parentElement.style.display='none'">关闭</button>`;
}

function clearV2Error(viewId) {
  const el = document.getElementById(`${viewId}-error`);
  if (!el) return;
  el.style.display = "none";
  el.innerHTML = "";
  el.classList.remove("is-success");
}

function showV2Success(viewId, message) {
  const el = document.getElementById(`${viewId}-error`);
  if (!el) return;
  el.style.display = "flex";
  el.classList.add("is-success");
  el.innerHTML = `<span>${escapeHtml(message)}</span><button class="ghost-button" style="padding:4px 10px;font-size:12px;" onclick="this.parentElement.style.display='none'">关闭</button>`;
}

function renderEmptyState(emptyState) {
  if (!emptyState) return "";
  return `
    <div class="empty-state">
      <div class="empty-state-icon">📭</div>
      <h4>${escapeHtml(emptyState.title)}</h4>
      <p class="muted">${escapeHtml(emptyState.description)}</p>
      ${emptyState.next_action ? `<p class="muted" style="margin-top:8px;"><strong>下一步：</strong>${escapeHtml(emptyState.next_action)}</p>` : ""}
    </div>
  `;
}

function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("zh-CN");
}

function formatMetadata(metadata) {
  if (!metadata || Object.keys(metadata).length === 0) {
    return "<p class='muted'>无元数据</p>";
  }
  return `<pre class="metadata-box">${escapeHtml(JSON.stringify(metadata, null, 2))}</pre>`;
}

function observableStatusLabel(status) {
  const map = {
    queued: "排队",
    running: "运行中",
    succeeded: "成功",
    failed: "失败",
    completed: "已完成",
    skipped: "已跳过",
    open: "待确认",
    resolved: "已处理",
  };
  return map[status] || status || "-";
}

function getLatestRun(runs) {
  return [...runs].sort((a, b) => {
    const aTime = new Date(a.started_at || a.finished_at || 0).getTime();
    const bTime = new Date(b.started_at || b.finished_at || 0).getTime();
    return bTime - aTime;
  })[0] || null;
}

function renderObservableExecutionEmpty(message = "当前项目还没有运行记录。") {
  renderExecutionPreflight();
  document.getElementById("run-selector").innerHTML = "";
  document.getElementById("observable-run-id").textContent = "尚未选择 run";
  document.getElementById("observable-run-status").textContent = "-";
  document.getElementById("observable-run-mode").textContent = "-";
  document.getElementById("observable-run-evidence").textContent = "-";
  document.getElementById("observable-run-time").textContent = message;
  const datasetContainer = document.getElementById("observable-dataset-source-body");
  if (datasetContainer) {
    datasetContainer.innerHTML = "<p class='muted'>未记录数据来源。请从数据页选择本地数据后重新启动运行。</p>";
  }
  const variableRolesContainer = document.getElementById("observable-variable-roles-body");
  if (variableRolesContainer) {
    variableRolesContainer.innerHTML = "<p class='muted'>未记录变量角色。请从数据页选择本地数据后重新启动运行。</p>";
  }
  const methodExecutionContainer = document.getElementById("observable-method-execution-body");
  if (methodExecutionContainer) {
    methodExecutionContainer.innerHTML = "<p class='muted'>尚未生成方法执行证据。完成 full run 后会显示 OLS 执行结果。</p>";
  }
  document.getElementById("observable-step-board").innerHTML = renderEmptyState({
    title: "暂无可观察阶段",
    description: message,
    next_action: "完成执行计划后启动正式执行；开发阶段可使用“开发试运行”生成可观察轨迹。",
  });
  document.getElementById("observable-event-stream").innerHTML = "<p class='muted'>暂无事件流</p>";
  document.getElementById("observable-hitl-gates").innerHTML = "<p class='muted'>暂无人工确认点</p>";
  document.getElementById("observable-artifact-evidence").innerHTML = "<p class='muted'>暂无产物证据</p>";
}

function renderExecutionPreflight() {
  const contract = getWorkflowContract();
  const preflight = document.getElementById("run-plan-preflight-body");
  const blockersContainer = document.getElementById("run-blockers-body");
  if (!preflight || !blockersContainer) return;

  if (!contract) {
    preflight.innerHTML = "<p class='muted'>正在读取工作流契约...</p>";
    blockersContainer.innerHTML = "<p class='muted'>等待执行预检。</p>";
    return;
  }

  const readiness = contract.run_readiness || {};
  const canStart = Boolean(readiness.can_start_full_run);
  const blockers = readiness.blockers || [];
  preflight.innerHTML = `
    <div class="run-preflight-summary ${canStart ? "is-ready" : "is-blocked"}">
      <div>
        <span class="eyebrow">can_start_full_run=${String(canStart)}</span>
        <h4>${canStart ? "可以启动完整实证运行" : "完整实证运行暂不可启动"}</h4>
        <p class="muted">执行入口必须先有已确认的变量角色、研究设计和执行计划。现有运行日志只作为执行证据。</p>
      </div>
      <span class="status-pill ${canStart ? "status-completed" : "status-open"}">${canStart ? "已就绪" : "已阻塞"}</span>
    </div>
  `;
  blockersContainer.innerHTML = blockers.length
    ? blockers.map((blocker) => `
        <div class="run-blocker-item">
          <strong>${escapeHtml(WORKFLOW_BLOCKER_LABELS[blocker] || blocker)}</strong>
          <span class="muted">${escapeHtml(blocker)}</span>
        </div>
      `).join("")
    : "<p class='muted'>当前没有阻塞项。</p>";

  const dryRunButton = document.getElementById("observable-run-dry-button");
  if (dryRunButton) {
    dryRunButton.classList.toggle("is-development-shortcut", !canStart);
    dryRunButton.title = canStart ? "启动当前执行计划" : "开发捷径：用于验证可观察轨迹，不代表完整产品执行路径";
  }
  const fullRunButton = document.getElementById("observable-run-full-button");
  if (fullRunButton) {
    fullRunButton.disabled = !canStart;
    fullRunButton.dataset.workflowAction = "start_full_run";
    fullRunButton.title = canStart ? "从已确认执行计划启动完整实证执行" : "需要先确认变量角色集、研究设计方案和执行计划";
  }
}

function renderObservableDatasetSource() {
  const container = document.getElementById("observable-dataset-source-body");
  if (!container) return;

  const observability = state.runObservability;
  const dataset = observability ? observability.dataset_source || observability.manifest?.dataset_source : null;
  if (!dataset) {
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>未记录数据来源</h4>
        <p class="muted">这个运行没有记录数据来源。请从数据页选择本地数据后重新启动运行。</p>
      </div>
    `;
    return;
  }

  const shapeText =
    dataset.row_count !== null && dataset.row_count !== undefined && dataset.column_count !== null && dataset.column_count !== undefined
      ? `${dataset.row_count} 行 · ${dataset.column_count} 列`
      : "未读取行列数";
  container.innerHTML = `
    <article class="dataset-source-card">
      <div class="observable-card-head">
        <div>
          <strong>${escapeHtml(dataset.name || dataset.path || "数据集")}</strong>
          <div class="muted">${escapeHtml(dataset.path || "-")}</div>
        </div>
        ${renderEvidenceBadge(dataset)}
      </div>
      <div class="dataset-source-meta">
        <span>${escapeHtml(shapeText)}</span>
        <span>${escapeHtml(dataset.file_type || "-")}</span>
        <span>${escapeHtml(dataset.role || "已选择数据集")}</span>
        <span>是否存在：${yesNo(dataset.exists)}</span>
      </div>
    </article>
  `;
}

function renderVariableRoleGroup(label, values) {
  const items = values && values.length ? values : ["未识别"];
  return `
    <div class="variable-role-group">
      <span class="meta-label">${escapeHtml(label)}</span>
      <div class="observable-option-list">
        ${items.map((item) => `<span class="pill">${escapeHtml(item)}</span>`).join("")}
      </div>
    </div>
  `;
}

function renderObservableVariableRoles() {
  const container = document.getElementById("observable-variable-roles-body");
  if (!container) return;

  const observability = state.runObservability;
  const variableRoles = observability ? observability.variable_roles : null;
  if (!variableRoles) {
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>未记录变量角色</h4>
        <p class="muted">这个运行没有记录变量角色。请从数据页选择本地数据后重新启动运行。</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <article class="variable-roles-card">
      <div class="observable-card-head">
        <div>
          <strong>字段角色</strong>
          <div class="muted">确认点：${escapeHtml(variableRoles.confirmation_gate_id || "-")} · 状态：${observableStatusLabel(variableRoles.confirmation_status || "-")}</div>
        </div>
        ${renderEvidenceBadge({ evidence_level: variableRoles.evidence_level })}
      </div>
      <div class="variable-roles-grid">
        ${renderVariableRoleGroup("结果变量", variableRoles.roles.outcome)}
        ${renderVariableRoleGroup("处理变量", variableRoles.roles.treatment)}
        ${renderVariableRoleGroup("控制变量", variableRoles.roles.controls)}
        ${renderVariableRoleGroup("工具变量", variableRoles.roles.instruments)}
      </div>
    </article>
  `;
}

function renderObservableMethodExecution() {
  const container = document.getElementById("observable-method-execution-body");
  if (!container) return;

  const observability = state.runObservability;
  const methodExecution = observability ? observability.method_execution || observability.manifest?.method_execution : null;
  const contract = methodExecution?.execution_contract || null;
  if (!methodExecution) {
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>尚未生成方法执行证据</h4>
        <p class="muted">这个运行没有记录 OLS 方法执行结果。请从已确认执行计划启动完整实证执行。</p>
      </div>
    `;
    return;
  }

  const methods = methodExecution.methods || [];
  container.innerHTML = `
    <div class="method-execution-summary">
      <div>
        <span class="meta-label">执行引擎</span>
        <strong>${escapeHtml(methodExecution.engine || "-")}</strong>
      </div>
      <div>
        <span class="meta-label">产物路径</span>
        <code>${escapeHtml(methodExecution.artifact_path || "-")}</code>
      </div>
      ${renderEvidenceBadge({ evidence_level: methodExecution.evidence_level || "local_execution" })}
    </div>
    ${renderMethodExecutionContract(contract)}
    ${methods.length ? methods.map((method) => `
      <article class="method-execution-card">
        <div class="observable-card-head">
          <div>
            <strong>${escapeHtml(productTermLabel(method.method_id || method.estimator || "method"))}</strong>
            <div class="muted">${escapeHtml(method.task_id || "baseline_regression")} · ${escapeHtml(method.dataset_path || "-")}</div>
          </div>
          ${renderEvidenceBadge({ evidence_level: method.evidence_level || methodExecution.evidence_level || "local_execution" })}
        </div>
        <div class="method-execution-grid">
          <div><span class="meta-label">模型公式</span><strong>${escapeHtml(method.formula || "-")}</strong></div>
          <div><span class="meta-label">样本量</span><strong>${escapeHtml(String(method.nobs ?? "-"))}</strong></div>
          <div><span class="meta-label">处理变量</span><strong>${escapeHtml(method.treatment || "-")}</strong></div>
          <div><span class="meta-label">处理变量系数</span><strong>${formatNumber(method.treatment_coefficient)}</strong></div>
        </div>
        ${renderMethodDataPreflight(method.data_preflight)}
        ${renderMethodReproducibility(method.reproducibility)}
        ${renderMethodBackendValidations(method.backend_validations)}
      </article>
    `).join("") : "<p class='muted'>方法执行产物中没有 method item。</p>"}
  `;
}

function renderMethodExecutionContract(contract) {
  if (!contract) {
    return `
      <section class="method-contract-panel">
        <strong>严谨执行契约</strong>
        <p class="muted">尚未记录执行后端契约。</p>
      </section>
    `;
  }
  const backends = contract.available_backends || [];
  return `
    <section class="method-contract-panel">
      <div class="method-contract-head">
        <div>
          <span class="meta-label">严谨执行契约</span>
          <strong>当前执行后端：${escapeHtml(contract.active_backend || "-")}</strong>
          <p class="muted">分析边界：${escapeHtml(contract.analysis_boundary || "-")}</p>
        </div>
      </div>
      <div class="method-backend-list">
        ${backends.map((backend) => `
          <div class="method-backend-item">
            <strong>${escapeHtml(backend.label || backend.id)}</strong>
            <span>${escapeHtml(backend.role || "-")} · ${escapeHtml(backend.availability_status || "-")}</span>
            ${renderEvidenceBadge({ evidence_level: backend.evidence_level || "local_file" })}
          </div>
        `).join("") || "<p class='muted'>暂无候选后端。</p>"}
      </div>
      <div class="muted">候选后端：StatsPAI/StatsAPI 与 StataMCP/Stata 只有在真实调用并写出产物后，才能升级为 local_execution。</div>
    </section>
  `;
}

function renderMethodDataPreflight(data_preflight) {
  if (!data_preflight) {
    return "<div class='method-subpanel'><strong>数据预检</strong><p class='muted'>尚未记录数据预检。</p></div>";
  }
  const checks = data_preflight.checks || [];
  return `
    <div class="method-subpanel">
      <strong>数据预检</strong>
      <div class="method-preflight-grid">
        <div><span class="meta-label">读取行数</span><strong>${escapeHtml(String(data_preflight.rows_read ?? "-"))}</strong></div>
        <div><span class="meta-label">可用数值行</span><strong>${escapeHtml(String(data_preflight.usable_numeric_rows ?? "-"))}</strong></div>
        <div><span class="meta-label">丢弃行数</span><strong>${escapeHtml(String(data_preflight.dropped_rows ?? "-"))}</strong></div>
        <div><span class="meta-label">必需字段</span><strong>${escapeHtml((data_preflight.required_fields || []).join(", ") || "-")}</strong></div>
      </div>
      <div class="method-check-list">
        ${checks.map((check) => `
          <span class="method-check is-${escapeHtml(check.status || "unknown")}">${escapeHtml(check.label || check.id)} · ${escapeHtml(check.status || "-")}</span>
        `).join("")}
      </div>
    </div>
  `;
}

function renderMethodReproducibility(reproducibility) {
  if (!reproducibility) {
    return "<div class='method-subpanel'><strong>可复现入口</strong><p class='muted'>尚未记录可复现执行说明。</p></div>";
  }
  return `
    <div class="method-subpanel">
      <strong>可复现入口</strong>
      <div class="method-preflight-grid">
        <div><span class="meta-label">适配器</span><strong>${escapeHtml(reproducibility.adapter || "-")}</strong></div>
        <div><span class="meta-label">RunPlan 版本</span><strong>${escapeHtml(String(reproducibility.run_plan_version ?? "-"))}</strong></div>
        <div><span class="meta-label">结果产物</span><code>${escapeHtml(reproducibility.result_artifact_path || "-")}</code></div>
        <div><span class="meta-label">源码入口</span><code>${escapeHtml(reproducibility.source_entrypoint || "-")}</code></div>
      </div>
    </div>
  `;
}

function renderMethodBackendValidations(backend_validations) {
  const validations = Array.isArray(backend_validations) ? backend_validations : [];
  if (!validations.length) {
    return "<div class='method-subpanel'><strong>独立后端验证</strong><p class='muted'>尚未记录 StatsPAI / StatsAPI 或 Stata 的独立验证结果。</p></div>";
  }
  return `
    <div class="method-subpanel">
      <strong>独立后端验证</strong>
      <div class="method-validation-list">
        ${validations.map((validation) => `
          <div class="method-validation-item is-${escapeHtml(validation.status || "unknown")}">
            <div>
              <span class="meta-label">${escapeHtml(validation.backend_label || validation.backend_id || "StatsPAI / StatsAPI")}</span>
              <strong>${escapeHtml(validation.status || "-")}</strong>
              <p class="muted">${escapeHtml(validation.adapter || "statspai.regress")} · <code>${escapeHtml(validation.artifact_path || "Results/json/statspai_execution_result.json")}</code></p>
            </div>
            ${renderEvidenceBadge({ evidence_level: validation.evidence_level || "local_file" })}
            <div class="method-check-list">
              ${(validation.checks || []).map((check) => `
                <span class="method-check is-${escapeHtml(check.status || "unknown")}">
                  ${escapeHtml(check.id === "treatment_coefficient_cross_check" ? "treatment_coefficient_cross_check" : (check.label || check.id))}
                  · ${escapeHtml(check.status || "-")}
                </span>
              `).join("")}
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function renderRunSelector() {
  const selector = document.getElementById("run-selector");
  if (!selector) return;

  selector.innerHTML = state.projectRuns.length
    ? state.projectRuns.map((run) => `
        <option value="${escapeHtml(run.id)}" ${run.id === state.selectedRunId ? "selected" : ""}>
          ${escapeHtml(run.id)} · ${escapeHtml(run.status)} · ${escapeHtml(run.mode)}
        </option>
      `).join("")
    : `<option value="">暂无运行</option>`;
}

function renderObservableRunHeader() {
  const run = state.projectRuns.find((item) => item.id === state.selectedRunId);
  const observability = state.runObservability;
  const meta = observability?._meta || observability?.manifest?._meta || { evidence_level: "local_execution" };

  if (!run && !observability) {
    renderObservableExecutionEmpty();
    return;
  }

  document.getElementById("observable-run-id").textContent = state.selectedRunId || "-";
  document.getElementById("observable-run-status").textContent = observableStatusLabel(run?.status || observability?.manifest?.status);
  document.getElementById("observable-run-mode").textContent = run?.mode || observability?.manifest?.mode || "-";
  document.getElementById("observable-run-evidence").innerHTML = renderEvidenceBadge(meta) || "-";
  document.getElementById("observable-run-time").textContent =
    `开始：${formatDateTime(run?.started_at || observability?.manifest?.started_at)} · 结束：${formatDateTime(run?.finished_at || observability?.manifest?.finished_at)} · 产物：${run?.artifact_count ?? observability?.manifest?.artifact_count ?? 0}`;
}

function renderObservableSteps() {
  const steps = state.runObservability?.steps?.items || [];
  const container = document.getElementById("observable-step-board");
  if (!container) return;

  if (!steps.length) {
    container.innerHTML = "<p class='muted'>该运行尚无阶段记录。</p>";
    return;
  }

  container.innerHTML = steps.map((step) => {
    const actor = step.actor || "系统";
    const statusClass = `status-${step.status || "unknown"}`;
    return `
      <article class="observable-step-card">
        <div class="observable-card-head">
          <div>
            <strong>${escapeHtml(step.title || step.id)}</strong>
            <div class="muted">${escapeHtml(step.id)} · 执行者：${escapeHtml(actor)}</div>
          </div>
          <span class="status-pill ${statusClass}">${observableStatusLabel(step.status)}</span>
        </div>
        <p>${escapeHtml(step.summary || step.description || "等待执行摘要。")}</p>
        <div class="muted">开始：${formatDateTime(step.started_at)} · 结束：${formatDateTime(step.finished_at)}</div>
        ${formatMetadata(step.metadata)}
      </article>
    `;
  }).join("");
}

function renderObservableEvents() {
  const events = [...(state.runObservability?.events?.items || [])]
    .sort((a, b) => (a.sequence || 0) - (b.sequence || 0));
  const container = document.getElementById("observable-event-stream");
  if (!container) return;

  if (!events.length) {
    container.innerHTML = "<p class='muted'>该运行尚无事件。</p>";
    return;
  }

  container.innerHTML = events.map((event) => `
    <div class="observable-event-item">
      <div class="observable-event-seq">#${event.sequence ?? "-"}</div>
      <div class="observable-event-body">
        <div class="observable-card-head">
          <strong>${escapeHtml(event.type || "event")}</strong>
          ${renderEvidenceBadge({ evidence_level: event.evidence_level || state.runObservability?._meta?.evidence_level })}
        </div>
        <div>${escapeHtml(event.message || "")}</div>
        <div class="muted">执行者：${escapeHtml(event.actor || "系统")} · 步骤：${escapeHtml(event.step_id || "-")} · ${formatDateTime(event.timestamp)}</div>
      </div>
    </div>
  `).join("");
}

function renderResolvedGateResolution(gate) {
  const resolution = gate.resolution || {};
  return `
    <div class="gate-resolution">
      <strong>处理结果</strong>
      <div class="muted">动作：${escapeHtml(resolution.action || "-")} · 处理时间：${formatDateTime(resolution.resolved_at)}</div>
      <div>${escapeHtml(resolution.note || "未填写处理说明。")}</div>
    </div>
  `;
}

function renderGateResolveControls(gate) {
  if (gate.status === "resolved") {
    return renderResolvedGateResolution(gate);
  }

  const isResolving = state.resolvingGateId === gate.id;
  const disabled = isResolving ? "disabled" : "";
  const busyLabel = isResolving ? "处理中..." : "";
  return `
    <label class="gate-note-label" for="gate-note-${escapeHtml(gate.id)}">处理说明</label>
    <textarea
      class="gate-resolution-note"
      id="gate-note-${escapeHtml(gate.id)}"
      data-gate-note="${escapeHtml(gate.id)}"
      placeholder="记录确认、驳回或调整的原因"
      ${disabled}
    ></textarea>
    <div class="action-group">
      <button class="ghost-button" data-gate-id="${escapeHtml(gate.id)}" data-gate-resolve-action="confirm" ${disabled}>确认</button>
      <button class="ghost-button" data-gate-id="${escapeHtml(gate.id)}" data-gate-resolve-action="reject" ${disabled}>驳回</button>
      <button class="ghost-button" data-gate-id="${escapeHtml(gate.id)}" data-gate-resolve-action="adjust" ${disabled}>调整</button>
      ${busyLabel ? `<span class="muted">${busyLabel}</span>` : ""}
    </div>
  `;
}

function renderObservableGates() {
  const gates = state.runObservability?.gates?.items || [];
  const container = document.getElementById("observable-hitl-gates");
  if (!container) return;

  if (!gates.length) {
    container.innerHTML = "<p class='muted'>该运行暂无人工介入点。</p>";
    return;
  }

  container.innerHTML = gates.map((gate) => `
    <article class="observable-gate-card ${gate.blocking ? "is-blocking" : ""}">
      <div class="observable-card-head">
        <div>
          <strong>${escapeHtml(gate.title || gate.id)}</strong>
          <div class="muted">${escapeHtml(gate.id)} · 步骤：${escapeHtml(gate.step_id || "-")}</div>
        </div>
        <span class="status-pill status-${escapeHtml(gate.status || "open")}">${observableStatusLabel(gate.status)}</span>
      </div>
      <p>${escapeHtml(gate.reason || "等待用户确认。")}</p>
      <div class="muted">要求方：${escapeHtml(gate.required_by || "-")} · 是否阻塞：${yesNo(Boolean(gate.blocking))}</div>
      <div class="observable-option-list">
        ${(gate.options || []).map((option) => `<span class="pill">${escapeHtml(option)}</span>`).join("")}
      </div>
      ${formatMetadata(gate.metadata)}
      ${renderGateResolveControls(gate)}
    </article>
  `).join("");
}

function collectObservableArtifacts() {
  const evidenceLevel = state.runObservability?._meta?.evidence_level || "local_execution";
  const fromEvents = (state.runObservability?.events?.items || [])
    .filter((event) => event.type === "artifact_written")
    .map((event) => ({
      path: event.metadata?.path || event.metadata?.artifact_path || event.message,
      source: event.step_id || "event",
      actor: event.actor || "系统",
      evidence_level: event.evidence_level || evidenceLevel,
    }));
  const fromSteps = (state.runObservability?.steps?.items || []).flatMap((step) =>
    (step.artifacts || []).map((artifact) => ({
      path: typeof artifact === "string" ? artifact : artifact.path || artifact.id,
      source: step.id,
      actor: step.actor || "系统",
      evidence_level: artifact.evidence_level || evidenceLevel,
    })),
  );

  const seen = new Set();
  return [...fromEvents, ...fromSteps].filter((artifact) => {
    const key = `${artifact.path}|${artifact.source}`;
    if (!artifact.path || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function renderObservableArtifactEvidence() {
  const container = document.getElementById("observable-artifact-evidence");
  if (!container) return;

  const artifacts = collectObservableArtifacts();
  const meta = state.runObservability?._meta || { evidence_level: "local_execution" };
  if (!artifacts.length) {
    container.innerHTML = `
      ${renderEvidenceBadge(meta)}
      <p class="muted">该运行暂无产物写入事件或阶段产物。</p>
    `;
    return;
  }

  container.innerHTML = `
    <div style="margin-bottom:12px;">${renderEvidenceBadge(meta)}</div>
    ${artifacts.map((artifact) => `
      <article class="project-card">
        <strong>${escapeHtml(artifact.path)}</strong>
        <div class="muted">来源：${escapeHtml(artifact.source)} · 执行者：${escapeHtml(artifact.actor)}</div>
        ${renderEvidenceBadge({ evidence_level: artifact.evidence_level })}
      </article>
    `).join("")}
  `;
}

function renderObservableExecution() {
  renderExecutionPreflight();
  if (state.runObservabilityLoading) {
    document.getElementById("observable-step-board").innerHTML = "<p class='muted'>正在读取运行可观察轨迹...</p>";
    return;
  }
  renderRunSelector();
  renderObservableRunHeader();
  renderObservableDatasetSource();
  renderObservableVariableRoles();
  renderObservableMethodExecution();
  renderObservableSteps();
  renderObservableEvents();
  renderObservableGates();
  renderObservableArtifactEvidence();
}

function handleMissingRunObservability(runId) {
  state.runObservability = null;
  renderRunSelector();

  const run = state.projectRuns.find((item) => item.id === runId);
  document.getElementById("observable-run-id").textContent = runId || "尚未选择 run";
  document.getElementById("observable-run-time").textContent = run
    ? `开始：${formatDateTime(run.started_at)} · 结束：${formatDateTime(run.finished_at)} · 产物：${run.artifact_count || 0}`
    : "该运行记录缺少可观察执行轨迹";
  document.getElementById("observable-run-status").textContent = observableStatusLabel(run?.status || "missing_observability");
  document.getElementById("observable-run-mode").textContent = run?.mode || "-";
  document.getElementById("observable-run-evidence").innerHTML = renderEvidenceBadge({ evidence_level: "local_file" });
  renderObservableDatasetSource();
  renderObservableVariableRoles();
  renderObservableMethodExecution();

  document.getElementById("observable-step-board").innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">📭</div>
      <h4>缺少可观察执行轨迹</h4>
      <p class="muted">这个历史运行没有 state/runs 下的清单、阶段、事件或确认点文件。</p>
      <p class="muted"><strong>下一步：</strong>完成执行计划后启动正式执行；开发调试可生成新的可观察运行。</p>
    </div>
  `;
  document.getElementById("observable-event-stream").innerHTML = "<p class='muted'>缺少 run_events.jsonl</p>";
  document.getElementById("observable-hitl-gates").innerHTML = "<p class='muted'>缺少 gates.json</p>";
  document.getElementById("observable-artifact-evidence").innerHTML = "<p class='muted'>完成执行计划后会产生新的可观察运行。</p>";
}

async function loadRunObservability(projectId, runId) {
  if (!projectId || !runId) {
    state.runObservability = null;
    renderObservableExecutionEmpty();
    return;
  }

  state.runObservabilityLoading = true;
  renderObservableExecution();
  try {
    state.runObservability = await v2api.runs.observability(projectId, runId);
  } catch (error) {
    if (error.status === 404) {
      state.runObservabilityLoading = false;
      handleMissingRunObservability(runId);
      return;
    }
    throw error;
  } finally {
    state.runObservabilityLoading = false;
  }
  renderObservableExecution();
}

async function loadObservableExecution() {
  if (!state.selectedProjectId) return;

  clearV2Error("empirical-execution");
  const payload = await v2api.runs.list(state.selectedProjectId);
  state.projectRuns = payload.items || [];

  if (!state.projectRuns.length) {
    state.selectedRunId = null;
    state.runObservability = null;
    renderObservableExecutionEmpty();
    return;
  }

  if (!state.projectRuns.find((run) => run.id === state.selectedRunId)) {
    state.selectedRunId = getLatestRun(state.projectRuns)?.id || null;
  }
  renderRunSelector();
  await loadRunObservability(state.selectedProjectId, state.selectedRunId);
}

async function createObservableRun(mode, datasetPath = state.selectedDatasetPath) {
  if (!state.selectedProjectId) return;

  clearV2Error("empirical-execution");
  document.getElementById("observable-step-board").innerHTML = "<p class='muted'>正在启动真实试运行...</p>";
  const run = await v2api.runs.create(state.selectedProjectId, mode, datasetPath);
  state.selectedRunId = run.id;
  if (run.id) {
    void connectRunStream(run.id);
  }
  await loadObservableExecution();
  await refreshProjects();
}

async function createFullRunFromPlan() {
  if (!state.selectedProjectId) return;

  clearV2Error("empirical-execution");
  document.getElementById("observable-step-board").innerHTML = "<p class='muted'>正在按执行计划启动完整实证执行...</p>";
  try {
    const run = await v2api.runs.startFull(state.selectedProjectId);
    state.selectedRunId = run.id;
    if (run.id) {
      void connectRunStream(run.id);
    }
    await refreshProjects();
    state.overviewData = await v2api.overview.get(state.selectedProjectId);
    renderExecutionPreflight();
    await loadObservableExecution();
  } catch (error) {
    showV2Error("empirical-execution", `启动完整实证执行失败：${error.message}`);
  }
}

function openDesignAction(datasetPath) {
  if (datasetPath) {
    state.selectedDatasetPath = datasetPath;
  }
  const dataNav = document.querySelector('.nav-link[data-view="data-variables"]');
  if (dataNav instanceof HTMLElement && !document.getElementById("view-data-variables")?.classList.contains("is-active")) {
    dataNav.click();
    return;
  }
  renderVariableRoleWorkflow(state.datasetsData?.items || []);
  document.getElementById("variable-role-workflow-card")?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

async function startObservableRunForDataset(datasetPath) {
  if (!datasetPath) return;
  state.selectedDatasetPath = datasetPath;
  const executionNav = document.querySelector('.nav-link[data-view="empirical-execution"]');
  if (executionNav instanceof HTMLElement) {
    executionNav.click();
  }
  await createObservableRun("dry-run", datasetPath);
}

async function resolveObservableGate(gateId, action) {
  if (!state.selectedProjectId || !state.selectedRunId || !gateId) return;
  if (!["confirm", "reject", "adjust"].includes(action)) return;

  const noteNode = Array.from(document.querySelectorAll("[data-gate-note]"))
    .find((node) => node.dataset.gateNote === gateId);
  const note = noteNode?.value?.trim() || "";

  clearV2Error("empirical-execution");
  state.resolvingGateId = gateId;
  state.resolvingGateAction = action;
  renderObservableGates();
  try {
    await v2api.runs.resolveGate(state.selectedProjectId, state.selectedRunId, gateId, action, note);
    await loadRunObservability(state.selectedProjectId, state.selectedRunId);
  } catch (error) {
    showV2Error("empirical-execution", `处理 gate 失败：${error.message}`);
  } finally {
    state.resolvingGateId = null;
    state.resolvingGateAction = null;
    renderObservableGates();
  }
}

async function connectRunStream(runId, resetOutput = true) {
  disconnectRunStream();
  if (!state.selectedProjectId || !runId) return;

  state.sseConnection.runId = runId;
  state.sseConnection.connected = false;
  if (resetOutput) {
    state.sseConnection.reconnectAttempts = 0;
    state.agentOutput.lines = [];
    state.agentOutput.currentStage = null;
    state.agentOutput.currentAgent = null;
  }
  state.agentOutput.visible = true;
  renderAgentOutputPanel();

  const es = await v2api.runs.stream(state.selectedProjectId, runId, (event) => {
    handleRunEvent(event);
  });

  state.sseConnection.eventSource = es;
}

function disconnectRunStream() {
  if (state.sseConnection.eventSource) {
    state.sseConnection.eventSource.close();
    state.sseConnection.eventSource = null;
  }
  state.sseConnection.connected = false;
  state.sseConnection.runId = null;
}

function scheduleRunStreamReconnect() {
  const runId = state.sseConnection.runId;
  if (!runId || state.sseConnection.reconnectAttempts >= 5) return;
  const attempt = state.sseConnection.reconnectAttempts + 1;
  state.sseConnection.reconnectAttempts = attempt;
  const delayMs = Math.min(30000, 1000 * (2 ** (attempt - 1)));
  window.setTimeout(() => {
    if (!state.sseConnection.connected && state.selectedProjectId) {
      void connectRunStream(runId, false);
    }
  }, delayMs);
}

function handleRunEvent(event) {
  switch (event.type) {
    case "connected":
      state.sseConnection.connected = true;
      state.sseConnection.reconnectAttempts = 0;
      break;
    case "run.started":
      addAgentOutputLine(event.data.timestamp, "system", `运行开始：${event.data.payload?.mode || ""}`);
      break;
    case "stage.start":
      state.agentOutput.currentStage = event.data.stage;
      state.agentOutput.currentAgent = event.data.agent_name;
      addAgentOutputLine(
        event.data.timestamp,
        "system",
        `${event.data.agent_name} 开始执行 ${stageNameCN(event.data.stage)}`,
      );
      updateJourneyStageStatus(event.data.stage, "running");
      break;
    case "stage.output":
      addAgentOutputLine(
        event.data.timestamp,
        event.data.payload?.source || "log",
        event.data.payload?.chunk || "",
      );
      break;
    case "stage.complete": {
      const statusLabel = event.data.payload?.status === "succeeded" ? "完成" : "失败";
      addAgentOutputLine(
        event.data.timestamp,
        "system",
        `${event.data.agent_name} ${statusLabel} (${event.data.payload?.wall_seconds || 0}s)`,
      );
      updateJourneyStageStatus(
        event.data.stage,
        event.data.payload?.status === "succeeded" ? "completed" : "failed",
      );
      break;
    }
    case "checkpoint.pending":
      addAgentOutputLine(event.data.timestamp, "system", `检查点: ${event.data.payload?.title || ""}`);
      updateJourneyStageStatus(event.data.stage, "pending_confirmation");
      void pollCheckpoint();
      break;
    case "checkpoint.resolved":
      addAgentOutputLine(
        event.data.timestamp,
        "system",
        `检查点已处理: ${event.data.payload?.status || ""}`,
      );
      break;
    case "run.completed":
      addAgentOutputLine(event.data.timestamp, "system", "运行完成");
      disconnectRunStream();
      break;
    case "run.failed":
      addAgentOutputLine(event.data.timestamp, "system", `运行失败: ${event.data.payload?.error || ""}`);
      disconnectRunStream();
      break;
    case "error":
      state.sseConnection.connected = false;
      scheduleRunStreamReconnect();
      break;
  }
  renderAgentOutputPanel();
}

function addAgentOutputLine(timestamp, source, text) {
  state.agentOutput.lines.push({
    timestamp: timestamp ? new Date(timestamp).toLocaleTimeString("zh-CN") : "",
    source,
    text,
  });
  if (state.agentOutput.lines.length > 200) {
    state.agentOutput.lines = state.agentOutput.lines.slice(-200);
  }
}

function stageNameCN(stageId) {
  const map = {
    "00_intake": "选题解析",
    "01_sources": "数据源发现",
    "02_literature": "文献综述",
    "03_strategy": "识别策略",
    "04_modeling": "基线估计",
    "05_results": "结果整理",
    "06_writing": "写作",
    "07_review": "审阅",
    "08_final": "导出",
  };
  return map[stageId] || stageId;
}

function journeyStageIdForRunStage(stageId) {
  const map = {
    "00_intake": "question-definition",
    "01_sources": "data-readiness",
    "02_literature": "literature-review",
    "03_strategy": "identification-design",
    "04_modeling": "baseline-estimation",
    "05_results": "robustness",
    "06_writing": "manuscript-drafting",
    "07_review": "submission-prep",
    "08_final": "submission-prep",
  };
  return map[stageId] || stageId;
}

function updateJourneyStageStatus(stageId, status) {
  const journeyStageId = journeyStageIdForRunStage(stageId);
  if (state.overviewData) {
    const summaries = state.overviewData.stage_summaries || [];
    state.overviewData.stage_summaries = summaries;
    const existing = summaries.find((item) => item.stage_id === journeyStageId || item.stage_id === stageId);
    if (existing) {
      existing.status = status;
    } else {
      summaries.push({ stage_id: journeyStageId, title: stageNameCN(stageId), status });
    }
    renderJourney();
  }
  if (state.journeyData?.stages) {
    const stage = state.journeyData.stages.find((item) => item.id === journeyStageId || item.stage_id === journeyStageId);
    if (stage) stage.status = status;
    renderJourneyBar();
  }
}

function renderAgentOutputPanel() {
  const panel = document.getElementById("agent-output-panel");
  if (!panel) return;

  if (!state.agentOutput.visible) {
    panel.style.display = "none";
    return;
  }

  panel.style.display = "flex";
  const linesHtml = state.agentOutput.lines.map((line) => {
    const sourceClass = line.source === "llm" ? "is-llm"
      : line.source === "statspai" ? "is-statspai"
      : line.source === "system" ? "is-system"
      : "is-log";
    return `<div class="agent-output-line ${sourceClass}">
      <span class="agent-output-time">${escapeHtml(line.timestamp)}</span>
      <span class="agent-output-source">${escapeHtml(line.source)}</span>
      <span class="agent-output-text">${escapeHtml(line.text)}</span>
    </div>`;
  }).join("");

  panel.innerHTML = `
    <div class="agent-output-header">
      <strong>Agent 实时输出</strong>
      <span class="agent-output-status ${state.sseConnection.connected ? "is-connected" : "is-disconnected"}">
        ${state.sseConnection.connected ? "● 实时连接中" : "○ 已断开"}
      </span>
      <button class="ghost-button" data-close-agent-output>关闭</button>
    </div>
    <div class="agent-output-body">
      ${linesHtml}
    </div>
  `;

  const body = panel.querySelector(".agent-output-body");
  if (body) body.scrollTop = body.scrollHeight;
}

// --- Journey Bar ---

function renderJourneyBar() {
  const container = document.getElementById("journey-bar");
  const content = document.getElementById("journey-bar-content");
  if (!container || !content) return;

  const journey = state.journeyData;
  if (!journey || !journey.stages) {
    container.style.display = "none";
    return;
  }

  container.style.display = "block";
  const stages = journey.stages;

  content.innerHTML = stages.map((stage, index) => {
    const statusClass = stage.status === "completed" ? "is-completed"
      : stage.status === "running" ? "is-running"
      : stage.status === "in_progress" ? "is-current"
      : stage.status === "pending_confirmation" ? "is-pending"
      : stage.status === "failed" ? "is-failed"
      : "";
    const arrow = index < stages.length - 1 ? `<span class="journey-arrow">→</span>` : "";
    return `
      <a class="journey-stage ${statusClass}" href="${escapeHtml(stage.href || "#")}" data-jump-view="${escapeHtml(stage.href?.replace("#view-", "") || "")}">
        <span class="journey-dot"></span>
        <span class="journey-label">${escapeHtml(productTermLabel(stage.name))}</span>
      </a>
      ${arrow}
    `;
  }).join("");
}

// --- Overview Page ---

function researchTopicStorageKey() {
  return `empirical-workbench.research-topic.${state.selectedProjectId || "default"}`;
}

function existingResearchTopic(data = state.overviewData) {
  return data?.research_question_state?.question || data?.research_question || data?.project?.title || "";
}

function loadResearchQuestionState(data = state.overviewData) {
  const questionState = state.researchQuestionData?.research_question || data?.research_question_state || null;
  if (questionState?.status === "confirmed" && questionState.question) {
    state.researchTopicConfirmed = true;
    state.researchTopicDraft = questionState.question;
  }
  return questionState;
}

function loadResearchTopicState() {
  const backendQuestion = loadResearchQuestionState();
  if (backendQuestion?.status === "confirmed") return;
  try {
    const raw = window.localStorage.getItem(researchTopicStorageKey());
    if (!raw) {
      if (state.researchTopicConfirmed && state.researchTopicDraft) return;
      state.researchTopicConfirmed = false;
      state.researchTopicDraft = "";
      return;
    }
    const saved = JSON.parse(raw);
    state.researchTopicConfirmed = Boolean(saved.confirmed);
    state.researchTopicDraft = saved.topic || "";
  } catch (error) {
    if (state.researchTopicConfirmed && state.researchTopicDraft) return;
    state.researchTopicConfirmed = false;
    state.researchTopicDraft = "";
  }
}

function saveResearchQuestionState(topic, backendQuestion = null) {
  state.researchTopicConfirmed = true;
  state.researchTopicDraft = topic;
  if (backendQuestion) {
    state.researchQuestionData = { research_question: backendQuestion };
  }
  try {
    window.localStorage.setItem(researchTopicStorageKey(), JSON.stringify({
      confirmed: true,
      topic,
      project_id: state.selectedProjectId,
      updated_at: new Date().toISOString(),
    }));
  } catch (error) {
    console.warn("Unable to persist research topic locally", error);
  }
}

function saveResearchTopicState(topic) {
  saveResearchQuestionState(topic);
}

function renderResearchTopicIntake(data = state.overviewData) {
  const intake = document.getElementById("research-topic-intake");
  const workbench = document.getElementById("research-workbench-after-topic");
  const input = document.getElementById("research-topic-input");
  const existing = document.getElementById("research-topic-existing");
  if (!intake || !workbench) return;

  loadResearchTopicState();
  const topic = state.researchTopicDraft || existingResearchTopic(data);
  if (input instanceof HTMLTextAreaElement && !input.value) {
    input.value = state.researchTopicDraft || "";
    input.placeholder = existingResearchTopic(data) || "例如：培训是否影响工资？";
  }
  if (existing) {
    existing.textContent = existingResearchTopic(data)
      ? `从已有选题继续：${existingResearchTopic(data)}`
      : "当前项目还没有可复用的选题，可以先输入一个研究问题。";
  }

  intake.classList.toggle("is-topic-confirmed", state.researchTopicConfirmed);
  workbench.classList.toggle("is-topic-pending", !state.researchTopicConfirmed);
  workbench.setAttribute("aria-hidden", state.researchTopicConfirmed ? "false" : "true");
  if (state.researchTopicConfirmed && topic) {
    const topicCopy = intake.querySelector(".topic-intake-copy p");
    if (topicCopy) topicCopy.textContent = `已确认选题：${topic}`;
  }
}

async function confirmResearchTopic(useExisting = false) {
  const input = document.getElementById("research-topic-input");
  const typedTopic = input instanceof HTMLTextAreaElement ? input.value.trim() : "";
  const topic = useExisting ? existingResearchTopic() : typedTopic || existingResearchTopic();
  if (!topic) return;
  try {
    const response = await v2api.researchQuestion.save(state.selectedProjectId, {
      question: topic,
      source: useExisting ? "project_seed" : "user_input",
      note: useExisting ? "从已有选题继续。" : "首页输入后确认。",
    });
    saveResearchQuestionState(topic, response.research_question);
    state.overviewData = await v2api.overview.get(state.selectedProjectId);
    renderJourney();
    document.getElementById("research-workbench-after-topic")?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showV2Error("journey", `保存研究选题失败：${error.message}`);
  }
}

// --- Journey Page ---

const STAGE_PIPELINE = [
  { id: "question-definition", name: "选题解析", description: "明确研究问题、核心假设与识别策略方向。" },
  { id: "literature-review", name: "文献综述", description: "梳理相关文献，定位研究缺口与理论支撑。" },
  { id: "data-readiness", name: "数据准备", description: "上传数据集、定义变量角色、完成数据质量检查。" },
  { id: "identification-design", name: "识别策略", description: "确定识别策略、模型设定与威胁清单。" },
  { id: "baseline-estimation", name: "基线估计", description: "运行基线回归、诊断检验与结果解读。" },
  { id: "robustness", name: "稳健性检验", description: "执行稳健性检验、安慰剂检验与敏感性分析。" },
  { id: "manuscript-drafting", name: "写作", description: "生成结果表格、撰写正文段落与整合证据。" },
  { id: "submission-prep", name: "审阅导出", description: "审稿评分、验证闸门与导出复现包。" },
];

function renderJourney() {
  const data = state.overviewData;
  if (!data) return;

  clearV2Error("journey");
  renderResearchTopicIntake(data);

  const intake = document.getElementById("research-topic-intake");
  const pipeline = document.getElementById("research-workbench-after-topic");
  if (!intake || !pipeline) return;

  if (!state.researchTopicConfirmed) {
    intake.style.display = "flex";
    pipeline.style.display = "none";
    return;
  }

  intake.style.display = "none";
  pipeline.style.display = "block";
  renderSupervisorPlan();
  renderAgentTaskQueue();

  // Build stage statuses from backend data or fallback
  const stageSummaries = data.stage_summaries || [];
  const currentStage = data.current_stage || "";
  const overallProgress = data.overall_progress || 0;

  const stages = STAGE_PIPELINE.map((stage, index) => {
    const summary = stageSummaries.find((s) => s.stage_id === stage.id || s.title === stage.name);
    let status = "locked";
    if (summary?.status === "completed") status = "completed";
    else if (summary?.status === "running") status = "running";
    else if (summary?.status === "in_progress" || currentStage === stage.id) status = "current";
    else if (summary?.status === "pending_confirmation") status = "pending";
    else if (summary?.status === "failed") status = "failed";
    else if (index === 0 || stageSummaries.some((s, i) => i < index && s.status === "completed")) {
      const prevSummary = stageSummaries.find((s) => s.stage_id === STAGE_PIPELINE[index - 1]?.id);
      if (index === 0 || prevSummary?.status === "completed") status = "unlocked";
    }
    return { ...stage, status, summary };
  });

  // Render track
  const track = document.getElementById("journey-track");
  if (track) {
    track.innerHTML = stages.map((stage, index) => {
      const isLast = index === stages.length - 1;
      const check = stage.status === "completed" ? `<span class="journey-node-check">✓</span>` : "";
      return `
        <div class="journey-node is-${stage.status}" data-journey-stage="${escapeHtml(stage.id)}" title="${escapeHtml(stage.description)}">
          <div class="journey-node-dot"></div>
          ${check}
          <span class="journey-node-label">${escapeHtml(stage.name)}</span>
        </div>
        ${!isLast ? `<div class="journey-connector ${stage.status === "completed" ? "is-completed" : ""}"></div>` : ""}
      `;
    }).join("");
  }

  // Find current stage for detail panel
  const currentStageData = stages.find((s) => s.status === "current") || stages.find((s) => s.status === "pending") || stages.find((s) => s.status === "unlocked") || stages[0];

  // Render stage detail
  const detail = document.getElementById("journey-stage-detail");
  if (detail) {
    if (currentStageData) {
      const metrics = currentStageData.summary?.metrics || [];
      const metricsHtml = metrics.length
        ? `<div class="stage-summary-metrics" style="margin: 12px 0;">
            ${metrics.map((m) => `<div class="stage-summary-metric"><span class="stage-summary-metric-value">${escapeHtml(productTermLabel(m.value))}</span><span class="stage-summary-metric-label">${escapeHtml(productTermLabel(m.label))}</span></div>`).join("")}
          </div>`
        : "";

      const risks = data.risks?.filter((r) => r.stage_id === currentStageData.id) || [];
      const risksHtml = risks.length
        ? `<div style="margin-top: 12px;"><strong style="color: #c0392b;">阶段风险：</strong>${risks.map((r) => escapeHtml(productTermLabel(r.description))).join("；")}</div>`
        : "";

      detail.innerHTML = `
        <div class="journey-stage-header">
          <h3>${escapeHtml(currentStageData.name)}</h3>
          <div class="journey-stage-meta">
            <span class="pill">${productTermLabel(currentStageData.status)}</span>
            <span class="muted">总体进度 ${Math.round(overallProgress * 100)}%</span>
          </div>
        </div>
        <div class="journey-stage-body">
          <p>${escapeHtml(currentStageData.description)}</p>
          ${metricsHtml}
          ${risksHtml}
        </div>
      `;
      detail.classList.remove("empty");
    } else {
      detail.innerHTML = `<p class="muted">暂无阶段详情</p>`;
      detail.classList.add("empty");
    }
  }

  // Render quick actions
  const actions = document.getElementById("journey-actions");
  if (actions) {
    const nextSteps = data.next_steps || [];
    const primaryAction = nextSteps[0];
    state.journeyPrimaryAction = primaryAction;
    const isStreaming = state.sseConnection.connected && state.sseConnection.runId;
    const canStartRun = !isStreaming && state.researchTopicConfirmed;
    actions.innerHTML = `
      ${isStreaming ? `<button class="primary-button" data-journey-action="view-output">查看 Agent 实时输出</button>` : ""}
      ${canStartRun ? `<button class="primary-button" data-journey-action="start-run">启动完整执行</button>` : ""}
      ${primaryAction && !canStartRun && !isStreaming ? `<button class="primary-button" data-journey-action="primary">${escapeHtml(productTermLabel(primaryAction.action || "继续"))}</button>` : ""}
      <button class="ghost-button" data-journey-action="refresh">刷新状态</button>
      ${currentStageData?.status === "pending" ? `<button class="ghost-button" data-journey-action="checkpoint" style="color: #e67e22; border-color: #e67e22;">确认检查点</button>` : ""}
    `;
  }
}

// --- Data & Variables Page ---

function renderDataVariables() {
  const data = state.datasetsData;
  if (!data) {
    document.getElementById("datasets-list").innerHTML = "<p class='muted'>加载中...</p>";
    return;
  }

  clearV2Error("data");

  // Evidence banner
  const bannerHtml = renderEvidenceBanner(data._meta);
  const existingBanner = document.querySelector("#view-data-variables > .evidence-banner");
  if (existingBanner) existingBanner.remove();
  if (bannerHtml) {
    document.getElementById("view-data-variables").insertAdjacentHTML("afterbegin", bannerHtml);
  }

  const items = data.items || [];
  document.getElementById("datasets-count").textContent = items.length;
  renderExternalDataLibrary(data.external_catalog);
  renderExternalBindPreflight(data.external_import_preflight);
  renderDatasetImportProfile(data.external_import_profile);
  renderVariableRoleCandidateReview(data.external_import_profile);
  renderVariableRoleWorkflow(items);
  renderDatasetQualityProfile(items);

  if (items.length === 0) {
    document.getElementById("datasets-list").innerHTML = renderEmptyState(data.empty_state);
  } else {
    if (!state.selectedDatasetPath) {
      state.selectedDatasetPath = items.find((ds) => ds.role === "configured_final_dataset")?.path || items[0]?.path || null;
    }
    document.getElementById("datasets-list").innerHTML = items.map((ds) => `
      <div class="project-card dataset-card ${ds.path === state.selectedDatasetPath ? "is-selected" : ""}">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
          <strong>${escapeHtml(ds.name || ds.id)}</strong>
          ${renderEvidenceBadge(ds)}
        </div>
        <div class="muted">${ds.row_count ?? 0} 行 · ${ds.column_count ?? 0} 列 · ${ds.file_type || "未知格式"} · ${escapeHtml(ds.role || "candidate_dataset")}</div>
        <div class="muted">${escapeHtml(ds.path || "")}</div>
        <div class="compact-action-row">
          <button class="ghost-button" data-select-dataset-quality data-dataset-path="${escapeHtml(ds.path || "")}">查看质量画像</button>
          <button class="ghost-button" data-open-design-action data-dataset-path="${escapeHtml(ds.path || "")}">检查并确认变量角色</button>
        </div>
      </div>
    `).join("");
  }
}

function renderExternalDataLibrary(catalog) {
  const container = document.getElementById("external-datasets-list");
  const count = document.getElementById("external-datasets-count");
  if (!container) return;

  if (!catalog || !catalog.exists) {
    if (count) count.textContent = "0";
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>尚未找到真实数据仓库</h4>
        <p class="muted">可通过 EMPIRICAL_DATA_LIBRARY_ROOT 指向本机实证数据库目录。这里是候选池，不会修改原始数据。</p>
      </div>
    `;
    return;
  }

  const items = catalog.items || [];
  const visibleItems = items.slice(0, 6);
  if (count) count.textContent = String(catalog.total_count ?? items.length);
  if (items.length === 0) {
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>${escapeHtml(catalog.empty_state?.title || "真实数据仓库为空")}</h4>
        <p class="muted">${escapeHtml(catalog.empty_state?.description || "没有发现可识别的数据文件。")}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="external-library-note">
      <div>
        <span class="eyebrow">真实数据候选池 · 只读</span>
        <strong>${escapeHtml(catalog.root || "实证数据库")}</strong>
      </div>
      <p class="muted">这些是真实数据资产，需要导入或绑定到当前项目后，才会进入变量确认、研究设计和执行。</p>
    </div>
    <div class="external-dataset-grid">
      ${visibleItems.map((item) => renderExternalDatasetCard(item)).join("")}
    </div>
    ${(catalog.total_count || 0) > visibleItems.length ? `
      <p class="muted external-catalog-limit">已显示前 ${visibleItems.length} 个候选文件，共发现 ${catalog.total_count} 个。</p>
    ` : ""}
  `;
}

function renderExternalDatasetCard(item) {
  const profile = item.quality_profile || {};
  const profileLine = profile.supported
    ? `${profile.row_count ?? "-"} 行预览 · ${profile.column_count ?? "-"} 列 · 缺失率 ${formatQualityRate(profile.missing_rate)}`
    : "暂未解析内容，仅登记文件与来源";
  return `
    <article class="external-dataset-card">
      <div class="external-dataset-card-head">
        <div>
          <span class="eyebrow">${escapeHtml(item.collection || "真实数据")}</span>
          <strong>${escapeHtml(item.name || "候选数据")}</strong>
        </div>
        ${renderEvidenceBadge(item)}
      </div>
      <p class="muted">${escapeHtml(profileLine)}</p>
      <div class="external-dataset-meta">
        <span>${escapeHtml((item.file_type || "unknown").toUpperCase())}</span>
        <span>${formatBytes(item.size)}</span>
        <span>${escapeHtml(qualityReadinessLabel(profile.readiness_status))}</span>
        <span>只读</span>
      </div>
      <code>${escapeHtml(item.relative_path || item.path || "")}</code>
      <div class="compact-action-row">
        <button class="ghost-button compact"
          data-external-bind-preflight-action
          data-source-path="${escapeHtml(item.path || "")}"
          ${state.bindingExternalDatasetPath === item.path ? "disabled" : ""}>
          ${state.bindingExternalDatasetPath === item.path ? "正在生成预检..." : "生成导入/绑定预检"}
        </button>
      </div>
    </article>
  `;
}

function renderExternalBindPreflight(preflight) {
  const container = document.getElementById("external-bind-preflight-body");
  const statusPill = document.getElementById("external-bind-preflight-status");
  if (!container) return;

  if (!preflight) {
    if (statusPill) statusPill.textContent = "尚未生成";
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>等待选择真实数据</h4>
        <p class="muted">点击候选数据卡片上的“生成导入/绑定预检”，系统只会记录来源、目标路径和检查项，不会复制或修改数据。</p>
      </div>
    `;
    return;
  }

  if (statusPill) statusPill.textContent = externalPreflightStatusLabel(preflight.status || "ready_for_review");
  const checks = preflight.checks || [];
  const datasetImport = preflight.dataset_import || null;
  const isApplying = state.applyingExternalPreflightId === preflight.id;
  container.innerHTML = `
    <article class="external-bind-preflight-record">
      <div class="record-header">
        <div>
          <span class="eyebrow">导入/绑定预检</span>
          <h4>${escapeHtml(preflight.source?.name || "真实数据文件")}</h4>
        </div>
        ${renderEvidenceBadge(preflight)}
      </div>
      <div class="record-meta-grid">
        <div>
          <span class="record-label">来源</span>
          <p class="record-path">${escapeHtml(preflight.source?.path || "")}</p>
        </div>
        <div>
          <span class="record-label">预检目标</span>
          <p class="record-path">${escapeHtml(preflight.target?.path || "")}</p>
        </div>
        <div>
          <span class="record-label">策略</span>
          <p>${escapeHtml(preflight.strategy || "copy_to_project_raw")}</p>
        </div>
        <div>
          <span class="record-label">执行状态</span>
          <p>${preflight.will_create_project_file ? "会创建项目文件" : "尚未导入/绑定"} · ${preflight.will_mutate_source ? "会修改源文件" : "源文件只读"}</p>
        </div>
      </div>
      <div class="preflight-check-list">
        ${checks.map((check) => `
          <div class="quality-check is-${escapeHtml(check.status || "unknown")}">
            <span>${qualityCheckIcon(check.status)}</span>
            <div>
              <strong>${escapeHtml(check.label || check.id || "检查项")}</strong>
              <p class="muted">${escapeHtml(check.detail || "")}</p>
            </div>
          </div>
        `).join("") || "<p class='muted'>暂无检查项。</p>"}
      </div>
      ${preflight.status === "ready_for_review" ? `
        <div class="preflight-action-row">
          ${renderExternalPreflightApplyButton(preflight, "copy_to_project_raw", "确认导入到项目", "复制到当前项目 Data/Raw，后续可做变量画像。")}
          ${renderExternalPreflightApplyButton(preflight, "bind_external_reference", "只绑定引用", "不复制大文件，只记录本机外部引用。")}
          ${renderExternalPreflightApplyButton(preflight, "cancel", "取消预检", "废弃这次选择，不影响项目。")}
        </div>
        <p class="muted external-bind-preflight-note">按钮说明：确认导入会复制一份数据到当前项目；只绑定引用不会复制大文件，只记录本机路径；取消预检会废弃这次选择。</p>
        ${isApplying ? `<p class="muted external-bind-preflight-note">正在处理：${escapeHtml(externalApplyActionLabel(state.applyingExternalPreflightAction))}</p>` : ""}
      ` : ""}
      ${datasetImport ? `
        <div class="external-import-result">
          <strong>${escapeHtml(externalApplyResultLabel(datasetImport))}</strong>
          <p class="muted">动作：${escapeHtml(externalApplyActionLabel(datasetImport.action))} · 模式：${escapeHtml(datasetImport.runtime_mode || "local")}</p>
          ${datasetImport.target?.path ? `<p class="record-path">目标：${escapeHtml(datasetImport.target.path)}</p>` : ""}
          ${datasetImport.source?.sha256 ? `<p class="record-path">SHA256：${escapeHtml(datasetImport.source.sha256)}</p>` : ""}
          ${datasetImport.status === "applied" ? `
            <div class="compact-action-row">
              <button
                class="primary-button compact"
                data-external-import-profile-action
                data-dataset-import-id="${escapeHtml(datasetImport.id || "")}"
                ${state.profilingDatasetImportId === datasetImport.id ? "disabled" : ""}
              >
                ${state.profilingDatasetImportId === datasetImport.id ? "画像生成中..." : "生成字段画像"}
              </button>
            </div>
          ` : ""}
        </div>
      ` : ""}
      <p class="muted external-bind-preflight-note">状态文件：${escapeHtml(preflight.manifest_path || "state/product/dataset_import_preflights.json")} · 本阶段不会改写 paper.yaml、VariableRoleSet、DesignSpec 或 RunPlan。</p>
    </article>
  `;
}

function renderDatasetImportProfile(profile) {
  const container = document.getElementById("dataset-import-profile-body");
  const statusPill = document.getElementById("dataset-import-profile-status");
  if (!container) return;

  if (!profile) {
    if (statusPill) statusPill.textContent = "尚未画像";
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>等待真实数据接入</h4>
        <p class="muted">导入或绑定真实数据后，先生成字段画像 / 变量字典预览。该步骤不会改写 VariableRoleSet、DesignSpec 或 RunPlan。</p>
      </div>
    `;
    return;
  }

  if (statusPill) statusPill.textContent = datasetImportProfileStatusLabel(profile.status || "blocked");
  const fields = profile.fields || [];
  const checks = profile.checks || [];
  container.innerHTML = `
    <article class="dataset-import-profile-record">
      <div class="record-header">
        <div>
          <span class="eyebrow">字段画像 / 变量字典预览</span>
          <h4>${escapeHtml(profile.source?.name || "真实数据")}</h4>
          <p class="muted">dataset_import_id=${escapeHtml(profile.dataset_import_id || "-")} · ${escapeHtml(profile.readiness_status || "-")}</p>
        </div>
        ${renderEvidenceBadge(profile)}
      </div>
      <div class="record-meta-grid">
        <div>
          <span class="record-label">来源</span>
          <p class="record-path">${escapeHtml(profile.source?.path || "")}</p>
        </div>
        <div>
          <span class="record-label">绑定方式</span>
          <p>${escapeHtml(profile.binding?.mode || "project_file")} · ${profile.binding?.read_only ? "只读" : "项目文件"}</p>
        </div>
        <div>
          <span class="record-label">样本范围</span>
          <p>${profile.quality_profile?.row_count ?? "-"} 行 · ${profile.quality_profile?.column_count ?? "-"} 列 · row_limit=${profile.row_limit ?? "-"}</p>
        </div>
        <div>
          <span class="record-label">状态边界</span>
          <p>${profile.can_feed_variable_roles ? "可进入变量确认" : "不会改写 VariableRoleSet、DesignSpec 或 RunPlan"}</p>
        </div>
      </div>
      ${profile.blocking_reason ? `<p class="warning-copy">${escapeHtml(profile.blocking_reason)}</p>` : ""}
      <div class="preflight-check-list">
        ${checks.map((check) => `
          <div class="quality-check is-${escapeHtml(check.status || "unknown")}">
            <span>${qualityCheckIcon(check.status)}</span>
            <div>
              <strong>${escapeHtml(check.label || check.id || "检查项")}</strong>
              <p class="muted">${escapeHtml(check.detail || "")}</p>
            </div>
          </div>
        `).join("") || "<p class='muted'>暂无画像检查项。</p>"}
      </div>
      <div class="field-profile-table" role="table" aria-label="字段画像">
        <div class="field-profile-row field-profile-head" role="row">
          <span>字段</span><span>变量标签</span><span>Stata 类型</span><span>缺失率</span>
        </div>
        ${fields.length ? fields.map((field) => `
          <div class="field-profile-row" role="row">
            <span>${escapeHtml(field.name || "-")}</span>
            <span>${escapeHtml(field.label || field.inferred_type || "-")}</span>
            <span>${escapeHtml(field.stata_type || field.display_format || field.inferred_type || "-")}</span>
            <span>${formatQualityRate(field.missing_rate)}</span>
          </div>
        `).join("") : `
          <div class="field-profile-row empty" role="row">
            <span>暂无字段</span><span>未画像</span><span>-</span><span>解析器未接入或文件为空</span>
          </div>
        `}
      </div>
      <p class="muted external-bind-preflight-note">状态文件：${escapeHtml(profile.manifest_path || "state/product/dataset_import_preflights.json")} · ${escapeHtml(profile.next_action || "先人工审阅字段画像。")}</p>
    </article>
  `;
}

function renderVariableRoleCandidateReview(profile) {
  const container = document.getElementById("variable-role-candidate-body");
  const statusPill = document.getElementById("variable-role-candidate-status");
  if (!container) return;

  if (!profile || profile.status !== "profiled") {
    if (statusPill) statusPill.textContent = "等待字段画像";
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>先生成字段画像</h4>
        <p class="muted">变量角色候选只能来自真实字段画像。系统不会根据文件名猜测 outcome、treatment 或 controls。</p>
      </div>
    `;
    return;
  }

  const candidate = latestVariableRoleCandidateForProfile(profile);
  if (!candidate) {
    if (statusPill) statusPill.textContent = "可生成候选";
    const isGenerating = state.generatingVariableRoleCandidateId === profile.dataset_import_id;
    container.innerHTML = `
      <article class="variable-role-candidate-record research-record-card">
        <div class="record-header">
          <div>
            <span class="eyebrow">字段审阅</span>
            <h4>从字段画像生成变量角色候选</h4>
            <p class="muted">${escapeHtml(profile.source?.name || "真实数据")} · ${profile.fields?.length || 0} 个字段</p>
          </div>
          ${renderEvidenceBadge(profile)}
        </div>
        <p class="muted">生成变量角色候选后，你可以审阅结果变量、处理变量、控制变量和工具变量。该步骤不会写入正式变量角色集。</p>
        <div class="compact-action-row">
          <button
            class="primary-button compact"
            data-variable-role-candidate-generate
            data-dataset-import-id="${escapeHtml(profile.dataset_import_id || "")}"
            ${isGenerating ? "disabled" : ""}
          >
            ${isGenerating ? "生成中..." : "生成变量角色候选"}
          </button>
        </div>
      </article>
    `;
    return;
  }

  if (statusPill) statusPill.textContent = variableRoleCandidateStatusLabel(candidate.status);
  const roles = candidate.candidate_roles || {};
  const fields = candidate.field_options || [];
  const latestEvent = (candidate.review_events || []).slice(-1)[0];
  const isPromotingCandidate = state.promotingVariableRoleCandidateId === candidate.id;
  container.innerHTML = `
    <article class="variable-role-candidate-record research-record-card">
      <div class="record-header">
        <div>
          <span class="eyebrow">候选建议</span>
          <h4>${escapeHtml(candidate.source?.name || "变量角色候选")}</h4>
          <p class="muted">${escapeHtml(variableRoleCandidateStatusLabel(candidate.status))} · evidence_level=${escapeHtml(candidate.evidence_level || "local_file")}</p>
        </div>
        ${renderEvidenceBadge(candidate)}
      </div>
      <div class="record-meta-grid">
        <div>
          <span class="record-label">候选边界</span>
          <p>${candidate.does_not_mutate_variable_role_set ? "不会写入正式变量角色集" : "需要检查写回边界"}</p>
        </div>
        <div>
          <span class="record-label">后续动作</span>
          <p>${candidate.can_apply_to_variable_roles ? "可进入正式变量角色集编辑器" : "仍需人工审阅"}</p>
        </div>
        <div>
          <span class="record-label">来源画像</span>
          <p class="record-path">${escapeHtml(candidate.dataset_import_profile_id || "-")}</p>
        </div>
        <div>
          <span class="record-label">状态文件</span>
          <p class="record-path">${escapeHtml(candidate.manifest_path || "state/product/variable_role_candidates.json")}</p>
        </div>
      </div>
      <div class="variable-role-candidate-roles">
        ${renderCandidateRoleGroup("结果变量", roles.outcome)}
        ${renderCandidateRoleGroup("处理变量", roles.treatment)}
        ${renderCandidateRoleGroup("控制变量", roles.controls)}
        ${renderCandidateRoleGroup("工具变量", roles.instruments)}
      </div>
      <div class="field-profile-table compact" role="table" aria-label="变量角色候选字段">
        <div class="field-profile-row field-profile-head" role="row">
          <span>字段</span><span>变量标签</span><span>类型</span><span>建议角色</span>
        </div>
        ${fields.slice(0, 12).map((field) => `
          <div class="field-profile-row" role="row">
            <span>${escapeHtml(field.name || "-")}</span>
            <span>${escapeHtml(field.label || "-")}</span>
            <span>${escapeHtml(field.stata_type || field.inferred_type || "-")}</span>
            <span>${escapeHtml(variableRoleNameLabel(field.recommended_role || "exclude"))}</span>
          </div>
        `).join("")}
      </div>
      <p class="muted external-bind-preflight-note">最近审阅：${escapeHtml(latestEvent?.action || "generate_variable_role_candidate")} · ${escapeHtml(latestEvent?.note || "尚未人工审批")}</p>
      <div class="compact-action-row">
        ${renderVariableRoleCandidateReviewButton(candidate, "approve_candidate", "候选已确认")}
        ${renderVariableRoleCandidateReviewButton(candidate, "needs_revision", "需要调整")}
        ${renderVariableRoleCandidateReviewButton(candidate, "reject", "驳回候选")}
        ${candidate.can_apply_to_variable_roles ? `
          <button
            class="primary-button compact"
            data-promote-variable-candidate-action
            data-candidate-id="${escapeHtml(candidate.id || "")}"
            title="把候选建议保存成可编辑草稿；不会覆盖正式变量角色。"
            ${isPromotingCandidate ? "disabled" : ""}
          >
            ${isPromotingCandidate ? "创建草稿中..." : "基于候选创建变量角色草稿"}
          </button>
          <button
            class="ghost-button compact"
            data-variable-role-candidate-load-editor
            data-candidate-id="${escapeHtml(candidate.id || "")}"
            title="兼容旧路径：只在本页载入，不写入草稿状态。"
          >
            仅载入编辑器
          </button>
        ` : ""}
      </div>
      ${candidate.can_apply_to_variable_roles ? `
        <p class="muted external-bind-preflight-note">保存后才写入正式变量角色集；载入编辑器后仍可调整每一类变量。</p>
      ` : ""}
    </article>
  `;
}

function latestVariableRoleCandidateForProfile(profile) {
  const latest = state.variableRoleCandidatesData?.latest_variable_role_candidate;
  if (latest?.dataset_import_profile_id === profile.id) return latest;
  const candidates = state.variableRoleCandidatesData?.variable_role_candidates || [];
  return candidates.find((candidate) => candidate.dataset_import_profile_id === profile.id) || null;
}

function renderCandidateRoleGroup(label, values) {
  return `
    <div class="variable-role-group">
      <span class="meta-label">${escapeHtml(label)}</span>
      <p>${Array.isArray(values) && values.length ? values.map(escapeHtml).join("、") : "未识别"}</p>
    </div>
  `;
}

function renderVariableRoleCandidateReviewButton(candidate, action, label) {
  const active = state.reviewingVariableRoleCandidateId === candidate.id
    && state.reviewingVariableRoleCandidateAction === action;
  return `
    <button
      class="${action === "approve_candidate" ? "primary-button" : "ghost-button"} compact"
      data-variable-role-candidate-review-action="${escapeHtml(action)}"
      data-candidate-id="${escapeHtml(candidate.id || "")}"
      ${state.reviewingVariableRoleCandidateId === candidate.id ? "disabled" : ""}
    >
      ${active ? "处理中..." : escapeHtml(label)}
    </button>
  `;
}

function variableRoleCandidateStatusLabel(status) {
  return {
    needs_review: "待人工审阅",
    approved_candidate: "候选已确认",
    applied_to_variable_roles: "已写入正式变量角色集",
    rejected: "已驳回",
  }[status] || status || "未知状态";
}

function variableRoleNameLabel(role) {
  return {
    outcome: "结果变量",
    treatment: "处理变量",
    controls: "控制变量",
    instruments: "工具变量",
    fixed_effects: "固定效应",
    cluster_by: "聚类方式",
    exclude: "暂不纳入",
  }[role] || role || "暂不纳入";
}

function renderExternalPreflightApplyButton(preflight, action, label, description) {
  const isApplying = state.applyingExternalPreflightId === preflight.id;
  const active = isApplying && state.applyingExternalPreflightAction === action;
  return `
    <button
      class="${action === "copy_to_project_raw" ? "primary-button" : "ghost-button"} compact"
      data-external-preflight-apply-action="${escapeHtml(action)}"
      data-preflight-id="${escapeHtml(preflight.id || "")}"
      title="${escapeHtml(description)}"
      ${isApplying ? "disabled" : ""}
    >
      ${active ? "处理中..." : escapeHtml(label)}
    </button>
  `;
}

function externalPreflightStatusLabel(status) {
  return {
    ready_for_review: "待人工确认",
    applied: "已接入",
    cancelled: "已取消",
  }[status] || status;
}

function externalApplyActionLabel(action) {
  return {
    copy_to_project_raw: "确认导入到项目",
    bind_external_reference: "只绑定引用",
    cancel: "取消预检",
  }[action] || action || "未知动作";
}

function externalApplyResultLabel(datasetImport) {
  if (datasetImport.status === "cancelled") return "预检已取消";
  if (datasetImport.action === "copy_to_project_raw") return "已导入到项目";
  if (datasetImport.action === "bind_external_reference") return "已绑定外部引用";
  return datasetImport.status || "已处理";
}

function datasetImportProfileStatusLabel(status) {
  return {
    profiled: "已画像",
    blocked: "暂未画像",
  }[status] || status || "未知状态";
}

function renderDatasetQualityProfile(items) {
  const container = document.getElementById("data-quality-profile-body");
  if (!container) return;

  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>等待数据文件</h4>
        <p class="muted">发现本地数据后，这里会显示字段、缺失率和进入研究设计前的检查结果。</p>
      </div>
    `;
    return;
  }

  const selected = items.find((item) => item.path === state.selectedDatasetPath)
    || items.find((item) => item.role === "configured_final_dataset")
    || items[0];
  const profile = selected?.quality_profile || null;
  if (!profile) {
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>尚未生成质量画像</h4>
        <p class="muted">当前数据集只有文件登记信息，尚未返回字段质量检查。</p>
      </div>
    `;
    return;
  }

  const columns = profile.columns || [];
  const checks = profile.checks || [];
  container.innerHTML = `
    <div class="data-quality-profile">
      <div class="quality-profile-header">
        <div>
          <span class="eyebrow">数据质量画像</span>
          <h4>${escapeHtml(selected.name || selected.path || "数据集")}</h4>
          <p class="muted">${escapeHtml(selected.path || "")}</p>
        </div>
        <div class="quality-profile-status">
          ${renderEvidenceBadge(profile)}
          <span class="status-pill status-${escapeHtml(profile.readiness_status || "unknown")}">
            ${escapeHtml(qualityReadinessLabel(profile.readiness_status))}
          </span>
        </div>
      </div>
      <div class="quality-profile-grid">
        <div class="quality-metric">
          <span>样本</span>
          <strong>${profile.row_count ?? "-"}</strong>
          <small>${profile.column_count ?? "-"} 个字段</small>
        </div>
        <div class="quality-metric">
          <span>缺失率</span>
          <strong>${formatQualityRate(profile.missing_rate)}</strong>
          <small>${profile.missing_cells ?? "-"} 个空单元格</small>
        </div>
        <div class="quality-metric">
          <span>数值字段</span>
          <strong>${profile.numeric_column_count ?? "-"}</strong>
          <small>可进入模型候选</small>
        </div>
        <div class="quality-metric">
          <span>文本字段</span>
          <strong>${profile.text_column_count ?? "-"}</strong>
          <small>需人工解释</small>
        </div>
      </div>
      <div class="quality-profile-section">
        <h5>检查项</h5>
        <div class="quality-check-list">
          ${checks.map((check) => `
            <div class="quality-check is-${escapeHtml(check.status || "unknown")}">
              <span>${qualityCheckIcon(check.status)}</span>
              <div>
                <strong>${escapeHtml(check.label || check.id)}</strong>
                <p class="muted">${escapeHtml(check.detail || "")}</p>
              </div>
            </div>
          `).join("") || "<p class='muted'>暂无检查项。</p>"}
        </div>
      </div>
      <div class="quality-profile-section">
        <h5>字段画像</h5>
        <div class="quality-column-list">
          ${columns.slice(0, 8).map((column) => `
            <div class="quality-column">
              <div>
                <strong>${escapeHtml(column.name || "")}</strong>
                <span>${escapeHtml(qualityColumnTypeLabel(column.inferred_type))}</span>
              </div>
              <small>缺失 ${formatQualityRate(column.missing_rate)} · 样例 ${escapeHtml((column.sample_values || []).join(", ") || "-")}</small>
            </div>
          `).join("") || "<p class='muted'>当前格式暂未解析字段画像。</p>"}
        </div>
      </div>
    </div>
  `;
}

function qualityReadinessLabel(status) {
  return {
    ready: "可进入变量确认",
    needs_review: "需要人工检查",
    blocked: "阻塞",
    not_profiled: "尚未画像",
  }[status] || status || "未知";
}

function qualityColumnTypeLabel(type) {
  return {
    numeric: "数值",
    text: "文本",
    empty: "空列",
  }[type] || type || "未知";
}

function qualityCheckIcon(status) {
  return status === "passed" ? "✓" : status === "warning" ? "!" : "×";
}

function formatQualityRate(value) {
  if (value === null || value === undefined) return "-";
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return escapeHtml(String(value));
  return `${Math.round(numeric * 1000) / 10}%`;
}

function formatBytes(value) {
  const size = Number(value);
  if (!Number.isFinite(size)) return "-";
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${Math.round(size / 102.4) / 10} KB`;
  if (size < 1024 * 1024 * 1024) return `${Math.round(size / 1024 / 102.4) / 10} MB`;
  return `${Math.round(size / 1024 / 1024 / 102.4) / 10} GB`;
}

function renderVariableRoleWorkflow(items) {
  const container = document.getElementById("variable-role-workflow-body");
  if (!container) return;

  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="empty-state compact">
        <h4>等待数据集</h4>
        <p class="muted">先把 csv/dta/xlsx/parquet 等文件放入 Data 目录，再进入变量角色确认。</p>
      </div>
    `;
    return;
  }

  const selected = items.find((item) => item.path === state.selectedDatasetPath)
    || items.find((item) => item.role === "configured_final_dataset")
    || items[0];
  state.selectedDatasetPath = selected?.path || state.selectedDatasetPath;

  container.innerHTML = `
    <div class="variable-role-workflow-layout research-record-card">
      <div class="record-header">
        <div>
          <span class="eyebrow">确认变量角色</span>
          <h4>${escapeHtml(selected?.name || "已选择数据集")}</h4>
        </div>
        ${renderEvidenceBadge(selected)}
      </div>
      <div class="record-meta-grid">
        <div>
          <span class="record-label">样本路径</span>
          <p class="record-path">${escapeHtml(selected?.path || "")}</p>
        </div>
        <div>
          <span class="record-label">数据规模</span>
          <p>${selected?.row_count ?? 0} 行 · ${selected?.column_count ?? 0} 列 · ${escapeHtml(selected?.file_type || "未知格式")}</p>
        </div>
      </div>
      <ol class="research-step-list">
        <li>
          <strong>读取字段与样本口径</strong>
          <span>本地文件证据，路径和行列数必须可追溯。</span>
        </li>
        <li>
          <strong>确认结果变量 / 处理变量 / 控制变量 / 工具变量</strong>
          <span>确认后进入研究设计方案，不在执行页临时猜测变量角色。</span>
        </li>
      </ol>
      <div class="compact-action-row">
        <button class="primary-button" data-open-design-action data-dataset-path="${escapeHtml(selected?.path || "")}">
          检查并确认变量角色
        </button>
      </div>
    </div>
  `;
  renderVariableRoleEditor();
}

function joinRoleValues(values) {
  return Array.isArray(values) ? values.join(", ") : "";
}

function parseVariableRoleField(fieldId) {
  const value = document.getElementById(fieldId)?.value || "";
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

function setVariableRoleField(fieldId, values) {
  const field = document.getElementById(fieldId);
  if (field) {
    field.value = joinRoleValues(values);
  }
}

async function requestExternalBindPreflight(sourcePath) {
  if (!state.selectedProjectId || !sourcePath) return;
  clearV2Error("data");
  state.bindingExternalDatasetPath = sourcePath;
  renderDataVariables();
  try {
    await v2api.datasets.bindPreflight(state.selectedProjectId, {
      source_path: sourcePath,
      strategy: "copy_to_project_raw",
      note: "用户在数据与设计页请求真实数据导入/绑定预检。",
    });
    state.datasetsData = await v2api.datasets.list(state.selectedProjectId);
    renderDataVariables();
  } catch (error) {
    showV2Error("data", `生成导入/绑定预检失败：${error.message}`);
  } finally {
    state.bindingExternalDatasetPath = null;
    renderDataVariables();
  }
}

async function requestExternalPreflightApply(preflightId, action) {
  if (!state.selectedProjectId || !preflightId || !action) return;
  clearV2Error("data");
  state.applyingExternalPreflightId = preflightId;
  state.applyingExternalPreflightAction = action;
  renderDataVariables();
  try {
    await v2api.datasets.applyPreflight(state.selectedProjectId, preflightId, {
      action,
      runtime_mode: "local",
      note: `用户在数据与设计页执行：${externalApplyActionLabel(action)}。`,
    });
    state.datasetsData = await v2api.datasets.list(state.selectedProjectId);
    renderDataVariables();
  } catch (error) {
    showV2Error("data", `处理导入/绑定预检失败：${error.message}`);
  } finally {
    state.applyingExternalPreflightId = null;
    state.applyingExternalPreflightAction = null;
    renderDataVariables();
  }
}

async function requestExternalImportProfile(datasetImportId) {
  if (!state.selectedProjectId || !datasetImportId) return;
  clearV2Error("data");
  state.profilingDatasetImportId = datasetImportId;
  renderDataVariables();
  try {
    await v2api.datasets.profileImport(state.selectedProjectId, datasetImportId, {
      row_limit: 200,
    });
    state.datasetsData = await v2api.datasets.list(state.selectedProjectId);
    renderDataVariables();
  } catch (error) {
    showV2Error("data", `生成字段画像失败：${error.message}`);
  } finally {
    state.profilingDatasetImportId = null;
    renderDataVariables();
  }
}

async function generateVariableRoleCandidate(datasetImportId) {
  if (!state.selectedProjectId || !datasetImportId) return;
  clearV2Error("data");
  state.generatingVariableRoleCandidateId = datasetImportId;
  renderDataVariables();
  try {
    await v2api.variableRoleCandidates.generate(state.selectedProjectId, datasetImportId, {
      note: "用户在字段审阅面板请求基于真实字段画像生成变量角色候选。",
    });
    state.variableRoleCandidatesData = await v2api.variableRoleCandidates.list(state.selectedProjectId);
    renderDataVariables();
  } catch (error) {
    showV2Error("data", `生成变量角色候选失败：${error.message}`);
  } finally {
    state.generatingVariableRoleCandidateId = null;
    renderDataVariables();
  }
}

async function reviewVariableRoleCandidate(candidateId, action) {
  if (!state.selectedProjectId || !candidateId || !action) return;
  clearV2Error("data");
  const candidate = (state.variableRoleCandidatesData?.variable_role_candidates || [])
    .find((item) => item.id === candidateId)
    || state.variableRoleCandidatesData?.latest_variable_role_candidate;
  state.reviewingVariableRoleCandidateId = candidateId;
  state.reviewingVariableRoleCandidateAction = action;
  renderDataVariables();
  try {
    await v2api.variableRoleCandidates.review(state.selectedProjectId, candidateId, {
      action,
      note: `用户在字段审阅面板执行：${variableRoleCandidateReviewActionLabel(action)}。`,
      candidate_roles: candidate?.candidate_roles || {},
    });
    state.variableRoleCandidatesData = await v2api.variableRoleCandidates.list(state.selectedProjectId);
    renderDataVariables();
  } catch (error) {
    showV2Error("data", `审阅变量角色候选失败：${error.message}`);
  } finally {
    state.reviewingVariableRoleCandidateId = null;
    state.reviewingVariableRoleCandidateAction = null;
    renderDataVariables();
  }
}

async function promoteVariableRoleCandidate(candidateId) {
  if (!state.selectedProjectId || !candidateId) return;
  const candidate = (state.variableRoleCandidatesData?.variable_role_candidates || [])
    .find((item) => item.id === candidateId)
    || state.variableRoleCandidatesData?.latest_variable_role_candidate;
  if (!candidate || candidate.id !== candidateId) return;

  clearV2Error("data");
  state.promotingVariableRoleCandidateId = candidateId;
  renderDataVariables();
  try {
    const response = await v2api.variableRoleCandidates.promote(state.selectedProjectId, candidateId, {
      note: `基于候选建议 ${candidateId} 创建正式变量角色草稿。`,
    });
    const draft = response.variable_role_set_draft;
    state.pendingVariableRoleCandidateId = candidateId;
    state.variableRolesData = {
      ...(state.variableRolesData || {}),
      variable_role_set: {
        ...(state.variableRolesData?.variable_role_set || {}),
        ...draft,
        candidate_id: draft.source_candidate_id,
        source: candidate.source || {},
        binding: candidate.binding || {},
      },
    };
    renderDataVariables();
    const note = document.getElementById("variable-role-note");
    if (note) {
      note.value = `已从候选建议 ${candidateId} 创建草稿；编辑后点击“保存正式变量角色”才会写入正式状态。`;
    }
    document.getElementById("variable-role-confirmation-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showV2Error("data", `创建变量角色草稿失败：${error.message}`);
  } finally {
    state.promotingVariableRoleCandidateId = null;
    renderDataVariables();
  }
}

function loadVariableRoleCandidateIntoEditor(candidateId) {
  const candidate = (state.variableRoleCandidatesData?.variable_role_candidates || [])
    .find((item) => item.id === candidateId)
    || state.variableRoleCandidatesData?.latest_variable_role_candidate;
  if (!candidate || candidate.id !== candidateId) return;

  state.pendingVariableRoleCandidateId = candidateId;
  const roles = candidate.candidate_roles || {};
  const sourcePath = candidate.source?.path || candidate.binding?.path || "";
  state.selectedDatasetPath = sourcePath || state.selectedDatasetPath;
  state.variableRolesData = {
    ...(state.variableRolesData || {}),
    variable_role_set: {
      ...(state.variableRolesData?.variable_role_set || {}),
      status: "draft_from_candidate",
      evidence_level: candidate.evidence_level || "local_file",
      dataset_path: sourcePath,
      dataset_name: candidate.source?.name || "",
      candidate_id: candidate.id,
      dataset_import_id: candidate.dataset_import_id,
      dataset_import_profile_id: candidate.dataset_import_profile_id,
      source: candidate.source || {},
      binding: candidate.binding || {},
      roles: {
        outcome: roles.outcome || [],
        treatment: roles.treatment || [],
        controls: roles.controls || [],
        instruments: roles.instruments || [],
        fixed_effects: roles.fixed_effects || [],
        cluster_by: roles.cluster_by || [],
      },
    },
  };
  renderVariableRoleEditor();
  const note = document.getElementById("variable-role-note");
  if (note) {
    note.value = `从真实字段候选 ${candidate.id} 正式确认变量角色；保存后才写入正式变量角色集。`;
  }
  document.getElementById("variable-role-confirmation-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function variableRoleCandidateReviewActionLabel(action) {
  return {
    approve_candidate: "候选已确认",
    needs_revision: "需要调整",
    reject: "驳回候选",
  }[action] || action;
}

function renderVariableRoleEditor() {
  const roleSet = state.variableRolesData?.variable_role_set || null;
  const form = document.getElementById("variable-role-confirmation-form");
  const meta = document.getElementById("variable-role-editor-meta");
  const statusPill = document.getElementById("variable-role-status-pill");
  const saveButton = document.querySelector("[data-variable-role-save]");
  if (!form || !meta || !statusPill) return;

  if (!roleSet) {
    meta.textContent = "正式变量角色：正在读取...";
    return;
  }

  const roles = roleSet.roles || {};
  state.selectedDatasetPath = roleSet.dataset_path || state.selectedDatasetPath;
  document.getElementById("variable-role-dataset-path").value = roleSet.dataset_path || "";
  setVariableRoleField("variable-role-outcome", roles.outcome);
  setVariableRoleField("variable-role-treatment", roles.treatment);
  setVariableRoleField("variable-role-controls", roles.controls);
  setVariableRoleField("variable-role-instruments", roles.instruments);
  setVariableRoleField("variable-role-fixed-effects", roles.fixed_effects);
  setVariableRoleField("variable-role-cluster-by", roles.cluster_by);
  statusPill.textContent = `正式变量角色 · ${roleSet.status || "draft"} · ${roleSet.evidence_level || "local_file"}`;
  const pendingCandidateText = state.pendingVariableRoleCandidateId
    ? ` · candidate_id=${state.pendingVariableRoleCandidateId} · 保存后才写入正式变量角色集`
    : "";
  meta.textContent = `正式变量角色：${roleSet.dataset_path || "未选择数据集"} · version=${roleSet.version ?? 0} · evidence_level=${roleSet.evidence_level || "local_file"}${pendingCandidateText}`;
  if (saveButton) {
    saveButton.disabled = state.savingVariableRoles;
  }
  document.getElementById("variable-role-save-status").textContent = state.savingVariableRoles ? "保存中..." : "";
}

async function handleSaveVariableRoles(event) {
  event.preventDefault();
  if (!state.selectedProjectId) return;

  const datasetPath = document.getElementById("variable-role-dataset-path")?.value || state.selectedDatasetPath;
  const payload = {
    dataset_path: datasetPath,
    roles: {
      outcome: parseVariableRoleField("variable-role-outcome"),
      treatment: parseVariableRoleField("variable-role-treatment"),
      controls: parseVariableRoleField("variable-role-controls"),
      instruments: parseVariableRoleField("variable-role-instruments"),
      fixed_effects: parseVariableRoleField("variable-role-fixed-effects"),
      cluster_by: parseVariableRoleField("variable-role-cluster-by"),
    },
    note: document.getElementById("variable-role-note")?.value?.trim() || "",
  };
  if (state.pendingVariableRoleCandidateId) {
    payload.candidate_id = state.pendingVariableRoleCandidateId;
  }

  clearV2Error("data");
  state.savingVariableRoles = true;
  renderVariableRoleEditor();
  try {
    await v2api.variableRoles.save(state.selectedProjectId, payload);
    state.variableRolesData = await v2api.variableRoles.get(state.selectedProjectId);
    state.variableRoleCandidatesData = await v2api.variableRoleCandidates.list(state.selectedProjectId);
    state.overviewData = await v2api.overview.get(state.selectedProjectId);
    state.pendingVariableRoleCandidateId = null;
    renderDataVariables();
    renderWorkflowContract(state.overviewData.workflow_contract);
    document.getElementById("variable-role-save-status").textContent = "已保存";
  } catch (error) {
    showV2Error("data", `保存变量角色集失败：${error.message}`);
  } finally {
    state.savingVariableRoles = false;
    renderVariableRoleEditor();
  }
}

function parseCommaField(fieldId) {
  return parseVariableRoleField(fieldId);
}

function setTextField(fieldId, value) {
  const field = document.getElementById(fieldId);
  if (field) {
    field.value = value || "";
  }
}

function renderDesignSpecEditor() {
  const designSpec = state.designSpecData?.design_spec || null;
  const form = document.getElementById("design-spec-confirmation-form");
  const meta = document.getElementById("design-spec-editor-meta");
  const statusPill = document.getElementById("design-spec-status-pill");
  const saveButton = document.querySelector("[data-design-spec-save]");
  if (!form || !meta || !statusPill) return;

  if (!designSpec) {
    meta.textContent = "正在读取研究设计方案...";
    return;
  }

  const strategy = designSpec.identification_strategy || {};
  const model = designSpec.model || {};
  setTextField("design-spec-question", designSpec.research_question);
  setTextField("design-spec-strategy", strategy.name || "baseline_ols");
  setTextField("design-spec-estimator", model.estimator || "ols");
  setTextField("design-spec-formula", model.formula || "");
  setTextField("design-spec-fixed-effects", joinRoleValues(model.fixed_effects));
  setTextField("design-spec-cluster-by", joinRoleValues(model.cluster_by));
  setTextField("design-spec-summary", strategy.summary || "");
  setTextField("design-spec-threats", joinRoleValues(strategy.threats));
  statusPill.textContent = `${designSpec.status || "draft"} · ${designSpec.evidence_level || "local_file"}`;
  meta.textContent = `${designSpec.dataset_path || "未绑定数据集"} · version=${designSpec.version ?? 0} · variable_role_set_version=${designSpec.variable_role_set_version ?? 0}`;
  if (saveButton) {
    saveButton.disabled = state.savingDesignSpec;
  }
  document.getElementById("design-spec-save-status").textContent = state.savingDesignSpec ? "保存中..." : "";
}

function methodReadinessLabel(status) {
  return {
    ready: "可进入执行计划",
    blocked: "前置条件不足",
    needs_review: "需要人工复核",
  }[status] || productTermLabel(status || "unknown");
}

function requirementStatusLabel(status) {
  return status === "present" ? "已具备" : "缺失";
}

function renderMethodRequirement(requirement) {
  const values = requirement.values || [];
  return `
    <li class="method-requirement ${requirement.status === "present" ? "is-present" : "is-missing"}">
      <span>${escapeHtml(requirement.label || requirement.id || "")}</span>
      <strong>${escapeHtml(requirementStatusLabel(requirement.status))}</strong>
      ${values.length ? `<small>${escapeHtml(values.join(", "))}</small>` : ""}
    </li>
  `;
}

function renderMethodSkillCatalog() {
  const container = document.getElementById("method-skill-catalog-body");
  if (!container) return;

  const catalog = state.runPlanData?.run_plan?.method_catalog || null;
  if (!catalog) {
    container.innerHTML = renderEmptyState({
      title: "方法技能集尚未生成",
      description: "需要先确认变量角色和研究设计方案，系统才会生成 OLS、DID、IV、RDD、PSM、DML 的前置条件目录。",
    });
    return;
  }

  const methods = catalog.methods || [];
  container.innerHTML = `
    <div class="method-catalog-summary">
      <div>
        <span class="eyebrow">方法技能集</span>
        <h4>${escapeHtml(catalog.source || "StatsPAI/CoPaper methodology index")}</h4>
        <p class="muted">这里只做方法前置条件判断，不代表已经执行 StatsPAI。</p>
      </div>
      ${renderEvidenceBadge({ evidence_level: catalog.evidence_level || "local_file" })}
    </div>
    <div class="method-skill-list">
      ${methods.map((method) => `
        <article class="method-skill-card ${method.readiness_status === "ready" ? "is-ready" : "is-blocked"}">
          <div class="method-skill-card-head">
            <div>
              <strong>${escapeHtml(method.label || method.id || "")}</strong>
              <p class="muted">${escapeHtml(method.summary || "")}</p>
            </div>
            <span class="status-chip ${method.readiness_status === "ready" ? "is-ready" : "is-blocked"}">
              ${escapeHtml(methodReadinessLabel(method.readiness_status))}
            </span>
          </div>
          <div class="method-skill-meta">
            <span>${escapeHtml(method.statspai_method || "")}</span>
            <span>执行者：${escapeHtml(method.agent_role || "")}</span>
            <span>证据：${escapeHtml(method.evidence_level || "local_file")}</span>
          </div>
          <ul class="method-requirement-list">
            ${(method.requirements || []).map(renderMethodRequirement).join("")}
          </ul>
          ${method.blockers?.length ? `
            <div class="method-blockers">
              阻塞原因：${method.blockers.map((blocker) => escapeHtml(productTermLabel(blocker))).join("、")}
            </div>
          ` : ""}
        </article>
      `).join("")}
    </div>
  `;
}

function renderMethodWorkflows() {
  const containers = Array.from(document.querySelectorAll("[data-method-workflow-body]"));
  if (!containers.length) return;

  const workflows = state.methodWorkflowsData;
  const html = workflows ? renderMethodWorkflowsBody(workflows) : renderEmptyState({
    title: "方法工作流尚未生成",
    description: "需要先确认研究设计方案，系统才会给出 OLS、DID、IV、RDD、PSM、DML 的执行前门禁。",
  });

  containers.forEach((container) => {
    container.innerHTML = html;
  });
}

const METHOD_WORKFLOW_REFERENCE_LABELS = [
  "OLS：可执行",
  "DID：缺少时间变量、处理时点",
  "IV：缺少工具变量",
  "RDD：缺少断点运行变量",
  "PSM：可预检",
  "DML：可预检",
];

function renderMethodWorkflowsBody(workflows) {
  const methods = workflows.methods || [];
  if (!methods.length) {
    return renderEmptyState({
      title: "暂无方法工作流",
      description: "当前项目还没有可检查的方法清单。",
    });
  }

  return `
    <div class="method-workflow-summary">
      <div>
        <span class="eyebrow">方法工作流</span>
        <h4>先检查方法门禁，再批准执行计划</h4>
        <p class="muted">默认只展示状态摘要；变量、诊断和阻塞原因放在“查看方法要求”里，避免一屏堆满技术细节。</p>
      </div>
      ${renderEvidenceBadge({ evidence_level: workflows.evidence_level || "local_file" })}
    </div>
    <div class="method-workflow-list">
      ${methods.map((method) => `
        <article class="method-workflow-card ${method.readiness_status === "ready" ? "is-ready" : "is-blocked"}">
          <div class="method-workflow-card-head">
            <div>
              <strong>${escapeHtml(method.label || method.method || method.id || "")}</strong>
              <p class="muted">${escapeHtml(method.summary || "")}</p>
            </div>
            <span class="status-chip ${method.readiness_status === "ready" ? "is-ready" : "is-blocked"}">
              ${escapeHtml(methodReadinessLabel(method.readiness_status))}
            </span>
          </div>
          <details class="method-workflow-details">
            <summary>查看方法要求</summary>
            <div class="method-workflow-detail-grid">
              <div>
                <span class="meta-label">输入要求</span>
                <p>${(method.required_inputs || []).map((item) => `<code>${escapeHtml(item)}</code>`).join(" ")}</p>
              </div>
              <div>
                <span class="meta-label">诊断证据</span>
                <p>${(method.required_diagnostics || []).map((item) => `<code>${escapeHtml(item)}</code>`).join(" ")}</p>
              </div>
              <div>
                <span class="meta-label">阻塞原因</span>
                <p>${method.blockers?.length ? method.blockers.map((blocker) => escapeHtml(productTermLabel(blocker))).join("、") : "无阻塞项"}</p>
              </div>
            </div>
          </details>
        </article>
      `).join("")}
    </div>
  `;
}

async function handleSaveDesignSpec(event) {
  event.preventDefault();
  if (!state.selectedProjectId) return;

  const payload = {
    research_question: document.getElementById("design-spec-question")?.value?.trim() || "",
    identification_strategy: {
      name: document.getElementById("design-spec-strategy")?.value?.trim() || "baseline_ols",
      summary: document.getElementById("design-spec-summary")?.value?.trim() || "",
      assumptions: [],
      threats: parseCommaField("design-spec-threats"),
    },
    model: {
      estimator: document.getElementById("design-spec-estimator")?.value?.trim() || "ols",
      formula: document.getElementById("design-spec-formula")?.value?.trim() || "",
      fixed_effects: parseCommaField("design-spec-fixed-effects"),
      cluster_by: parseCommaField("design-spec-cluster-by"),
      sample_filter: "all",
    },
    note: document.getElementById("design-spec-note")?.value?.trim() || "",
  };

  clearV2Error("design");
  state.savingDesignSpec = true;
  renderDesignSpecEditor();
  try {
    await v2api.designSpec.save(state.selectedProjectId, payload);
    state.designSpecData = await v2api.designSpec.get(state.selectedProjectId);
    try {
      state.runPlanData = await v2api.runPlan.get(state.selectedProjectId);
    } catch (error) {
      state.runPlanData = null;
    }
    state.overviewData = await v2api.overview.get(state.selectedProjectId);
    state.methodWorkflowsData = await v2api.methodWorkflows.get(state.selectedProjectId);
    renderDesignSpecEditor();
    renderMethodSkillCatalog();
    renderMethodWorkflows();
    renderWorkflowContract(state.overviewData.workflow_contract);
    document.getElementById("design-spec-save-status").textContent = "已保存";
  } catch (error) {
    showV2Error("design", `保存研究设计方案失败：${error.message}`);
  } finally {
    state.savingDesignSpec = false;
    renderDesignSpecEditor();
  }
}

function renderRunPlanEditor() {
  const runPlan = state.runPlanData?.run_plan || null;
  const form = document.getElementById("run-plan-confirmation-form");
  const meta = document.getElementById("run-plan-editor-meta");
  const statusPill = document.getElementById("run-plan-status-pill");
  const saveButton = document.querySelector("[data-run-plan-save]");
  if (!form || !meta || !statusPill) return;

  if (!runPlan) {
    meta.textContent = "正在读取执行计划，需先确认研究设计方案。";
    if (saveButton) saveButton.disabled = true;
    return;
  }

  setTextField("run-plan-tasks", JSON.stringify(runPlan.tasks || [], null, 2));
  setTextField("run-plan-outputs", joinRoleValues(runPlan.outputs || []));
  statusPill.textContent = `${runPlan.status || "draft"} · ${runPlan.evidence_level || "local_file"}`;
  meta.textContent = `${runPlan.dataset_path || "未绑定数据集"} · version=${runPlan.version ?? 0} · design_spec_version=${runPlan.design_spec_version ?? 0}`;
  if (saveButton) {
    saveButton.disabled = state.savingRunPlan;
  }
  document.getElementById("run-plan-save-status").textContent = state.savingRunPlan ? "保存中..." : "";
}

async function handleSaveRunPlan(event) {
  event.preventDefault();
  if (!state.selectedProjectId) return;

  let tasks = [];
  try {
    tasks = JSON.parse(document.getElementById("run-plan-tasks")?.value || "[]");
  } catch (error) {
    showV2Error("empirical-execution", "执行计划任务必须是 JSON 数组。");
    return;
  }

  const payload = {
    tasks,
    outputs: parseCommaField("run-plan-outputs"),
    note: document.getElementById("run-plan-note")?.value?.trim() || "",
  };

  clearV2Error("empirical-execution");
  state.savingRunPlan = true;
  renderRunPlanEditor();
  try {
    await v2api.runPlan.save(state.selectedProjectId, payload);
    state.runPlanData = await v2api.runPlan.get(state.selectedProjectId);
    state.overviewData = await v2api.overview.get(state.selectedProjectId);
    state.methodWorkflowsData = await v2api.methodWorkflows.get(state.selectedProjectId);
    renderRunPlanEditor();
    renderMethodWorkflows();
    renderExecutionPreflight();
    document.getElementById("run-plan-save-status").textContent = "已保存";
  } catch (error) {
    showV2Error("empirical-execution", `保存执行计划失败：${error.message}`);
  } finally {
    state.savingRunPlan = false;
    renderRunPlanEditor();
  }
}

// --- Research Design Page ---

function renderResearchDesign() {
  const data = state.designData;
  if (!data) {
    document.getElementById("design-question").innerHTML = "<p class='muted'>加载中...</p>";
    return;
  }

  clearV2Error("design");

  // Evidence banner
  const bannerHtml = renderEvidenceBanner(data._meta);
  const existingBanner = document.querySelector("#view-research-design > .evidence-banner");
  if (existingBanner) existingBanner.remove();
  if (bannerHtml) {
    document.getElementById("view-research-design").insertAdjacentHTML("afterbegin", bannerHtml);
  }

  renderDesignSpecEditor();
  renderMethodSkillCatalog();
  renderMethodWorkflows();

  // Question
  document.getElementById("design-question").innerHTML = `
    <div class="project-card">
      <strong>${escapeHtml(data.research_question || "未设置")}</strong>
      <div class="muted" style="margin-top:8px;">变量角色将在 Phase B 自动推断。</div>
    </div>
  `;

  // Strategies
  const strategies = data.strategies || [];
  document.getElementById("design-strategies").innerHTML = strategies.map((s) => `
    <div class="project-card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>${escapeHtml(s.name)}</strong>
        ${renderEvidenceBadge({ evidence_level: s.evidence_level })}
      </div>
      <div class="muted">状态：${s.status === "candidate" ? "候选方案" : s.status}</div>
    </div>
  `).join("");

  // Pending confirmations
  const pending = data.pending_confirmations || [];
  document.getElementById("design-pending").innerHTML = pending.length
    ? pending.map((p, i) => `
        <div class="event-item">
          <span style="color:#e67e22;font-weight:600;">${i + 1}.</span>
          <div class="event-item-content">${escapeHtml(p)}</div>
        </div>
      `).join("")
    : `<p class="muted">暂无待确认项</p>`;
}

// --- Paper Draft Page ---

function renderPaperDraft() {
  const data = state.draftsData;
  if (!data) {
    document.getElementById("drafts-list").innerHTML = "<p class='muted'>加载中...</p>";
    renderResultsDraftEvidence();
    renderManuscriptCandidates();
    return;
  }

  clearV2Error("draft");
  renderResultsDraftEvidence();
  renderManuscriptCandidates();

  // Evidence banner (local_file is good, but show it)
  const bannerHtml = renderEvidenceBanner(data._meta);
  const existingBanner = document.querySelector("#view-paper-draft > .evidence-banner");
  if (existingBanner) existingBanner.remove();
  if (bannerHtml) {
    document.getElementById("view-paper-draft").insertAdjacentHTML("afterbegin", bannerHtml);
  }

  const items = data.items || [];
  document.getElementById("drafts-count").textContent = items.length;

  if (items.length === 0) {
    document.getElementById("drafts-list").innerHTML = renderEmptyState(data.empty_state);
  } else {
    document.getElementById("drafts-list").innerHTML = items.map((draft) => `
      <div class="project-card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <strong>${escapeHtml(draft.title)}</strong>
          <span class="pill">${draft.format || "md"}</span>
        </div>
        <div class="muted">${escapeHtml(draft.path)} · ${draft.status === "available" ? "✓ 可用" : draft.status}</div>
      </div>
    `).join("");
  }
}

function renderResultsDraftEvidence() {
  const findingsContainer = document.getElementById("results-findings-list");
  const sectionsContainer = document.getElementById("draft-evidence-sections");
  if (!findingsContainer || !sectionsContainer) return;

  const data = state.resultsDraftData;
  if (!data) {
    findingsContainer.innerHTML = "<p class='muted'>正在读取完整执行结果...</p>";
    sectionsContainer.innerHTML = "<p class='muted'>正在读取草稿证据绑定...</p>";
    return;
  }

  if (data.empty_state) {
    const empty = renderEmptyState(data.empty_state);
    findingsContainer.innerHTML = empty;
    sectionsContainer.innerHTML = empty;
    return;
  }

  const findings = data.findings || [];
  findingsContainer.innerHTML = findings.length
    ? findings.map((finding) => `
      <article class="project-card finding-card">
        <div class="card-row">
          <strong>${escapeHtml(finding.title || finding.id)}</strong>
          ${renderEvidenceBadge({ evidence_level: finding.evidence_level })}
        </div>
        <div class="card-row finding-review-row">
          <span class="review-status ${finding.can_write_to_draft ? "is-approved" : ""}">
            审阅状态：${escapeHtml(reviewStatusLabel(finding.review_status || "needs_review"))}
          </span>
          <span class="review-status ${finding.can_write_to_draft ? "is-approved" : "is-blocked"}">
            可写入正文：${yesNo(finding.can_write_to_draft)}
          </span>
        </div>
        <div class="finding-estimate">
          ${escapeHtml(finding.treatment)} → ${escapeHtml(finding.dependent_var)}:
          <strong>${formatNumber(finding.estimate)}</strong>
          <span class="muted">标准误=${formatNumber(finding.std_error)} · p=${formatNumber(finding.p_value)} · 样本量=${escapeHtml(String(finding.sample_size || "-"))}</span>
        </div>
        <div class="muted evidence-line">
          运行：${escapeHtml(finding.run_id)} · 执行计划版本：${escapeHtml(String(finding.run_plan_version || "-"))}
        </div>
        <div class="muted evidence-line">${escapeHtml(finding.artifact_path || "")}</div>
        ${renderFindingMethodEvidence(finding.method_evidence)}
        ${renderFindingReviewPanel(finding)}
      </article>
    `).join("")
    : "<p class='muted'>最新完整执行暂未生成可展示的结果论断。</p>";

  const sections = data.draft_sections || [];
  sectionsContainer.innerHTML = sections.length
    ? sections.map((section) => {
      const binding = section.evidence_binding || {};
      return `
        <article class="project-card draft-section-binding">
          <div class="card-row">
            <strong>${escapeHtml(section.title || section.id)}</strong>
            ${renderEvidenceBadge({ evidence_level: section.source_evidence_level })}
          </div>
          <div class="muted evidence-line">${escapeHtml(section.source_path || "")}</div>
          <div class="muted evidence-line">
            论断证据：
            ${renderEvidenceBadge({ evidence_level: binding.claim_evidence_level })}
            运行：${escapeHtml(binding.run_id || "")} · 执行计划版本：${escapeHtml(String(binding.run_plan_version || "-"))}
          </div>
          <div class="muted evidence-line">${escapeHtml(binding.artifact_path || "")}</div>
        </article>
      `;
    }).join("")
    : "<p class='muted'>尚未发现可绑定的草稿章节。</p>";
}

function renderFindingMethodEvidence(methodEvidence) {
  if (!methodEvidence) {
    return `
      <div class="finding-method-evidence is-empty">
        <strong>方法执行证据</strong>
        <span class="muted">尚未绑定 method_execution_result.json。</span>
      </div>
    `;
  }

  return `
    <div class="finding-method-evidence">
      <div class="card-row">
        <strong>方法执行证据</strong>
        ${renderEvidenceBadge({ evidence_level: methodEvidence.evidence_level })}
      </div>
      <p class="method-evidence-summary">
        ${escapeHtml(productTermLabel(methodEvidence.method_id || "-"))} ·
        n=${escapeHtml(String(methodEvidence.nobs ?? "-"))} ·
        β=${formatNumber(methodEvidence.treatment_coefficient)} ·
        标准误=${formatNumber(methodEvidence.standard_error)} ·
        p=${formatNumber(methodEvidence.p_value)} ·
        95% 置信区间 ${renderConfidenceInterval(methodEvidence.confidence_interval)} ·
        评估器${escapeHtml(evaluatorStatusLabel(methodEvidence.evaluator_status || "needs_review"))}
      </p>
      <div class="muted evidence-line">执行引擎：${escapeHtml(methodEvidence.engine || "-")}</div>
      <div class="muted evidence-line">公式：${escapeHtml(methodEvidence.formula || "-")}</div>
      <div class="muted evidence-line">${escapeHtml(methodEvidence.artifact_path || "")}</div>
    </div>
  `;
}

function evaluatorStatusLabel(status) {
  return {
    passed: "通过",
    needs_review: "需要复核",
    failed: "未通过",
  }[status] || status;
}

function renderConfidenceInterval(interval) {
  if (!interval) return "-";
  return `${formatNumber(interval.low)} ~ ${formatNumber(interval.high)}`;
}

function renderManuscriptCandidates() {
  const container = document.getElementById("manuscript-candidates-list");
  if (!container) return;

  const data = state.manuscriptCandidatesData;
  if (!data) {
    container.innerHTML = "<p class='muted'>正在根据已审阅论断生成正文候选...</p>";
    return;
  }

  const candidates = data.items || [];
  if (!candidates.length) {
    container.innerHTML = data.empty_state
      ? renderEmptyState({
          title: data.empty_state.title || "尚无正文候选",
          description: data.empty_state.description || "需要先确认至少一个结果论断",
        })
      : "<p class='muted'>需要先确认至少一个结果论断</p>";
    return;
  }

  container.innerHTML = candidates.map((candidate) => {
    const provenance = candidate.provenance || {};
    return `
      <article class="project-card manuscript-candidate-card">
        <div class="card-row">
          <strong>${escapeHtml(candidate.section || "正文")} · ${escapeHtml(candidate.title || candidate.id)}</strong>
          <span class="review-status">状态：${escapeHtml(candidateStatusLabel(candidate.status || "draft"))}</span>
        </div>
        <div class="card-row finding-review-row">
          <span class="review-status ${candidate.review_status === "approved" ? "is-approved" : ""}">
            审阅状态：${escapeHtml(reviewStatusLabel(candidate.review_status || "needs_review"))}
          </span>
          <span class="review-status ${candidate.can_promote ? "is-approved" : "is-blocked"}">
            可进入导出：${yesNo(candidate.can_promote)}
          </span>
          <span class="review-status ${candidate.promotion_status === "ready_for_export" ? "is-approved" : ""}">
            提升状态：${escapeHtml(promotionStatusLabel(candidate.promotion_status || "not_promoted"))}
          </span>
          <span class="review-status ${candidate.can_write_back ? "is-approved" : "is-blocked"}">
            可写回正文：${yesNo(candidate.can_write_back)}
          </span>
          <span class="review-status ${candidate.export_status === "preview_ready" ? "is-approved" : ""}">
            导出状态：${escapeHtml(exportStatusLabel(candidate.export_status || "not_started"))}
          </span>
        </div>
        <p class="manuscript-candidate-body">${escapeHtml(candidate.body || "")}</p>
        <div class="muted evidence-line">
          论断：${escapeHtml(candidate.finding_id || "")} · 运行：${escapeHtml(candidate.run_id || "")} · 执行计划版本：${escapeHtml(String(candidate.run_plan_version || "-"))}
        </div>
        <div class="candidate-provenance">
          ${renderCandidateProvenance("source_draft", provenance.source_draft)}
          ${renderCandidateProvenance("result_artifact", provenance.result_artifact)}
          ${renderCandidateProvenance("review_decision", provenance.review_decision)}
          ${renderCandidateProvenance("candidate_review", provenance.candidate_review)}
          ${renderCandidateProvenance("promotion_state", provenance.promotion_state)}
          ${renderCandidateProvenance("export_package", provenance.export_package)}
        </div>
        ${renderCandidateReviewPanel(candidate)}
        ${renderCandidatePromotePanel(candidate)}
        ${renderCandidateExportPreflightPanel(candidate)}
      </article>
    `;
  }).join("");
}

function renderCandidateProvenance(label, item = {}) {
  if (!item || (!item.path && !item.evidence_level)) return "";
  return `
    <div class="candidate-provenance-row">
      <span>${escapeHtml(provenanceLabel(label))}</span>
      <span>${escapeHtml(item.path || "")}</span>
      ${renderEvidenceBadge({ evidence_level: item.evidence_level })}
    </div>
  `;
}

function renderCandidatePromotePanel(candidate) {
  const promotion = candidate.promotion || {};
  const canPromote = candidate.can_promote === true;
  const isPromoting = state.promotingCandidateId === candidate.id;
  const disabled = !canPromote || isPromoting;
  return `
    <div class="candidate-promote-panel">
      <div class="card-row">
        <div>
          <strong>导出前检查</strong>
          <div class="muted evidence-line">
            ${candidate.promotion_status === "ready_for_export"
              ? "已进入导出前检查：该段落可以生成写回预览。"
              : "需要先确认正文候选，才能进入导出前检查。"}
          </div>
        </div>
        <button
          class="primary-button"
          data-candidate-id="${escapeHtml(candidate.id)}"
          data-candidate-promote-action="preflight"
          ${disabled ? "disabled" : ""}
        >
          ${isPromoting ? "生成中..." : "进入导出前检查"}
        </button>
      </div>
      <div class="muted evidence-line">
        导出前提升检查不会直接覆盖 paper_draft.md；可写回正文：${yesNo(candidate.can_write_back)}
      </div>
      ${promotion.evidence_level ? `
        <div class="muted evidence-line">
          提升证据：
          ${renderEvidenceBadge({ evidence_level: promotion.evidence_level })}
          ${escapeHtml(promotion.promotion_path || "")}
        </div>
      ` : ""}
    </div>
  `;
}

function renderCandidateExportPreflightPanel(candidate) {
  const exportEntry = candidate.export || {};
  const isExporting = state.exportingCandidateId === candidate.id;
  const canExportPreflight = candidate.promotion_status === "ready_for_export" && candidate.can_export === true;
  const disabled = !canExportPreflight || isExporting;
  return `
    <div class="candidate-export-panel">
      <div class="card-row">
        <div>
          <strong>写回预览</strong>
          <div class="muted evidence-line">
            ${candidate.export_status === "preview_ready"
              ? "预览已就绪：已生成独立写回预览。"
              : "进入导出前检查后可生成独立预览和导出清单。"}
          </div>
        </div>
        <button
          class="ghost-button"
          data-candidate-id="${escapeHtml(candidate.id)}"
          data-candidate-export-preflight-action="preview"
          ${disabled ? "disabled" : ""}
        >
          ${isExporting ? "生成中..." : "生成写回预览"}
        </button>
      </div>
      ${candidate.writeback_preview_path ? `
        <div class="muted evidence-line">写回预览路径：${escapeHtml(candidate.writeback_preview_path)}</div>
      ` : ""}
      ${candidate.export_manifest_path ? `
        <div class="muted evidence-line">清单路径：${escapeHtml(candidate.export_manifest_path)}</div>
      ` : ""}
      ${exportEntry.evidence_level ? `
        <div class="muted evidence-line">
          导出预检：
          ${renderEvidenceBadge({ evidence_level: exportEntry.evidence_level })}
          ${escapeHtml(exportEntry.writeback_preview_path || "")}
        </div>
      ` : ""}
    </div>
  `;
}

function renderCandidateReviewPanel(candidate) {
  const review = candidate.review || {};
  const note = review.note || "";
  const isSaving = state.reviewingCandidateId === candidate.id;
  return `
    <div class="finding-review-panel candidate-review-panel">
      <label class="claim-review-note">
        <span>正文候选审阅备注</span>
        <textarea data-candidate-review-note="${escapeHtml(candidate.id)}" rows="2" placeholder="说明该段落是否可以进入正文，或需要怎样修改。">${escapeHtml(note)}</textarea>
      </label>
      <div class="claim-review-actions">
        ${["approve", "needs_revision", "reject"].map((action) => `
          <button
            class="${action === "approve" ? "primary-button" : "ghost-button"}"
            data-candidate-id="${escapeHtml(candidate.id)}"
            data-candidate-review-action="${action}"
            ${isSaving ? "disabled" : ""}
          >
            ${isSaving && state.reviewingCandidateAction === action ? "保存中..." : candidateReviewActionLabel(action)}
          </button>
        `).join("")}
      </div>
      ${review.evidence_level ? `
        <div class="muted evidence-line">
          正文候选审阅：
          ${renderEvidenceBadge({ evidence_level: review.evidence_level })}
          执行者：${escapeHtml(review.actor || "用户")} · ${escapeHtml(review.timestamp || "")}
        </div>
      ` : `<div class="muted evidence-line">该正文候选尚未完成人工审阅。</div>`}
    </div>
  `;
}

function candidateReviewActionLabel(action) {
  return {
    approve: "确认段落",
    needs_revision: "需要修改",
    reject: "拒绝段落",
  }[action] || action;
}

function renderFindingReviewPanel(finding) {
  const review = finding.review || {};
  const note = review.note || "";
  const isSaving = state.reviewingFindingId === finding.id;
  return `
    <div class="finding-review-panel">
      <label class="claim-review-note">
        <span>审阅备注</span>
        <textarea data-finding-review-note="${escapeHtml(finding.id)}" rows="2" placeholder="说明为什么允许写入、拒绝或需要修改。">${escapeHtml(note)}</textarea>
      </label>
      <div class="claim-review-actions">
        ${["approve", "needs_revision", "reject"].map((action) => `
          <button
            class="${action === "approve" ? "primary-button" : "ghost-button"}"
            data-finding-id="${escapeHtml(finding.id)}"
            data-finding-review-action="${action}"
            ${isSaving ? "disabled" : ""}
          >
            ${isSaving && state.reviewingFindingAction === action ? "保存中..." : findingReviewActionLabel(action)}
          </button>
        `).join("")}
      </div>
      ${review.evidence_level ? `
        <div class="muted evidence-line">
          审阅证据：
          ${renderEvidenceBadge({ evidence_level: review.evidence_level })}
          执行者：${escapeHtml(review.actor || "用户")} · ${escapeHtml(review.timestamp || "")}
        </div>
      ` : `<div class="muted evidence-line">该结果论断尚未完成人工审阅。</div>`}
    </div>
  `;
}

function findingReviewActionLabel(action) {
  return {
    approve: "允许写入正文",
    needs_revision: "需要修改",
    reject: "拒绝使用",
  }[action] || action;
}

async function reviewFinding(findingId, action) {
  if (!state.selectedProjectId || !findingId || !action) return;
  const note = document.querySelector(`[data-finding-review-note="${CSS.escape(findingId)}"]`)?.value?.trim() || "";
  clearV2Error("draft");
  state.reviewingFindingId = findingId;
  state.reviewingFindingAction = action;
  renderResultsDraftEvidence();
  try {
    await v2api.resultsDraft.reviewFinding(state.selectedProjectId, findingId, { action, note });
    state.resultsDraftData = await v2api.resultsDraft.get(state.selectedProjectId);
    state.manuscriptCandidatesData = await v2api.manuscriptCandidates.get(state.selectedProjectId);
    renderResultsDraftEvidence();
    renderManuscriptCandidates();
  } catch (error) {
    showV2Error("draft", `保存结果论断卡审阅失败：${error.message}`);
  } finally {
    state.reviewingFindingId = null;
    state.reviewingFindingAction = null;
    renderResultsDraftEvidence();
  }
}

async function reviewManuscriptCandidate(candidateId, action) {
  if (!state.selectedProjectId || !candidateId || !action) return;
  const note = document.querySelector(`[data-candidate-review-note="${CSS.escape(candidateId)}"]`)?.value?.trim() || "";
  clearV2Error("draft");
  state.reviewingCandidateId = candidateId;
  state.reviewingCandidateAction = action;
  renderManuscriptCandidates();
  try {
    await v2api.manuscriptCandidates.reviewCandidate(state.selectedProjectId, candidateId, { action, note });
    state.manuscriptCandidatesData = await v2api.manuscriptCandidates.get(state.selectedProjectId);
    renderManuscriptCandidates();
  } catch (error) {
    showV2Error("draft", `保存正文候选审阅失败：${error.message}`);
  } finally {
    state.reviewingCandidateId = null;
    state.reviewingCandidateAction = null;
    renderManuscriptCandidates();
  }
}

async function promoteManuscriptCandidate(candidateId) {
  if (!state.selectedProjectId || !candidateId) return;
  clearV2Error("draft");
  state.promotingCandidateId = candidateId;
  renderManuscriptCandidates();
  try {
    await v2api.manuscriptCandidates.promoteCandidate(state.selectedProjectId, candidateId, {
      note: "进入导出前检查，不直接覆盖草稿。",
    });
    state.manuscriptCandidatesData = await v2api.manuscriptCandidates.get(state.selectedProjectId);
    renderManuscriptCandidates();
  } catch (error) {
    showV2Error("draft", `生成正文候选导出前检查失败：${error.message}`);
  } finally {
    state.promotingCandidateId = null;
    renderManuscriptCandidates();
  }
}

async function exportPreflightManuscriptCandidate(candidateId) {
  if (!state.selectedProjectId || !candidateId) return;
  clearV2Error("draft");
  state.exportingCandidateId = candidateId;
  renderManuscriptCandidates();
  try {
    await v2api.manuscriptCandidates.exportPreflightCandidate(state.selectedProjectId, candidateId, {
      note: "生成写回预览和导出清单，不直接覆盖草稿。",
    });
    state.manuscriptCandidatesData = await v2api.manuscriptCandidates.get(state.selectedProjectId);
    renderManuscriptCandidates();
  } catch (error) {
    showV2Error("draft", `生成写回预览失败：${error.message}`);
  } finally {
    state.exportingCandidateId = null;
    renderManuscriptCandidates();
  }
}

function formatNumber(value) {
  if (value === null || value === undefined || value === "") return "-";
  const number = Number(value);
  if (!Number.isFinite(number)) return escapeHtml(String(value));
  if (Math.abs(number) < 0.001 && number !== 0) return number.toExponential(2);
  return number.toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
}

// --- Artifacts & Replication Page ---

function renderArtifactsReplication() {
  renderReviewerScorecard();
  renderVerifierGates();
  renderExportPackageWorkbench();

  const artifacts = mergedArtifacts(state.selectedProject);
  const container = document.getElementById("artifacts-replication-list");

  if (artifacts.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📦</div>
        <h4>暂无产物</h4>
        <p class="muted">运行工作流后将在此显示产物。</p>
      </div>
    `;
    return;
  }

  container.innerHTML = artifacts.map((artifact) => `
    <div class="project-card" style="cursor:pointer;" data-artifact-id="${escapeHtml(artifact.path)}" onclick="loadProvenance('${escapeHtml(artifact.path)}')">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>${escapeHtml(artifact.kind)}</strong>
        <span class="pill">🔍 查看溯源</span>
      </div>
      <div class="muted">${escapeHtml(artifact.path)}</div>
      <div class="muted">${escapeHtml(artifact.description || "")}</div>
    </div>
  `).join("");
}

function renderVerifierGates() {
  const container = document.getElementById("verifier-gate-body");
  if (!container) return;

  const data = state.verifierChecksData;
  if (!data) {
    container.innerHTML = "<p class='muted'>正在读取导出前验证...</p>";
    return;
  }

  const checks = data.checks || [];
  if (!checks.length) {
    container.innerHTML = `
      <div class="verifier-gate-empty">
        <div>
          <strong>${escapeHtml(data.empty_state?.title || "尚未运行验证闸门")}</strong>
          <p class="muted">${escapeHtml(data.empty_state?.description || "运行后会逐项检查结果绑定、复现清单、方法执行产物、草稿预览和 docx 预检。")}</p>
        </div>
        <button class="primary-button" data-run-verifier-checks ${state.runningVerifierChecks ? "disabled" : ""}>
          ${state.runningVerifierChecks ? "核验中..." : "运行验证闸门"}
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="verifier-gate-summary">
      <div>
        <span class="eyebrow">docx 导出</span>
        <strong>${data.can_export_docx ? "可以进入人工导出" : "保持阻断"}</strong>
        <p class="muted">${escapeHtml(data.next_manual_action || "先处理失败项，再进入最终导出。")}</p>
      </div>
      <button class="primary-button" data-run-verifier-checks ${state.runningVerifierChecks ? "disabled" : ""}>
        ${state.runningVerifierChecks ? "核验中..." : "重新运行核验"}
      </button>
      <button id="verifier-final-export-button" class="ghost-button" data-docx-final-export ${!state.verifierChecksData?.can_export_docx ? "disabled" : ""}>
        docx 最终导出
      </button>
    </div>
    <div class="verifier-gate-list">
      ${checks.map((check) => `
        <div class="verifier-gate-row is-${escapeHtml(check.status || "unknown")}">
          <span class="verifier-gate-status">${verifierCheckStatusText(check.status)}</span>
          <div>
            <strong>${escapeHtml(check.label || check.id)}</strong>
            <p class="muted">${escapeHtml(check.detail || "")}</p>
            <code>${escapeHtml((check.artifact_paths || []).join(" · ") || "-")}</code>
          </div>
          ${renderEvidenceBadge({ evidence_level: check.evidence_level || "local_file" })}
        </div>
      `).join("")}
    </div>
  `;
}

function verifierCheckStatusText(status) {
  return {
    passed: "通过",
    failed: "失败",
    blocked: "阻断",
  }[status] || "待核验";
}

function renderReviewerScorecard() {
  const container = document.getElementById("reviewer-scorecard-body");
  if (!container) return;

  const data = state.reviewerScorecardData;
  if (!data) {
    container.innerHTML = "<p class='muted'>正在读取审稿评分...</p>";
    return;
  }

  const dimensions = data.dimensions || [];
  if (!dimensions.length) {
    container.innerHTML = `
      <div class="reviewer-scorecard-empty">
        <div>
          <strong>${escapeHtml(data.empty_state?.title || "尚未生成审稿评分卡")}</strong>
          <p class="muted">${escapeHtml(data.empty_state?.description || "生成后会显示五个审稿维度、理由、证据和后续任务建议。")}</p>
        </div>
        <button class="primary-button" data-generate-reviewer-scorecard ${state.generatingReviewerScorecard ? "disabled" : ""}>
          ${state.generatingReviewerScorecard ? "生成中..." : "生成审稿评分卡"}
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="reviewer-scorecard-summary">
      <div>
        <span class="eyebrow">${escapeHtml(data.reviewer_backend || "deterministic_baseline")}</span>
        <strong>来源运行：${escapeHtml(data.source_run_id || "-")}</strong>
      </div>
      ${renderEvidenceBadge({ evidence_level: data.evidence_level || data._meta?.evidence_level || "local_file" })}
    </div>
    <div class="reviewer-scorecard-list">
      ${dimensions.map((dimension) => renderReviewerScorecardRow(dimension)).join("")}
    </div>
  `;
}

function renderReviewerScorecardRow(dimension) {
  const score = Number(dimension.score);
  const isLow = Number.isFinite(score) && score < 6;
  return `
    <article class="reviewer-scorecard-row ${isLow ? "is-low" : "is-ok"}">
      <div class="reviewer-scorecard-row-main">
        <div>
          <strong>${escapeHtml(dimension.label || dimension.id)}</strong>
          <p class="muted">${escapeHtml(scorecardSignalText(dimension))}</p>
        </div>
        <span class="score-pill">${formatNumber(score)}/10</span>
      </div>
      <details class="reviewer-scorecard-detail">
        <summary>查看理由与后续任务</summary>
        <p>${escapeHtml(dimension.rationale || "")}</p>
        <div class="reviewer-evidence-list">
          ${(dimension.evidence || []).map((evidence) => `
            <div class="reviewer-evidence-item">
              <code>${escapeHtml(evidence.path || "")}</code>
              ${renderEvidenceBadge({ evidence_level: evidence.evidence_level || "local_file" })}
            </div>
          `).join("")}
        </div>
        <div class="reviewer-suggested-task-list">
          ${(dimension.suggested_tasks || []).map((task) => `
            <div class="reviewer-suggested-task">
              <div>
                <strong>${escapeHtml(task.label || task.id)}</strong>
                <p class="muted">
                  ${escapeHtml(task.target_agent || "Agent")} · ${task.requires_human_acceptance ? "需要人工接受" : "自动任务"}
                </p>
              </div>
              <button class="ghost-button" data-accept-reviewer-task-suggestion="${escapeHtml(task.id)}">
                加入任务队列草案
              </button>
            </div>
          `).join("") || "<p class='muted'>暂无后续任务建议</p>"}
        </div>
      </details>
    </article>
  `;
}

function scorecardSignalText(dimension) {
  const score = Number(dimension.score);
  if (!Number.isFinite(score)) return "等待评分";
  if (score < 6) return "需要补证据或方法升级";
  if (score < 7) return "可继续打磨";
  return "当前证据较稳";
}

function renderExportPackageWorkbench() {
  const container = document.getElementById("export-package-workbench");
  if (!container) return;

  const data = state.exportPackageData;
  if (!data) {
    container.innerHTML = "<p class='muted'>正在读取导出包...</p>";
    return;
  }

  const packages = data.packages || [];
  if (!packages.length) {
    container.innerHTML = data.empty_state
      ? renderEmptyState(data.empty_state)
      : "<p class='muted'>需要先生成导出预检</p>";
    return;
  }

  container.innerHTML = packages.map((pkg) => `
    <article class="review-export-evidence-bench export-package-card">
      <div class="export-bench-header">
        <div>
          <span class="eyebrow">${escapeHtml(pkg.candidate_id || "export_package")}</span>
          <h4>${escapeHtml(pkg.title || "结果导出包")}</h4>
          <p class="muted">
            运行：${escapeHtml(pkg.run_id || "")} · 章节：${escapeHtml(pkg.section || "")} · 导出状态：${escapeHtml(exportStatusLabel(pkg.export_status || ""))}
          </p>
        </div>
        <div class="export-bench-status">
          ${renderEvidenceBadge({ evidence_level: pkg.evidence_level })}
          <span class="review-status ${pkg.evaluator_status === "passed" ? "is-approved" : "is-blocked"}">
            评估器：${escapeHtml(evaluatorStatusLabel(pkg.evaluator_status || "unknown"))}
          </span>
          <span class="review-status ${pkg.can_write_back ? "is-approved" : "is-pending"}">
            写回：${pkg.can_write_back ? "已审批" : "未审批"}
          </span>
        </div>
      </div>

      ${renderExportEvidenceTable(pkg)}

      <div class="export-decision-strip">
        ${renderWritebackApprovalPanel(pkg)}
        ${renderDocxPreflightPanel(pkg)}
      </div>

      <div class="export-workbench-grid">
        <section class="export-evaluator-section">
          <div class="card-row">
            <strong>评估检查</strong>
            <span class="pill">导出前必须通过</span>
          </div>
          <div class="export-evaluator-checks">
            ${(pkg.evaluator_checks || []).map((check) => `
              <div class="export-check is-${escapeHtml(check.status || "unknown")}">
                <span class="export-check-status">${check.status === "passed" ? "✓" : "!"}</span>
                <div>
                  <strong>${escapeHtml(check.label || check.id)}</strong>
                  <div class="muted evidence-line">
                    ${escapeHtml(check.path || "")}
                    ${check.detail ? ` · ${escapeHtml(check.detail)}` : ""}
                  </div>
                </div>
                ${renderEvidenceBadge({ evidence_level: check.evidence_level })}
              </div>
            `).join("")}
          </div>
        </section>

        <section class="export-loop-section">
          <div class="card-row">
            <strong>迭代日志</strong>
            <span class="pill">${escapeHtml(pkg.frontier_loop?.reference || "前沿工程闭环")}</span>
          </div>
          <div class="frontier-iteration-log">
            ${(pkg.frontier_iteration_log || []).map((entry) => `
              <div class="frontier-log-row">
                <span>${escapeHtml(frontierPhaseLabel(entry.phase || ""))}</span>
                <div>
                  <strong>${escapeHtml(entry.title || "")}</strong>
                  <p class="muted">${escapeHtml(entry.description || "")}</p>
                </div>
              </div>
            `).join("")}
          </div>
        </section>
      </div>

      <div class="export-package-footer">
        <p class="muted">${escapeHtml(pkg.next_manual_action || "")}</p>
        <button class="ghost-button" data-open-results-draft>回到结果与草稿查看候选来源</button>
      </div>
    </article>
  `).join("");
}

function renderExportEvidenceTable(pkg) {
  const rows = [
    ["写回预览路径", pkg.writeback_preview_path || "-", "local_file"],
    ["导出清单路径", pkg.manifest_path || "-", "local_file"],
    ["结果产物路径", pkg.result_artifact_path || "-", "local_execution"],
    ["源草稿路径", pkg.source_draft_path || "-", "local_file"],
    ["目标 docx 路径", pkg.docx_preflight?.expected_docx_path || "Submissions/paper_draft.docx", "local_file"],
  ];
  return `
    <table class="export-evidence-table">
      <thead>
        <tr>
          <th>验收项</th>
          <th>路径 / 状态</th>
          <th>证据</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(([label, value, evidence]) => `
          <tr>
            <td>${escapeHtml(label)}</td>
            <td><code>${escapeHtml(value)}</code></td>
            <td>${renderEvidenceBadge({ evidence_level: evidence })}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderWritebackApprovalPanel(pkg) {
  const approval = pkg.writeback_approval || {};
  const isSaving = state.approvingWritebackCandidateId === pkg.candidate_id;
  return `
    <section class="writeback-approval-panel export-decision-panel">
      <div>
        <span class="eyebrow">写回审批</span>
        <strong>${escapeHtml(writebackApprovalLabel(approval.status || "not_requested"))}</strong>
        <p class="muted">审批只写入 ${escapeHtml(approval.path || "state/product/writeback_approvals.json")}，不会覆盖源草稿。</p>
      </div>
      <div class="export-action-row">
        ${["approve", "needs_revision", "reject"].map((action) => `
          <button
            class="${action === "approve" ? "primary-button" : "ghost-button"}"
            data-candidate-id="${escapeHtml(pkg.candidate_id || "")}"
            data-writeback-approval-action="${action}"
            ${isSaving ? "disabled" : ""}
          >
            ${isSaving && state.approvingWritebackAction === action ? "保存中..." : writebackApprovalActionLabel(action)}
          </button>
        `).join("")}
      </div>
    </section>
  `;
}

function renderDocxPreflightPanel(pkg) {
  const preflight = pkg.docx_preflight || {};
  const canRun = pkg.writeback_approval?.status === "approved" && pkg.can_write_back === true;
  const isSaving = state.preflightingDocxCandidateId === pkg.candidate_id;
  return `
    <section class="docx-preflight-panel export-decision-panel">
      <div>
        <span class="eyebrow">docx 导出预检</span>
        <strong>${escapeHtml(docxPreflightLabel(preflight.status || "not_generated"))}</strong>
        <p class="muted">预检生成 ${escapeHtml(preflight.path || "state/product/docx_export_preflight.json")}，只检查条件，不直接生成 docx。</p>
      </div>
      <div class="export-action-row">
        <button
          class="primary-button"
          data-candidate-id="${escapeHtml(pkg.candidate_id || "")}"
          data-docx-preflight-action
          ${!canRun || isSaving ? "disabled" : ""}
        >
          ${isSaving ? "预检中..." : "运行 docx 预检"}
        </button>
      </div>
      ${(preflight.checks || []).length ? `
        <div class="docx-preflight-checks">
          ${(preflight.checks || []).map((check) => `
            <div class="docx-check is-${escapeHtml(check.status || "unknown")}">
              <span>${check.status === "passed" ? "✓" : "!"}</span>
              <strong>${escapeHtml(check.label || check.id)}</strong>
              <code>${escapeHtml(check.path || check.detail || "")}</code>
            </div>
          `).join("")}
        </div>
      ` : ""}
    </section>
  `;
}

function writebackApprovalLabel(status) {
  return {
    not_requested: "尚未审批",
    approved: "已审批，可进入预检",
    rejected: "已拒绝",
    needs_revision: "需要修改",
  }[status] || status;
}

function writebackApprovalActionLabel(action) {
  return {
    approve: "批准写回",
    needs_revision: "要求修改",
    reject: "拒绝写回",
  }[action] || action;
}

function docxPreflightLabel(status) {
  return {
    not_generated: "尚未生成",
    ready: "预检通过",
    blocked: "预检阻塞",
  }[status] || status;
}

async function requestWritebackApproval(candidateId, action) {
  if (!state.selectedProjectId || !candidateId || !action) return;
  clearV2Error("artifacts-replication");
  state.approvingWritebackCandidateId = candidateId;
  state.approvingWritebackAction = action;
  renderArtifactsReplication();
  try {
    await v2api.exportPackage.approveWriteback(state.selectedProjectId, candidateId, {
      action,
      note: "Review & Export 验收台显式写回审批。",
    });
    state.exportPackageData = await v2api.exportPackage.get(state.selectedProjectId);
    renderArtifactsReplication();
  } catch (error) {
    showV2Error("artifacts-replication", `保存写回审批失败：${error.message}`);
  } finally {
    state.approvingWritebackCandidateId = null;
    state.approvingWritebackAction = null;
    renderArtifactsReplication();
  }
}

async function runDocxExportPreflight(candidateId) {
  if (!state.selectedProjectId || !candidateId) return;
  clearV2Error("artifacts-replication");
  state.preflightingDocxCandidateId = candidateId;
  renderArtifactsReplication();
  try {
    await v2api.exportPackage.docxPreflight(state.selectedProjectId, candidateId, {
      note: "Review & Export 验收台运行 docx 导出预检。",
    });
    state.exportPackageData = await v2api.exportPackage.get(state.selectedProjectId);
    renderArtifactsReplication();
  } catch (error) {
    showV2Error("artifacts-replication", `运行 docx 导出预检失败：${error.message}`);
  } finally {
    state.preflightingDocxCandidateId = null;
    renderArtifactsReplication();
  }
}

async function runVerifierChecks() {
  if (!state.selectedProjectId) return;
  clearV2Error("artifacts-replication");
  state.runningVerifierChecks = true;
  renderArtifactsReplication();
  try {
    state.verifierChecksData = await v2api.verifierChecks.run(state.selectedProjectId);
    renderArtifactsReplication();
  } catch (error) {
    showV2Error("artifacts-replication", `运行验证闸门失败：${error.message}`);
  } finally {
    state.runningVerifierChecks = false;
    renderArtifactsReplication();
  }
}

async function generateReviewerScorecard() {
  if (!state.selectedProjectId) return;
  clearV2Error("artifacts-replication");
  state.generatingReviewerScorecard = true;
  renderArtifactsReplication();
  try {
    state.reviewerScorecardData = await v2api.reviewerScorecard.generate(state.selectedProjectId, {
      note: "Review & Export 验收台生成确定性审稿评分卡。",
    });
    renderArtifactsReplication();
  } catch (error) {
    showV2Error("artifacts-replication", `生成审稿评分失败：${error.message}`);
  } finally {
    state.generatingReviewerScorecard = false;
    renderArtifactsReplication();
  }
}

function acceptReviewerTaskSuggestion(taskId) {
  state.acceptingReviewerTaskSuggestionId = taskId;
  showV2Error(
    "artifacts-replication",
    "任务建议已选中：当前版本只生成任务草案入口，不会自动写入 Agent Task Queue。",
  );
  renderArtifactsReplication();
}

async function loadProvenance(artifactId) {
  const panel = document.getElementById("provenance-panel");
  if (!panel) return;

  panel.innerHTML = "<p class='muted'>加载溯源链...</p>";

  try {
    const data = await v2api.provenance.get(artifactId);
    state.provenanceData = data;

    const lineage = data.lineage || [];
    const promotion = data.promotion_policy || {};

    panel.innerHTML = `
      ${renderEvidenceBanner(data._meta)}
      <div class="provenance-lineage">
        ${lineage.map((step, i) => `
          <div class="provenance-step">
            <div class="provenance-step-number">${step.step || i + 1}</div>
            <div class="provenance-step-content">
              <div class="provenance-step-type">${escapeHtml(step.type)}</div>
              <div class="provenance-step-desc">${escapeHtml(step.description)}</div>
              <div class="provenance-step-actor">执行者：${escapeHtml(step.actor)} · ${new Date(step.timestamp).toLocaleString("zh-CN")}</div>
            </div>
          </div>
        `).join("")}
      </div>
      ${promotion.reason ? `
        <div class="evidence-banner" style="margin-top:12px;">
          <span>📋</span>
          <span>提升策略：${promotion.allowed ? "允许提升" : escapeHtml(promotion.reason)}</span>
        </div>
      ` : ""}
    `;
  } catch (error) {
    panel.innerHTML = `<div class="error-banner"><span>加载溯源失败：${escapeHtml(error.message)}</span></div>`;
  }
}

// --- Agent Console Page ---

function renderAgentConsole() {
  const data = state.agentsData;
  if (!data || !data.items) {
    document.getElementById("agent-pipeline-list").innerHTML = "<p class='muted'>加载中...</p>";
    document.getElementById("agent-dimension-list").innerHTML = "<p class='muted'>加载中...</p>";
    return;
  }

  clearV2Error("agent-console");

  // Evidence banner
  const bannerHtml = renderEvidenceBanner(data._meta);
  const existingBanner = document.querySelector("#view-agent-console > .evidence-banner");
  if (existingBanner) existingBanner.remove();
  if (bannerHtml) {
    document.getElementById("view-agent-console").insertAdjacentHTML("afterbegin", bannerHtml);
  }

  const pipeline = data.items.filter((a) => a.role_type === "pipeline");
  const dimension = data.items.filter((a) => a.role_type === "dimension");

  const renderAgentCard = (agent) => {
    const isSelected = state.selectedAgentId === agent.id;
    const initial = agent.name ? agent.name.charAt(0) : "?";
    const colors = ["#1e6f62", "#a14a18", "#2c5282", "#744210", "#553c9a"];
    const color = colors[Math.abs(agent.id.split("").reduce((a, c) => a + c.charCodeAt(0), 0)) % colors.length];
    return `
      <div class="agent-console-card agent-row ${isSelected ? "is-selected is-active" : ""}" data-agent-id="${escapeHtml(agent.id)}" data-task-id="${escapeHtml(agent.id)}" role="button" tabindex="0" onclick="openAgentDetail('${escapeHtml(agent.id)}')">
        <div class="agent-console-avatar" style="background:${color}">${initial}</div>
        <div class="agent-console-info">
          <p class="agent-console-name">${escapeHtml(agent.name)}</p>
          <p class="agent-console-role">${escapeHtml(agent.role)}</p>
        </div>
        <span class="agent-console-status">${escapeHtml(agent.status)}</span>
      </div>
    `;
  };

  document.getElementById("agent-pipeline-list").innerHTML = pipeline.length
    ? pipeline.map(renderAgentCard).join("")
    : "<p class='muted'>暂无流水线角色</p>";

  document.getElementById("agent-dimension-list").innerHTML = dimension.length
    ? dimension.map(renderAgentCard).join("")
    : "<p class='muted'>暂无研究维度智能体</p>";
}

function getAgentIds() {
  return (state.agentsData?.items || []).map((agent) => agent.id).filter(Boolean);
}

function updateAgentDrawerNavigation() {
  const ids = getAgentIds();
  const index = ids.indexOf(state.selectedAgentId);
  const prevButton = document.getElementById("prev-agent-button");
  const nextButton = document.getElementById("next-agent-button");
  if (prevButton) prevButton.disabled = index <= 0;
  if (nextButton) nextButton.disabled = index < 0 || index >= ids.length - 1;
}

function closeAgentDetailDrawer() {
  const drawer = document.getElementById("agent-detail-drawer");
  if (!drawer) return;
  drawer.classList.remove("is-open");
  drawer.setAttribute("aria-hidden", "true");
}

async function openAgentDetail(agentId) {
  const drawer = document.getElementById("agent-detail-drawer");
  if (drawer) {
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
  }
  await selectAgent(agentId);
  updateAgentDrawerNavigation();
}

function navigateToPrevAgent() {
  const ids = getAgentIds();
  const index = ids.indexOf(state.selectedAgentId);
  if (index > 0) void openAgentDetail(ids[index - 1]);
  updateAgentDrawerNavigation();
}

function navigateToNextAgent() {
  const ids = getAgentIds();
  const index = ids.indexOf(state.selectedAgentId);
  if (index >= 0 && index < ids.length - 1) void openAgentDetail(ids[index + 1]);
  updateAgentDrawerNavigation();
}

function renderAgentArtifactPreview(outputs = []) {
  const apiError = state.agentDetailPreviewError || state.apiError;
  if (state.agentDetailPreviewLoading) {
    return `
      <div class="agent-detail-preview-state">
        <strong>正在读取产物正文</strong>
        <p class="muted">产物内容会在当前右侧抽屉内展开，不跳出工作台。</p>
      </div>
    `;
  }
  if (apiError) {
    return `
      <div class="agent-detail-preview-state is-error">
        <strong>无法读取产物正文</strong>
        <p class="muted">${escapeHtml(apiError.message || apiError || "请检查本地产物路径和后端读取权限。")}</p>
      </div>
    `;
  }
  if (state.agentDetailPreviewContent) {
    return `
      <div class="agent-detail-preview-body">
        <div class="muted">当前产物：${escapeHtml(state.agentDetailPreviewPath || "未命名产物")}</div>
        <pre>${escapeHtml(state.agentDetailPreviewContent)}</pre>
      </div>
    `;
  }
  if (!Array.isArray(outputs) || outputs.length === 0) {
    return `
      <div class="agent-detail-preview-state">
        <strong>等待研究完成后自动生成</strong>
        <p class="muted">该 Agent 暂无可预览产物。完成执行后会在这里显示报告、表格或日志摘要。</p>
      </div>
    `;
  }
  return `
    <div class="agent-detail-preview-body">
      <p class="muted">选择一个产物后在这里预览正文。</p>
      ${outputs.map((output) => `
        <button class="ghost-button agent-artifact-preview-button" type="button" data-agent-artifact-path="${escapeHtml(output.path || output.name || "")}">
          ${escapeHtml(output.label || output.path || output.name || "未命名产物")}
        </button>
      `).join("")}
    </div>
  `;
}

function openAgentArtifactPreview(path) {
  state.agentDetailPreviewLoading = true;
  state.agentDetailPreviewError = null;
  state.agentDetailPreviewPath = path;
  const preview = document.getElementById("agent-detail-artifact-preview");
  if (preview) preview.innerHTML = renderAgentArtifactPreview(state.agentDetailData?.agent?.outputs || state.agentDetailData?.outputs || []);

  window.setTimeout(() => {
    state.agentDetailPreviewLoading = false;
    state.agentDetailPreviewContent = path
      ? `产物路径：${path}\n\n当前版本只在抽屉内登记预览入口；完整正文读取将由后端产物读取 API 接管。`
      : "";
    if (preview) preview.innerHTML = renderAgentArtifactPreview(state.agentDetailData?.agent?.outputs || state.agentDetailData?.outputs || []);
  }, 120);
}

function setupAgentDrawerInteractions() {
  document.getElementById("close-agent-detail-drawer")?.addEventListener("click", closeAgentDetailDrawer);
  document.getElementById("prev-agent-button")?.addEventListener("click", navigateToPrevAgent);
  document.getElementById("next-agent-button")?.addEventListener("click", navigateToNextAgent);

  const panels = [
    document.getElementById("agent-pipeline-list"),
    document.getElementById("agent-dimension-list"),
  ].filter(Boolean);
  for (const panel of panels) {
    panel.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const row = target.closest(".agent-row");
      if (!row) return;
      void openAgentDetail(row.dataset.agentId || row.dataset.taskId || "");
    });
    panel.addEventListener("keydown", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (event.key !== "Enter" && event.key !== " ") return;
      const row = target.closest(".agent-row");
      if (!row) return;
      event.preventDefault();
      void openAgentDetail(row.dataset.agentId || row.dataset.taskId || "");
    });
  }

  document.getElementById("agent-detail-artifact-preview")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const output = target.closest("[data-agent-artifact-path]");
    if (!output) return;
    openAgentArtifactPreview(output.dataset.agentArtifactPath || "");
  });
}

async function selectAgent(agentId) {
  state.selectedAgentId = agentId;
  renderAgentConsole(); // re-render to update selection

  const inlinePanel = document.getElementById("agent-detail-panel");
  const drawerPanel = document.getElementById("agent-detail-drawer-content");
  const panels = [inlinePanel, drawerPanel].filter(Boolean);
  const idLabel = document.getElementById("agent-detail-id");
  if (!panels.length) return;

  if (idLabel) idLabel.textContent = agentId;
  panels.forEach((panel) => {
    panel.innerHTML = "<p class='muted'>加载详情...</p>";
  });

  try {
    const data = await v2api.agents.get(agentId);
    state.agentDetailData = data;
    state.agentDetailPreviewLoading = false;
    state.agentDetailPreviewError = null;
    state.agentDetailPreviewContent = null;
    state.agentDetailPreviewPath = null;

    const agent = data.agent || {};
    const identity = data.identity || {};
    const permissions = data.permissions || [];
    const capabilities = data.capabilities || [];
    const cost = data.cost || {};
    const audit = data.audit_log || [];
    const outputs = agent.outputs || data.outputs || [];

    const detailHtml = `
      ${renderEvidenceBanner(data._meta)}

      <div class="agent-detail-section">
        <h4>身份</h4>
        <div class="project-card">
          <strong>${escapeHtml(agent.name || identity.name || agentId)}</strong>
          <div class="muted">角色：${escapeHtml(agent.role || identity.role || "")} · 类型：${escapeHtml(agent.role_type || identity.role_type || "")}</div>
          <div class="muted">模型提供方：${escapeHtml(identity.provider || "local_codex")}</div>
        </div>
      </div>

      <div class="agent-detail-section">
        <h4>权限</h4>
        ${permissions.length ? permissions.map((p) => `
          <div class="permission-item">
            <span>${escapeHtml(p.scope)}</span>
            <span class="permission-level ${p.level === "requires_approval" ? "requires-approval" : p.level === "disabled_in_phase_a" ? "disabled" : ""}">${escapeHtml(p.level)}</span>
          </div>
        `).join("") : "<p class='muted'>暂无权限数据</p>"}
      </div>

      <div class="agent-detail-section">
        <h4>能力注册</h4>
        ${capabilities.length ? capabilities.map((c) => `
          <div class="permission-item">
            <span>${escapeHtml(c.name)} (${escapeHtml(c.id)})</span>
            <span class="permission-level">${escapeHtml(c.status)}</span>
          </div>
        `).join("") : "<p class='muted'>暂无能力数据</p>"}
      </div>

      <div class="agent-detail-section">
        <h4>成本追踪</h4>
        <div class="project-card">
          <div class="muted">模型提供方：${escapeHtml(cost.provider || "local_codex")}</div>
          <div class="muted">预估令牌数：${cost.estimated_tokens || 0}</div>
          <div class="muted">预估成本：$${cost.estimated_cost_usd || 0}</div>
          ${renderEvidenceBadge(cost)}
        </div>
      </div>

      <div class="agent-detail-section">
        <h4>审计日志</h4>
        <div class="event-timeline">
          ${audit.length ? audit.map((log) => `
            <div class="event-item">
              <span class="event-item-time">${new Date(log.timestamp).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}</span>
              <div class="event-item-content">
                <strong>${escapeHtml(log.actor)}</strong> · ${escapeHtml(log.action)}
                <div class="muted" style="margin-top:2px;">${escapeHtml(log.description || "")}</div>
              </div>
            </div>
          `).join("") : "<p class='muted'>暂无审计日志</p>"}
        </div>
      </div>
    `;
    panels.forEach((panel) => {
      panel.innerHTML = detailHtml;
    });
    const preview = document.getElementById("agent-detail-artifact-preview");
    if (preview) preview.innerHTML = renderAgentArtifactPreview(outputs);
    updateAgentDrawerNavigation();
  } catch (error) {
    state.agentDetailPreviewError = error;
    panels.forEach((panel) => {
      panel.innerHTML = `<div class="error-banner"><span>加载智能体详情失败：${escapeHtml(error.message)}</span></div>`;
    });
    const preview = document.getElementById("agent-detail-artifact-preview");
    if (preview) preview.innerHTML = renderAgentArtifactPreview([]);
  }
}

// --- Governance Panel ---

let activeGovernanceTab = "identity";

function switchGovernanceTab(tabName) {
  activeGovernanceTab = tabName;
  document.querySelectorAll(".governance-tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.governanceTab === tabName);
  });
  document.querySelectorAll(".governance-tab-content").forEach((content) => {
    content.classList.toggle("is-active", content.id === `governance-tab-${tabName}`);
  });
  // Re-render current tab with latest data
  renderGovernancePanel();
}

async function loadGovernanceData(projectId) {
  try {
    state.governanceIdentityData = await v2api.governance.identity.get(projectId);
  } catch (error) {
    state.governanceIdentityData = null;
  }
  try {
    state.governancePermissionsData = await v2api.governance.permissions.get(projectId);
  } catch (error) {
    state.governancePermissionsData = null;
  }
  try {
    state.governanceCapabilitiesData = await v2api.governance.capabilities.get(projectId);
  } catch (error) {
    state.governanceCapabilitiesData = null;
  }
  try {
    state.governanceCostsData = await v2api.governance.costs.get(projectId);
  } catch (error) {
    state.governanceCostsData = null;
  }
}

function renderGovernancePanel() {
  clearV2Error("governance-panel");

  // Evidence banner
  const bannerHtml = renderEvidenceBanner({ evidence_level: "local_file", service: "governance_panel", generated_at: new Date().toISOString() });
  const existingBanner = document.querySelector("#view-governance-panel > .evidence-banner");
  if (existingBanner) existingBanner.remove();
  if (bannerHtml) {
    document.getElementById("view-governance-panel").insertAdjacentHTML("afterbegin", bannerHtml);
  }

  switch (activeGovernanceTab) {
    case "identity":
      renderGovernanceIdentityTab();
      break;
    case "permissions":
      renderGovernancePermissionsTab();
      break;
    case "capabilities":
      renderGovernanceCapabilitiesTab();
      break;
    case "costs":
      renderGovernanceCostsTab();
      break;
  }
}

function renderGovernanceIdentityTab() {
  const body = document.getElementById("governance-identity-body");
  const statusPill = document.getElementById("governance-identity-status");
  const data = state.governanceIdentityData;

  if (!data || !data.identity) {
    body.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🆔</div>
        <h4>身份注册表尚未初始化</h4>
        <p class="muted">点击初始化创建默认 Agent 身份。</p>
        <button class="primary-button" onclick="initGovernanceIdentity()">初始化身份注册表</button>
      </div>
    `;
    if (statusPill) statusPill.textContent = "未初始化";
    return;
  }

  const registry = data.identity;
  const identities = registry.identities || [];
  const defaults = registry.default_agents || [];

  if (statusPill) statusPill.textContent = registry.status === "active" ? "已激活" : registry.status || "-";

  body.innerHTML = `
    <div class="governance-section">
      <h4>已注册身份 (${identities.length})</h4>
      ${identities.length ? identities.map((id) => `
        <div class="governance-row">
          <div class="governance-row-main">
            <strong>${escapeHtml(id.display_name || id.id)}</strong>
            <span class="muted">${escapeHtml(id.role || "")} · ${escapeHtml(id.kind || "agent")}</span>
          </div>
          <div class="governance-row-meta">
            <span class="pill ${id.status === "active" ? "is-approved" : ""}">${escapeHtml(id.status || "unknown")}</span>
            ${id.status === "inactive" ? `<button class="ghost-button" onclick="activateGovernanceAgent('${escapeHtml(id.id)}')">激活</button>` : ""}
            ${id.status === "active" ? `<button class="ghost-button" onclick="deactivateGovernanceAgent('${escapeHtml(id.id)}')">停用</button>` : ""}
          </div>
        </div>
      `).join("") : "<p class='muted'>暂无已注册身份</p>"}
    </div>
    <div class="governance-section" style="margin-top: 18px;">
      <h4>默认角色模板</h4>
      ${defaults.map((d) => `
        <div class="governance-row">
          <div class="governance-row-main">
            <strong>${escapeHtml(d.display_name || d.role)}</strong>
            <span class="muted">${escapeHtml(d.role)}</span>
          </div>
        </div>
      `).join("")}
    </div>
  `;
}

function renderGovernancePermissionsTab() {
  const body = document.getElementById("governance-permissions-body");
  const checkBody = document.getElementById("governance-permission-check-body");
  const statusPill = document.getElementById("governance-permissions-status");
  const data = state.governancePermissionsData;

  if (!data || !data.permissions) {
    body.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔐</div>
        <h4>权限策略尚未初始化</h4>
        <p class="muted">点击初始化创建默认权限策略。</p>
        <button class="primary-button" onclick="initGovernancePermissions()">初始化权限策略</button>
      </div>
    `;
    if (statusPill) statusPill.textContent = "未初始化";
    if (checkBody) checkBody.innerHTML = "<p class='muted'>请先初始化权限策略</p>";
    return;
  }

  const registry = data.permissions;
  const policies = registry.policies || [];
  const actionCatalog = registry.action_catalog || [];

  if (statusPill) statusPill.textContent = registry.status === "active" ? "已激活" : registry.status || "-";

  // Build editable permission matrix
  const roles = [...new Set(policies.map((p) => p.subject_id))];
  const matrixHtml = `
    <div class="permission-matrix-wrapper">
      <table class="permission-matrix" id="permission-matrix-table">
        <thead>
          <tr>
            <th>Action \\ Agent</th>
            ${roles.map((r) => `<th>${escapeHtml(r.replace("agent_", "").replace("_01", ""))}</th>`).join("")}
          </tr>
        </thead>
        <tbody>
          ${actionCatalog.map((action) => {
            const cells = roles.map((role) => {
              const policy = policies.find((p) => p.subject_id === role);
              const allowed = policy?.allow?.includes(action);
              const denied = policy?.deny?.includes(action);
              const cellClass = denied ? "denied" : allowed ? "allowed" : "neutral";
              const cellLabel = denied ? "✗" : allowed ? "✓" : "−";
              return `<td class="${cellClass} editable-cell" data-role="${escapeHtml(role)}" data-action="${escapeHtml(action)}" onclick="togglePermissionCell(this)">${cellLabel}</td>`;
            }).join("");
            return `<tr><td class="action-name">${escapeHtml(action)}</td>${cells}</tr>`;
          }).join("")}
        </tbody>
      </table>
    </div>
    <div class="permission-edit-actions" style="margin-top: 12px;">
      <button class="primary-button" onclick="saveGovernancePermissions()">保存更改</button>
      <button class="secondary-button" onclick="renderGovernancePermissionsTab()" style="margin-left: 8px;">取消</button>
    </div>
  `;

  body.innerHTML = `
    <div class="governance-section">
      <h4>权限矩阵 <span class="muted" style="font-size: 12px; font-weight: normal;">（点击单元格切换允许 / 拒绝 / 中性）</span></h4>
      ${matrixHtml}
    </div>
    <div class="governance-section" style="margin-top: 18px;">
      <h4>策略列表</h4>
      ${policies.map((p) => `
        <div class="governance-row">
          <div class="governance-row-main">
            <strong>${escapeHtml(p.subject_id)}</strong>
            <span class="muted">允许: ${p.allow?.length || 0} 项 · 拒绝: ${p.deny?.length || 0} 项</span>
          </div>
        </div>
      `).join("")}
    </div>
  `;

  // Permission check tool
  if (checkBody) {
    const agentOptions = roles.map((r) => `<option value="${escapeHtml(r)}">${escapeHtml(r)}</option>`).join("");
    const actionOptions = actionCatalog.map((a) => `<option value="${escapeHtml(a)}">${escapeHtml(a)}</option>`).join("");
    checkBody.innerHTML = `
      <div class="permission-check-form">
        <label>
          <span>Agent</span>
          <select id="permission-check-agent">${agentOptions}</select>
        </label>
        <label>
          <span>Action</span>
          <select id="permission-check-action">${actionOptions}</select>
        </label>
        <button class="primary-button" onclick="runPermissionCheck()">检查权限</button>
      </div>
      <div id="permission-check-result" class="permission-check-result"></div>
    `;
  }
}

function togglePermissionCell(cell) {
  const role = cell.getAttribute("data-role");
  const action = cell.getAttribute("data-action");
  if (!role || !action) return;

  const currentClass = cell.classList.contains("allowed")
    ? "allowed"
    : cell.classList.contains("denied")
      ? "denied"
      : "neutral";

  const nextMap = { allowed: "denied", denied: "neutral", neutral: "allowed" };
  const labelMap = { allowed: "✓", denied: "✗", neutral: "−" };
  const nextClass = nextMap[currentClass];

  cell.classList.remove("allowed", "denied", "neutral");
  cell.classList.add(nextClass);
  cell.textContent = labelMap[nextClass];
  cell.setAttribute("data-modified", "true");
}

async function saveGovernancePermissions() {
  const data = state.governancePermissionsData;
  if (!data || !data.permissions) return;

  const registry = data.permissions;
  const policies = registry.policies || [];
  const actionCatalog = registry.action_catalog || [];

  // Rebuild policies from DOM
  const cells = document.querySelectorAll("#permission-matrix-table td[data-modified='true']");
  if (cells.length === 0) {
    showV2Success("governance-panel", "没有检测到更改");
    return;
  }

  // Build a map of role -> {allow: Set, deny: Set}
  const roleMap = {};
  for (const p of policies) {
    roleMap[p.subject_id] = {
      id: p.id,
      subject_id: p.subject_id,
      subject_kind: p.subject_kind || "agent",
      project_id: p.project_id,
      allow: new Set(p.allow || []),
      deny: new Set(p.deny || []),
    };
  }

  // Apply all modified cells
  cells.forEach((cell) => {
    const role = cell.getAttribute("data-role");
    const action = cell.getAttribute("data-action");
    const newState = cell.classList.contains("allowed")
      ? "allowed"
      : cell.classList.contains("denied")
        ? "denied"
        : "neutral";

    const entry = roleMap[role];
    if (!entry) return;

    entry.allow.delete(action);
    entry.deny.delete(action);
    if (newState === "allowed") entry.allow.add(action);
    else if (newState === "denied") entry.deny.add(action);
  });

  // Convert to array format
  const newPolicies = Object.values(roleMap).map((e) => ({
    id: e.id,
    subject_id: e.subject_id,
    subject_kind: e.subject_kind,
    project_id: e.project_id,
    allow: Array.from(e.allow),
    deny: Array.from(e.deny),
  }));

  const projectId = state.selectedProjectId;
  if (!projectId) {
    showV2Error("governance-panel", "未选择项目");
    return;
  }

  try {
    const result = await v2api.governance.permissions.save(projectId, newPolicies);
    if (result.status === "saved") {
      showV2Success("governance-panel", `权限策略已保存（${result.policies_count} 条）`);
      await loadGovernanceData(projectId);
    } else {
      showV2Error("governance-panel", "保存失败：" + (result.error || "未知错误"));
    }
  } catch (err) {
    showV2Error("governance-panel", "保存失败: " + err.message);
  }
}

function renderGovernanceCapabilitiesTab() {
  const body = document.getElementById("governance-capabilities-body");
  const statusPill = document.getElementById("governance-capabilities-status");
  const data = state.governanceCapabilitiesData;

  if (!data || !data.capability) {
    body.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">⚙️</div>
        <h4>能力目录尚未索引</h4>
        <p class="muted">点击索引能力目录（包含 StatsPAI 函数）。</p>
        <button class="primary-button" onclick="reindexGovernanceCapabilities()">索引能力目录</button>
      </div>
    `;
    if (statusPill) statusPill.textContent = "未索引";
    return;
  }

  const registry = data.capability;
  const capabilities = registry.capabilities || [];
  const sources = registry.sources || {};
  const classification = registry.classification || {};

  if (statusPill) statusPill.textContent = `${capabilities.length} 项能力`;

  const sourceHtml = Object.entries(sources).map(([name, info]) => `
    <div class="governance-row">
      <div class="governance-row-main">
        <strong>${escapeHtml(name)}</strong>
        <span class="muted">${info.available ? `v${escapeHtml(info.version || "?")} · ${info.function_count || 0} 函数` : "不可用"}</span>
      </div>
    </div>
  `).join("");

  const capList = capabilities.slice(0, 50).map((cap) => `
    <div class="governance-row">
      <div class="governance-row-main">
        <strong>${escapeHtml(cap.name)}</strong>
        <span class="muted">${escapeHtml(cap.namespace || "")} · ${escapeHtml(cap.category || "")} · 风险: ${escapeHtml(cap.risk_level || "?")}</span>
      </div>
      <div class="governance-row-meta">
        <span class="pill ${cap.status === "executable" ? "is-approved" : ""}">${escapeHtml(cap.status || "-")}</span>
      </div>
    </div>
  `).join("");

  const moreMsg = capabilities.length > 50 ? `<p class="muted">... 还有 ${capabilities.length - 50} 项能力</p>` : "";

  body.innerHTML = `
    <div class="governance-section">
      <h4>能力来源</h4>
      ${sourceHtml}
      <button class="ghost-button" style="margin-top: 8px;" onclick="reindexGovernanceCapabilities()">重新索引</button>
    </div>
    <div class="governance-section" style="margin-top: 18px;">
      <h4>能力列表 (${capabilities.length})</h4>
      ${capList}
      ${moreMsg}
    </div>
  `;
}

function renderGovernanceCostsTab() {
  const summaryBody = document.getElementById("governance-costs-summary-body");
  const eventsBody = document.getElementById("governance-costs-events-body");
  const statusPill = document.getElementById("governance-costs-status");
  const eventsCountPill = document.getElementById("governance-costs-events-count");
  const data = state.governanceCostsData;

  if (!data || !data.costs) {
    if (summaryBody) summaryBody.innerHTML = "<p class='muted'>暂无成本数据</p>";
    if (eventsBody) eventsBody.innerHTML = "<p class='muted'>暂无成本事件</p>";
    if (statusPill) statusPill.textContent = "-";
    if (eventsCountPill) eventsCountPill.textContent = "0";
    return;
  }

  const summary = data.costs.summary || {};
  const events = data.costs.events || [];
  const totalInputTokens = events.reduce((sum, evt) => sum + (Number(evt.input_tokens) || 0), 0);
  const totalOutputTokens = events.reduce((sum, evt) => sum + (Number(evt.output_tokens) || 0), 0);
  const totalTokens = totalInputTokens + totalOutputTokens;
  const totalUsd = events.reduce((sum, evt) => sum + (Number(evt.estimated_usd) || 0), 0);
  const providerModelSummary = events.reduce((acc, evt) => {
    const provider = evt.provider || "unknown";
    const model = evt.model || "unknown";
    const key = `${provider} / ${model}`;
    if (!acc[key]) {
      acc[key] = { count: 0, inputTokens: 0, outputTokens: 0, usd: 0 };
    }
    acc[key].count += 1;
    acc[key].inputTokens += Number(evt.input_tokens) || 0;
    acc[key].outputTokens += Number(evt.output_tokens) || 0;
    acc[key].usd += Number(evt.estimated_usd) || 0;
    return acc;
  }, {});

  if (statusPill) statusPill.textContent = `总计 $${totalUsd.toFixed(4)}`;
  if (eventsCountPill) eventsCountPill.textContent = String(events.length);

  if (summaryBody) {
    summaryBody.innerHTML = `
      <div class="metric-grid small">
        <article class="metric-card">
          <span class="eyebrow">总事件数</span>
          <strong>${summary.total_events || 0}</strong>
        </article>
        <article class="metric-card">
          <span class="eyebrow">总耗时(秒)</span>
          <strong>${summary.total_wall_seconds || 0}</strong>
        </article>
        <article class="metric-card">
          <span class="eyebrow">总 Tokens</span>
          <strong>${totalTokens.toLocaleString()}</strong>
        </article>
        <article class="metric-card">
          <span class="eyebrow">预估成本(USD)</span>
          <strong>$${totalUsd.toFixed(4)}</strong>
        </article>
        <article class="metric-card">
          <span class="eyebrow">成功 / 失败</span>
          <strong>${summary.status_counts?.succeeded || 0} / ${summary.status_counts?.failed || 0}</strong>
        </article>
      </div>
      ${Object.entries(summary.capability_counts || {}).length ? `
        <div style="margin-top: 12px;">
          <h5>能力使用次数</h5>
          ${Object.entries(summary.capability_counts).map(([cap, count]) => `
            <div class="governance-row">
              <div class="governance-row-main">
                <span>${escapeHtml(cap)}</span>
              </div>
              <div class="governance-row-meta">
                <span class="pill">${count}</span>
              </div>
            </div>
          `).join("")}
        </div>
      ` : ""}
      ${Object.entries(providerModelSummary).length ? `
        <div style="margin-top: 12px;">
          <h5>Provider / Model 汇总</h5>
          ${Object.entries(providerModelSummary).map(([label, item]) => `
            <div class="governance-row">
              <div class="governance-row-main">
                <span>${escapeHtml(label)}</span>
                <span class="muted">${item.inputTokens.toLocaleString()} → ${item.outputTokens.toLocaleString()} tokens</span>
              </div>
              <div class="governance-row-meta">
                <span class="pill">${item.count} 次</span>
                <span class="muted">$${item.usd.toFixed(4)}</span>
              </div>
            </div>
          `).join("")}
        </div>
      ` : ""}
    `;
  }

  if (eventsBody) {
    eventsBody.innerHTML = events.length ? events.slice().reverse().map((evt) => {
      const inputTokens = Number(evt.input_tokens) || 0;
      const outputTokens = Number(evt.output_tokens) || 0;
      const estimatedUsd = Number(evt.estimated_usd) || 0;
      const tokenInfo = inputTokens || outputTokens
        ? `<span class="cost-tokens">${inputTokens.toLocaleString()} → ${outputTokens.toLocaleString()} tokens</span>`
        : "";
      const usdInfo = estimatedUsd
        ? `<span class="cost-usd">$${estimatedUsd.toFixed(4)}</span>`
        : "";
      const providerModel = [evt.provider, evt.model].filter(Boolean).join(" / ");
      return `
        <div class="cost-event">
          <span class="cost-actor">${escapeHtml(evt.actor_id || "unknown")}</span>
          <span class="cost-time">${evt.wall_seconds || 0}s</span>
          ${tokenInfo}
          ${usdInfo}
          ${providerModel ? `<span class="muted">${escapeHtml(providerModel)}</span>` : ""}
          <span class="cost-cap">${escapeHtml(evt.capability_id || "-")} · ${escapeHtml(evt.status || "-")}</span>
        </div>
      `;
    }).join("") : "<p class='muted'>暂无成本事件</p>";
  }
}

// --- Governance Actions ---

async function initGovernanceIdentity() {
  if (!state.selectedProjectId) return;
  state.initializingGovernanceIdentity = true;
  try {
    state.governanceIdentityData = await v2api.governance.identity.init(state.selectedProjectId);
    renderGovernancePanel();
  } catch (error) {
    showV2Error("governance-panel", `初始化身份失败：${error.message}`);
  } finally {
    state.initializingGovernanceIdentity = false;
  }
}

async function initGovernancePermissions() {
  if (!state.selectedProjectId) return;
  state.initializingGovernancePermissions = true;
  try {
    state.governancePermissionsData = await v2api.governance.permissions.init(state.selectedProjectId);
    renderGovernancePanel();
  } catch (error) {
    showV2Error("governance-panel", `初始化权限失败：${error.message}`);
  } finally {
    state.initializingGovernancePermissions = false;
  }
}

async function reindexGovernanceCapabilities() {
  if (!state.selectedProjectId) return;
  state.reindexingCapabilities = true;
  try {
    state.governanceCapabilitiesData = await v2api.governance.capabilities.reindex(state.selectedProjectId);
    renderGovernancePanel();
  } catch (error) {
    showV2Error("governance-panel", `索引能力失败：${error.message}`);
  } finally {
    state.reindexingCapabilities = false;
  }
}

async function activateGovernanceAgent(agentId) {
  if (!state.selectedProjectId) return;
  state.activatingAgentId = agentId;
  try {
    await v2api.governance.identity.activateAgent(state.selectedProjectId, agentId);
    state.governanceIdentityData = await v2api.governance.identity.get(state.selectedProjectId);
    renderGovernancePanel();
  } catch (error) {
    showV2Error("governance-panel", `激活 Agent 失败：${error.message}`);
  } finally {
    state.activatingAgentId = null;
  }
}

async function deactivateGovernanceAgent(agentId) {
  if (!state.selectedProjectId) return;
  state.deactivatingAgentId = agentId;
  try {
    await v2api.governance.identity.deactivateAgent(state.selectedProjectId, agentId);
    state.governanceIdentityData = await v2api.governance.identity.get(state.selectedProjectId);
    renderGovernancePanel();
  } catch (error) {
    showV2Error("governance-panel", `停用 Agent 失败：${error.message}`);
  } finally {
    state.deactivatingAgentId = null;
  }
}

async function runPermissionCheck() {
  const agentSelect = document.getElementById("permission-check-agent");
  const actionSelect = document.getElementById("permission-check-action");
  const resultDiv = document.getElementById("permission-check-result");
  if (!agentSelect || !actionSelect || !resultDiv) return;

  const agentId = agentSelect.value;
  const action = actionSelect.value;

  try {
    const result = await v2api.governance.permissions.check(state.selectedProjectId, { subject_id: agentId, action });
    const isAllowed = result.allowed;
    resultDiv.innerHTML = `
      <div class="permission-check-result-item ${isAllowed ? "is-allowed" : "is-denied"}">
        <strong>${isAllowed ? "✓ 允许" : "✗ 拒绝"}</strong>
        <span class="muted">${escapeHtml(result.reason || "")}</span>
        ${result.policy_id ? `<span class="muted">策略: ${escapeHtml(result.policy_id)}</span>` : ""}
      </div>
    `;
  } catch (error) {
    resultDiv.innerHTML = `<div class="error-banner"><span>检查失败：${escapeHtml(error.message)}</span></div>`;
  }
}

// --- Data Loading ---

async function loadV2Data(viewName) {
  if (!state.selectedProjectId) return;

  const projectId = state.selectedProjectId;

  try {
    switch (viewName) {
      case "journey":
        state.overviewData = await v2api.overview.get(projectId);
        state.journeyData = await v2api.journey.get(projectId);
        state.researchQuestionData = await v2api.researchQuestion.get(projectId);
        state.supervisorPlanData = await v2api.supervisorPlan.get(projectId);
        state.agentTaskQueueData = await v2api.agentTaskQueue.get(projectId);
        renderJourney();
        renderJourneyBar();
        break;
      case "data-variables":
        state.overviewData = await v2api.overview.get(projectId);
        state.datasetsData = await v2api.datasets.list(projectId);
        state.variableRolesData = await v2api.variableRoles.get(projectId);
        state.variableRoleCandidatesData = await v2api.variableRoleCandidates.list(projectId);
        renderDataVariables();
        break;
      case "research-design":
        state.overviewData = await v2api.overview.get(projectId);
        state.designData = await v2api.design.get(projectId);
        state.designSpecData = await v2api.designSpec.get(projectId);
        try {
          state.runPlanData = await v2api.runPlan.get(projectId);
        } catch (error) {
          state.runPlanData = null;
        }
        try {
          state.methodWorkflowsData = await v2api.methodWorkflows.get(projectId);
        } catch (error) {
          state.methodWorkflowsData = null;
        }
        renderResearchDesign();
        break;
      case "paper-draft":
        state.draftsData = await v2api.drafts.list(projectId);
        try {
          state.resultsDraftData = await v2api.resultsDraft.get(projectId);
          state.manuscriptCandidatesData = await v2api.manuscriptCandidates.get(projectId);
        } catch (error) {
          state.resultsDraftData = {
            empty_state: {
              title: "尚未形成完整执行结果",
              description: "结果与草稿需要先完成一次成功的完整实证执行。",
            },
          };
          state.manuscriptCandidatesData = {
            items: [],
            empty_state: {
              code: "approved_finding_required",
              title: "尚无正文候选",
              description: "需要先完成完整执行，并审阅通过至少一个结果论断卡。",
            },
          };
        }
        renderPaperDraft();
        break;
      case "artifacts-replication":
        try {
          state.reviewerScorecardData = await v2api.reviewerScorecard.get(projectId);
        } catch (error) {
          state.reviewerScorecardData = {
            empty_state: {
              title: "尚未形成审稿评分",
              description: "需要先完成一次成功的完整实证执行，再生成审稿评分卡。",
            },
            dimensions: [],
          };
        }
        try {
          state.verifierChecksData = await v2api.verifierChecks.get(projectId);
        } catch (error) {
          state.verifierChecksData = {
            empty_state: {
              title: "尚未运行验证闸门",
              description: "需要先生成 preview_ready 导出包；验证闸门不会自动覆盖草稿或导出 docx。",
            },
            checks: [],
            can_export_docx: false,
          };
        }
        state.exportPackageData = await v2api.exportPackage.get(projectId);
        renderArtifactsReplication();
        break;
      case "agent-console":
        state.agentsData = await v2api.agents.list();
        renderAgentConsole();
        break;
      case "governance-panel":
        await loadGovernanceData(projectId);
        renderGovernancePanel();
        break;
      case "empirical-execution":
        state.overviewData = await v2api.overview.get(projectId);
        try {
          state.runPlanData = await v2api.runPlan.get(projectId);
        } catch (error) {
          state.runPlanData = null;
        }
        try {
          state.methodWorkflowsData = await v2api.methodWorkflows.get(projectId);
        } catch (error) {
          state.methodWorkflowsData = null;
        }
        renderExecutionPreflight();
        renderMethodWorkflows();
        renderRunPlanEditor();
        await loadObservableExecution();
        break;
    }
  } catch (error) {
    console.error(`Failed to load ${viewName}:`, error);
    const viewIdMap = {
      "data-variables": "data",
      "research-design": "design",
      "paper-draft": "draft",
      "artifacts-replication": "artifacts-replication",
      "agent-console": "agent-console",
      "governance-panel": "governance-panel",
      "empirical-execution": "empirical-execution",
    };
    const viewId = viewIdMap[viewName] || viewName;
    showV2Error(viewId, `加载失败：${error.message}`);
  }
}

// ============================================================
// Agent Cluster
// ============================================================
async function boot() {
  mountNav();
  mountArchiveInspector();
  mountProjectSelection();
  setupAgentDrawerInteractions();
  document.body.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.matches("[data-close-agent-output]")) {
      state.agentOutput.visible = false;
      renderAgentOutputPanel();
      return;
    }
    const journeyButton = target.closest("[data-journey-action]");
    if (!journeyButton) return;
    switch (journeyButton.dataset.journeyAction) {
      case "view-output":
        state.agentOutput.visible = true;
        renderAgentOutputPanel();
        break;
      case "refresh":
        void loadV2Data("journey");
        break;
      case "checkpoint":
        void pollCheckpoint();
        break;
      case "start-run":
        void createFullRunFromPlan();
        break;
      case "primary": {
        const primaryAction = state.journeyPrimaryAction;
        if (primaryAction?.action?.includes("run") || primaryAction?.action?.includes("执行")) {
          void createFullRunFromPlan();
        } else {
          void loadV2Data("journey");
        }
        break;
      }
    }
  });
  document.getElementById("run-selector")?.addEventListener("change", (event) => {
    state.selectedRunId = event.target.value || null;
    void loadRunObservability(state.selectedProjectId, state.selectedRunId);
  });
  document.getElementById("run-refresh-button")?.addEventListener("click", () => void loadObservableExecution());
  document.getElementById("observable-run-full-button")?.addEventListener("click", () => void createFullRunFromPlan());
  document.getElementById("observable-run-dry-button")?.addEventListener("click", () => void createObservableRun("dry-run"));
  document.getElementById("observable-hitl-gates")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const button = target.closest("[data-gate-resolve-action]");
    if (!button) return;
    void resolveObservableGate(button.dataset.gateId, button.dataset.gateResolveAction);
  });
  document.getElementById("results-findings-list")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const button = target.closest("[data-finding-review-action]");
    if (!button) return;
    void reviewFinding(button.dataset.findingId, button.dataset.findingReviewAction);
  });
  document.getElementById("manuscript-candidates-list")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const reviewButton = target.closest("[data-candidate-review-action]");
    if (reviewButton) {
      void reviewManuscriptCandidate(reviewButton.dataset.candidateId, reviewButton.dataset.candidateReviewAction);
      return;
    }
    const promoteButton = target.closest("[data-candidate-promote-action]");
    if (promoteButton) {
      void promoteManuscriptCandidate(promoteButton.dataset.candidateId);
      return;
    }
    const exportButton = target.closest("[data-candidate-export-preflight-action]");
    if (exportButton) {
      void exportPreflightManuscriptCandidate(exportButton.dataset.candidateId);
    }
  });
  document.getElementById("export-package-workbench")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const writebackButton = target.closest("[data-writeback-approval-action]");
    if (writebackButton) {
      void requestWritebackApproval(writebackButton.dataset.candidateId, writebackButton.dataset.writebackApprovalAction);
      return;
    }
    const docxButton = target.closest("[data-docx-preflight-action]");
    if (docxButton) {
      void runDocxExportPreflight(docxButton.dataset.candidateId);
      return;
    }
    const sourceButton = target.closest("[data-open-results-draft]");
    if (!sourceButton) return;
    document.querySelector('.nav-link[data-view="paper-draft"]')?.click();
  });
  document.getElementById("reviewer-scorecard-body")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const generateButton = target.closest("[data-generate-reviewer-scorecard]");
    if (generateButton) {
      void generateReviewerScorecard();
      return;
    }
    const suggestionButton = target.closest("[data-accept-reviewer-task-suggestion]");
    if (!suggestionButton) return;
    acceptReviewerTaskSuggestion(suggestionButton.dataset.acceptReviewerTaskSuggestion || "");
  });
  document.getElementById("verifier-gate-body")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const runButton = target.closest("[data-run-verifier-checks]");
    if (runButton) {
      void runVerifierChecks();
      return;
    }
    const finalExportButton = target.closest("[data-docx-final-export]");
    if (!finalExportButton) return;
    showV2Error("artifacts-replication", "docx 最终导出仍需人工触发；当前按钮只在 verifier checks 全部通过后解锁。");
  });
  document.getElementById("datasets-list")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const selectButton = target.closest("[data-select-dataset-quality]");
    if (selectButton) {
      state.selectedDatasetPath = selectButton.dataset.datasetPath || state.selectedDatasetPath;
      renderDataVariables();
      return;
    }
    const button = target.closest("[data-open-design-action]");
    if (!button) return;
    openDesignAction(button.dataset.datasetPath);
  });
  document.getElementById("external-datasets-list")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const button = target.closest("[data-external-bind-preflight-action]");
    if (!button) return;
    void requestExternalBindPreflight(button.dataset.sourcePath || "");
  });
  document.getElementById("external-bind-preflight-panel")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const profileButton = target.closest("[data-external-import-profile-action]");
    if (profileButton) {
      void requestExternalImportProfile(profileButton.dataset.datasetImportId || "");
      return;
    }
    const button = target.closest("[data-external-preflight-apply-action]");
    if (!button) return;
    void requestExternalPreflightApply(button.dataset.preflightId || "", button.dataset.externalPreflightApplyAction || "");
  });
  document.getElementById("variable-role-candidate-panel")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const generateButton = target.closest("[data-variable-role-candidate-generate]");
    if (generateButton) {
      void generateVariableRoleCandidate(generateButton.dataset.datasetImportId || "");
      return;
    }
    const loadEditorButton = target.closest("[data-variable-role-candidate-load-editor]");
    if (loadEditorButton) {
      loadVariableRoleCandidateIntoEditor(loadEditorButton.dataset.candidateId || "");
      return;
    }
    const promoteButton = target.closest("[data-promote-variable-candidate-action]");
    if (promoteButton) {
      void promoteVariableRoleCandidate(promoteButton.dataset.candidateId || "");
      return;
    }
    const reviewButton = target.closest("[data-variable-role-candidate-review-action]");
    if (!reviewButton) return;
    void reviewVariableRoleCandidate(reviewButton.dataset.candidateId || "", reviewButton.dataset.variableRoleCandidateReviewAction || "");
  });
  document.getElementById("view-journey")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.closest("[data-topic-confirm-action]")) {
      void confirmResearchTopic(false);
      return;
    }
    if (target.closest("[data-topic-use-existing-action]")) {
      void confirmResearchTopic(true);
      return;
    }
    if (target.closest("[data-topic-start-action]")) {
      switchView("data-variables");
      return;
    }
    const supervisorButton = target.closest("[data-supervisor-plan-generate]");
    if (supervisorButton) {
      void handleGenerateSupervisorPlan();
      return;
    }
    const supervisorReviewButton = target.closest("[data-supervisor-plan-review-action]");
    if (supervisorReviewButton) {
      void handleReviewSupervisorPlan(supervisorReviewButton.dataset.supervisorPlanReviewAction);
      return;
    }
    if (target.closest("[data-agent-task-create-action]")) {
      void handleCreateAgentTaskQueue();
      return;
    }
    const dispatchReviewButton = target.closest("[data-dispatch-review-action]");
    if (dispatchReviewButton) {
      void handleReviewAgentTaskDispatch(
        dispatchReviewButton.dataset.agentTaskId,
        dispatchReviewButton.dataset.dispatchReviewAction,
      );
      return;
    }
    const referenceSeedReviewButton = target.closest("[data-reference-seed-review-action]");
    if (referenceSeedReviewButton) {
      void handleReferenceSeedPackageReview(
        referenceSeedReviewButton.dataset.agentTaskId,
        referenceSeedReviewButton.dataset.referenceSeedReviewAction,
      );
      return;
    }
    const draftLiteratureReviewButton = target.closest("[data-draft-literature-review-action]");
    if (draftLiteratureReviewButton) {
      void handleDraftLiteratureReview(draftLiteratureReviewButton.dataset.agentTaskId || "");
      return;
    }
    const draftLiteratureReviewReviewButton = target.closest("[data-draft-literature-review-review-action]");
    if (draftLiteratureReviewReviewButton) {
      void handleDraftLiteratureReviewReview(
        draftLiteratureReviewReviewButton.dataset.agentTaskId || "",
        draftLiteratureReviewReviewButton.dataset.draftLiteratureReviewReviewAction || "",
      );
      return;
    }
    const citationEvidenceButton = target.closest("[data-citation-verification-evidence-action]");
    if (citationEvidenceButton) {
      void handleCitationVerificationEvidence(
        citationEvidenceButton.dataset.agentTaskId || "",
        citationEvidenceButton.dataset.citationTaskId || "",
      );
      return;
    }
    const verifiedLiteraturePackageButton = target.closest("[data-verified-literature-package-action]");
    if (verifiedLiteraturePackageButton) {
      void handleVerifiedLiteraturePackage(verifiedLiteraturePackageButton.dataset.agentTaskId || "");
      return;
    }
    const verifiedLiteraturePackageReviewButton = target.closest("[data-verified-literature-package-review-action]");
    if (verifiedLiteraturePackageReviewButton) {
      void handleVerifiedLiteraturePackageReview(
        verifiedLiteraturePackageReviewButton.dataset.agentTaskId || "",
        verifiedLiteraturePackageReviewButton.dataset.verifiedLiteraturePackageReviewAction || "",
      );
      return;
    }
    const manuscriptCitationPlanButton = target.closest("[data-manuscript-citation-plan-action]");
    if (manuscriptCitationPlanButton) {
      void handleManuscriptCitationPlan(manuscriptCitationPlanButton.dataset.agentTaskId || "");
      return;
    }
    const manuscriptCitationPlanReviewButton = target.closest("[data-manuscript-citation-plan-review-action]");
    if (manuscriptCitationPlanReviewButton) {
      void handleManuscriptCitationPlanReview(
        manuscriptCitationPlanReviewButton.dataset.agentTaskId || "",
        manuscriptCitationPlanReviewButton.dataset.manuscriptCitationPlanReviewAction || "",
      );
      return;
    }
    const draftSectionPlanButton = target.closest("[data-draft-section-plan-action]");
    if (draftSectionPlanButton) {
      void handleDraftSectionPlan(draftSectionPlanButton.dataset.agentTaskId || "");
      return;
    }
    const draftSectionPlanReviewButton = target.closest("[data-draft-section-plan-review-action]");
    if (draftSectionPlanReviewButton) {
      void handleDraftSectionPlanReview(
        draftSectionPlanReviewButton.dataset.agentTaskId || "",
        draftSectionPlanReviewButton.dataset.draftSectionPlanReviewAction || "",
      );
      return;
    }
    const draftSectionTasksButton = target.closest("[data-draft-section-tasks-action]");
    if (draftSectionTasksButton) {
      void handleDraftSectionTasks(draftSectionTasksButton.dataset.agentTaskId || "");
      return;
    }
    const draftSectionTasksReviewButton = target.closest("[data-draft-section-tasks-review-action]");
    if (draftSectionTasksReviewButton) {
      void handleDraftSectionTasksReview(
        draftSectionTasksReviewButton.dataset.agentTaskId || "",
        draftSectionTasksReviewButton.dataset.draftSectionTasksReviewAction || "",
      );
      return;
    }
    const sectionDraftsReviewButton = target.closest("[data-section-drafts-review-action]");
    if (sectionDraftsReviewButton) {
      void handleSectionDraftsReview(
        sectionDraftsReviewButton.dataset.agentTaskId || "",
        sectionDraftsReviewButton.dataset.sectionDraftsReviewAction || "",
      );
      return;
    }
    const formalWritebackReviewButton = target.closest("[data-formal-writeback-preflight-review-action]");
    if (formalWritebackReviewButton) {
      void handleFormalWritebackPreflightReview(
        formalWritebackReviewButton.dataset.agentTaskId || "",
        formalWritebackReviewButton.dataset.formalWritebackPreflightReviewAction || "",
      );
      return;
    }
    const formalExportPreflightButton = target.closest("[data-formal-export-preflight-action]");
    if (formalExportPreflightButton) {
      void handleFormalExportPreflight(formalExportPreflightButton.dataset.agentTaskId || "");
      return;
    }
    const pdfCandidateExportButton = target.closest("[data-pdf-candidate-export-action]");
    if (pdfCandidateExportButton) {
      void handlePdfCandidateExport(pdfCandidateExportButton.dataset.agentTaskId || "");
      return;
    }
    const sectionDraftsButton = target.closest("[data-section-drafts-action]");
    if (sectionDraftsButton) {
      void handleSectionDrafts(sectionDraftsButton.dataset.agentTaskId || "");
      return;
    }
    const selectBackendButton = target.closest("[data-select-backend-action]");
    if (selectBackendButton) {
      const taskId = selectBackendButton.dataset.agentTaskId || "";
      const selectEl = document.querySelector(`select[data-backend-select][data-agent-task-id="${CSS.escape(taskId)}"]`);
      const backendId = selectEl?.value || "statspai";
      void handleSelectBackendAndExecute(taskId, backendId);
      return;
    }
    const executeButton = target.closest("[data-execute-action]");
    if (executeButton) {
      void handleExecuteAgentTask(executeButton.dataset.agentTaskId || "");
      return;
    }
    const button = target.closest("[data-open-design-action]");
    if (!button) return;
    openDesignAction(state.selectedDatasetPath || button.dataset.datasetPath || "");
  });
  document.getElementById("variable-role-confirmation-form")?.addEventListener("submit", (event) => {
    void handleSaveVariableRoles(event);
  });
  document.getElementById("design-spec-confirmation-form")?.addEventListener("submit", (event) => {
    void handleSaveDesignSpec(event);
  });
  document.getElementById("run-plan-confirmation-form")?.addEventListener("submit", (event) => {
    void handleSaveRunPlan(event);
  });
  await refreshProjects();
  // Load default V2 view data
  if (state.selectedProjectId) {
    await loadV2Data("journey");
  }
  // Start HITL checkpoint polling after boot
  startCheckpointPolling();
}

// ============================================================
// HITL Checkpoint Polling & Modal
// ============================================================

function startCheckpointPolling() {
  stopCheckpointPolling();
  if (!state.selectedProjectId) return;
  // Poll immediately once, then every 5 seconds
  void pollCheckpoint();
  state.checkpoint.pollIntervalId = window.setInterval(() => {
    void pollCheckpoint();
  }, 5000);
}

function stopCheckpointPolling() {
  if (state.checkpoint.pollIntervalId) {
    clearInterval(state.checkpoint.pollIntervalId);
    state.checkpoint.pollIntervalId = null;
  }
}

async function pollCheckpoint() {
  if (!state.selectedProjectId || state.checkpoint.resolving) return;
  try {
    const result = await v2api.checkpoints.poll(state.selectedProjectId);
    const checkpoint = result?.checkpoint || result?.pending?.[0] || null;
    if (checkpoint) {
      if (!state.checkpoint.pending || state.checkpoint.pending.id !== checkpoint.id) {
        state.checkpoint.pending = checkpoint;
        openCheckpointModal(checkpoint);
      }
    } else {
      if (state.checkpoint.pending) {
        state.checkpoint.pending = null;
        closeCheckpointModal();
      }
    }
  } catch (error) {
    // Silently ignore polling errors to avoid spamming the user
    console.error("Checkpoint poll failed:", error);
  }
}

function openCheckpointModal(checkpoint) {
  const overlay = document.getElementById("checkpoint-modal-overlay");
  const stageEl = document.getElementById("checkpoint-modal-stage");
  const descEl = document.getElementById("checkpoint-modal-description");
  const payloadEl = document.getElementById("checkpoint-modal-payload");
  const feedbackEl = document.getElementById("checkpoint-feedback");

  if (!overlay) return;

  const stageMap = {
    literature_review: "文献综述",
    identification_strategy: "识别策略",
    modeling_results: "建模结果",
    writing: "论文写作",
  };

  if (stageEl) stageEl.textContent = `阶段: ${stageMap[checkpoint.stage] || checkpoint.stage || "未知"}`;
  if (descEl) descEl.textContent = checkpoint.description || "系统已完成当前阶段，请审阅结果并决定下一步。";
  if (payloadEl) {
    payloadEl.textContent = checkpoint.payload ? JSON.stringify(checkpoint.payload, null, 2) : "无附加数据";
  }
  if (feedbackEl) feedbackEl.value = "";

  overlay.style.display = "flex";
  // Trigger reflow for transition
  void overlay.offsetWidth;
  overlay.classList.add("is-visible");
}

function closeCheckpointModal() {
  const overlay = document.getElementById("checkpoint-modal-overlay");
  if (!overlay) return;
  overlay.classList.remove("is-visible");
  // Wait for transition to finish before hiding
  setTimeout(() => {
    if (!overlay.classList.contains("is-visible")) {
      overlay.style.display = "none";
    }
  }, 250);
}

async function resolveCheckpoint(action) {
  const checkpoint = state.checkpoint.pending;
  if (!checkpoint || !state.selectedProjectId) return;

  const feedbackEl = document.getElementById("checkpoint-feedback");
  const feedback = feedbackEl?.value?.trim() || "";

  if (action === "modify" && !feedback) {
    alert("请填写修改意见后再选择\"修改后继续\"。");
    return;
  }

  state.checkpoint.resolving = true;
  try {
    await v2api.checkpoints.resolve(state.selectedProjectId, checkpoint.id, action, feedback);
    state.checkpoint.pending = null;
    closeCheckpointModal();
  } catch (error) {
    console.error("Checkpoint resolution failed:", error);
    alert(`操作失败: ${error instanceof Error ? error.message : "未知错误"}`);
  } finally {
    state.checkpoint.resolving = false;
  }
}

// Bind checkpoint modal button events
document.getElementById("checkpoint-btn-approve")?.addEventListener("click", () => resolveCheckpoint("approve"));
document.getElementById("checkpoint-btn-modify")?.addEventListener("click", () => resolveCheckpoint("modify"));
document.getElementById("checkpoint-btn-reject")?.addEventListener("click", () => resolveCheckpoint("reject"));

void boot();
