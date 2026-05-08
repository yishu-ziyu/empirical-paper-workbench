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
  isArtifactDrawerOpen: false,
  isCompletionVisible: false,
  pollIntervalId: null,

  // UI state
  isLoading: false,
  apiError: null,
  useMock: false,
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
    throw new Error(`${response.status} ${message}`);
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
    { label: "Projects", value: state.projects.length },
    { label: "Selected", value: selected ? selected.slug : "none" },
    { label: "Draft Ready", value: selected?.artifacts?.markdown ? "yes" : "no" },
    { label: "Review Loop", value: orchestration?.review_loop?.status ?? "none" },
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
    });
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
    async promote(artifactId, target) {
      return fetchJson(`/api/v1/artifacts/${artifactId}/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target }),
      });
    },
  },
};

function getAvatarColor(index) {
  return AGENT_AVATAR_COLORS[index % AGENT_AVATAR_COLORS.length];
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
  updateComposerState();
}

function renderErrorBanner() {
  const banner = document.getElementById("agent-cluster-error");
  if (!banner) return;

  if (state.apiError) {
    banner.style.display = "block";
    banner.innerHTML = `
      <span>${escapeHtml(state.apiError)}</span>
      <button class="ghost-button" id="dismiss-error" style="padding: 4px 10px; font-size: 12px;">Dismiss</button>
    `;
    banner.querySelector("#dismiss-error")?.addEventListener("click", () => {
      state.apiError = null;
      renderErrorBanner();
    });
  } else {
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

  if (!workflow) {
    titleEl.textContent = "尚未启动研究";
    subtitleEl.textContent = "输入研究问题并点击启动";
    phaseEl.textContent = "-";
    progressEl.textContent = "0%";
    countEl.textContent = "0/10";
    return;
  }

  titleEl.textContent = workflow.title;
  subtitleEl.textContent = `创建于 ${new Date(workflow.created_at).toLocaleString("zh-CN")}`;
  phaseEl.textContent = getStatusLabel(workflow.phase);
  progressEl.textContent = `${Math.round(workflow.progress * 100)}%`;

  const completedCount = state.workflowTasks.filter((t) => t.status === "completed").length;
  countEl.textContent = `${completedCount}/${state.workflowTasks.length}`;
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
      const progressPercent = Math.round(task.progress * 100);

      return `
        <div
          class="agent-row ${isCompleted ? "is-completed" : ""} ${isFailed ? "is-failed" : ""}"
          data-task-id="${task.id}"
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

  // Artifact drawer toggle
  document.getElementById("toggle-artifact-drawer")?.addEventListener("click", () => {
    state.isArtifactDrawerOpen = !state.isArtifactDrawerOpen;
    renderArtifactDrawer();
  });

  document.getElementById("close-artifact-drawer")?.addEventListener("click", () => {
    state.isArtifactDrawerOpen = false;
    renderArtifactDrawer();
  });

  // Start workflow
  document.getElementById("start-workflow-button")?.addEventListener("click", () => {
    const input = document.getElementById("research-goal-input");
    const goal = input.value.trim();
    if (!goal) return;

    void startWorkflow(goal);
    input.value = "";
  });

  // Toggle mock mode (dev helper: Ctrl+M)
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "m") {
      e.preventDefault();
      state.useMock = !state.useMock;
      console.log(`[Dev] Mock mode: ${state.useMock ? "ON" : "OFF"}`);
    }
  });

  // Completion card actions
  document.getElementById("dismiss-completion-button")?.addEventListener("click", () => {
    state.isCompletionVisible = false;
    renderCompletionCard();
  });

  document.getElementById("view-report-button")?.addEventListener("click", () => {
    alert("最终报告功能待后端实现");
  });

  document.getElementById("promote-artifacts-button")?.addEventListener("click", () => {
    alert("导出到项目功能待后端实现");
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

async function startWorkflow(title) {
  state.isLoading = true;
  state.apiError = null;
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
    console.error("Polling error:", error);
  }
}

async function boot() {
  mountNav();
  mountProjectSelection();
  mountActions();
  mountForm();
  mountAgentClusterEvents();
  await refreshProjects();
}

void boot();
