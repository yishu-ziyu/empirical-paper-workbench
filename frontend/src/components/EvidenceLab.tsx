import { useEffect, useMemo, useState, type Ref } from 'react'
import type { ResearchLab } from '../lib/workspace'
import { useAgentCursor } from '../lib/agentCursor/context'
import { useSemanticTarget, useSemanticTargets } from '../lib/agentCursor/useSemanticTarget'
import { TARGET } from '../lib/agentCursor/scripts'

type SpecRun = NonNullable<ResearchLab['specification_runs']>[number]

const DIMS = [
  { key: 'estimator', label: 'Method' },
  { key: 'experience', label: 'Experience' },
  { key: 'region', label: 'Region' },
  { key: 'demographics', label: 'Demographics' },
] as const

function choiceValue(run: SpecRun, dimension: string): string {
  const hit = (run.choices ?? []).find((item) => item.dimension === dimension)
  return hit?.value || '—'
}

function comparableIds(runs: SpecRun[]): { ols: string; iv: string } {
  const ids = new Set(runs.map((run) => run.spec_id))
  if (ids.has('ols_region_dummies') && ids.has('iv_region_dummies')) {
    return { ols: 'ols_region_dummies', iv: 'iv_region_dummies' }
  }
  return { ols: 'ols_full_controls', iv: 'iv_nearc4_full' }
}

function semanticId(run: SpecRun, comparable: { ols: string; iv: string }): string | null {
  if (run.spec_id === comparable.ols) return TARGET.ols
  if (run.spec_id === comparable.iv) return TARGET.iv
  return null
}

function semanticIdsFor(run: SpecRun, comparable: { ols: string; iv: string }): string[] {
  const ids: string[] = []
  const primary = semanticId(run, comparable)
  if (primary) ids.push(primary)
  const experience = (run.choices ?? []).find((item) => item.dimension === 'experience')?.value
  const estimator = (run.choices ?? []).find((item) => item.dimension === 'estimator')?.value || run.method
  if (experience === 'linear' && estimator === 'ols' && !ids.includes(TARGET.experienceLinear)) {
    ids.push(TARGET.experienceLinear)
  }
  if (experience === 'quadratic' && run.spec_id === comparable.ols) {
    ids.push(TARGET.experienceQuadratic)
  }
  return ids
}

export function compareRuns(a: SpecRun, b: SpecRun) {
  const coefA = typeof a.coef === 'number' ? a.coef : null
  const coefB = typeof b.coef === 'number' ? b.coef : null
  const deltaAbs = coefA == null || coefB == null ? null : coefB - coefA
  const deltaPct =
    deltaAbs == null || coefA == null ? null : (deltaAbs / Math.max(Math.abs(coefA), 1e-6)) * 100
  const dims = Array.from(
    new Set([...(a.choices ?? []), ...(b.choices ?? [])].map((item) => item.dimension).filter(Boolean)),
  )
  const changed: Array<{ dimension: string; a?: string; b?: string }> = []
  const unchanged: Array<{ dimension: string; a?: string; b?: string }> = []
  for (const dim of dims) {
    const left = choiceValue(a, dim)
    const right = choiceValue(b, dim)
    const row = { dimension: dim, a: left, b: right }
    if (left !== right) changed.push(row)
    else unchanged.push(row)
  }
  const changedDims = new Set(changed.map((item) => item.dimension))
  let why = 'Little changed'
  if (changedDims.has('estimator') || changedDims.has('identification')) {
    why = 'Identification strategy changed'
  } else if (changedDims.has('experience')) {
    why = 'Experience functional form changed'
  } else if (changedDims.has('region')) {
    why = 'Region controls changed'
  } else if (changedDims.has('demographics')) {
    why = 'Demographic controls changed'
  }
  return { coefA, coefB, deltaAbs, deltaPct, changed, unchanged, why }
}

function formatCoef(value: number | null | undefined): string {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—'
  return value.toFixed(4)
}

function ChoiceHeader({
  dimKey,
  label,
}: {
  dimKey: string
  label: string
}) {
  const semantic =
    dimKey === 'estimator' ? TARGET.estimator : dimKey === 'experience' ? TARGET.experience : null
  const ref = useSemanticTarget(semantic)
  return (
    <th
      ref={ref as Ref<HTMLTableCellElement>}
      data-semantic-id={semantic ?? undefined}
      data-testid={semantic ? `evidence-choice-${dimKey}` : undefined}
      className="px-3 py-2"
    >
      {label}
    </th>
  )
}

