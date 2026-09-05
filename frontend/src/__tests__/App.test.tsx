import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { act, render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'
import { I18nProvider } from '../lib/i18n'
import { API_BASE } from '../lib/apiBase'
import { CLEAN_STEPS, PAPER_NODES } from '../lib/paperPath'
import { CAPSULE_DELAY_MS, READING_NOTICE_MS } from '../components/ReadingFocus'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

class AppFakeEventSource {
  static latest: AppFakeEventSource | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: (() => void) | null = null
  closed = false
  url: string

  constructor(url: string) {
    this.url = url
    AppFakeEventSource.latest = this
  }

  close() {
    this.closed = true
  }
}

describe('App 三栏布局', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    localStorage.clear()
    sessionStorage.clear()
    localStorage.setItem("econpaper_access_token", "test-token-for-auth")
    AppFakeEventSource.latest = null
  })
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  test('C1 首次访问直接进空桌：无 seen_guide 无会话时首屏是 DeskPage，无落地页内容', () => {
    renderWithI18n(<App />)

    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
    expect(screen.getByTestId('desk-paper')).toBeInTheDocument()
    expect(screen.queryByText('用数据写实证论文')).not.toBeInTheDocument()
    expect(screen.queryByText('四步写出论文')).not.toBeInTheDocument()
    expect(screen.queryByTestId('direction-section')).not.toBeInTheDocument()
    expect(screen.queryByTestId('journey-stage-0')).not.toBeInTheDocument()
  })

  test('C2 seenGuide 不再是进门条件：seen_guide 键存在与否首屏都是 desk-page', () => {
    const seeds: Array<[string, () => void]> = [
      ['未看过落地页（无键）', () => {}],
      ['看过落地页（键=1）', () => localStorage.setItem('econpaper_seen_guide', '1')],
    ]
    for (const [label, seed] of seeds) {
      localStorage.clear()
      localStorage.setItem('econpaper_access_token', 'test-token-for-auth')
      seed()
      const { unmount } = renderWithI18n(<App />)
      expect(screen.getByTestId('desk-page'), label).toBeInTheDocument()
      unmount()
    }
  })

  test('C4 空桌页眉「了解产品」进入 GuidePage，CTA 再回到空桌', () => {
    renderWithI18n(<App />)
    fireEvent.click(screen.getByTestId('desk-open-guide'))
    expect(screen.getByTestId('guide-page')).toBeInTheDocument()
    expect(screen.getByText('用数据写实证论文')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('guide-write-paper'))
    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
    expect(screen.queryByTestId('direction-section')).not.toBeInTheDocument()
  })

  test('C4 GuidePage 的返回按钮回到 desk-page', () => {
    renderWithI18n(<App />)
    fireEvent.click(screen.getByTestId('desk-open-guide'))
    expect(screen.getByTestId('guide-page')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('guide-back-desk'))
    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
  })

  test('C5 无会话工作台点「再看一次产品页」能看 GuidePage，且能回到工作台不丢方向', async () => {
    const user = userEvent.setup()
    const shapedTitle = '养老金并轨之后，临近退休的人是不是更早离开劳动力市场？'
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.includes('/desk/discuss')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              intent: 'research',
              reflection: '收到，方向可以先定下来。',
              title: shapedTitle,
              heard: ['CHARLS', '养老'],
              comparison: '比较政策前后',
              outcome: '看就业、工时或退休',
              question: '',
              options: [],
              explain: '',
              ready: true,
              source: 'llm',
            }),
        })
      }
      if (href.endsWith('/auth/me')) {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ exists: true }) })
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    // 等 /auth/me 的微任务链落地，authed 置真后再走 desk 确认流
    await act(async () => {
      await Promise.resolve()
    })
    expect(screen.getByTestId('desk-page')).toBeInTheDocument()

    await user.type(screen.getByTestId('desk-paper'), '导师让我用 CHARLS 做点养老的')
    await user.click(screen.getByTestId('desk-shape-btn'))
    const confirm = await screen.findByTestId('desk-confirm-btn')
    await user.click(confirm)

    // desk 确认方向后进入无会话工作台
    expect(screen.getByTestId('desk-columns')).toBeInTheDocument()
    expect(screen.getByTestId('open-guide-btn')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('open-guide-btn'))
    expect(screen.getByTestId('guide-page')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('guide-back-desk'))
    expect(screen.getByTestId('desk-columns')).toBeInTheDocument()
    expect(screen.getByTestId('direction-section')).toBeInTheDocument()
    expect(screen.getByLabelText(/研究问题/)).toHaveValue(shapedTitle)
  })

  test('GuidePage 发送研究想法后进入空桌对话，并保留用户原文', async () => {
    const user = userEvent.setup()
    renderWithI18n(<App />)
    fireEvent.click(screen.getByTestId('desk-open-guide'))

    await user.type(screen.getByTestId('guide-idea-input'), '我想研究高铁开通是否促进县域创业')
    await user.click(screen.getByTestId('guide-send-idea'))

    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
    expect(screen.getByTestId('desk-paper')).toHaveValue('我想研究高铁开通是否促进县域创业')
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
    expect(screen.queryByTestId('product-journey')).not.toBeInTheDocument()
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
    expect(rightPane).toHaveAttribute('data-open', 'true')
    const desk = screen.getByTestId('desk-columns')
    expect(desk).toContainElement(rightPane)
    expect(desk.className).not.toMatch(/grid-cols-1|lg:grid-cols/)
    expect(rightPane).toHaveStyle({ width: '280px' })
    expect(screen.getByTestId('outline-panel')).toHaveStyle({ width: '220px' })
    expect(screen.getByTestId('left-resize-handle')).toBeInTheDocument()
    expect(screen.getByTestId('right-resize-handle')).toBeInTheDocument()
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

  test('右栏命名「研究进度」，并分成研究结构、数据与设计、证据写作和运行记录', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ exists: true }) }))
    localStorage.setItem('econpaper_session_id', 'test-sess')
    renderWithI18n(<App />)

    expect(await screen.findByTestId('research-computer')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '研究进度' })).toBeInTheDocument()
    expect(screen.getByTestId('research-structure')).toBeInTheDocument()
    expect(screen.getByTestId('research-data-design')).toBeInTheDocument()
    expect(screen.getByTestId('research-evidence-writing')).toBeInTheDocument()
    expect(screen.getByTestId('research-run-records')).toBeInTheDocument()
    expect(screen.getByTestId('research-computer')).toContainElement(screen.getByTestId('paper-path'))
  })

  test('提交状态显示真实阻塞与已通过条件', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ exists: true }),
      }),
    )
    renderWithI18n(<App />)

    const status = await screen.findByTestId('submission-status')
    expect(status).toHaveTextContent(/暂不可提交 · \d+/)
    fireEvent.click(screen.getByTestId('submission-toggle'))
    expect(screen.getByTestId('submission-details')).toBeInTheDocument()
    expect(screen.getAllByTestId('submission-blocker').length).toBeGreaterThan(0)
    expect(screen.getByTestId('submission-passed')).toBeInTheDocument()
  })

  test('已有章节但仍待审批时不会把 canExport 误显示为生成提交包', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            exists: true,
            claim: 'association',
            results: '| age | 0.1 |',
            outline: [{ type: 'intro', title: '引言' }],
            body_chapters: [
              { type: 'intro', title: '引言', content: '正文', status: 'generated' },
            ],
            research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
          }),
      }),
    )
    renderWithI18n(<App />)

    const status = await screen.findByTestId('submission-status')
    expect(screen.queryByTestId('submission-generate')).not.toBeInTheDocument()
    expect(screen.getByTestId('submission-toggle')).toHaveTextContent('暂不可提交 · 1')
    fireEvent.click(screen.getByTestId('submission-toggle'))
    expect(screen.getByTestId('submission-details')).toHaveTextContent('还有 1 个章节待你确认')
    expect(status).toBeInTheDocument()
  })

  test('所有真实条件通过后才显示生成提交包并打开导出对话框', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            exists: true,
            claim: 'age is associated with income',
            results: '| age | 0.1 |',
            estimate: { status: 'ok', treatment_row: 'age | 0.1' },
            outline: [{ type: 'intro', title: '引言' }],
            body_chapters: [
              { type: 'intro', title: '引言', content: '正文', status: 'approved' },
            ],
            research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
          }),
      }),
    )
    renderWithI18n(<App />)

    const generate = await screen.findByTestId('submission-generate')
    expect(generate).toHaveTextContent('生成提交包')
    fireEvent.click(generate)
    expect(screen.getByTestId('doc-export-dialog')).toBeInTheDocument()
  })

  test('证据入口会展开右栏，手动收起说明后仍可再次打开', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            exists: true,
            claim: 'association',
            results: '| age | 0.1 |',
            estimate: { status: 'ok', treatment_row: 'age | 0.1' },
            research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
          }),
      }),
    )
    renderWithI18n(<App />)

    await screen.findByTestId('evidence-why')
    fireEvent.click(screen.getByTestId('right-collapse-btn'))
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'false')

    fireEvent.click(screen.getByTestId('evidence-why'))
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'true')
    const details = screen.getByTestId('research-evidence-explanation') as HTMLDetailsElement
    expect(details.open).toBe(true)

    act(() => {
      details.open = false
      fireEvent(details, new Event('toggle'))
    })
    expect(details.open).toBe(false)

    fireEvent.click(screen.getByTestId('evidence-why'))
    expect(details.open).toBe(true)
  })

  test('左栏一次只显示一个阻塞决策，优先提示识别失败', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            exists: true,
            claim: 'association',
            identification_failed: true,
            identification_report: '设计未通过',
            write_blockers: ['缺少主表', '结果章被锁定'],
            outline: [{ type: 'intro', title: '引言' }],
            research_direction: { method: 'OLS', dv: 'income', iv: 'age' },
          }),
      }),
    )
    renderWithI18n(<App />)

    expect(await screen.findByTestId('decision-blocker')).toBeInTheDocument()
    expect(screen.getAllByTestId('decision-blocker')).toHaveLength(1)
    expect(screen.getByTestId('decision-blocker-title')).toHaveTextContent('研究设计')
    expect(screen.getByTestId('decision-blocker-reason')).toHaveTextContent('设计未通过')
  })

  test('专注阅读提示可进入收起状态，八秒无操作后变成胶囊并可恢复', () => {
    vi.useFakeTimers()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ exists: true }) }))
    renderWithI18n(<App />)

    expect(screen.queryByTestId('focus-reading-prompt')).not.toBeInTheDocument()
    act(() => vi.advanceTimersByTime(READING_NOTICE_MS))
    expect(screen.getByTestId('focus-reading-prompt')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('focus-reading-enter'))
    expect(screen.getByTestId('outline-panel')).toHaveAttribute('data-open', 'false')
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'false')
    expect(screen.getByTestId('focus-reading-open-left')).toBeInTheDocument()
    expect(screen.getByTestId('focus-reading-open-right')).toBeInTheDocument()

    act(() => vi.advanceTimersByTime(CAPSULE_DELAY_MS))
    expect(screen.getByTestId('focus-reading-capsule')).toHaveTextContent('专注阅读')
    fireEvent.click(screen.getByTestId('focus-reading-capsule'))
    expect(screen.getByTestId('outline-panel')).toHaveAttribute('data-open', 'true')
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'true')
  })

  test('离开论文页时恢复进入专注前的侧栏布局', () => {
    vi.useFakeTimers()
    localStorage.setItem('econpaper_session_id', 'test-sess')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ exists: true }) }))
    renderWithI18n(<App />)

    fireEvent.click(screen.getByTestId('left-collapse-btn'))
    expect(screen.getByTestId('outline-panel')).toHaveAttribute('data-open', 'false')
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'true')

    act(() => vi.advanceTimersByTime(READING_NOTICE_MS))
    fireEvent.click(screen.getByTestId('focus-reading-enter'))
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'false')

    fireEvent.click(screen.getByTestId('workbench-tab-format'))
    expect(screen.getByTestId('outline-panel')).toHaveAttribute('data-open', 'false')
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'true')
  })

  test('工作台不以百分比呈现生成进度', async () => {
    localStorage.setItem('econpaper_session_id', 'test-sess')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ exists: true }) }))
    renderWithI18n(<App />)
    await screen.findByTestId('desk-columns')
    expect(screen.queryByTestId('paper-agent')).not.toBeInTheDocument()
    expect(screen.getByTestId('desk-columns')).not.toHaveTextContent(/\d+%/)
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

    expect(screen.getByTestId('desk-page')).toBeInTheDocument()

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
    expect(init.headers).toEqual(expect.objectContaining({ 'Idempotency-Key': expect.any(String) }))
  })

  test('202 上传在等待 Runner 前持久化 session、数据和 kind-aware handle', async () => {
    vi.stubGlobal('EventSource', AppFakeEventSource)
    let pendingAtRequest: Record<string, unknown> | null = null
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/upload')) {
        pendingAtRequest = JSON.parse(localStorage.getItem('econpaper_pending_upload') || 'null')
        return Promise.resolve(
          new Response(
            JSON.stringify({
              session_id: 'sess-upload-202',
              run_id: 'run-upload-202',
              status: 'PENDING',
              events_url: '/api/runs/run-upload-202/events',
              dataset_meta: { columns: ['year', 'income'], rows: 2 },
            }),
            { status: 202, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      if (href.endsWith('/runs/run-upload-202')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              status: 'SUCCEEDED',
              result: {
                upload_readiness: 'READY',
                cleaning_report: { steps: [{ name: 'profiling', status: 'success' }] },
              },
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    fireEvent.change(screen.getByTestId('file-input'), {
      target: { files: [new File(['year,income\n2020,1'], 'panel.csv')] },
    })

    await waitFor(() => expect(AppFakeEventSource.latest?.url).toBe('/api/runs/run-upload-202/events'))
    expect(pendingAtRequest).toMatchObject({ fileName: 'panel.csv', idempotencyKey: expect.any(String) })
    expect(localStorage.getItem('econpaper_session_id')).toBe('sess-upload-202')
    expect(JSON.parse(sessionStorage.getItem('econpaper_csv_meta') || '{}')).toMatchObject({
      sessionId: 'sess-upload-202',
      name: 'panel.csv',
      rows: 2,
      cols: 2,
    })
    expect(JSON.parse(localStorage.getItem('econpaper_active_run_id:sess-upload-202') || '{}')).toMatchObject({
      runId: 'run-upload-202',
      kind: 'upload_pipeline',
    })
    expect(screen.getByTestId('upload-live-status')).toHaveTextContent('正在清理')
    expect(screen.getByTestId('direction-disabled-reason')).toHaveTextContent('数据清理完成后')
    expect(screen.queryByText('正在估计主结果并检索文献…')).not.toBeInTheDocument()

    await act(async () => {
      AppFakeEventSource.latest?.onmessage?.(
        new MessageEvent('message', {
          data: JSON.stringify({ status: 'SUCCEEDED' }),
        }),
      )
    })
    await waitFor(() => {
      expect(localStorage.getItem('econpaper_active_run_id:sess-upload-202')).toBeNull()
      expect(localStorage.getItem('econpaper_pending_upload')).toBeNull()
    })
    expect(screen.queryByTestId('direction-disabled-reason')).not.toBeInTheDocument()
    expect(screen.getByTestId('clean-step-profiling')).toHaveAttribute('data-status', 'completed')
  })

  test('新上传一开始就清除上一份数据的清理结果', async () => {
    localStorage.setItem('econpaper_session_id', 'sess-previous')
    const previousSteps = CLEAN_STEPS.map((name) => ({ name, status: 'success' }))
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/sessions/sess-previous')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              exists: true,
              upload_readiness: 'READY',
              cleaning_report: { steps: previousSteps },
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      if (href.endsWith('/upload')) return new Promise<Response>(() => {})
      return Promise.resolve(new Response('{}', { status: 200 }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)
    expect(await screen.findByText('8/8 ✓')).toBeInTheDocument()

    fireEvent.change(screen.getByTestId('file-input'), {
      target: { files: [new File(['year,income\n2021,2'], 'replacement.csv')] },
    })

    await waitFor(() => expect(screen.queryByText('8/8 ✓')).not.toBeInTheDocument())
    expect(screen.getByTestId('upload-live-status')).toHaveTextContent('正在接收数据')
  })

  test('上传 Run 失败时保留 Session、清理恢复句柄并提供可键盘触发的重选动作', async () => {
    vi.stubGlobal('EventSource', AppFakeEventSource)
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/upload')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              session_id: 'sess-failed-upload',
              run_id: 'run-failed-upload',
              status: 'PENDING',
              events_url: '/api/runs/run-failed-upload/events',
              dataset_meta: { columns: ['id'], rows: 1 },
            }),
            { status: 202, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      if (href.endsWith('/runs/run-failed-upload')) {
        return Promise.resolve(
          new Response(JSON.stringify({ status: 'FAILED', error: 'internal path omitted' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }),
        )
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)

    fireEvent.change(screen.getByTestId('file-input'), {
      target: { files: [new File(['id\n1'], 'failed.csv')] },
    })
    await waitFor(() => expect(AppFakeEventSource.latest).not.toBeNull())
    await act(async () => {
      AppFakeEventSource.latest?.onmessage?.(
        new MessageEvent('message', { data: JSON.stringify({ status: 'FAILED' }) }),
      )
    })

    expect(await screen.findByTestId('upload-reselect-btn')).toBeEnabled()
    expect(screen.getByTestId('upload-error')).toHaveTextContent('数据处理失败')
    expect(screen.getByTestId('upload-error')).not.toHaveTextContent('internal path omitted')
    expect(localStorage.getItem('econpaper_session_id')).toBe('sess-failed-upload')
    expect(localStorage.getItem('econpaper_active_run_id:sess-failed-upload')).toBeNull()
    expect(localStorage.getItem('econpaper_pending_upload')).toBeNull()
    expect(screen.getByTestId('direction-disabled-reason')).toBeInTheDocument()
    fireEvent.keyDown(screen.getByTestId('upload-reselect-btn'), { key: 'Enter' })
    expect(screen.getByTestId('upload-reselect-btn').tagName).toBe('BUTTON')
  })

  test('上传 Run 取消时保留 Session、禁用方向并显示重选动作', async () => {
    vi.stubGlobal('EventSource', AppFakeEventSource)
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        const href = String(url)
        if (href.endsWith('/upload')) {
          return Promise.resolve(
            new Response(
              JSON.stringify({
                session_id: 'sess-cancelled-upload',
                run_id: 'run-cancelled-upload',
                status: 'PENDING',
                events_url: '/api/runs/run-cancelled-upload/events',
                dataset_meta: { columns: ['id'], rows: 1 },
              }),
              { status: 202, headers: { 'Content-Type': 'application/json' } },
            ),
          )
        }
        if (href.endsWith('/runs/run-cancelled-upload')) {
          return Promise.resolve(
            new Response(JSON.stringify({ status: 'CANCELLED' }), {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            }),
          )
        }
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
      }),
    )
    renderWithI18n(<App />)

    fireEvent.change(screen.getByTestId('file-input'), {
      target: { files: [new File(['id\n1'], 'cancelled.csv')] },
    })
    await waitFor(() => expect(AppFakeEventSource.latest).not.toBeNull())
    await act(async () => {
      AppFakeEventSource.latest?.onmessage?.(
        new MessageEvent('message', { data: JSON.stringify({ status: 'CANCELLED' }) }),
      )
    })

    expect(await screen.findByTestId('upload-reselect-btn')).toBeEnabled()
    expect(screen.getByTestId('upload-error')).toHaveTextContent('数据处理已取消')
    expect(screen.getByTestId('direction-disabled-reason')).toBeInTheDocument()
    expect(localStorage.getItem('econpaper_session_id')).toBe('sess-cancelled-upload')
    expect(localStorage.getItem('econpaper_active_run_id:sess-cancelled-upload')).toBeNull()
  })

  test('更新的上传意图隔离上一个 Run 的晚到结果', async () => {
    vi.stubGlobal('EventSource', AppFakeEventSource)
    let uploadCount = 0
    const keys: string[] = []
    const mockFetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      const href = String(url)
      if (href.endsWith('/upload')) {
        uploadCount += 1
        keys.push(String((init?.headers as Record<string, string>)?.['Idempotency-Key']))
        if (uploadCount === 1) {
          return Promise.resolve(
            new Response(
              JSON.stringify({
                session_id: 'sess-first',
                run_id: 'run-first',
                status: 'PENDING',
                events_url: '/api/runs/run-first/events',
                dataset_meta: { columns: ['first'], rows: 1 },
              }),
              { status: 202, headers: { 'Content-Type': 'application/json' } },
            ),
          )
        }
        return Promise.resolve(
          new Response(
            JSON.stringify({
              session_id: 'sess-second',
              dataset_meta: { columns: ['second'], rows: 1 },
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
    })
    vi.stubGlobal('fetch', mockFetch)
    renderWithI18n(<App />)

    fireEvent.change(screen.getByTestId('file-input'), {
      target: { files: [new File(['first\n1'], 'first.csv')] },
    })
    await waitFor(() => expect(AppFakeEventSource.latest?.url).toContain('run-first'))
    const firstSource = AppFakeEventSource.latest
    fireEvent.change(screen.getByTestId('file-input'), {
      target: { files: [new File(['second\n1'], 'second.csv')] },
    })
    await waitFor(() => expect(localStorage.getItem('econpaper_session_id')).toBe('sess-second'))

    firstSource?.onmessage?.(
      new MessageEvent('message', { data: JSON.stringify({ status: 'SUCCEEDED' }) }),
    )
    await Promise.resolve()
    expect(localStorage.getItem('econpaper_session_id')).toBe('sess-second')
    expect(screen.getByTestId('session-file')).toHaveTextContent('second.csv')
    expect(keys[1]).not.toBe(keys[0])
  })

  test.each([
    [401, '登录已失效'],
    [403, '没有权限'],
  ])('恢复上传遇到 %i 时清理敏感句柄并给出恢复提示', async (status, message) => {
    vi.stubGlobal('EventSource', AppFakeEventSource)
    localStorage.setItem('econpaper_session_id', 'sess-protected')
    localStorage.setItem('econpaper_seen_guide', '1')
    localStorage.setItem(
      'econpaper_active_run_id:sess-protected',
      JSON.stringify({
        runId: 'run-protected',
        eventsUrl: '/api/runs/run-protected/events',
        kind: 'upload_pipeline',
      }),
    )
    localStorage.setItem(
      'econpaper_pending_upload',
      JSON.stringify({ idempotencyKey: 'protected-key', fileName: 'protected.csv' }),
    )
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        const href = String(url)
        if (href.endsWith('/sessions/sess-protected')) {
          return Promise.resolve(
            new Response(JSON.stringify({ exists: true, upload_readiness: 'PROCESSING' }), {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            }),
          )
        }
        if (href.endsWith('/runs/run-protected')) {
          return Promise.resolve(new Response('{}', { status }))
        }
        if (href.endsWith('/auth/refresh')) {
          return Promise.resolve(new Response('{}', { status: 401 }))
        }
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
      }),
    )

    renderWithI18n(<App />)
    await waitFor(() => expect(AppFakeEventSource.latest).not.toBeNull())
    AppFakeEventSource.latest?.onerror?.()

    // 新入口语义：恢复失败不再回落地页，而是回到可重新上传的空桌
    expect(await screen.findByTestId('desk-page')).toBeInTheDocument()
    expect(screen.getByTestId('upload-error')).toHaveTextContent(message)
    expect(localStorage.getItem('econpaper_session_id')).toBeNull()
    expect(localStorage.getItem('econpaper_active_run_id:sess-protected')).toBeNull()
    expect(localStorage.getItem('econpaper_pending_upload')).toBeNull()
  })

  test('恢复中的上传 Run 已不存在时清理 handle 并回到上传引导', async () => {
    vi.stubGlobal('EventSource', AppFakeEventSource)
    localStorage.setItem('econpaper_session_id', 'sess-missing-run')
    localStorage.setItem('econpaper_seen_guide', '1')
    localStorage.setItem(
      'econpaper_active_run_id:sess-missing-run',
      JSON.stringify({
        runId: 'run-missing-upload',
        eventsUrl: '/api/runs/run-missing-upload/events',
        kind: 'upload_pipeline',
      }),
    )
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        const href = String(url)
        if (href.endsWith('/sessions/sess-missing-run')) {
          return Promise.resolve(
            new Response(JSON.stringify({ exists: true, upload_readiness: 'PROCESSING' }), {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            }),
          )
        }
        if (href.endsWith('/runs/run-missing-upload')) {
          return Promise.resolve(new Response('{}', { status: 404 }))
        }
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
      }),
    )

    renderWithI18n(<App />)
    await waitFor(() => expect(AppFakeEventSource.latest).not.toBeNull())
    AppFakeEventSource.latest?.onerror?.()

    expect(await screen.findByTestId('desk-page')).toBeInTheDocument()
    expect(screen.getByTestId('upload-error')).toHaveTextContent('未找到这次数据处理')
    expect(localStorage.getItem('econpaper_session_id')).toBeNull()
    expect(localStorage.getItem('econpaper_active_run_id:sess-missing-run')).toBeNull()
  })

  test('刷新后用全局 key 解析已接纳上传，不再发送文件体', async () => {
    vi.stubGlobal('EventSource', AppFakeEventSource)
    localStorage.setItem(
      'econpaper_pending_upload',
      JSON.stringify({
        idempotencyKey: '11111111-1111-4111-8111-111111111111',
        fileName: 'recovered.csv',
      }),
    )
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/upload/resolve')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              session_id: 'sess-recovered',
              run_id: 'run-recovered-upload',
              status: 'PENDING',
              events_url: '/api/runs/run-recovered-upload/events',
              dataset_meta: { columns: ['id'], rows: 1 },
            }),
            { status: 202, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    await waitFor(() => expect(AppFakeEventSource.latest?.url).toContain('run-recovered-upload'))
    const resolveCall = mockFetch.mock.calls.find((call) => String(call[0]).endsWith('/upload/resolve'))
    expect(resolveCall?.[1]).not.toHaveProperty('body')
    expect(resolveCall?.[1]?.headers).toMatchObject({
      'Idempotency-Key': '11111111-1111-4111-8111-111111111111',
    })
    expect(screen.getByTestId('upload-live-status')).toHaveTextContent('恢复')
    expect(screen.queryByText('正在估计主结果并检索文献…')).not.toBeInTheDocument()
  })

  test('刷新时新上传意图优先于旧上传 Run', async () => {
    vi.stubGlobal('EventSource', AppFakeEventSource)
    localStorage.setItem('econpaper_session_id', 'sess-old')
    localStorage.setItem('econpaper_seen_guide', '1')
    localStorage.setItem(
      'econpaper_active_run_id:sess-old',
      JSON.stringify({
        runId: 'run-old',
        eventsUrl: '/api/runs/run-old/events',
        kind: 'upload_pipeline',
        idempotencyKey: '11111111-1111-4111-8111-111111111111',
      }),
    )
    localStorage.setItem(
      'econpaper_pending_upload',
      JSON.stringify({
        idempotencyKey: '22222222-2222-4222-8222-222222222222',
        fileName: 'new.csv',
      }),
    )
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      const href = String(url)
      if (href.endsWith('/upload/resolve')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              session_id: 'sess-new',
              run_id: 'run-new',
              status: 'PENDING',
              events_url: '/api/runs/run-new/events',
              dataset_meta: { columns: ['new'], rows: 1 },
            }),
            { status: 202, headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }
      if (href.endsWith('/sessions/sess-old')) {
        return Promise.resolve(
          new Response(JSON.stringify({ exists: true, upload_readiness: 'PROCESSING' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }),
        )
      }
      if (href.endsWith('/sessions/sess-new')) {
        return Promise.resolve(
          new Response(JSON.stringify({ exists: true, upload_readiness: 'PROCESSING' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }),
        )
      }
      return Promise.resolve(new Response(JSON.stringify({ status: 'RUNNING' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }))
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<App />)

    await waitFor(() => expect(localStorage.getItem('econpaper_session_id')).toBe('sess-new'))
    expect(mockFetch.mock.calls.some((call) => String(call[0]).endsWith('/upload/resolve'))).toBe(true)
    expect(JSON.parse(localStorage.getItem('econpaper_active_run_id:sess-new') || '{}')).toMatchObject({
      runId: 'run-new',
      idempotencyKey: '22222222-2222-4222-8222-222222222222',
    })
  })

  test('刷新解析 404 时清理 key 并回到可重新选文件的空桌', async () => {
    localStorage.setItem(
      'econpaper_pending_upload',
      JSON.stringify({ idempotencyKey: 'missing-upload', fileName: 'missing.csv' }),
    )
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response('{}', { status: 404, headers: { 'Content-Type': 'application/json' } })),
    )

    renderWithI18n(<App />)

    expect(await screen.findByTestId('upload-error')).toHaveTextContent(
      '上次上传未被接收，请重新选择文件。',
    )
    expect(screen.getByTestId('desk-page')).toBeInTheDocument()
    expect(screen.getByTestId('desk-upload-inline')).toBeEnabled()
    expect(localStorage.getItem('econpaper_pending_upload')).toBeNull()
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
    expect(screen.getByTestId('upload-error')).toHaveTextContent('数据处理失败')
    expect(screen.queryByText(/HTTP 400/i)).not.toBeInTheDocument()
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
      expect(screen.getByTestId('desk-upload-inline')).toHaveTextContent(/上传中/)
    })
    expect(screen.getByTestId('desk-upload-inline')).toBeDisabled()
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
    fireEvent.click(screen.getByTestId('desk-open-guide'))
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
    // U1: 到大纲阶段后信息卡默认折叠，先展开再断言
    fireEvent.click(screen.getByTestId('info-expand'))
    expect(screen.getByTestId('info-controls')).toHaveTextContent('gdp, pop')
    expect(screen.getByTestId('info-dataset')).toHaveTextContent('macro.csv')
    expect(screen.getByTestId('info-dataset')).toHaveTextContent('42')
    expect(screen.getByTestId('info-dataset')).not.toHaveTextContent(/^CSV$/)
  })

  test('补充研究信息 remounts DirectionForm from directionRecord, not sample fallback', async () => {
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
    // U1: 大纲阶段信息卡默认折叠，先展开
    fireEvent.click(await screen.findByTestId('info-expand'))
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
    fireEvent.click(await screen.findByTestId('info-expand'))
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
    fireEvent.click(await screen.findByTestId('info-expand'))
    expect(await screen.findByTestId('info-dataset')).toHaveTextContent('macro.csv')
    await user.click(screen.getByRole('button', { name: '退出' }))
    // 空桌直入语义：退出后回到可立即输入/上传的空桌，而不是落地页
    expect(await screen.findByTestId('desk-page')).toBeInTheDocument()
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
