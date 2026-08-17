import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../App'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('App 三栏布局', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    localStorage.clear()
    localStorage.setItem("econpaper_access_token", "test-token-for-auth")
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('无 session 时先进入空桌，不摊开工作台', () => {
    renderWithI18n(<App />)

    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
    expect(screen.getByTestId('upload-btn')).toBeInTheDocument()
    expect(screen.queryByTestId('direction-section')).not.toBeInTheDocument()
    expect(screen.queryByTestId('journey-stage-0')).not.toBeInTheDocument()
    expect(screen.queryByTestId('welcome-card')).not.toBeInTheDocument()
  })

  test('未上传时不显示 EdaSidebar', () => {
    renderWithI18n(<App />)
    expect(screen.queryByTestId('eda-sidebar')).not.toBeInTheDocument()
  })

  test('左栏从 state 渲染章节列表（T-02 仅 1 章 title）', () => {
    // Mock session存在时Outline渲染章节标题
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ exists: true }) }))
    localStorage.setItem('econpaper_session_id', 'test-sess')
    renderWithI18n(<App />)
    expect(screen.getByText(/title/i)).toBeInTheDocument()
  })

  test('上传 CSV 成功后 sessionId 从 response 获取并显示', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          session_id: 'sess-abc-123',
          dataset_meta: {
            columns: ['age', 'income'],
            rows: 100,
            dtypes: { age: 'int64', income: 'float64' },
            missing_count: 0,
          },
        }),
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    expect(screen.getByTestId('desk-page')).toBeInTheDocument()

    // 触发文件选择 → 模拟选择 CSV
    const fileInput = screen.getByTestId('file-input')
    const file = new File(['a,b\n1,2'], 'test.csv', { type: 'text/csv' })
    fireEvent.change(fileInput, { target: { files: [file] } })

    // 等待上传完成 → sessionId 显示
    await waitFor(() => {
      expect(screen.getByTestId('session-id-indicator')).toBeInTheDocument()
    })
    expect(screen.getByText(/sess-abc-123/i)).toBeInTheDocument()

    // Header 不再显示提示文字（已显示 sessionId 代替）
    // Editor 空态仍显示相同文案，所以用 session-id-indicator 验证 header 状态
    expect(screen.getByTestId('session-id-indicator')).toHaveTextContent('sess-abc-123')

    // fetch 被正确调用（localStorage 为空，不会触发 mount 时的 session verify）
    // 注意：mockFetch 可能被其他测试的全局 mock 干扰，检查至少有一次 /upload 调用
    expect(mockFetch.mock.calls.length).toBeGreaterThanOrEqual(1)
    const uploadCall = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/upload'))
    expect(uploadCall).toBeDefined()
    const [, init] = uploadCall!
    expect(init.method).toBe('POST')
    expect(init.body).toBeInstanceOf(FormData)
  })

  test('上传失败时显示错误信息', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 400, json: () => Promise.resolve({ detail: 'bad' }) }),
    )

    renderWithI18n(<App />)

    const fileInput = screen.getByTestId('file-input')
    const file = new File(['a,b\n1,2'], 'test.csv', { type: 'text/csv' })
    fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByTestId('upload-error')).toBeInTheDocument()
    })
    expect(screen.getByText(/HTTP 400/i)).toBeInTheDocument()
  })

  test('提交研究方向后显示识别报告', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
              research_direction: { method: 'OLS' },
              star_rating: null,
              identification_failed: false,
              identification_report: '当前方法没有对应的识别诊断套餐',
              claim: 'association',
              literature_source: 'mock',
              estimate: { treatment_row: '| age | 0.1234 | 0.0456 | 0.0078 |', produced_by: 'estimate' },
              results: '| age | 0.1234 | 0.0456 | 0.0078 |',
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

    fireEvent.change(screen.getByLabelText(/研究问题/), {
      target: { value: '教育对收入的影响' },
    })
    fireEvent.submit(screen.getByTestId('direction-form'))

    await waitFor(() => {
      expect(screen.getByTestId('ident-report')).toBeInTheDocument()
    })
    expect(screen.getByTestId('ident-report')).toHaveTextContent('识别诊断套餐')
    expect(screen.getByText('引言')).toBeInTheDocument()
    expect(screen.getByTestId('instrument-readout')).toBeInTheDocument()
    expect(screen.getByTestId('readout-claim')).toHaveTextContent('association')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('| age | 0.1234 |')
    expect(screen.getByTestId('write-chapter-results')).toBeInTheDocument()
  })

  test('上传中按钮显示"上传中..."并禁用', async () => {
    // fetch 永不 resolve
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise(() => {})))

    renderWithI18n(<App />)

    const fileInput = screen.getByTestId('file-input')
    const file = new File(['a,b\n1,2'], 'test.csv', { type: 'text/csv' })
    fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText(/上传中\.\.\./i)).toBeInTheDocument()
    })
    expect(screen.getByTestId('upload-btn')).toBeDisabled()
  })
})