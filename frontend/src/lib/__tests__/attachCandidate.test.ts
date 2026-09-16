import { describe, expect, test } from 'vitest'
import { candidateKey, fileCandidate, isIngestBlocking } from '../attachCandidate'

describe('attachCandidate', () => {
  test('fileCandidate stamps source file, not classic-5', () => {
    expect(fileCandidate('panel.csv')).toEqual({
      source: 'file',
      id: 'panel.csv',
      label: 'panel.csv',
    })
    expect(candidateKey(fileCandidate('panel.csv'))).toBe('file:panel.csv')
  })

  test('ingest blocking matches confirm-attach readiness, not hasData', () => {
    expect(isIngestBlocking(undefined)).toBe(false)
    expect(isIngestBlocking('READY')).toBe(false)
    expect(isIngestBlocking('PROCESSING')).toBe(true)
    expect(isIngestBlocking('FAILED')).toBe(true)
    expect(isIngestBlocking('CANCELLED')).toBe(true)
  })
})
