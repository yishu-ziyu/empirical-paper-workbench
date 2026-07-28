// T-10 RED tests for LatexPreview component.
//
// 契约（任务规格 §T-10）：
// 1. 显示 LaTeX 源码（可编辑 textarea）
// 2. 编辑时触发 onLatexChange(value)
// 3. pdfUrl 提供时渲染 PDF 预览
// 4. degraded=true 时显示降级提示（latexmk 未安装）
// 5. 刷新按钮触发 onRefresh
import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import LatexPreview, { type LatexPreviewProps } from '../LatexPreview'

const sampleTex =
  '\\documentclass{article}\n\\begin{document}\n\\title{测试}\n\\end{document}'

const baseProps: LatexPreviewProps = {
  latexSource: sampleTex,
}

describe('LatexPreview LaTeX 预览组件', () => {
  test('渲染 LaTeX 源码', () => {
    render(<LatexPreview {...baseProps} />)
    const input = screen.getByTestId('latex-source-input') as HTMLTextAreaElement
    expect(input.value).toContain('\\title{测试}')
  })

  test('编辑源码触发 onLatexChange', async () => {
    const user = userEvent.setup()
    const onLatexChange = vi.fn()
    // 受控组件需要 stateful wrapper 才能让 value 跟随输入更新
    function Wrapper() {
      const [src, setSrc] = useState(sampleTex)
      return (
        <LatexPreview
          latexSource={src}
          onLatexChange={(v) => {
            onLatexChange(v)
            setSrc(v)
          }}
        />
      )
    }
    render(<Wrapper />)
    const input = screen.getByTestId('latex-source-input') as HTMLTextAreaElement
    await user.clear(input)
    await user.type(input, '新的内容')
    expect(onLatexChange).toHaveBeenCalled()
    // 最后一次调用值包含输入文本
    const lastCall = onLatexChange.mock.calls.at(-1)?.[0]
    expect(lastCall).toContain('新的内容')
  })

  test('pdfUrl 提供时渲染 PDF 预览', () => {
    render(<LatexPreview {...baseProps} pdfUrl="/sessions/x/doc-export?format=pdf" />)
    const preview = screen.getByTestId('pdf-preview')
    expect(preview).toBeInTheDocument()
  })

  test('无 pdfUrl 时不渲染 PDF 预览', () => {
    render(<LatexPreview {...baseProps} />)
    expect(screen.queryByTestId('pdf-preview')).toBeNull()
  })

  test('degraded=true 显示降级提示', () => {
    render(<LatexPreview {...baseProps} degraded={true} />)
    const hint = screen.getByTestId('degraded-hint')
    expect(hint).toBeInTheDocument()
    // 提示文本应包含 latexmk 关键词
    expect(hint.textContent).toContain('latexmk')
  })

  test('degraded=false 不显示降级提示', () => {
    render(<LatexPreview {...baseProps} degraded={false} />)
    expect(screen.queryByTestId('degraded-hint')).toBeNull()
  })

  test('刷新按钮触发 onRefresh', async () => {
    const user = userEvent.setup()
    const onRefresh = vi.fn()
    render(<LatexPreview {...baseProps} onRefresh={onRefresh} />)
    const btn = screen.getByTestId('refresh-button')
    await user.click(btn)
    expect(onRefresh).toHaveBeenCalledOnce()
  })
})
