import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "../lib/cn";

/** Tufte 风格：raw_output 截断到 N 字符避免页面失控。 */
const RAW_TRUNCATE_LIMIT = 800;

/**
 * 推理链可视化（D2 / Kimi 蜂群IDE 启发）。
 * 3 个 collapsible 段：1) 提示词 2) 原始 LLM 输出 3) 解析后 markdown。
 * 默认全部折叠 — 避免一次性把 1500+ 字的论文段展开遮住主 UI。
 */
export interface ReasoningChainViewProps {
  /** 喂给 LLM 的完整 prompt */
  prompt: string;
  /** LLM 返回的原始文本 */
  rawOutput: string;
  /** 解析后 / 落盘后的最终 markdown 段 */
  parsedOutput: string;
  /** 关联的 section_index（用于 data-testid 区分） */
  sectionIndex: number;
}

function truncate(s: string, n: number): string {
  if (s.length <= n) return s;
  return s.slice(0, n) + "...";
}

export function ReasoningChainView({
  prompt,
  rawOutput,
  parsedOutput,
  sectionIndex,
}: ReasoningChainViewProps) {
  const [openKey, setOpenKey] = useState<"prompt" | "raw" | "parsed" | null>(null);
  const toggle = (key: "prompt" | "raw" | "parsed") => {
    setOpenKey((prev) => (prev === key ? null : key));
  };

  const items: Array<{
    key: "prompt" | "raw" | "parsed";
    title: string;
    body: string;
    truncated: boolean;
  }> = [
    { key: "prompt", title: "1. 提示词", body: prompt, truncated: false },
    {
      key: "raw",
      title: "2. 原始输出",
      body: truncate(rawOutput, RAW_TRUNCATE_LIMIT),
      truncated: rawOutput.length > RAW_TRUNCATE_LIMIT,
    },
    { key: "parsed", title: "3. 解析后", body: parsedOutput, truncated: false },
  ];

  return (
    <div
      className="reasoning-chain"
      data-testid={`reasoning-chain-${sectionIndex}`}
    >
      <div className="reasoning-chain__header">推理链</div>
      {items.map((item) => {
        const isOpen = openKey === item.key;
        return (
          <details
            key={item.key}
            className="reasoning-chain__item"
            data-testid={`reasoning-chain-${sectionIndex}-${item.key}`}
            open={isOpen}
          >
            <summary
              onClick={(e) => {
                e.preventDefault();
                toggle(item.key);
              }}
              className="reasoning-chain__summary"
            >
              {isOpen ? (
                <ChevronDown size={14} />
              ) : (
                <ChevronRight size={14} />
              )}
              <span>{item.title}</span>
              {item.truncated ? (
                <span className="reasoning-chain__truncated-tag">
                  (截断)
                </span>
              ) : null}
            </summary>
            <pre
              className={cn(
                "reasoning-chain__body",
                item.key === "prompt" && "reasoning-chain__body--prompt",
              )}
            >
              {item.body}
            </pre>
          </details>
        );
      })}
      <style>{`
        .reasoning-chain {
          margin-top: 0.5rem;
          padding: 0.5rem 0.75rem;
          background: var(--color-panel-soft);
          border: 1px solid var(--color-line);
          border-radius: 6px;
          font-size: 0.8rem;
        }
        .reasoning-chain__header {
          font-weight: 600;
          color: var(--color-muted);
          margin-bottom: 0.4rem;
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .reasoning-chain__item {
          margin-bottom: 0.3rem;
        }
        .reasoning-chain__summary {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          cursor: pointer;
          list-style: none;
          color: var(--color-ink);
          padding: 0.2rem 0;
        }
        .reasoning-chain__summary::-webkit-details-marker {
          display: none;
        }
        .reasoning-chain__truncated-tag {
          font-size: 0.7rem;
          color: var(--color-muted);
          margin-left: 0.3rem;
        }
        .reasoning-chain__body {
          margin: 0.3rem 0 0.3rem 1.4rem;
          padding: 0.5rem;
          background: rgba(230, 230, 230, 0.04);
          border: 1px solid var(--color-line);
          border-radius: 4px;
          white-space: pre-wrap;
          word-break: break-word;
          font-family: ui-monospace, "SF Mono", Menlo, monospace;
          font-size: 0.75rem;
          max-height: 320px;
          overflow-y: auto;
          color: var(--color-ink);
        }
        .reasoning-chain__body--prompt {
          color: var(--color-muted);
        }
      `}</style>
    </div>
  );
}
