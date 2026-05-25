import { useState } from "react";
import { ResearchCommandInput } from "./components/ResearchCommandInput";
import { SlideTabs } from "./components/SlideTabs";

interface SubmittedResearchTask {
  message: string;
  mode: string;
  fileCount: number;
  pastedCount: number;
}

export function App() {
  const [task, setTask] = useState<SubmittedResearchTask | null>(null);

  return (
    <main className="app-shell">
      <section className="start-panel">
        <div className="start-panel__heading">
          <span className="eyebrow">本地实证研究 OS</span>
          <h1>今天要推进什么研究？</h1>
          <p>先写题目，必要时附上数据、文献片段或方法要求。系统只进入草案层，不静默改写正式论文状态。</p>
        </div>
        <ResearchCommandInput
          onSubmit={({ message, files, pastedContent, mode }) =>
            setTask({
              message,
              mode,
              fileCount: files.length,
              pastedCount: pastedContent.length,
            })
          }
        />
      </section>

      <section className="stage-panel" aria-label="研究路径">
        <SlideTabs />
        <div className="stage-panel__summary">
          {task ? (
            <>
              <span>已接收</span>
              <strong>{task.message || "附件驱动任务"}</strong>
              <p>
                模式：{task.mode} · 文件 {task.fileCount} · 长文本 {task.pastedCount}
              </p>
            </>
          ) : (
            <>
              <span>等待任务书</span>
              <strong>输入题目后再展开后续判断</strong>
              <p>这个 React 切片目前只验证输入器和阶段导航，不展开 Agent 队列或审计面板。</p>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
