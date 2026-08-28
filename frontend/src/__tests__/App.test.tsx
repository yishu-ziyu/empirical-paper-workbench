import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'
import { I18nProvider } from '../lib/i18n'
import { API_BASE } from '../lib/apiBase'
import { CLEAN_STEPS, PAPER_NODES } from '../lib/paperPath'

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

  test('无 session 时先进入引导，不摊开工作台', () => {
    renderWithI18n(<App />)

    expect(screen.getByTestId('guide-page')).toBeInTheDocument()
    expect(screen.getByTestId('guide-steps')).toBeInTheDocument()
    expect(screen.getByTestId('guide-upload-btn')).toBeInTheDocument()
    expect(screen.queryByTestId('direction-section')).not.toBeInTheDocument()
    expect(screen.queryByTestId('journey-stage-0')).not.toBeInTheDocument()
    expect(screen.queryByTestId('desk-page')).not.toBeInTheDocument()
  })

  test('引导里点先写在纸上才进入空桌', () => {
    renderWithI18n(<App />)
    fireEvent.click(screen.getByTestId('guide-write-paper'))
    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
    expect(screen.queryByTestId('direction-section')).not.toBeInTheDocument()
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
    expect(screen.getByTestId('product-journey')).toHaveTextContent('上传')
    expect(screen.getByTestId('product-journey')).toHaveTextContent('方向')
    expect(screen.getByTestId('product-journey')).toHaveTextContent('估计')
    expect(screen.getByTestId('product-journey')).toHaveTextContent('按章写')
    expect(screen.queryByTestId('write-chapter-intro')).not.toBeInTheDocument()
    expect(screen.queryByTestId('editor-content')).not.toBeInTheDocument()
    expect(screen.queryByTestId('agent-panel-content')).not.toBeInTheDocument()
  })

  test('工作台右栏是锁定论文路径，不含额外站点', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ exists: true }) }))
    localStorage.setItem('econpaper_session_id', 'test-sess')
    renderWithI18n(<App />)
    expect(await screen.findByTestId('paper-path')).toBeInTheDocument()
    const rightPane = screen.getByTestId('agent-panel')
    expect(rightPane).toContainElement(screen.getByTestId('paper-path'))
    expect(rightPane.className).not.toMatch(/\bhidden\b|opacity-0|max-h-0|lg:block|lg:hidden/)
    const desk = screen.getByTestId('desk-columns')
    expect(desk).toContainElement(rightPane)
    expect(desk.className).not.toMatch(/grid-cols-1|lg:grid-cols/)
    expect(desk).toHaveStyle({
      display: 'grid',
      gridTemplateColumns: '220px minmax(0, 1fr) 280px',
    })
    expect(rightPane).toHaveStyle({ minWidth: '280px' })
    for (const id of PAPER_NODES) {
      expect(rightPane).toContainElement(screen.getByTestId(`paper-path-${id}`))
    }
    expect(screen.getByTestId('paper-path-set_direction')).toHaveAttribute('data-status', 'paused')
    for (const id of CLEAN_STEPS) {
      expect(rightPane).toContainElement(screen.getByTestId(`clean-step-${id}`))
      expect(screen.getByTestId(`clean-step-${id}`)).toHaveAttribute('data-status', 'pending')
    }
    expect(screen.getByTestId('workbench-tab-paper')).toBeInTheDocument()
    expect(screen.getByTestId('workbench-tab-data')).toBeInTheDocument()
    expect(screen.getByTestId('workbench-tab-format')).toBeInTheDocument()
    expect(screen.queryByTestId('paper-path-generate_title')).not.toBeInTheDocument()
    expect(screen.queryByTestId('paper-path-identification_verify')).not.toBeInTheDocument()
    expect(screen.queryByTestId('paper-path-search_literature')).not.toBeInTheDocument()
    expect(screen.queryByTestId('paper-path-eda')).not.toBeInTheDocument()
    expect(screen.queryByTestId('journey-stage-0')).not.toBeInTheDocument()
  })

  test('Format 页有导出 CTA；路径 translate_code / export_docx 打开现有对话框', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ exists: true }) }))
    localStorage.setItem('econpaper_session_id', 'test-sess')
    renderWithI18n(<App />)
    expect(await screen.findByTestId('paper-path')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('workbench-tab-format'))
    expect(screen.getByTestId('format-pane')).toBeInTheDocument()
    expect(screen.getByTestId('format-export-doc-btn')).toHaveTextContent('导出论文')
    expect(screen.getByTestId('format-export-code-btn')).toHaveTextContent('导出代码')

    fireEvent.click(screen.getByTestId('paper-path-translate_code').querySelector('button')!)
    expect(screen.getByTestId('format-pane')).toBeInTheDocument()
    expect(screen.getByTestId('code-export-dialog')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('code-export-close'))

    fireEvent.click(screen.getByTestId('paper-path-export_docx').querySelector('button')!)
    expect(screen.getByTestId('format-pane')).toBeInTheDocument()
    expect(screen.getByTestId('doc-export-dialog')).toBeInTheDocument()
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

    expect(screen.getByTestId('guide-page')).toBeInTheDocument()

    // 触发文件选择 → 模拟选择 CSV
    const fileInput = screen.getByTestId('file-input')
    const file = new File(['a,b\n1,2'], 'test.csv', { type: 'text/csv' })
    fireEvent.change(fileInput, { target: { files: [file] } })

    // 等待上传完成 → sessionId 显示
    await waitFor(() => {
      expect(screen.getByTestId('direction-section')).toBeInTheDocument()
    })
    expect(screen.getByTestId('session-ready')).toBeInTheDocument()
    expect(screen.getByTestId('session-file')).toHaveTextContent('test.csv')
    expect(screen.getByTestId('direction-form')).toBeInTheDocument()
    expect(screen.queryByText(/sess-abc-123/i)).not.toBeInTheDocument()
    expect(screen.getByTestId('export-doc-btn')).toBeDisabled()
    expect(screen.getByTestId('export-code-btn')).toBeDisabled()

    // fetch 被正确调用（localStorage 为空，不会触发 mount 时的 session verify）
    // 注意：mockFetch 可能被其他测试的全局 mock 干扰，检查至少有一次 /upload 调用
    expect(mockFetch.mock.calls.length).toBeGreaterThanOrEqual(1)
    const uploadCall = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/upload'))
    expect(uploadCall).toBeDefined()
    expect(String(uploadCall![0])).toBe(`${API_BASE}/upload`)
    expect(String(uploadCall![0])).not.toMatch(/localhost:8000|127\.0\.0\.1:8000/)
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
    expect(screen.getByTestId('readout-question')).toHaveTextContent('教育对收入的影响')
    expect(screen.getByTestId('readout-code')).toHaveTextContent('0.1234')
    expect(screen.getByTestId('readout-claim')).toHaveTextContent('相关')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('age')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('0.1234')
    expect(screen.getByTestId('readout-robust')).toHaveTextContent('已跑')
    expect(screen.getByTestId('write-chapter-results')).toBeInTheDocument()
    expect(screen.getByTestId('info-confirm')).toBeInTheDocument()
    expect(screen.getByTestId('chapter-pause')).toBeInTheDocument()
    expect(screen.getByTestId('outline-approve-btn')).toBeInTheDocument()
    expect(screen.getByTestId('agent-panel')).toContainElement(screen.getByTestId('paper-path'))
    expect(screen.getByTestId('agent-panel')).toContainElement(screen.getByTestId('clean-step-profiling'))
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
      expect(screen.getByTestId('guide-upload-btn')).toHaveTextContent(/上传中/)
    })
    expect(screen.getByTestId('guide-upload-btn')).toBeDisabled()
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
    fireEvent.click(screen.getByTestId('guide-sample-btn'))
    await waitFor(() => {
      expect(screen.getByTestId('direction-form')).toBeInTheDocument()
    })
    expect(screen.getByLabelText(/因变量/i)).toHaveValue('income')
    expect(screen.getByLabelText(/自变量/i)).toHaveValue('age')
    expect(screen.getByTestId('method-selector')).toHaveValue('OLS')
    expect(screen.getByLabelText(/模板/i)).toHaveValue('undergrad')
    expect(screen.getByTestId('data-columns')).toHaveTextContent('income')
    expect(screen.getByLabelText(/研究问题/i)).toHaveValue('这份课设样例里，年龄和收入是否相关？')
    const sampleCsvCall = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/samples/course-panel.csv'))
    const sampleUpload = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/upload'))
    expect(String(sampleCsvCall![0])).toBe('/samples/course-panel.csv')
    expect(String(sampleUpload![0])).toBe(`${API_BASE}/upload`)
    expect(String(sampleUpload![0])).not.toMatch(/localhost:8000|127\.0\.0\.1:8000/)
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
    expect(await screen.findByLabelText(/因变量/i)).toHaveValue('income')
    expect(screen.getByTestId('method-selector')).toHaveValue('OLS')
    expect(screen.getByTestId('data-columns')).toHaveTextContent('income')
  })

  test('Approve Outline POSTs /resume and does not generate-chapter', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/resume')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            ok: true,
            outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
          }),
        })
      }
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
            research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
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

    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对收入的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))
    expect(await screen.findByTestId('outline-approve-btn')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('outline-approve-btn'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/resume'))).toBe(true)
    })
    const resumeCall = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/resume'))!
    expect(JSON.parse(String(resumeCall[1].body)).outline).toEqual([
      { type: 'intro', title: '引言' },
      { type: 'results', title: '结果' },
    ])
    expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toBe(false)
    expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/approve-chapter'))).toBe(false)
    await waitFor(() => {
      expect(screen.queryByTestId('outline-approve-btn')).not.toBeInTheDocument()
    })
  })

  test('I-decide chapters change the outline posted to /resume', async () => {
    const user = userEvent.setup()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/resume')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ok: true, outline: [{ type: 'intro', title: '引言' }] }),
        })
      }
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
            research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
            identification_failed: false,
            identification_report: 'ok',
            claim: 'association',
            literature_source: 'mock',
            robustness_status: 'ran',
            estimate: { treatment_row: '| age | 0.1 | 0.0 | 0.0 |', produced_by: 'estimate' },
            results: '| age | 0.1 |',
          }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对收入的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))
    expect(await screen.findByTestId('chapters-me')).toBeInTheDocument()
    await user.click(screen.getByTestId('chapters-me'))
    await user.click(screen.getByTestId('pause-keep-results'))
    await user.click(screen.getByTestId('outline-approve-btn'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/resume'))).toBe(true)
    })
    const resumeCall = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/resume'))!
    expect(JSON.parse(String(resumeCall[1].body)).outline).toEqual([{ type: 'intro', title: '引言' }])
    expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toBe(false)
  })

  test('I-decide paragraphs appear in generate-chapter render_kwargs', async () => {
    const user = userEvent.setup()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/generate-chapter')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            chapter: { type: 'intro', title: '引言', content: '正文', status: 'generated' },
            body_chapters: [{ type: 'intro', title: '引言', content: '正文', status: 'generated' }],
          }),
        })
      }
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
            research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
            identification_failed: false,
            identification_report: 'ok',
            claim: 'association',
            literature_source: 'mock',
            robustness_status: 'ran',
            estimate: { treatment_row: '| age | 0.1 | 0.0 | 0.0 |', produced_by: 'estimate' },
            results: '| age | 0.1 |',
          }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对收入的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))
    expect(await screen.findByTestId('paragraphs-me')).toBeInTheDocument()
    await user.click(screen.getByTestId('paragraphs-me'))
    fireEvent.change(screen.getByTestId('pause-paragraphs'), { target: { value: '5' } })
    await user.click(screen.getByTestId('pause-apply'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toBe(true)
    })
    const genCall = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/generate-chapter'))!
    const body = JSON.parse(String(genCall[1].body))
    expect(body.render_kwargs.paragraphs).toBe(5)
    expect(body.chapter).toEqual({ type: 'intro', title: '引言' })
    expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/resume'))).toBe(false)
  })

  test('refine 发送 POSTs /regenerate with the typed instruction', async () => {
    const user = userEvent.setup()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/regenerate')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            chapter: { type: 'intro', title: '引言', content: '改写后', status: 'generated' },
            body_chapters: [{ type: 'intro', title: '引言', content: '改写后', status: 'generated' }],
          }),
        })
      }
      if (href.endsWith('/sessions/test-sess')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            exists: true,
            claim: 'association',
            literature_source: 'mock',
            robustness_status: 'ran',
            estimate: { treatment_row: '| age | 0.1 | 0.0 | 0.0 |' },
            results: '| age | 0.1 |',
            outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
            body_chapters: [{ type: 'intro', title: '引言', content: '原稿', status: 'generated' }],
            research_direction: { method: 'OLS', dv: 'income', iv: 'age', question: '教育对收入的影响' },
          }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    expect(await screen.findByTestId('refine-send-btn')).toBeInTheDocument()
    expect(screen.getByTestId('refine-send-btn').tagName).toBe('BUTTON')
    await user.type(screen.getByTestId('refine-input'), '写短一点')
    await user.click(screen.getByTestId('refine-send-btn'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/regenerate'))).toBe(true)
    })
    const regenCall = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/regenerate'))!
    expect(JSON.parse(String(regenCall[1].body))).toEqual({
      chapter_index: 0,
      instruction: '写短一点',
    })
    expect(await screen.findByText('改写后')).toBeInTheDocument()
  })

  test('refresh hydrates controls and csv meta into info-confirm', async () => {
    sessionStorage.setItem(
      'econpaper_csv_meta',
      JSON.stringify({ sessionId: 'test-sess', name: 'macro.csv', rows: 42, cols: 8 }),
    )
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
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| age | 0.1 | 0.0 | 0.0 |' },
              results: '| age | 0.1 |',
              outline: [{ type: 'intro', title: '引言' }],
              research_direction: {
                method: 'OLS',
                dv: 'income',
                iv: 'age',
                controls: ['gdp', 'pop'],
                question: '教育对收入的影响',
              },
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    expect(await screen.findByTestId('info-confirm')).toBeInTheDocument()
    expect(screen.getByTestId('info-controls')).toHaveTextContent('gdp, pop')
    expect(screen.getByTestId('info-dataset')).toHaveTextContent('macro.csv')
    expect(screen.getByTestId('info-dataset')).toHaveTextContent('42')
    expect(screen.getByTestId('info-dataset')).not.toHaveTextContent(/^CSV$/)
  })

  test('是，再补充 remounts DirectionForm from directionRecord, not sample fallback', async () => {
    const user = userEvent.setup()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              outline: [{ type: 'intro', title: '引言' }],
              research_direction: {
                method: 'OLS',
                dv: 'wage',
                iv: 'edu',
                controls: ['age', 'gender'],
                question: '教育对工资的影响',
              },
              identification_failed: false,
              identification_report: 'ok',
              claim: 'association',
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| edu | 0.1 |', produced_by: 'estimate' },
              results: '| edu | 0.1 |',
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对工资的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'wage' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'edu' } })
    fireEvent.change(screen.getByLabelText(/控制变量/), { target: { value: 'age, gender' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))
    expect(await screen.findByTestId('info-add-more')).toBeInTheDocument()
    await user.click(screen.getByTestId('info-add-more'))
    expect(await screen.findByTestId('direction-form')).toBeInTheDocument()
    expect(screen.getByLabelText(/因变量/)).toHaveValue('wage')
    expect(screen.getByLabelText(/自变量/)).toHaveValue('edu')
    expect(screen.getByLabelText(/控制变量/)).toHaveValue('age, gender')
    expect(screen.getByTestId('method-selector')).toHaveValue('OLS')
    expect(screen.getByLabelText(/研究问题/)).toHaveValue('教育对工资的影响')
  })

  test('I-decide Apply POSTs /resume with the edited outline then generate-chapter', async () => {
    const user = userEvent.setup()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/resume')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ok: true, outline: [{ type: 'intro', title: '引言' }] }),
        })
      }
      if (href.includes('/generate-chapter')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              chapter: { type: 'intro', title: '引言', content: '正文', status: 'generated' },
            }),
        })
      }
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
              research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
              identification_failed: false,
              identification_report: 'ok',
              claim: 'association',
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| age | 0.1 |', produced_by: 'estimate' },
              results: '| age | 0.1 |',
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对收入的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))
    expect(await screen.findByTestId('chapters-me')).toBeInTheDocument()
    await user.click(screen.getByTestId('chapters-me'))
    await user.click(screen.getByTestId('pause-keep-results'))
    await user.click(screen.getByTestId('pause-apply'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/resume'))).toBe(true)
      expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toBe(true)
    })
    const resumeIdx = mockFetch.mock.calls.findIndex((c: unknown[]) => String(c[0]).includes('/resume'))
    const genIdx = mockFetch.mock.calls.findIndex((c: unknown[]) => String(c[0]).includes('/generate-chapter'))
    expect(resumeIdx).toBeGreaterThan(-1)
    expect(genIdx).toBeGreaterThan(resumeIdx)
    expect(JSON.parse(String(mockFetch.mock.calls[resumeIdx][1].body)).outline).toEqual([
      { type: 'intro', title: '引言' },
    ])
    expect(JSON.parse(String(mockFetch.mock.calls[genIdx][1].body)).chapter).toEqual({
      type: 'intro',
      title: '引言',
    })
  })

  test('locked I-decide Apply does not re-POST /resume and writes the current chapter', async () => {
    const user = userEvent.setup()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (href.includes('/resume')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ok: true,
              outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
            }),
        })
      }
      if (href.includes('/generate-chapter')) {
        const body = JSON.parse(String(init?.body || '{}')) as { chapter?: { type: string; title: string } }
        const ch = body.chapter || { type: 'intro', title: '引言' }
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              chapter: { type: ch.type, title: ch.title, content: `${ch.type}正文`, status: 'generated' },
            }),
        })
      }
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
              research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
              identification_failed: false,
              identification_report: 'ok',
              claim: 'association',
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| age | 0.1 |', produced_by: 'estimate' },
              results: '| age | 0.1 |',
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对收入的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))
    expect(await screen.findByTestId('chapters-me')).toBeInTheDocument()
    await user.click(screen.getByTestId('chapters-me'))
    await user.click(screen.getByTestId('outline-approve-btn'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.filter((c: unknown[]) => String(c[0]).includes('/resume'))).toHaveLength(1)
    })
    await user.click(screen.getByTestId('pause-apply'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.filter((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toHaveLength(1)
    })
    expect(JSON.parse(String(
      mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/generate-chapter'))![1].body,
    )).chapter.type).toBe('intro')
    expect(await screen.findByText('intro正文')).toBeInTheDocument()
    await user.click(screen.getByTestId('write-chapter-results'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.filter((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toHaveLength(2)
    })
    expect(await screen.findByText('results正文')).toBeInTheDocument()
    await user.click(screen.getByTestId('paragraphs-me'))
    fireEvent.change(screen.getByTestId('pause-paragraphs'), { target: { value: '5' } })
    await user.click(screen.getByTestId('pause-apply'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.filter((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toHaveLength(3)
    })
    const genCalls = mockFetch.mock.calls.filter((c: unknown[]) => String(c[0]).includes('/generate-chapter'))
    const lastBody = JSON.parse(String(genCalls[2][1].body))
    expect(lastBody.chapter).toEqual({ type: 'results', title: '结果' })
    expect(lastBody.render_kwargs).toEqual({ paragraphs: 5 })
    expect(mockFetch.mock.calls.filter((c: unknown[]) => String(c[0]).includes('/resume'))).toHaveLength(1)
  })

  test('refresh I-decide Apply on last written chapter does not regenerate intro', async () => {
    const user = userEvent.setup()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (href.includes('/generate-chapter')) {
        const body = JSON.parse(String(init?.body || '{}')) as { chapter?: { type: string; title: string } }
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              chapter: {
                type: body.chapter?.type,
                title: body.chapter?.title,
                content: '新写',
                status: 'generated',
              },
            }),
        })
      }
      if (href.endsWith('/sessions/test-sess')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              exists: true,
              claim: 'association',
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| age | 0.1 |' },
              results: '| age | 0.1 |',
              outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
              body_chapters: [
                { type: 'intro', title: '引言', content: '引言已写', status: 'generated' },
                { type: 'results', title: '结果', content: '结果已写', status: 'generated' },
              ],
              research_direction: { method: 'OLS', dv: 'income', iv: 'age', question: '教育对收入的影响' },
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    expect(await screen.findByTestId('pause-apply')).toBeInTheDocument()
    expect(screen.getByTestId('chapter-pause')).toHaveTextContent('配置第 2 部分')
    await user.click(screen.getByTestId('pause-apply'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toBe(true)
    })
    const genCall = mockFetch.mock.calls.find((c: unknown[]) => String(c[0]).includes('/generate-chapter'))!
    expect(JSON.parse(String(genCall[1].body)).chapter).toEqual({ type: 'results', title: '结果' })
    expect(mockFetch.mock.calls.some((c: unknown[]) => String(c[0]).includes('/resume'))).toBe(false)
  })

  test('csv meta from another session does not hydrate info-dataset', async () => {
    sessionStorage.setItem(
      'econpaper_csv_meta',
      JSON.stringify({ sessionId: 'old-sess', name: 'macro.csv', rows: 42, cols: 8 }),
    )
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
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| age | 0.1 |' },
              results: '| age | 0.1 |',
              outline: [{ type: 'intro', title: '引言' }],
              research_direction: {
                method: 'OLS',
                dv: 'income',
                iv: 'age',
                controls: ['gdp'],
                question: '教育对收入的影响',
              },
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    expect(await screen.findByTestId('info-dataset')).toBeInTheDocument()
    expect(screen.getByTestId('info-dataset')).toHaveTextContent('CSV')
    expect(screen.getByTestId('info-dataset')).not.toHaveTextContent('macro.csv')
  })

  test('logout clears csv meta so a later session cannot inherit the file', async () => {
    const user = userEvent.setup()
    sessionStorage.setItem(
      'econpaper_csv_meta',
      JSON.stringify({ sessionId: 'test-sess', name: 'macro.csv', rows: 42, cols: 8 }),
    )
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
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| age | 0.1 |' },
              outline: [{ type: 'intro', title: '引言' }],
              research_direction: { method: 'OLS', dv: 'income', iv: 'age', question: 'q' },
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    expect(await screen.findByTestId('info-dataset')).toHaveTextContent('macro.csv')
    await user.click(screen.getByRole('button', { name: '退出' }))
    expect(sessionStorage.getItem('econpaper_csv_meta')).toBeNull()
  })

  test('writeBusy blocks a second generate-chapter POST', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/generate-chapter')) {
        return new Promise(() => {})
      }
      if (href.includes('/direction')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              outline: [{ type: 'intro', title: '引言' }, { type: 'results', title: '结果' }],
              research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
              identification_failed: false,
              identification_report: 'ok',
              claim: 'association',
              literature_source: 'mock',
              robustness_status: 'ran',
              estimate: { treatment_row: '| age | 0.1 |', produced_by: 'estimate' },
              results: '| age | 0.1 |',
            }),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)
    fireEvent.change(screen.getByLabelText(/研究问题/), { target: { value: '教育对收入的影响' } })
    fireEvent.change(screen.getByLabelText(/因变量/), { target: { value: 'income' } })
    fireEvent.change(screen.getByLabelText(/自变量/), { target: { value: 'age' } })
    fireEvent.change(screen.getByLabelText(/方法/), { target: { value: 'OLS' } })
    fireEvent.submit(screen.getByTestId('direction-form'))
    const apply = await screen.findByTestId('pause-apply')
    fireEvent.click(apply)
    fireEvent.click(apply)
    fireEvent.click(screen.getByTestId('write-chapter-intro'))
    fireEvent.click(screen.getByTestId('outline-approve-btn'))
    await waitFor(() => {
      expect(mockFetch.mock.calls.filter((c: unknown[]) => String(c[0]).includes('/generate-chapter'))).toHaveLength(1)
    })
    expect(mockFetch.mock.calls.filter((c: unknown[]) => String(c[0]).includes('/resume'))).toHaveLength(0)
    expect(screen.getByTestId('pause-apply')).toBeDisabled()
    expect(screen.getByTestId('outline-approve-btn')).toBeDisabled()
  })
})