// R6 + R8 at page level: the main area and the "next step" rail must describe
// the same pending fact, an unknown assessment must not be announced as
// passed, and a `forbid` permission must not open the estimate entry.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'

import App from '../App'
import { I18nProvider } from '../lib/i18n'
import { API_BASE } from '../lib/apiBase'

class FakeEventSource {
  static latest: FakeEventSource | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: (() => void) | null = null
  closed = false
  url: string

  constructor(url: string) {
    this.url = url
    FakeEventSource.latest = this
  }

  close() {
    this.closed = true
  }

  emit(payload: Record<string, unknown>) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(payload) }))
  }
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const DESIGN = {
  status: 'confirmed',
  confirmed: true,
  proposed_at: '2026-09-17T10:00:00Z',
  confirmed_at: '2026-09-17T10:05:00Z',
  source: { title: '教育年限与工资', question: '' },
  method: 'ols',
  outcome: 'income',
  treatment: 'schooling',
  controls: [],
  qType: 'average',
}

function previewSnapshot(overrides: Record<string, unknown> = {}) {
  return {
    exists: true,
    session_id: 'sess-perm',
    has_dataset: true,
    upload_readiness: 'READY',
    dataAttached: true,
    design: DESIGN,
    research_direction: { question: '教育年限与工资', dv: 'income', iv: 'schooling', method: 'OLS' },
    prewrite_gate: 'awaiting_estimate',
    table1: {
      produced_by: 'prewrite_preview',
      columns: ['variable', 'count'],
      rows: [{ variable: 'income', count: 5 }],
      n: 5,
    },
    specification_equation: 'income = β₀ + β₁ schooling + ε',
    qType: 'average',
    specMode: 'level',
    ...overrides,
  }
}

beforeEach(() => {
  localStorage.clear()
  sessionStorage.clear()
  localStorage.setItem('econpaper_session_id', 'sess-perm')
  vi.stubGlobal('EventSource', FakeEventSource)
  FakeEventSource.latest = null
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

function renderApp() {
  render(
    <I18nProvider>
      <App />
    </I18nProvider>,
  )
}

describe('page-level consistency between the preview card and the next-step rail', () => {
  it('asks for the sample confirmation on both sides when the assessment is unknown', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        const href = String(url)
        if (href.endsWith('/auth/me')) return Promise.resolve(json({}))
        if (href.endsWith('/sessions/sess-perm')) {
          return Promise.resolve(
            json(
              previewSnapshot({
                table1Confirmed: false,
                specConfirmed: false,
              }),
            ),
          )
        }
        return Promise.resolve(json({ exists: true }))
      }),
    )

    renderApp()
    fireEvent.click(await screen.findByTestId('rail-question'))

    const card = await screen.findByTestId('prewrite-confirm')
    expect(card.textContent).not.toContain('核查已通过')
    expect(screen.getByTestId('prewrite-permission-note').textContent).toContain('尚未')

    // The rail must not say "nothing to confirm" while the card asks for the sample.
    expect(screen.queryByTestId('decision-rail-waiting')).not.toBeInTheDocument()
    const railTitle = screen.getByTestId('decision-blocker-title').textContent || ''
    expect(railTitle).toContain('样本')
    expect(screen.getByTestId('confirm-table1-btn')).toBeEnabled()
  })

  it('asks for the risk decision on both sides when the permission is confirm', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        const href = String(url)
        if (href.endsWith('/auth/me')) return Promise.resolve(json({}))
        if (href.endsWith('/sessions/sess-perm')) {
          return Promise.resolve(
            json(
              previewSnapshot({
                table1Confirmed: true,
                specConfirmed: true,
                riskConfirmed: false,
                permissions: { continue_to_estimate: 'confirm' },
              }),
            ),
          )
        }
        return Promise.resolve(json({ exists: true }))
      }),
    )

    renderApp()
    fireEvent.click(await screen.findByTestId('rail-question'))

    await screen.findByTestId('prewrite-confirm')
    expect(screen.getByTestId('decision-blocker-title').textContent).toContain('风险')
    expect(screen.getByTestId('start-estimate-btn')).toBeDisabled()
  })

  it('never opens the estimate when the permission is forbid', async () => {
    const fetchMock = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/auth/me')) return Promise.resolve(json({}))
      if (href.endsWith('/prewrite/confirm')) {
        return Promise.resolve(json({ ok: true }, 202))
      }
      if (href.endsWith('/sessions/sess-perm')) {
        return Promise.resolve(
          json(
            previewSnapshot({
              table1Confirmed: true,
              specConfirmed: true,
              permissions: { continue_to_estimate: 'forbid' },
            }),
          ),
        )
      }
      return Promise.resolve(json({ exists: true }))
    })
    vi.stubGlobal('fetch', fetchMock)

    renderApp()
    fireEvent.click(await screen.findByTestId('rail-question'))

    await screen.findByTestId('prewrite-confirm')
    const start = screen.getByTestId('start-estimate-btn')
    expect(start).toBeDisabled()
    expect(screen.getByTestId('prewrite-forbid-reason')).toBeInTheDocument()
    fireEvent.click(start)
    expect(
      fetchMock.mock.calls.filter((call) => String(call[0]).endsWith('/prewrite/confirm')),
    ).toHaveLength(0)
  })
})

