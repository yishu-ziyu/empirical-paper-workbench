import { useState } from "react";
import { DottedSurface } from "./components/DottedSurface";
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
      <DottedSurface />
      <section className="start-panel">
        <div className="start-panel__heading">
          <span className="eyebrow">本地实证研究 OS</span>
          <h1>今天要推进什么研究？</h1>
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
              <p>任务建立后，再进入数据、方法和执行。</p>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
