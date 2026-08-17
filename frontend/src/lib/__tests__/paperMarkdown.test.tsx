import { describe, expect, test } from 'vitest'
import { render } from '@testing-library/react'
import { renderPaperMarkdown } from '../paperMarkdown'

describe('paperMarkdown', () => {
  test('renders ATX headings without hash marks', () => {
    const { container } = render(
      <div>{renderPaperMarkdown('## 研究背景\n\n教育回报是劳动经济学经典议题。')}</div>,
    )
    expect(container.querySelector('h2')?.textContent).toBe('研究背景')
    expect(container.textContent).toContain('教育回报')
    expect(container.textContent).not.toContain('##')
  })

  test('renders dash lists as bullets', () => {
    const { container } = render(
      <div>{renderPaperMarkdown('贡献如下：\n\n- 方法层面\n- 证据层面')}</div>,
    )
    const items = container.querySelectorAll('li')
    expect(items).toHaveLength(2)
    expect(items[0].textContent).toBe('方法层面')
    expect(container.textContent).not.toMatch(/^- /m)
  })

  test('renders bold markers as strong', () => {
    const { container } = render(<div>{renderPaperMarkdown('这是**粗体**字。')}</div>)
    expect(container.querySelector('strong')?.textContent).toBe('粗体')
    expect(container.textContent).not.toContain('**')
  })
})
