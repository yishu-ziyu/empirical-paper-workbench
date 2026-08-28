import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../App'
import { I18nProvider } from '../lib/i18n'
import { API_BASE } from '../lib/apiBase'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

// Mock WebSocket — 捕获 WSClient 创建的实例并允许测试触发 onmessage/onopen
class MockWebSocket {
  static instances: MockWebSocket[] = []
  url: string
  onmessage: ((ev: { data: string }) => void) | null = null
  onopen: ((ev: unknown) => void) | null = null
  onclose: ((ev: unknown) => void) | null = null
  onerror: ((ev: unknown) => void) | null = null
  readyState = 0

  constructor(url: string) {
    this.url = url
    MockWebSocket.instances.push(this)
  }

  send(_data: string): void {
    // no-op
  }

  close(): void {
    this.readyState = 3
  }
}

beforeEach(() => {
  MockWebSocket.instances = []
  vi.stubGlobal('WebSocket', MockWebSocket)
  vi.stubGlobal('fetch', vi.fn())
  localStorage.clear()
  localStorage.setItem("econpaper_access_token", "test-token-for-auth")
})

afterEach(() => {
  vi.unstubAllGlobals()
  localStorage.clear()
})

describe('前端集成测试', () => {
  // ── 场景 A：upload → sessionId 传递 ──────────────────────
  test('场景 A：上传文件创建 session 并传递 sessionId 到子组件', async () => {
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (String(url).includes('/upload')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ session_id: 'test-123' }),
        })
      }
      return Promise.reject(new Error('unexpected URL'))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    expect(screen.getByTestId('guide-page')).toBeInTheDocument()

    // 触发文件上传
    const fileInput = screen.getByTestId('file-input') as HTMLInputElement
    fireEvent.change(fileInput, {
      target: { files: [new File(['a,b\n1,2'], 'test.csv', { type: 'text/csv' })] },
    })

    await waitFor(() => {
      expect(screen.getByTestId('direction-section')).toBeInTheDocument()
    })
    expect(screen.getByTestId('session-ready')).toBeInTheDocument()
    expect(screen.queryByText(/test-123/i)).not.toBeInTheDocument()

    expect(localStorage.getItem('econpaper_session_id')).toBe('test-123')
    expect(screen.getByTestId('direction-section')).toBeInTheDocument()
    expect(screen.queryByTestId('editor-content')).not.toBeInTheDocument()
    expect(screen.queryByTestId('eda-sidebar')).not.toBeInTheDocument()
  })

  test('场景 B：提交方向后出现读数和按章写，不再走整篇 WebSocket', async () => {
    localStorage.setItem('econpaper_session_id', 'test-456')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
              research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
              star_rating: null,
              identification_failed: false,
              identification_report: '当前方法没有对应的识别诊断套餐',
              claim: 'association',
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| age | 0.12 | 0.04 | 0.01 |', produced_by: 'estimate' },
              results: '| age | 0.12 | 0.04 | 0.01 |',
            }),
        })
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ exists: true, currentStage: 0, stages: [] }),
      })
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    await waitFor(() => {
      expect(screen.getByTestId('direction-section')).toBeInTheDocument()
    })
    fireEvent.change(screen.getByLabelText(/研究问题/), {
      target: { value: '教育对收入的影响' },
    })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))

    await waitFor(() => {
      expect(screen.getByTestId('instrument-readout')).toBeInTheDocument()
    })
    expect(screen.getByTestId('readout-table')).toHaveTextContent('age')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('0.12')
    expect(screen.getByTestId('write-chapter-intro')).toBeInTheDocument()
    expect(MockWebSocket.instances.length).toBe(0)
    expect(screen.queryByTestId('editor-content')).not.toBeInTheDocument()
    expect(screen.queryByText(/connected/i)).not.toBeInTheDocument()
  })

  test('场景 C：页面刷新后从 session 回填读数，不重连 WebSocket', async () => {
    localStorage.setItem('econpaper_session_id', 'test-789')

    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (String(url).endsWith('/sessions/test-789')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              exists: true,
              claim: 'association',
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| treat | 0.08 | 0.05 | 0.12 |' },
              outline: [{ type: 'results', title: '结果' }],
              research_direction: { method: 'DiD', dv: 'y', iv: 'd' },
            }),
        })
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ exists: true, currentStage: 0, stages: [] }),
      })
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    await waitFor(() => {
      expect(screen.getByTestId('direction-section')).toBeInTheDocument()
    })
    expect(screen.queryByText(/test-789/i)).not.toBeInTheDocument()
    expect(await screen.findByTestId('instrument-readout')).toBeInTheDocument()
    expect(screen.getByTestId('readout-claim')).toHaveTextContent('相关')

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_BASE}/sessions/test-789`,
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer test-token-for-auth' }),
      }),
    )
    expect(MockWebSocket.instances.length).toBe(0)
  })
})