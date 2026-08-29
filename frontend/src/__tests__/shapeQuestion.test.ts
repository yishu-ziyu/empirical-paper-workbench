import { describe, expect, test } from 'vitest'
import { extractHeard, nextPrompt, reflect, shapeQuestion } from '../lib/shapeQuestion'

describe('shapeQuestion', () => {
  test('能从乱想法里听出对象', () => {
    const heard = extractHeard('导师让我用 CHARLS 做点养老的')
    expect(heard.map((item) => item.id)).toEqual(expect.arrayContaining(['charls', 'pension', 'advisor']))
  })

  test('一次只补一个缺口', () => {
    expect(nextPrompt({})!.id).toBe('compare')
    expect(nextPrompt({ compare: 'policy' })?.id).toBe('outcome')
    expect(nextPrompt({ compare: 'policy', outcome: 'work' })).toBeNull()
  })

  test('复述只回应当下听到的，不另开一段对话', () => {
    expect(reflect('', [], {})).toBe('你先说，我听着。')
    expect(reflect('导师让我用 CHARLS 做点养老的', extractHeard('导师让我用 CHARLS 做点养老的'), {})).toMatch(/CHARLS|养老/)
  })

  test('两轮之后才算成形', () => {
    const early = shapeQuestion('导师让我用 CHARLS 做点养老的')
    expect(early.ready).toBe(false)
    const later = shapeQuestion('导师让我用 CHARLS 做点养老的', {
      compare: 'policy',
      outcome: 'work',
    })
    expect(later.ready).toBe(true)
    expect(later.title).toMatch(/养老|退休/)
  })
})
