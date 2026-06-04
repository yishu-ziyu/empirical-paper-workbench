import { useCallback, useEffect, useRef, useState } from "react";
import { StepCard, type StepStatus } from "./StepCard";

export interface BriefResult {
  markdown: string;
  path: string;
}

export interface BriefPanelProps {
  topic: string;
  onComplete?: (brief: BriefResult) => void;
}

interface StepState {
  status: StepStatus;
  title: string;
  liveText: string;
  summary: string;
}

type Phase = "idle" | "running" | "awaiting" | "completed" | "error";

const STEP_TITLES: Record<1 | 2 | 3 | 4, string> = {
  1: "分析研究问题",
  2: "映射文献缺口",
  3: "拟定贡献点",
  4: "写出研究简报",
};

const INITIAL_STEPS: Record<1 | 2 | 3 | 4, StepState> = {
  1: { status: "pending", title: STEP_TITLES[1], liveText: "", summary: "" },
  2: { status: "pending", title: STEP_TITLES[2], liveText: "", summary: "" },
  3: { status: "pending", title: STEP_TITLES[3], liveText: "", summary: "" },
  4: { status: "pending", title: STEP_TITLES[4], liveText: "", summary: "" },
};

function isStepIndex(n: unknown): n is 1 | 2 | 3 | 4 {
  return n === 1 || n === 2 || n === 3 || n === 4;
}

interface BriefSseEvent {
  event: string;
  step_index?: number;
  title?: string;
  text?: string;
  summary?: string;
  markdown?: string;
  brief_path?: string;
  verdict_passed?: boolean;
  message?: string;
}

/**
 * BriefPanel — 任务书 LLM 扩写面板 (L1 brief tab, Phase 1 step-cards).
 *
 * 行为契约 (ref: docs/superpowers/specs/2026-06-04-brief-step-cards-design.md):
 * - 点 "开始研究" → POST /api/brief SSE → 4 步流式播放
 * - 步骤 3 抵达时显示 3 个按钮 (继续/修改/重选)
 * - 用户决策 → POST /api/brief/resume SSE → 步骤 4 → final_brief → onComplete
 * - 任何 SSE 错误显示重试按钮
 */
