import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
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
})

async function actOnce(fn: () => Promise<void> | void) {
  const { act } = await import('@testing-library/react')
  await act(async () => {
    await fn()
  })
}
