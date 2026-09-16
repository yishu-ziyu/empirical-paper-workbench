import { describe, expect, it } from 'vitest'

import { chapterHasBody, chaptersMissingBodies } from '../workspace'

const SIX = [
  { type: 'intro', title: '引言' },
  { type: 'lit_review', title: '文献综述' },
  { type: 'data_desc', title: '数据描述' },
  { type: 'methods', title: '方法' },
  { type: 'results', title: '结果' },
  { type: 'conclusion', title: '结论' },
]

describe('six-chapter outline bodies', () => {
  it('treats heading-only drafts as missing', () => {
    expect(chapterHasBody({ content: '## 引言\n\n' })).toBe(false)
    expect(chapterHasBody({ content: '研究背景。' })).toBe(true)
  })

  it('lists every outline chapter that still lacks a body', () => {
    const missing = chaptersMissingBodies(SIX, [
      { type: 'intro', content: '研究背景。' },
      { type: 'methods', content: '## 模型设定\n' },
    ])
    expect(missing.map((ch) => ch.type)).toEqual([
      'lit_review',
      'data_desc',
      'methods',
      'results',
      'conclusion',
    ])
  })
})
