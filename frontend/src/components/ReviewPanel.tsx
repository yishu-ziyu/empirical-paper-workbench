// ADR-0007 Stage 2: HITL 人工评审面板
// - 显示评审反馈、5 维 rubric 分数（条形图）、修改建议、综合分、迭代轮次
// - 三个按钮：接受、拒绝（重生成）、强制通过
// - 调 POST /sessions/{id}/review/decision
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调（与 VersionHistory 一致）
// 类型：从 types/api.ts import（遵循 ADR 0003 codegen 规范，不手写 API 响应 interface）

import { useState } from 'react'
import type { components } from '../types/api'

type ReviewInfoResponse = components['schemas']['ReviewInfoResponse']

export interface ReviewPanelProps {
  review: ReviewInfoResponse
  sessionId: string
  /** 决策提交后回调，父组件可据此刷新或切换 UI */
  onDecision?: (decision: string, nextAction: string) => void
}

// rubric 5 维中文标签 + 取值 key
const RUBRIC_DIMS: { key: keyof NonNullable<ReviewInfoResponse['rubric']>; label: string }[] = [
  { key: 'endogeneity', label: '内生性' },
  { key: 'identification', label: '识别策略' },
  { key: 'robustness', label: '稳健性' },
  { key: 'contribution', label: '贡献度' },
  { key: 'readability', label: '可读性' },
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
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const autoPass = review.auto_decision === 'pass'
  const rubric = review.rubric ?? {}

  async function submitDecision(decision: string) {
    setSubmitting(true)
    setError(null)
    try {
      const resp = await fetch(
        `/sessions/${sessionId}/review/decision`,
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
      className="border border-border rounded bg-paper shadow-sm"
    >
      {/* 头部：综合分 + 迭代轮次 + 自动决策 */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-3">
          <span className="font-serif text-sm font-semibold text-ink">
            章节评审
          </span>
          <span
            data-testid="review-auto-decision"
            className={`rounded px-2 py-0.5 font-serif text-xs ${
              autoPass
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            {autoPass ? '自动通过' : '自动不通过'}
          </span>
        </div>
        <span className="font-serif text-xs text-muted">
          第 {review.review_iteration}/{review.max_review_iterations} 轮 · 综合{' '}
          {review.score.toFixed(2)}
        </span>
      </div>

      {/* 5 维 rubric 条形图 */}
      <div data-testid="review-rubric" className="px-4 py-3">
        <div className="mb-2 font-serif text-xs font-semibold text-muted">
          评审 Rubric（5 维）
        </div>
        <div className="flex flex-col gap-2">
          {RUBRIC_DIMS.map(({ key, label }) => {
            const val = rubric[key] ?? null
            const pct = val !== null ? Math.round(val * 100) : 0
            return (
              <div
                key={key}
                data-testid={`rubric-dim-${key}`}
                className="flex items-center gap-2"
              >
                <span className="w-20 shrink-0 font-serif text-xs text-ink">
                  {label}
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
          评审反馈
        </div>
        <p className="font-serif text-sm text-ink whitespace-pre-wrap">
          {review.feedback || '暂无评审反馈'}
        </p>
      </div>

      {/* 修改建议 */}
      <div
        data-testid="review-suggestions"
        className="border-t border-border px-4 py-3"
      >
        <div className="mb-1 font-serif text-xs font-semibold text-muted">
          修改建议
        </div>
        <p className="font-serif text-sm text-ink whitespace-pre-wrap">
          {review.suggestions || '暂无修改建议'}
        </p>
      </div>

      {/* 错误提示 */}
      {error && (
        <div
          data-testid="review-error"
          className="border-t border-red-200 bg-red-50 px-4 py-2 font-serif text-xs text-red-700"
        >
          决策提交失败：{error}
        </div>
      )}

      {/* 决策按钮 */}
      <div className="flex gap-2 border-t border-border px-4 py-3">
        <button
          type="button"
          data-testid="review-btn-accept"
          disabled={submitting}
          onClick={() => submitDecision('accept')}
          className="flex-1 rounded border border-accent bg-accent px-3 py-1.5 font-serif text-xs font-semibold text-white transition-colors hover:bg-accent/80 disabled:opacity-50"
        >
          {autoPass ? '接受' : '接受重生成'}
        </button>
        <button
          type="button"
          data-testid="review-btn-reject"
          disabled={submitting}
          onClick={() => submitDecision('reject')}
          className="flex-1 rounded border border-red-400 bg-red-50 px-3 py-1.5 font-serif text-xs font-semibold text-red-700 transition-colors hover:bg-red-100 disabled:opacity-50"
        >
          拒绝重生成
        </button>
        <button
          type="button"
          data-testid="review-btn-force-pass"
          disabled={submitting || autoPass}
          title={autoPass ? '自动评审已通过，无需强制通过' : undefined}
          onClick={() => submitDecision('force_pass')}
          className="flex-1 rounded border border-amber-400 bg-amber-50 px-3 py-1.5 font-serif text-xs font-semibold text-amber-700 transition-colors hover:bg-amber-100 disabled:cursor-not-allowed disabled:opacity-40"
        >
          强制通过
        </button>
      </div>
    </div>
  )
}
