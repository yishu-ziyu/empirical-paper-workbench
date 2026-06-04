import { useState, useRef } from "react";
import { Play, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { cn } from "../lib/cn";

/** ExecuteEvent 6 种类型 + 必要字段（与 Product/types/research.py 一致） */
export type ExecuteEventType =
  | "start"
  | "progress"
  | "section_done"
  | "paper_ready"
  | "done"
  | "error";

export interface ExecuteEvent {
  event: ExecuteEventType;
  stage: string;
  message: string;
  section_index?: number | null;
  paper_pdf_path?: string | null;
  results_json_path?: string | null;
}

export interface ExecutionPanelProps {
  briefPath: string;
  variablesPath: string;
  designPath: string;
  topicSlug: string;
  /** 完成时回调（paper.pdf 路径 + results.json 路径） */
  onComplete?: (paperPath: string, resultsPath: string) => void;
}

const SECTION_TITLES: Record<number, string> = {
  1: "1. 引言",
  2: "2. 文献综述",
  3: "3. 制度背景",
  4: "4. 数据",
  5: "5. 实证策略",
  6: "6. 主结果",
  7: "7. 稳健性检验",
  8: "8. 结论",
  9: "9. 参考文献",
};

/**
 * 把 fetch 的 ReadableStream 当作 SSE 消费，逐行解析 "data: {...}" 事件。
 * EventSource 不支持 POST，因此手动消费。
 */
async function consumeSSE(
  response: Response,
  onEvent: (e: ExecuteEvent) => void
): Promise<void> {
  if (!response.body) {
    throw new Error("response.body is null — SSE not supported");
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";
    for (const part of parts) {
      const line = part.trim();
      if (line.startsWith("data: ")) {
        const json = line.slice(6);
        try {
          onEvent(JSON.parse(json) as ExecuteEvent);
        } catch {
          // 跳过无法解析的行
        }
      }
    }
  }
}

export function ExecutionPanel({
  briefPath,
  variablesPath,
  designPath,
  topicSlug,
  onComplete,
}: ExecutionPanelProps) {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  /** section_index -> 最后一个 section_done 事件（用于列表展示） */
  const [sections, setSections] = useState<Record<number, ExecuteEvent>>({});
  const [statusMessage, setStatusMessage] = useState<string>(
    "点击「开始跑」以流式生成 9 节论文 + paper.pdf + results.json"
  );
  const [statusStage, setStatusStage] = useState<string>("idle");
  const [paperPath, setPaperPath] = useState<string | null>(null);
  const [resultsPath, setResultsPath] = useState<string | null>(null);
  const completedRef = useRef(false);
  // Mirror paperPath in a ref so the SSE callback (closed over handleStart's
  // initial scope) can read the latest value when the `done` event fires.
  const paperPathRef = useRef<string | null>(null);

  async function handleStart() {
    if (running) return;
    setRunning(true);
    setError(null);
    setSections({});
    setPaperPath(null);
    setResultsPath(null);
    completedRef.current = false;
    setStatusMessage("正在打开 SSE 流...");
    setStatusStage("connecting");

    try {
      const response = await fetch("/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic_slug: topicSlug,
          brief_path: briefPath,
          variables_path: variablesPath,
          design_path: designPath,
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      await consumeSSE(response, (evt) => {
        setStatusMessage(evt.message);
        setStatusStage(evt.stage);
        if (evt.event === "section_done" && evt.section_index != null) {
          setSections((prev) => ({ ...prev, [evt.section_index as number]: evt }));
        } else if (evt.event === "paper_ready" && evt.paper_pdf_path) {
          setPaperPath(evt.paper_pdf_path);
          paperPathRef.current = evt.paper_pdf_path;
        } else if (evt.event === "done" && evt.results_json_path) {
          setResultsPath(evt.results_json_path);
          if (
            !completedRef.current &&
            paperPathRef.current &&
            evt.results_json_path
          ) {
            completedRef.current = true;
            onComplete?.(paperPathRef.current, evt.results_json_path);
          }
        } else if (evt.event === "error") {
          setError(evt.message);
        }
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
    } finally {
      setRunning(false);
    }
  }

  const sectionIndices = Object.keys(sections)
    .map((k) => Number(k))
    .sort((a, b) => a - b);
  const allSectionsDone = sectionIndices.length === 9;

  return (
    <div className="execution-panel">
      <header className="execution-panel__header">
        <h2>执行实验</h2>
        <p className="execution-panel__subtitle">
          按 9 节顺序写作、引言 → 参考文献，最终拼成 paper.pdf 并落盘 results.json
        </p>
      </header>

      <div className="execution-panel__controls">
        <button
          type="button"
          onClick={handleStart}
          disabled={running}
          className={cn("execution-panel__button", running && "is-running")}
          data-testid="execute-start"
        >
          {running ? (
            <>
              <Loader2 size={16} className="spin" /> 正在跑...
            </>
          ) : (
            <>
              <Play size={16} /> 开始跑
            </>
          )}
        </button>
        <div className="execution-panel__status">
          <span className="execution-panel__status-label">状态：</span>
          <code>{statusStage}</code>
          <span className="execution-panel__status-message">{statusMessage}</span>
        </div>
      </div>

      {error && (
        <div className="execution-panel__error" data-testid="execute-error">
          <AlertCircle size={16} /> {error}
        </div>
      )}

      <ol className="execution-panel__sections" data-testid="execute-sections">
        {Array.from({ length: 9 }, (_, i) => i + 1).map((idx) => {
          const done = sections[idx];
          return (
            <li
              key={idx}
              className={cn(
                "execution-panel__section",
                done && "is-done",
                running && !done && "is-pending"
              )}
              data-testid={`execute-section-${idx}`}
            >
              <span className="execution-panel__section-title">
                {SECTION_TITLES[idx] ?? `Section ${idx}`}
              </span>
              <span className="execution-panel__section-state">
                {done ? (
                  <>
                    <CheckCircle2 size={14} /> done
                  </>
                ) : running ? (
                  <>
                    <Loader2 size={14} className="spin" /> writing
                  </>
                ) : (
                  "—"
                )}
              </span>
            </li>
          );
        })}
      </ol>

      {allSectionsDone && paperPath && (
        <div
          className="execution-panel__result"
          data-testid="execute-paper-ready"
        >
          <FileText size={16} />
          <span>Paper ready:&nbsp;</span>
          <code>{paperPath}</code>
        </div>
      )}

      {resultsPath && (
        <div className="execution-panel__result" data-testid="execute-done">
          <CheckCircle2 size={16} />
          <span>Results:&nbsp;</span>
          <code>{resultsPath}</code>
        </div>
      )}

      <style>{`
        .execution-panel {
          padding: 1.25rem 1.5rem;
          background: #fafafa;
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .execution-panel__header h2 {
          margin: 0;
          font-size: 1.15rem;
        }
        .execution-panel__subtitle {
          margin: 0.25rem 0 0;
          font-size: 0.85rem;
          color: #666;
        }
        .execution-panel__controls {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .execution-panel__button {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          background: #1f2937;
          color: white;
          border: none;
          border-radius: 6px;
          padding: 0.5rem 0.9rem;
          cursor: pointer;
          font-size: 0.9rem;
        }
        .execution-panel__button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .execution-panel__button.is-running {
          background: #374151;
        }
        .execution-panel__status {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: #555;
        }
        .execution-panel__status code {
          background: #e5e7eb;
          padding: 0 0.3rem;
          border-radius: 4px;
          font-size: 0.8rem;
        }
        .execution-panel__status-message {
          color: #444;
        }
        .execution-panel__error {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #b91c1c;
          background: #fee2e2;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
          font-size: 0.9rem;
        }
        .execution-panel__sections {
          list-style: none;
          margin: 0;
          padding: 0;
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
          gap: 0.5rem;
        }
        .execution-panel__section {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.5rem;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
          background: #f3f4f6;
          font-size: 0.85rem;
        }
        .execution-panel__section.is-done {
          background: #ecfdf5;
          color: #047857;
        }
        .execution-panel__section.is-pending {
          background: #fef3c7;
        }
        .execution-panel__section-state {
          display: inline-flex;
          align-items: center;
          gap: 0.3rem;
          font-size: 0.75rem;
        }
        .execution-panel__result {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #ecfdf5;
          color: #065f46;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
          font-size: 0.85rem;
        }
        .execution-panel__result code {
          font-size: 0.75rem;
          word-break: break-all;
        }
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
