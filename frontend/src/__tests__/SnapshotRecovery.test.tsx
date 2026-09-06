import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import App from '../App'
import { I18nProvider } from '../lib/i18n'

/**
 * C3①：刷新恢复走后端，不靠前端业务存储。
 * 清空 localStorage/sessionStorage 只留 session id → 应用从
 * GET /sessions/{id} 的 Project Snapshot 恢复研究状态，并按
 * snapshot.active_run 重新订阅 /runs/{id}/events。
 */
class SnapshotRecoveryEventSource {
  static latest: SnapshotRecoveryEventSource | null = null
  static urls: string[] = []
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: (() => void) | null = null
  closed = false
  url: string

  constructor(url: string) {
    this.url = url
    SnapshotRecoveryEventSource.latest = this
    SnapshotRecoveryEventSource.urls.push(url)
  }

  close() {
    this.closed = true
  }
}

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('C3 刷新恢复走后端 snapshot', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    SnapshotRecoveryEventSource.latest = null
    SnapshotRecoveryEventSource.urls = []
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('storage 清空后凭 session id 从 snapshot 恢复，并按 active_run 订阅事件流', async () => {
    localStorage.setItem('econpaper_session_id', 'sess-recovery')
    vi.stubGlobal('EventSource', SnapshotRecoveryEventSource)
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-recovery')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              exists: true,
              has_dataset: true,
              claim: 'association',
              results: '| age | 0.9 |',
              estimate: { status: 'ok', produced_by: 'estimate', coef: 0.9, treatment_row: '| age | 0.9 |' },
              dataset: { name: 'course-panel.csv', rows: 5, columns: ['id', 'year', 'income', 'treat', 'age'] },
              outline: [{ type: 'intro', title: '引言' }],
              research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
              active_run: { run_id: 'run-recovery-9', kind: 'prewrite', status: 'RUNNING' },
            }),
        })
      }
      if (href.endsWith('/runs/run-recovery-9')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              status: 'SUCCEEDED',
              result: {
                claim: 'association',
                results: '| age | 0.9 |',
                estimate: { status: 'ok', produced_by: 'estimate', coef: 0.9 },
                research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
              },
            }),
        })
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    // 按 snapshot.active_run 重新订阅 durable run 事件流（SSE）。
    await waitFor(() =>
      expect(SnapshotRecoveryEventSource.urls).toContain('/api/runs/run-recovery-9/events'),
    )
    // 研究状态来自后端：数据集与方向无需任何前端存储副本。
    expect(await screen.findByTestId('workbench-shell')).toBeInTheDocument()
    expect(screen.getByTestId('project-name')).toHaveTextContent('OLS')
    expect(localStorage.getItem('econpaper_active_run_id:sess-recovery')).toBeNull()
    expect(sessionStorage.getItem('econpaper_csv_meta')).toBeNull()
    expect(sessionStorage.getItem('econpaper_data_columns')).toBeNull()
    expect(sessionStorage.getItem('econpaper_research_lab')).toBeNull()

    // run 到达终态后重新读取 snapshot，右侧不再有本地 run 句柄残留。
    await actOnce(async () => {
      SnapshotRecoveryEventSource.latest?.onmessage?.(
        new MessageEvent('message', { data: JSON.stringify({ status: 'SUCCEEDED' }) }),
      )
    })
    await waitFor(() => {
      const calls = mockFetch.mock.calls.filter((c) => String(c[0]).endsWith('/sessions/sess-recovery'))
      expect(calls.length).toBeGreaterThanOrEqual(2)
    })
  })

  test('storage 清空后从 snapshot 恢复 teaching_case / expectation / freeze', async () => {
    localStorage.setItem('econpaper_session_id', 'sess-card-lab')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-card-lab')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              exists: true,
              has_dataset: true,
              session_id: 'sess-card-lab',
              dataset: {
                name: 'card_1995.csv',
                rows: 3010,
                columns: ['lwage', 'educ', 'nearc4', 'exper'],
              },
              research: {
                teaching_case: 'card_1995',
                question: {
                  prompt_en: 'Does education increase earnings?',
                  prompt_zh: '教育是否提高工资?',
                  outcome: { name: 'lwage', label: 'Log wage', gloss: '对数工资' },
                  treatment: { name: 'educ', label: 'Years of education', gloss: '受教育年限' },
                  causal_threat: {
                    label: 'Ability and family background',
                    gloss: '能力与家庭背景',
                    text: 'Ability and family background jointly influence education and earnings.',
                  },
                  identification: {
                    instrument: 'nearc4',
                    label: 'College proximity (nearc4)',
                    gloss: '大学邻近',
                  },
                  estimand: {
                    ols: 'OLS association: conditional association.',
                    iv: 'IV local causal return.',
                  },
                },
                expectation: {
                  text: 'I expect OLS to be positive.',
                  confidence: 'medium',
                  version: 2,
                  history: [{ version: 2, text: 'I expect OLS to be positive.', confidence: 'medium', at: '2026-09-06T00:00:00+00:00', kind: 'edit' }],
                },
                specification_space: {
                  status: 'frozen',
                  frozen_at: '2026-09-06T00:00:00+00:00',
                  frozen_before_results: true,
                  revealed: false,
                  definitions: [
                    {
                      id: 'ols_linear_exper',
                      label: 'OLS · linear experience',
                      rationale: 'Baseline association',
                      dimension: 'estimator',
                      value: 'ols',
                      admissible: true,
                      user_decision: 'include',
                      choices: [],
                    },
                  ],
                },
              },
            }),
        })
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    expect(await screen.findByTestId('project-name')).toHaveTextContent(
      'Does education increase earnings?',
    )
    expect(screen.getByTestId('workbench-title')).toHaveTextContent(
      'Does education increase earnings?',
    )
    expect(screen.getByTestId('project-name')).not.toHaveTextContent('card_1995.csv')
    expect(screen.getByTestId('workbench-title')).not.toHaveTextContent('card_1995.csv')
    expect(screen.getByTestId('rail-question')).toHaveTextContent('已确认')
    expect(screen.getByTestId('rail-question')).not.toHaveTextContent('待确认方向')
    expect(screen.getByTestId('workbench-subtitle')).not.toHaveTextContent(
      '尚未设定研究方向',
    )
    expect(screen.getByTestId('rail-design')).toHaveTextContent('Admissible space frozen')

    fireEvent.click(screen.getByTestId('rail-question'))
    expect(await screen.findByTestId('teaching-case-badge')).toBeInTheDocument()
    expect(screen.getByTestId('research-question-card')).toHaveTextContent('Log wage')
    expect(screen.getByTestId('research-question-card')).toHaveTextContent('Years of education')
    expect(screen.getByTestId('expectation-editor').querySelector('textarea')).toHaveValue(
      'I expect OLS to be positive.',
    )
    expect(screen.getByTestId('expectation-confidence')).toHaveValue('medium')
    expect(localStorage.getItem('econpaper_research_lab')).toBeNull()
    expect(sessionStorage.getItem('econpaper_expectation')).toBeNull()

    fireEvent.click(screen.getByTestId('rail-design'))
    expect(screen.getByTestId('spec-space')).toBeInTheDocument()
    expect(screen.getByTestId('spec-space-freeze')).toBeInTheDocument()
    expect(screen.getByTestId('spec-space')).toHaveTextContent('OLS · linear experience')
  })

  test('storage 清空后从 snapshot 恢复 specification_runs 与 claim', async () => {
    localStorage.setItem('econpaper_session_id', 'sess-card-claim')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-card-claim')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({
              exists: true,
              has_dataset: true,
              session_id: 'sess-card-claim',
              dataset: {
                name: 'card_1995.csv',
                rows: 3010,
                columns: ['lwage', 'educ', 'nearc4', 'exper'],
              },
              research: {
                teaching_case: 'card_1995',
                question: {
                  prompt_en: 'Does education increase earnings?',
                  prompt_zh: '教育是否提高工资?',
                },
                expectation: {
                  text: 'I expect OLS to be positive.',
                  confidence: 'high',
                  version: 1,
                  history: [],
                },
                specification_space: {
                  status: 'frozen',
                  frozen_at: '2026-09-06T00:00:00+00:00',
                  frozen_before_results: true,
                  revealed: true,
                  definitions: [],
                },
                specification_runs: [
                  {
                    id: 'run-ols',
                    spec_id: 'ols_linear_exper',
                    label: 'OLS · linear experience',
                    status: 'ok',
                    method: 'ols',
                    coef: 0.07,
                    se: 0.004,
                    n: 3010,
                  },
                  {
                    id: 'run-iv',
                    spec_id: 'iv_nearc4_linear',
                    label: 'IV · nearc4',
                    status: 'ok',
                    method: 'iv',
                    coef: 0.13,
                    se: 0.05,
                    n: 3010,
                  },
                ],
                claim: {
                  id: 'claim-1',
                  supported_wording: 'Education is positively associated with earnings.',
                  conditionally_supported_wording:
                    'Under the college-proximity IV assumptions, IV estimates suggest a positive local causal return to schooling.',
                  unsupported_wording:
                    "One more year of education raises everyone's wage by 13%.",
                  approved_by_user: true,
                  unresolved_assumptions: ['exclusion'],
                  version: 1,
                },
              },
            }),
        })
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    expect(await screen.findByTestId('project-name')).toHaveTextContent(
      'Does education increase earnings?',
    )
    expect(screen.getByTestId('rail-question')).toHaveTextContent('已确认')
    fireEvent.click(screen.getByTestId('rail-question'))
    expect(await screen.findByTestId('research-question-card')).toHaveTextContent(
      'Does education increase earnings?',
    )
    expect(screen.getByTestId('expectation-editor').querySelector('textarea')).toHaveValue(
      'I expect OLS to be positive.',
    )
    fireEvent.click(screen.getByTestId('rail-evidence'))
    expect(await screen.findByTestId('claim-ledger')).toBeInTheDocument()
    expect(screen.getByTestId('claim-supported')).toHaveTextContent(
      'Education is positively associated with earnings.',
    )
    expect(screen.getByTestId('claim-approved')).toHaveTextContent('Approved')
    expect(screen.getByTestId('evidence-lab')).toHaveTextContent('OLS · linear experience')
  })
})

async function actOnce(fn: () => Promise<void> | void) {
  const { act } = await import('@testing-library/react')
  await act(async () => {
    await fn()
  })
}
