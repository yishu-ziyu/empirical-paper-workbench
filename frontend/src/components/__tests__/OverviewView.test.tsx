import { describe, expect, test, vi, beforeEach } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import OverviewView from '../OverviewView'
import { I18nProvider } from '../../lib/i18n'
import { LangPills } from '../UnauthHeader'
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
  beforeEach(() => {
    localStorage.clear()
  })

  test('renders Key Results rows from array-shaped table_rows', () => {
    render(
      <I18nProvider>
        <OverviewView
          ws={overviewWs()}
          sessionId="sess-1"
          hasSuccessfulEstimate
          onSelectView={vi.fn()}
          onOpenEvidence={vi.fn()}
          onOpenDirection={vi.fn()}
        />
      </I18nProvider>,
    )
    const table = screen.getByTestId('overview-results-table')
    expect(table).toHaveTextContent('age')
    expect(table).toHaveTextContent('-0.0687')
    expect(table).toHaveTextContent('treat')
    expect(table).toHaveTextContent('0.2031')
  })

  test('chrome is a single UI language', () => {
    render(
      <I18nProvider>
        <LangPills />
        <OverviewView
          ws={overviewWs()}
          sessionId="sess-1"
          hasSuccessfulEstimate
          onSelectView={vi.fn()}
          onOpenEvidence={vi.fn()}
          onOpenDirection={vi.fn()}
        />
      </I18nProvider>,
    )
    const view = screen.getByTestId('overview-view')
    expect(view).toHaveTextContent('数据集')
    expect(view).toHaveTextContent('样本行数')
    expect(view).toHaveTextContent('研究进度')
    expect(view).not.toHaveTextContent('Dataset')
    fireEvent.click(screen.getByRole('button', { name: 'English' }))
    expect(screen.getByTestId('overview-view')).toHaveTextContent('Dataset')
    expect(screen.getByTestId('overview-view')).toHaveTextContent('Sample size')
    expect(screen.getByTestId('overview-view')).toHaveTextContent('Study progress')
    expect(screen.getByTestId('overview-view')).not.toHaveTextContent('数据集')
  })
})