describe('the recorded risk decision opens the estimate', () => {
  it('records the risk decision, reads it back and only then starts the estimate', async () => {
    let riskConfirmed = false
    let estimateStarted = false
    const fetchMock = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (href.endsWith('/auth/me')) return Promise.resolve(json({}))
      if (href.endsWith('/prewrite/confirm') && init?.method === 'POST') {
        const body = JSON.parse(String(init.body))
        if (body.action === 'record_confirms') {
          riskConfirmed = body.riskConfirmed === true
          return Promise.resolve(
            json({
              ok: true,
              prewrite_gate: 'awaiting_estimate',
              table1Confirmed: true,
              specConfirmed: true,
              riskConfirmed,
            }),
          )
        }
        estimateStarted = true
        return Promise.resolve(
          json(
            {
              run_id: 'run-est-risk',
              session_id: 'sess-perm',
              status: 'PENDING',
              events_url: `${API_BASE}/runs/run-est-risk/events`,
            },
            202,
          ),
        )
      }
      if (href.includes('/runs/run-est-risk')) {
        return Promise.resolve(
          json({
            status: 'SUCCEEDED',
            result: previewSnapshot({
              table1Confirmed: true,
              specConfirmed: true,
              riskConfirmed,
              permissions: { continue_to_estimate: 'confirm' },
              prewrite_gate: 'estimate_complete',
            }),
          }),
        )
      }
      if (href.endsWith('/sessions/sess-perm')) {
        return Promise.resolve(
          json(
            previewSnapshot({
              table1Confirmed: true,
              specConfirmed: true,
              riskConfirmed,
              permissions: { continue_to_estimate: 'confirm' },
              prewrite_gate: estimateStarted ? 'estimate_complete' : 'awaiting_estimate',
            }),
          ),
        )
      }
      return Promise.resolve(json({ exists: true }))
    })
    vi.stubGlobal('fetch', fetchMock)

    renderApp()
    fireEvent.click(await screen.findByTestId('rail-question'))

    const riskBtn = await screen.findByTestId('confirm-risk-btn')
    expect(screen.getByTestId('start-estimate-btn')).toBeDisabled()
    fireEvent.click(riskBtn)

    await waitFor(() => {
      const record = fetchMock.mock.calls.find(
        (call) =>
          String(call[0]).endsWith('/prewrite/confirm') &&
          JSON.parse(String((call[1] as RequestInit)?.body)).riskConfirmed === true,
      )
      expect(record).toBeTruthy()
    })
    await waitFor(() => expect(screen.getByTestId('risk-flag')).toHaveTextContent('已作出风险决定'))
    await waitFor(() => expect(screen.getByTestId('start-estimate-btn')).toBeEnabled())

    fireEvent.click(screen.getByTestId('start-estimate-btn'))
    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(
          (call) =>
            String(call[0]).endsWith('/prewrite/confirm') &&
            JSON.parse(String((call[1] as RequestInit)?.body)).action === 'continue_estimate',
        ),
      ).toBe(true)
    })
    await act(async () => {
      FakeEventSource.latest?.emit({ status: 'SUCCEEDED' })
      await Promise.resolve()
    })
  })
})
