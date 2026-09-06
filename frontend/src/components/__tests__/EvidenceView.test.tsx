import { describe, expect, test, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import EvidenceView from '../EvidenceView'
import { fetchSessionEvidence } from '../../lib/workspace'

vi.mock('../../lib/workspace', async () => {
  const actual = await vi.importActual<typeof import('../../lib/workspace')>(
    '../../lib/workspace',
  )
  return {
    ...actual,
    fetchSessionEvidence: vi.fn(),
  }
})

const fetchEvidence = vi.mocked(fetchSessionEvidence)

function sixLayerEvidence(overrides: Record<string, unknown> = {}) {
  return {
    session_id: 'sess-1',
    available: true,
    blockers: [],
    claim: 'association',
    estimate: {
      produced_by: 'estimate',
      status: 'ok',
      coef: -0.0687,
      se: 0.0083,
      p: 0.0001,
      n: 24,
      estimator: 'statspai.feols',
      formula: 'income ~ age',
      treatment: 'age',
      treatment_row: '| age | -0.0687 | 0.0083 | 0.0001 |',
      table_rows: ['| age | -0.0687 | 0.0083 | 0.0001 |'],
    },
    results: '| age | -0.0687 | 0.0083 | 0.0001 |',
    specification: { method: 'OLS', dv: 'income', iv: 'age' },
    identification: { failed: false, report: 'ok', star_rating: null },
    robustness: { ran: true, status: 'ran' },
    provenance: {
      run_id: 'run-producer',
      run_status: 'SUCCEEDED',
      run_events_url: '/api/runs/run-producer/events',
      dataset: {
        name: 'cleaned.csv',
        path: '/tmp/cleaned.csv',
        hash: 'abc123',
        role: 'cleaned',
        rows: 24,
        columns: ['income', 'age'],
      },
      code: [],
      trace_events: [],
      artifacts: [],
      manifest: {},
    },
    ...overrides,
  }
}

describe('EvidenceView provenance layers', () => {
  beforeEach(() => {
    fetchEvidence.mockReset()
  })

  test('canExport-equivalent chapters without code artifact stay 5/6', async () => {
    fetchEvidence.mockResolvedValue(sixLayerEvidence() as never)
    render(<EvidenceView sessionId="sess-1" />)
    await waitFor(() => {
      expect(screen.getByTestId('evidence-traceability')).toHaveAttribute(
        'data-fully-traceable',
        'false',
      )
    })
    expect(screen.getByTestId('evidence-traceability')).toHaveTextContent('可溯源 5/6 层')
    expect(screen.getByTestId('evidence-traceability')).not.toHaveTextContent('Fully traceable')
  })

  test('real code artifact for the producer run allows Fully traceable 6/6', async () => {
    fetchEvidence.mockResolvedValue(
      sixLayerEvidence({
        provenance: {
          ...sixLayerEvidence().provenance,
          code: [
            {
              path: 'outputs/code/run-producer/analysis.py',
              bytes: 120,
              filename: 'analysis.py',
              run_id: 'run-producer',
            },
          ],
        },
      }) as never,
    )
    render(<EvidenceView sessionId="sess-1" />)
    await waitFor(() => {
      expect(screen.getByTestId('evidence-traceability')).toHaveAttribute(
        'data-fully-traceable',
        'true',
      )
    })
    expect(screen.getByTestId('evidence-traceability')).toHaveTextContent('Fully traceable')
  })
})
