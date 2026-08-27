import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ThreeColumn from '../ThreeColumn'

describe('ThreeColumn 桌面三栏', () => {
  test('left chapters, center paper, right steps — never collapsed', () => {
    render(
      <ThreeColumn
        outline={<p>chapters</p>}
        editor={<p>paper</p>}
        agent={<p data-testid="paper-path">steps</p>}
      />,
    )
    const right = screen.getByTestId('agent-panel')
    expect(screen.getByTestId('outline-panel')).toBeInTheDocument()
    expect(screen.getByTestId('editor-panel')).toBeInTheDocument()
    expect(right).toContainElement(screen.getByTestId('paper-path'))
    expect(right.className).not.toMatch(/\bhidden\b|opacity-0|max-h-0/)
    expect(right.className).toMatch(/border-l/)
    const main = right.parentElement
    expect(main?.className).toMatch(/grid-cols-\[220px_minmax\(0,1fr\)_280px\]/)
    expect(main?.className).toMatch(/min-w-\[760px\]/)
    expect(main?.className).not.toMatch(/grid-cols-1/)
  })
})
