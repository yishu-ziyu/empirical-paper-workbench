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

function visualDelta(a: SpecRun, b: SpecRun) {
  const coefA = typeof a.coef === 'number' ? a.coef : null
  const coefB = typeof b.coef === 'number' ? b.coef : null
  const deltaAbs = coefA == null || coefB == null ? null : coefB - coefA
  const deltaPct =
    deltaAbs == null || coefA == null ? null : (deltaAbs / Math.max(Math.abs(coefA), 1e-6)) * 100
  return { coefA, coefB, deltaAbs, deltaPct }
}

type CompareModel = {
  coef_a?: number | null
  coef_b?: number | null
  delta_abs?: number | null
  delta_pct?: number | null
  changed?: Array<{ dimension?: string; a?: string; b?: string }>
  unchanged?: Array<{ dimension?: string; a?: string; b?: string }>
  why_moved?: string | null
  intent?: string | null
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
  mismatch,
  onApprove,
  onPreparePaper,
  onPromoteSupporting,
  onReviewEvidence,
}: {
  claim: ClaimLedger
  busy: boolean
  mismatch: boolean
  onApprove?: (claimId: string) => Promise<void>
  onPreparePaper?: () => Promise<void>
  onPromoteSupporting?: () => Promise<void>
  onReviewEvidence?: () => Promise<void>
}) {
  const stale = Boolean(claim.stale)
  return (
    <section
      id="claim-ledger"
      data-testid="claim-ledger"
      className="rounded-md border border-wb-line bg-wb-surface px-3 py-3"
    >
      <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
        Claim Ledger（结论账本）
      </p>
      {stale ? (
        <p data-testid="claim-stale" className="mt-2 text-[13px] leading-6 text-wb-ink">
          New evidence available · 结论需要重新审视
        </p>
      ) : null}
      {mismatch && !stale ? (
        <p data-testid="claim-canonical-mismatch" className="mt-2 text-[13px] leading-6 text-wb-ink">
          当前 Claim 依赖 IV specification，但正式主规格不是该 IV。
        </p>
      ) : null}
      <p data-testid="claim-text" className="mt-2 font-serif text-[1.15rem] leading-7 text-wb-ink">
        {claim.claim_text || claim.supported_wording}
      </p>
      <dl className="mt-3 space-y-2 text-[13px] leading-6">
        <div>
          <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-wb-faint">
            Supported（当前证据支持）
          </dt>
          <dd data-testid="claim-supported" className="text-wb-ink">
            {claim.supported_wording}
          </dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-wb-faint">
            Conditionally supported（有条件支持）
          </dt>
          <dd data-testid="claim-conditional" className="text-wb-muted">
            {claim.conditionally_supported_wording}
          </dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase tracking-[0.12em] text-wb-faint">
            Unsupported（当前证据不支持）
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
      {stale ? (
        <button
          type="button"
          data-testid="claim-review-evidence"
          disabled={busy || !onReviewEvidence}
          onClick={() => {
            void onReviewEvidence?.()
          }}
          className="wb-press mt-3 rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
        >
          Review new evidence
        </button>
      ) : claim.approved_by_user ? (
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <p data-testid="claim-approved" className="text-[12px] text-wb-muted">
            Approved
          </p>
          {mismatch && onPromoteSupporting ? (
            <button
              type="button"
              data-testid="claim-promote-supporting"
              disabled={busy}
              onClick={() => {
                void onPromoteSupporting()
              }}
              className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white disabled:opacity-50"
            >
              Promote supporting specification
            </button>
          ) : null}
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
  onCompare,
  onDraftClaim,
}: {
  research: ResearchLab
  onPromote?: (runId: string) => Promise<void>
  onRevert?: () => Promise<void>
  onAcceptChallenge?: (challengeId: string) => Promise<void>
  onApproveClaim?: (claimId: string) => Promise<void>
  onPreparePaper?: () => Promise<void>
  onCompare?: (a: string, b: string) => Promise<CompareModel | null>
  onDraftClaim?: () => Promise<void>
}) {
  const runs = (research.specification_runs ?? []).filter((run) => run.status !== 'error')
  const [specRunOverrides, setSpecRunOverrides] = useState<Record<string, string>>({})
  const [reviewClaimRequested, setReviewClaimRequested] = useState(false)
  const [hasAcceptedChallenge, setHasAcceptedChallenge] = useState(false)

  const specGroups = useMemo(() => {
    const map = new Map<string, SpecRun[]>()
    for (const run of runs) {
      const list = map.get(run.spec_id) || []
      list.push(run)
      map.set(run.spec_id, list)
    }
    return map
  }, [runs])

  const displayedRuns = useMemo(() => {
    const result: SpecRun[] = []
    for (const [spec_id, groupRuns] of specGroups.entries()) {
      const overrideId = specRunOverrides[spec_id]
      const chosen = groupRuns.find((r) => r.id === overrideId) || groupRuns[groupRuns.length - 1]
      result.push(chosen)
    }
    return result
  }, [specGroups, specRunOverrides])

  const comparable = useMemo(() => comparableIds(displayedRuns), [displayedRuns])
  const [selected, setSelected] = useState<string[]>([])
  const [hovered, setHovered] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [serverCompare, setServerCompare] = useState<CompareModel | null>(null)
  const cursor = useAgentCursor()
  const reportDelta = cursor.reportDelta

  const claim = research.claim ?? research.claims?.[0]
  const requiredSpec = (claim?.provenance as { iv_spec_id?: string } | undefined)?.iv_spec_id
  const mismatch = Boolean(
    claim?.approved_by_user &&
      !claim?.stale &&
      requiredSpec &&
      research.canonical_spec_id !== requiredSpec,
  )
  const supportingRunId =
    (claim?.provenance as { iv_run_id?: string } | undefined)?.iv_run_id ||
    claim?.supporting_run_ids?.[1]

  const challenge = research.next_challenge as
    | {
        id?: string
        rationale?: string
        rationale_zh?: string
        status?: string
        target?: string
      }
    | null
    | undefined

  const isClaimExpanded = Boolean(
    claim?.approved_by_user ||
      reviewClaimRequested ||
      selected.length === 2 ||
      hasAcceptedChallenge ||
      challenge?.status === 'accepted',
  )

  const selectedRuns = selected
    .map((id) => runs.find((run) => run.id === id || run.spec_id === id))
    .filter((run): run is SpecRun => Boolean(run))
  const leftId = selectedRuns[0]?.id
  const rightId = selectedRuns[1]?.id
  const leftCoef = selectedRuns[0]?.coef
  const rightCoef = selectedRuns[1]?.coef
  const comparison = useMemo(() => {
    if (!leftId || !rightId) return null
    const fallback = visualDelta(
      { coef: leftCoef } as SpecRun,
      { coef: rightCoef } as SpecRun,
    )
    return {
      coefA: serverCompare?.coef_a ?? fallback.coefA,
      coefB: serverCompare?.coef_b ?? fallback.coefB,
      deltaAbs: serverCompare?.delta_abs ?? fallback.deltaAbs,
      deltaPct: serverCompare?.delta_pct ?? fallback.deltaPct,
      changed: serverCompare?.changed ?? [],
      unchanged: serverCompare?.unchanged ?? [],
      why: serverCompare?.why_moved || serverCompare?.intent || '',
    }
  }, [leftCoef, leftId, rightCoef, rightId, serverCompare])

  useEffect(() => {
    const pair = cursor.presentation.comparePair
    if (!pair || cursor.presentation.status === 'idle') return
    const mapped = pair
      .map(
        (sid) =>
          displayedRuns.find((run) => semanticIdsFor(run, comparable).includes(sid)) ||
          runs.find((run) => semanticIdsFor(run, comparable).includes(sid)),
      )
      .filter((run): run is SpecRun => Boolean(run))
    if (mapped.length === 2) {
      const nextA = mapped[0].id
      const nextB = mapped[1].id
      setSelected((prev) => {
        if (prev.length === 2 && prev[0] === nextA && prev[1] === nextB) {
          return prev
        }
        return [nextA, nextB]
      })
    }
  }, [comparable, cursor.presentation.comparePair, cursor.presentation.status, displayedRuns, runs])

  useEffect(() => {
    if (!leftId || !rightId || !onCompare) {
      setServerCompare(null)
      return
    }
    let cancelled = false
    void onCompare(leftId, rightId).then((payload) => {
      if (!cancelled) setServerCompare(payload)
    })
    return () => {
      cancelled = true
    }
  }, [leftId, onCompare, rightId])

  const deltaAbs = comparison?.deltaAbs ?? null
  const deltaPct = comparison?.deltaPct ?? null
  useEffect(() => {
    if (deltaAbs == null) {
      reportDelta(null)
      return
    }
    reportDelta({ deltaAbs, deltaPct })
  }, [deltaAbs, deltaPct, reportDelta])

  const toggle = (run: SpecRun) => {
    setSelected((current) => {
      if (current.includes(run.id)) return current.filter((id) => id !== run.id)
      if (current.length >= 2) return [current[1], run.id]
      return [...current, run.id]
    })
  }

  const points = useMemo(() => {
    const coefs = displayedRuns
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
    const ols = displayedRuns.filter(
      (run) => choiceValue(run, 'estimator') === 'ols' || run.method === 'ols',
    )
    const iv = displayedRuns.filter(
      (run) => choiceValue(run, 'estimator') === 'iv' || run.method === 'iv',
    )
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
  }, [displayedRuns])

  const surprise = research.surprise

  return (
    <section data-testid="evidence-lab" className="mx-auto max-w-[52rem] space-y-6 px-6 py-8">
      {/* 1. Header */}
      <header>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          Evidence Lab（证据实验室）
        </p>
        <h2 className="mt-1 font-serif text-[1.35rem] text-wb-ink">
          {isClaimExpanded ? 'Claim Ledger' : 'Results space'}
        </h2>
      </header>

      {/* 2. Surprise */}
      {surprise ? (
        <div
          data-testid="evidence-surprise"
          className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
            Surprise（意外）
          </p>
          <p className="mt-1 text-[14px] text-wb-ink">{surprise.status}</p>
          {surprise.expected ? (
            <p className="mt-1 text-[12px] text-wb-muted">Expected: {surprise.expected}</p>
          ) : null}
          {surprise.observed ? (
            <p className="text-[12px] text-wb-muted">Observed: {surprise.observed}</p>
          ) : null}
        </div>
      ) : null}

      {/* 3. Results Space: Scatter Plot */}
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

      {/* 3. Results Space: Choice Matrix */}
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
              {displayedRuns.map((run) => {
                const groupRuns = specGroups.get(run.spec_id) || [run]
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
                    <td className="px-3 py-2 text-wb-ink">
                      <div className="flex flex-wrap items-center gap-2">
                        <span>{run.label || run.spec_id}</span>
                        {groupRuns.length > 1 ? (
                          <button
                            type="button"
                            data-testid={`evidence-history-${run.spec_id}`}
                            onClick={(e) => {
                              e.stopPropagation()
                              const curIdx = groupRuns.findIndex((r) => r.id === run.id)
                              const nextIdx = (curIdx + 1) % groupRuns.length
                              const nextRun = groupRuns[nextIdx]
                              setSpecRunOverrides((prev) => ({
                                ...prev,
                                [run.spec_id]: nextRun.id,
                              }))
                              setSelected((curr) => {
                                if (curr.includes(run.id)) {
                                  return curr.map((id) => (id === run.id ? nextRun.id : id))
                                }
                                return curr
                              })
                            }}
                            className="rounded border border-wb-line bg-wb-subtle px-1.5 py-0.5 font-mono text-[10px] text-wb-muted hover:text-wb-ink"
                            title={`Switch run (${groupRuns.findIndex((r) => r.id === run.id) + 1}/${groupRuns.length})`}
                          >
                            History {groupRuns.length} (Preview · {groupRuns.length} runs)
                          </button>
                        ) : null}
                      </div>
                    </td>
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

      {/* 4. Compare / Why did it move? */}
      <section
        data-testid="evidence-compare"
        className="rounded-md border border-wb-line bg-wb-surface px-3 py-3"
      >
        <h3 className="font-serif text-[1.1rem] text-wb-ink">Compare（比较）</h3>
        {comparison && selectedRuns.length === 2 ? (
          <div className="mt-2 space-y-1 text-[13px] leading-6 text-wb-ink">
            <p data-testid="evidence-compare-delta">
              βA → βB {formatCoef(comparison.coefA)} → {formatCoef(comparison.coefB)}
              {comparison.deltaAbs != null ? ` · Δ ${comparison.deltaAbs.toFixed(4)}` : ''}
              {comparison.deltaPct != null ? ` · ${comparison.deltaPct.toFixed(1)}%` : ''}
            </p>
            <p data-testid="evidence-compare-intent">
              {comparison.why || '…'}
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

        {selectedRuns[0] ? (
          <div className="mt-3 flex flex-wrap gap-2">
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
      </section>

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

      {/* 5. Next-best Challenge */}
      {challenge?.id ? (
        <section
          data-testid="evidence-challenge"
          className="rounded-md border border-wb-line bg-wb-surface px-3 py-3"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
            Next-best Challenge（下一步最有价值的检验）
          </p>
          <p className="mt-1 text-[13px] leading-6 text-wb-ink">
            {challenge.rationale}
            {challenge.rationale_zh ? (
              <span className="mt-1 block text-[12px] text-wb-muted">
                {challenge.rationale_zh}
              </span>
            ) : null}
          </p>
          {challenge.status !== 'accepted' && !hasAcceptedChallenge ? (
            <button
              type="button"
              data-testid="evidence-challenge-accept"
              disabled={busy || !onAcceptChallenge}
              onClick={() => {
                if (!onAcceptChallenge || !challenge.id) return
                setBusy(true)
                setHasAcceptedChallenge(true)
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

      {/* 6. Claim Ledger */}
      {claim ? (
        <div data-testid="evidence-claim-ledger">
          {!isClaimExpanded ? (
            <section className="rounded-md border border-wb-line bg-wb-surface px-4 py-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
                    Claim Ledger（结论账本）
                  </p>
                  <p className="mt-1 text-[13px] font-medium text-wb-ink">
                    Draft claim ready · 已可以整理结论
                  </p>
                </div>
                <button
                  type="button"
                  data-testid="evidence-review-claim"
                  onClick={() => {
                    setReviewClaimRequested(true)
                    void onDraftClaim?.()
                  }}
                  className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white"
                >
                  Review claim · 整理结论
                </button>
              </div>
            </section>
          ) : (
            <ClaimLedgerSection
              claim={claim}
              busy={busy}
              mismatch={mismatch}
              onApprove={onApproveClaim}
              onPreparePaper={onPreparePaper}
              onPromoteSupporting={
                supportingRunId && onPromote
                  ? async () => {
                      setBusy(true)
                      try {
                        await onPromote(supportingRunId)
                      } finally {
                        setBusy(false)
                      }
                    }
                  : undefined
              }
              onReviewEvidence={
                onDraftClaim
                  ? async () => {
                      setBusy(true)
                      try {
                        await onDraftClaim()
                      } finally {
                        setBusy(false)
                      }
                    }
                  : undefined
              }
            />
          )}
        </div>
      ) : null}
    </section>
  )
}

