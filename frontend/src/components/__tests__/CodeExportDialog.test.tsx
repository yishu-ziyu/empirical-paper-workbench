// T-09 RED tests for CodeExportDialog component.
//
// 契约（任务规格 §T-09）：
// 1. 渲染 4 个下载按钮：Python (.py) / Stata (.do) / R (.R) / EViews (.m)
// 2. 每个按钮标注语言名 + 文件扩展名
// 3. 点击按钮 → 调 GET /sessions/{id}/code-export?format=xxx
// 4. isOpen=false 时不渲染
// 5. onClose 触发关闭
import { describe, test, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CodeExportDialog, { type CodeExportDialogProps } from '../CodeExportDialog'
import { I18nProvider } from '../../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

const baseProps: CodeExportDialogProps = {
  sessionId: 'test-session-123',
  isOpen: true,
  onClose: vi.fn(),
}

describe('CodeExportDialog 代码导出对话框', () => {
  beforeEach(() => {
    localStorage.setItem('econpaper_access_token', 'test-token-for-auth')
    // Mock fetch for download triggering
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      blob: () => Promise.resolve(new Blob(['code'], { type: 'text/plain' })),
      headers: { get: (name: string) => name === 'content-disposition' ? 'attachment; filename="analysis.py"' : '' },
    }))
    // Mock URL.createObjectURL / revokeObjectURL
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL: vi.fn().mockReturnValue('blob:mock'),
      revokeObjectURL: vi.fn(),
    })
    // Mock anchor click
    vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
      const el = document.createElementNS('http://www.w3.org/1999/xhtml', tag) as any
      if (tag === 'a') {
        el.click = vi.fn()
      }
      return el
    })
  })

  test('isOpen=false 时不渲染', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} isOpen={false} />)
    expect(screen.queryByTestId('code-export-dialog')).not.toBeInTheDocument()
  })

  test('isOpen=true 时渲染对话框', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    expect(screen.getByTestId('code-export-dialog')).toBeInTheDocument()
  })

  test('渲染 4 个下载按钮', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const buttons = screen.getAllByTestId('code-export-button')
    expect(buttons).toHaveLength(4)
  })

  test('Python 按钮显示 .py 扩展名', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    expect(screen.getByText(/Python/)).toBeInTheDocument()
    expect(screen.getByText(/\.py/)).toBeInTheDocument()
  })

  test('Stata 按钮显示 .do 扩展名', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    expect(screen.getByText(/Stata/)).toBeInTheDocument()
    expect(screen.getByText(/\.do/)).toBeInTheDocument()
  })

  test('R 按钮显示 .R 扩展名', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    expect(screen.getByText(/^R\b/)).toBeInTheDocument()
    expect(screen.getByText(/\.R/)).toBeInTheDocument()
  })

  test('EViews 按钮显示 .m 扩展名', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    expect(screen.getByText(/EViews/)).toBeInTheDocument()
    expect(screen.getByText(/\.m/)).toBeInTheDocument()
  })

  test('点击 Python 按钮触发 fetch 请求 format=py', async () => {
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const buttons = screen.getAllByTestId('code-export-button')
    await user.click(buttons[0]) // Python
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('format=py'),
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer test-token-for-auth' }),
      }),
    )
  })

  test('点击 Stata 按钮触发 fetch 请求 format=do', async () => {
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const buttons = screen.getAllByTestId('code-export-button')
    await user.click(buttons[1]) // Stata
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('format=do'),
      expect.any(Object),
    )
  })

  test('点击 R 按钮触发 fetch 请求 format=R', async () => {
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const buttons = screen.getAllByTestId('code-export-button')
    await user.click(buttons[2]) // R
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('format=R'),
      expect.any(Object),
    )
  })

  test('点击 EViews 按钮触发 fetch 请求 format=m', async () => {
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const buttons = screen.getAllByTestId('code-export-button')
    await user.click(buttons[3]) // EViews
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('format=m'),
      expect.any(Object),
    )
  })

  test('请求 URL 包含 session_id', async () => {
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const buttons = screen.getAllByTestId('code-export-button')
    await user.click(buttons[0])
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('test-session-123'),
      expect.any(Object),
    )
  })

  test('点击关闭按钮触发 onClose', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    renderWithI18n(<CodeExportDialog {...baseProps} onClose={onClose} />)
    const closeBtn = screen.getByTestId('code-export-close')
    await user.click(closeBtn)
    expect(onClose).toHaveBeenCalled()
  })
})
