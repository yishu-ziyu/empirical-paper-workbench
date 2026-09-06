import { useEffect, useState } from 'react'
import type { components } from '../types/api'
import type { ResearchLab } from '../lib/workspace'

type ExpectationCriterion = components['schemas']['ExpectationCriterion']
type EvidenceMetricRef = components['schemas']['EvidenceMetricRef']

function field(label: string, value: string, gloss?: string) {
  return (
    <div className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5">
      <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
        {label}
        {gloss ? <span className="ml-1 font-sans normal-case tracking-normal text-wb-muted">（{gloss}）</span> : null}
      </dt>
      <dd className="mt-1 text-[14px] leading-6 text-wb-ink">{value}</dd>
    </div>
  )
}

function named(raw: unknown): {
  name?: string
  label?: string
  gloss?: string
  text?: string
  instrument?: string
} {
  return raw && typeof raw === 'object' ? (raw as Record<string, string>) : {}
}

export function TeachingCaseBadge({ teachingCase }: { teachingCase?: string | null }) {
  if (!teachingCase) return null
  return (
    <p
      data-testid="teaching-case-badge"
      className="mb-4 inline-flex rounded-full border border-wb-line bg-wb-subtle px-2.5 py-1 font-mono text-[11px] text-wb-muted"
    >
      Teaching case · Card 1995
    </p>
  )
}

export function ResearchQuestionCard({ question }: { question: NonNullable<ResearchLab['question']> }) {
  const outcome = named(question.outcome)
  const treatment = named(question.treatment)
  const threat = named(question.causal_threat)
  const ident = named(question.identification)
  const estimand = question.estimand && typeof question.estimand === 'object'
    ? (question.estimand as Record<string, string>)
    : {}
  return (
    <section data-testid="research-question-card" className="mb-6 space-y-3">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          Research Question（研究问题）
        </p>
        <h2 className="mt-1 font-serif text-[1.35rem] text-wb-ink">
          {question.prompt_en || 'Research question'}
        </h2>
        {question.prompt_zh ? (
          <p className="mt-1 text-[13px] text-wb-muted">{question.prompt_zh}</p>
        ) : null}
      </header>
      <dl className="grid gap-2 sm:grid-cols-2">
        {field('Outcome', outcome.label || outcome.name || '—', outcome.gloss)}
        {field('Treatment', treatment.label || treatment.name || '—', treatment.gloss)}
        {field('Causal threat', threat.text || threat.label || '—', threat.gloss)}
        {field(
          'Candidate identification',
          ident.label || ident.instrument || '—',
          ident.gloss,
        )}
      </dl>
      <div className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5">
        <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
          Estimand
        </p>
        <p className="mt-1 text-[14px] leading-6 text-wb-ink">{estimand.ols || '—'}</p>
        <p className="mt-1 text-[14px] leading-6 text-wb-ink">{estimand.iv || '—'}</p>
      </div>
    </section>
  )
}

// 显式判定方向选项：每个选项映射到一条结构化 criterion（M1）。
// 判据只由这里显式构造或原样保留，绝不由 textarea 文本重猜。
type CriterionOption =
  | 'iv-lt-ols'
  | 'iv-gt-ols'
  | 'iv-approx-ols'
  | 'iv-positive'
  | 'iv-negative'

const CRITERION_OPTIONS: Array<{ value: CriterionOption; label: string }> = [
  { value: 'iv-lt-ols', label: 'IV < OLS' },
  { value: 'iv-gt-ols', label: 'IV > OLS' },
  { value: 'iv-approx-ols', label: 'IV ≈ OLS (±25%)' },
  { value: 'iv-positive', label: '预期为正' },
  { value: 'iv-negative', label: '预期为负' },
]

const IV_METRIC: EvidenceMetricRef = {
  metric: 'estimate.coef',
  estimator: 'iv',
  label: 'IV estimate',
}
const OLS_METRIC: EvidenceMetricRef = {
  metric: 'estimate.coef',
  estimator: 'ols',
  label: 'OLS estimate',
}

function criterionForOption(
  option: CriterionOption,
  source: 'seed' | 'user',
  existingId?: string,
): ExpectationCriterion {
  const id = existingId || `criterion.user.${option}`
  switch (option) {
    case 'iv-lt-ols':
      return {
        id,
        kind: 'ordering',
        operator: 'lt',
        left: IV_METRIC,
        right: OLS_METRIC,
        label: 'IV estimate < OLS estimate',
        source,
      }
    case 'iv-gt-ols':
      return {
        id,
        kind: 'ordering',
        operator: 'gt',
        left: IV_METRIC,
        right: OLS_METRIC,
        label: 'IV estimate > OLS estimate',
        source,
      }
    case 'iv-approx-ols':
      return {
        id,
        kind: 'distance',
        operator: 'approx',
        left: IV_METRIC,
        right: OLS_METRIC,
        tolerance: { rel: 0.25 },
        label: 'IV estimate ≈ OLS estimate (±25%)',
        source,
      }
    case 'iv-positive':
      return {
        id,
        kind: 'sign',
        operator: 'positive',
        left: IV_METRIC,
        label: 'IV estimate is positive',
        source,
      }
    case 'iv-negative':
      return {
        id,
        kind: 'sign',
        operator: 'negative',
        left: IV_METRIC,
        label: 'IV estimate is negative',
        source,
      }
  }
}

