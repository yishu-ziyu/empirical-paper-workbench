import { describe, expect, test } from 'vitest'
import {
  claimLabel,
  literatureLabel,
  normalizeEstimateTableSource,
  parseEstimateRows,
  starHumanLabel,
} from '../readoutTable'

describe('readoutTable', () => {
  test('parses a pipe treatment row into named cells', () => {
    const rows = parseEstimateRows('| age | -0.0687 | 0.0083 | 0.0000 |')
    expect(rows).toEqual([
      { variable: 'age', coef: '-0.0687', se: '0.0083', p: '0.0000' },
    ])
  })

  test('drops duplicate lines from results + treatment_row', () => {
    const rows = parseEstimateRows(
      '| age | 0.1234 | 0.0456 | 0.0078 |\n| age | 0.1234 | 0.0456 | 0.0078 |',
    )
    expect(rows).toHaveLength(1)
  })

  test('skips markdown header and separator rows', () => {
    const rows = parseEstimateRows(
      '| 变量 | 系数 | SE | p |\n|------|------|----|---|\n| age | -0.0687 | 0.0083 | 0.0000 |',
    )
    expect(rows).toEqual([
      { variable: 'age', coef: '-0.0687', se: '0.0083', p: '0.0000' },
    ])
  })

  test('normalizeEstimateTableSource joins string arrays', () => {
    expect(
      normalizeEstimateTableSource(['| age | 0.1 | 0.2 | 0.3 |', '| treat | 0.4 | 0.5 | 0.6 |']),
    ).toBe('| age | 0.1 | 0.2 | 0.3 |\n| treat | 0.4 | 0.5 | 0.6 |')
  })

  test('normalizeEstimateTableSource keeps a string as-is', () => {
    expect(normalizeEstimateTableSource('| age | 0.1 | 0.2 | 0.3 |')).toBe(
      '| age | 0.1 | 0.2 | 0.3 |',
    )
  })

  test('normalizeEstimateTableSource maps null and unknown to null', () => {
    expect(normalizeEstimateTableSource(null)).toBeNull()
    expect(normalizeEstimateTableSource(undefined)).toBeNull()
    expect(normalizeEstimateTableSource(12)).toBeNull()
    expect(normalizeEstimateTableSource({})).toBeNull()
    expect(normalizeEstimateTableSource([])).toBeNull()
  })

  test('human labels hide internal claim tokens', () => {
    expect(claimLabel('association')).toBe('相关')
    expect(starHumanLabel(null)).toBe('无因果评级')
    expect(literatureLabel('crossref')).toBe('Crossref')
    expect(literatureLabel('mock')).toBe('示例文献')
  })
})
