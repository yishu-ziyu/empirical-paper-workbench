// T-09 RED tests for CodeExportDialog component.
//
// 契约（任务规格 §T-09）：
// 1. 渲染 4 个下载按钮：Python (.py) / Stata (.do) / R (.R) / EViews (.m)
// 2. 每个按钮标注语言名 + 文件扩展名
// 3. 点击按钮 → 调 GET /sessions/{id}/code-export?format=xxx
// 4. isOpen=false 时不渲染
// 5. onClose 触发关闭
// 6. 第一项是复现包 / 复现脚本（实际运行的代码），翻译版单独成栏并标“数值未核对”
//    （docs/acceptance/replication-script.md）
import { describe, test, expect, vi, beforeEach } from 'vitest'
import { render, screen, within } from '@testing-library/react'
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
    // 鉴权走 httpOnly cookie：不再读 localStorage 的遗留 Bearer token。
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
    const translated = within(screen.getByTestId('code-export-translated'))
    expect(translated.getByText(/Python/)).toBeInTheDocument()
    expect(translated.getByText(/\.py/)).toBeInTheDocument()
  })

  test('Stata 按钮显示 .do 扩展名', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const translated = within(screen.getByTestId('code-export-translated'))
    expect(translated.getByText(/Stata/)).toBeInTheDocument()
    expect(translated.getByText(/\.do/)).toBeInTheDocument()
  })

  test('R 按钮显示 .R 扩展名', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const translated = within(screen.getByTestId('code-export-translated'))
    expect(translated.getByText(/^R\b/)).toBeInTheDocument()
    expect(translated.getByText(/\.R/)).toBeInTheDocument()
  })

  test('EViews 按钮显示 .m 扩展名', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const translated = within(screen.getByTestId('code-export-translated'))
    expect(translated.getByText(/EViews/)).toBeInTheDocument()
    expect(translated.getByText(/\.m/)).toBeInTheDocument()
  })

  test('点击 Python 按钮触发 fetch 请求 format=py（cookie 凭证，无遗留 Bearer 头）', async () => {
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const buttons = screen.getAllByTestId('code-export-button')
    await user.click(buttons[0]) // Python
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('format=py'),
      expect.objectContaining({ credentials: 'include' }),
    )
    const init = (fetch as unknown as { mock: { calls: Array<[string, RequestInit]> } }).mock.calls[0][1]
    const headers = (init?.headers ?? {}) as Record<string, string>
    expect(headers.Authorization).toBeUndefined()
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
  test('复现包是第一项，请求 replication-package', async () => {
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    const pkg = screen.getByTestId('replication-package-button')
    const first = screen.getByTestId('code-export-dialog').querySelectorAll('button[data-testid]')[1]
    expect(first).toBe(pkg) // [0] is the close button
    await user.click(pkg)
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/sessions/test-session-123/replication-package'),
      expect.objectContaining({ credentials: 'include' }),
    )
  })

  test('只下载脚本请求 replication-script，不走 code-export', async () => {
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    await user.click(screen.getByTestId('replication-script-button'))
    const url = (fetch as unknown as { mock: { calls: Array<[string]> } }).mock.calls[0][0]
    expect(url).toContain('/sessions/test-session-123/replication-script')
    expect(url).not.toContain('code-export')
  })

  test('没有设定运行（404）时说明原因，不静默', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404, text: () => Promise.resolve('') }))
    const user = userEvent.setup()
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    await user.click(screen.getByTestId('replication-package-button'))
    expect(await screen.findByTestId('replication-error')).toHaveTextContent(/还没有设定运行|no specification runs/)
  })

  test('翻译版单独成栏，标明数值未核对', () => {
    renderWithI18n(<CodeExportDialog {...baseProps} />)
    expect(screen.getByText(/翻译版 · 数值未核对|Translated · not numerically checked/)).toBeInTheDocument()
    expect(within(screen.getByTestId('code-export-translated')).getAllByTestId('code-export-button')).toHaveLength(4)
  })
})
