import { describe, expect, test } from 'vitest'
import { I18N_MESSAGES } from '../lib/i18n'

const sources = import.meta.glob(['../**/*.ts', '../**/*.tsx'], {
  eager: true,
  query: '?raw',
  import: 'default',
}) as Record<string, string>

const CONCEPTS = [
  { key: 'canonical.researchQuestion', zh: '研究问题', en: 'Research question' },
  { key: 'canonical.expectation', zh: '预期', en: 'Expectation' },
  { key: 'canonical.admissibleSpace', zh: '分析方案', en: 'Analysis plans' },
  { key: 'canonical.evidenceLab', zh: '结果与证据', en: 'Results & evidence' },
  { key: 'canonical.surprise', zh: '意外', en: 'Surprise' },
  { key: 'canonical.compare', zh: '比较', en: 'Compare' },
  { key: 'canonical.nextBestChallenge', zh: '建议的下一步检验', en: 'Suggested next check' },
  { key: 'canonical.claimLedger', zh: '研究结论', en: 'Research claims' },
  { key: 'canonical.supported', zh: '当前证据支持', en: 'Supported by current evidence' },
  { key: 'canonical.conditionallySupported', zh: '有条件支持', en: 'Conditionally supported' },
  { key: 'canonical.unsupported', zh: '当前证据不支持', en: 'Not supported by current evidence' },
  { key: 'canonical.primaryAnalysis', zh: '当前主分析', en: 'Primary analysis' },
  { key: 'canonical.setPrimary', zh: '设为主分析', en: 'Set as primary analysis' },
  { key: 'desk.tryCard', zh: '体验一项真实研究', en: 'Explore a real study' },
] as const

const STACKED_CHROME =
  /(?:Research Question（研究问题）|Expectation（预期）|Admissible Space（合理规格空间）|Evidence Lab（证据实验室）|Surprise（意外）|Compare（比较）|Next-best Challenge（下一步最有价值的检验）|Claim Ledger（结论账本）|Supported（当前证据支持）|Conditionally supported（有条件支持）|Unsupported（当前证据不支持）|Try a real study · Card|New study · 回工作台|Boot failed · 启动失败|Teaching case · Card 1995 · 教育是否提高工资|Review claim · 整理结论|Draft claim ready · 已可以整理结论|Surprise condition · 意外判定|New evidence available · 结论需要重新审视|Research trace · 研究记录|Result · 结果数字|Specification · 研究设定|Estimator · 估计量|Run · 运行|Dataset · 数据集|Code · 代码|Evidence · 结论与来源)/

const ALLOWED_PATH = /__tests__|i18nWorkbench|cardCanonicalLiterals/

describe('Card canonical literals', () => {
  test('frontend/src has no Card coefficient constants', () => {
    const banned = /0\.0747|0\.1315|14\.214/
    const hits = Object.entries(sources).filter(([, src]) => banned.test(src))
    expect(hits.map(([path]) => path)).toEqual([])
  })

  test('both language dictionaries hold the core chrome strings without stacking', () => {
    for (const item of CONCEPTS) {
      expect(I18N_MESSAGES.zh[item.key]).toBe(item.zh)
      expect(I18N_MESSAGES.en[item.key]).toBe(item.en)
      expect(I18N_MESSAGES.zh[item.key]).not.toMatch(/[A-Za-z].*[（·].*[\u4e00-\u9fff]/)
      expect(I18N_MESSAGES.en[item.key]).not.toMatch(/[\u4e00-\u9fff]/)
    }
  })

  test('default chrome source does not stack English and Chinese system titles', () => {
    const hits = Object.entries(sources).filter(
      ([path, src]) => !ALLOWED_PATH.test(path) && STACKED_CHROME.test(src),
    )
    expect(hits.map(([path]) => path)).toEqual([])
  })
})
