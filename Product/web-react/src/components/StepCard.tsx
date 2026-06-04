import { Check, Edit3, Loader2, X, RotateCcw } from "lucide-react";
import { useState } from "react";
import { cn } from "../lib/cn";

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
  // 仅 step 3 awaiting 时用
  onContinue?: () => void;
  onModify?: (userInput: string) => void;
  onReselect?: () => void;
}

/**
 * StepCard — 单步研究日志卡片.
 *
 * 状态机:
 *   pending  → running  → done
 *   running  → error
 *   done     → (用户看 summary)
 *   awaiting → (用户点按钮) → done
 */
export function StepCard({
  stepIndex,
  title,
  status,
  liveText = "",
  summary = "",
  onContinue,
  onModify,
  onReselect,
}: StepCardProps) {
  const [showModifyInput, setShowModifyInput] = useState(false);
  const [userInput, setUserInput] = useState("");

  const isAwaiting = status === "awaiting" && stepIndex === 3;
  const showFullText = status === "running" || status === "done" || status === "error";

  return (
    <div
      className={cn("step-card", `step-card--${status}`)}
      data-testid={`step-card-${stepIndex}`}
      data-status={status}
    >
      <header className="step-card__head">
        <span className="step-card__index">步骤 {stepIndex}</span>
        <h3 className="step-card__title">{title}</h3>
        <span className="step-card__status" aria-live="polite">
          {status === "pending" && <span>⏳ 等待</span>}
          {status === "running" && (
            <span className="step-card__status--running">
              <Loader2 className="step-card__spinner" size={14} />
              思考中…
            </span>
          )}
          {status === "done" && (
            <span className="step-card__status--done">
              <Check size={14} /> 完成
            </span>
          )}
          {status === "awaiting" && <span>🛑 等你决策</span>}
          {status === "error" && (
            <span className="step-card__status--error">
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
            <pre className="step-card__live">
              {liveText}
              <span className="caret" />
            </pre>
          ) : (
            <p className="step-card__summary">{summary}</p>
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
                data-testid="step-3-continue"
              >
                <Check size={14} /> 继续
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => setShowModifyInput(true)}
                data-testid="step-3-modify"
              >
                <Edit3 size={14} /> 修改
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={onReselect}
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
                data-testid="step-3-modify-input"
                className="step-card__textarea"
              />
              <div className="step-card__modify-actions">
                <button
                  type="button"
                  className="btn btn--primary"
                  disabled={!userInput.trim()}
                  onClick={() => onModify?.(userInput.trim())}
                  data-testid="step-3-modify-submit"
                >
                  提交修改
                </button>
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => {
                    setShowModifyInput(false);
                    setUserInput("");
                  }}
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
