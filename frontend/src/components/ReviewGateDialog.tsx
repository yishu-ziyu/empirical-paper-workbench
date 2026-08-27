// 审批硬证据门对话框（review_gate 409 的显式交互面）
//
// 交互契约取自 shadcn/ui AlertDialog（radix）参考实现：
// - role="alertdialog" + aria-labelledby / aria-describedby
// - 遮罩打断上下文；Cancel（安全动作：打回重写/返回）与
//   Action（破坏性动作：强行放行，红色、两步确认）严格分离
// 配色与布局走项目 Editorial Academic Refined 令牌，不引 radix 依赖。
//
// 两步确认：点"强行放行"先进入确认步（按钮文字变化），再点一次才真正
// 发出 force —— 让"留下永久绕过痕迹"成为一次有分量的决定。

import { useState } from 'react'
import { useT } from '../lib/i18n'

export interface ReviewGateDialogProps {
  /** 该章最新综合分（409 detail.score），可能为 null（无评审记录） */
  score: number | null
  /** 通过线（后端 REVIEW_SCORE_THRESHOLD） */
  threshold: number
  /** 当前章的评审意见（无匹配时给空串，隐藏该块） */
  feedback?: string
  busy?: boolean
  /** 打回重写（安全动作） */
  onRegenerate: () => void
  /** 强行放行（破坏性动作，两步确认后才触发一次） */
  onForce: () => void
  onClose: () => void
}

function fmtScore(score: number | null, fallback: string): string {
  return score === null || score === undefined ? fallback : score.toFixed(2)
}

export default function ReviewGateDialog({
  score,
  threshold,
  feedback = '',
  busy = false,
  onRegenerate,
  onForce,
  onClose,
}: ReviewGateDialogProps) {
  const { t } = useT()
  const [confirming, setConfirming] = useState(false)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40">
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="review-gate-title"
        aria-describedby="review-gate-desc"
        data-testid="review-gate-dialog"
        className="w-full max-w-md rounded-lg border border-border bg-panel p-5 shadow-xl"
      >
        <h2
          id="review-gate-title"
          data-testid="review-gate-title"
          className="font-serif text-base font-semibold text-ink"
        >
          {t('reviewGate.title')}
        </h2>

        <p
          data-testid="review-gate-score"
          className="mt-2 font-mono text-xs text-danger"
        >
          {t('reviewGate.scoreLine')
            .replace('{score}', fmtScore(score, t('reviewGate.noScore')))
            .replace('{threshold}', threshold.toFixed(2))}
        </p>

        <p
          id="review-gate-desc"
          className="mt-2 font-serif text-sm leading-6 text-muted"
        >
          {t('reviewGate.body')}
        </p>

        {feedback ? (
          <div
            data-testid="review-gate-feedback"
            className="mt-3 max-h-28 overflow-y-auto rounded border border-border bg-paper px-3 py-2"
          >
            <p className="mb-1 font-mono text-[11px] uppercase tracking-wide text-muted">
              {t('reviewGate.feedbackLabel')}
            </p>
            <p className="whitespace-pre-wrap font-serif text-xs leading-5 text-ink">
              {feedback}
            </p>
          </div>
        ) : null}

        <div className="mt-5 flex items-center justify-end gap-2">
          {!confirming ? (
            <>
              <button
                type="button"
                data-testid="review-gate-close"
                onClick={onClose}
                disabled={busy}
                className="rounded border border-border px-3 py-1.5 text-xs text-muted transition-colors duration-200 hover:bg-paper disabled:opacity-50"
              >
                {t('reviewGate.close')}
              </button>
              <button
                type="button"
                data-testid="review-gate-regen"
                onClick={onRegenerate}
                disabled={busy}
                className="rounded bg-accent px-3 py-1.5 text-xs font-medium text-paper transition-colors duration-200 hover:bg-accent/90 disabled:opacity-50"
              >
                {t('reviewGate.regen')}
              </button>
              <button
                type="button"
                data-testid="review-gate-force-arm"
                onClick={() => setConfirming(true)}
                disabled={busy}
                className="rounded border border-danger/50 px-3 py-1.5 text-xs font-medium text-danger transition-colors duration-200 hover:bg-danger/10 disabled:opacity-50"
              >
                {t('reviewGate.force')}
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                data-testid="review-gate-force-disarm"
                onClick={() => setConfirming(false)}
                disabled={busy}
                className="rounded border border-border px-3 py-1.5 text-xs text-muted transition-colors duration-200 hover:bg-paper disabled:opacity-50"
              >
                {t('reviewGate.close')}
              </button>
              <button
                type="button"
                data-testid="review-gate-force-confirm"
                onClick={onForce}
                disabled={busy}
                className="rounded bg-danger px-3 py-1.5 text-xs font-semibold text-paper transition-colors duration-200 hover:bg-danger/90 disabled:opacity-50"
              >
                {t('reviewGate.confirmForce')}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
