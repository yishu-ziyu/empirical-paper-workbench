import { useT } from '../lib/i18n'
import {
  CLEAN_STEPS,
  PAPER_NODES,
  derivePaperPath,
  type PaperNodeId,
  type PaperPathState,
  type PathStatus,
} from '../lib/paperPath'

export type { PaperPathState }

function statusClass(status: PathStatus): string {
  if (status === 'completed') return 'text-accent'
  if (status === 'active') return 'text-accent'
  if (status === 'paused') return 'text-warning'
  return 'text-muted'
}

function dotClass(status: PathStatus): string {
  if (status === 'completed') return 'bg-accent'
  if (status === 'active') return 'bg-accent animate-pulse-soft'
  if (status === 'paused') return 'bg-warning'
  return 'bg-border'
}

export interface PaperPathProps extends PaperPathState {
  onSelect?: (id: PaperNodeId) => void
}

export default function PaperPath({ onSelect, ...state }: PaperPathProps) {
  const { t } = useT()
  const { nodes, clean } = derivePaperPath(state)

  return (
    <section data-testid="paper-path">
      <h2 className="mb-3 font-mono text-xs uppercase tracking-wider text-muted">
        {t('bench.steps')}
      </h2>
      <ol className="flex flex-col gap-2">
        {PAPER_NODES.map((id) => {
          const status = nodes[id]
          const paused = status === 'paused'
          return (
            <li
              key={id}
              data-testid={`paper-path-${id}`}
              data-status={status}
              className="rounded-lg border border-border bg-panel px-3 py-2"
            >
              <button
                type="button"
                onClick={() => onSelect?.(id)}
                className="flex w-full items-start gap-2 text-left"
              >
                <span aria-hidden className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${dotClass(status)}`} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className={`font-mono text-[11px] leading-4 ${statusClass(status)}`}>
                      {t(`path.${id}`)}
                    </p>
                    {paused && (
                      <span className="shrink-0 font-mono text-[10px] text-warning">{t('path.paused')}</span>
                    )}
                  </div>
                  {id === 'clean_data' && (
                    <ol className="mt-2 space-y-1 border-l border-border pl-3">
                      {CLEAN_STEPS.map((step) => (
                        <li
                          key={step}
                          data-testid={`clean-step-${step}`}
                          data-status={clean[step]}
                          className={`font-mono text-[11px] leading-4 ${statusClass(clean[step])}`}
                        >
                          {t(`path.clean.${step}`)}
                          {clean[step] === 'paused' && (
                            <span className="ml-2 text-warning">{t('path.paused')}</span>
                          )}
                        </li>
                      ))}
                    </ol>
                  )}
                </div>
              </button>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
