import { useState, useRef } from "react";
import { Play, FileText, CheckCircle2, Loader2, Activity } from "lucide-react";
import { cn } from "../lib/cn";
import { apiUrl } from "../lib/apiBase";
import { ReasoningChainView } from "./ReasoningChainView";
import { FormalPackageAcceptancePanel } from "./FormalPackageAcceptancePanel";
import { ServiceConnectionRecovery } from "./ServiceConnectionRecovery";

/** ExecuteEvent 6 种类型 + 必要字段（与 Product/types/research.py 一致）
 *  推理链字段（D2）：prompt/raw_output/parsed_output —— 由 section_done 事件携带
 */
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
  prompt?: string | null;
  raw_output?: string | null;
  parsed_output?: string | null;
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

const SERVICE_ERROR_MESSAGE =
  "服务暂时没连上，稍后重试。不会影响已保存的研究材料。";

/**
 * 把 fetch 的 ReadableStream 当作 SSE 消费，逐行解析 "data: {...}" 事件。
 * EventSource 不支持 POST，因此手动消费。
 *
 * 关键: 流结束时把 buffer 剩余内容(可能没有 trailing \n\n 的最后一条事件)flush 出去,
 * 否则后端 `data: {...done...}\n` 这类最后一行事件会被丢掉.
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
    if (done) {
      // Flush 残留 UTF-8 bytes
      buffer += decoder.decode();
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";
    for (const part of parts) {
      const dataLines = part.split("\n").filter((l) => l.startsWith("data: "));
      if (dataLines.length === 0) continue;
      const json = dataLines.map((l) => l.slice(6)).join("\n");
      try {
        onEvent(JSON.parse(json) as ExecuteEvent);
      } catch {
        // 跳过无法解析的行
      }
    }
  }
  // Tail flush: 处理流结束时 buffer 里残留的最后一条事件(无 \n\n 分隔)
  const tail = buffer.trim();
  if (tail) {
    const dataLines = tail.split("\n").filter((l) => l.startsWith("data: "));
    if (dataLines.length > 0) {
      const json = dataLines.map((l) => l.slice(6)).join("\n");
      try {
        onEvent(JSON.parse(json) as ExecuteEvent);
      } catch {
        // ignore malformed tail
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
    "点击「生成论文与结果包」后，系统会按论文结构生成草稿、PDF 和结果记录。"
  );
  const [statusStage, setStatusStage] = useState<string>("idle");
  const [paperPath, setPaperPath] = useState<string | null>(null);
  const [resultsPath, setResultsPath] = useState<string | null>(null);
  /** 推理链数据：每节 section_done 事件注入 prompt/raw_output/parsed_output。 */
  const [reasoningChains, setReasoningChains] = useState<
    Record<number, { prompt: string; rawOutput: string; parsedOutput: string }>
  >({});
  const completedRef = useRef(false);
  // Mirror paperPath in a ref so the SSE callback (closed over handleStart's
  // initial scope) can read the latest value when the `done` event fires.
  const paperPathRef = useRef<string | null>(null);

  async function handleStart() {
    if (running) return;
    setRunning(true);
    setError(null);
    setSections({});
    setReasoningChains({});
    setPaperPath(null);
    setResultsPath(null);
    completedRef.current = false;
    setStatusMessage("正在准备生成论文与结果包...");
    setStatusStage("connecting");

    try {
      const response = await fetch(apiUrl("/api/execute"), {
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
        throw new Error("execution_service_unavailable");
      }
      await consumeSSE(response, (evt) => {
        setStatusMessage(evt.message);
        setStatusStage(evt.stage);
        if (evt.event === "section_done" && evt.section_index != null) {
          setSections((prev) => ({ ...prev, [evt.section_index as number]: evt }));
          // 推理链捕获（D2）：prompt/raw_output/parsed_output 三件套
          if (evt.prompt || evt.raw_output || evt.parsed_output) {
            setReasoningChains((prev) => ({
              ...prev,
              [evt.section_index as number]: {
                prompt: evt.prompt ?? "",
                rawOutput: evt.raw_output ?? "",
                parsedOutput: evt.parsed_output ?? "",
              },
            }));
          }
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
          setError(SERVICE_ERROR_MESSAGE);
        }
      });
    } catch (e) {
      setError(SERVICE_ERROR_MESSAGE);
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
        <h2>论文生成</h2>
        <p className="execution-panel__subtitle">
          按论文结构生成正文、PDF 和结果记录；完成后进入识别审计。
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
              <Loader2 size={16} className="spin" /> 生成中...
            </>
          ) : (
            <>
              <Play size={16} /> 生成论文与结果包
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
          <ServiceConnectionRecovery message={error} onRetry={handleStart} />
        </div>
      )}

      {/* Agent 实时活动: 由 section_done 事件驱动, 显示 1-9 节的实时状态条。 */}
      {(running || sectionIndices.length > 0) && (
        <section
          className="execution-panel__activities"
          data-testid="execute-agent-activities"
        >
          <header className="execution-panel__activities-header">
            <Activity size={14} />
            <span>生成进度</span>
            <code data-testid="execute-agent-activities-count">
              {sectionIndices.length} / 9 已完成
            </code>
          </header>
          <ul className="execution-panel__activity-list">
            {Array.from({ length: 9 }, (_, i) => i + 1).map((idx) => {
              const done = sections[idx];
              // 推断当前正在写的节：最后一个 done + 1，仅在 running 时显示
              const maxDone = sectionIndices.length > 0
                ? sectionIndices[sectionIndices.length - 1]
                : 0;
              const isWriting = running && idx === maxDone + 1;
              const status = done
                ? "done"
                : isWriting
                ? "writing"
                : "pending";
              return (
                <li
                  key={idx}
                  className={cn(
                    "execution-panel__activity-row",
                    `is-${status}`
                  )}
                  data-testid={`execute-agent-activity-${idx}`}
                >
                  <span className="execution-panel__activity-icon">
                    {status === "done" ? (
                      <CheckCircle2 size={14} />
                    ) : status === "writing" ? (
                      <Loader2 size={14} className="spin" />
                    ) : (
                      <span className="execution-panel__activity-dot" />
                    )}
                  </span>
                  <span className="execution-panel__activity-name">
                    第 {idx} 节（{SECTION_TITLES[idx] ?? `第 ${idx} 节`}）
                  </span>
                  <span className="execution-panel__activity-status">
                    {status === "done"
                      ? "已完成"
                      : status === "writing"
                      ? "写入中..."
                      : "等待"}
                  </span>
                </li>
              );
            })}
          </ul>
        </section>
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
                    <CheckCircle2 size={14} /> 已完成
                  </>
                ) : running ? (
                  <>
                    <Loader2 size={14} className="spin" /> 生成中
                  </>
                ) : (
                  "—"
                )}
              </span>
            </li>
          );
        })}
      </ol>

      {/* D2 推理链可视化：每节一次，section_done 事件注入三件套。默认折叠。 */}
      {Object.keys(reasoningChains).length > 0 ? (
        <div className="execution-panel__chains" data-testid="execute-reasoning-chains">
          {Object.entries(reasoningChains)
            .sort(([a], [b]) => Number(a) - Number(b))
            .map(([idxStr, chain]) => {
              const idx = Number(idxStr);
              const title = SECTION_TITLES[idx] ?? `Section ${idx}`;
              return (
                <details
                  key={idx}
                  className="execution-panel__chain-block"
                  data-testid={`execute-chain-block-${idx}`}
                >
                  <summary className="execution-panel__chain-summary">
                    {title} · 推理链
                  </summary>
                  <ReasoningChainView
                    sectionIndex={idx}
                    prompt={chain.prompt}
                    rawOutput={chain.rawOutput}
                    parsedOutput={chain.parsedOutput}
                  />
                </details>
              );
            })}
        </div>
      ) : null}

      {allSectionsDone && paperPath && (
        <div
          className="execution-panel__result"
          data-testid="execute-paper-ready"
        >
          <FileText size={16} />
          <span>论文文件：&nbsp;</span>
          <code>{paperPath}</code>
        </div>
      )}

      {resultsPath && (
        <div className="execution-panel__result" data-testid="execute-done">
          <CheckCircle2 size={16} />
          <span>结果记录：&nbsp;</span>
          <code>{resultsPath}</code>
        </div>
      )}

      {/* 形式化产物验收: 9 节跑完且 paper.pdf + results.json 都已落盘时出现。
          projectId 复用 ExecutionPanel 的 topicSlug, 避免硬编码。
       */}
      {allSectionsDone && paperPath && resultsPath && (
        <section
          className="execution-panel__acceptance"
          data-testid="execute-formal-acceptance"
        >
          <header className="execution-panel__acceptance-header">
            <h3>形式化产物验收</h3>
            <p>人工核验论文、结果和可复现性 3 张卡，确认后进入正式产物。</p>
          </header>
          <FormalPackageAcceptancePanel projectId={topicSlug} />
        </section>
      )}

      <style>{`
        .execution-panel {
          padding: 1.25rem 1.5rem;
          background: rgba(230, 230, 230, 0.025);
          border: 1px solid var(--color-line);
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .execution-panel__chains {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .execution-panel__activities {
          display: flex;
          flex-direction: column;
          gap: 0.4rem;
          background: rgba(230, 230, 230, 0.045);
          border: 1px solid var(--color-line);
          border-radius: 8px;
          padding: 0.5rem 0.75rem;
        }
        .execution-panel__activities-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--color-strong);
        }
        .execution-panel__activities-header code {
          margin-left: auto;
          background: rgba(230, 230, 230, 0.08);
          color: var(--color-ink);
          padding: 0 0.4rem;
          border-radius: 4px;
          font-size: 0.75rem;
        }
        .execution-panel__activity-list {
          list-style: none;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .execution-panel__activity-row {
          display: grid;
          grid-template-columns: 18px 1fr auto;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.8rem;
          padding: 0.2rem 0.4rem;
          border-radius: 4px;
        }
        .execution-panel__activity-row.is-done {
          color: var(--color-strong);
        }
        .execution-panel__activity-row.is-writing {
          background: rgba(230, 230, 230, 0.075);
          color: var(--color-strong);
        }
        .execution-panel__activity-row.is-pending {
          color: var(--color-muted);
        }
        .execution-panel__activity-icon {
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }
        .execution-panel__activity-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--color-muted);
          display: inline-block;
        }
        .execution-panel__activity-status {
          font-size: 0.75rem;
          color: inherit;
          opacity: 0.85;
        }
        .execution-panel__acceptance {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          background: rgba(230, 230, 230, 0.045);
          border: 1px solid var(--color-line);
          border-radius: 8px;
          padding: 0.75rem 1rem;
        }
        .execution-panel__acceptance-header h3 {
          margin: 0;
          font-size: 1rem;
        }
        .execution-panel__acceptance-header p {
          margin: 0.2rem 0 0;
          font-size: 0.8rem;
          color: var(--color-muted);
        }
        .execution-panel__chain-block {
          background: rgba(230, 230, 230, 0.04);
          border: 1px solid var(--color-line);
          border-radius: 6px;
          padding: 0.4rem 0.6rem;
        }
        .execution-panel__chain-summary {
          cursor: pointer;
          font-size: 0.85rem;
          color: var(--color-ink);
          font-weight: 500;
          list-style: none;
        }
        .execution-panel__chain-summary::-webkit-details-marker {
          display: none;
        }
        .execution-panel__header h2 {
          margin: 0;
          font-size: 1.15rem;
        }
        .execution-panel__subtitle {
          margin: 0.25rem 0 0;
          font-size: 0.85rem;
          color: var(--color-muted);
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
          background: var(--color-button-primary-bg);
          color: var(--color-button-primary-ink);
          border: 1px solid var(--color-button-primary-bg);
          border-radius: 6px;
          padding: 0.5rem 0.9rem;
          cursor: pointer;
          font-size: 0.9rem;
        }
        .execution-panel__button:disabled {
          background: var(--color-button-disabled-bg);
          color: var(--color-button-disabled-text);
          border-color: var(--color-button-disabled-border);
          opacity: 1;
          cursor: not-allowed;
        }
        .execution-panel__button.is-running {
          background: rgba(230, 230, 230, 0.18);
          color: var(--color-strong);
        }
        .execution-panel__status {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: var(--color-muted);
        }
        .execution-panel__status code {
          background: rgba(230, 230, 230, 0.08);
          padding: 0 0.3rem;
          border-radius: 4px;
          font-size: 0.8rem;
        }
        .execution-panel__status-message {
          color: var(--color-ink);
        }
        .execution-panel__error {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: var(--color-danger);
          background: rgba(190, 80, 80, 0.06);
          border: 1px solid rgba(190, 80, 80, 0.22);
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
          background: rgba(230, 230, 230, 0.04);
          border: 1px solid var(--color-line);
          font-size: 0.85rem;
        }
        .execution-panel__section.is-done {
          background: rgba(230, 230, 230, 0.07);
          color: var(--color-strong);
        }
        .execution-panel__section.is-pending {
          background: rgba(230, 230, 230, 0.055);
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
          background: rgba(230, 230, 230, 0.055);
          color: var(--color-ink);
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