function SpecPoint({
  semanticIds,
  testId,
  isCanonical,
  isSelected,
  isHovered,
  faded,
  cx,
  cy,
  se,
  coef,
  axisX,
  estimator,
  label,
  onToggle,
  onEnter,
  onLeave,
}: {
  semanticIds: string[]
  testId: string
  isCanonical: boolean
  isSelected: boolean
  isHovered: boolean
  faded: boolean
  cx: number
  cy: number
  se: number | null
  coef: number
  axisX: (value: number) => number
  estimator: string
  label: string
  onToggle: () => void
  onEnter: () => void
  onLeave: () => void
}) {
  const ref = useSemanticTargets(semanticIds)
  const ci = se != null ? 1.96 * se : null
  return (
    <g
      ref={ref as Ref<SVGGElement>}
      id={semanticIds[0]}
      data-semantic-id={semanticIds[0]}
      data-testid={testId}
      onClick={onToggle}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      className="cursor-pointer"
      opacity={faded ? 0.28 : 1}
    >
      {ci != null ? (
        <line
          x1={axisX(coef - ci)}
          x2={axisX(coef + ci)}
          y1={cy}
          y2={cy}
          className="stroke-wb-line-strong"
          strokeWidth={1.5}
        />
      ) : null}
      <circle
        cx={cx}
        cy={cy}
        r={isCanonical || isSelected ? 6.5 : 5}
        className={
          isCanonical
            ? 'fill-wb-ink'
            : estimator === 'iv'
              ? 'fill-wb-primary'
              : 'fill-wb-muted'
        }
        opacity={isHovered || isSelected || isCanonical ? 1 : 0.85}
      />
      {isHovered ? (
        <text x={cx + 8} y={cy - 8} fontSize="11" className="fill-wb-ink">
          {label} · {formatCoef(coef)}
        </text>
      ) : null}
    </g>
  )
}

type ClaimLedger = NonNullable<ResearchLab['claim']>

function ClaimLedgerSection({
  claim,
  busy,
  onApprove,
  onPreparePaper,
}: {
  claim: ClaimLedger
  busy: boolean
  onApprove?: (claimId: string) => Promise<void>
  onPreparePaper?: () => Promise<void>
}) {
  return (
    <section
      id="claim-ledger"
      data-testid="claim-ledger"
      className="rounded-md border border-wb-line bg-wb-surface px-3 py-3"
    >
      <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
        Claim Ledger · 主张账本
      </p>
      <p data-testid="claim-text" className="mt-2 font-serif text-[1.15rem] leading-7 text-wb-ink">
        {claim.claim_text || claim.supported_wording}
      </p>
      <dl className="mt-3 space-y-2 text-[13px] leading-6">
        <div>
          <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-wb-faint">
            Supported
          </dt>
          <dd data-testid="claim-supported" className="text-wb-ink">
            {claim.supported_wording}
          </dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-wb-faint">
            Conditionally supported
          </dt>
          <dd data-testid="claim-conditional" className="text-wb-muted">
            {claim.conditionally_supported_wording}
          </dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-wb-faint">
            Unsupported
          </dt>
          <dd data-testid="claim-unsupported" className="text-wb-faint">
            {claim.unsupported_wording}
          </dd>
        </div>
      </dl>
      {claim.unresolved_assumptions && claim.unresolved_assumptions.length > 0 ? (
        <p className="mt-3 text-[12px] leading-5 text-wb-muted">
          Unresolved: {claim.unresolved_assumptions.join(' · ')}
        </p>
      ) : null}
      {claim.approved_by_user ? (
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <p data-testid="claim-approved" className="text-[12px] text-wb-muted">
            Approved
          </p>
          {onPreparePaper ? (
            <button
              type="button"
              data-testid="claim-write-results"
              disabled={busy}
              onClick={() => {
                void onPreparePaper()
              }}
              className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
            >
              Write Results
            </button>
          ) : null}
        </div>
      ) : (
        <button
          type="button"
          data-testid="claim-approve"
          disabled={busy || !onApprove || !claim.id}
          onClick={() => {
            if (!onApprove || !claim.id) return
            void onApprove(claim.id)
          }}
          className="wb-press mt-3 rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
        >
          Approve claim
        </button>
      )}
    </section>
  )
}

