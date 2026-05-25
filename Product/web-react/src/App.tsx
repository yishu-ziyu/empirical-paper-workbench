import { useState } from "react";
import { DottedSurface } from "./components/DottedSurface";
import { ResearchCommandInput } from "./components/ResearchCommandInput";
import { SemanticGlowCards, type SemanticDraft } from "./components/SemanticGlowCards";
import { SlideTabs } from "./components/SlideTabs";
import { TaskBriefDemo } from "./components/TaskBriefDemo";
import { SupervisorPlanReview } from "./components/SupervisorPlanReview";
import { AgentActivityPanel } from "./components/AgentActivityPanel";

interface SubmittedResearchTask {
  message: string;
  mode: string;
  fileCount: number;
  pastedCount: number;
}

export function App() {
  const [task, setTask] = useState<SubmittedResearchTask | null>(null);
  const [draft, setDraft] = useState<SemanticDraft>({
    message: "",
    mode: "codex-supervisor",
    fileCount: 0,
    pastedCount: 0,
    hasMaterial: false,
  });
  const [analysisSeed, setAnalysisSeed] = useState<SemanticDraft | null>(null);
  const [activeStage, setActiveStage] = useState("brief");
  const [briefConfirmed, setBriefConfirmed] = useState(false);
  const [planApproved, setPlanApproved] = useState(false);
  const [executionStarted, setExecutionStarted] = useState(false);

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
            onDraftChange={setDraft}
            onSubmit={({ message, files, pastedContent, mode }) => {
              setAnalysisSeed({
                message,
                mode,
                fileCount: files.length,
                pastedCount: pastedContent.length,
                hasMaterial: true,
              });
              setTask({
                message,
                mode,
                fileCount: files.length,
                pastedCount: pastedContent.length,
              });
            }}
          />
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell analysis-workspace">
      <DottedSurface />
      <section className="analysis-workspace__header">
        <button
          className="analysis-workspace__back"
          type="button"
          onClick={() => {
            setTask(null);
            setAnalysisSeed(null);
            setActiveStage("brief");
            setBriefConfirmed(false);
            setPlanApproved(false);
            setExecutionStarted(false);
          }}
        >
          新任务
        </button>
        <div>
          <span className="eyebrow">分析工作台</span>
          <h1>{task.message || "附件驱动任务"}</h1>
          <p>
            模式：{task.mode} · 文件 {task.fileCount} · 长文本 {task.pastedCount}
          </p>
        </div>
      </section>

      <section className="stage-panel" aria-label="研究路径">
        <SlideTabs value={activeStage} onChange={setActiveStage} />
        {activeStage === "brief" ? (
          !briefConfirmed ? (
            <TaskBriefDemo
              draft={analysisSeed ?? draft}
              onApprove={() => setBriefConfirmed(true)}
            />
          ) : !planApproved ? (
            <SupervisorPlanReview
              onApprove={() => {
                setPlanApproved(true);
              }}
              onReject={() => {
                setBriefConfirmed(false);
              }}
            />
          ) : (
            <AgentActivityPanel
              executionStarted={executionStarted}
              onStartExecution={() => {
                setExecutionStarted(true);
              }}
              onBack={() => {
                setPlanApproved(false);
              }}
            />
          )
        ) : null}
        {activeStage !== "brief" ? <SemanticGlowCards draft={analysisSeed ?? draft} /> : null}
        <div className="stage-panel__summary">
          <span>当前阶段</span>
          <strong>
            {activeStage === "brief"
              ? !briefConfirmed
                ? "确认研究问题和边界"
                : !planApproved
                ? "审阅 Supervisor 规划路线"
                : "Agent 任务排队与真实执行阻断"
              : "拆解草案信号"}
          </strong>
          <p>
            {activeStage === "brief"
              ? !briefConfirmed
                ? "先确认任务书，再决定是否进入递归搜索、数据变量和方法设计。"
                : !planApproved
                ? "批准 Supervisor 规划路线后，将自动派发任务队列并阻断在执行前。"
                : executionStarted
                ? "真实执行授权已记录，后续由执行器把日志、产物和审计链写回队列。"
                : "确认真实执行范围后，再进入本地安全沙盒进行统计模型回归。"
              : "把输入信号拆为变量、方法和证据线索，供后续分析页接收。"}
          </p>
        </div>
      </section>
    </main>
  );
}
