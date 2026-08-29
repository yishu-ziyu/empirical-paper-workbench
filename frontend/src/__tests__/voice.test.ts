import { describe, expect, test } from 'vitest'
import { appendTranscript } from '../lib/voice'

describe('appendTranscript', () => {
  test('中文直接接上，不插入空格', () => {
    expect(appendTranscript('导师让我', '用 CHARLS')).toBe('导师让我用 CHARLS')
  })

  test('英文词之间补空格', () => {
    expect(appendTranscript('I want', 'a question')).toBe('I want a question')
  })

  test('空片段不改原文', () => {
    expect(appendTranscript('已有内容', '   ')).toBe('已有内容')
  })
})
