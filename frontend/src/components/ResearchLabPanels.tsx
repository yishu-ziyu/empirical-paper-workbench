import { useEffect, useState } from 'react'
import type { components } from '../types/api'
import type { ResearchLab } from '../lib/workspace'
import { useT } from '../lib/i18n'
import { MethodHelp, TaskHelp } from './TaskHelp'

type ExpectationCriterion = components['schemas']['ExpectationCriterion']
type EvidenceMetricRef = components['schemas']['EvidenceMetricRef']

function field(label: string, value: string) {
  return (
    <div className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5">
      <dt className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
        {label}
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
  const { t } = useT()
  if (!teachingCase) return null
  return (
    <p
      data-testid="teaching-case-badge"
      className="mb-4 inline-flex rounded-full border border-wb-line bg-wb-subtle px-2.5 py-1 font-mono text-[11px] text-wb-muted"
    >
      {t('workbench.teachingCase')} Card 1995
    </p>
  )
}

function displayNamed(
  raw: ReturnType<typeof named>,
  lang: 'zh' | 'en',
): string {
  if (lang === 'zh') {
    return raw.gloss || raw.label || raw.name || raw.text || raw.instrument || '—'
  }
  return raw.label || raw.name || raw.text || raw.instrument || raw.gloss || '—'
}

export function ResearchQuestionCard({ question }: { question: NonNullable<ResearchLab['question']> }) {
  const { t, lang } = useT()
  const outcome = named(question.outcome)
  const treatment = named(question.treatment)
  const threat = named(question.causal_threat)
  const ident = named(question.identification)
  const estimand = question.estimand && typeof question.estimand === 'object'
    ? (question.estimand as Record<string, string>)
    : {}
  const promptEn = typeof question.prompt_en === 'string' ? question.prompt_en.trim() : ''
  const promptZh = typeof question.prompt_zh === 'string' ? question.prompt_zh.trim() : ''
  const primary = lang === 'zh' ? promptZh || promptEn : promptEn || promptZh
  const original = lang === 'zh' ? (promptZh && promptEn ? promptEn : '') : promptEn && promptZh ? promptZh : ''
  const originalLang = lang === 'zh' ? 'en' : 'zh-CN'
  return (
    <section data-testid="research-question-card" className="mb-6 space-y-3">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          {t('question.kicker')}
        </p>
        <h2 className="mt-1 font-serif text-[1.35rem] text-wb-ink">
          {primary || t('question.fallback')}
        </h2>
        {original ? (
          <details className="mt-1">
            <summary className="cursor-pointer text-[12px] text-wb-muted">{t('question.original')}</summary>
            <p lang={originalLang} className="mt-1 text-[13px] text-wb-muted">
              {original}
            </p>
          </details>
        ) : null}
      </header>
      <dl className="grid gap-2 sm:grid-cols-2">
        {field(t('question.outcome'), displayNamed(outcome, lang))}
        {field(t('question.treatment'), displayNamed(treatment, lang))}
        {field(t('question.threat'), displayNamed(threat, lang))}
        {field(t('question.identification'), displayNamed(ident, lang))}
      </dl>
      <div className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5">
        <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
          {t('question.estimand')}
        </p>
        <p className="mt-1 text-[14px] leading-6 text-wb-ink">{estimand.ols || '—'}</p>
        <p className="mt-1 text-[14px] leading-6 text-wb-ink">{estimand.iv || '—'}</p>
        <div className="mt-2 space-y-2">
          <MethodHelp method="OLS" />
          <MethodHelp method="IV" />
        </div>
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

const CRITERION_OPTIONS: Array<{ value: CriterionOption; labelKey: string }> = [
  { value: 'iv-lt-ols', labelKey: 'expectation.opt.ivLtOls' },
  { value: 'iv-gt-ols', labelKey: 'expectation.opt.ivGtOls' },
  { value: 'iv-approx-ols', labelKey: 'expectation.opt.ivApprox' },
  { value: 'iv-positive', labelKey: 'expectation.opt.positive' },
  { value: 'iv-negative', labelKey: 'expectation.opt.negative' },
]

function comparableSpecIdsFromDefinitions(
  definitions: Array<{ id?: string; admissible?: boolean }> | undefined,
): { olsId: string; ivId: string } {
  const byId = new Map<string, { id?: string; admissible?: boolean }>()
  for (const item of definitions ?? []) {
    if (item.id) byId.set(item.id, item)
  }
  const ols = byId.get('ols_region_dummies')
  const iv = byId.get('iv_region_dummies')
  if (ols?.admissible && iv?.admissible) {
    return { olsId: 'ols_region_dummies', ivId: 'iv_region_dummies' }
  }
  return { olsId: 'ols_full_controls', ivId: 'iv_nearc4_full' }
}

function boundMetric(estimator: 'iv' | 'ols', specId: string): EvidenceMetricRef {
  return {
    metric: 'estimate.coef',
    estimator,
    spec_id: specId,
    label: estimator === 'iv' ? 'IV estimate' : 'OLS estimate',
  }
}

function metricRefFromRight(
  right: ExpectationCriterion['right'] | undefined,
): EvidenceMetricRef | undefined {
  if (right != null && typeof right === 'object') return right
  return undefined
}

function criterionForOption(
  option: CriterionOption,
  existing: ExpectationCriterion | null,
  preservedRight: EvidenceMetricRef | undefined,
  comparable: { olsId: string; ivId: string },
): ExpectationCriterion {
  const id = existing?.id || `criterion.user.${option}`
  const source: 'seed' | 'user' = existing ? 'user' : 'user'
  const left = existing?.left ?? boundMetric('iv', comparable.ivId)
  const right =
    metricRefFromRight(existing?.right) ??
    preservedRight ??
    boundMetric('ols', comparable.olsId)
  switch (option) {
    case 'iv-lt-ols':
      return {
        id,
        kind: 'ordering',
        operator: 'lt',
        left,
        right,
        label: 'IV estimate < OLS estimate',
        source,
      }
    case 'iv-gt-ols':
      return {
        id,
        kind: 'ordering',
        operator: 'gt',
        left,
        right,
        label: 'IV estimate > OLS estimate',
        source,
      }
    case 'iv-approx-ols':
      return {
        id,
        kind: 'distance',
        operator: 'approx',
        left,
        right,
        tolerance: { rel: 0.25 },
        label: 'IV estimate ≈ OLS estimate (±25%)',
        source,
      }
    case 'iv-positive':
      return {
        id,
        kind: 'sign',
        operator: 'positive',
        left,
        label: 'IV estimate is positive',
        source,
      }
    case 'iv-negative':
      return {
        id,
        kind: 'sign',
        operator: 'negative',
        left,
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
  criteriaLocked = false,
  specificationSpace,
}: {
  expectation: NonNullable<ResearchLab['expectation']>
  onSave: (payload: {
    text: string
    confidence: 'low' | 'medium' | 'high'
    criteria?: ExpectationCriterion[]
  }) => Promise<void>
  criteriaLocked?: boolean
  specificationSpace?: ResearchLab['specification_space']
}) {
  const { t } = useT()
  const [text, setText] = useState(expectation.text || '')
  const [confidence, setConfidence] = useState<'low' | 'medium' | 'high'>(
    expectation.confidence || 'medium',
  )
  const [criteria, setCriteria] = useState<ExpectationCriterion[]>(
    expectation.criteria ?? [],
  )
  const [preservedRight, setPreservedRight] = useState<EvidenceMetricRef | undefined>(
    () => metricRefFromRight(expectation.criteria?.[0]?.right),
  )
  const [busy, setBusy] = useState(false)
  const [saveFailed, setSaveFailed] = useState(false)
  useEffect(() => {
    setText(expectation.text || '')
    setConfidence(expectation.confidence || 'medium')
    setCriteria(expectation.criteria ?? [])
    setPreservedRight(metricRefFromRight(expectation.criteria?.[0]?.right))
    setSaveFailed(false)
  }, [expectation.text, expectation.confidence, expectation.version, expectation.criteria])

  const primary = criteria[0] ?? null
  const selectedOption = primary ? optionForCriterion(primary) : null
  const comparable = comparableSpecIdsFromDefinitions(specificationSpace?.definitions)

  const changeCriterion = (option: CriterionOption) => {
    if (criteriaLocked) return
    const next = criterionForOption(option, primary, preservedRight, comparable)
    const nextRight = metricRefFromRight(next.right)
    if (nextRight) setPreservedRight(nextRight)
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
          {t('expectation.kicker')}
        </p>
        <h3 className="mt-1 font-serif text-[1.15rem] text-wb-ink">{t('expectation.before')}</h3>
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
          {t('expectation.condition')}
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
            {t('expectation.noCriteria')}
          </p>
        )}
        <label className="mt-2 flex flex-wrap items-center gap-2 text-[12px] text-wb-muted">
          {t('expectation.direction')}
          <select
            data-testid="expectation-criterion-select"
            value={selectedOption ?? ''}
            disabled={criteriaLocked}
            onChange={(event) => {
              const value = event.target.value as CriterionOption | ''
              if (value) changeCriterion(value)
            }}
            className="rounded border border-wb-line bg-wb-surface px-2 py-1 text-[12px] text-wb-ink disabled:cursor-not-allowed disabled:opacity-60"
          >
            <option value="" disabled>
              {t('expectation.choose')}
            </option>
            {CRITERION_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {t(option.labelKey)}
              </option>
            ))}
          </select>
          {criteriaLocked ? (
            <span data-testid="expectation-criterion-locked" className="text-[11px] text-wb-muted">
              {t('expectation.locked')}
            </span>
          ) : (
            <span className="text-[11px] text-wb-faint">
              {t('expectation.saveHint')}
            </span>
          )}
        </label>
      </div>
      {saveFailed ? (
        <div
          data-testid="expectation-save-error"
          role="alert"
          className="flex flex-wrap items-center gap-3 rounded-md border border-wb-danger/30 bg-wb-danger-soft px-3 py-2"
        >
          <p className="text-[12px] text-wb-danger">
            {t('expectation.saveFailed')}
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
            {t('expectation.retry')}
          </button>
        </div>
      ) : null}
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-[12px] text-wb-muted">
          {t('expectation.confidence')}
          <select
            data-testid="expectation-confidence"
            value={confidence}
            onChange={(event) =>
              setConfidence(event.target.value as 'low' | 'medium' | 'high')
            }
            className="ml-2 rounded border border-wb-line bg-wb-surface px-2 py-1 text-[12px] text-wb-ink"
          >
            <option value="low">{t('expectation.conf.low')}</option>
            <option value="medium">{t('expectation.conf.medium')}</option>
            <option value="high">{t('expectation.conf.high')}</option>
          </select>
        </label>
        <button
          type="button"
          data-testid="expectation-save"
          disabled={busy || !text.trim()}
          onClick={() => {
            void save()
          }}
          className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
        >
          {t('expectation.save')}
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
  const { t } = useT()
  const [busy, setBusy] = useState(false)
  const definitions = space.definitions ?? []
  const runLabel = running
    ? progress
      ? t('spec.running', { done: progress.done, total: progress.total })
      : t('spec.runningIndeterminate')
    : t('spec.run')
  return (
    <section data-testid="spec-space" className="space-y-3">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
            {t('spec.kicker')}
          </p>
          <h2 className="mt-1 font-serif text-[1.35rem] text-ink">{t('spec.title')}</h2>
          <p className="mt-1 text-[13px] text-wb-muted">
            {space.frozen_at
              ? t('spec.frozenAt', { time: new Date(space.frozen_at).toLocaleString() })
              : t('spec.confirmBefore')}
          </p>
          <TaskHelp
            testId="help-confirm-plans"
            summary={t('spec.helpFreeze')}
            details={t('spec.helpFreezeMore')}
          />
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
          {space.frozen_at ? t('spec.frozen') : t('spec.freeze')}
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
            ? t('spec.runStatus', { done: progress.done, total: progress.total })
            : t('spec.runStatusIndeterminate')}
        </p>
      ) : null}
      {failure ? (
        <div
          data-testid="spec-space-run-error"
          role="alert"
          className="flex flex-wrap items-center gap-3 rounded-md border border-wb-danger/30 bg-wb-danger-soft px-3 py-2"
        >
          <p className="text-[12px] text-wb-danger">
            {t('spec.runFailed', { category: failure.category })}
          </p>
          {onRetryRun ? (
            <button
              type="button"
              data-testid="spec-space-run-retry"
              onClick={onRetryRun}
              className="wb-press rounded-md border border-wb-line bg-wb-surface px-2.5 py-1 text-[12px] text-wb-ink"
            >
              {t('spec.retry')}
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
              {item.admissible ? item.user_decision : t('spec.unavailable')}
            </p>
          </li>
        ))}
      </ul>
    </section>
  )
}
