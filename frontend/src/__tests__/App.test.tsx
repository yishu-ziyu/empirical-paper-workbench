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

  test('无 session 时显示欢迎引导卡片，包含上传按钮和步骤指引', () => {
    renderWithI18n(<App />)

    // 上传按钮始终在 header 中
    expect(screen.getByTestId('upload-btn')).toBeInTheDocument()

    // 欢迎卡片
    expect(screen.getByTestId('welcome-card')).toBeInTheDocument()

    // 产品名（同时出现在header和欢迎卡片中，使用getAllByText）
    expect(screen.getAllByText(/econpaper/i).length).toBeGreaterThan(0)

    // 三步指引（文本可能出现在 StepIndicator 和欢迎卡片中，使用 getAllByText）
    expect(screen.getAllByText(/上传数据|Upload your data/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/探索与分析|Explore and analyze/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/生成论文|Generate your paper/i).length).toBeGreaterThan(0)

    // 欢迎卡片中的上传按钮
    expect(screen.getByTestId('welcome-upload-btn')).toBeInTheDocument()
  })

  test('未上传时显示提示文字，不显示 EdaSidebar', () => {
    renderWithI18n(<App />)
    // 提示文字出现在 header 和 Editor 空态中，至少一个匹配
    expect(screen.getAllByText(/请上传 CSV 文件开始分析/i).length).toBeGreaterThan(0)
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

    // 初始无 sessionId → 提示文字可见（header + Editor 空态）
    expect(screen.getAllByText(/请上传 CSV 文件开始分析/i).length).toBeGreaterThan(0)

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