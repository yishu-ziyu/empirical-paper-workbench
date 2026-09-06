import { describe, expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import OverviewView from '../OverviewView'
import type { WorkspaceApi } from '../../lib/workspace'

function overviewWs(overrides: Partial<WorkspaceApi> = {}): WorkspaceApi {
  return {
    cleaningReport: null,
    uploadReadiness: 'READY',
    writtenChapters: [],
    literatureSource: null,
    canExport: false,
    writeBusy: false,
    outline: [],
    identFailed: false,
    directionSummary: 'OLS · income ~ age',
    directionBusy: false,
    estimateMeta: {
      status: 'ok',
      method: 'OLS',
      table_rows: [
        '| age | -0.0687 | 0.0083 | 0.0000 |',
        '| treat | 0.2031 | 0.1461 | 0.1789 |',
      ],
    },
    robustnessStatus: 'ran',
    activeRun: null,
    uploading: false,
    runFailure: null,
    dataset: { name: 'course-panel.csv', rows: 24, columns: ['income', 'age', 'treat'] },
    csvName: 'course-panel.csv',
    csvRows: 24,
    directionRecord: {
      question: '年龄和收入是否相关？',
      method: 'OLS',
      dv: 'income',
      iv: 'age',
      controls: [],
      template: '',
    },
    hasReadout: true,
    mainResults: null,
    degradations: [],
    ...overrides,
  } as WorkspaceApi
}

describe('OverviewView table_rows', () => {
  test('renders Key Results rows from array-shaped table_rows', () => {
    render(
      <OverviewView
        ws={overviewWs()}
        sessionId="sess-1"
        hasSuccessfulEstimate
        onSelectView={vi.fn()}
        onOpenEvidence={vi.fn()}
        onOpenDirection={vi.fn()}
      />,
    )
    const table = screen.getByTestId('overview-results-table')
    expect(table).toHaveTextContent('age')
    expect(table).toHaveTextContent('-0.0687')
    expect(table).toHaveTextContent('treat')
    expect(table).toHaveTextContent('0.2031')
  })
})
