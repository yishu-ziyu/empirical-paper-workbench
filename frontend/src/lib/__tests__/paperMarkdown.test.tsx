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

  test('promotes a standalone regression line to a numbered equation block', () => {
    const { container } = render(
      <div>
        {renderPaperMarkdown(
          '## 计量模型\n\n$Y_i = \\alpha + \\beta age_i + \\varepsilon_i$\n\n系数读作相关。',
        )}
      </div>,
    )
    const eq = container.querySelector('[data-testid="paper-equation"]')
    expect(eq).toBeTruthy()
    expect(eq?.textContent).toContain('Y_i')
    expect(eq?.textContent).toContain('(1)')
    expect(eq?.textContent).not.toContain('$')
  })

  test('renders pipe tables as booktabs with notes', () => {
    const md = [
      '表 1 — 主估计',
      '',
      '| 变量 | (1) |',
      '| --- | --- |',
      '| age | 0.124*** |',
      '',
      '注：括号内为标准误。',
    ].join('\n')
    const { container } = render(<div>{renderPaperMarkdown(md)}</div>)
    const table = container.querySelector('[data-testid="paper-table"]')
    expect(table).toBeTruthy()
    expect(table?.textContent).toContain('age')
    expect(table?.textContent).toContain('0.124')
    expect(container.querySelector('figcaption')?.textContent).toBe('表 1 — 主估计')
    expect(container.textContent).toContain('括号内为标准误')
  })
})
