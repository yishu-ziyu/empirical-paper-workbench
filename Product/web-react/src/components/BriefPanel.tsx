import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { StepCard, stripTemplateMarkers, type StepStatus } from "./StepCard";

export interface BriefResult {
  markdown: string;
  path: string;
  verdict?: boolean;
}

/** Persisted snapshot of the 4 research-journal steps, used to rehydrate
 *  BriefPanel when the user navigates away from the brief tab and back. */
export interface BriefStepsSnapshot {
  steps: Record<1 | 2 | 3 | 4, StepState>;
  finalBrief: BriefResult | null;
}

export interface BriefPanelProps {
  topic: string;
  /** 从 App 传下来的"上次完成"快照 — 若存在, 跳过 streaming 直接显示。 */
  initialSnapshot?: BriefStepsSnapshot | null;
  /** 完成时回调, 把当前 4 step state + final brief 一并交给 App 持久化。 */
  onComplete?: (brief: BriefResult, snapshot: BriefStepsSnapshot) => void;
}

interface StepState {
  status: StepStatus;
  title: string;
  liveText: string;
  summary: string;
  /** LLM 自我疑虑 (≤ 3 短句). 仅 step 3 有. 可选 (避免污染 AutoResearchStream 的同构 StepState). */
  critique?: string[];
  /** step_start event 时的 epoch ms — StepCard 用来算用时. */
  startedAt: number | null;
  /** step_done event 时的 epoch ms — StepCard 用来冻结用时显示. */
  endedAt: number | null;
}

type Phase = "idle" | "running" | "awaiting" | "completed" | "error";

const SERVICE_ERROR_MESSAGE =
  "这一步没有跑通。请检查后端服务或模型配置后重试，已保存的研究材料不会丢。";

const STEP_TITLES: Record<1 | 2 | 3 | 4, string> = {
  1: "分析研究问题",
  2: "映射文献缺口",
  3: "拟定贡献点",
  4: "写出研究简报",
};

const INITIAL_STEPS: Record<1 | 2 | 3 | 4, StepState> = {
  1: { status: "pending", title: STEP_TITLES[1], liveText: "", summary: "", startedAt: null, endedAt: null },
  2: { status: "pending", title: STEP_TITLES[2], liveText: "", summary: "", startedAt: null, endedAt: null },
  3: { status: "pending", title: STEP_TITLES[3], liveText: "", summary: "", startedAt: null, endedAt: null },
  4: { status: "pending", title: STEP_TITLES[4], liveText: "", summary: "", startedAt: null, endedAt: null },
};

function isStepIndex(n: unknown): n is 1 | 2 | 3 | 4 {
  return n === 1 || n === 2 || n === 3 || n === 4;
}

