import { describe, expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import WorkbenchArtifact from '../WorkbenchArtifact'
import { I18nProvider } from '../../lib/i18n'
import type { WorkspaceApi } from '../../lib/workspace'

const research = {
  teaching_case: 'card_1995',
  question: {
    prompt_en: 'Does education increase earnings?',
    outcome: { name: 'lwage', label: 'Log wage', gloss: '对数工资' },
    treatment: { name: 'educ', label: 'Years of education', gloss: '受教育年限' },
    causal_threat: { label: 'Ability and family background', gloss: '能力与家庭背景' },
    identification: { label: 'College proximity (nearc4)', gloss: '大学邻近' },
    estimand: { ols: 'OLS association', iv: 'IV local causal return' },
  },
  expectation: {
    text: 'OLS positive',
    confidence: 'medium' as const,
    version: 1,
    history: [],
  },
  specification_space: {
    status: 'proposed',
    frozen_at: null,
    frozen_before_results: false,
    revealed: false,
    definitions: [
      {
        id: 'iv_nearc4_linear',
        label: 'IV · nearc4, linear experience',
        rationale: 'College proximity as an instrument',
        dimension: 'identification',
        value: 'nearc4',
        admissible: true,
        user_decision: 'include',
        choices: [],
      },
    ],
  },
}

function mockWs(tab: 'question' | 'design'): WorkspaceApi {
  return {
    workbenchTab: tab,
    research,
    handleSaveExpectation: vi.fn(async () => undefined),
    handleFreezeSpecSpace: vi.fn(async () => undefined),
    degraded: false,
    directionOpen: true,
    directionSummary: null,
    directionBusy: false,
    directionDisabledReason: null,
    shapedQuestion: '',
    directionRecord: null,
    sampleDirection: null,
    dataColumns: ['lwage', 'educ'],
    handleDirectionSubmit: vi.fn(),
    setDirectionOpen: vi.fn(),
    identReport: null,
    writtenChapters: [],
    outline: [],
    writeBusy: false,
    canExport: false,
    writeBlockers: [],
    identFailed: false,
    hasReadout: false,
    csvName: 'card_1995.csv',
    csvRows: 3010,
    csvCols: 9,
    uploading: false,
    takeCsv: vi.fn(),
    fileInputRef: { current: null },
    edaOpen: false,
    setEdaOpen: vi.fn(),
    evidenceRefreshKey: 0,
    estimateMeta: null,
    railItems: [],
    writtenChapter: null,
  } as unknown as WorkspaceApi
}

describe('WorkbenchArtifact research lab', () => {
  test('question card, teaching badge and freeze control come from snapshot props', () => {
    const { rerender } = render(
      <I18nProvider>
        <WorkbenchArtifact
          ws={mockWs('question')}
          sessionId="sess-card"
          hasSuccessfulEstimate={false}
          onOpenDirection={vi.fn()}
          onOpenEvidence={vi.fn()}
          onSelectView={vi.fn()}
          onOpenCode={vi.fn()}
        />
      </I18nProvider>,
    )
    expect(screen.getByTestId('teaching-case-badge')).toBeInTheDocument()
    expect(screen.getByTestId('research-question-card')).toHaveTextContent('Log wage')
    expect(screen.getByTestId('research-question-card')).toHaveTextContent('Years of education')
    expect(screen.getByTestId('research-question-card')).toHaveTextContent('Ability and family background')
    expect(screen.getByTestId('research-question-card')).toHaveTextContent('College proximity')
    expect(screen.getByTestId('research-question-card')).toHaveTextContent('OLS association')
    expect(screen.getByTestId('expectation-editor')).toBeInTheDocument()

    rerender(
      <I18nProvider>
        <WorkbenchArtifact
          ws={mockWs('design')}
          sessionId="sess-card"
          hasSuccessfulEstimate={false}
          onOpenDirection={vi.fn()}
          onOpenEvidence={vi.fn()}
          onSelectView={vi.fn()}
          onOpenCode={vi.fn()}
        />
      </I18nProvider>,
    )
    expect(screen.getByTestId('spec-space')).toBeInTheDocument()
    expect(screen.getByTestId('spec-space-freeze')).toHaveTextContent('Freeze admissible space')
    expect(screen.queryByText(/βA → βB|compare/i)).not.toBeInTheDocument()
  })
})
