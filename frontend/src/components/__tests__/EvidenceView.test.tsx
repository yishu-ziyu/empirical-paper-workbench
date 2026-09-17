import { describe, expect, test, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import EvidenceView from '../EvidenceView'
import { I18nProvider } from '../../lib/i18n'
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
    render(<I18nProvider><EvidenceView sessionId="sess-1" /></I18nProvider>)
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
    render(<I18nProvider><EvidenceView sessionId="sess-1" /></I18nProvider>)
    await waitFor(() => {
      expect(screen.getByTestId('evidence-traceability')).toHaveAttribute(
        'data-fully-traceable',
        'true',
      )
    })
    expect(screen.getByTestId('evidence-traceability')).toHaveTextContent('完全可溯源')
    expect(screen.getByTestId('evidence-traceability')).not.toHaveTextContent('Fully traceable')
  })

  test('OLS method shows OLS engine label, not statspai.feols', async () => {
    fetchEvidence.mockResolvedValue(
      sixLayerEvidence({
        estimate: {
          ...sixLayerEvidence().estimate,
          method: 'ols',
          estimator: 'statspai.feols',
        },
      }) as never,
    )
    render(<I18nProvider><EvidenceView sessionId="sess-1" /></I18nProvider>)
    await waitFor(() => {
      expect(screen.getByTestId('evidence-provenance')).toBeInTheDocument()
    })
    const layer = screen.getByTestId('evidence-provenance').querySelector('[data-layer="estimator"]')
    expect(layer).toHaveTextContent('OLS')
    expect(layer).not.toHaveTextContent('feols')
  })
})

describe('EvidenceView identification readout', () => {
  beforeEach(() => {
    fetchEvidence.mockReset()
  })

  async function renderIdent(identification: Record<string, unknown>) {
    fetchEvidence.mockResolvedValue(sixLayerEvidence({ identification }) as never)
    render(<I18nProvider><EvidenceView sessionId="sess-1" /></I18nProvider>)
    await waitFor(() => {
      expect(screen.getByTestId('evidence-identification')).toBeInTheDocument()
    })
    return screen.getByTestId('evidence-identification')
  }

  test('尚未评估不写「通过」：passed=null 报尚未核查', async () => {
    const node = await renderIdent({
      failed: false,
      report: '诊断工具没有运行成功，识别策略的风险尚未核查。',
      passed: null,
      star_rating: null,
      execution: 'failed',
      assessment: 'insufficient_evidence',
    })

    expect(node).toHaveTextContent('尚未核查')
    expect(node).not.toHaveTextContent('通过')
  })

  test('有风险不等于通过：assessment=risk_found 必须说出来', async () => {
    const node = await renderIdent({
      failed: false,
      report: 'IV 诊断: first-stage F=6.0，存在弱工具变量风险。',
      passed: true,
      star_rating: 2,
      execution: 'completed',
      assessment: 'risk_found',
    })

    expect(node).toHaveTextContent('有风险，需披露')
    expect(node).not.toHaveTextContent('通过')
  })

  test('干净通过才写通过', async () => {
    const node = await renderIdent({
      failed: false,
      report: '识别策略星级：★★★（3星）',
      passed: true,
      star_rating: 3,
      execution: 'completed',
      assessment: 'risk_not_found',
    })

    expect(node).toHaveTextContent('通过')
    expect(node).toHaveTextContent('★★★')
  })
})
