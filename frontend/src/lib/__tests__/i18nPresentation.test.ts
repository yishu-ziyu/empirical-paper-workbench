import { describe, expect, test } from 'vitest'
import { I18N_MESSAGES } from '../i18n'
import {
  criterionSpecIdentities,
  displayAssumption,
  displayClaimExplanation,
  displayCompareWhy,
  displayCriterionLabel,
  displayDimension,
  displayEstimand,
  displaySpecLabel,
  displaySpecRationale,
  displaySurpriseExpected,
  displaySurpriseObserved,
} from '../i18nPresentation'
import type { Translate } from '../i18n'

function tFor(lang: 'zh' | 'en'): Translate {
  return (key, vars) => {
    let template = I18N_MESSAGES[lang][key] ?? key
    if (!vars) return template
    return template.replace(/\{(\w+)\}/g, (match, name: string) =>
      Object.prototype.hasOwnProperty.call(vars, name) ? String(vars[name]) : match,
    )
  }
}

const seed = {
  kind: 'ordering',
  operator: 'lt',
  left: { metric: 'estimate.coef', estimator: 'iv', spec_id: 'iv_region_dummies', label: 'IV estimate' },
  right: { metric: 'estimate.coef', estimator: 'ols', spec_id: 'ols_region_dummies', label: 'OLS estimate' },
  label: 'IV estimate < OLS estimate',
}