export default function EvidenceLab({
  research,
  onPromote,
  onRevert,
  onAcceptChallenge,
  onApproveClaim,
  onPreparePaper,
}: {
  research: ResearchLab
  onPromote?: (runId: string) => Promise<void>
  onRevert?: () => Promise<void>
  onAcceptChallenge?: (challengeId: string) => Promise<void>
  onApproveClaim?: (claimId: string) => Promise<void>
  onPreparePaper?: () => Promise<void>
}) {
  const runs = (research.specification_runs ?? []).filter((run) => run.status !== 'error')
  const comparable = comparableIds(runs)
  const [selected, setSelected] = useState<string[]>([])
  const [hovered, setHovered] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const cursor = useAgentCursor()

  const selectedRuns = selected
    .map((id) => runs.find((run) => run.id === id || run.spec_id === id))
    .filter((run): run is SpecRun => Boolean(run))
  const comparison =
    selectedRuns.length === 2 ? compareRuns(selectedRuns[0], selectedRuns[1]) : null

  useEffect(() => {
    const pair = cursor.presentation.comparePair
    if (!pair || cursor.presentation.status === 'idle') return
    const mapped = pair
      .map((sid) => runs.find((run) => semanticIdsFor(run, comparable).includes(sid)))
      .filter((run): run is SpecRun => Boolean(run))
    if (mapped.length === 2) {
      setSelected([mapped[0].id, mapped[1].id])
    }
  }, [comparable, cursor.presentation.comparePair, cursor.presentation.status, runs])

  useEffect(() => {
    if (!comparison) {
      cursor.reportDelta(null)
      return
    }
    cursor.reportDelta({ deltaAbs: comparison.deltaAbs, deltaPct: comparison.deltaPct })
  }, [comparison, cursor])

  const toggle = (run: SpecRun) => {
    setSelected((current) => {
      if (current.includes(run.id)) return current.filter((id) => id !== run.id)
      if (current.length >= 2) return [current[1], run.id]
      return [...current, run.id]
    })
  }

  const points = useMemo(() => {
    const coefs = runs
      .map((run) => run.coef)
      .filter((value): value is number => typeof value === 'number')
    const min = coefs.length ? Math.min(...coefs) : 0
    const max = coefs.length ? Math.max(...coefs) : 1
    const pad = Math.max((max - min) * 0.15, 0.01)
    const lo = min - pad
    const hi = max + pad
    const width = 640
    const height = 220
    const left = 56
    const right = 24
    const top = 28
    const innerW = width - left - right
    const x = (coef: number) => left + ((coef - lo) / (hi - lo)) * innerW
    const ols = runs.filter((run) => choiceValue(run, 'estimator') === 'ols' || run.method === 'ols')
    const iv = runs.filter((run) => choiceValue(run, 'estimator') === 'iv' || run.method === 'iv')
    const place = (group: SpecRun[], lane: number) =>
      group.map((run, index) => {
        const coef = typeof run.coef === 'number' ? run.coef : 0
        const se = typeof run.se === 'number' ? run.se : null
        const y = top + 50 + lane * 80 + (index - (group.length - 1) / 2) * 10
        return { run, cx: x(coef), cy: y, se, coef }
      })
    return {
      width,
      height,
      left,
      x,
      lo,
      hi,
      placed: [...place(ols, 0), ...place(iv, 1)],
      lanes: [
        { label: 'OLS', y: top + 50 },
        { label: 'IV', y: top + 130 },
      ],
    }
  }, [runs])

  const surprise = research.surprise
  const challenge = research.next_challenge as
    | {
        id?: string
        rationale?: string
        status?: string
        target?: string
      }
    | null
    | undefined

  const claim = research.claim ?? research.claims?.[0]

  return (
    <section data-testid="evidence-lab" className="mx-auto max-w-[52rem] space-y-6 px-6 py-8">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          Evidence Lab · 证据实验室
        </p>
        <h2 className="mt-1 font-serif text-[1.35rem] text-wb-ink">
          {claim ? 'Claim Ledger' : 'Results space'}
        </h2>
      </header>

      {claim ? (
        <ClaimLedgerSection
          claim={claim}
          busy={busy}
          onApprove={onApproveClaim}
          onPreparePaper={onPreparePaper}
        />
      ) : null}

      {surprise ? (
        <div
          data-testid="evidence-surprise"
          className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">Surprise</p>
          <p className="mt-1 text-[14px] text-wb-ink">{surprise.status}</p>
          {surprise.expected ? (
            <p className="mt-1 text-[12px] text-wb-muted">Expected: {surprise.expected}</p>
          ) : null}
          {surprise.observed ? (
            <p className="text-[12px] text-wb-muted">Observed: {surprise.observed}</p>
          ) : null}
        </div>
      ) : null}

      <svg
        data-testid="evidence-results-space"
        viewBox={`0 0 ${points.width} ${points.height}`}
        className="w-full rounded-md border border-wb-line bg-wb-surface"
        role="img"
        aria-label="Specification coefficients"
      >
        {points.lanes.map((lane) => (
          <text
            key={lane.label}
            x={12}
            y={lane.y + 4}
            className="fill-wb-muted"
            fontSize="11"
          >
            {lane.label}
          </text>
        ))}
        {points.placed.map(({ run, cx, cy, se, coef }) => {
          const ids = semanticIdsFor(run, comparable)
          const semantic = ids[0]
          const isCanonical =
            run.relation === 'canonical' || run.spec_id === research.canonical_spec_id
          const isSelected = selected.includes(run.id)
          const isHovered = hovered === run.id
          const testId =
            semantic === TARGET.ols
              ? 'evidence-spec-ols'
              : semantic === TARGET.iv
                ? 'evidence-spec-iv'
                : `evidence-spec-${run.spec_id}`
          const faded =
            cursor.presentation.fadeUnchanged &&
            Boolean(cursor.presentation.comparePair) &&
            !isSelected &&
            !ids.some((id) => cursor.presentation.highlighted.includes(id))
          return (
            <SpecPoint
              key={run.id}
              semanticIds={ids}
              testId={testId}
              isCanonical={isCanonical}
              isSelected={isSelected}
              isHovered={isHovered}
              faded={faded}
              cx={cx}
              cy={cy}
              se={se}
              coef={coef}
              axisX={points.x}
              estimator={
                (run.choices ?? []).find((item) => item.dimension === 'estimator')?.value ||
                run.method ||
                ''
              }
              label={run.label || run.spec_id}
              onToggle={() => toggle(run)}
              onEnter={() => setHovered(run.id)}
              onLeave={() => setHovered(null)}
            />
          )
        })}
      </svg>

      <section data-testid="evidence-choice-matrix">
        <h3 className="mb-2 font-serif text-[1.1rem] text-wb-ink">Choice matrix</h3>
        <div className="overflow-x-auto rounded-md border border-wb-line">
          <table className="w-full text-left text-[12px]">
            <thead className="bg-wb-subtle font-mono text-[10px] uppercase tracking-[0.12em] text-wb-faint">
              <tr>
                <th className="px-3 py-2">Spec</th>
                {DIMS.map((dim) => (
                  <ChoiceHeader key={dim.key} dimKey={dim.key} label={dim.label} />
                ))}
                <th className="px-3 py-2">β</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => {
                const isSelected = selected.includes(run.id)
                return (
                  <tr
                    key={run.id}
                    data-testid={`evidence-matrix-${run.spec_id}`}
                    onClick={() => toggle(run)}
                    className={`cursor-pointer border-t border-wb-line ${
                      isSelected ? 'bg-wb-subtle' : 'bg-wb-surface'
                    }`}
                  >
                    <td className="px-3 py-2 text-wb-ink">{run.label || run.spec_id}</td>
                    {DIMS.map((dim) => {
                      const unchanged =
                        cursor.presentation.fadeUnchanged &&
                        comparison?.unchanged.some((item) => item.dimension === dim.key)
                      return (
                        <td
                          key={dim.key}
                          className={`px-3 py-2 text-wb-muted ${unchanged ? 'opacity-40' : ''}`}
                        >
                          {choiceValue(run, dim.key)}
                        </td>
                      )
                    })}
                    <td className="px-3 py-2 font-mono tabular-nums text-wb-ink">
                      {formatCoef(run.coef)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section data-testid="evidence-compare" className="rounded-md border border-wb-line bg-wb-surface px-3 py-3">
        <h3 className="font-serif text-[1.1rem] text-wb-ink">Compare</h3>
        {comparison && selectedRuns.length === 2 ? (
          <div className="mt-2 space-y-1 text-[13px] leading-6 text-wb-ink">
            <p data-testid="evidence-compare-delta">
              βA → βB {formatCoef(comparison.coefA)} → {formatCoef(comparison.coefB)}
              {comparison.deltaAbs != null ? ` · Δ ${comparison.deltaAbs.toFixed(4)}` : ''}
              {comparison.deltaPct != null ? ` · ${comparison.deltaPct.toFixed(1)}%` : ''}
            </p>
            <p data-testid="evidence-compare-intent">
              {cursor.presentation.intent === 'Little changed' ? 'Little changed' : comparison.why}
            </p>
            <p className="text-[12px] text-wb-muted">
              Changed: {comparison.changed.map((item) => item.dimension).join(', ') || 'none'}
            </p>
            <p className="text-[12px] text-wb-muted">
              Unchanged: {comparison.unchanged.map((item) => item.dimension).join(', ') || 'none'}
            </p>
          </div>
        ) : (
          <p className="mt-2 text-[13px] text-wb-muted">Select two specifications to compare.</p>
        )}
      </section>

      {selectedRuns[0] ? (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            data-testid="evidence-promote"
            disabled={busy || !onPromote}
            onClick={() => {
              if (!onPromote || !selectedRuns[0]) return
              setBusy(true)
              void onPromote(selectedRuns[0].id).finally(() => setBusy(false))
            }}
            className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
          >
            Promote to canonical
          </button>
          <button
            type="button"
            data-testid="evidence-revert"
            disabled={busy || !onRevert}
            onClick={() => {
              if (!onRevert) return
              setBusy(true)
              void onRevert().finally(() => setBusy(false))
            }}
            className="wb-press rounded-md border border-wb-line px-3 py-1.5 text-[12px] text-wb-ink disabled:opacity-50"
          >
            Revert canonical
          </button>
        </div>
      ) : null}

      {cursor.presentation.previewCommand ? (
        <section
          data-testid="agent-cursor-preview-proposal"
          className="rounded-md border border-dashed border-wb-line bg-wb-subtle px-3 py-3"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
            Preview proposal
          </p>
          <p className="mt-1 text-[13px] leading-6 text-wb-ink">
            Experience: quadratic → linear. Canonical estimate is unchanged until you promote.
          </p>
        </section>
      ) : null}

      {research.teaching_case &&
      (cursor.presentation.status === 'idle' ||
        cursor.presentation.status === 'done' ||
        cursor.presentation.status === 'aborted') ? (
        <section
          data-testid="evidence-challenge-experience"
          className="rounded-md border border-wb-line bg-wb-surface px-3 py-3"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
            Experience form
          </p>
          <p className="mt-1 text-[13px] leading-6 text-wb-ink">
            Experience may enter linearly or as a quadratic.
          </p>
          <button
            type="button"
            data-testid="agent-cursor-show-preview"
            data-agent-cursor-control=""
            onClick={cursor.playChallengeExperience}
            className="wb-press mt-2 rounded-md border border-wb-line px-3 py-1.5 text-[12px] text-wb-ink"
          >
            Show preview
          </button>
        </section>
      ) : null}

      {challenge?.id ? (
        <section
          data-testid="evidence-challenge"
          className="rounded-md border border-wb-line bg-wb-surface px-3 py-3"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
            Next-best challenge
          </p>
          <p className="mt-1 text-[13px] leading-6 text-wb-ink">{challenge.rationale}</p>
          {challenge.status !== 'accepted' ? (
            <button
              type="button"
              data-testid="evidence-challenge-accept"
              disabled={busy || !onAcceptChallenge}
              onClick={() => {
                if (!onAcceptChallenge || !challenge.id) return
                setBusy(true)
                void onAcceptChallenge(challenge.id).finally(() => setBusy(false))
              }}
              className="wb-press mt-2 rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
            >
              Accept challenge
            </button>
          ) : (
            <p className="mt-1 text-[12px] text-wb-muted">Accepted</p>
          )}
        </section>
      ) : null}
    </section>
  )
}