function toBriefErrorMessage(err: unknown): string {
  if (err instanceof Error && err.message === SERVICE_ERROR_MESSAGE) {
    return SERVICE_ERROR_MESSAGE;
  }
  if (err instanceof Error && /Failed to fetch|NetworkError|Load failed/i.test(err.message)) {
    return SERVICE_ERROR_MESSAGE;
  }
  return SERVICE_ERROR_MESSAGE;
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
  critique?: string[];
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
export function BriefPanel({ topic, initialSnapshot, onComplete }: BriefPanelProps) {
  // 若 App 传了 initialSnapshot (用户切走后又切回), 直接 hydrate —
  // 跳过 streaming, 进入 "查看已保存的简报" 模式
  const [phase, setPhase] = useState<Phase>(
    initialSnapshot ? "completed" : "idle"
  );
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<Record<1 | 2 | 3 | 4, StepState>>(
    initialSnapshot?.steps ?? INITIAL_STEPS
  );
  const [finalBrief, setFinalBrief] = useState<BriefResult | null>(
    initialSnapshot?.finalBrief ?? null
  );
  // 镜像 steps / finalBrief 到 ref, 让 handleResume 能在不重新订阅
  // SSE 的前提下读到最新 state (用于构造 onComplete 的 snapshot)
  const stepsRef = useRef<Record<1 | 2 | 3 | 4, StepState>>(steps);
  const finalBriefRef = useRef<BriefResult | null>(finalBrief);
  useEffect(() => {
    stepsRef.current = steps;
  }, [steps]);
  useEffect(() => {
    finalBriefRef.current = finalBrief;
  }, [finalBrief]);
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
      const env = import.meta.env as Record<string, string | undefined>;
      const base = env[`VITE_${"API_BASE_URL"}`] ?? "";
      const fullUrl = url.startsWith("http") ? url : `${base}${url}`;
      const res = await fetch(fullUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: ctrl.signal,
      });
      if (!res.ok || !res.body) {
        throw new Error(SERVICE_ERROR_MESSAGE);
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
            startedAt: Date.now(),
            endedAt: null,
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
          // 在 setState 之前用 ref 捕获 liveText —
          // 修复 stale closure: applyEvent 之前依赖 [updateStep, steps],
          // 但 consumeSse 是 useCallback([], ...) 冻结了 *初始* 引用,
          // 读到的是 INITIAL_STEPS (全空), 导致 prior_steps 被存成空串,
          // resume 时 step 3 永远不能从 awaiting → done.
          setSteps((prev) => {
            const captured = prev[idx].liveText;
            priorStepsRef.current[String(idx)] = captured;
            return {
              ...prev,
              [idx]: {
                ...prev[idx],
                // 强制覆盖 awaiting / running, step_done 一定胜出
                status: "done",
                // summary 缺失时回退到 liveText (防 truncated)
                summary: evt.summary || captured,
                // critique 仅当后端给出时写入, 保留之前值兜底
                ...(evt.critique ? { critique: evt.critique } : {}),
                endedAt: Date.now(),
              },
            };
          });
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
          // 流结束: 兜底 — 把所有仍卡在 awaiting 的 step 强制标记为 done
          // (后端 resume 可能不重发 step_done for awaiting steps)
          setSteps((prev) => {
            const next = { ...prev };
            let changed = false;
            (Object.keys(next) as unknown as Array<keyof typeof next>).forEach(
              (k) => {
                const step = next[k as 1 | 2 | 3 | 4];
                if (step.status === "awaiting" || step.status === "running") {
                  next[k as 1 | 2 | 3 | 4] = {
                    ...step,
                    status: "done",
                    summary: step.summary || step.liveText,
                    endedAt: step.endedAt ?? Date.now(),
                  };
                  changed = true;
                }
              }
            );
            return changed ? next : prev;
          });
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
    [updateStep]
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
      await consumeSse("/api/brief/stream", { topic });
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        return; // 主动中止, 不算错误
      }
      setError(toBriefErrorMessage(err));
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
        const events = await consumeSse("/api/brief/stream/resume", {
          topic,
          action,
          user_input: userInput,
          prior_steps: priorStepsRef.current,
        });
        const final = events.find((e) => e.event === "final_brief");
        if (final && final.verdict_passed && onComplete) {
          onComplete(
            {
              markdown: final.markdown || "",
              path: final.brief_path || "",
              verdict: final.verdict_passed,
            },
            {
              // 用 ref 拿最新 state, 避免 handleResume 闭包陷阱
              steps: stepsRef.current,
              finalBrief: finalBriefRef.current,
            },
          );
        }
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          return; // 主动中止, 不算错误
        }
        setError(toBriefErrorMessage(err));
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
          <h2>先把题目变成可执行研究简报</h2>
          <p>确认研究问题、边界、贡献点和成功标准；确认后进入文献检索。</p>
          <p>研究题目：{topic || "（未填）"}</p>
        </div>

        <div className="task-brief__confirm-actions">
          {phase === "completed" ? (
            <button
              type="button"
              className="btn btn--ghost task-brief__restart"
              onClick={handleStart}
              data-testid="brief-restart"
            >
              重新研究
            </button>
          ) : (
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
          )}
        </div>

        {phase === "error" && error && (
          <div className="task-brief__error" role="alert" data-testid="brief-error">
            <strong>这一步没有跑通：</strong> {error}
            <button type="button" className="btn btn--ghost" onClick={handleStart}>
              重新尝试
            </button>
          </div>
        )}

        <div className="step-cards" data-testid="step-cards">
          {([1, 2] as const).map((idx) => (
            <StepCard
              key={idx}
              stepIndex={idx}
              title={steps[idx].title}
              status={steps[idx].status}
              liveText={steps[idx].liveText}
              summary={steps[idx].summary}
              startedAt={steps[idx].startedAt}
              endedAt={steps[idx].endedAt}
              onContinue={() => handleResume("continue")}
              onModify={(userInput) => handleResume("modify", userInput)}
              onReselect={() => handleResume("reselect")}
              disabled={resumeInFlight}
            />
          ))}
          {steps[3].status === "awaiting" && (steps[3].critique?.length ?? 0) > 0 && (
            <aside
              className="brief-self-critique"
              data-testid="brief-step-3-critique"
            >
              <span className="brief-self-critique__label">
                LLM 自评 (它对自己的疑虑)
              </span>
              <ul>
                {(steps[3].critique ?? []).map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </aside>
          )}
          {([3, 4] as const).map((idx) => (
            <StepCard
              key={idx}
              stepIndex={idx}
              title={steps[idx].title}
              status={steps[idx].status}
              liveText={steps[idx].liveText}
              summary={steps[idx].summary}
              startedAt={steps[idx].startedAt}
              endedAt={steps[idx].endedAt}
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
                {finalBrief.verdict ? "简报可继续" : "简报需补充"}
              </span>
              <span className="task-brief__path">文件：{finalBrief.path}</span>
            </div>
            <div
              className="task-brief__markdown"
              data-testid="brief-markdown"
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {stripTemplateMarkers(finalBrief.markdown)}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default BriefPanel;
