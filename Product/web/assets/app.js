const state = {
  projects: [],
  selectedProjectId: null,
  selectedProject: null,
  activeRun: null,
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

async function boot() {
  mountNav();
  mountProjectSelection();
  mountActions();
  mountForm();
  await refreshProjects();
}

void boot();
