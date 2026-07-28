// T-10 RED tests for DocExportDialog component.
//
// 契约（任务规格 §T-10）：
// 1. 显示 4 个模板选项（cn_journal / undergraduate / master_thesis / english_submission）
// 2. 默认选中 cn_journal
// 3. 可选择其他模板
// 4. 显示 3 个导出按钮（.tex / .pdf / .docx）
// 5. 点击导出按钮触发 onExport(format, template)
// 6. 关闭按钮触发 onClose
import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DocExportDialog, { type DocExportDialogProps } from '../DocExportDialog'

const baseProps: DocExportDialogProps = {
  sessionId: 'sess-123',
  onClose: vi.fn(),
  onExport: vi.fn(),
}

describe('DocExportDialog 文档导出对话框', () => {
  test('渲染 4 个模板选项', () => {
    render(<DocExportDialog {...baseProps} />)
    const options = screen.getAllByTestId('template-option')
    expect(options).toHaveLength(4)
  })

  test('模板选项包含 4 个模板名', () => {
    render(<DocExportDialog {...baseProps} />)
    const text = screen.getByTestId('doc-export-dialog').textContent ?? ''
    expect(text).toContain('cn_journal')
    expect(text).toContain('undergraduate')
    expect(text).toContain('master_thesis')
    expect(text).toContain('english_submission')
  })

  test('默认选中 cn_journal', () => {
    render(<DocExportDialog {...baseProps} />)
    const options = screen.getAllByTestId('template-option') as HTMLInputElement[]
    const cn = options.find((o) => o.value === 'cn_journal')
    expect(cn?.checked).toBe(true)
  })

  test('可选择 master_thesis 模板', async () => {
    const user = userEvent.setup()
    render(<DocExportDialog {...baseProps} />)
    const options = screen.getAllByTestId('template-option') as HTMLInputElement[]
    const master = options.find((o) => o.value === 'master_thesis')
    await user.click(master!)
    expect(master?.checked).toBe(true)
    // cn_journal 不再选中
    const cn = options.find((o) => o.value === 'cn_journal')
    expect(cn?.checked).toBe(false)
  })

  test('渲染 3 个导出按钮（tex/pdf/docx）', () => {
    render(<DocExportDialog {...baseProps} />)
    const buttons = screen.getAllByTestId('export-button')
    const formats = buttons.map((b) => b.getAttribute('data-format'))
    expect(formats).toEqual(expect.arrayContaining(['tex', 'pdf', 'docx']))
    expect(buttons).toHaveLength(3)
  })

  test('点击 tex 导出按钮触发 onExport("tex", "cn_journal")', async () => {
    const user = userEvent.setup()
    const onExport = vi.fn()
    render(<DocExportDialog {...baseProps} onExport={onExport} />)
    const buttons = screen.getAllByTestId('export-button')
    const texBtn = buttons.find((b) => b.getAttribute('data-format') === 'tex')!
    await user.click(texBtn)
    expect(onExport).toHaveBeenCalledWith('tex', 'cn_journal')
  })

  test('选择模板后导出传入选中的模板', async () => {
    const user = userEvent.setup()
    const onExport = vi.fn()
    render(<DocExportDialog {...baseProps} onExport={onExport} />)
    const options = screen.getAllByTestId('template-option') as HTMLInputElement[]
    const master = options.find((o) => o.value === 'master_thesis')!
    await user.click(master)
    const buttons = screen.getAllByTestId('export-button')
    const pdfBtn = buttons.find((b) => b.getAttribute('data-format') === 'pdf')!
    await user.click(pdfBtn)
    expect(onExport).toHaveBeenCalledWith('pdf', 'master_thesis')
  })

  test('关闭按钮触发 onClose', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(<DocExportDialog {...baseProps} onClose={onClose} />)
    const btn = screen.getByTestId('close-button')
    await user.click(btn)
    expect(onClose).toHaveBeenCalledOnce()
  })
})
