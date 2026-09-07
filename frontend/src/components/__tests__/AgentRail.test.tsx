import { describe, expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import AgentRail from '../AgentRail'
import type { WorkspaceApi } from '../../lib/workspace'
import { I18nProvider } from '../../lib/i18n'

function renderRail(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

function ws(overrides: Record<string, unknown> = {}): WorkspaceApi {
  return {
    uploading: false,
    directionBusy: false,
    writeBusy: false,
    writingType: null,
    activeRun: null,
    identFailed: false,
    writeBlockers: [],
    estimateMeta: { coef: 0.08, se: 0.01, p: 0.001, n: 3010 },
    writtenChapters: [
      {
        type: 'results',
        title: '结果',
        content: 'Education is positively associated with earnings.',
        grounded: true,
      },
    ],
    research: {
      claims: [
        {
          id: 'claim.card.education-earnings',
          approved_by_user: true,
          unsupported_wording: "One more year of education raises everyone's wage by 13%.",
        },
      ],
      claim: {
        id: 'claim.card.education-earnings',
        approved_by_user: true,
        unsupported_wording: "One more year of education raises everyone's wage by 13%.",
      },
    },
    ...overrides,
  } as unknown as WorkspaceApi
}

describe('AgentRail linked evidence', () => {
  test('results grounded badge requires approved claim', () => {
    renderRail(
      <AgentRail
        ws={ws()}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence
        hasSuccessfulEstimate
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.getByTestId('evidence-grounded-badge')).toHaveAttribute('data-grounded', 'true')
  })

  test('missing based_on_evidence_revision is not grounded when lab has revision', () => {
    renderRail(
      <AgentRail
        ws={ws({
          research: {
            evidence_revision: 3,
            claims: [
              {
                id: 'claim.card.education-earnings',
                approved_by_user: true,
                stale: false,
              },
            ],
            claim: {
              id: 'claim.card.education-earnings',
              approved_by_user: true,
              stale: false,
            },
          },
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence
        hasSuccessfulEstimate
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.getByTestId('evidence-grounded-badge')).toHaveAttribute('data-grounded', 'false')
  })

  test('stale claim is not marked grounded', () => {
    renderRail(
      <AgentRail
        ws={ws({
          research: {
            evidence_revision: 2,
            claims: [
              {
                id: 'claim.card.education-earnings',
                approved_by_user: true,
                stale: true,
                based_on_evidence_revision: 1,
              },
            ],
            claim: {
              id: 'claim.card.education-earnings',
              approved_by_user: true,
              stale: true,
              based_on_evidence_revision: 1,
            },
          },
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence
        hasSuccessfulEstimate
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.getByTestId('evidence-grounded-badge')).toHaveAttribute('data-grounded', 'false')
  })

  test('unsupported wording is not marked grounded', () => {
    renderRail(
      <AgentRail
        ws={ws({
          writtenChapters: [
            {
              type: 'results',
              title: '结果',
              content: "One more year of education raises everyone's wage by 13%.",
              grounded: false,
            },
          ],
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence
        hasSuccessfulEstimate
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.getByTestId('evidence-grounded-badge')).toHaveAttribute('data-grounded', 'false')
  })

  test('C2 Question tab does not leak Evidence "Show me" or "IV > OLS"', () => {
    renderRail(
      <AgentRail
        ws={ws({
          workbenchTab: 'question',
          research: {
            surprise: { status: 'Unexpected', observed: 'IV > OLS' },
          },
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={false}
        hasSuccessfulEstimate={false}
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.queryByTestId('agent-cursor-prompt')).not.toBeInTheDocument()
    expect(screen.queryByTestId('agent-cursor-show-me')).not.toBeInTheDocument()
    expect(screen.queryByText(/这个变化值得检查/)).not.toBeInTheDocument()
    expect(screen.queryByText(/IV > OLS/)).not.toBeInTheDocument()
  })

  test('C2 Paper tab shows Linked Evidence and never leaks Show me or Unexpected result', () => {
    renderRail(
      <AgentRail
        ws={ws({
          workbenchTab: 'paper',
          research: {
            surprise: { status: 'Unexpected', observed: 'IV > OLS' },
          },
        })}
        decision={{
          title: '写作暂时被阻塞',
          reason: '识别未通过',
        }}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={true}
        hasSuccessfulEstimate={true}
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.getByTestId('linked-evidence')).toBeInTheDocument()
    expect(screen.queryByTestId('agent-cursor-prompt')).not.toBeInTheDocument()
    expect(screen.queryByTestId('agent-cursor-show-me')).not.toBeInTheDocument()
    expect(screen.queryByText(/这个变化值得检查/)).not.toBeInTheDocument()
    expect(screen.getByTestId('decision-blocker-title')).toHaveTextContent('写作暂时被阻塞')
    // Max 1 primary decision card
    expect(screen.getAllByTestId('decision-blocker')).toHaveLength(1)
  })

  test('C2 Evidence tab displays Unexpected result prompt and Show me', () => {
    renderRail(
      <AgentRail
        ws={ws({
          workbenchTab: 'evidence',
          research: {
            surprise: { status: 'Unexpected', observed: 'IV estimate 0.13 > OLS estimate 0.08' },
            expectation: {
              criteria: [
                {
                  kind: 'ordering',
                  operator: 'lt',
                  left: { estimator: 'iv', spec_id: 'iv_region_dummies' },
                  right: { estimator: 'ols', spec_id: 'ols_region_dummies' },
                },
              ],
            },
            specification_runs: [
              { spec_id: 'ols_region_dummies', method: 'ols', coef: 0.08, status: 'ok' },
              { spec_id: 'iv_region_dummies', method: 'iv', coef: 0.13, status: 'ok' },
            ],
          },
        })}
        decision={{
          title: '结果与预期不符',
          reason: 'IV 估计 0.1300 > OLS 估计 0.0800',
        }}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={false}
        hasSuccessfulEstimate={true}
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.getByTestId('agent-cursor-prompt')).toBeInTheDocument()
    expect(screen.getByTestId('agent-cursor-show-me')).toBeInTheDocument()
    expect(screen.getByText(/这个变化值得检查/)).toBeInTheDocument()
    expect(screen.getByTestId('agent-cursor-prompt')).toHaveTextContent('IV 估计 0.1300 > OLS 估计 0.0800')
    expect(screen.getByTestId('agent-cursor-prompt')).not.toHaveTextContent('IV estimate')
    expect(screen.getAllByTestId('decision-blocker')).toHaveLength(1)
  })

  test('Unevaluated does not show Show me', () => {
    renderRail(
      <AgentRail
        ws={ws({
          workbenchTab: 'evidence',
          research: {
            surprise: { status: 'Unevaluated', observed: null },
          },
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={false}
        hasSuccessfulEstimate={true}
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.queryByTestId('agent-cursor-show-me')).not.toBeInTheDocument()
  })

  test('no_criteria Unevaluated does not show Show me', () => {
    renderRail(
      <AgentRail
        ws={ws({
          workbenchTab: 'evidence',
          research: {
            surprise: {
              status: 'Unevaluated',
              unevaluated_reason: 'no_criteria',
              observed: null,
              expected: null,
            },
          },
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={false}
        hasSuccessfulEstimate={true}
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.queryByTestId('agent-cursor-show-me')).not.toBeInTheDocument()
    expect(screen.queryByTestId('agent-cursor-prompt')).not.toBeInTheDocument()
  })

  test('Inconclusive does not show Show me', () => {
    renderRail(
      <AgentRail
        ws={ws({
          workbenchTab: 'evidence',
          research: {
            surprise: { status: 'Inconclusive' },
          },
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={false}
        hasSuccessfulEstimate={true}
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.queryByTestId('agent-cursor-show-me')).not.toBeInTheDocument()
  })
})

describe('AgentRail spec_run progress (M2)', () => {
  test('shows real per-spec progress while a spec_run is active', () => {
    renderRail(
      <AgentRail
        ws={ws({
          activeRun: { run_id: 'run-spec-1', kind: 'spec_run', status: 'RUNNING' },
          specRunProgress: { done: 3, total: 12 },
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={false}
        hasSuccessfulEstimate={false}
        onOpenEvidence={vi.fn()}
      />,
    )
    const task = screen.getByTestId('agent-current-task')
    expect(task).toHaveAttribute('data-busy', 'true')
    expect(task).toHaveTextContent('正在运行分析方案 3/12')
    expect(task).not.toHaveTextContent('空闲')
    expect(task).not.toHaveTextContent('后台运行监控中')
  })

  test('indeterminate wording when the progress denominator is unknown', () => {
    renderRail(
      <AgentRail
        ws={ws({
          activeRun: { run_id: 'run-spec-2', kind: 'spec_run', status: 'RUNNING' },
          specRunProgress: null,
        })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={false}
        hasSuccessfulEstimate={false}
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.getByTestId('agent-current-task')).toHaveTextContent('正在运行分析方案…')
  })

  test('terminal spec_run clears the background-run claim (no stale monitoring)', () => {
    renderRail(
      <AgentRail
        ws={ws({ activeRun: null, specRunProgress: null })}
        decision={null}
        waiting={null}
        suggestions={[]}
        showLinkedEvidence={false}
        hasSuccessfulEstimate={false}
        onOpenEvidence={vi.fn()}
      />,
    )
    expect(screen.getByTestId('agent-current-task')).toHaveAttribute('data-busy', 'false')
    expect(screen.queryByText(/后台运行监控中/)).not.toBeInTheDocument()
  })
})