function optionForCriterion(criterion: ExpectationCriterion): CriterionOption | null {
  const leftIsIv = criterion.left?.estimator === 'iv'
  const right = criterion.right
  const rightIsOls =
    right != null && typeof right === 'object' && right.estimator === 'ols'
  if (leftIsIv && rightIsOls) {
    if (criterion.kind === 'ordering' && criterion.operator === 'lt') return 'iv-lt-ols'
    if (criterion.kind === 'ordering' && criterion.operator === 'gt') return 'iv-gt-ols'
    if (criterion.kind === 'distance' && criterion.operator === 'approx') return 'iv-approx-ols'
  }
  if (criterion.kind === 'sign' && leftIsIv) {
    if (criterion.operator === 'positive') return 'iv-positive'
    if (criterion.operator === 'negative') return 'iv-negative'
  }
  return null
}

export function ExpectationEditor({
  expectation,
  onSave,
}: {
  expectation: NonNullable<ResearchLab['expectation']>
  onSave: (payload: {
    text: string
    confidence: 'low' | 'medium' | 'high'
    criteria?: ExpectationCriterion[]
  }) => Promise<void>
}) {
  const [text, setText] = useState(expectation.text || '')
  const [confidence, setConfidence] = useState<'low' | 'medium' | 'high'>(
    expectation.confidence || 'medium',
  )
  const [criteria, setCriteria] = useState<ExpectationCriterion[]>(
    expectation.criteria ?? [],
  )
  const [busy, setBusy] = useState(false)
  const [saveFailed, setSaveFailed] = useState(false)
  useEffect(() => {
    setText(expectation.text || '')
    setConfidence(expectation.confidence || 'medium')
    setCriteria(expectation.criteria ?? [])
    setSaveFailed(false)
  }, [expectation.text, expectation.confidence, expectation.version, expectation.criteria])

  const primary = criteria[0] ?? null
  const selectedOption = primary ? optionForCriterion(primary) : null

  const changeCriterion = (option: CriterionOption) => {
    // 显式修改：替换第一条判据，保留其余判据；文本不动。
    const next = criterionForOption(
      option,
      primary?.source === 'seed' ? 'user' : (primary?.source ?? 'user'),
      primary?.id,
    )
    setCriteria(criteria.length > 0 ? [next, ...criteria.slice(1)] : [next])
  }

  const save = async () => {
    setBusy(true)
    setSaveFailed(false)
    try {
      await onSave({ text: text.trim(), confidence, criteria })
    } catch {
      // 失败不吞文本：textarea 保留，错误就地显示，Retry 可重试。
      setSaveFailed(true)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section data-testid="expectation-editor" className="mb-6 space-y-3">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          Expectation（预期）
        </p>
        <h3 className="mt-1 font-serif text-[1.15rem] text-wb-ink">Before seeing results</h3>
      </header>
      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={3}
        className="w-full rounded-md border border-wb-line bg-wb-surface px-3 py-2 text-[14px] leading-6 text-wb-ink"
      />
      <div
        data-testid="expectation-criteria-block"
        className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5"
      >
        <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
          Surprise condition · 意外判定
        </p>
        {criteria.length > 0 ? (
          <ul className="mt-1.5 space-y-1">
            {criteria.map((criterion) => (
              <li
                key={criterion.id}
                data-testid="expectation-criterion"
                data-source={criterion.source}
                className="flex items-center gap-2 text-[13px] leading-5 text-wb-ink"
              >
                <span aria-hidden className="text-wb-primary">◇</span>
                {criterion.label}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-1.5 text-[12px] text-wb-muted">
            还没有结构化判据；可用下方控件添加。
          </p>
        )}
        <label className="mt-2 flex flex-wrap items-center gap-2 text-[12px] text-wb-muted">
          判定方向
          <select
            data-testid="expectation-criterion-select"
            value={selectedOption ?? ''}
            onChange={(event) => {
              const value = event.target.value as CriterionOption | ''
              if (value) changeCriterion(value)
            }}
            className="rounded border border-wb-line bg-wb-surface px-2 py-1 text-[12px] text-wb-ink"
          >
            <option value="" disabled>
              选择判定方向…
            </option>
            {CRITERION_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <span className="text-[11px] text-wb-faint">
            保存时随预期一起显式提交；改上方文字不会改变判定。
          </span>
        </label>
      </div>
      {saveFailed ? (
        <div
          data-testid="expectation-save-error"
          role="alert"
          className="flex flex-wrap items-center gap-3 rounded-md border border-wb-danger/30 bg-wb-danger-soft px-3 py-2"
        >
          <p className="text-[12px] text-wb-danger">
            保存失败（网络或服务暂不可用）。你的修改仍保留在下方输入框里。
          </p>
          <button
            type="button"
            data-testid="expectation-save-retry"
            disabled={busy || !text.trim()}
            onClick={() => {
              void save()
            }}
            className="wb-press rounded-md border border-wb-line bg-wb-surface px-2.5 py-1 text-[12px] text-wb-ink disabled:opacity-50"
          >
            Retry
          </button>
        </div>
      ) : null}
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-[12px] text-wb-muted">
          Confidence
          <select
            data-testid="expectation-confidence"
            value={confidence}
            onChange={(event) =>
              setConfidence(event.target.value as 'low' | 'medium' | 'high')
            }
            className="ml-2 rounded border border-wb-line bg-wb-surface px-2 py-1 text-[12px] text-wb-ink"
          >
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </label>
        <button
          type="button"
          disabled={busy || !text.trim()}
          onClick={() => {
            void save()
          }}
          className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
        >
          Save expectation
        </button>
      </div>
    </section>
  )
}

export function SpecificationSpacePanel({
  space,
  onFreeze,
  onRun,
  running = false,
  progress = null,
  failure = null,
  onRetryRun,
}: {
  space: NonNullable<ResearchLab['specification_space']>
  onFreeze: () => Promise<void>
  onRun?: () => Promise<void>
  /** 运行态来自全局 state（snapshot.active_run 投影），刷新/重挂载不丢。 */
  running?: boolean
  /** 逐 spec 进度；null 表示 indeterminate（分母不可数时不虚构）。 */
  progress?: { done: number; total: number } | null
  /** spec_run 终态失败（稳定错误类别）。 */
  failure?: { category: string } | null
  onRetryRun?: () => void
}) {
  const [busy, setBusy] = useState(false)
  const definitions = space.definitions ?? []
  const runLabel = running
    ? progress
      ? `Running ${progress.done}/${progress.total}`
      : 'Running specifications…'
    : 'Run specifications'
  return (
    <section data-testid="spec-space" className="space-y-3">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
            Admissible Space（合理规格空间）
          </p>
          <h2 className="mt-1 font-serif text-[1.35rem] text-ink">Proposed specifications</h2>
          <p className="mt-1 text-[13px] text-wb-muted">
            {space.frozen_at
              ? `Frozen ${new Date(space.frozen_at).toLocaleString()}`
              : 'Confirm this space before any comparison results.'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
        <button
          type="button"
          data-testid="spec-space-freeze"
          disabled={busy || running || Boolean(space.frozen_at)}
          onClick={() => {
            setBusy(true)
            void onFreeze().finally(() => setBusy(false))
          }}
          className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
        >
          {space.frozen_at ? 'Admissible space frozen' : 'Freeze admissible space'}
        </button>
        {space.frozen_at && onRun ? (
          <button
            type="button"
            data-testid="spec-space-run"
            data-running={running}
            disabled={busy || running}
            onClick={() => {
              setBusy(true)
              void onRun().finally(() => setBusy(false))
            }}
            className="wb-press rounded-md border border-wb-line px-3 py-1.5 text-[12px] text-wb-ink disabled:opacity-50"
          >
            {runLabel}
          </button>
        ) : null}
        </div>
      </header>
      {running ? (
        <p
          data-testid="spec-space-run-status"
          role="status"
          aria-live="polite"
          className="rounded-md border border-wb-line bg-wb-subtle px-3 py-2 text-[12px] text-wb-muted"
        >
          {progress
            ? `正在运行规格 ${progress.done}/${progress.total}；完成后自动进入 Evidence。`
            : '正在运行规格…完成后自动进入 Evidence。'}
        </p>
      ) : null}
      {failure ? (
        <div
          data-testid="spec-space-run-error"
          role="alert"
          className="flex flex-wrap items-center gap-3 rounded-md border border-wb-danger/30 bg-wb-danger-soft px-3 py-2"
        >
          <p className="text-[12px] text-wb-danger">
            规格运行失败（
            <span className="font-mono">{failure.category}</span>
            ）。没有产生任何结果；可重试。
          </p>
          {onRetryRun ? (
            <button
              type="button"
              data-testid="spec-space-run-retry"
              onClick={onRetryRun}
              className="wb-press rounded-md border border-wb-line bg-wb-surface px-2.5 py-1 text-[12px] text-wb-ink"
            >
              Retry
            </button>
          ) : null}
        </div>
      ) : null}
      <ul className="space-y-2">
        {definitions.map((item) => (
          <li
            key={item.id}
            className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5"
          >
            <p className="text-[14px] font-medium text-wb-ink">{item.label}</p>
            <p className="mt-1 text-[12px] leading-5 text-wb-muted">{item.rationale}</p>
            <p className="mt-1 font-mono text-[11px] text-wb-faint">
              {item.id} · {item.dimension}={item.value} ·{' '}
              {item.admissible ? item.user_decision : 'unavailable'}
            </p>
          </li>
        ))}
      </ul>
    </section>
  )
}
