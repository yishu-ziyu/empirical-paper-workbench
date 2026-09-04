import { useState } from 'react'

export interface SubmissionStatusProps {
  canExport: boolean
  blockers: string[]
  passed: string[]
  onGenerate: () => void
}

/** 论文提交包状态：条件来自现有工作区状态，最终动作仍交给导出对话框。 */
export default function SubmissionStatus({
  canExport,
  blockers,
  passed,
  onGenerate,
}: SubmissionStatusProps) {
  const [open, setOpen] = useState(false)

  return (
    <section
      data-testid="submission-status"
      className="mb-5 rounded-lg border border-border bg-panel px-4 py-3"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        {canExport ? (
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-accent">提交状态</p>
            <p className="mt-1 font-serif text-sm text-ink">生成提交包</p>
          </div>
        ) : (
          <button
            type="button"
            data-testid="submission-toggle"
            aria-expanded={open}
            onClick={() => setOpen((value) => !value)}
            className="text-left"
          >
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-warning">提交状态</p>
            <p className="mt-1 font-serif text-sm text-ink">暂不可提交 · {blockers.length}</p>
          </button>
        )}
        {canExport ? (
          <button
            type="button"
            data-testid="submission-generate"
            onClick={onGenerate}
            className="rounded-full bg-accent px-3.5 py-1.5 text-xs text-white transition-colors hover:bg-accent/90"
          >
            生成提交包
          </button>
        ) : (
          <span className="text-xs text-muted">点击查看条件</span>
        )}
      </div>

      {!canExport && open ? (
        <div data-testid="submission-details" className="mt-3 grid gap-3 border-t border-border pt-3 text-xs sm:grid-cols-2">
          <div>
            <h3 className="font-medium text-warning">还差这些条件</h3>
            <ul className="mt-1 space-y-1 leading-5 text-muted">
              {blockers.map((blocker) => (
                <li key={blocker} data-testid="submission-blocker">{blocker}</li>
              ))}
            </ul>
          </div>
          <div data-testid="submission-passed">
            <h3 className="font-medium text-accent">已通过</h3>
            <ul className="mt-1 space-y-1 leading-5 text-muted">
              {passed.map((condition) => <li key={condition}>{condition}</li>)}
            </ul>
          </div>
        </div>
      ) : null}
    </section>
  )
}
