import { describe, expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import AgentRail from '../AgentRail'
import type { WorkspaceApi } from '../../lib/workspace'

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
    render(
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
    render(
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
    render(
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
    render(
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
    render(
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
    render(
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
    render(
      <AgentRail
        ws={ws({
          workbenchTab: 'evidence',
          research: {
            surprise: { status: 'Unexpected', observed: 'IV > OLS' },
          },
        })}
        decision={{
          title: 'Unexpected result',
          reason: 'IV > OLS',
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
    expect(screen.getByTestId('agent-cursor-prompt')).toHaveTextContent('IV > OLS')
    expect(screen.getAllByTestId('decision-blocker')).toHaveLength(1)
  })
})

