/**
 * 分析中的次级披露：一句真实状态 + 可展开的真实路径。
 *
 * 对应 `docs/specs/frontend-interaction-current.md` §3 与审阅稿
 * `docs/design/progressive-research-flow/index.html` 的第 05 状态。
 *
 * 纪律：
 * - 只渲染后端真的发过的 `run.progress` 事件（`projectRunSteps`），没有事件就整个
 *   不出现 —— 不用定时器制造「看起来在忙」；
 * - 不做百分比、不做倒计时、不做「还剩 N 步」；
 * - 数字不 count-up（这里根本不显示数字）；
 * - 动效沿用现有 primitive：`wb-dot-running`（呼吸点）、`wb-pane-in`（进入）。
 */
import { useMemo } from 'react'
import { useT } from '../lib/i18n'
import type { RunProgressEvent } from '../lib/runEvents'
import { projectRunSteps, type RunStep } from '../lib/runSteps'

export interface RunProgressDisclosureProps {
  /** 本次 run 收到的真实事件（顺序即真实发生顺序） */
  events: RunProgressEvent[] | undefined | null
  /** 展开区里每一步的说明可以省略；默认给出「后端事件里的节点名」以保持可核对 */
  className?: string
}

function stepDotClass(status: RunStep['status']): string {
  if (status === 'done') return 'bg-wb-success border-wb-success'
  if (status === 'blocked') return 'bg-wb-warning border-wb-warning'
  return 'border-wb-primary wb-dot-running'
}

export default function RunProgressDisclosure({
  events,
  className,
}: RunProgressDisclosureProps) {
  const { t } = useT()
  const progress = useMemo(() => projectRunSteps(events), [events])

  if (!progress.hasSteps) return null

  const label = (step: RunStep) =>
    step.labelKey ? t(step.labelKey) : step.node

  const activeText = progress.activeNode
    ? label({ node: progress.activeNode, labelKey: progress.activeLabelKey, status: 'active' })
    : progress.blocked
      ? t('runStep.held')
      : t('runStep.settled')

  return (
    <details
      data-testid="run-progress-disclosure"
      className={`group relative ${className || ''}`}
    >
      <summary
        className="flex cursor-pointer list-none items-center gap-1.5 text-wb-muted hover:text-wb-ink [&::-webkit-details-marker]:hidden"
        data-testid="run-progress-summary"
      >
        <span
          aria-hidden
          className={`h-1.5 w-1.5 rounded-full ${
            progress.blocked
              ? 'bg-wb-warning'
              : progress.activeNode
                ? 'wb-dot-running bg-wb-primary'
                : 'bg-wb-success'
          }`}
        />
        <span data-testid="run-progress-active">{activeText}</span>
        <span aria-hidden className="text-wb-faint">
          ＋
        </span>
        <span className="sr-only">{t('runStep.expand')}</span>
      </summary>

      <div
        data-testid="run-progress-steps"
        className="wb-pane-enter fixed bottom-9 left-5 z-40 w-[min(360px,90vw)] rounded-md border border-wb-line bg-wb-surface p-3 shadow-sm"
      >
        <p className="mb-2 font-sans text-[11px] text-wb-faint">{t('runStep.observed')}</p>
        <ol className="wb-stagger space-y-1.5">
          {progress.steps.map((step) => (
            <li
              key={`${step.node}::${step.specId || ''}`}
              data-testid="run-progress-step"
              data-node={step.node}
              data-step-status={step.status}
              className="flex items-center gap-2 font-sans text-[12px]"
            >
              <span
                aria-hidden
                className={`h-1.5 w-1.5 shrink-0 rounded-full border ${stepDotClass(step.status)}`}
              />
              <span className={step.status === 'done' ? 'text-wb-muted' : 'text-wb-ink'}>
                {label(step)}
              </span>
              {step.specId ? (
                <span className="font-mono text-[10px] text-wb-faint">{step.specId}</span>
              ) : null}
              <span className="ml-auto font-mono text-[10px] text-wb-faint">
                {t(`runStep.status.${step.status}`)}
              </span>
            </li>
          ))}
        </ol>
      </div>
    </details>
  )
}
