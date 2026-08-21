// HITL 评审：人先点，机器意见可选看。
// 点之前不显示自动通过、综合分、五维分数，也不说教。
// 修改建议里的「结构层失败」会泄底，点之前剥掉。

import { useEffect, useState } from 'react'
import { useT } from '../lib/i18n'
import type { components } from '../types/api'

type ReviewInfoResponse = components['schemas']['ReviewInfoResponse']

export interface ReviewPanelProps {
  review: ReviewInfoResponse
  sessionId: string
  /** 点完之后，父组件再刷新 */
  onDecision?: (decision: string, nextAction: string) => void
}

const RUBRIC_DIMS: { key: keyof NonNullable<ReviewInfoResponse['rubric']>; labelKey: string }[] = [
  { key: 'endogeneity', labelKey: 'review.rubricEndogeneity' },
  { key: 'identification', labelKey: 'review.rubricIdentification' },
  { key: 'robustness', labelKey: 'review.rubricRobustness' },
  { key: 'contribution', labelKey: 'review.rubricContribution' },
  { key: 'readability', labelKey: 'review.rubricReadability' },
]

function barColorClass(score: number | null | undefined): string {
  if (score === null || score === undefined) return 'bg-muted'
  if (score >= 0.7) return 'bg-emerald-600'
  if (score >= 0.5) return 'bg-amber-600'
  return 'bg-red-600'
}

/** 点之前把判决从建议里剥掉，避免提前泄底。 */
export function stripVerdictFromSuggestions(text: string): string {
  return (text || '')
    .replace(/结构层失败[：:][^.。]*[。.]?/g, '')
    .replace(/主张\/接地层失败[：:][^.。]*[。.]?/g, '')
    .replace(/未处理识别威胁[：:][^.。]*[。.]?/g, '')
    .replace(/不得只堆关键词。?/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

export default function ReviewPanel({
  review,
  sessionId,
  onDecision,
}: ReviewPanelProps) {
  const { t } = useT()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [decided, setDecided] = useState(false)
  const [peekMachine, setPeekMachine] = useState(false)
  const [pending, setPending] = useState<{
    decision: string
    nextAction: string
  } | null>(null)

  useEffect(() => {
    setDecided(false)
    setPeekMachine(false)
    setPending(null)
    setError(null)
  }, [review.chapter_index, review.review_iteration])

  const autoPass = review.auto_decision === 'pass'
  const rubric = review.rubric ?? {}
  const extra = review as ReviewInfoResponse & {
    review_source?: string | null
    grounding_failures?: string[]
  }
  const reviewSource = extra.review_source
  const grounding = extra.grounding_failures ?? []
  const showMachine = decided && peekMachine
  const suggestionsText = showMachine
    ? (review.suggestions || '').trim()
    : stripVerdictFromSuggestions(review.suggestions || '')

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
      setPending({ decision, nextAction: data.next_action })
      setDecided(true)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setSubmitting(false)
    }
  }

  function continueAfterReveal() {
    if (!pending) return
    onDecision?.(pending.decision, pending.nextAction)
  }

  return (
    <div
      data-testid="review-panel"
      className="border border-border rounded bg-paper shadow-sm"
    >
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-3">
          <span className="font-serif text-sm font-semibold text-ink">
            {t('review.title')}
          </span>
          {showMachine && (
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
          )}
        </div>
        <span className="font-serif text-xs text-muted">
          {t('review.roundLabel')
            .replace('{0}', String(review.review_iteration))
            .replace('{1}', String(review.max_review_iterations))}
          {showMachine ? (
            <>
              {' · '}
              <span data-testid="review-score">
                {t('review.scoreLabel').replace('{0}', review.score.toFixed(2))}
              </span>
            </>
          ) : null}
        </span>
      </div>

      {showMachine && (reviewSource || grounding.length > 0) && (
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

      {decided && pending && (
        <div
          data-testid="review-your-decision"
          className="flex items-center justify-between gap-2 border-b border-border px-4 py-2"
        >
          <span className="font-serif text-xs text-ink">
            {t('review.yourDecision').replace(
              '{0}',
              pending.decision === 'reject'
                ? t('review.blindReject')
                : t('review.blindAccept'),
            )}
          </span>
          <button
            type="button"
            data-testid="review-btn-peek"
            onClick={() => setPeekMachine((open) => !open)}
            className="font-serif text-xs text-muted underline underline-offset-2 hover:text-ink"
          >
            {peekMachine ? t('review.hideMachine') : t('review.peekMachine')}
          </button>
        </div>
      )}

      {showMachine && (
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
      )}

      {showMachine && (
        <div data-testid="review-feedback" className="border-t border-border px-4 py-3">
          <div className="mb-1 font-serif text-xs font-semibold text-muted">
            {t('review.feedback')}
          </div>
          <p className="font-serif text-sm text-ink whitespace-pre-wrap">
            {review.feedback || t('review.noFeedback')}
          </p>
        </div>
      )}

      <div
        data-testid="review-suggestions"
        className="border-t border-border px-4 py-3"
      >
        <div className="mb-1 font-serif text-xs font-semibold text-muted">
          {t('review.suggestions')}
        </div>
        <p className="font-serif text-sm text-ink whitespace-pre-wrap">
          {suggestionsText || t('review.noSuggestions')}
        </p>
      </div>

      {error && (
        <div
          data-testid="review-error"
          className="border-t border-red-200 bg-red-50 px-4 py-2 font-serif text-xs text-red-700"
        >
          {t('review.submitError')}{error}
        </div>
      )}

      <div className="flex gap-2 border-t border-border px-4 py-3">
        {decided ? (
          <button
            type="button"
            data-testid="review-btn-continue"
            onClick={continueAfterReveal}
            className="flex-1 rounded border border-accent bg-accent px-3 py-1.5 font-serif text-xs font-semibold text-white transition-colors hover:bg-accent/80"
          >
            {t('review.continue')}
          </button>
        ) : (
          <>
            <button
              type="button"
              data-testid="review-btn-accept"
              disabled={submitting}
              onClick={() => submitDecision('accept')}
              className="flex-1 rounded border border-accent bg-accent px-3 py-1.5 font-serif text-xs font-semibold text-white transition-colors hover:bg-accent/80 disabled:opacity-50"
            >
              {t('review.blindAccept')}
            </button>
            <button
              type="button"
              data-testid="review-btn-reject"
              disabled={submitting}
              onClick={() => submitDecision('reject')}
              className="flex-1 rounded border border-red-400 bg-red-50 px-3 py-1.5 font-serif text-xs font-semibold text-red-700 transition-colors hover:bg-red-100 disabled:opacity-50"
            >
              {t('review.blindReject')}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
