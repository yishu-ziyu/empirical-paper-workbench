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
    sessionStorage.clear()
    localStorage.setItem("econpaper_access_token", "test-token-for-auth")
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('无 session 时先进对话首页，不摊开工作台', () => {
    renderWithI18n(<App />)

    expect(screen.getByTestId('home-page')).toBeInTheDocument()
    expect(screen.getByTestId('direction-chat-input')).toBeInTheDocument()
    expect(screen.getByTestId('home-upload-btn')).toBeInTheDocument()
    expect(screen.getByTestId('home-sample-btn')).toBeInTheDocument()
    expect(screen.queryByTestId('direction-section')).not.toBeInTheDocument()
    expect(screen.queryByTestId('desk-page')).not.toBeInTheDocument()
  })

  test('首页里点上传即打开文件选择（对话不换页）', () => {
    renderWithI18n(<App />)
    fireEvent.click(screen.getByTestId('home-upload-btn'))
    expect(screen.getByTestId('file-input')).toBeInTheDocument()
    expect(screen.queryByTestId('desk-page')).not.toBeInTheDocument()
  })

  test('未上传时不显示 EdaSidebar', () => {
    renderWithI18n(<App />)
    expect(screen.queryByTestId('eda-sidebar')).not.toBeInTheDocument()
  })

  test('有 session 无方向时不摊写章，中栏是方向表', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ exists: true }) }))
    localStorage.setItem('econpaper_session_id', 'test-sess')
    renderWithI18n(<App />)
    expect(await screen.findByTestId('direction-section')).toBeInTheDocument()
    expect(screen.getByTestId('now-hint')).toHaveTextContent('填写研究问题')
    expect(screen.queryByTestId('write-chapter-intro')).not.toBeInTheDocument()
    expect(screen.queryByTestId('editor-content')).not.toBeInTheDocument()
    expect(screen.queryByTestId('agent-panel-content')).not.toBeInTheDocument()
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

    expect(screen.getByTestId('home-page')).toBeInTheDocument()

    // 触发文件选择 → 模拟选择 CSV
    const fileInput = screen.getByTestId('file-input')
    const file = new File(['a,b\n1,2'], 'test.csv', { type: 'text/csv' })
    fireEvent.change(fileInput, { target: { files: [file] } })

    // 等待上传完成 → sessionId 显示
    await waitFor(() => {
      expect(screen.getByTestId('direction-section')).toBeInTheDocument()
    })
    expect(screen.getByTestId('session-ready')).toBeInTheDocument()
    expect(screen.queryByText(/sess-abc-123/i)).not.toBeInTheDocument()
    expect(screen.getByTestId('export-doc-btn')).toBeDisabled()
    expect(screen.getByTestId('export-code-btn')).toBeDisabled()

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
              robustness_status: 'ran',
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

    fireEvent.click(screen.getByTestId('direction-chat-to-form'))
    fireEvent.change(screen.getByLabelText(/研究问题/), {
      target: { value: '教育对收入的影响' },
    })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))

    await waitFor(() => {
      expect(screen.getByTestId('ident-report')).toBeInTheDocument()
    })
    expect(screen.getByTestId('ident-report')).toHaveTextContent('识别诊断套餐')
    expect(screen.getByText('引言')).toBeInTheDocument()
    expect(screen.getByTestId('instrument-readout')).toBeInTheDocument()
    expect(screen.getByTestId('readout-claim')).toHaveTextContent('相关')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('age')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('0.1234')
    expect(screen.getByTestId('readout-robust')).toHaveTextContent('已跑')
    expect(screen.getByTestId('write-chapter-results')).toBeInTheDocument()
    expect(screen.queryByTestId('editor-content')).not.toBeInTheDocument()
  })

  test('刷新后从 session 回填读数，不必再交一次方向', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/test-sess')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              exists: true,
              claim: 'association',
              star_rating: null,
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| treat | 0.08 | 0.05 | 0.12 |' },
              outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
              research_direction: { method: 'DiD', dv: 'oop', iv: 'treat_post' },
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
    expect(await screen.findByTestId('instrument-readout')).toBeInTheDocument()
    expect(screen.getByTestId('readout-claim')).toHaveTextContent('相关')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('treat')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('0.08')
    expect(screen.getByTestId('direction-summary')).toHaveTextContent('DiD')
    expect(screen.getByTestId('write-chapter-intro')).toBeInTheDocument()
    expect(screen.queryByTestId('editor-content')).not.toBeInTheDocument()
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
    expect(screen.getByTestId('home-upload-btn')).toBeDisabled()
  })

  test('课设样例预填方向并显示列名', async () => {
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/samples/course-panel.csv')) {
        return Promise.resolve({
          ok: true,
          blob: () =>
            Promise.resolve(
              new Blob(['id,year,income,treat,age\n1,2011,8.2,0,52'], { type: 'text/csv' }),
            ),
        })
      }
      if (href.includes('/upload')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              session_id: 'sess-sample',
              dataset_meta: {
                columns: ['id', 'year', 'income', 'treat', 'age'],
                rows: 1,
                dtypes: {},
                missing_count: 0,
              },
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
    fireEvent.click(screen.getByTestId('home-sample-btn'))
    await waitFor(() => {
      expect(screen.getByTestId('direction-design-card')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByTestId('direction-chat-to-form'))
    expect(screen.getByTestId('direction-form')).toBeInTheDocument()
    expect(screen.getByLabelText(/因变量/i)).toHaveValue('income')
    expect(screen.getByLabelText(/自变量/i)).toHaveValue('age')
    expect(screen.getByTestId('method-selector')).toHaveValue('OLS')
    expect(screen.getByLabelText(/模板/i)).toHaveValue('undergrad')
    expect(screen.getByTestId('data-columns')).toHaveTextContent('income')
    expect(screen.getByLabelText(/研究问题/i)).toHaveValue('这份课设样例里，年龄和收入是否相关？')
  })

  test('刷新后仍保留课设样例预填', async () => {
    sessionStorage.setItem(
      'econpaper_sample_direction',
      JSON.stringify({
        question: '这份课设样例里，年龄和收入是否相关？',
        dv: 'income',
        iv: 'age',
        controls: 'treat',
        method: 'OLS',
        template: 'undergrad',
      }),
    )
    sessionStorage.setItem(
      'econpaper_data_columns',
      JSON.stringify(['id', 'year', 'income', 'treat', 'age']),
    )
    localStorage.setItem('econpaper_session_id', 'sess-sample')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ exists: true, currentStage: 0, stages: [] }),
      }),
    )
    renderWithI18n(<App />)
    fireEvent.click(await screen.findByTestId('direction-chat-to-form'))
    expect(await screen.findByLabelText(/因变量/i)).toHaveValue('income')
    expect(screen.getByTestId('method-selector')).toHaveValue('OLS')
    expect(screen.getByTestId('data-columns')).toHaveTextContent('income')
  })
})