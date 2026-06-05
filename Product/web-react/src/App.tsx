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

const STAGE_LABELS: Record<Stage, { label: string; hint: string }> = {
  brief: { label: "任务书", hint: "生成 4 段式研究简报（研究问题 / 边际贡献 / 研究边界 / 成功标准）" },
  search: { label: "递归搜索", hint: "arxiv 召回 + LLM 重排，提炼 8-12 篇相关文献" },
  variables: { label: "数据变量", hint: "基于数据集 schema + 简报识别 X / Y / control 候选变量" },
  design: { label: "方法设计", hint: "StatsPAI 估算候选识别策略，LLM 解释并推荐" },
  execution: { label: "执行实验", hint: "流式生成 9 节论文 + paper.pdf + results.json" },
  "identification-audit": { label: "识别审计", hint: "Pre-trend + 弱 IV 诊断 + DAG（pre-registration 占位）" },
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

export function App() {
  const [task, setTask] = useState<SubmittedResearchTask | null>(null);
  const [topicSlug, setTopicSlug] = useState<string>("");
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
    const base = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";
    fetch(`${base}/api/supervisor/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: task.message }),
      signal: ctrl.signal,
    })
      .then(async (r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: { stages?: SupervisorPlanStage[] }) => {
        setPlanStages(data.stages ?? []);
        setPlanFetchError(null);
      })
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === "AbortError") return;
        setPlanFetchError(err instanceof Error ? err.message : String(err));
        // 兜底: 即使拉取失败也给一个空 stages, 让 SupervisorPlanReview 仍可渲染
        setPlanStages([]);
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
      label: unlocked ? info.label : `${info.label} (待解锁)`,
      hint: unlocked ? info.hint : "请按顺序完成前一阶段后再进入。",
    };
  });

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
            {" · "}文件 {task.fileCount} · 长文本 {task.pastedCount} · slug:{" "}
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

        {activeStage === "brief" ? (
          task.mode === "codex-supervisor" ? (
            <>
              <SupervisorPlanReview
                onApprove={() => {
                  setPlanApproved(true);
                }}
                onReject={() => {
                  showToast("已否决计划，回到新任务选择。");
                  resetAll();
                }}
              />
              {planApproved ? (
                <BriefPanel
                  topic={task.message}
                  initialSnapshot={briefSnapshot}
                  onComplete={(b, snapshot) => {
                    setBriefResult(b);
                    setBriefSnapshot(snapshot);
                    setActiveStage("search");
                  }}
                />
              ) : planFetchError ? (
                <div className="task-brief__error" role="alert" data-testid="plan-fetch-error">
                  <strong>计划加载失败：</strong> {planFetchError}
                </div>
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

        {activeStage === "identification-audit" && executionResult ? (
          <IdentificationAuditPanel />
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
              className="btn btn--ghost"
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
              paper.pdf:{" "}
              <code data-testid="final-paper-path">{executionResult.paperPath}</code>
            </p>
            <p>
              results.json:{" "}
              <code data-testid="final-results-path">
                {executionResult.resultsPath}
              </code>
            </p>
            <p className="stage-panel__completion-hint">
              5 tab 走通完成，产物已落盘到项目目录，可以入库。
            </p>
          </div>
        ) : null}

        <div className="stage-panel__summary">
          <span>当前阶段</span>
          <strong>{STAGE_LABELS[activeStage].label}</strong>
          <p>{STAGE_LABELS[activeStage].hint}</p>
        </div>
      </section>
    </main>
  );
}
