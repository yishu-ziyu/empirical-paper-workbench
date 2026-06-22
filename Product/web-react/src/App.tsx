import { useCallback, useEffect, useState } from "react";
import { DottedSurface } from "./components/DottedSurface";
import { ResearchCommandInput } from "./components/ResearchCommandInput";
import { SlideTabs, type StageTab } from "./components/SlideTabs";
import { BriefPanel, type BriefResult, type BriefStepsSnapshot } from "./components/BriefPanel";
import { SearchPanel, type Paper } from "./components/SearchPanel";
import { VariablesPanel, type Variable } from "./components/VariablesPanel";
import { DesignPanel } from "./components/DesignPanel";
import { ExecutionPanel } from "./components/ExecutionPanel";
import { IdentificationAuditPanel } from "./components/IdentificationAuditPanel";
import { SupervisorPlanReview } from "./components/SupervisorPlanReview";
import { AutoResearchStream } from "./components/AutoResearchStream";
import { SystemStatusBar } from "./components/SystemStatusBar";
import { AgentTaskQueuePanel } from "./components/AgentTaskQueuePanel";
import { PaperProductionStatusPanel } from "./components/PaperProductionStatusPanel";
import { ServiceConnectionRecovery } from "./components/ServiceConnectionRecovery";
import { ResearchJourneyBar } from "./components/ResearchJourneyBar";
import { DEFAULT_LOCAL_API_BASE, apiBase, apiUrl, setBrowserApiBase } from "./lib/apiBase";

interface SupervisorPlanStage {
  id: string;
  title: string;
  owner: string;
  status: "empty" | "draft" | "ready" | "running" | "completed" | "failed";
  reason: string;
  inputs: string[];
  outputs: string[];
}

interface SupervisorPlanInspector {
  inputs_used?: string[];
  assumptions?: string[];
  evidence_required?: string[];
  risks?: string[];
  formal_boundary?: string[];
}

interface SubmittedResearchTask {
  message: string;
  mode: string;
  fileCount: number;
  pastedCount: number;
}

type TopicIntakeStatus = "idle" | "registering" | "ready" | "failed";

/** Six end-to-end stages (BDD ref: spec §6.1 + §6.2 + D3 6th tab stub). */
type Stage = "brief" | "search" | "variables" | "design" | "execution" | "identification-audit";

interface LiteratureResult {
  papers: Paper[];
  literaturePath: string;
}

interface VariablesResult {
  variables: Variable[];
  variablesPath: string;
}

interface DesignResult {
  recommended: string;
  designPath: string;
}

interface ExecutionResult {
  paperPath: string;
  resultsPath: string;
}

const STAGE_ORDER: Stage[] = [
  "brief",
  "search",
  "variables",
  "design",
  "execution",
  "identification-audit",
];

const TOPIC_INTAKE_TIMEOUT_MS = 30000;
const CANONICAL_PARENT_EDUCATION_PROJECT_ID = "proj_empirical_paper_template_main";
const CANONICAL_CGSS_HAPPINESS_PROJECT_ID = "proj_cgss_social_capital_happiness";

const STAGE_LABELS: Record<
  Stage,
  { label: string; hint: string; action: string; next: string }
> = {
  brief: {
    label: "研究简报",
    hint: "确认研究问题、边界、贡献和成功标准",
    action: "确认研究简报",
    next: "文献检索",
  },
  search: {
    label: "文献检索",
    hint: "从中文和英文来源筛选相关文献，形成综述素材",
    action: "筛选可用文献",
    next: "变量审阅",
  },
  variables: {
    label: "变量审阅",
    hint: "确认因变量、解释变量和控制变量是否能被数据支持",
    action: "确认变量角色",
    next: "方法选择",
  },
  design: {
    label: "方法选择",
    hint: "比较可行识别策略，查看假设、风险和所需检验",
    action: "选择识别策略",
    next: "论文生成",
  },
  execution: {
    label: "论文生成",
    hint: "生成论文草稿、PDF、结果记录和可复现产物",
    action: "生成论文与结果包",
    next: "识别审计",
  },
  "identification-audit": {
    label: "识别审计",
    hint: "检查趋势、工具变量强度和因果路径是否支撑结论",
    action: "核验识别可信度",
    next: "导出或修订",
  },
};

