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

type SpecRunLike = {
  id?: string | null
  spec_id?: string | null
  method?: string | null
  estimator?: string | null
  coef?: number | null
  status?: string | null
}

type ChangedDim = { dimension?: string; a?: string; b?: string }

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

export function displayCriterionLabel(criterion: CriterionLike | null | undefined, t: Translate): string {
  if (!criterion) return t('presentation.criterion.missing')
  const left = estimatorWord(
    typeof criterion.left === 'object' ? criterion.left?.estimator : undefined,
    t,
  )
  const rightRef = criterion.right && typeof criterion.right === 'object' ? criterion.right : null
  const right = rightRef ? estimatorWord(rightRef.estimator, t) : null
  const kind = String(criterion.kind || '')
  const operator = String(criterion.operator || '')
  if (kind === 'ordering' && right) {
    if (operator === 'lt') return `${left} < ${right}`
    if (operator === 'gt') return `${left} > ${right}`
    if (operator === 'eq') return `${left} = ${right}`
  }
  if (kind === 'sign') {
    if (operator === 'positive') return t('presentation.criterion.positive', { left })
    if (operator === 'negative') return t('presentation.criterion.negative', { left })
  }
  if (kind === 'distance' && right) {
    return t('presentation.criterion.approx', { left, right })
  }
  return t('presentation.criterion.generic')
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

function runCoef(
  ref: MetricRef | null | undefined,
  runs: SpecRunLike[],
): number | null {
  if (!ref) return null
  const specId = ref.spec_id
  if (specId) {
    for (let i = runs.length - 1; i >= 0; i -= 1) {
      if (runs[i].spec_id === specId && typeof runs[i].coef === 'number') return runs[i].coef as number
    }
    return null
  }
  const estimator = String(ref.estimator || '').toLowerCase()
  if (!estimator) return null
  for (let i = runs.length - 1; i >= 0; i -= 1) {
    const method = String(runs[i].method || '').toLowerCase()
    const runEstimator = String(runs[i].estimator || '').toLowerCase()
    if (estimator === method || estimator === runEstimator) {
      if (typeof runs[i].coef === 'number') return runs[i].coef as number
    }
  }
  return null
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

export function displaySurpriseObserved(
  criteria: CriterionLike[] | undefined,
  runs: SpecRunLike[] | undefined,
  t: Translate,
): string | null {
  if (!criteria || criteria.length === 0 || !runs) return null
  const parts: string[] = []
  for (const criterion of criteria) {
    const leftRef = criterion.left
    const rightRef = criterion.right && typeof criterion.right === 'object' ? criterion.right : undefined
    const leftValue = runCoef(leftRef, runs)
    const rightValue = rightRef ? runCoef(rightRef, runs) : null
    if (leftValue == null) continue
    const left = estimatorWord(leftRef?.estimator, t)
    if (criterion.kind === 'sign') {
      parts.push(`${left} ${formatCoef(leftValue)}`)
      continue
    }
    if (rightValue == null) continue
    const right = estimatorWord(rightRef?.estimator, t)
    const cmp = leftValue > rightValue ? '>' : leftValue < rightValue ? '<' : '='
    parts.push(`${left} ${formatCoef(leftValue)} ${cmp} ${right} ${formatCoef(rightValue)}`)
  }
  return parts.length ? parts.join(' · ') : null
}

export function displayClaimExplanation(
  evidenceStatus: string | undefined,
  t: Translate,
  teachingCase?: string | null,
): string | null {
  if (teachingCase !== 'card_1995') return null
  const status = evidenceStatus === 'conditional' ? 'conditional' : evidenceStatus === 'unsupported' ? 'unsupported' : 'supported'
  return t(`presentation.claim.card.${status}`)
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
