import { describe, expect, test } from 'vitest'

const sources = import.meta.glob(['../**/*.ts', '../**/*.tsx'], {
  eager: true,
  query: '?raw',
  import: 'default',
}) as Record<string, string>

describe('Card canonical literals', () => {
  test('frontend/src has no Card coefficient constants', () => {
    const banned = /0\.0747|0\.1315|14\.214/
    const hits = Object.entries(sources).filter(([, src]) => banned.test(src))
    expect(hits.map(([path]) => path)).toEqual([])
  })

  test('C5 all 11 canonical concepts have clear Chinese explanations', () => {
    const requiredConcepts = [
      { en: 'Research Question', zh: '研究问题' },
      { en: 'Expectation', zh: '预期' },
      { en: 'Admissible Space', zh: '合理规格空间' },
      { en: 'Evidence Lab', zh: '证据实验室' },
      { en: 'Surprise', zh: '意外' },
      { en: 'Compare', zh: '比较' },
      { en: 'Next-best Challenge', zh: '下一步最有价值的检验' },
      { en: 'Claim Ledger', zh: '结论账本' },
      { en: 'Supported', zh: '当前证据支持' },
      { en: 'Conditionally supported', zh: '有条件支持' },
      { en: 'Unsupported', zh: '当前证据不支持' },
    ]

    const allSourceText = Object.values(sources).join('\n')

    for (const { en, zh } of requiredConcepts) {
      const combinedPattern = new RegExp(`${en}[（·\\s].*${zh}|${zh}.*${en}`, 'i')
      expect(
        combinedPattern.test(allSourceText),
        `Expected both English "${en}" and Chinese "${zh}" to appear together in UI/i18n sources`,
      ).toBe(true)
    }
  })
})