const STAGE_REQUIREMENTS: Record<Stage, string> = {
  brief: "输入题目后即可生成研究简报。",
  search: "先完成研究简报并保存 brief.md。",
  variables: "先完成文献检索并保存 literature_review.md。",
  design: "先完成变量审阅并保存 variables.json。",
  execution: "先完成方法选择并保存 design.json。",
  "identification-audit": "先完成论文生成并保存 results.json。",
};

function stageRequirement(stage: Stage): string {
  return STAGE_REQUIREMENTS[stage];
}

function stageStatusLabel(stage: Stage, activeStage: Stage, unlocked: boolean): string {
  if (stage === activeStage) return "当前";
  return unlocked ? "已解锁" : "待解锁";
}

function topicHash(s: string): string {
  let hash = 0;
  for (let i = 0; i < s.length; i += 1) {
    hash = (hash * 31 + s.charCodeAt(i)) | 0;
  }
  return Math.abs(hash).toString(36).padStart(6, "0").slice(0, 10);
}

/** Convert a free-form research topic into a filesystem-safe slug. */
function slugify(s: string): string {
  const asciiSlug = s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 50);
  return asciiSlug || `topic-${topicHash(s)}`;
}

function normalizeTaskMode(mode: string | null): string {
  if (mode === "codex-supervisor" || mode === "auto-research" || mode === "human-review") {
    return mode;
  }
  return "codex-supervisor";
}

function buildInitialTaskFromUrl(): SubmittedResearchTask | null {
  if (typeof window === "undefined") return null;
  const params = new URLSearchParams(window.location.search);
  const message = (params.get("topic") ?? params.get("research_topic") ?? "").trim();
  if (!message) return null;
  return {
    message,
    mode: normalizeTaskMode(params.get("mode")),
    fileCount: 0,
    pastedCount: 0,
  };
}

function initialTopicSlugFromUrl(): string {
  return slugify(buildInitialTaskFromUrl()?.message ?? "");
}

function canonicalProjectIdForTask(task: SubmittedResearchTask | null, topicSlug: string): string {
  const topic = task?.message ?? "";
  const isParentEducationWageDemo =
    topic.includes("父母") &&
    (topic.includes("教育水平") || topic.includes("受教育水平")) &&
    (topic.includes("工资") || topic.includes("收入"));
  if (isParentEducationWageDemo) {
    return CANONICAL_PARENT_EDUCATION_PROJECT_ID;
  }
  const isCgssHappinessPaper =
    topic.includes("CGSS") &&
    (topic.includes("幸福感") || topic.toLowerCase().includes("happiness")) &&
    (topic.includes("互联网") || topic.includes("社会资本") || topic.toLowerCase().includes("internet"));
  if (isCgssHappinessPaper) {
    return CANONICAL_CGSS_HAPPINESS_PROJECT_ID;
  }
  return topicSlug ? `proj_${topicSlug.replace(/-/g, "_")}` : "";
}

async function responseErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const body = await response.json();
    const error = body?.error;
    return error?.message || error?.code || fallback;
  } catch {
    return fallback;
  }
}

function explainPlanApprovalError(message: string): string {
  if (message.includes("project_not_found") || message.includes("does not exist")) {
    return "当前题目还没有注册为项目。请先完成研究简报落盘，或从已登记项目进入规划审阅。";
  }
  if (message.includes("SupervisorPlan is required") || message.includes("supervisor_plan_required")) {
    return "还没有可审阅的正式 SupervisorPlan。需要先生成并保存项目级计划。";
  }
  if (message.includes("must be approved") || message.includes("can_dispatch")) {
    return "SupervisorPlan 还没有达到可派发状态。请先完成计划审阅。";
  }
  if (message.includes("subagent_dispatch")) {
    return "SupervisorPlan 还没有子 Agent 派工清单。需要让 Supervisor 重新生成包含分工的计划。";
  }
  return message || "批准失败，请检查本地后端和项目状态。";
}

function toStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item)).filter((item) => item.trim().length > 0);
}

function normalizePlanStatus(value: unknown): SupervisorPlanStage["status"] {
  if (
    value === "empty" ||
    value === "draft" ||
    value === "ready" ||
    value === "running" ||
    value === "completed" ||
    value === "failed"
  ) {
    return value;
  }
  return "draft";
}

function normalizeSupervisorPlanStages(value: unknown): SupervisorPlanStage[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((stage, index) => ({
      id: String(stage.id || `stage-${index + 1}`),
      title: String(stage.title || stage.task || `阶段 ${index + 1}`),
      owner: String(stage.owner || stage.owner_agent || stage.role || "Supervisor"),
      status: normalizePlanStatus(stage.status),
      reason: String(stage.reason || stage.summary || "等待审阅后进入下一步。"),
      inputs: toStringList(stage.inputs),
      outputs: toStringList(stage.outputs),
    }));
}

function normalizeSupervisorPlanInspector(
  plan: Record<string, unknown>,
  fallback: SupervisorPlanInspector | null,
): SupervisorPlanInspector {
  const inputResearchQuestion =
    plan.input_research_question && typeof plan.input_research_question === "object"
      ? (plan.input_research_question as Record<string, unknown>)
      : {};
  const question = inputResearchQuestion.question ? String(inputResearchQuestion.question) : "";
  return {
    inputs_used: question ? [`研究题目：${question}`] : fallback?.inputs_used,
    assumptions: toStringList(plan.human_gates).length
      ? toStringList(plan.human_gates)
      : fallback?.assumptions,
    evidence_required: toStringList(plan.evidence_requirements).length
      ? toStringList(plan.evidence_requirements)
      : fallback?.evidence_required,
    risks: toStringList(plan.risks).length ? toStringList(plan.risks) : fallback?.risks,
    formal_boundary:
      typeof plan.write_boundary === "string" && plan.write_boundary
        ? [plan.write_boundary]
        : fallback?.formal_boundary,
  };
}