export function BriefPanel({ topic, onComplete }: BriefPanelProps) {
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [finalBrief, setFinalBrief] = useState<{
    markdown: string;
    path: string;
    verdict: boolean;
  } | null>(null);
  // 保存 step 1-3 输出, 供 /resume 用
  const priorStepsRef = useRef<Record<string, string>>({});
  const abortRef = useRef<AbortController | null>(null);
  // 防止 step 3 按钮被双击 → 多次 POST /api/brief/resume
  const [resumeInFlight, setResumeInFlight] = useState(false);

  // 组件卸载时中止未完成的 SSE 请求, 避免在已卸载组件上 setState
  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  const updateStep = useCallback(
    (idx: 1 | 2 | 3 | 4, patch: Partial<StepState>) => {
      setSteps((prev) => ({ ...prev, [idx]: { ...prev[idx], ...patch } }));
    },
    []
  );

  const consumeSse = useCallback(
    async (url: string, body: object): Promise<BriefSseEvent[]> => {
      const collected: BriefSseEvent[] = [];
      // 中止上一次未完成的请求, 避免 zombie stream 污染新 state
      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: ctrl.signal,
      });
      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          // 刷新 decoder 里残留的 UTF-8 字节
          buffer += decoder.decode();
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";
        for (const part of parts) {
          // SSE spec: 同一事件可有多个 data: 行, 用 \n 拼接
          const dataLines = part.split("\n").filter((l) => l.startsWith("data: "));
          if (dataLines.length === 0) continue;
          const payload = dataLines.map((l) => l.slice(6)).join("\n");
          try {
            const evt: BriefSseEvent = JSON.parse(payload);
            collected.push(evt);
            applyEvent(evt);
          } catch {
            // ignore malformed
          }
        }
      }
      // Flush remaining buffered partial event (no trailing \n\n)
      const finalTail = buffer.trim();
      if (finalTail) {
        const dataLines = finalTail
          .split("\n")
          .filter((l) => l.startsWith("data: "));
        if (dataLines.length > 0) {
          const payload = dataLines.map((l) => l.slice(6)).join("\n");
          try {
            const evt: BriefSseEvent = JSON.parse(payload);
            collected.push(evt);
            applyEvent(evt);
          } catch {
            // ignore malformed tail
          }
        }
      }
      return collected;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const applyEvent = useCallback(
    (evt: BriefSseEvent) => {
      switch (evt.event) {
        case "step_start": {
          const idx = evt.step_index;
          if (!isStepIndex(idx)) return;
          updateStep(idx, {
            status: "running",
            title: evt.title || STEP_TITLES[idx],
            liveText: "",
          });
          break;
        }
        case "step_delta": {
          const idx = evt.step_index;
          if (!isStepIndex(idx)) return;
          setSteps((prev) => ({
            ...prev,
            [idx]: {
              ...prev[idx],
              liveText: prev[idx].liveText + (evt.text || ""),
            },
          }));
          break;
        }
        case "step_done": {
          const idx = evt.step_index;
          if (!isStepIndex(idx)) return;
          // 在 setState 之前捕获 liveText (reducer 应当是纯的)
          const captured = steps[idx].liveText;
          priorStepsRef.current[String(idx)] = captured;
          updateStep(idx, { status: "done", summary: evt.summary || "" });
          break;
        }
        case "await_user": {
          const idx = evt.step_index;
          if (!isStepIndex(idx)) return;
          updateStep(idx, { status: "awaiting" });
          setPhase("awaiting");
          break;
        }
        case "final_brief": {
          setFinalBrief({
            markdown: evt.markdown || "",
            path: evt.brief_path || "",
            verdict: evt.verdict_passed || false,
          });
          break;
        }
        case "done": {
          setPhase("completed");
          setResumeInFlight(false);
          break;
        }
        case "error": {
          setError(evt.message || "未知错误");
          setPhase("error");
          setResumeInFlight(false);
          break;
        }
        default:
          break;
      }
    },
    [updateStep, steps]
  );

  const handleStart = useCallback(async () => {
    setPhase("running");
    setError(null);
    setSteps(INITIAL_STEPS);
    setFinalBrief(null);
    priorStepsRef.current = {};
    setResumeInFlight(false);
    // 中止上一次未完成的请求 (防 zombie stream)
    abortRef.current?.abort();
    try {
      await consumeSse("/api/brief", { topic });
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        return; // 主动中止, 不算错误
      }
      setError(err instanceof Error ? err.message : String(err));
      setPhase("error");
      setResumeInFlight(false);
    }
  }, [topic, consumeSse]);

  const handleResume = useCallback(
    async (action: "continue" | "modify" | "reselect", userInput?: string) => {
      // 防止双击 → 多个 POST /resume 竞态
      if (resumeInFlight) return;
      setResumeInFlight(true);
      setPhase("running");
      // 中止上一次未完成的请求 (防 zombie stream)
      abortRef.current?.abort();
      try {
        const events = await consumeSse("/api/brief/resume", {
          topic,
          action,
          user_input: userInput,
          prior_steps: priorStepsRef.current,
        });
        const final = events.find((e) => e.event === "final_brief");
        if (final && final.verdict_passed && onComplete) {
          onComplete({ markdown: final.markdown || "", path: final.brief_path || "" });
        }
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          return; // 主动中止, 不算错误
        }
        setError(err instanceof Error ? err.message : String(err));
        setPhase("error");
      } finally {
        setResumeInFlight(false);
      }
    },
    [topic, consumeSse, onComplete, resumeInFlight]
  );

  return (
    <section aria-label="任务书扩写" className="task-brief">
      <div className="task-brief__main">
        <div className="task-brief__lead">
          <span className="eyebrow">第 1 阶段：研究简报</span>
          <h2>生成研究简报</h2>
          <p>研究题目：{topic || "（未填）"}</p>
        </div>

        <div className="task-brief__confirm-actions">
          <button
            type="button"
            className="btn btn--primary"
            onClick={handleStart}
            disabled={phase === "running" || phase === "awaiting" || !topic.trim()}
            data-testid="brief-start"
          >
            {phase === "running"
              ? "研究中…"
              : phase === "awaiting"
                ? "等你的决策"
                : "开始研究"}
          </button>
        </div>

        {phase === "error" && error && (
          <div className="task-brief__error" role="alert" data-testid="brief-error">
            <strong>错误：</strong> {error}
            <button type="button" className="btn btn--ghost" onClick={handleStart}>
              重试
            </button>
          </div>
        )}

        <div className="step-cards" data-testid="step-cards">
          {([1, 2, 3, 4] as const).map((idx) => (
            <StepCard
              key={idx}
              stepIndex={idx}
              title={steps[idx].title}
              status={steps[idx].status}
              liveText={steps[idx].liveText}
              summary={steps[idx].summary}
              onContinue={() => handleResume("continue")}
              onModify={(userInput) => handleResume("modify", userInput)}
              onReselect={() => handleResume("reselect")}
              disabled={resumeInFlight}
            />
          ))}
        </div>

        {finalBrief && (
          <div className="task-brief__result" data-testid="brief-result">
            <div className="task-brief__verdict">
              <span
                className={
                  finalBrief.verdict
                    ? "checklist-status-badge checklist-status-badge--ready"
                    : "checklist-status-badge checklist-status-badge--pending"
                }
                data-testid="brief-verdict"
              >
                {finalBrief.verdict ? "verdict passed" : "verdict failed"}
              </span>
              <span className="task-brief__path">文件：{finalBrief.path}</span>
            </div>
            <pre
              className="task-brief__markdown"
              data-testid="brief-markdown"
            >
              {finalBrief.markdown}
            </pre>
          </div>
        )}
      </div>
    </section>
  );
}

export default BriefPanel;
