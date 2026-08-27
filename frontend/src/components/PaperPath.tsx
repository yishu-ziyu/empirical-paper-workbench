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
  if (status === 'completed' || status === 'active') return 'text-accent'
  if (status === 'paused') return 'text-warning'
  return 'text-ink'
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
    <section data-testid="paper-path" className="flex min-h-0 flex-col">
      <h2 className="mb-4 font-mono text-[12px] uppercase tracking-[0.16em] text-muted">
        {t('bench.steps')}
      </h2>
      <ol className="relative ml-1.5 border-l border-border">
        {PAPER_NODES.map((id) => {
          const status = nodes[id]
          const paused = status === 'paused'
          return (
            <li
              key={id}
              data-testid={`paper-path-${id}`}
              data-status={status}
              className={`relative pb-3 pl-5 ${status === 'paused' ? 'bg-warning/5' : ''}`}
            >
              <span
                aria-hidden
                className={`absolute -left-[5px] top-2 h-2.5 w-2.5 rounded-full ring-4 ring-cream ${dotClass(status)}`}
              />
              <button
                type="button"
                onClick={() => onSelect?.(id)}
                className="flex w-full items-baseline justify-between gap-2 py-0.5 text-left"
              >
                <span className={`font-mono text-[12px] leading-5 ${statusClass(status)}`}>
                  {t(`path.${id}`)}
                </span>
                {paused && (
                  <span className="shrink-0 font-mono text-[10px] text-warning">{t('path.paused')}</span>
                )}
              </button>
              {id === 'clean_data' && (
                <ol className="mt-1.5 space-y-1 border-l border-border pl-3">
                  {CLEAN_STEPS.map((step) => (
                    <li
                      key={step}
                      data-testid={`clean-step-${step}`}
                      data-status={clean[step]}
                      className={`font-mono text-[12px] leading-5 ${statusClass(clean[step])}`}
                    >
                      {t(`path.clean.${step}`)}
                      {clean[step] === 'paused' && (
                        <span className="ml-2 text-[10px] text-warning">{t('path.paused')}</span>
                      )}
                    </li>
                  ))}
                </ol>
              )}
            </li>
          )
        })}
      </ol>
    </section>
  )
}