describe('i18nPresentation', () => {
  test('criterion display is generated from kind/operator/refs, not stored English as Chinese', () => {
    expect(displayCriterionLabel(seed, tFor('zh'))).toBe('IV 估计 < OLS 估计')
    expect(displayCriterionLabel(seed, tFor('en'))).toBe('IV estimate < OLS estimate')
    expect(displayCriterionLabel(seed, tFor('zh'))).not.toBe(seed.label)
  })

  test('Card spec labels map by semantic id', () => {
    expect(displaySpecLabel('ols_linear_exper', tFor('zh'), 'zh', 'OLS · linear experience')).toBe(
      'OLS · 线性经验',
    )
    expect(displaySpecLabel('iv_region_dummies', tFor('en'), 'en', 'ignored')).toBe(
      'IV · nearc4 with 1966 region dummies',
    )
    expect(displaySpecRationale('ols_full_controls', tFor('zh'), 'zh')).toMatch(/经验/)
  })

  test('estimand is keyed by teaching case, not regex of stored English', () => {
    const zh = displayEstimand('ols', tFor('zh'), { teachingCase: 'card_1995' })
    expect(zh).toMatch(/OLS 关联/)
    expect(zh).not.toMatch(/conditional association/)
    expect(displayEstimand('iv', tFor('en'), { questionId: 'card_1995.question' })).toMatch(
      /local causal return/,
    )
  })

  test('surprise expected comes from criteria; observed comes only from backend outcomes', () => {
    expect(displaySurpriseExpected([seed], tFor('zh'))).toBe('IV 估计 < OLS 估计')
    // Backend structured resolution: the run_id/value the evaluator read.
    const surprise = {
      status: 'Unexpected',
      criterion_outcomes: [
        {
          id: 'criterion.seed.iv-below-ols',
          outcome: 'violated',
          kind: 'ordering',
          operator: 'lt',
          left: {
            source: 'metric',
            metric: 'estimate.coef',
            estimator: 'iv',
            spec_id: 'iv_region_dummies',
            run_id: 'run-iv',
            value: 0.13,
          },
          right: {
            source: 'metric',
            metric: 'estimate.coef',
            estimator: 'ols',
            spec_id: 'ols_region_dummies',
            run_id: 'run-ols',
            value: 0.08,
          },
        },
      ],
    }
    expect(displaySurpriseObserved(surprise, tFor('zh'))).toBe(
      'IV 估计 0.1300 > OLS 估计 0.0800',
    )
    expect(displaySurpriseObserved(surprise, tFor('zh'))).not.toMatch(/IV estimate/)
    // No structured outcomes (legacy stored snapshot): nothing fabricated.
    expect(displaySurpriseObserved({ status: 'Unexpected' }, tFor('zh'))).toBeNull()
    expect(displaySurpriseObserved(null, tFor('zh'))).toBeNull()
  })

  test('surprise observed never fills unresolved outcomes from other metrics', () => {
    const surprise = {
      status: 'Inconclusive',
      criterion_outcomes: [
        {
          id: 'criterion.seed.iv-below-ols',
          outcome: 'satisfied',
          kind: 'ordering',
          operator: 'lt',
          left: {
            source: 'metric',
            estimator: 'iv',
            spec_id: 'iv_region_dummies',
            run_id: 'run-iv',
            value: 0.09,
          },
          right: {
            source: 'metric',
            estimator: 'ols',
            spec_id: 'ols_region_dummies',
            run_id: 'run-ols',
            value: 0.13,
          },
        },
        // Unsupported metric: stays unresolved, {id, outcome} only — even
        // though a coef-bearing run of the same spec_id exists.
        { id: 'criterion.future-att', outcome: 'unresolved' },
      ],
    }
    expect(displaySurpriseObserved(surprise, tFor('en'))).toBe(
      'IV estimate 0.0900 < OLS estimate 0.1300',
    )
    const signOnly = {
      status: 'Expected',
      criterion_outcomes: [
        {
          id: 'criterion.iv-positive',
          outcome: 'satisfied',
          kind: 'sign',
          operator: 'positive',
          left: { source: 'metric', estimator: 'iv', run_id: 'run-iv', value: 0.13 },
        },
      ],
    }
    expect(displaySurpriseObserved(signOnly, tFor('zh'))).toBe('IV 估计 0.1300')
    const constantRight = {
      status: 'Unexpected',
      criterion_outcomes: [
        {
          id: 'criterion.iv-lt-const',
          outcome: 'satisfied',
          kind: 'ordering',
          operator: 'lt',
          left: { source: 'metric', estimator: 'iv', run_id: 'run-iv', value: 0.095 },
          right: { source: 'constant', value: 0.1 },
        },
      ],
    }
    expect(displaySurpriseObserved(constantRight, tFor('zh'))).toBe('IV 估计 0.0950 < 0.1000')
  })

  test('compare why and dimensions are structured, not dumped English keys', () => {
    expect(displayCompareWhy([{ dimension: 'estimator' }], tFor('zh'))).toBe('识别策略改变了')
    expect(displayDimension('demographics', tFor('zh'))).toBe('人口特征')
    expect(displayDimension('experience', tFor('en'))).toBe('Experience')
  })

  test('Card claim explanation is display-only', () => {
    expect(displayClaimExplanation('supported', tFor('zh'), 'card_1995')).toMatch(/正向关联/)
    expect(displayAssumption('LATE is not ATE', tFor('zh'))).toBe('LATE 不是 ATE')
  })

  test('C1 claim explanation maps the full backend status set honestly (zh + en)', () => {
    const zh = tFor('zh')
    const en = tFor('en')
    // Backend draft payload statuses
    expect(displayClaimExplanation('supported', zh, 'card_1995')).toMatch(/正向关联/)
    expect(displayClaimExplanation('supported', en, 'card_1995')).toMatch(
      /positively associated/,
    )
    const insufficientZh = displayClaimExplanation('insufficient', zh, 'card_1995')
    expect(insufficientZh).toMatch(/证据不足/)
    expect(insufficientZh).not.toContain('在当前证据下，教育与工资呈正向关联')
    expect(insufficientZh).not.toMatch(/正向关联/)
    expect(displayClaimExplanation('insufficient', en, 'card_1995')).toMatch(
      /[Ii]nsufficient evidence/,
    )
    const draftZh = displayClaimExplanation('draft', zh, 'card_1995')
    expect(draftZh).toMatch(/草稿/)
    expect(draftZh).not.toMatch(/正向关联|不能把/)
    expect(displayClaimExplanation('draft', en, 'card_1995')).toMatch(/[Dd]raft/)
    // approve_card_claim rewrites the status to approved: an approval is a
    // user action, not new evidence — never a stronger substantive claim.
    const approvedZh = displayClaimExplanation('approved', zh, 'card_1995')
    expect(approvedZh).toMatch(/已获批准/)
    expect(approvedZh).not.toMatch(/正向关联|不能把/)
    expect(displayClaimExplanation('approved', en, 'card_1995')).toMatch(/[Aa]pproved/)

    // Display-only branches still exist for future backend statuses
    expect(displayClaimExplanation('conditional', zh, 'card_1995')).toMatch(/工具变量假设/)
    expect(displayClaimExplanation('unsupported', zh, 'card_1995')).toMatch(/13%/)

    // Missing / unknown future values: conservative neutral, never supported
    for (const status of [undefined, '', 'some_future_status', null]) {
      const neutralZh = displayClaimExplanation(status, zh, 'card_1995')
      expect(neutralZh).toBeTruthy()
      expect(neutralZh).not.toMatch(/正向关联|13%|局部因果回报|草稿/)
      expect(displayClaimExplanation(status, en, 'card_1995')).toMatch(/[Uu]navailable/)
    }

    // Non-card teaching cases keep the raw original (no mapping invented)
    expect(displayClaimExplanation('insufficient', zh, 'other_case')).toBeNull()
    expect(displayClaimExplanation(undefined, zh, undefined)).toBeNull()
  })

  test('C3 criterion label carries constants, tolerance, and spec identity', () => {
    const zh = tFor('zh')
    const en = tFor('en')
    const orderingConst = {
      kind: 'ordering',
      operator: 'lt',
      left: { metric: 'estimate.coef', estimator: 'iv', spec_id: 'iv_nearc4_full' },
      right: 0.1,
    }
    expect(displayCriterionLabel(orderingConst, zh)).toBe('IV 估计 < 0.1')
    expect(displayCriterionLabel(orderingConst, en)).toBe('IV estimate < 0.1')
    expect(displayCriterionLabel(orderingConst, zh)).not.toBe('可检验判定')
    expect(
      displayCriterionLabel({ ...orderingConst, operator: 'gt', right: 0.05 }, zh),
    ).toBe('IV 估计 > 0.05')

    const distance = (tolerance?: { abs?: number; rel?: number }) => ({
      kind: 'distance',
      operator: 'approx',
      left: { metric: 'estimate.coef', estimator: 'iv' },
      right: { metric: 'estimate.coef', estimator: 'ols' },
      tolerance,
    })
    const rel05 = displayCriterionLabel(distance({ rel: 0.05 }), zh)
    const rel25 = displayCriterionLabel(distance({ rel: 0.25 }), zh)
    expect(rel05).toBe('IV 估计 ≈ OLS 估计 ±5%')
    expect(rel25).toBe('IV 估计 ≈ OLS 估计 ±25%')
    expect(rel05).not.toBe(rel25)
    expect(displayCriterionLabel(distance({ abs: 0.02 }), zh)).toBe(
      'IV 估计 ≈ OLS 估计 ±0.02',
    )
    expect(displayCriterionLabel(distance({ abs: 0.02, rel: 0.05 }), zh)).toBe(
      'IV 估计 ≈ OLS 估计 ±0.02 / ±5%',
    )
    // Both tolerance slots empty: the backend default rel=0.25 is what the
    // judgment uses, so the label must say ±25% (not "no tolerance").
    expect(displayCriterionLabel(distance(), zh)).toBe('IV 估计 ≈ OLS 估计 ±25%')
    expect(
      displayCriterionLabel(
        {
          kind: 'distance',
          operator: 'approx',
          left: { estimator: 'iv' },
          right: 0.1,
          tolerance: { rel: 0.25 },
        },
        en,
      ),
    ).toBe('IV estimate ≈ 0.1 ±25%')

    // Unfriendly combination keeps the original condition, never silently
    // drops the parameters.
    expect(
      displayCriterionLabel(
        {
          kind: 'ratio',
          operator: 'lt',
          left: { estimator: 'iv' },
          right: 1.2,
          label: 'IV/OLS ratio < 1.2',
        },
        zh,
      ),
    ).toBe('可检验判定 · IV/OLS ratio < 1.2')
    expect(
      displayCriterionLabel({ kind: 'ratio', operator: 'lt', left: { estimator: 'iv' } }, zh),
    ).toBe('可检验判定')

    // Spec identity: the authoritative selector stays extractable so
    // same-estimator different-spec refs are distinguishable.
    expect(criterionSpecIdentities(orderingConst)).toEqual({
      left: 'iv_nearc4_full',
      right: null,
    })
    expect(criterionSpecIdentities(seed)).toEqual({
      left: 'iv_region_dummies',
      right: 'ols_region_dummies',
    })
    expect(
      criterionSpecIdentities({
        kind: 'distance',
        operator: 'approx',
        left: { estimator: 'iv', spec_id: 'iv_nearc4_full' },
        right: { estimator: 'iv', spec_id: 'iv_region_dummies' },
      }),
    ).toEqual({ left: 'iv_nearc4_full', right: 'iv_region_dummies' })
  })
})
