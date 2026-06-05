import { Check, Edit3, Loader2, X, RotateCcw, Sparkles, Clock3, Hash } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "../lib/cn";

/**
 * Strip LLM-leaked template markers from streaming/final text:
 *  - `### 步骤 N: title`  (v4 prompt header the model sometimes echoes)
 *  - `---`               (markdown horizontal rules)
 *  - leading/trailing whitespace
 *
 * 渲染前调用, 保证 ReactMarkdown 不会把 `### 步骤 3` 当成 H3 显示.
 */
export function stripTemplateMarkers(s: string): string {
  return s
    .replace(/^###\s*步骤\s*\d+[^\n]*$/gm, "")
    .replace(/^---\s*$/gm, "")
    .replace(/^\s+|\s+$/g, "");
}

/** 把毫秒用时格式化为 "12s" / "1m23s" — 比 Date.now diff 更易读. */
export function formatElapsed(ms: number): string {
  const s = Math.max(0, Math.floor(ms / 1000));
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  return `${m}m${(s % 60).toString().padStart(2, "0")}s`;
}

/** 中文字符数 = CJK 字符 + ASCII 词, 排除 markdown 标点和空白.
 *  用户更在意"内容增量"而不是字符数, 但中文字符 + markdown 标点是最直观的"流长度"指标. */
export function countMeaningfulChars(s: string): number {
  // 去掉 markdown 模板标记 (避免 step title 重复计数)
  const cleaned = stripTemplateMarkers(s);
  // CJK 字符按字数计; 英文按 word count; 不算空白/标点
  const cjk = (cleaned.match(/[一-鿿㐀-䶿]/g) || []).length;
  const words = (cleaned.match(/[A-Za-z0-9]+/g) || []).length;
  return cjk + words;
}

/** 每步的"阶段副标题" — BriefPanel 跑 LLM 时, step 1 内部还有 5 段, 但用户只想知道
 *  "现在大致在干什么". 这是高层级的人类可读描述, 跟 streaming delta 无关. */
const STEP_PHASE_LABEL: Record<1 | 2 | 3 | 4, string> = {
  1: "拆解研究问题 · 识别关键变量",
  2: "扫描文献缺口 · 找差异化空间",
  3: "拟出 3 个边际贡献点",
  4: "把分析写成可执行简报",
};

export type StepStatus =
  | "pending"
  | "running"
  | "done"
  | "awaiting"
  | "error";

export interface StepCardProps {
  stepIndex: 1 | 2 | 3 | 4;
  title: string;
  status: StepStatus;
  liveText?: string;
  summary?: string;
  /** step_start 事件触发时的 epoch ms, 用于计算用时. */
  startedAt?: number | null;
  /** step_done 事件触发时的 epoch ms, 用于显示"完成用时". */
  endedAt?: number | null;
  // 仅 step 3 awaiting 时用
  onContinue?: () => void;
  onModify?: (userInput: string) => void;
  onReselect?: () => void;
  disabled?: boolean;
}

/**
 * StepCard — 单步研究日志卡片.
 *
 * 状态机:
 *   pending  → running  → done
 *   running  → error
 *   done     → (用户看 summary)
 *   awaiting → (用户点按钮) → done
 *
 * 可视化约定 (v2 — 2026-06-05 用户反馈 "可视化还是不够清楚" 后):
 *   pending  → 灰色 placeholder 行 + 序号徽章
 *   running  → 顶部: 圆点 + 标题 + 用时 (每秒刷新) + 字符数
 *            → 中部: live text + 闪烁 caret (有内容) 或 skeleton 占位 (无内容)
 *   done     → 顶部: 绿色对勾 + 标题 + "用时 Xs · 字符 N"
 *            → 中部: summary 渲染为 markdown
 *   awaiting → step 3 专属: 三个决策按钮
 *   error    → 红色 X + 错误
 */
export function StepCard({
  stepIndex,
  title,
  status,
  liveText = "",
  summary = "",
  startedAt = null,
  endedAt = null,
  onContinue,
  onModify,
  onReselect,
  disabled = false,
}: StepCardProps) {
  const [showModifyInput, setShowModifyInput] = useState(false);
  const [userInput, setUserInput] = useState("");

  const isAwaiting = status === "awaiting" && stepIndex === 3;
  const showFullText = status === "running" || status === "done" || status === "error";

  // 用时 — running 时每秒刷新; done 时冻结在 endedAt
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (status !== "running") return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [status]);

  const elapsedMs = useMemo(() => {
    if (!startedAt) return 0;
    const end = status === "running" ? now : endedAt ?? now;
    return Math.max(0, end - startedAt);
  }, [startedAt, endedAt, now, status]);

  // 显示字符数 — running 用 liveText (实时的), done 用 summary
  const charCount = useMemo(() => {
    const src = status === "done" ? (summary || liveText) : liveText;
    return countMeaningfulChars(src);
  }, [status, summary, liveText]);

  return (
    <div
      className={cn("step-card", `step-card--${status}`)}
      data-testid={`step-card-${stepIndex}`}
      data-status={status}
    >
      <header className="step-card__head">
        <span className="step-card__index">步骤 {stepIndex}</span>
        <h3 className="step-card__title">{title}</h3>
        {status === "running" && startedAt && (
          <span className="step-card__phase" aria-live="polite">
            <Sparkles size={12} className="step-card__phase-icon" />
            {STEP_PHASE_LABEL[stepIndex]}
          </span>
        )}
        <span className="step-card__status" aria-live="polite">
          {status === "pending" && <span className="step-card__pill step-card__pill--pending">⏳ 等待</span>}
          {status === "running" && (
            <span className="step-card__pill step-card__pill--running" data-testid={`step-card-${stepIndex}-elapsed`}>
              <Loader2 className="step-card__spinner" size={14} />
              <span>思考中</span>
              <span className="step-card__metric">
                <Clock3 size={11} />
                {formatElapsed(elapsedMs)}
              </span>
              <span className="step-card__metric" data-testid={`step-card-${stepIndex}-chars`}>
                <Hash size={11} />
                {charCount}
              </span>
            </span>
          )}
          {status === "done" && (
            <span className="step-card__pill step-card__pill--done">
              <Check size={14} />
              <span>完成</span>
              {startedAt && endedAt && (
                <span className="step-card__metric" data-testid={`step-card-${stepIndex}-elapsed`}>
                  <Clock3 size={11} />
                  {formatElapsed(endedAt - startedAt)}
                </span>
              )}
              {charCount > 0 && (
                <span className="step-card__metric" data-testid={`step-card-${stepIndex}-chars`}>
                  <Hash size={11} />
                  {charCount}
                </span>
              )}
            </span>
          )}
          {status === "awaiting" && (
            <span className="step-card__pill step-card__pill--awaiting">🛑 等你决策</span>
          )}
          {status === "error" && (
            <span className="step-card__pill step-card__pill--error">
              <X size={14} /> 失败
            </span>
          )}
        </span>
      </header>

      {showFullText && (
        <div
          className="step-card__body"
          data-testid={`step-card-${stepIndex}-body`}
        >
          {status === "running" ? (
            liveText ? (
              <pre className="step-card__live">
                {stripTemplateMarkers(liveText)}
                <span className="caret" />
              </pre>
            ) : (
              // skeleton: liveText 为空时, 给用户 "agent 在准备第一段" 的视觉
              <div className="step-card__skeleton" data-testid={`step-card-${stepIndex}-skeleton`}>
                <div className="step-card__skeleton-line" style={{ width: "92%" }} />
                <div className="step-card__skeleton-line" style={{ width: "78%" }} />
                <div className="step-card__skeleton-line" style={{ width: "84%" }} />
                <div className="step-card__skeleton-line" style={{ width: "60%" }} />
              </div>
            )
          ) : (
            <div className="step-card__summary">
              {(() => {
                // done 时优先显示 backend 给的 summary;
                // 若 summary 为空, 回退到 streaming 累积的 liveText (防 truncated)
                const text = stripTemplateMarkers(summary || liveText);
                return text ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {text}
                  </ReactMarkdown>
                ) : null;
              })()}
            </div>
          )}
        </div>
      )}

      {isAwaiting && (
        <div className="step-card__actions" data-testid="step-3-actions">
          {!showModifyInput && (
            <div className="step-card__buttons">
              <button
                type="button"
                className="btn btn--primary"
                onClick={onContinue}
                disabled={disabled}
                data-testid="step-3-continue"
              >
                <Check size={14} /> 继续
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => !disabled && setShowModifyInput(true)}
                disabled={disabled}
                data-testid="step-3-modify"
              >
                <Edit3 size={14} /> 修改
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={onReselect}
                disabled={disabled}
                data-testid="step-3-reselect"
              >
                <RotateCcw size={14} /> 重选
              </button>
            </div>
          )}
          {showModifyInput && (
            <div className="step-card__modify">
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="告诉 LLM 怎么调整这 3 个贡献点…"
                rows={3}
                disabled={disabled}
                data-testid="step-3-modify-input"
                className="step-card__textarea"
              />
              <div className="step-card__modify-actions">
                <button
                  type="button"
                  className="btn btn--primary"
                  disabled={disabled || !userInput.trim()}
                  onClick={() => !disabled && onModify?.(userInput.trim())}
                  data-testid="step-3-modify-submit"
                >
                  提交修改
                </button>
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => {
                    if (disabled) return;
                    setShowModifyInput(false);
                    setUserInput("");
                  }}
                  disabled={disabled}
                >
                  取消
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default StepCard;
