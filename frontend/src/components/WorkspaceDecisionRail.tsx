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
 * 左栏只承载需要作者决定的下一件事；可选建议收在 details 里，
 * 章节导航继续沿用已有的 ChapterList，不改变写作状态来源。
 */
export default function WorkspaceDecisionRail({
  decision,
  waiting,
  suggestions = [],
  children,
}: WorkspaceDecisionRailProps) {
  return (
    <section data-testid="decision-rail" className="space-y-5">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
          研究工作台
        </p>
        <h2 className="mt-1 font-serif text-[1.1rem] leading-6 text-ink">
          对话 / 待确认决策
        </h2>
      </header>

      {decision ? (
        <article
          data-testid="decision-blocker"
          className="rounded-lg border border-warning/35 bg-warning/5 p-3"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-warning">
            需要你确认
          </p>
          <h3 data-testid="decision-blocker-title" className="mt-2 font-serif text-sm text-ink">
            {decision.title}
          </h3>
          <p data-testid="decision-blocker-reason" className="mt-1 text-xs leading-5 text-muted">
            {decision.reason}
          </p>
          {decision.actionLabel && decision.onAction ? (
            <button
              type="button"
              data-testid="decision-blocker-action"
              onClick={decision.onAction}
              className="mt-3 rounded-full border border-warning/40 bg-panel px-3 py-1.5 text-xs text-ink transition-colors hover:bg-warning/10"
            >
              {decision.actionLabel}
            </button>
          ) : null}
        </article>
      ) : (
        <p data-testid="decision-rail-waiting" className="text-xs leading-5 text-muted">
          {waiting || '当前没有阻塞决策。系统会在需要你介入时停下。'}
        </p>
      )}

      <details data-testid="decision-suggestions" className="rounded-lg border border-border bg-panel">
        <summary className="cursor-pointer px-3 py-2.5 text-xs text-ink">
          非阻塞建议{suggestions.length ? ` · ${suggestions.length}` : ''}
        </summary>
        <div className="border-t border-border px-3 py-3">
          {suggestions.length ? (
            <ul className="space-y-3">
              {suggestions.map((suggestion) => (
                <li key={suggestion.title} className="text-xs leading-5">
                  <p className="text-ink">{suggestion.title}</p>
                  {suggestion.detail ? <p className="text-muted">{suggestion.detail}</p> : null}
                  {suggestion.actionLabel && suggestion.onAction ? (
                    <button
                      type="button"
                      onClick={suggestion.onAction}
                      className="mt-1 text-accent hover:text-accent/80"
                    >
                      {suggestion.actionLabel}
                    </button>
                  ) : null}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs leading-5 text-muted">暂无建议，继续按当前研究路径推进。</p>
          )}
        </div>
      </details>

      {children}
    </section>
  )
}
