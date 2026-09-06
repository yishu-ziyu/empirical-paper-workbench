import type { ReactNode } from 'react'

export interface WorkspaceDecision {
  title: string
  reason: string
  actionLabel?: string
  onAction?: () => void
}

export interface WorkspaceSuggestion {
  title: string
  detail?: string
  actionLabel?: string
  onAction?: () => void
}

export interface WorkspaceDecisionRailProps {
  decision?: WorkspaceDecision | null
  waiting?: string | null
  suggestions?: WorkspaceSuggestion[]
  children?: ReactNode
}

/**
 * 下一步决策卡（契约 C5）：amber 语义色只给「需要你决定」的事；
 * 非阻塞建议收进 details。锚点 testid 与上一阶段保持一致。
 */
export default function WorkspaceDecisionRail({
  decision,
  waiting,
  suggestions = [],
  children,
}: WorkspaceDecisionRailProps) {
  return (
    <section data-testid="decision-rail" className="space-y-3">
      <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
        下一步
      </p>

      {decision ? (
        <article
          data-testid="decision-blocker"
          className="rounded-lg border border-wb-warning/35 bg-wb-warning-soft p-3"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-wb-warning">
            需要你确认
          </p>
          <h3 data-testid="decision-blocker-title" className="mt-1.5 text-[13px] font-medium text-wb-ink">
            {decision.title}
          </h3>
          <p data-testid="decision-blocker-reason" className="mt-1 text-[11.5px] leading-4 text-wb-muted">
            {decision.reason}
          </p>
          {decision.actionLabel && decision.onAction ? (
            <button
              type="button"
              data-testid="decision-blocker-action"
              onClick={decision.onAction}
              className="wb-press mt-2.5 rounded-md border border-wb-warning/40 bg-wb-surface px-2.5 py-1 text-[12px] text-wb-ink hover:bg-wb-warning-soft"
            >
              {decision.actionLabel}
            </button>
          ) : null}
        </article>
      ) : (
        <p data-testid="decision-rail-waiting" className="text-[12px] leading-5 text-wb-muted">
          {waiting || '当前没有阻塞决策。系统会在需要你介入时停下。'}
        </p>
      )}

      <details data-testid="decision-suggestions" className="rounded-lg border border-wb-line bg-wb-surface">
        <summary className="wb-press cursor-pointer px-3 py-2 text-[12px] text-wb-ink">
          非阻塞建议{suggestions.length ? ` · ${suggestions.length}` : ''}
        </summary>
        <div className="border-t border-wb-line px-3 py-2.5">
          {suggestions.length ? (
            <ul className="space-y-2.5">
              {suggestions.map((suggestion) => (
                <li key={suggestion.title} className="text-[12px] leading-4">
                  <p className="text-wb-ink">{suggestion.title}</p>
                  {suggestion.detail ? <p className="text-wb-muted">{suggestion.detail}</p> : null}
                  {suggestion.actionLabel && suggestion.onAction ? (
                    <button
                      type="button"
                      onClick={suggestion.onAction}
                      className="mt-0.5 text-wb-primary underline-offset-2 hover:underline"
                    >
                      {suggestion.actionLabel}
                    </button>
                  ) : null}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-[12px] leading-4 text-wb-muted">暂无建议，继续按当前研究路径推进。</p>
          )}
        </div>
      </details>

      {children}
    </section>
  )
}
