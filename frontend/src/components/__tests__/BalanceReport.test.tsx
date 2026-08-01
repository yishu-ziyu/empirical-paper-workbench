import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BalanceReport } from '../BalanceReport'
import { I18nProvider } from '../../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('BalanceReport 面板平衡性报告', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  test('渲染平衡性检查表单 (panel_id / time_col 输入 + 检查按钮)', () => {
    renderWithI18n(<BalanceReport sessionId="sess-123" />)
    expect(screen.getByTestId('balance-report')).toBeInTheDocument()
    expect(screen.getByTestId('br-panel-id-input')).toBeInTheDocument()
    expect(screen.getByTestId('br-time-col-input')).toBeInTheDocument()
    expect(screen.getByTestId('br-check')).toBeInTheDocument()
  })

  test('点击检查 → 调 POST /sessions/{id}/balance → 渲染平衡性指标表格', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          balanced: 800,
          unbalanced: 200,
          n_periods: 5,
          attrition_rate: 0.2,
        }),
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<BalanceReport sessionId="sess-123" />)

    fireEvent.change(screen.getByTestId('br-panel-id-input'), {
      target: { value: 'id' },
    })
    fireEvent.change(screen.getByTestId('br-time-col-input'), {
      target: { value: 'year' },
    })
    fireEvent.click(screen.getByTestId('br-check'))

    // 四个指标值渲染（Stage D: 字段名 balanced/unbalanced/n_periods/attrition_rate）
    expect(await screen.findByTestId('br-balanced')).toHaveTextContent('800')
    expect(screen.getByTestId('br-unbalanced')).toHaveTextContent('200')
    expect(screen.getByTestId('br-n-periods')).toHaveTextContent('5')
    expect(screen.getByTestId('br-attrition-rate')).toHaveTextContent('20%')

    // fetch 被以正确的 URL + body 调用
    expect(mockFetch).toHaveBeenCalledTimes(1)
    const [url, init] = mockFetch.mock.calls[0]
    expect(String(url)).toContain('/sessions/sess-123/balance')
    expect(init.method).toBe('POST')
    const body = JSON.parse(init.body)
    expect(body.panel_id).toBe('id')
    expect(body.time_col).toBe('year')
  })

  test('attrition_rate 显示为百分比 (0.2 -> 20%)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            balanced: 800,
            unbalanced: 200,
            n_periods: 5,
            attrition_rate: 0.2,
          }),
      }),
    )

    renderWithI18n(<BalanceReport sessionId="sess-123" />)
    fireEvent.change(screen.getByTestId('br-panel-id-input'), { target: { value: 'id' } })
    fireEvent.change(screen.getByTestId('br-time-col-input'), { target: { value: 'year' } })
    fireEvent.click(screen.getByTestId('br-check'))

    expect(await screen.findByTestId('br-attrition-rate')).toHaveTextContent('20%')
  })

  test('API 报错时显示错误信息', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 400, json: () => Promise.resolve({ detail: 'no panel' }) }),
    )
    renderWithI18n(<BalanceReport sessionId="sess-123" />)
    fireEvent.click(screen.getByTestId('br-check'))

    await waitFor(() => {
      expect(screen.getByText(/400|no panel/i)).toBeInTheDocument()
    })
  })
})
