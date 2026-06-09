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

interface SubmittedResearchTask {
  message: string;
  mode: string;
  fileCount: number;
  pastedCount: number;
}

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

/**
 * Convert a free-form research topic into a filesystem-safe slug.
 * Falls back to "untitled" when the input contains no ASCII alphanumerics
 * (e.g. pure Chinese topics will slugify to "untitled" — acceptable for
 * Phase 1; downstream code can read the raw topic from brief.md).
 */
function slugify(s: string): string {
  return (
    s
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 50) || "untitled"
  );
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

export function App() {
  const [task, setTask] = useState<SubmittedResearchTask | null>(() => buildInitialTaskFromUrl());
  const [topicSlug, setTopicSlug] = useState<string>(() => initialTopicSlugFromUrl());
  const [activeStage, setActiveStage] = useState<Stage>("brief");
  // codex-supervisor mode: 计划审核通过前, BriefPanel 不渲染
  const [planApproved, setPlanApproved] = useState<boolean>(false);
  const [planStages, setPlanStages] = useState<SupervisorPlanStage[] | null>(null);
  const [planFetchError, setPlanFetchError] = useState<string | null>(null);

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
      showToast("请按顺序完成前一阶段后再进入。");
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
    setPlanFetchError(null);
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
      .then((data: { stages?: SupervisorPlanStage[] }) => {
        setPlanStages(data.stages ?? []);
        setPlanFetchError(null);
      })
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === "AbortError") return;
        setPlanFetchError(
          "没有拿到 SupervisorPlan。请确认当前地址运行的是 FastAPI Product.app，而不是普通静态文件服务。",
        );
        setPlanStages(null);
      });
    return () => ctrl.abort();
  }, [task, planStages]);

  // task 重置时清掉 plan
  useEffect(() => {
    if (task === null) {
      setPlanStages(null);
      setPlanApproved(false);
      setPlanFetchError(null);
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
      hint: unlocked ? info.hint : "请按顺序完成前一阶段后再进入。",
      disabled: !unlocked,
    };
  });
  const currentStageMeta = STAGE_LABELS[activeStage];
  const currentApiBase = apiBase() || "同源服务";
  const handleResetApiBase = () => {
    setBrowserApiBase(DEFAULT_LOCAL_API_BASE);
    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.set("api_base", DEFAULT_LOCAL_API_BASE);
    window.location.assign(nextUrl.toString());
  };

  return (
    <main className="app-shell analysis-workspace">
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
          <SystemStatusBar
            projectId={`proj_${topicSlug}`}
            topicSlug={topicSlug}
          />
        </div>
      </section>

      <section className="stage-panel" aria-label="研究路径">
        {toastMessage ? (
          <div className="inline-toast" role="alert" data-testid="stage-locked-toast">
            <span className="toast-icon">🔒</span>
            <span>{toastMessage}</span>
          </div>
        ) : null}

        <SlideTabs tabs={tabs} value={activeStage} onChange={handleStageChange} />

        <div className="stage-panel__current-action" data-testid="stage-current-action">
          <span>现在只做</span>
          <strong>{currentStageMeta.action}</strong>
          <span>完成后进入：{currentStageMeta.next}</span>
        </div>

        {activeStage === "brief" ? (
          task.mode === "codex-supervisor" ? (
            <>
              {planFetchError ? (
                <div className="task-brief__error" role="alert" data-testid="plan-fetch-error">
                  <strong>计划加载失败：</strong> {planFetchError}
                  <p>
                    当前后端地址：
                    <code className="task-brief__error-address">{currentApiBase}</code>
                  </p>
                  <div className="task-brief__error-actions">
                    <button
                      className="btn btn--secondary"
                      type="button"
                      onClick={handleResetApiBase}
                      data-testid="reset-api-base-action"
                    >
                      切回本地后端
                    </button>
                    <span>本地后端默认地址：{DEFAULT_LOCAL_API_BASE}</span>
                  </div>
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
                    onApprove={() => {
                      setPlanApproved(true);
                    }}
                    onReject={() => {
                      showToast("已否决计划，回到新任务选择。");
                      resetAll();
                    }}
                  />
                </div>
              )}
              {planApproved ? (
                <>
                  <AgentTaskQueuePanel projectId={`proj_${topicSlug}`} />
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
      </section>
    </main>
  );
}
