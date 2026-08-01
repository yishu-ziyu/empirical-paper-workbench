import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { VariableConstructor } from '../VariableConstructor'
import { I18nProvider } from '../../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('VariableConstructor 变量构造表单', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  test('渲染变量构造表单 (type / column / params 输入)', () => {
    renderWithI18n(<VariableConstructor sessionId="sess-123" />)
    expect(screen.getByTestId('variable-constructor')).toBeInTheDocument()
    expect(screen.getByTestId('vc-type-select')).toBeInTheDocument()
    expect(screen.getByTestId('vc-column-input')).toBeInTheDocument()
    expect(screen.getByTestId('vc-submit')).toBeInTheDocument()
  })

  test('类型下拉包含 log / onehot / label / bin / interaction / policy_dummy', () => {
    renderWithI18n(<VariableConstructor sessionId="sess-123" />)
    const select = screen.getByTestId('vc-type-select') as HTMLSelectElement
    const options = Array.from(select.options).map((o) => o.value)
    expect(options).toContain('log_transform')
    expect(options).toContain('onehot')
    expect(options).toContain('label')
    expect(options).toContain('bin')
    expect(options).toContain('interaction')
    expect(options).toContain('policy_dummy')
  })

  test('提交表单 → 调 POST /sessions/{id}/transform → 显示已构造变量列表', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          constructed_vars: ['income_log', 'treat_post'],
        }),
    })
    vi.stubGlobal('fetch', mockFetch)

    renderWithI18n(<VariableConstructor sessionId="sess-123" />)

    fireEvent.change(screen.getByTestId('vc-column-input'), {
      target: { value: 'income' },
    })
    fireEvent.change(screen.getByTestId('vc-type-select'), {
      target: { value: 'log_transform' },
    })
    fireEvent.click(screen.getByTestId('vc-submit'))

    // 已构造变量列表渲染
    expect(await screen.findByTestId('vc-constructed-income_log')).toBeInTheDocument()
    expect(screen.getByTestId('vc-constructed-treat_post')).toBeInTheDocument()

    // fetch 被以正确的 URL + body 调用
    expect(mockFetch).toHaveBeenCalledTimes(1)
    const [url, init] = mockFetch.mock.calls[0]
    expect(String(url)).toContain('/sessions/sess-123/transform')
    expect(init.method).toBe('POST')
    const body = JSON.parse(init.body)
    expect(body.type).toBe('log_transform')
    expect(body.column).toBe('income')
  })

  test('API 报错时显示错误信息', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 400, json: () => Promise.resolve({ detail: 'bad column' }) }),
    )
    renderWithI18n(<VariableConstructor sessionId="sess-123" />)
    fireEvent.click(screen.getByTestId('vc-submit'))

    await waitFor(() => {
      expect(screen.getByText(/400|bad column/i)).toBeInTheDocument()
    })
  })
})
