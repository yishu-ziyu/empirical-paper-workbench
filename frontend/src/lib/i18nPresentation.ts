/** Display adapters for teaching-case research objects. Never write back. */

import type { Lang, Translate } from './i18n'

type MetricRef = {
  metric?: string | null
  estimator?: string | null
  spec_id?: string | null
  label?: string | null
}

type CriterionLike = {
  kind?: string | null
  operator?: string | null
  left?: MetricRef | null
  right?: MetricRef | number | null
  label?: string | null
  tolerance?: { abs?: number | null; rel?: number | null } | null
}

type ChangedDim = { dimension?: string; a?: string; b?: string }

/** Backend display-only mirror of one resolved criterion side. */
type CriterionOutcomeRef = {
  source?: 'metric' | 'constant' | null
  metric?: string | null
  estimator?: string | null
  spec_id?: string | null
  run_id?: string | null
  value?: number | null
}

type CriterionOutcomeLike = {
  id?: string | null
  outcome?: 'satisfied' | 'violated' | 'unresolved' | null
  kind?: string | null
  operator?: string | null
  left?: CriterionOutcomeRef | null
  right?: CriterionOutcomeRef | null
  tolerance?: { abs?: number | null; rel?: number | null } | null
}

type SurpriseLike = {
  status?: string | null
  criterion_outcomes?: CriterionOutcomeLike[] | null
} | null

export const CARD_SPEC_IDS = [
  'ols_linear_exper',
  'ols_quadratic_exper',
  'ols_demographics',
  'ols_urban_south',
  'ols_full_controls',
  'iv_nearc4',
  'iv_nearc4_linear',
  'iv_nearc4_quadratic',
  'iv_nearc4_demographics',
  'iv_nearc4_urban_south',
  'iv_nearc4_full',
  'ols_region_dummies',
  'iv_region_dummies',
] as const

const ASSUMPTION_KEYS: Record<string, string> = {
  'IV exclusion restriction': 'presentation.assumption.exclusion',
  monotonicity: 'presentation.assumption.monotonicity',
  'LATE is not ATE': 'presentation.assumption.lateNotAte',
}

function lookup(t: Translate, key: string): string | null {
  const value = t(key)
  return value === key ? null : value
}

function isCard(teachingCase?: string | null, questionId?: string | null): boolean {
  return teachingCase === 'card_1995' || Boolean(questionId && questionId.startsWith('card_1995'))
}

export function displayEstimand(
  kind: 'ols' | 'iv',
  t: Translate,
  opts?: { teachingCase?: string | null; questionId?: string | null },
): string {
  if (isCard(opts?.teachingCase, opts?.questionId)) {
    return lookup(t, `presentation.estimand.card.${kind}`) ?? t(`presentation.estimand.${kind}`)
  }
  return t(`presentation.estimand.${kind}`)
}

function estimatorWord(estimator: string | null | undefined, t: Translate): string {
  const key = String(estimator || '').toLowerCase()
  if (key === 'iv') return t('presentation.estimator.iv')
  if (key === 'ols') return t('presentation.estimator.ols')
  if (estimator) return estimator.toUpperCase()
  return t('presentation.estimator.metric')
}

/** Compact number for constants and tolerances: 0.1 stays 0.1, 0.02 stays 0.02. */
function formatCompactNumber(value: number): string {
  if (!Number.isFinite(value)) return String(value)
  const rounded = Math.round(value * 1e6) / 1e6
  return String(rounded)
}

/** rel 0.05 -> "5%", 0.25 -> "25%", 0.125 -> "12.5%". */
function formatRelTolerance(rel: number): string {
  if (!Number.isFinite(rel)) return `${rel}%`
  const pct = rel * 100
  return `${Math.round(pct * 100) / 100}%`
}

/**
 * Effective tolerance text, matching the backend judgment exactly:
 * both slots empty means the backend default rel=0.25 is in force
 * (research_lab.py distance branch) — show that, never a different one.
 */
function toleranceText(
  tolerance: { abs?: number | null; rel?: number | null } | null | undefined,
): string | null {
  let abs = typeof tolerance?.abs === 'number' ? tolerance.abs : null
  let rel = typeof tolerance?.rel === 'number' ? tolerance.rel : null
  if (abs == null && rel == null) rel = 0.25
  const parts: string[] = []
  if (abs != null) parts.push(`±${formatCompactNumber(abs)}`)
  if (rel != null) parts.push(`±${formatRelTolerance(rel)}`)
  return parts.length ? parts.join(' / ') : null
}

function rightHandText(
  right: MetricRef | number | null | undefined,
  t: Translate,
): string | null {
  if (right == null) return null
  if (typeof right === 'object') return estimatorWord(right.estimator, t)
  return formatCompactNumber(right)
}

export function displayCriterionLabel(criterion: CriterionLike | null | undefined, t: Translate): string {
  if (!criterion) return t('presentation.criterion.missing')
  const left = estimatorWord(
    typeof criterion.left === 'object' ? criterion.left?.estimator : undefined,
    t,
  )
  const kind = String(criterion.kind || '')
  const operator = String(criterion.operator || '')
  const right = rightHandText(criterion.right, t)
  if (kind === 'ordering' && right != null) {
    if (operator === 'lt') return `${left} < ${right}`
    if (operator === 'gt') return `${left} > ${right}`
    if (operator === 'eq') return `${left} = ${right}`
  }
  if (kind === 'sign') {
    if (operator === 'positive') return t('presentation.criterion.positive', { left })
    if (operator === 'negative') return t('presentation.criterion.negative', { left })
  }
  if (kind === 'distance' && right != null) {
    const tol = toleranceText(criterion.tolerance)
    const base = t('presentation.criterion.approx', { left, right })
    return tol ? `${base} ${tol}` : base
  }
  // No friendly localized shape for this combination: keep the stored
  // original condition visible instead of silently dropping it.
  const generic = t('presentation.criterion.generic')
  const label = typeof criterion.label === 'string' ? criterion.label.trim() : ''
  return label ? `${generic} · ${label}` : generic
}