export function App() {
  const [task, setTask] = useState<SubmittedResearchTask | null>(() => buildInitialTaskFromUrl());
  const [topicSlug, setTopicSlug] = useState<string>(() => initialTopicSlugFromUrl());
  const [activeStage, setActiveStage] = useState<Stage>("brief");
  // codex-supervisor mode: 计划审核通过前, BriefPanel 不渲染
  const [planApproved, setPlanApproved] = useState<boolean>(false);
  const [planStages, setPlanStages] = useState<SupervisorPlanStage[] | null>(null);
  const [planInspector, setPlanInspector] = useState<SupervisorPlanInspector | null>(null);
  const [planEvidenceLevel, setPlanEvidenceLevel] = useState<string | null>(null);
  const [planFetchError, setPlanFetchError] = useState<string | null>(null);
  const [approvingPlan, setApprovingPlan] = useState(false);
  const [planApprovalError, setPlanApprovalError] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string>("");
  const [planIntakeStatus, setPlanIntakeStatus] = useState<TopicIntakeStatus>("idle");
  const [planIntakeMessage, setPlanIntakeMessage] = useState<string | null>(null);
  const [planReloadNonce, setPlanReloadNonce] = useState(0);

  // Results from each stage. Preserved across navigation so the user can
  // jump back to an earlier tab without losing state.
  const [briefResult, setBriefResult] = useState<BriefResult | null>(null);
  // 4 个 research-journal step 的累积文本 + 落盘的 final brief —
  // 用户切走后再切回 brief tab, BriefPanel 据此 hydrate, 不重新跑 streaming
  const [briefSnapshot, setBriefSnapshot] = useState<BriefStepsSnapshot | null>(null);
  const [literatureResult, setLiteratureResult] = useState<LiteratureResult | null>(null);
  const [variablesResult, setVariablesResult] = useState<VariablesResult | null>(null);
  const [designResult, setDesignResult] = useState<DesignResult | null>(null);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);

  const [toastMessage, setToastMessage] = useState<string | null>(null);

  /**
   * Tab is unlocked iff every stage strictly before it has completed.
   * brief is always unlocked; execution is unlocked only when design done.
   * 6th tab (identification-audit) unlocked only when executionResult is set.
   */
  const canEnter = useCallback(
    (stage: Stage): boolean => {
      switch (stage) {
        case "brief":
          return true;
        case "search":
          return briefResult !== null;
        case "variables":
          return briefResult !== null && literatureResult !== null;
        case "design":
          return (
            briefResult !== null &&
            literatureResult !== null &&
            variablesResult !== null
          );
        case "execution":
          return (
            briefResult !== null &&
            variablesResult !== null &&
            designResult !== null
          );
        case "identification-audit":
          return executionResult !== null;
        default:
          return false;
      }
    },
    [briefResult, literatureResult, variablesResult, designResult, executionResult],
  );

  const showToast = useCallback((msg: string) => {
    setToastMessage(msg);
    window.setTimeout(() => setToastMessage(null), 3000);
  }, []);

  const handleStageChange = (newId: string) => {
    if (!STAGE_ORDER.includes(newId as Stage)) return;
    const target = newId as Stage;
    if (!canEnter(target)) {
      showToast(stageRequirement(target));
      return;
    }
    setActiveStage(target);
  };

  const resetAll = () => {
    setTask(null);
    setTopicSlug("");
    setActiveStage("brief");
    setBriefResult(null);
    setBriefSnapshot(null);
    setLiteratureResult(null);
    setVariablesResult(null);
    setDesignResult(null);
    setExecutionResult(null);
    setPlanApproved(false);
    setPlanStages(null);
    setPlanInspector(null);
    setPlanEvidenceLevel(null);
    setPlanFetchError(null);
    setPlanApprovalError(null);
    setApprovingPlan(false);
    setProjectId("");
    setPlanIntakeStatus("idle");
    setPlanIntakeMessage(null);
    setPlanReloadNonce(0);
  };

  // codex-supervisor mode: 进入 brief tab 时拉计划草案.
  // 仅在 mode 切换 / 任务首次进入时拉一次 (topic 变化时重拉).
  useEffect(() => {
    if (!task) return;
    if (task.mode !== "codex-supervisor") return;
    if (planStages !== null) return;
    const ctrl = new AbortController();
    fetch(apiUrl("/api/supervisor/plan"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: task.message }),
      signal: ctrl.signal,
    })
      .then(async (r) => {
        if (!r.ok) throw new Error("plan_service_unavailable");
        return r.json();
      })
      .then((data: { stages?: SupervisorPlanStage[]; inspector?: SupervisorPlanInspector; evidence_level?: string }) => {
        setPlanStages(data.stages ?? []);
        setPlanInspector(data.inspector ?? null);
        setPlanEvidenceLevel(data.evidence_level ?? null);
        setPlanFetchError(null);
        setPlanApprovalError(null);
      })
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === "AbortError") return;
        setPlanFetchError(
          "没有拿到 SupervisorPlan。请确认当前地址运行的是 FastAPI Product.app，而不是普通静态文件服务。",
        );
        setPlanStages(null);
        setPlanInspector(null);
        setPlanEvidenceLevel(null);
      });
    return () => ctrl.abort();
  }, [task, planStages, planReloadNonce]);

  // task 重置时清掉 plan
  useEffect(() => {
    if (task === null) {
      setPlanStages(null);
      setPlanInspector(null);
      setPlanEvidenceLevel(null);
      setPlanApproved(false);
      setPlanFetchError(null);
      setPlanApprovalError(null);
      setApprovingPlan(false);
      setProjectId("");
      setPlanIntakeStatus("idle");
      setPlanIntakeMessage(null);
      setPlanReloadNonce(0);
    }
  }, [task]);

  // ── Intake screen ──
  if (task === null) {
    return (
      <main className="app-shell app-shell--intake">
        <DottedSurface />
        <section className="start-panel">
          <div className="start-panel__heading">
            <span className="eyebrow">本地实证研究 OS</span>
            <h1>今天要推进什么研究？</h1>
          </div>
          <ResearchCommandInput
            onSubmit={({ message, files, pastedContent, mode }) => {
              setTask({
                message,
                mode,
                fileCount: files.length,
                pastedCount: pastedContent.length,
              });
              setTopicSlug(slugify(message));
              setActiveStage("brief");
              setProjectId("");
              setPlanIntakeStatus("idle");
              setPlanIntakeMessage(null);
            }}
          />
        </section>
      </main>
    );
  }

  // ── Build 5-tab configuration with stage-locking hints ──
  const tabs: StageTab[] = STAGE_ORDER.map((stage) => {
    const info = STAGE_LABELS[stage];
    const unlocked = canEnter(stage);
    return {
      id: stage,
      label: info.label,
      hint: unlocked ? info.hint : stageRequirement(stage),
      disabled: !unlocked,
    };
  });
  const completedStages: Stage[] = [
    ...(briefResult ? (["brief"] as Stage[]) : []),
    ...(literatureResult ? (["search"] as Stage[]) : []),
    ...(variablesResult ? (["variables"] as Stage[]) : []),
    ...(designResult ? (["design"] as Stage[]) : []),
    ...(executionResult ? (["execution", "identification-audit"] as Stage[]) : []),
  ];
  const currentStageMeta = STAGE_LABELS[activeStage];
  const currentStageIndex = STAGE_ORDER.indexOf(activeStage);
  const nextStage = STAGE_ORDER[currentStageIndex + 1] ?? null;
  const currentApiBase = apiBase() || "同源服务";
  const candidateProjectId = canonicalProjectIdForTask(task, topicSlug);
  const effectiveProjectId = projectId || candidateProjectId;
  const handleResetApiBase = () => {
    const targetApiBase = /^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?/i.test(currentApiBase)
      ? currentApiBase.replace(/\/+$/, "")
      : DEFAULT_LOCAL_API_BASE;
    setBrowserApiBase(targetApiBase);
    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.set("api_base", targetApiBase);
    window.location.assign(nextUrl.toString());
  };
  const retrySupervisorPlan = () => {
    setPlanFetchError(null);
    setPlanApprovalError(null);
    setPlanStages(null);
    setPlanReloadNonce((value) => value + 1);
  };
  const ensureTopicProjectAndSupervisorPlan = async (): Promise<string> => {
    if (!task) {
      throw new Error("missing_task");
    }
    if (projectId && planStages !== null) {
      setPlanIntakeStatus("ready");
      setPlanIntakeMessage(`已登记项目：${projectId}`);
      return projectId;
    }
    setPlanIntakeStatus("registering");
    setPlanIntakeMessage(planStages !== null ? "正在保存当前任务路线" : "正在登记题目和任务路线");
    const topicIntakeController = new AbortController();
    const topicIntakeTimeoutId = window.setTimeout(
      () => topicIntakeController.abort(),
      TOPIC_INTAKE_TIMEOUT_MS,
    );
    try {
      const response = await fetch(
        apiUrl(
          planStages !== null
            ? "/api/v1/topic-intake/supervisor-plan/preview"
            : "/api/v1/topic-intake/supervisor-plan",
        ),
        {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: topicIntakeController.signal,
        body: JSON.stringify({
          topic: task.message,
          slug: topicSlug,
          note:
            planStages !== null
              ? "用户批准当前 SupervisorPlan 预览前，将审阅页路线保存为项目级计划。"
              : "用户从研究入口批准路线前登记题目和 SupervisorPlan。",
          supervisor_plan:
            planStages !== null
              ? {
                  stage_plan: planStages,
                  evidence_requirements: planInspector?.evidence_required ?? [],
                  risks: planInspector?.risks ?? [],
                  human_gates: planInspector?.assumptions ?? [],
                  reference_chain_policy: null,
                }
              : undefined,
        }),
        },
      );
      if (!response.ok) {
        const message = await responseErrorMessage(response, "题目登记失败。");
        setPlanIntakeStatus("failed");
        setPlanIntakeMessage(message);
        throw new Error(message);
      }

      const data = await response.json();
      setProjectId(data.project.id);
      const supervisorPlan = (data.supervisor_plan ?? {}) as Record<string, unknown>;
      setPlanStages(normalizeSupervisorPlanStages(supervisorPlan.stage_plan));
      setPlanInspector(normalizeSupervisorPlanInspector(supervisorPlan, planInspector));
      setPlanEvidenceLevel(String(supervisorPlan.evidence_level || "topic_intake"));
      setPlanFetchError(null);
      setPlanApprovalError(null);
      setPlanIntakeStatus("ready");
      setPlanIntakeMessage(`已登记项目：${data.project.id}`);
      return data.project.id;
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        const message =
          "LLM Supervisor 生成计划超时。当前主模型可能仍在后台处理；你可以重试，或稍后重新读取队列。";
        setPlanIntakeStatus("failed");
        setPlanIntakeMessage(message);
        throw new Error(message);
      }
      throw err;
    } finally {
      window.clearTimeout(topicIntakeTimeoutId);
    }
  };

  const approveSupervisorPlan = async () => {
    setApprovingPlan(true);
    setPlanApprovalError(null);
    try {
      const activeProjectId = await ensureTopicProjectAndSupervisorPlan();
      const reviewResponse = await fetch(apiUrl(`/api/v1/projects/${activeProjectId}/supervisor-plan/review`), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "approve",
          note: "用户在研究工作台批准 SupervisorPlan，并请求创建 Agent Task Queue。",
        }),
      });
      if (!reviewResponse.ok) {
        throw new Error(
          await responseErrorMessage(reviewResponse, "SupervisorPlan 审阅写回失败。"),
        );
      }

      const queueResponse = await fetch(apiUrl(`/api/v1/projects/${activeProjectId}/agent-task-queue`), {
        method: "POST",
      });
      if (!queueResponse.ok) {
        throw new Error(
          await responseErrorMessage(queueResponse, "Agent Task Queue 创建失败。"),
        );
      }

      setPlanApproved(true);
      setPlanApprovalError(null);
    } catch (err) {
      const message = explainPlanApprovalError(err instanceof Error ? err.message : "");
      setPlanApproved(false);
      setPlanApprovalError(message);
      setPlanIntakeStatus("failed");
      setPlanIntakeMessage(message);
    } finally {
      setApprovingPlan(false);
    }
  };

  return (
    <main className="app-shell analysis-workspace" data-effective-project-id={effectiveProjectId}>
      <DottedSurface />
      <section className="analysis-workspace__header">
        <button
          className="analysis-workspace__back"
          type="button"
          onClick={resetAll}
        >
          新任务
        </button>
        <div>
          <span className="eyebrow">分析工作台</span>
          <h1>{task.message || "附件驱动任务"}</h1>
          <p>
            模式：
            {task.mode === "codex-supervisor"
              ? "智能规划模式"
              : task.mode === "auto-research"
                ? "自动探索模式"
                : "人工审阅模式"}
            {" · "}文件 {task.fileCount} · 长文本 {task.pastedCount} · 任务编号：{" "}
            <code data-testid="topic-slug">{topicSlug}</code>
          </p>
          <details className="analysis-workspace__connection">
            <summary>连接状态</summary>
            <SystemStatusBar
              projectId={effectiveProjectId}
              topicSlug={topicSlug}
            />
          </details>
        </div>
      </section>

      <section className="stage-panel" aria-label="研究路径">
        {toastMessage ? (
          <div className="inline-toast" role="alert" data-testid="stage-locked-toast">
            <span className="toast-icon">🔒</span>
            <span>{toastMessage}</span>
          </div>
        ) : null}

        {effectiveProjectId ? (
          <PaperProductionStatusPanel
            projectId={effectiveProjectId}
            fallbackProjectId={CANONICAL_PARENT_EDUCATION_PROJECT_ID}
            topic={task.message}
          />
        ) : null}

        <details className="analysis-workspace__flow-details">
          <summary>研究流程</summary>
          <ResearchJourneyBar
            activeStage={activeStage}
            completedStages={completedStages}
            onStageSelect={setActiveStage}
          />
          <SlideTabs tabs={tabs} value={activeStage} onChange={handleStageChange} />

          <div className="stage-panel__current-action" data-testid="stage-current-action">
            <span>现在只做</span>
            <strong>{currentStageMeta.action}</strong>
            <span>完成后进入：{currentStageMeta.next}</span>
          </div>

          <div className="stage-panel__guide" data-testid="stage-guide">
            <div>
              <span>当前交付</span>
              <strong>{currentStageMeta.action}</strong>
              <p>{stageRequirement(activeStage)}</p>
            </div>
            <div data-testid="stage-unlock-requirement">
              <span>下一步门槛</span>
              <strong>{nextStage ? STAGE_LABELS[nextStage].label : "已到最后阶段"}</strong>
              <p>{nextStage ? stageRequirement(nextStage) : "完成识别审计后进入导出或修订。"}</p>
            </div>
          </div>

          <ol className="stage-unlock-list" data-testid="stage-unlock-list" aria-label="阶段解锁条件">
            {STAGE_ORDER.map((stage) => {
              const unlocked = canEnter(stage);
              return (
                <li
                  className={stage === activeStage ? "stage-unlock-list__item stage-unlock-list__item--active" : "stage-unlock-list__item"}
                  key={stage}
                >
                  <span>{stageStatusLabel(stage, activeStage, unlocked)}</span>
                  <strong>{STAGE_LABELS[stage].label}</strong>
                  <p>{unlocked ? STAGE_LABELS[stage].hint : stageRequirement(stage)}</p>
                </li>
              );
            })}
          </ol>

        {activeStage === "brief" ? (
          task.mode === "codex-supervisor" ? (
            <>
              {planFetchError ? (
                <div data-testid="plan-fetch-error">
                  <ServiceConnectionRecovery
                    message={planFetchError}
                    currentApiBase={currentApiBase}
                    onRetry={retrySupervisorPlan}
                    onUseLocalBackend={handleResetApiBase}
                    localActionTestId="reset-api-base-action"
                  />
                </div>
              ) : planStages === null ? (
                <div className="task-brief__loading" role="status" data-testid="supervisor-plan-loading">
                  <span className="eyebrow">SupervisorPlan</span>
                  <strong>正在生成 SupervisorPlan</strong>
                  <p>系统正在读取题目、模式和本地服务状态，完成后再进入路线审阅。</p>
                </div>
              ) : (
                <div data-testid="supervisor-plan-ready">
                  <SupervisorPlanReview
                    stages={planStages}
                    inspector={planInspector}
                    topic={task.message}
                    evidenceLevel={planEvidenceLevel}
                    approving={approvingPlan}
                    approved={planApproved}
                    approvalError={planApprovalError}
                    intakeStatus={planIntakeStatus}
                    intakeMessage={planIntakeMessage}
                    projectId={effectiveProjectId}
                    onApprove={approveSupervisorPlan}
                    onReject={() => {
                      showToast("已否决计划，回到新任务选择。");
                      resetAll();
                    }}
                  />
                </div>
              )}
              {planApproved ? (
                <>
                  <AgentTaskQueuePanel projectId={effectiveProjectId} />
                  <BriefPanel
                    topic={task.message}
                    initialSnapshot={briefSnapshot}
                    onComplete={(b, snapshot) => {
                      setBriefResult(b);
                      setBriefSnapshot(snapshot);
                      setActiveStage("search");
                    }}
                  />
                </>
              ) : null}
            </>
          ) : task.mode === "auto-research" ? (
            <AutoResearchStream
              topic={task.message}
              topicSlug={topicSlug}
              onComplete={(b, snapshot) => {
                setBriefResult(b);
                setBriefSnapshot(snapshot);
                setActiveStage("search");
              }}
            />
          ) : (
            // human-review (default) and any unrecognized mode → BriefPanel as today
            <BriefPanel
              topic={task.message}
              initialSnapshot={briefSnapshot}
              onComplete={(b, snapshot) => {
                setBriefResult(b);
                setBriefSnapshot(snapshot);
                setActiveStage("search");
              }}
            />
          )
        ) : null}

        {activeStage === "search" && briefResult ? (
          <SearchPanel
            briefPath={briefResult.path}
            topicSlug={topicSlug}
            onComplete={(papers, literaturePath) => {
              setLiteratureResult({ papers, literaturePath });
              setActiveStage("variables");
            }}
          />
        ) : null}

        {activeStage === "variables" && briefResult ? (
          <VariablesPanel
            briefPath={briefResult.path}
            topicSlug={topicSlug}
            onComplete={(variables, variablesPath) => {
              setVariablesResult({ variables, variablesPath });
              setActiveStage("design");
            }}
          />
        ) : null}

        {activeStage === "design" && briefResult && variablesResult ? (
          <DesignPanel
            topicSlug={topicSlug}
            briefPath={briefResult.path}
            variablesPath={variablesResult.variablesPath}
            onComplete={(recommended, designPath) => {
              setDesignResult({ recommended, designPath });
              setActiveStage("execution");
            }}
          />
        ) : null}

        {activeStage === "execution" && briefResult && variablesResult && designResult ? (
          <ExecutionPanel
            briefPath={briefResult.path}
            variablesPath={variablesResult.variablesPath}
            topicSlug={topicSlug}
            designPath={designResult.designPath}
            onComplete={(paperPath, resultsPath) => {
              setExecutionResult({ paperPath, resultsPath });
            }}
          />
        ) : null}

        {activeStage === "identification-audit" && executionResult && designResult ? (
          <IdentificationAuditPanel
            resultsPath={executionResult.resultsPath}
            designPath={designResult.designPath}
          />
        ) : null}

        {briefResult && activeStage !== "brief" ? (
          <div className="stage-panel__saved-link" data-testid="saved-brief-link">
            <span className="eyebrow">已落盘</span>
            <p>
              研究简报已生成（路径：
              <code data-testid="saved-brief-path">{briefResult.path}</code>）
            </p>
            <button
              type="button"
              className="btn btn--ghost workbench-saved-brief"
              onClick={() => setActiveStage("brief")}
              data-testid="view-saved-brief"
            >
              查看已保存的简报
            </button>
          </div>
        ) : null}

        {executionResult ? (
          <div
            className="stage-panel__completion"
            data-testid="final-complete"
            role="status"
          >
            <h2>研究链路完成</h2>
            <p>
              论文文件：{" "}
              <code data-testid="final-paper-path">{executionResult.paperPath}</code>
            </p>
            <p>
              结果记录：{" "}
              <code data-testid="final-results-path">
                {executionResult.resultsPath}
              </code>
            </p>
            <p className="stage-panel__completion-hint">
              全流程已完成。下一步可以打开识别审计，确认哪些结论可以进入正式稿。
            </p>
          </div>
        ) : null}

        <div className="stage-panel__summary">
          <span>当前阶段</span>
          <strong>{currentStageMeta.label}</strong>
          <p>{currentStageMeta.hint}</p>
        </div>
        </details>
      </section>
    </main>
  );
}
