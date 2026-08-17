import { describe, expect, test } from 'vitest'
import {
  claimLabel,
  literatureLabel,
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

  test('human labels hide internal claim tokens', () => {
    expect(claimLabel('association')).toBe('相关')
    expect(starHumanLabel(null)).toBe('无因果评级')
    expect(literatureLabel('crossref')).toBe('Crossref')
    expect(literatureLabel('mock')).toBe('示例文献')
  })
})
