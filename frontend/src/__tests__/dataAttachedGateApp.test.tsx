import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import App from '../App'
import { I18nProvider } from '../lib/i18n'
import { API_BASE } from '../lib/apiBase'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('DC-FE-gate App wiring', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    localStorage.clear()
    sessionStorage.clear()
    localStorage.setItem('econpaper_access_token', 'test-token-for-auth')
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('formal snapshot without dataAttached diverts Table 1 / direction / estimate to attach', async () => {
    localStorage.setItem('econpaper_session_id', 'sess-unattached')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-unattached')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              exists: true,
              session_id: 'sess-unattached',
              has_dataset: true,
              upload_readiness: 'READY',
              dataAttached: false,
              dataset: { name: 'panel.csv', rows: 4, columns: ['income', 'age'] },
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      return Promise.resolve(new Response('{}', { status: 200 }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    expect(await screen.findByTestId('decision-blocker-title')).toHaveTextContent('确认挂接数据')
    expect(screen.getByTestId('direction-disabled-reason')).toHaveTextContent('请先确认挂接数据')
    fireEvent.submit(screen.getByTestId('direction-form'))
    expect(mockFetch.mock.calls.some((call) => String(call[0]).includes('/direction'))).toBe(false)

    fireEvent.click(screen.getByTestId('run-btn'))
    expect(await screen.findByTestId('dataset-summary')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('decision-blocker-action'))
    expect(screen.getByTestId('dataset-summary')).toBeInTheDocument()
  })

  test('formal snapshot with dataAttached allows direction after ingest READY', async () => {
    localStorage.setItem('econpaper_session_id', 'sess-attached')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-attached')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              exists: true,
              session_id: 'sess-attached',
              has_dataset: true,
              upload_readiness: 'READY',
              dataAttached: true,
              dataset: { name: 'panel.csv', rows: 4, columns: ['income', 'age'] },
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      return Promise.resolve(new Response('{}', { status: 200 }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    expect(await screen.findByTestId('direction-form')).toBeInTheDocument()
    expect(screen.queryByTestId('direction-disabled-reason')).not.toBeInTheDocument()
    expect(screen.queryByTestId('decision-blocker-title')).not.toHaveTextContent('确认挂接数据')
  })

  test('409 upload_not_ready on direction returns to attach-confirm', async () => {
    localStorage.setItem('econpaper_session_id', 'sess-409-ready')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-409-ready')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              exists: true,
              session_id: 'sess-409-ready',
              upload_readiness: 'READY',
              dataAttached: true,
              dataset: { name: 'panel.csv', rows: 2, columns: ['income', 'age'] },
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      if (href.includes('/direction')) {
        return Promise.resolve(
          new Response(JSON.stringify({ detail: { code: 'upload_not_ready' } }), {
            status: 409,
            headers: { 'Content-Type': 'application/json' },
          }),
        )
      }
      return Promise.resolve(new Response('{}', { status: 200 }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    await screen.findByTestId('direction-form')
    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对收入的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))

    expect(await screen.findByTestId('global-error-toast')).toHaveTextContent('数据尚未就绪')
    expect(await screen.findByTestId('dataset-summary')).toBeInTheDocument()
    expect(String(mockFetch.mock.calls.find((call) => String(call[0]).includes('/direction'))?.[0])).toBe(
      `${API_BASE}/sessions/sess-409-ready/direction`,
    )
  })

  test('409 session_busy on direction does not start another estimate', async () => {
    localStorage.setItem('econpaper_session_id', 'sess-409-busy')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-409-busy')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              exists: true,
              session_id: 'sess-409-busy',
              upload_readiness: 'READY',
              dataAttached: true,
              dataset: { name: 'panel.csv', rows: 2, columns: ['income', 'age'] },
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      if (href.includes('/direction')) {
        return Promise.resolve(
          new Response(JSON.stringify({ detail: { code: 'session_busy', run_id: 'run-live' } }), {
            status: 409,
            headers: { 'Content-Type': 'application/json' },
          }),
        )
      }
      return Promise.resolve(new Response('{}', { status: 200 }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    await screen.findByTestId('direction-form')
    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对收入的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))

    expect(await screen.findByTestId('global-error-toast')).toHaveTextContent('已有进行中的任务')
    expect(mockFetch.mock.calls.filter((call) => String(call[0]).includes('/direction'))).toHaveLength(1)
  })
})
