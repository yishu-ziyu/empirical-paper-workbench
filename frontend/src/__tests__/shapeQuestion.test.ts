import { describe, expect, test } from 'vitest'
import { nextPrompt, reflect, shapeQuestion } from '../lib/shapeQuestion'

describe('shapeQuestion', () => {
  test('降级逻辑不会用关键词猜研究领域', () => {
    expect(shapeQuestion('导师让我用 CHARLS 做点养老的').heard).toEqual([])
  })

  test('一次只补一个缺口', () => {
    expect(nextPrompt({})!.id).toBe('compare')
    expect(nextPrompt({ compare: 'policy' })?.id).toBe('outcome')
    expect(nextPrompt({ compare: 'policy', outcome: 'work' })).toBeNull()
  })

  test('复述只回应当下听到的，不另开一段对话', () => {
    expect(reflect('', {})).toBe('你先说，我听着。')
    expect(reflect('导师让我用 CHARLS 做点养老的', {})).toBe('我先保留你的原话。现在只确认要比较什么。')
  })

  test('两轮之后才算成形', () => {
    const early = shapeQuestion('导师让我用 CHARLS 做点养老的')
    expect(early.ready).toBe(false)
    const later = shapeQuestion('导师让我用 CHARLS 做点养老的', {
      compare: 'policy',
      outcome: 'work',
    })
    expect(later.ready).toBe(true)
    expect(later.title).toBe('导师让我用 CHARLS 做点养老的')
  })

  test('明确写出的研究对象和结果变量不会被数字经济模板替换', () => {
    const draft = shapeQuestion('我想研究数字经济发展是否提高了制造业企业的生产率')

    expect(draft.title).toBe('我想研究数字经济发展是否提高了制造业企业的生产率')
    expect(draft.title).not.toMatch(/用工|工资/)
  })

  test('陌生研究领域也只保留用户原话，不依赖领域模板', () => {
    const notes = '我想研究绿色金融是否降低了高耗能企业的碳排放'

    expect(shapeQuestion(notes).title).toBe(notes)
  })

  test('问候不会被降级逻辑强行变成论文问题', () => {
    const draft = shapeQuestion("ni'hao")

    expect(draft.intent).toBe('conversation')
    expect(draft.title).toBe('')
    expect(draft.ready).toBe(false)
    expect(draft.reflection).toContain('研究')
  })
})
