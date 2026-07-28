import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { SampleFilter } from '../SampleFilter'

describe('SampleFilter 条件构建器', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  test('渲染条件构建器 (列 / 操作符 / 值 输入 + 添加按钮)', () => {
    render(<SampleFilter sessionId="sess-123" />)
    expect(screen.getByTestId('sample-filter')).toBeInTheDocument()
    expect(screen.getByTestId('sf-column-input')).toBeInTheDocument()
    expect(screen.getByTestId('sf-op-select')).toBeInTheDocument()
    expect(screen.getByTestId('sf-value-input')).toBeInTheDocument()
    expect(screen.getByTestId('sf-add-condition')).toBeInTheDocument()
  })

  test('操作符下拉包含 >= <= > < == !=', () => {
    render(<SampleFilter sessionId="sess-123" />)
    const select = screen.getByTestId('sf-op-select') as HTMLSelectElement
    const options = Array.from(select.options).map((o) => o.value)
    expect(options).toContain('>=')
    expect(options).toContain('<=')
    expect(options).toContain('>')
    expect(options).toContain('<')
    expect(options).toContain('==')
    expect(options).toContain('!=')
  })

  test('添加条件后显示在条件列表中', async () => {
    render(<SampleFilter sessionId="sess-123" />)

    fireEvent.change(screen.getByTestId('sf-column-input'), {
      target: { value: 'age' },
    })
    fireEvent.change(screen.getByTestId('sf-op-select'), {
      target: { value: '>=' },
    })
    fireEvent.change(screen.getByTestId('sf-value-input'), {
      target: { value: '50' },
    })
    fireEvent.click(screen.getByTestId('sf-add-condition'))

    // 条件显示在列表中
    expect(await screen.findByTestId('sf-condition-0')).toBeInTheDocument()
    expect(screen.getByTestId('sf-condition-0')).toHaveTextContent('age')
    expect(screen.getByTestId('sf-condition-0')).toHaveTextContent('>=')
    expect(screen.getByTestId('sf-condition-0')).toHaveTextContent('50')
  })

  test('应用筛选 → 调 POST /sessions/{id}/filter → 显示前后样本量', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () =>
        Promise.resolve({
          n_before: 1000,
          n_after: 450,
          conditions: [{ col: 'age', op: '>=', val: 50 }],
        }),
    })
    vi.stubGlobal('fetch', mockFetch)

    render(<SampleFilter sessionId="sess-123" />)

    // 先添加一个条件
    fireEvent.change(screen.getByTestId('sf-column-input'), {
      target: { value: 'age' },
    })
    fireEvent.change(screen.getByTestId('sf-op-select'), {
      target: { value: '>=' },
    })
    fireEvent.change(screen.getByTestId('sf-value-input'), {
      target: { value: '50' },
    })
    fireEvent.click(screen.getByTestId('sf-add-condition'))

    // 应用筛选
    fireEvent.click(screen.getByTestId('sf-apply'))

    // 前后样本量显示
    expect(await screen.findByTestId('sf-n-before')).toHaveTextContent('1000')
    expect(screen.getByTestId('sf-n-after')).toHaveTextContent('450')

    // fetch 被以正确的 URL + body 调用
    expect(mockFetch).toHaveBeenCalledTimes(1)
    const [url, init] = mockFetch.mock.calls[0]
    expect(String(url)).toContain('/sessions/sess-123/filter')
    expect(init.method).toBe('POST')
    const body = JSON.parse(init.body)
    expect(body.conditions).toEqual([{ col: 'age', op: '>=', val: 50 }])
  })

  test('API 报错时显示错误信息', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 400, json: () => Promise.resolve({ detail: 'bad' }) }),
    )
    render(<SampleFilter sessionId="sess-123" />)
    fireEvent.change(screen.getByTestId('sf-column-input'), { target: { value: 'age' } })
    fireEvent.change(screen.getByTestId('sf-op-select'), { target: { value: '>=' } })
    fireEvent.change(screen.getByTestId('sf-value-input'), { target: { value: '50' } })
    fireEvent.click(screen.getByTestId('sf-add-condition'))
    fireEvent.click(screen.getByTestId('sf-apply'))

    await waitFor(() => {
      expect(screen.getByText(/400|bad/i)).toBeInTheDocument()
    })
  })
})
