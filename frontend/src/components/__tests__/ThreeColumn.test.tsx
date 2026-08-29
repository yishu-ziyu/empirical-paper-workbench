import { beforeEach, describe, test, expect } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import ThreeColumn from '../ThreeColumn'

describe('ThreeColumn 桌面三栏', () => {
  beforeEach(() => localStorage.clear())

  test('左右功能保留，并允许用户收起或调整宽度', () => {
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
    expect(right).toHaveAttribute('data-open', 'true')
    expect(right.className).toMatch(/border-l/)
    const main = screen.getByTestId('desk-columns')
    expect(main).toContainElement(right)
    expect(screen.getByTestId('outline-panel')).toHaveStyle({ width: '220px' })
    expect(right).toHaveStyle({ width: '280px' })

    fireEvent.keyDown(screen.getByTestId('left-resize-handle'), { key: 'ArrowRight' })
    expect(screen.getByTestId('outline-panel')).toHaveStyle({ width: '232px' })

    fireEvent.click(screen.getByTestId('right-collapse-btn'))
    expect(right).toHaveClass('hidden')
    expect(screen.getByTestId('right-expand-btn')).toBeInTheDocument()
  })
})
