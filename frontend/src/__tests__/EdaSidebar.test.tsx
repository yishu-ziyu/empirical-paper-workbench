import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { EdaSidebar } from '../components/EdaSidebar'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('EdaSidebar EDA 侧边栏', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  test('渲染 6 个 EDA 动作按钮', () => {
    renderWithI18n(<EdaSidebar sessionId="test-session" />)
    expect(screen.getByText(/描述统计/i)).toBeInTheDocument()
    expect(screen.getByText(/相关性/i)).toBeInTheDocument()
    expect(screen.getByText(/分布图/i)).toBeInTheDocument()
    expect(screen.getByText(/散点图/i)).toBeInTheDocument()
    expect(screen.getByText(/回归诊断/i)).toBeInTheDocument()
    expect(screen.getByText(/缺失值/i)).toBeInTheDocument()
  })

  test('按钮带 data-testid 标识 (eda-btn-{action})', () => {
    renderWithI18n(<EdaSidebar sessionId="test-session" />)
    expect(screen.getByTestId('eda-btn-describe')).toBeInTheDocument()
    expect(screen.getByTestId('eda-btn-corr')).toBeInTheDocument()
    expect(screen.getByTestId('eda-btn-missing')).toBeInTheDocument()
  })

  test('点"描述统计"按钮 → 调 POST /eda → 渲染表格到侧边栏', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          columns: ['variable', 'mean', 'std', 'min', 'max', 'missing'],
          rows: [
            { variable: 'age', mean: 31.6, std: 5.94, min: 25, max: 40, missing: 0 },
            { variable: 'income', mean: 187.5, std: 85.39, min: 100, max: 300, missing: 1 },
          ],
        }),
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<EdaSidebar sessionId="sess-123" />)
    fireEvent.click(screen.getByTestId('eda-btn-describe'))

    // 表格行渲染出来（age + income）
    expect(await screen.findByText('age')).toBeInTheDocument()
    expect(screen.getByText('income')).toBeInTheDocument()
    // 均值渲染
    expect(screen.getByText('31.6')).toBeInTheDocument()

    // fetch 被以正确的 URL + body 调用
    expect(mockFetch).toHaveBeenCalledTimes(1)
    const [url, init] = mockFetch.mock.calls[0]
    expect(String(url)).toContain('/sessions/sess-123/eda')
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body).action).toBe('describe')
  })

  test('点"相关性"按钮 → 渲染相关性矩阵', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          variables: ['income', 'age'],
          matrix: [
            [1.0, 0.53],
            [0.53, 1.0],
          ],
        }),
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<EdaSidebar sessionId="sess-123" />)
    fireEvent.click(screen.getByTestId('eda-btn-corr'))

    // 变量名渲染（表头 + 行标签可能重复出现，用 findAllByText）
    const incomeCells = await screen.findAllByText('income')
    expect(incomeCells.length).toBeGreaterThan(0)
    // 对角值 1.00 渲染（2x2 矩阵有两个对角元素，用 getAllByText）
    expect(screen.getAllByText('1.00').length).toBeGreaterThan(0)
  })

  test('请求中显示 loading 状态', async () => {
    // fetch 永不 resolve → 一直 loading
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise(() => {})))

    renderWithI18n(<EdaSidebar sessionId="sess-123" />)
    fireEvent.click(screen.getByTestId('eda-btn-describe'))

    await waitFor(() => {
      expect(screen.getByText(/加载中|loading/i)).toBeInTheDocument()
    })
  })

  test('API 报错时显示错误信息', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 400, json: () => Promise.resolve({ detail: 'bad' }) }),
    )

    renderWithI18n(<EdaSidebar sessionId="sess-123" />)
    fireEvent.click(screen.getByTestId('eda-btn-describe'))

    await waitFor(() => {
      expect(screen.getByText(/400/i)).toBeInTheDocument()
    })
  })
})
