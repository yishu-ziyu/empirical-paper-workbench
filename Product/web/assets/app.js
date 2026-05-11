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
  designData: null,
  draftsData: null,
  agentsData: null,
  selectedAgentId: null,
  agentDetailData: null,
  provenanceData: null,
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
          <div class="muted">stage=${project.current_stage} · mode=${project.last_run_mode}</div>
          <div class="muted">dataset=${project.dataset_exists}</div>
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
              <div class="muted">exists=${artifact.exists}</div>
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
  },
  design: {
    async get(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/design`);
    },
  },
  drafts: {
    async list(projectId) {
      return fetchJson(`/api/v1/projects/${projectId}/drafts`);
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
    queued: "Queued",
    planning: "Planning",
    researching: "Researching",
    synthesizing: "Synthesizing",
    reviewing: "Reviewing",
    completed: "Completed",
    failed: "Failed",
    cancelled: "Cancelled",
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
      <button class="ghost-button" id="dismiss-error" style="padding: 4px 10px; font-size: 12px;">Dismiss</button>
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
      <span class="completion-stat-label">完成 Agents</span>
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
          <option value="manuscripts">Manuscripts</option>
          <option value="results">Results</option>
          <option value="submissions">Submissions</option>
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
    <p class="muted">${escapeHtml(state.agentDetailPreview.path || "local preview")}</p>
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
  const label = level === "mock" ? "演示数据" : level === "local_file" ? "本地文件" : level;
  return `<span class="evidence-badge ${level}">${label}</span>`;
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
        <span class="journey-label">${escapeHtml(stage.name)}</span>
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
    `项目：${data.project?.slug || ""} · 当前阶段：${data.current_stage || ""} · 总体进度：${Math.round((data.overall_progress || 0) * 100)}%`;

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
          ${metrics.map((m) => `<div class="stage-summary-metric"><span class="stage-summary-metric-value">${escapeHtml(m.value)}</span><span class="stage-summary-metric-label">${escapeHtml(m.label)}</span></div>`).join("")}
        </div>`
      : `<div class="stage-summary-metrics"><span class="muted">暂无指标</span></div>`;
    return `
      <div class="stage-summary-card ${statusClass}">
        <div class="stage-summary-header">
          <h4 class="stage-summary-title">${escapeHtml(summary.title)}</h4>
          ${summary.has_pending_action ? `<span class="pill" style="background:rgba(230,126,34,0.12);color:#e67e22;">需确认</span>` : ""}
        </div>
        ${metricsHtml}
        <p class="stage-summary-hint">${escapeHtml(summary.summary || summary.next_step_hint || "")}</p>
      </div>
    `;
  }).join("");

  // Risks
  const risks = data.risks || [];
  document.getElementById("overview-risks").innerHTML = risks.length
    ? risks.map((risk) => `
        <div class="event-item">
          <span style="color:${risk.level === "warning" ? "#e67e22" : "#c0392b"};font-size:16px;">${risk.level === "warning" ? "⚠" : "🚫"}</span>
          <div class="event-item-content">${escapeHtml(risk.description)}</div>
        </div>
      `).join("")
    : `<div class="event-item"><span>✓</span><div class="event-item-content">当前没有识别到关键风险。</div></div>`;

  // Next steps
  const steps = data.next_steps || [];
  document.getElementById("overview-next-steps").innerHTML = steps.length
    ? steps.map((step, i) => `
        <div class="event-item">
          <span style="color:var(--accent);font-weight:600;">${i + 1}.</span>
          <div class="event-item-content">${escapeHtml(step.description)} ${step.action ? `· <strong>${escapeHtml(step.action)}</strong>` : ""}</div>
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
            ${escapeHtml(evt.action || "")}
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

  if (items.length === 0) {
    document.getElementById("datasets-list").innerHTML = renderEmptyState(data.empty_state);
  } else {
    document.getElementById("datasets-list").innerHTML = items.map((ds) => `
      <div class="project-card">
        <strong>${escapeHtml(ds.name || ds.id)}</strong>
        <div class="muted">${ds.row_count || 0} 行 · ${ds.column_count || 0} 列 · ${ds.file_type || "未知格式"}</div>
      </div>
    `).join("");
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
    return;
  }

  clearV2Error("draft");

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

// --- Artifacts & Replication Page ---

function renderArtifactsReplication() {
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
    : "<p class='muted'>暂无 Pipeline Roles</p>";

  document.getElementById("agent-dimension-list").innerHTML = dimension.length
    ? dimension.map(renderAgentCard).join("")
    : "<p class='muted'>暂无 Research Dimension Agents</p>";
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
          <div class="muted">Provider：${escapeHtml(identity.provider || "local_codex")}</div>
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
          <div class="muted">Provider：${escapeHtml(cost.provider || "local_codex")}</div>
          <div class="muted">预估 Token：${cost.estimated_tokens || 0}</div>
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
    panel.innerHTML = `<div class="error-banner"><span>加载 Agent 详情失败：${escapeHtml(error.message)}</span></div>`;
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
        state.datasetsData = await v2api.datasets.list(projectId);
        renderDataVariables();
        break;
      case "research-design":
        state.designData = await v2api.design.get(projectId);
        renderResearchDesign();
        break;
      case "paper-draft":
        state.draftsData = await v2api.drafts.list(projectId);
        renderPaperDraft();
        break;
      case "artifacts-replication":
        renderArtifactsReplication();
        break;
      case "agent-console":
        state.agentsData = await v2api.agents.list();
        renderAgentConsole();
        break;
      case "empirical-execution":
        // Phase A skeleton only, no data to load
        break;
    }
  } catch (error) {
    console.error(`Failed to load ${viewName}:`, error);
    const viewId = viewName.replace(/-/g, "");
    showV2Error(viewId, `加载失败：${error.message}`);
  }
}

// ============================================================
// Agent Cluster
// ============================================================
async function boot() {
  mountNav();
  mountProjectSelection();
  mountActions();
  mountForm();
  mountAgentClusterEvents();
  await refreshProjects();
  // Load default V2 view data
  if (state.selectedProjectId) {
    await loadV2Data("overview");
  }
}

void boot();
