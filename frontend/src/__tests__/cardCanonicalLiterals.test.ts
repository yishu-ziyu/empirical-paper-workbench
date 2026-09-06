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
})
