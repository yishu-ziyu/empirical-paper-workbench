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
})