/**
 * Identity of the specification each side points at. Display channel for
 * "same estimator, different spec" — the label alone says "IV estimate"
 * for both iv_nearc4_full and iv_region_dummies; the spec_id is the
 * authoritative selector and must stay viewable.
 */
export function criterionSpecIdentities(
  criterion: CriterionLike | null | undefined,
): { left: string | null; right: string | null } {
  const leftRef = criterion?.left && typeof criterion.left === 'object' ? criterion.left : null
  const rightRef =
    criterion?.right && typeof criterion.right === 'object' ? criterion.right : null
  return {
    left: (leftRef?.spec_id && String(leftRef.spec_id)) || null,
    right: (rightRef?.spec_id && String(rightRef.spec_id)) || null,
  }
}

export function displaySpecLabel(
  specId: string | null | undefined,
  t: Translate,
  lang: Lang,
  stored?: string | null,
): string {
  if (!specId) return stored || '—'
  const hit = lookup(t, `presentation.spec.${specId}.label`)
  if (hit) return hit
  return lang === 'en' ? stored || specId : specId
}

export function displaySpecRationale(
  specId: string | null | undefined,
  t: Translate,
  lang: Lang,
  stored?: string | null,
): string {
  if (!specId) return stored || ''
  const hit = lookup(t, `presentation.spec.${specId}.rationale`)
  if (hit) return hit
  return lang === 'en' ? stored || '' : ''
}

export function displayDimension(dimension: string | undefined, t: Translate): string {
  if (!dimension) return t('evidence.none')
  return lookup(t, `evidence.dim.${dimension}`) ?? dimension
}

export function displayCompareWhy(changed: ChangedDim[] | undefined, t: Translate): string {
  const dims = new Set((changed ?? []).map((item) => item.dimension).filter(Boolean) as string[])
  if (dims.size === 0) return t('presentation.why.little')
  if (dims.has('estimator') || dims.has('identification')) {
    return t('presentation.why.identification')
  }
  if (dims.has('experience')) return t('presentation.why.experience')
  if (dims.has('region')) return t('presentation.why.region')
  if (dims.has('demographics')) return t('presentation.why.demographics')
  return t('presentation.why.little')
}

function formatCoef(value: number): string {
  return value.toFixed(4)
}

export function displaySurpriseExpected(
  criteria: CriterionLike[] | undefined,
  t: Translate,
): string | null {
  if (!criteria || criteria.length === 0) return null
  return criteria.map((item) => displayCriterionLabel(item, t)).join(' · ')
}

/**
 * Observed values come ONLY from the backend evaluator's structured
 * criterion_outcomes (run_id + value it actually read). The frontend
 * never selects runs or coefs itself; unresolved outcomes contribute
 * nothing and are never filled from another metric's numbers.
 */
export function displaySurpriseObserved(
  surprise: SurpriseLike,
  t: Translate,
): string | null {
  const outcomes = surprise?.criterion_outcomes
  if (!outcomes || outcomes.length === 0) return null
  const parts: string[] = []
  for (const outcome of outcomes) {
    if (!outcome || outcome.outcome === 'unresolved') continue
    const left = outcome.left
    if (!left || typeof left.value !== 'number') continue
    const leftText = `${estimatorWord(left.estimator, t)} ${formatCoef(left.value)}`
    const right = outcome.right
    if (!right || typeof right.value !== 'number') {
      parts.push(leftText)
      continue
    }
    const cmp = left.value > right.value ? '>' : left.value < right.value ? '<' : '='
    const rightText =
      right.source === 'constant'
        ? formatCoef(right.value)
        : `${estimatorWord(right.estimator, t)} ${formatCoef(right.value)}`
    parts.push(`${leftText} ${cmp} ${rightText}`)
  }
  return parts.length ? parts.join(' · ') : null
}

/**
 * Map the backend's actual claim evidence_status set — supported /
 * insufficient / draft / approved, plus the display branches
 * conditional / unsupported — onto honest localized wording. Missing
 * or unknown values stay conservatively neutral: no affirmation, no
 * denial, and never the supported wording.
 */
const CLAIM_STATUS_KEYS: Record<string, string> = {
  supported: 'presentation.claim.card.supported',
  conditional: 'presentation.claim.card.conditional',
  unsupported: 'presentation.claim.card.unsupported',
  insufficient: 'presentation.claim.card.insufficient',
  draft: 'presentation.claim.card.draft',
  approved: 'presentation.claim.card.approved',
}

export function displayClaimExplanation(
  evidenceStatus: string | undefined,
  t: Translate,
  teachingCase?: string | null,
): string | null {
  if (teachingCase !== 'card_1995') return null
  const key = CLAIM_STATUS_KEYS[String(evidenceStatus ?? '').trim()]
  return t(key ?? 'presentation.claim.card.unknown')
}

export function displayAssumption(raw: string, t: Translate): string {
  const exact = ASSUMPTION_KEYS[raw]
  if (exact) return t(exact)
  const lower = raw.toLowerCase()
  if (lower.startsWith('iv exclusion')) return t('presentation.assumption.exclusion')
  if (lower.startsWith('monotonicity')) return t('presentation.assumption.monotonicity')
  if (lower.includes('late is not ate') || lower.startsWith('late ')) {
    return t('presentation.assumption.lateNotAte')
  }
  if (lower.includes('instrument strength')) return t('presentation.assumption.strength')
  return raw
}
