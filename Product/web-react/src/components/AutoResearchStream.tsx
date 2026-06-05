import { useCallback, useEffect, useRef, useState } from "react";
import { StepCard, type StepStatus } from "./StepCard";
import type { BriefResult, BriefStepsSnapshot } from "./BriefPanel";

/**
 * AutoResearchStream — auto-research mode brief tab panel.
 *
 * Mirrors BriefPanel's SSE consumption shape (step_start / step_delta /
 * step_done / final_brief / done / error) but skips the await_user
 * checkpoint: the backend auto-runs all 4 steps without pausing.
 *
 * BDD ref: docs/superpowers/specs/2026-06-04-brief-step-cards-design.md
 *          ui-gap-fill-bdd-2026-06-05.md §Task 42 behavior 2
 */

interface StepState {
  status: StepStatus;
  title: string;
  liveText: string;
  summary: string;
}

const STEP_TITLES: Record<1 | 2 | 3 | 4, string> = {
  1: "扫描题目意图",
  2: "匹配本地数据与文献",
  3: "拟定方法与变量",
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

interface AutoSseEvent {
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

export interface AutoResearchStreamProps {
  topic: string;
  topicSlug?: string;
  onComplete?: (brief: BriefResult, snapshot: BriefStepsSnapshot) => void;
}

export function AutoResearchStream({ topic, topicSlug, onComplete }: AutoResearchStreamProps) {
  const [phase, setPhase] = useState<"idle" | "running" | "completed" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<Record<1 | 2 | 3 | 4, StepState>>(INITIAL_STEPS);
  const [finalBrief, setFinalBrief] = useState<BriefResult | null>(null);
  const stepsRef = useRef<Record<1 | 2 | 3 | 4, StepState>>(steps);
  const finalBriefRef = useRef<BriefResult | null>(finalBrief);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    stepsRef.current = steps;
  }, [steps]);
  useEffect(() => {
    finalBriefRef.current = finalBrief;
  }, [finalBrief]);
  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  const updateStep = useCallback(
    (idx: 1 | 2 | 3 | 4, patch: Partial<StepState>) => {
      setSteps((prev) => ({ ...prev, [idx]: { ...prev[idx], ...patch } }));
    },
    []
  );

  const applyEvent = useCallback(
    (evt: AutoSseEvent) => {
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
          setSteps((prev) => ({
            ...prev,
            [idx]: {
              ...prev[idx],
              status: "done",
              summary: evt.summary || prev[idx].liveText,
            },
          }));
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
          setSteps((prev) => {
            const next = { ...prev };
            let changed = false;
            (Object.keys(next) as unknown as Array<keyof typeof next>).forEach((k) => {
              const step = next[k as 1 | 2 | 3 | 4];
              if (step.status === "running") {
                next[k as 1 | 2 | 3 | 4] = {
                  ...step,
                  status: "done",
                  summary: step.summary || step.liveText,
                };
                changed = true;
              }
            });
            return changed ? next : prev;
          });
          setPhase("completed");
          if (onComplete) {
            onComplete(
              {
                markdown: finalBriefRef.current?.markdown || "",
                path: finalBriefRef.current?.path || "",
                verdict: finalBriefRef.current?.verdict ?? false,
              },
              {
                steps: stepsRef.current,
                finalBrief: finalBriefRef.current,
              },
            );
          }
          break;
        }
        case "error": {
          setError(evt.message || "未知错误");
          setPhase("error");
          break;
        }
        default:
          break;
      }
    },
    [updateStep, onComplete]
  );

  const consumeSse = useCallback(
    async (url: string, body: object): Promise<AutoSseEvent[]> => {
      const collected: AutoSseEvent[] = [];
      abortRef.current?.abort();
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      const base = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";
      const fullUrl = url.startsWith("http") ? url : `${base}${url}`;
      const res = await fetch(fullUrl, {
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
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          buffer += decoder.decode();
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";
        for (const part of parts) {
          const dataLines = part.split("\n").filter((l) => l.startsWith("data: "));
          if (dataLines.length === 0) continue;
          const payload = dataLines.map((l) => l.slice(6)).join("\n");
          try {
            const evt: AutoSseEvent = JSON.parse(payload);
            collected.push(evt);
            applyEvent(evt);
          } catch {
            // ignore malformed
          }
        }
      }
      return collected;
    },
    [applyEvent]
  );

  const handleStart = useCallback(async () => {
    setPhase("running");
    setError(null);
    setSteps(INITIAL_STEPS);
    setFinalBrief(null);
    abortRef.current?.abort();
    try {
      await consumeSse("/api/auto-research/start", { topic, topic_slug: topicSlug });
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") return;
      setError(err instanceof Error ? err.message : String(err));
      setPhase("error");
    }
  }, [topic, topicSlug, consumeSse]);

  // Auto-start on mount: auto-research mode skips the "开始研究" button.
  useEffect(() => {
    if (phase === "idle" && topic.trim()) {
      void handleStart();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section aria-label="自动研究流" className="task-brief" data-testid="auto-research-stream">
      <div className="task-brief__main">
        <div className="task-brief__lead">
          <span className="eyebrow">自动探索模式</span>
          <h2>正在自动推进研究链路</h2>
          <p>研究题目：{topic || "（未填）"}</p>
          <p data-testid="auto-mode-hint">无需人工介入，4 步跑完自动进入 search tab。</p>
        </div>

        {phase === "error" && error && (
          <div className="task-brief__error" role="alert" data-testid="auto-research-error">
            <strong>错误：</strong> {error}
            <button type="button" className="btn btn--ghost" onClick={handleStart}>
              重试
            </button>
          </div>
        )}

        <div className="step-cards" data-testid="auto-step-cards">
          {([1, 2, 3, 4] as const).map((idx) => (
            <StepCard
              key={idx}
              stepIndex={idx}
              title={steps[idx].title}
              status={steps[idx].status}
              liveText={steps[idx].liveText}
              summary={steps[idx].summary}
            />
          ))}
        </div>

        {finalBrief && (
          <div className="task-brief__result" data-testid="auto-brief-result">
            <div className="task-brief__verdict">
              <span
                className={
                  finalBrief.verdict
                    ? "checklist-status-badge checklist-status-badge--ready"
                    : "checklist-status-badge checklist-status-badge--pending"
                }
                data-testid="auto-brief-verdict"
              >
                {finalBrief.verdict ? "verdict passed" : "verdict failed"}
              </span>
              <span className="task-brief__path">文件：{finalBrief.path}</span>
            </div>
            <pre
              className="task-brief__markdown"
              data-testid="auto-brief-markdown"
            >
              {finalBrief.markdown}
            </pre>
          </div>
        )}
      </div>
    </section>
  );
}

export default AutoResearchStream;
