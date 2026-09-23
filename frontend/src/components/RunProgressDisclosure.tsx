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
import { useMemo, useState } from 'react'
import { useT } from '../lib/i18n'
import {
  projectRunSteps,
  type RunProgressState,
  type RunStep,
} from '../lib/runSteps'

export interface RunProgressDisclosureProps {
  /** 当前 run 的短期观测；null 表示底栏没有正在运行的任务。 */
  progress: RunProgressState | undefined | null
  /** 可选外层样式；未知节点在展开详情保留原始技术标识以便核对。 */
  className?: string
}

function stepDotClass(status: RunStep['status']): string {
  if (status === 'done') return 'bg-wb-success border-wb-success'
  if (status === 'blocked') return 'bg-wb-warning border-wb-warning'
  return 'border-wb-primary wb-dot-running'
}

export default function RunProgressDisclosure({
  progress: runProgress,
  className,
}: RunProgressDisclosureProps) {
  const { t } = useT()
  const [open, setOpen] = useState(false)
  const progress = useMemo(
    () => projectRunSteps(runProgress?.events),
    [runProgress?.events],
  )

  if (!runProgress || !progress.hasSteps) return null

  const label = (step: RunStep) =>
    step.labelKey ? t(step.labelKey) : t('runStep.node.unknown')

  const activeText = progress.blockedStep
    ? t('runStep.summary.blocked', { step: label(progress.blockedStep) })
    : progress.latestUnresolvedStep
      ? progress.activeSteps.length > 1
        ? t('runStep.summary.activeMany', {
            step: label(progress.latestUnresolvedStep),
            n: progress.activeSteps.length - 1,
          })
        : label(progress.latestUnresolvedStep)
      : t('runStep.awaitingResult')

  return (
    <details
      data-testid="run-progress-disclosure"
      data-run-id={runProgress.runId}
      className={`group relative shrink-0 ${className || ''}`}
      onToggle={(event) => setOpen(event.currentTarget.open)}
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
        <span
          data-testid="run-progress-active"
          aria-live="polite"
          aria-atomic="true"
        >
          {activeText}
        </span>
        <span aria-hidden className="text-wb-faint">
          {open ? '−' : '＋'}
        </span>
        <span className="sr-only">
          {open ? t('runStep.collapse') : t('runStep.expand')}
        </span>
      </summary>

      <div
        data-testid="run-progress-steps"
        className="wb-pane-enter fixed inset-x-4 bottom-10 z-40 max-h-[min(60vh,420px)] overflow-y-auto rounded-md border border-wb-line bg-wb-surface p-3 shadow-sm sm:absolute sm:inset-x-auto sm:bottom-[calc(100%+0.5rem)] sm:left-0 sm:w-[360px]"
      >
        <p className="mb-2 font-sans text-[11px] text-wb-faint">{t('runStep.observed')}</p>
        {runProgress.truncated ? (
          <p
            data-testid="run-progress-truncated"
            className="mb-2 rounded border border-wb-warning/30 bg-wb-warning-soft px-2 py-1 font-sans text-[11px] text-wb-warning"
          >
            {t('runStep.truncated', { n: runProgress.omittedCount })}
          </p>
        ) : null}
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
              {!step.labelKey ? (
                <span className="font-mono text-[10px] text-wb-faint">{step.node}</span>
              ) : null}
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
