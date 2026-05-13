const state = {
  projects: [],
  selectedProjectId: null,
  selectedProject: null,
  activeRun: null,

  // Agent Cluster state
  workflows: [],
  selectedWorkflowId: null,
  selectedWorkflow: null,
  workflowTasks: [],
  workflowArtifacts: [],
  hoverTaskId: null,
  activeAgentTaskId: null,
  agentDetailPreview: null,
  agentDetailPreviewLoading: false,
  isArtifactDrawerOpen: false,
  isCompletionVisible: false,
  pollIntervalId: null,

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
  datasetsData: null,
  variableRolesData: null,
  designSpecData: null,
  runPlanData: null,
  designData: null,
  draftsData: null,
  resultsDraftData: null,
  manuscriptCandidatesData: null,
  exportPackageData: null,
  agentsData: null,
  selectedAgentId: null,
  agentDetailData: null,
  provenanceData: null,
  projectRuns: [],
  selectedRunId: null,
  runObservability: null,
  runObservabilityLoading: false,
  resolvingGateId: null,
  resolvingGateAction: null,
  selectedDatasetPath: null,
  bindingExternalDatasetPath: null,
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
  overview: {
    title: "工作台首页",
    summary: "研究问题、主链路、关键风险和下一步动作的总索引。",
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

function setExecutionLog(message) {
  document.getElementById("execution-log").textContent = message;
}

function selectedProjectSummary(project) {
  if (!project) {
    return [];
  }
  return [
    `标题：${project.title}`,
    `问题：${project.question ?? "unknown"}`,
    `Project ID：${project.id}`,
    `根目录：${project.project_root ?? project.root}`,
    `当前阶段：${project.paper?.current_stage ?? project.current_stage ?? "unknown"}`,
    `最近运行：${project.paper?.last_run_mode ?? project.last_run_mode ?? "never"}`,
    `数据存在：${project.paper?.dataset_exists ?? project.dataset_exists ?? false}`,
  ];
}

function renderMetrics() {
  const selected = state.selectedProject;
  const orchestration = selected?.latest_orchestration?.manifest;
  const metrics = [
    { label: "项目数", value: state.projects.length },
    { label: "当前项目", value: selected ? selected.slug : "未选择" },
    { label: "草稿状态", value: selected?.artifacts?.markdown ? "已生成" : "未生成" },
    { label: "审阅循环", value: orchestration?.review_loop?.status ?? "未启动" },
  ];

  document.getElementById("metric-grid").innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card">
          <span class="eyebrow">${metric.label}</span>
          <strong>${metric.value}</strong>
        </article>
      `,
    )
    .join("");
}

function renderProjectCards(targetId, clickable = false) {
  const html = state.projects
    .map((project) => {
      const active = project.id === state.selectedProjectId ? " is-selected" : "";
      return `
        <article class="project-card${active}">
          <strong>${project.title}</strong>
          <div class="muted">${project.slug}</div>
          <div class="muted">${project.question ?? ""}</div>
          <div class="muted">阶段：${project.current_stage} · 模式：${project.last_run_mode}</div>
          <div class="muted">数据集是否存在：${yesNo(project.dataset_exists)}</div>
          ${clickable ? `<button class="ghost-button" data-select-project-id="${project.id}">查看项目</button>` : ""}
        </article>
      `;
    })
    .join("");

  document.getElementById(targetId).innerHTML = html || "<p class='muted'>暂无项目</p>";
}

function renderSelectedProject() {
  const project = state.selectedProject;
  document.getElementById("selected-project-pill").textContent = project ? project.slug : "none";
  document.getElementById("status-pill").textContent =
    state.activeRun?.status ?? project?.paper?.last_run_mode ?? "idle";

  if (!project) {
    document.getElementById("selected-project-summary").innerHTML = "<p>尚未选择项目。</p>";
    return;
  }

  document.getElementById("selected-project-summary").innerHTML = selectedProjectSummary(project)
    .map((line) => `<div>${line}</div>`)
    .join("");
}

function buildWorkflowEntries() {
  const orchestration = state.selectedProject?.latest_orchestration?.manifest;
  if (orchestration) {
    return [
      { label: "supervisor", status: orchestration.supervisor?.status ?? "unknown" },
      ...orchestration.primary_agents.map((agent) => ({
        label: agent.name,
        status: agent.status,
      })),
      {
        label: "review_loop",
        status: orchestration.review_loop?.status ?? "unknown",
      },
    ];
  }

  const currentStage =
    state.selectedProject?.paper?.current_stage ?? state.selectedProject?.current_stage ?? "question-definition";
  return fallbackWorkflowSteps.map((step) => ({
    label: step,
    status: step === currentStage ? "current" : "idle",
  }));
}

function renderWorkflow() {
  document.getElementById("workflow-steps").innerHTML = buildWorkflowEntries()
    .map((entry) => `<li><strong>${entry.label}</strong> <span class="muted">${entry.status}</span></li>`)
    .join("");
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

function renderArtifacts() {
  const artifacts = mergedArtifacts(state.selectedProject);
  document.getElementById("artifact-list").innerHTML = artifacts.length
    ? artifacts
        .map(
          (artifact) => `
            <article class="artifact-card">
              <strong>${artifact.kind}</strong>
              <div>${artifact.description}</div>
              <div class="muted">${artifact.path}</div>
              <div class="muted">是否存在：${yesNo(artifact.exists)}</div>
            </article>
          `,
        )
        .join("")
    : "<p class='muted'>当前项目还没有结构化产物。</p>";
}

function renderDrafts() {
  const orchestrationDraft = state.selectedProject?.latest_orchestration?.revised_draft;
  if (orchestrationDraft) {
    document.getElementById("markdown-preview").textContent = orchestrationDraft;
  } else {
    const draft = state.selectedProject?.analysis_result?.draft?.sections;
    document.getElementById("markdown-preview").textContent = draft
      ? Object.entries(draft)
          .map(([section, content]) => `## ${section}\n\n${content}`)
          .join("\n\n")
      : "暂无内容";
  }

  const resultsPayload = {
    result_payload: state.selectedProject?.analysis_result?.result_payload ?? {},
    latest_orchestration_review: state.selectedProject?.latest_orchestration?.review_packet ?? null,
    active_run: state.activeRun ?? null,
  };
  document.getElementById("results-preview").textContent = JSON.stringify(resultsPayload, null, 2);
}

function renderAll() {
  renderMetrics();
  renderProjectCards("dashboard-projects", false);
  renderProjectCards("project-list", true);
  renderSelectedProject();
  renderWorkflow();
  renderArtifacts();
  renderDrafts();
}

async function loadSelectedProject() {
  if (!state.selectedProjectId) {
    state.selectedProject = null;
    renderAll();
    return;
  }
  state.selectedProject = await fetchJson(`/api/v1/projects/${state.selectedProjectId}`);
  renderAll();
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
  await loadSelectedProject();
  // Reload current V2 view data after project switch
  const activeNav = document.querySelector(".nav-link.is-active");
  const viewName = activeNav?.dataset.view;
  if (viewName && isV2View(viewName)) {
    await loadV2Data(viewName);
  }
}

async function pollRun(projectId, runId) {
  while (true) {
    const run = await fetchJson(`/api/v1/projects/${projectId}/runs/${runId}`);
    state.activeRun = run;
    setExecutionLog(JSON.stringify(run, null, 2));
    renderAll();
    if (["succeeded", "failed"].includes(run.status)) {
      break;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}

async function createRun(mode, label) {
  if (!state.selectedProjectId) {
    return;
  }
  setExecutionLog(`${label}...`);
  const run = await fetchJson(`/api/v1/projects/${state.selectedProjectId}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  });
  state.activeRun = run;
  renderAll();
  await pollRun(state.selectedProjectId, run.id);
  await refreshProjects();
}

async function postAction(path, label) {
  if (!state.selectedProjectId) {
    return;
  }
  setExecutionLog(`${label}...`);
  const payload = await fetchJson(path, { method: "POST" });
  state.activeRun = payload.execution ?? payload.orchestration ?? payload;
  setExecutionLog(JSON.stringify(payload, null, 2));
  await refreshProjects();
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
  updateArchiveInspector("overview");
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

function mountActions() {
  document.getElementById("refresh-button").addEventListener("click", () => void refreshProjects());
  document.getElementById("run-dry-button").addEventListener("click", () => void createRun("dry-run", "Running dry"));
  document.getElementById("run-live-button").addEventListener("click", () => void createRun("live", "Running live"));
  document.getElementById("orchestrate-button").addEventListener("click", () =>
    void postAction(`/api/v1/projects/${state.selectedProjectId}/orchestrate?mode=dry-run`, "Running orchestration"),
  );
  document.getElementById("export-button").addEventListener("click", () =>
    void postAction(`/api/v1/projects/${state.selectedProjectId}/export`, "Exporting docx"),
  );
}

function mountForm() {
  document.getElementById("project-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = Object.fromEntries(form.entries());
    const resultNode = document.getElementById("project-form-result");
    resultNode.textContent = "创建中...";
    try {
      const response = await fetchJson("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      resultNode.textContent = `已创建：${response.project.root}`;
      await refreshProjects();
      const created = state.projects.find((project) => project.slug === response.project.slug);
      if (created) {
        await selectProject(created.id);
      }
      event.currentTarget.reset();
    } catch (error) {
      resultNode.textContent = `创建失败：${error.message}`;
    }
  });
}

// ============================================================
// Agent Cluster
// ============================================================

const AGENT_AVATAR_COLORS = [
  "#1e6f62", "#a14a18", "#2c5282", "#744210", "#553c9a",
  "#285e61", "#9c4221", "#276749", "#702459", "#1a365d",
];

const STAGE_ORDER = ["queued", "planning", "researching", "synthesizing", "reviewing", "completed"];

const DEFAULT_RESEARCH_DIMENSIONS = [
  { id: "task_01", agent_name: "墨白", title: "研究背景与政策语境" },
  { id: "task_02", agent_name: "知远", title: "文献综述与研究缺口" },
  { id: "task_03", agent_name: "数澜", title: "数据源与变量可得性" },
  { id: "task_04", agent_name: "量衡", title: "核心变量定义与测度" },
  { id: "task_05", agent_name: "维农", title: "识别策略与内生性处理" },
  { id: "task_06", agent_name: "建模", title: "基准模型与估计方案" },
  { id: "task_07", agent_name: "固盾", title: "稳健性检验设计" },
  { id: "task_08", agent_name: "析微", title: "异质性与机制分析" },
  { id: "task_09", agent_name: "图灵", title: "表格图形与结果呈现" },
  { id: "task_10", agent_name: "文心", title: "论文结构与写作路径" },
];

// === API Client ===

const api = {
  workflows: {
    async create(title, projectId = null) {
      return fetchJson("/api/v1/workflows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, project_id: projectId }),
      });
    },
    async list() {
      return fetchJson("/api/v1/workflows");
    },
    async get(workflowId) {
      return fetchJson(`/api/v1/workflows/${workflowId}`);
    },
    async start(workflowId) {
      return fetchJson(`/api/v1/workflows/${workflowId}/start`, { method: "POST" });
    },
    async cancel(workflowId) {
      return fetchJson(`/api/v1/workflows/${workflowId}/cancel`, { method: "POST" });
    },
    async getTasks(workflowId) {
      return fetchJson(`/api/v1/workflows/${workflowId}/tasks`);
    },
    async getArtifacts(workflowId) {
      return fetchJson(`/api/v1/workflows/${workflowId}/artifacts`);
    },
    async getReport(workflowId) {
      return fetchJson(`/api/v1/workflows/${workflowId}/report`);
    },
  },
  artifacts: {
    async get(artifactId) {
      return fetchJson(`/api/v1/artifacts/${artifactId}`);
    },
    async promote(artifactId, target) {
      return fetchJson(`/api/v1/artifacts/${artifactId}/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target }),
      });
    },
  },
};

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
    async resolveGate(projectId, runId, gateId, action, note) {
      return fetchJson(`/api/v1/projects/${projectId}/runs/${runId}/gates/${gateId}/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, note }),
      });
    },
  },
};

// ============================================================
// Agent Cluster
// ============================================================
function getAvatarColor(index) {
}

function getAvatarInitial(name) {
  return name ? name.charAt(0) : "?";
}

function getStatusLabel(status) {
  const map = {
    queued: "排队中",
    planning: "规划中",
    researching: "研究中",
    synthesizing: "综合中",
    reviewing: "审阅中",
    completed: "已完成",
    failed: "失败",
    cancelled: "已取消",
  };
  return map[status] || status;
}

function getStatusClass(status) {
  return `status-${status}`;
}

// --- Mock Data ---

function createMockWorkflow(title) {
  const workflowId = `wf_${Date.now()}`;
  const tasks = DEFAULT_RESEARCH_DIMENSIONS.map((dim, i) => ({
    id: dim.id,
    workflow_id: workflowId,
    agent_name: dim.agent_name,
    role: `${dim.title}研究员`,
    dimension: dim.title,
    dimension_number: i + 1,
    status: "queued",
    progress: 0,
    summary: "等待启动...",
    research_scope: [
      "相关文献梳理",
      "关键概念界定",
      "研究假设提出",
      "方法论初步评估",
    ],
    outputs: [],
    evidence_gaps: [],
  }));

  return {
    workflow: {
      id: workflowId,
      title: title || "未命名研究",
      status: "queued",
      phase: "queued",
      progress: 0,
      agent_count: tasks.length,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    tasks,
  };
}

function createMockArtifacts(workflowId, tasks) {
  return tasks.map((task) => ({
    id: `artifact_${task.id}`,
    workflow_id: workflowId,
    task_id: task.id,
    kind: "markdown",
    path: `docs/workflows/${workflowId}/${task.id.padStart(2, "0")}_${task.dimension.replace(/\s+/g, "_")}.md`,
    title: task.dimension,
    created_by: task.id,
    status: "draft",
    created_at: new Date().toISOString(),
  }));
}

// Simulate task progress (for UI validation before real API)
function simulateTaskProgress() {
  if (!state.selectedWorkflow) return;

  let allCompleted = true;
  let totalProgress = 0;

  state.workflowTasks = state.workflowTasks.map((task) => {
    if (task.status === "completed" || task.status === "failed") {
      totalProgress += task.progress;
      if (task.status !== "completed") allCompleted = false;
      return task;
    }

    allCompleted = false;
    const stageIndex = STAGE_ORDER.indexOf(task.status);

    // Advance progress
    let newProgress = task.progress + Math.random() * 0.15;
    if (newProgress >= 1) {
      newProgress = 1;
    }

    // Advance stage based on progress thresholds
    let newStatus = task.status;
    if (newProgress >= 0.95 && task.status !== "completed") {
      newStatus = "completed";
      newProgress = 1;
    } else if (newProgress >= 0.75 && stageIndex < 4) {
      newStatus = STAGE_ORDER[Math.min(stageIndex + 1, 4)];
    } else if (newProgress >= 0.5 && stageIndex < 3) {
      newStatus = STAGE_ORDER[Math.min(stageIndex + 1, 3)];
    } else if (newProgress >= 0.25 && stageIndex < 2) {
      newStatus = STAGE_ORDER[Math.min(stageIndex + 1, 2)];
    } else if (newProgress >= 0.05 && stageIndex < 1) {
      newStatus = "planning";
    }

    // Add mock outputs when completed
    const outputs = newStatus === "completed" && task.outputs.length === 0
      ? [`docs/workflows/${state.selectedWorkflow.id}/${String(task.dimension_number).padStart(2, "0")}_${task.dimension.replace(/\s+/g, "_")}.md`]
      : task.outputs;

    totalProgress += newProgress;

    return {
      ...task,
      status: newStatus,
      progress: newProgress,
      outputs,
      summary: newStatus === "completed" ? "研究完成" : `正在${getStatusLabel(newStatus).toLowerCase()}...`,
    };
  });

  // Update workflow aggregate state
  const avgProgress = totalProgress / state.workflowTasks.length;
  state.selectedWorkflow = {
    ...state.selectedWorkflow,
    progress: avgProgress,
    status: allCompleted ? "completed" : "running",
    phase: allCompleted ? "completed" : "parallel_research",
    updated_at: new Date().toISOString(),
  };

  // Show completion card when all done
  if (allCompleted && !state.isCompletionVisible) {
    state.isCompletionVisible = true;
  }

  renderAgentCluster();

  if (allCompleted) {
    clearInterval(state.pollIntervalId);
    state.pollIntervalId = null;
  }
}

// --- Rendering ---

function renderAgentCluster() {
  renderErrorBanner();
  renderLoadingOverlay();
  renderWorkflowHeader();
  renderStageTimeline();
  renderAgentRows();
  renderCompletionCard();
  renderArtifactDrawer();
  renderAgentDetailDrawer();
  renderReportModal();
  updateComposerState();
}

function renderErrorBanner() {
  const banner = document.getElementById("agent-cluster-error");
  if (!banner) return;

  if (state.apiError || state.apiNotice) {
    const isError = Boolean(state.apiError);
    const message = state.apiError || state.apiNotice;
    banner.classList.toggle("is-info", !isError);
    banner.style.display = "block";
    banner.innerHTML = `
      <span>${escapeHtml(message)}</span>
      <button class="ghost-button" id="dismiss-error" style="padding: 4px 10px; font-size: 12px;">关闭</button>
    `;
    banner.querySelector("#dismiss-error")?.addEventListener("click", () => {
      state.apiError = null;
      state.apiNotice = null;
      renderErrorBanner();
    });
  } else {
    banner.classList.remove("is-info");
    banner.style.display = "none";
    banner.innerHTML = "";
  }
}

function renderLoadingOverlay() {
  const composer = document.querySelector(".composer-bar");
  if (!composer) return;

  if (state.isLoading) {
    composer.classList.add("is-loading");
  } else {
    composer.classList.remove("is-loading");
  }
}

function updateComposerState() {
  const input = document.getElementById("research-goal-input");
  const button = document.getElementById("start-workflow-button");
  if (input) input.disabled = state.isLoading;
  if (button) button.disabled = state.isLoading;
}

function renderWorkflowHeader() {
  const workflow = state.selectedWorkflow;
  const titleEl = document.getElementById("workflow-title");
  const subtitleEl = document.getElementById("workflow-subtitle");
  const phaseEl = document.getElementById("workflow-phase");
  const progressEl = document.getElementById("workflow-progress");
  const countEl = document.getElementById("workflow-agent-count");
  const cancelButton = document.getElementById("cancel-workflow-button");

  if (!workflow) {
    titleEl.textContent = "尚未启动研究";
    subtitleEl.textContent = "输入研究问题并点击启动";
    phaseEl.textContent = "-";
    progressEl.textContent = "0%";
    countEl.textContent = "0/10";
    if (cancelButton) cancelButton.style.display = "none";
    return;
  }

  titleEl.textContent = workflow.title;
  subtitleEl.textContent = `创建于 ${new Date(workflow.created_at).toLocaleString("zh-CN")}`;
  phaseEl.textContent = getStatusLabel(workflow.phase);
  progressEl.textContent = `${Math.round(workflow.progress * 100)}%`;

  const completedCount = state.workflowTasks.filter((t) => t.status === "completed").length;
  countEl.textContent = `${completedCount}/${state.workflowTasks.length}`;
  if (cancelButton) {
    const canCancel = workflow.status === "running" || workflow.status === "queued";
    cancelButton.style.display = canCancel ? "inline-flex" : "none";
    cancelButton.disabled = state.isLoading;
  }
}

function renderStageTimeline() {
  const container = document.getElementById("stage-timeline");
  const workflow = state.selectedWorkflow;

  if (!workflow) {
    container.innerHTML = "";
    return;
  }

  const currentStageIndex = STAGE_ORDER.indexOf(workflow.phase);

  const html = STAGE_ORDER.map((stage, index) => {
    const isCompleted = index < currentStageIndex;
    const isCurrent = index === currentStageIndex;
    const label = getStatusLabel(stage);

    const stageHtml = `
      <div class="timeline-stage ${isCompleted ? "is-completed" : ""} ${isCurrent ? "is-current" : ""}">
        <span class="timeline-dot"></span>
        <span>${label}</span>
      </div>
    `;

    if (index < STAGE_ORDER.length - 1) {
      const lineCompleted = index < currentStageIndex;
      return `${stageHtml}<div class="timeline-line ${lineCompleted ? "is-completed" : ""}"></div>`;
    }
    return stageHtml;
  }).join("");

  container.innerHTML = html;
}

function renderAgentRows() {
  const container = document.getElementById("agent-cluster-panel");
  const tasks = state.workflowTasks;

  if (tasks.length === 0) {
    container.innerHTML = `
      <div class="panel" style="text-align: center; padding: 48px;">
        <p class="muted">暂无研究任务。在下方输入研究问题并启动。</p>
      </div>
    `;
    return;
  }

  container.innerHTML = tasks
    .map((task, index) => {
      const color = getAvatarColor(index);
      const initial = getAvatarInitial(task.agent_name);
      const statusClass = getStatusClass(task.status);
      const isCompleted = task.status === "completed";
      const isFailed = task.status === "failed";
      const isActive = task.id === state.activeAgentTaskId;
      const progressPercent = Math.round(task.progress * 100);

      return `
        <div
          class="agent-row ${isCompleted ? "is-completed" : ""} ${isFailed ? "is-failed" : ""} ${isActive ? "is-active" : ""}"
          data-task-id="${task.id}"
          role="button"
          tabindex="0"
          aria-label="打开 ${escapeHtml(task.agent_name)} 的工作详情"
        >
          <div class="agent-avatar" style="background: ${color}">${initial}</div>
          <div class="agent-row-info">
            <div class="agent-row-title">${escapeHtml(task.dimension)}</div>
            <div class="agent-row-name">${escapeHtml(task.agent_name)} · ${escapeHtml(task.summary)}</div>
          </div>
          <div class="agent-row-dimension">#${String(task.dimension_number).padStart(2, "0")}</div>
          <div class="agent-row-progress">
            <div class="agent-progress-bar">
              <div class="agent-progress-fill" style="width: ${progressPercent}%"></div>
            </div>
          </div>
          <div class="agent-row-status">
            <span class="status-pill ${statusClass}">${getStatusLabel(task.status)}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderCompletionCard() {
  const card = document.getElementById("completion-card");
  if (!state.isCompletionVisible || !state.selectedWorkflow) {
    card.style.display = "none";
    return;
  }

  card.style.display = "block";

  const completedCount = state.workflowTasks.filter((t) => t.status === "completed").length;
  const totalArtifacts = state.workflowTasks.reduce((sum, t) => sum + t.outputs.length, 0);

  const statsHtml = `
    <div class="completion-stat">
      <span class="completion-stat-value">${completedCount}</span>
      <span class="completion-stat-label">已完成智能体</span>
    </div>
    <div class="completion-stat">
      <span class="completion-stat-value">${totalArtifacts}</span>
      <span class="completion-stat-label">产出物</span>
    </div>
    <div class="completion-stat">
      <span class="completion-stat-value">${Math.round(state.selectedWorkflow.progress * 100)}%</span>
      <span class="completion-stat-label">总体进度</span>
    </div>
  `;

  document.getElementById("completion-stats").innerHTML = statsHtml;

  const reportButton = document.getElementById("view-report-button");
  const promoteButton = document.getElementById("promote-artifacts-button");
  if (reportButton) reportButton.disabled = state.isLoading;
  if (promoteButton) {
    promoteButton.disabled = state.isPromoting;
    promoteButton.textContent = state.isPromoting ? "导出中..." : "导出到项目";
  }

  if (promoteButton && !document.getElementById("promote-target-select")) {
    promoteButton.insertAdjacentHTML(
      "beforebegin",
      `
        <select id="promote-target-select" class="promote-target-select">
          <option value="manuscripts">论文稿件</option>
          <option value="results">结果目录</option>
          <option value="submissions">投稿材料</option>
        </select>
      `,
    );
  }
}

function renderAgentHoverCard(task) {
  const card = document.getElementById("agent-hover-card");
  const content = document.getElementById("agent-hover-card-content");

  if (!task) {
    card.classList.remove("is-visible");
    return;
  }

  const index = state.workflowTasks.findIndex((t) => t.id === task.id);
  const color = getAvatarColor(index);
  const initial = getAvatarInitial(task.agent_name);
  const progressPercent = Math.round(task.progress * 100);

  const scopeList = (task.research_scope || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  const outputsList = task.outputs.length
    ? task.outputs
        .map((path) => `<a class="hover-card-output-link" data-path="${escapeHtml(path)}">${escapeHtml(path.split("/").pop())}</a>`)
        .join("<br>")
    : "暂无产出";

  content.innerHTML = `
    <div class="hover-card-header">
      <div class="agent-avatar" style="background: ${color}">${initial}</div>
      <div>
        <p class="hover-card-title">${escapeHtml(task.agent_name)} · ${escapeHtml(task.role || task.dimension)}</p>
        <p class="hover-card-subtitle">${escapeHtml(task.dimension)}</p>
      </div>
    </div>
    <div class="hover-card-section">
      <h4>研究范围</h4>
      <ul class="hover-card-list">${scopeList}</ul>
    </div>
    <div class="hover-card-section">
      <h4>当前状态</h4>
      <div class="hover-card-meta">
        <span>${getStatusLabel(task.status)} (${progressPercent}%)</span>
      </div>
    </div>
    <div class="hover-card-section">
      <h4>已产出</h4>
      <div class="hover-card-outputs">${outputsList}</div>
    </div>
    ${task.evidence_gaps?.length ? `
      <div class="hover-card-section">
        <h4>证据缺口</h4>
        <ul class="hover-card-list">${task.evidence_gaps.map((g) => `<li>${escapeHtml(g)}</li>`).join("")}</ul>
      </div>
    ` : ""}
  `;

  card.classList.add("is-visible");
}

function renderArtifactDrawer() {
  const drawer = document.getElementById("artifact-drawer");
  const content = document.getElementById("artifact-drawer-content");

  if (state.isArtifactDrawerOpen) {
    drawer.classList.add("is-open");
  } else {
    drawer.classList.remove("is-open");
    return;
  }

  // Group artifacts by task
  const tasks = state.workflowTasks;
  if (tasks.length === 0) {
    content.innerHTML = "<p class=\"muted\">暂无产物</p>";
    return;
  }

  const html = tasks
    .filter((task) => task.outputs.length > 0)
    .map((task) => {
      const outputsHtml = task.outputs
        .map((path) => `
          <div class="artifact-item" data-path="${escapeHtml(path)}">
            <span class="artifact-icon">📄</span>
            <span class="artifact-name">${escapeHtml(path.split("/").pop())}</span>
          </div>
        `)
        .join("");

      return `
        <div class="artifact-group">
          <div class="artifact-group-title">${escapeHtml(task.agent_name)} · ${escapeHtml(task.dimension)}</div>
          ${outputsHtml}
        </div>
      `;
    })
    .join("");

  content.innerHTML = html || "<p class=\"muted\">暂无产物</p>";
}

function getAgentGovernance(task) {
  const provider = state.selectedWorkflow?.execution_provider || "local_codex";
  const outputCount = task.outputs?.length || 0;
  const progressPercent = Math.round((task.progress || 0) * 100);
  const permissionStatus = task.status === "completed"
    ? "仅可提交草稿产物；导出到正式项目仍需人工确认"
    : "可读取项目上下文；未授予正式产物导出权限";

  return {
    costs: [
      `执行提供方：${provider}`,
      `当前进度：${progressPercent}%`,
      `产物数量：${outputCount}`,
    ],
    permissions: [
      "读取当前 workflow 与项目上下文",
      "写入 docs/workflows 下的研究草稿",
      permissionStatus,
    ],
    capabilities: [
      task.role || "研究执行",
      "结构化研究范围拆解",
      "Markdown 研究产物生成",
    ],
  };
}

function renderAgentDetailDrawer() {
  const drawer = document.getElementById("agent-detail-drawer");
  const content = document.getElementById("agent-detail-drawer-content");
  if (!drawer || !content) return;

  const task = state.workflowTasks.find((item) => item.id === state.activeAgentTaskId);
  if (!task) {
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    content.innerHTML = "";
    return;
  }

  drawer.classList.add("is-open");
  drawer.setAttribute("aria-hidden", "false");

  // Update prev/next navigation button states
  const currentIndex = state.workflowTasks.findIndex((item) => item.id === task.id);
  const prevButton = document.getElementById("prev-agent-button");
  const nextButton = document.getElementById("next-agent-button");
  if (prevButton) prevButton.disabled = currentIndex <= 0;
  if (nextButton) nextButton.disabled = currentIndex < 0 || currentIndex >= state.workflowTasks.length - 1;

  const index = currentIndex;
  const color = getAvatarColor(index);
  const initial = getAvatarInitial(task.agent_name);
  const progressPercent = Math.round((task.progress || 0) * 100);
  const governance = getAgentGovernance(task);
  const scopeList = (task.research_scope || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const evidenceGaps = (task.evidence_gaps || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const outputsHtml = task.outputs?.length
    ? task.outputs.map((path) => `
        <button class="agent-detail-output" data-path="${escapeHtml(path)}">
          <span class="artifact-icon">📄</span>
          <span>${escapeHtml(path.split("/").pop())}</span>
        </button>
      `).join("")
    : "<p class=\"muted\">暂无最终产物</p>";

  content.innerHTML = `
    <div class="agent-detail-identity">
      <div class="agent-avatar" style="background: ${color}">${initial}</div>
      <div>
        <p class="agent-detail-name">${escapeHtml(task.agent_name)} · ${escapeHtml(task.role || task.dimension)}</p>
        <p class="muted">${escapeHtml(task.dimension)} · #${String(task.dimension_number).padStart(2, "0")}</p>
      </div>
    </div>

    <section class="agent-detail-section">
      <h4>当前工作</h4>
      <div class="agent-detail-status">
        <span class="status-pill ${getStatusClass(task.status)}">${getStatusLabel(task.status)}</span>
        <span>${progressPercent}%</span>
      </div>
      <div class="agent-progress-bar">
        <div class="agent-progress-fill" style="width: ${progressPercent}%"></div>
      </div>
      <p>${escapeHtml(task.summary || "等待研究状态更新。")}</p>
    </section>

    <section class="agent-detail-section">
      <h4>研究范围</h4>
      <ul class="agent-detail-list">${scopeList || "<li>暂无研究范围</li>"}</ul>
    </section>

    <section class="agent-detail-grid">
      <div class="agent-detail-section">
        <h4>成本追踪</h4>
        <ul class="agent-detail-list">${governance.costs.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </div>
      <div class="agent-detail-section">
        <h4>权限</h4>
        <ul class="agent-detail-list">${governance.permissions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </div>
      <div class="agent-detail-section">
        <h4>能力注册</h4>
        <ul class="agent-detail-list">${governance.capabilities.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </div>
    </section>

    ${evidenceGaps ? `
      <section class="agent-detail-section">
        <h4>证据缺口</h4>
        <ul class="agent-detail-list">${evidenceGaps}</ul>
      </section>
    ` : ""}

    <section class="agent-detail-section">
      <h4>产物</h4>
      <div class="agent-detail-outputs">${outputsHtml}</div>
    </section>

    <section class="agent-detail-section agent-detail-artifact-preview">
      <h4>产物预览</h4>
      ${task.outputs?.length ? renderAgentArtifactPreview() : '<p class="muted">暂无产物。等待研究完成后自动生成。</p>'}
    </section>
  `;
}

function renderAgentArtifactPreview() {
  if (state.agentDetailPreviewLoading) {
    return '<p class="muted">正在读取产物正文...</p>';
  }

  if (state.apiError) {
    return `<p class="muted">无法读取产物正文：${escapeHtml(state.apiError)}</p>`;
  }

  if (!state.agentDetailPreview) {
    return '<p class="muted">点击上方产物后在这里预览正文。</p>';
  }

  return `
    <p class="muted">${escapeHtml(state.agentDetailPreview.path || "本地预览")}</p>
    <pre class="agent-detail-preview-body">${escapeHtml(state.agentDetailPreview.content || "暂无正文")}</pre>
  `;
}

function renderReportModal() {
  const modal = document.getElementById("report-modal");
  const title = document.getElementById("report-modal-title");
  const path = document.getElementById("report-modal-path");
  const body = document.getElementById("report-modal-body");
  if (!modal || !title || !path || !body) return;

  if (!state.isReportModalOpen || !state.activeReport) {
    modal.style.display = "none";
    return;
  }

  modal.style.display = "flex";
  title.textContent = "最终研究报告";
  path.textContent = state.activeReport.path || "local preview";
  body.textContent = state.activeReport.content || "";
}

function positionHoverCard(element) {
  const card = document.getElementById("agent-hover-card");
  const rect = element.getBoundingClientRect();
  const cardRect = card.getBoundingClientRect();

  let left = rect.left;
  let top = rect.bottom + 8;

  // Prevent overflow right
  if (left + cardRect.width > window.innerWidth - 16) {
    left = window.innerWidth - cardRect.width - 16;
  }

  // Prevent overflow bottom - show above instead
  if (top + cardRect.height > window.innerHeight - 16) {
    top = rect.top - cardRect.height - 8;
  }

  card.style.left = `${left}px`;
  card.style.top = `${top}px`;
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function buildMockReport() {
  const taskLines = state.workflowTasks
    .map(
      (task) =>
        `- ${String(task.dimension_number).padStart(2, "0")}. ${task.agent_name}: ${task.dimension} - ${task.status}`,
    )
    .join("\n");

  return {
    path: `mock://${state.selectedWorkflow?.id || "workflow"}/final_research_report.md`,
    content: `# ${state.selectedWorkflow?.title || "Mock Workflow"}\n\n当前处于 Mock 模式，报告仅用于前端演示，不代表真实研究证据。\n\n## 任务矩阵\n${taskLines}\n`,
  };
}

// --- Event Binding ---

function mountAgentClusterEvents() {
  // Hover card
  const panel = document.getElementById("agent-cluster-panel");
  let hoverTimeout = null;
  let leaveTimeout = null;

  panel.addEventListener("mouseenter", (event) => {
    const row = event.target.closest(".agent-row");
    if (!row) return;

    clearTimeout(leaveTimeout);
    hoverTimeout = setTimeout(() => {
      const taskId = row.dataset.taskId;
      const task = state.workflowTasks.find((t) => t.id === taskId);
      if (task) {
        state.hoverTaskId = taskId;
        renderAgentHoverCard(task);
        positionHoverCard(row);
      }
    }, 200);
  }, true);

  panel.addEventListener("mouseleave", (event) => {
    const row = event.target.closest(".agent-row");
    if (!row) return;

    clearTimeout(hoverTimeout);
    leaveTimeout = setTimeout(() => {
      state.hoverTaskId = null;
      renderAgentHoverCard(null);
    }, 300);
  }, true);

  panel.addEventListener("click", (event) => {
    const row = event.target.closest(".agent-row");
    if (!row) return;
    openAgentDetail(row.dataset.taskId);
  });

  panel.addEventListener("keydown", (event) => {
    const row = event.target.closest(".agent-row");
    if (!row || (event.key !== "Enter" && event.key !== " ")) return;
    event.preventDefault();
    openAgentDetail(row.dataset.taskId);
  });

  // Artifact drawer toggle
  document.getElementById("toggle-artifact-drawer")?.addEventListener("click", () => {
    state.isArtifactDrawerOpen = !state.isArtifactDrawerOpen;
    renderArtifactDrawer();
  });

  document.getElementById("close-artifact-drawer")?.addEventListener("click", () => {
    state.isArtifactDrawerOpen = false;
    renderArtifactDrawer();
  });

  document.getElementById("artifact-drawer-content")?.addEventListener("click", (event) => {
    const item = event.target.closest(".artifact-item");
    if (!item) return;
    void openArtifactPreview(item.dataset.path);
  });

  document.getElementById("close-agent-detail-drawer")?.addEventListener("click", () => {
    closeAgentDetail();
  });

  document.getElementById("prev-agent-button")?.addEventListener("click", () => {
    navigateToPrevAgent();
  });

  document.getElementById("next-agent-button")?.addEventListener("click", () => {
    navigateToNextAgent();
  });

  document.getElementById("agent-detail-drawer-content")?.addEventListener("click", (event) => {
    const output = event.target.closest(".agent-detail-output");
    if (!output) return;
    void openAgentArtifactPreview(output.dataset.path);
  });

  // Start workflow
  document.getElementById("start-workflow-button")?.addEventListener("click", () => {
    const input = document.getElementById("research-goal-input");
    const goal = input.value.trim();
    if (!goal) return;

    void startWorkflow(goal);
    input.value = "";
  });

  document.getElementById("cancel-workflow-button")?.addEventListener("click", () => {
    void cancelActiveWorkflow();
  });

  // Toggle mock mode (dev helper: Ctrl+M)
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "m") {
      e.preventDefault();
      state.useMock = !state.useMock;
      console.log(`[Dev] Mock mode: ${state.useMock ? "ON" : "OFF"}`);
    } else if (e.key === "Escape" && state.activeAgentTaskId) {
      closeAgentDetail();
    }
  });

  // Completion card actions
  document.getElementById("dismiss-completion-button")?.addEventListener("click", () => {
    state.isCompletionVisible = false;
    renderCompletionCard();
  });

  document.getElementById("view-report-button")?.addEventListener("click", () => {
    void openWorkflowReport();
  });

  document.getElementById("promote-artifacts-button")?.addEventListener("click", () => {
    void promoteWorkflowArtifacts();
  });

  document.getElementById("close-report-modal")?.addEventListener("click", () => {
    state.isReportModalOpen = false;
    renderReportModal();
  });

  document.getElementById("report-modal")?.addEventListener("click", (event) => {
    if (event.target.id === "report-modal") {
      state.isReportModalOpen = false;
      renderReportModal();
    }
  });

  // Close drawer on backdrop click
  document.getElementById("artifact-drawer")?.addEventListener("click", (event) => {
    if (event.target.id === "artifact-drawer") {
      state.isArtifactDrawerOpen = false;
      renderArtifactDrawer();
    }
  });
}

// --- Workflow Operations ---

function openAgentDetail(taskId) {
  if (!taskId) return;
  const task = state.workflowTasks.find((item) => item.id === taskId);
  if (!task) return;

  state.activeAgentTaskId = taskId;
  state.agentDetailPreview = null;
  state.agentDetailPreviewLoading = false;
  state.apiError = null;
  state.apiNotice = null;
  renderAgentDetailDrawer();
  renderAgentRows();
}

function closeAgentDetail() {
  state.activeAgentTaskId = null;
  state.agentDetailPreview = null;
  state.agentDetailPreviewLoading = false;
  state.apiError = null;
  state.apiNotice = null;
  renderAgentDetailDrawer();
  renderAgentRows();
}

function navigateToPrevAgent() {
  if (!state.activeAgentTaskId) return;
  const tasks = state.workflowTasks;
  const currentIndex = tasks.findIndex((t) => t.id === state.activeAgentTaskId);
  if (currentIndex > 0) {
    openAgentDetail(tasks[currentIndex - 1].id);
  }
}

function navigateToNextAgent() {
  if (!state.activeAgentTaskId) return;
  const tasks = state.workflowTasks;
  const currentIndex = tasks.findIndex((t) => t.id === state.activeAgentTaskId);
  if (currentIndex >= 0 && currentIndex < tasks.length - 1) {
    openAgentDetail(tasks[currentIndex + 1].id);
  }
}

async function openAgentArtifactPreview(path) {
  if (!path || !state.activeAgentTaskId) return;

  const artifact = state.workflowArtifacts.find((item) => item.path === path);
  state.agentDetailPreviewLoading = true;
  state.agentDetailPreview = null;
  state.apiError = null;
  state.apiNotice = null;
  renderAgentDetailDrawer();

  try {
    if (state.useMock || !artifact?.id) {
      state.agentDetailPreview = {
        path,
        content: `# ${path.split("/").pop()}\n\n当前为 Mock 模式产物预览。真实内容需要通过 Real API 的 artifact endpoint 读取。`,
      };
    } else {
      const response = await api.artifacts.get(artifact.id);
      state.agentDetailPreview = {
        path: response.artifact.path,
        content: response.content || "后端未返回该产物正文。",
      };
    }
  } catch (error) {
    state.apiError = error.message;
  } finally {
    state.agentDetailPreviewLoading = false;
    renderAgentCluster();
  }
}

async function openWorkflowReport() {
  if (!state.selectedWorkflow) {
    state.apiError = "请先启动或选择一个工作流。";
    renderAgentCluster();
    return;
  }

  state.isLoading = true;
  state.apiError = null;
  state.apiNotice = null;
  renderAgentCluster();

  try {
    const report = state.useMock
      ? buildMockReport()
      : await api.workflows.getReport(state.selectedWorkflow.id);
    state.activeReport = report;
    state.isReportModalOpen = true;
  } catch (error) {
    state.apiError = error.message;
  } finally {
    state.isLoading = false;
    renderAgentCluster();
  }
}

async function openArtifactPreview(path) {
  if (!path) return;

  const artifact = state.workflowArtifacts.find((item) => item.path === path);
  state.isLoading = true;
  state.apiError = null;
  state.apiNotice = null;
  renderAgentCluster();

  try {
    if (state.useMock || !artifact?.id) {
      state.activeReport = {
        path,
        content: `# ${path.split("/").pop()}\n\n当前为 Mock 模式产物预览。真实内容需要通过 Real API 的 artifact endpoint 读取。`,
      };
    } else {
      const response = await api.artifacts.get(artifact.id);
      state.activeReport = {
        path: response.artifact.path,
        content: response.content || "后端未返回该产物正文。",
      };
    }
    state.isReportModalOpen = true;
  } catch (error) {
    state.apiError = error.message;
  } finally {
    state.isLoading = false;
    renderAgentCluster();
  }
}

async function cancelActiveWorkflow() {
  if (!state.selectedWorkflow) return;

  state.isLoading = true;
  state.apiError = null;
  state.apiNotice = null;
  renderAgentCluster();

  try {
    if (state.pollIntervalId) {
      clearInterval(state.pollIntervalId);
      state.pollIntervalId = null;
    }

    if (state.useMock) {
      state.selectedWorkflow = {
        ...state.selectedWorkflow,
        status: "cancelled",
        phase: "cancelled",
        updated_at: new Date().toISOString(),
      };
      state.workflowTasks = state.workflowTasks.map((task) =>
        task.status === "completed" ? task : { ...task, status: "cancelled" },
      );
    } else {
      const response = await api.workflows.cancel(state.selectedWorkflow.id);
      state.selectedWorkflow = response.workflow;
      const bundle = await api.workflows.get(state.selectedWorkflow.id);
      state.workflowTasks = bundle.tasks || state.workflowTasks;
      state.workflowArtifacts = bundle.artifacts || state.workflowArtifacts;
    }

    state.isCompletionVisible = false;
    state.apiNotice = "工作流已取消。";
  } catch (error) {
    state.apiError = error.message;
  } finally {
    state.isLoading = false;
    renderAgentCluster();
  }
}

async function promoteWorkflowArtifacts() {
  if (!state.selectedWorkflow) {
    state.apiError = "请先完成一个工作流，再导出产物。";
    renderAgentCluster();
    return;
  }

  if (state.useMock) {
    state.apiError = "Mock 模式下不能导出到项目；请切换到 Real API 后使用后端产物。";
    renderAgentCluster();
    return;
  }

  const artifacts = state.workflowArtifacts.filter((artifact) => artifact.id);
  if (artifacts.length === 0) {
    state.apiError = "当前工作流还没有可导出的后端产物。";
    renderAgentCluster();
    return;
  }

  const target = document.getElementById("promote-target-select")?.value || "manuscripts";
  state.isPromoting = true;
  state.apiError = null;
  state.apiNotice = null;
  renderAgentCluster();

  try {
    const results = await Promise.allSettled(
      artifacts.map((artifact) => api.artifacts.promote(artifact.id, target)),
    );
    const rejected = results.filter((result) => result.status === "rejected");
    if (rejected.length > 0) {
      throw new Error(
        `${rejected.length}/${artifacts.length} 个产物未导出：${rejected[0].reason.message}`,
      );
    }

    state.workflowArtifacts = results.map((result) => result.value.artifact);
    state.apiNotice = `已导出 ${artifacts.length} 个产物到 ${target}。`;
  } catch (error) {
    state.apiError = error.message;
  } finally {
    state.isPromoting = false;
    renderAgentCluster();
  }
}

async function startWorkflow(title) {
  state.isLoading = true;
  state.apiError = null;
  state.apiNotice = null;
  renderAgentCluster();

  try {
    let workflow, tasks, artifacts;

    if (state.useMock) {
      const mock = createMockWorkflow(title);
      workflow = mock.workflow;
      tasks = mock.tasks;
      artifacts = createMockArtifacts(workflow.id, tasks);
    } else {
      const response = await api.workflows.create(title, state.selectedProjectId);
      workflow = response.workflow;
      tasks = response.tasks;
      artifacts = response.artifacts || [];
      await api.workflows.start(workflow.id);
    }

    state.workflows.push(workflow);
    state.selectedWorkflowId = workflow.id;
    state.selectedWorkflow = workflow;
    state.workflowTasks = tasks;
    state.workflowArtifacts = artifacts;
    state.isCompletionVisible = false;

    // Start polling
    if (state.pollIntervalId) {
      clearInterval(state.pollIntervalId);
    }

    if (state.useMock) {
      state.pollIntervalId = setInterval(simulateTaskProgress, 2500);
    } else {
      state.pollIntervalId = setInterval(() => pollWorkflowStatus(workflow.id), 3000);
    }

    renderAgentCluster();
  } catch (error) {
    state.apiError = error.message;
    console.error("Failed to start workflow:", error);
  } finally {
    state.isLoading = false;
    renderAgentCluster();
  }
}

async function pollWorkflowStatus(workflowId) {
  try {
    const response = await api.workflows.get(workflowId);
    state.selectedWorkflow = response.workflow;
    state.workflowTasks = response.tasks || [];
    state.workflowArtifacts = response.artifacts || [];

    const allTerminal = state.workflowTasks.every(
      (t) => t.status === "completed" || t.status === "failed"
    );

    if (
      allTerminal ||
      response.workflow.status === "completed" ||
      response.workflow.status === "failed"
    ) {
      clearInterval(state.pollIntervalId);
      state.pollIntervalId = null;
      state.isCompletionVisible = true;
    }

    renderAgentCluster();
  } catch (error) {
    if (error.status === 404) {
      if (state.pollIntervalId) {
        clearInterval(state.pollIntervalId);
        state.pollIntervalId = null;
      }
      state.apiError = "工作流已不存在，轮询已停止。";
      renderAgentCluster();
      return;
    }
    console.error("Polling error:", error);
  }
}

// ============================================================
// V2 Page Rendering
// ============================================================

const V2_VIEWS = [
  "overview", "data-variables", "research-design",
  "empirical-execution", "paper-draft", "artifacts-replication", "agent-console",
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
      </article>
    `).join("") : "<p class='muted'>方法执行产物中没有 method item。</p>"}
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

function renderOverview() {
  const data = state.overviewData;
  if (!data) {
    document.getElementById("overview-question").textContent = "加载中...";
    return;
  }

  clearV2Error("overview");

  // Evidence banner
  const bannerHtml = renderEvidenceBanner(data._meta);
  const existingBanner = document.querySelector("#view-overview > .evidence-banner");
  if (existingBanner) existingBanner.remove();
  if (bannerHtml) {
    document.getElementById("view-overview").insertAdjacentHTML("afterbegin", bannerHtml);
  }

  // Research question
  document.getElementById("overview-question").textContent = data.research_question || data.project?.title || "未设置研究问题";
  document.getElementById("overview-project-meta").textContent =
    `项目：${data.project?.slug || ""} · 当前阶段：${productTermLabel(data.current_stage || "")} · 总体进度：${Math.round((data.overall_progress || 0) * 100)}%`;

  renderWorkflowContract(data.workflow_contract);

  // Stage summary cards
  const summaries = data.stage_summaries || [];
  document.getElementById("stage-summary-grid").innerHTML = summaries.map((summary) => {
    const statusClass = summary.status === "completed" ? "is-completed"
      : summary.status === "in_progress" ? "is-in-progress"
      : summary.status === "pending_confirmation" ? "is-pending"
      : "is-not-started";
    const metrics = summary.metrics || [];
    const metricsHtml = metrics.length
      ? `<div class="stage-summary-metrics">
          ${metrics.map((m) => `<div class="stage-summary-metric"><span class="stage-summary-metric-value">${escapeHtml(productTermLabel(m.value))}</span><span class="stage-summary-metric-label">${escapeHtml(productTermLabel(m.label))}</span></div>`).join("")}
        </div>`
      : `<div class="stage-summary-metrics"><span class="muted">暂无指标</span></div>`;
    return `
      <div class="stage-summary-card ${statusClass}">
        <div class="stage-summary-header">
          <h4 class="stage-summary-title">${escapeHtml(productTermLabel(summary.title))}</h4>
          ${summary.has_pending_action ? `<span class="pill" style="background:rgba(230,126,34,0.12);color:#e67e22;">需确认</span>` : ""}
        </div>
        ${metricsHtml}
        <p class="stage-summary-hint">${escapeHtml(productTermLabel(summary.summary || summary.next_step_hint || ""))}</p>
      </div>
    `;
  }).join("");

  // Risks
  const risks = data.risks || [];
  document.getElementById("overview-risks").innerHTML = risks.length
    ? risks.map((risk) => `
        <div class="event-item">
          <span style="color:${risk.level === "warning" ? "#e67e22" : "#c0392b"};font-size:16px;">${risk.level === "warning" ? "⚠" : "🚫"}</span>
          <div class="event-item-content">${escapeHtml(productTermLabel(risk.description))}</div>
        </div>
      `).join("")
    : `<div class="event-item"><span>✓</span><div class="event-item-content">当前没有识别到关键风险。</div></div>`;

  // Next steps
  const steps = data.next_steps || [];
  document.getElementById("overview-next-steps").innerHTML = steps.length
    ? steps.map((step, i) => `
        <div class="event-item">
          <span style="color:var(--accent);font-weight:600;">${i + 1}.</span>
          <div class="event-item-content">${escapeHtml(productTermLabel(step.description))} ${step.action ? `· <strong>${escapeHtml(productTermLabel(step.action))}</strong>` : ""}</div>
        </div>
      `).join("")
    : `<div class="event-item"><span>→</span><div class="event-item-content">暂无明确下一步建议。</div></div>`;

  // Events
  const events = data.recent_events || [];
  document.getElementById("overview-events").innerHTML = events.length
    ? events.map((evt) => `
        <div class="event-item">
          <span class="event-item-time">${new Date(evt.timestamp).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}</span>
          <div class="event-item-content">
            <span class="event-item-agent">${escapeHtml(evt.agent_name || evt.agent || "系统")}</span>
            ${escapeHtml(productTermLabel(evt.action || ""))}
            ${evt.result === "success" ? "✓" : evt.result === "failed" ? "✗" : ""}
          </div>
        </div>
      `).join("")
    : `<p class="muted">暂无最近事件</p>`;
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

  if (statusPill) statusPill.textContent = preflight.status === "ready_for_review" ? "待人工确认" : (preflight.status || "预检");
  const checks = preflight.checks || [];
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
      <p class="muted external-bind-preflight-note">状态文件：${escapeHtml(preflight.manifest_path || "state/product/dataset_import_preflights.json")} · 本阶段不会改写 paper.yaml、VariableRoleSet、DesignSpec 或 RunPlan。</p>
    </article>
  `;
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

function renderVariableRoleEditor() {
  const roleSet = state.variableRolesData?.variable_role_set || null;
  const form = document.getElementById("variable-role-confirmation-form");
  const meta = document.getElementById("variable-role-editor-meta");
  const statusPill = document.getElementById("variable-role-status-pill");
  const saveButton = document.querySelector("[data-variable-role-save]");
  if (!form || !meta || !statusPill) return;

  if (!roleSet) {
    meta.textContent = "正在读取变量角色集...";
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
  statusPill.textContent = `${roleSet.status || "draft"} · ${roleSet.evidence_level || "local_file"}`;
  meta.textContent = `${roleSet.dataset_path || "未选择数据集"} · version=${roleSet.version ?? 0} · evidence_level=${roleSet.evidence_level || "local_file"}`;
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

  clearV2Error("data");
  state.savingVariableRoles = true;
  renderVariableRoleEditor();
  try {
    await v2api.variableRoles.save(state.selectedProjectId, payload);
    state.variableRolesData = await v2api.variableRoles.get(state.selectedProjectId);
    state.overviewData = await v2api.overview.get(state.selectedProjectId);
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
    renderDesignSpecEditor();
    renderMethodSkillCatalog();
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
    renderRunPlanEditor();
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
      <div class="agent-console-card ${isSelected ? "is-selected" : ""}" data-agent-id="${escapeHtml(agent.id)}" onclick="selectAgent('${escapeHtml(agent.id)}')">
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

async function selectAgent(agentId) {
  state.selectedAgentId = agentId;
  renderAgentConsole(); // re-render to update selection

  const panel = document.getElementById("agent-detail-panel");
  const idLabel = document.getElementById("agent-detail-id");
  if (!panel || !idLabel) return;

  idLabel.textContent = agentId;
  panel.innerHTML = "<p class='muted'>加载详情...</p>";

  try {
    const data = await v2api.agents.get(agentId);
    state.agentDetailData = data;

    const agent = data.agent || {};
    const identity = data.identity || {};
    const permissions = data.permissions || [];
    const capabilities = data.capabilities || [];
    const cost = data.cost || {};
    const audit = data.audit_log || [];

    panel.innerHTML = `
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
  } catch (error) {
    panel.innerHTML = `<div class="error-banner"><span>加载智能体详情失败：${escapeHtml(error.message)}</span></div>`;
  }
}

// --- Data Loading ---

async function loadV2Data(viewName) {
  if (!state.selectedProjectId) return;

  const projectId = state.selectedProjectId;

  try {
    switch (viewName) {
      case "overview":
        state.overviewData = await v2api.overview.get(projectId);
        state.journeyData = await v2api.journey.get(projectId);
        renderOverview();
        renderJourneyBar();
        break;
      case "data-variables":
        state.overviewData = await v2api.overview.get(projectId);
        state.datasetsData = await v2api.datasets.list(projectId);
        state.variableRolesData = await v2api.variableRoles.get(projectId);
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
        state.exportPackageData = await v2api.exportPackage.get(projectId);
        renderArtifactsReplication();
        break;
      case "agent-console":
        state.agentsData = await v2api.agents.list();
        renderAgentConsole();
        break;
      case "empirical-execution":
        state.overviewData = await v2api.overview.get(projectId);
        try {
          state.runPlanData = await v2api.runPlan.get(projectId);
        } catch (error) {
          state.runPlanData = null;
        }
        renderExecutionPreflight();
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
  mountActions();
  mountForm();
  mountAgentClusterEvents();
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
  document.getElementById("view-overview")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
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
    await loadV2Data("overview");
  }
}

void boot();
