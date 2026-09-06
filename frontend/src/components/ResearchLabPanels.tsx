import { useEffect, useState } from 'react'
import type { ResearchLab } from '../lib/workspace'

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

export function ExpectationEditor({
  expectation,
  onSave,
}: {
  expectation: NonNullable<ResearchLab['expectation']>
  onSave: (payload: { text: string; confidence: 'low' | 'medium' | 'high' }) => Promise<void>
}) {
  const [text, setText] = useState(expectation.text || '')
  const [confidence, setConfidence] = useState<'low' | 'medium' | 'high'>(
    expectation.confidence || 'medium',
  )
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    setText(expectation.text || '')
    setConfidence(expectation.confidence || 'medium')
  }, [expectation.text, expectation.confidence, expectation.version])

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
            setBusy(true)
            void onSave({ text: text.trim(), confidence }).finally(() => setBusy(false))
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
}: {
  space: NonNullable<ResearchLab['specification_space']>
  onFreeze: () => Promise<void>
  onRun?: () => Promise<void>
}) {
  const [busy, setBusy] = useState(false)
  const definitions = space.definitions ?? []
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
          disabled={busy || Boolean(space.frozen_at)}
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
            disabled={busy}
            onClick={() => {
              setBusy(true)
              void onRun().finally(() => setBusy(false))
            }}
            className="wb-press rounded-md border border-wb-line px-3 py-1.5 text-[12px] text-wb-ink disabled:opacity-50"
          >
            Run specifications
          </button>
        ) : null}
        </div>
      </header>
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
