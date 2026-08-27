// ADR-0007 Stage 2: HITL 人工评审面板
// - 显示评审反馈、5 维 rubric 分数（条形图）、修改建议、综合分、迭代轮次
// - 三个按钮：接受、拒绝（重生成）、{t('review.forcePass')}
// - 调 POST /sessions/{id}/review/decision
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调（与 VersionHistory 一致）
// 类型：从 types/api.ts import（遵循 ADR 0003 codegen 规范，不手写 API 响应 interface）

import { useState } from 'react'
import { useT } from '../lib/i18n'
import type { components } from '../types/api'

type ReviewInfoResponse = components['schemas']['ReviewInfoResponse']

export interface ReviewPanelProps {
  review: ReviewInfoResponse
  sessionId: string
  /** 决策提交后回调，父组件可据此刷新或切换 UI */
  onDecision?: (decision: string, nextAction: string) => void
}

// rubric 5 维中文标签 + 取值 key
const RUBRIC_DIMS: { key: keyof NonNullable<ReviewInfoResponse['rubric']>; labelKey: string }[] = [
  { key: 'endogeneity', labelKey: 'review.rubricEndogeneity' },
  { key: 'identification', labelKey: 'review.rubricIdentification' },
  { key: 'robustness', labelKey: 'review.rubricRobustness' },
  { key: 'contribution', labelKey: 'review.rubricContribution' },
  { key: 'readability', labelKey: 'review.rubricReadability' },
]

// 按分数返回条形颜色 class（0-1）
function barColorClass(score: number | null | undefined): string {
  if (score === null || score === undefined) return 'bg-muted'
  if (score >= 0.7) return 'bg-emerald-600'
  if (score >= 0.5) return 'bg-amber-600'
  return 'bg-red-600'
}

export default function ReviewPanel({
  review,
  sessionId,
  onDecision,
}: ReviewPanelProps) {
  const { t } = useT()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const autoPass = review.auto_decision === 'pass'
  const rubric = review.rubric ?? {}
  const extra = review as ReviewInfoResponse & {
    review_source?: string | null
    grounding_failures?: string[]
  }
  const reviewSource = extra.review_source
  const grounding = extra.grounding_failures ?? []

  async function submitDecision(decision: string) {
    setSubmitting(true)
    setError(null)
    try {
      const resp = await fetch(
        `http://localhost:8000/sessions/${sessionId}/review/decision`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ decision }),
        },
      )
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}))
        throw new Error(body.detail || `HTTP ${resp.status}`)
      }
      const data = await resp.json()
      onDecision?.(decision, data.next_action)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      data-testid="review-panel"
      className="rounded-xl border border-border bg-white shadow-sm"
    >
      {/* 头部：综合分 + 迭代轮次 + 自动决策 */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-3">
          <span className="font-serif text-sm font-semibold text-ink">
            {t('review.title')}
          </span>
          <span
            data-testid="review-auto-decision"
            className={`rounded px-2 py-0.5 font-serif text-xs ${
              autoPass
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            {autoPass ? t('review.autoPass') : t('review.autoFail')}
          </span>
        </div>
        <span className="font-serif text-xs text-muted">
          {t('review.roundLabel').replace('{0}', String(review.review_iteration)).replace('{1}', String(review.max_review_iterations))} · {t('review.scoreLabel').replace('{0}', review.score.toFixed(2))}
        </span>
      </div>
      {(reviewSource || grounding.length > 0) && (
        <div className="border-b border-border px-4 py-2 font-mono text-[11px] text-muted">
          {reviewSource ? (
            <span data-testid="review-source">source={reviewSource}</span>
          ) : null}
          {grounding.length > 0 ? (
            <span data-testid="review-grounding" className="ml-3 text-warning">
              {grounding.join(' · ')}
            </span>
          ) : null}
        </div>
      )}

      {/* 5 维 rubric 条形图 */}
      <div data-testid="review-rubric" className="px-4 py-3">
        <div className="mb-2 font-serif text-xs font-semibold text-muted">
          {t('review.rubric')}
        </div>
        <div className="flex flex-col gap-2">
          {RUBRIC_DIMS.map(({ key, labelKey }) => {
            const val = rubric[key] ?? null
            const pct = val !== null ? Math.round(val * 100) : 0
            return (
              <div
                key={key}
                data-testid={`rubric-dim-${key}`}
                className="flex items-center gap-2"
              >
                <span className="w-20 shrink-0 font-serif text-xs text-ink">
                  {t(labelKey)}
                </span>
                <div className="h-2 flex-1 overflow-hidden rounded bg-panel">
                  <div
                    className={`h-full ${barColorClass(val)}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span
                  data-testid={`rubric-val-${key}`}
                  className="w-10 shrink-0 text-right font-serif text-xs text-muted"
                >
                  {val !== null ? val.toFixed(2) : '—'}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* 评审反馈 */}
      <div data-testid="review-feedback" className="border-t border-border px-4 py-3">
        <div className="mb-1 font-serif text-xs font-semibold text-muted">
          {t('review.feedback')}
        </div>
        <p className="font-serif text-sm text-ink whitespace-pre-wrap">
          {review.feedback || t('review.noFeedback')}
        </p>
      </div>

      {/* 修改建议 */}
      <div
        data-testid="review-suggestions"
        className="border-t border-border px-4 py-3"
      >
        <div className="mb-1 font-serif text-xs font-semibold text-muted">
          {t('review.suggestions')}
        </div>
        <p className="font-serif text-sm text-ink whitespace-pre-wrap">
          {review.suggestions || t('review.noSuggestions')}
        </p>
      </div>

      {/* 错误提示 */}
      {error && (
        <div
          data-testid="review-error"
          className="border-t border-red-200 bg-red-50 px-4 py-2 font-serif text-xs text-red-700"
        >
          {t('review.submitError')}{error}
        </div>
      )}

      {/* 决策按钮 */}
      <div className="flex gap-2 border-t border-border px-4 py-3">
        <button
          type="button"
          data-testid="review-btn-accept"
          disabled={submitting}
          onClick={() => submitDecision('accept')}
          className="flex-1 rounded bg-accent px-3 py-1.5 font-serif text-xs font-semibold text-white transition-colors hover:bg-accent/90 disabled:opacity-50"
        >
          {autoPass ? t('review.accept') : t('review.acceptRegen')}
        </button>
        <button
          type="button"
          data-testid="review-btn-reject"
          disabled={submitting}
          onClick={() => submitDecision('reject')}
          className="flex-1 rounded border border-red-400 bg-red-50 px-3 py-1.5 font-serif text-xs font-semibold text-red-700 transition-colors hover:bg-red-100 disabled:opacity-50"
        >
          {t('review.reject')}
        </button>
        <button
          type="button"
          data-testid="review-btn-force-pass"
          disabled={submitting || autoPass}
          title={autoPass ? t('review.forcePassDisabled') : undefined}
          onClick={() => submitDecision('force_pass')}
          className="flex-1 rounded border border-amber-400 bg-amber-50 px-3 py-1.5 font-serif text-xs font-semibold text-amber-700 transition-colors hover:bg-amber-100 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {t('review.forcePass')}
        </button>
      </div>
    </div>
  )
}
