import { describe, expect, test } from 'vitest'
import { I18N_MESSAGES } from '../i18n'
import {
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

  test('surprise expected/observed come from criteria + runs', () => {
    const runs = [
      { spec_id: 'ols_region_dummies', method: 'ols', coef: 0.08, status: 'ok' },
      { spec_id: 'iv_region_dummies', method: 'iv', coef: 0.13, status: 'ok' },
    ]
    expect(displaySurpriseExpected([seed], tFor('zh'))).toBe('IV 估计 < OLS 估计')
    expect(displaySurpriseObserved([seed], runs, tFor('zh'))).toBe(
      'IV 估计 0.1300 > OLS 估计 0.0800',
    )
    expect(displaySurpriseObserved([seed], runs, tFor('zh'))).not.toMatch(/IV estimate/)
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
})
