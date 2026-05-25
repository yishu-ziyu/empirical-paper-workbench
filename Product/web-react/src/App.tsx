import { useState } from "react";
import { DottedSurface } from "./components/DottedSurface";
import { ResearchCommandInput } from "./components/ResearchCommandInput";
import { SemanticGlowCards, type SemanticDraft } from "./components/SemanticGlowCards";
import { SlideTabs } from "./components/SlideTabs";
import { TaskBriefDemo } from "./components/TaskBriefDemo";

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
        {activeStage === "brief" ? <TaskBriefDemo draft={analysisSeed ?? draft} /> : null}
        {activeStage !== "brief" ? <SemanticGlowCards draft={analysisSeed ?? draft} /> : null}
        <div className="stage-panel__summary">
          <span>当前阶段</span>
          <strong>{activeStage === "brief" ? "确认研究问题和边界" : "拆解草案信号"}</strong>
          <p>
            {activeStage === "brief"
              ? "先确认任务书，再决定是否进入递归搜索、数据变量和方法设计。"
              : "这些卡片只用于讨论后续分析页形态，不写入正式研究状态。"}
          </p>
        </div>
      </section>
    </main>
  );
}
